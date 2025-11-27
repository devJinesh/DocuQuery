import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from config import settings
from database import get_db, init_db
from models import Document, Chunk, Conversation, Message, ExtractedImage, ExtractedTable
from schemas import (
    DocumentUpload, DocumentInfo, DocumentList,
    QueryRequest, QueryResponse,
    ConversationInfo, ConversationCreate,
    SystemSettings, SystemStats,
    ReindexRequest, ErrorResponse
)
from pdf_processor import PDFProcessor
from chunker import SemanticChunker
from vector_store import VectorStore
from rag_engine import RAGEngine, ConversationManager

logger.add(
    settings.logs_dir / "app_{time}.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
rag_engine = RAGEngine(vector_store=vector_store)
conversation_manager = ConversationManager(rag_engine)


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info(f"{settings.app_name} started")


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.post("/api/upload", response_model=DocumentUpload)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files supported")
    
    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {settings.max_file_size_mb}MB limit")
    
    doc_dir = settings.upload_dir / datetime.now().strftime("%Y%m%d")
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = doc_dir / file.filename.replace(" ", "_")
    file_path.write_bytes(content)
    
    logger.info(f"Saved: {file_path}")
    
    try:
        with PDFProcessor(str(file_path)) as processor:
            metadata = processor.get_metadata()
        
        doc = Document(
            name=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            page_count=metadata["page_count"],
            file_size=len(content),
            doc_metadata=metadata,
            processed=False
        )
        
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        
        background_tasks.add_task(process_document, doc.id, str(file_path))
        
        return DocumentUpload(
            id=doc.id,
            name=doc.name,
            page_count=doc.page_count,
            file_size=doc.file_size,
            upload_date=doc.upload_date
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        file_path.unlink(missing_ok=True)
        raise HTTPException(500, str(e))


async def process_document(doc_id: int, file_path: str):
    logger.info(f"Processing document {doc_id}")
    
    from database import AsyncSessionLocal
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Document).filter(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            
            if not doc:
                logger.error(f"Document {doc_id} not found")
                return
            
            doc_data_dir = settings.data_dir / f"doc_{doc_id}"
            doc_data_dir.mkdir(parents=True, exist_ok=True)
            
            images_dir = doc_data_dir / "images"
            tables_dir = doc_data_dir / "tables"
            
            with PDFProcessor(file_path) as processor:
                logger.info(f"Extracting text from {doc.page_count} pages...")
                pages_text = processor.extract_text()
                logger.info(f"Text extraction complete")
                
                logger.info(f"Extracting images...")
                images = processor.extract_images(images_dir)
                logger.info(f"Extracted {len(images)} images")
                for img_data in images:
                    img = ExtractedImage(
                        doc_id=doc_id,
                        page_number=img_data["page_number"],
                        image_path=img_data["image_path"],
                        width=img_data.get("width"),
                        height=img_data.get("height"),
                        bbox=img_data.get("bbox")
                    )
                    db.add(img)
                
                logger.info(f"Extracting tables...")
                tables = processor.extract_tables(tables_dir)
                logger.info(f"Extracted {len(tables)} tables")
                for table_data in tables:
                    table = ExtractedTable(
                        doc_id=doc_id,
                        page_number=table_data["page_number"],
                        table_data=table_data["table_data"],
                        csv_path=table_data.get("csv_path"),
                        excel_path=table_data.get("excel_path"),
                        bbox=table_data.get("bbox")
                    )
                    db.add(table)
                
                thumbnail_path = doc_data_dir / "thumbnail.png"
                processor.generate_thumbnail(thumbnail_path)
                doc.thumbnail_path = str(thumbnail_path)
                
                logger.info(f"Chunking text...")
                chunker = SemanticChunker()
                chunks_data = chunker.chunk_document(pages_text)
                logger.info(f"Created {len(chunks_data)} chunks")
                
                for chunk_data in chunks_data:
                    chunk = Chunk(
                        doc_id=doc_id,
                        text=chunk_data["text"],
                        tokens=chunk_data["tokens"],
                        page_number=chunk_data["page_number"],
                        chunk_index=chunk_data["chunk_index"]
                    )
                    db.add(chunk)
                
                await db.commit()
                
                logger.info(f"Generating embeddings for {len(chunks_data)} chunks...")
                embedding_ids = rag_engine.add_document_to_index(doc_id, chunks_data)
                logger.info(f"Embeddings complete")
                
                # Update embedding IDs
                result = await db.execute(
                    select(Chunk).filter(Chunk.doc_id == doc_id).order_by(Chunk.id)
                )
                chunks = result.scalars().all()
                
                for chunk, emb_id in zip(chunks, embedding_ids):
                    chunk.embedding_id = emb_id
                
                doc.processed = True
                await db.commit()
                
                logger.info(f"Document {doc_id} processed successfully")
    
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Document).filter(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if doc:
                doc.processed = False
                await db.commit()


@app.get("/api/documents", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    count_result = await db.execute(select(func.count(Document.id)))
    total = count_result.scalar()
    
    result = await db.execute(
        select(Document)
        .order_by(Document.upload_date.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    
    doc_list = [
        DocumentInfo(
            id=doc.id,
            name=doc.name,
            original_filename=doc.original_filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            upload_date=doc.upload_date,
            tags=doc.tags or [],
            metadata=doc.doc_metadata or {},
            processed=doc.processed,
            thumbnail_path=doc.thumbnail_path
        )
        for doc in documents
    ]
    
    return DocumentList(documents=doc_list, total=total)


@app.get("/api/documents/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Get document details."""
    result = await db.execute(select(Document).filter(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentInfo(
        id=doc.id,
        name=doc.name,
        original_filename=doc.original_filename,
        page_count=doc.page_count,
        file_size=doc.file_size,
        upload_date=doc.upload_date,
        tags=doc.tags or [],
        metadata=doc.doc_metadata or {},
        processed=doc.processed,
        thumbnail_path=doc.thumbnail_path
    )


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document."""
    result = await db.execute(select(Document).filter(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from vector store
    rag_engine.remove_document_from_index(doc_id)
    
    # Delete files
    if Path(doc.file_path).exists():
        Path(doc.file_path).unlink()
    
    doc_data_dir = settings.data_dir / f"doc_{doc_id}"
    if doc_data_dir.exists():
        shutil.rmtree(doc_data_dir)
    
    # Delete from database
    await db.delete(doc)
    await db.commit()
    
    logger.info(f"Deleted document {doc_id}")
    return {"message": "Document deleted successfully"}


@app.post("/api/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    if request.doc_id:
        result = await db.execute(
            select(Document).filter(Document.id == request.doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if not doc.processed:
            raise HTTPException(
                status_code=400,
                detail="Document is still being processed"
            )
    
    custom_rag_engine = None
    if request.api_base_url or request.api_key or request.model:
        from llm import OpenAILLM
        custom_llm = OpenAILLM(
            api_key=request.api_key or settings.openai_api_key,
            model=request.model or getattr(settings, 'openai_model', 'gpt-3.5-turbo'),
            base_url=request.api_base_url or getattr(settings, 'openai_base_url', None)
        )
        custom_rag_engine = RAGEngine(llm=custom_llm)
        logger.info(f"Using custom API config: {request.model or 'default'} @ {request.api_base_url or 'default'}")
    
    if request.conversation_id:
        response = conversation_manager.query_with_history(
            request.conversation_id,
            request.question,
            request.doc_id
        )
    else:
        engine = custom_rag_engine if custom_rag_engine else rag_engine
        response = engine.query(
            request.question,
            request.doc_id,
            stream=request.stream
        )
    
    return QueryResponse(
        answer=response["answer"],
        chunks=response["chunks"],
        citations=response["citations"]
    )


@app.post("/api/conversations", response_model=ConversationInfo)
async def create_conversation(
    request: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    conv = Conversation(
        title=request.title,
        doc_id=request.doc_id
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    
    return ConversationInfo(
        id=conv.id,
        title=conv.title,
        doc_id=conv.doc_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[]
    )


@app.get("/api/conversations/{conv_id}", response_model=ConversationInfo)
async def get_conversation(conv_id: int, db: AsyncSession = Depends(get_db)):
    """Get conversation details."""
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    result = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.timestamp)
    )
    messages = result.scalars().all()
    
    from schemas import MessageInfo
    msg_list = [
        MessageInfo(
            sender=msg.sender,
            text=msg.text,
            timestamp=msg.timestamp,
            citations=msg.citations or []
        )
        for msg in messages
    ]
    
    return ConversationInfo(
        id=conv.id,
        title=conv.title,
        doc_id=conv.doc_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=msg_list
    )


@app.get("/api/stats", response_model=SystemStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics."""
    # Count documents
    doc_count = await db.execute(select(func.count(Document.id)))
    total_docs = doc_count.scalar()
    
    # Count chunks
    chunk_count = await db.execute(select(func.count(Chunk.id)))
    total_chunks = chunk_count.scalar()
    
    # Count conversations
    conv_count = await db.execute(select(func.count(Conversation.id)))
    total_convs = conv_count.scalar()
    
    # Calculate disk usage
    disk_usage = 0
    if settings.data_dir.exists():
        for path in settings.data_dir.rglob('*'):
            if path.is_file():
                disk_usage += path.stat().st_size
    
    disk_usage_mb = disk_usage / (1024 * 1024)
    
    # Vector store stats
    vector_stats = rag_engine.get_stats()
    
    return SystemStats(
        total_documents=total_docs,
        total_chunks=total_chunks,
        total_conversations=total_convs,
        disk_usage_mb=round(disk_usage_mb, 2),
        vector_store_stats=vector_stats
    )


@app.post("/api/reindex")
async def reindex_documents(
    request: ReindexRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Reindex documents."""
    if request.doc_id:
        # Reindex specific document
        result = await db.execute(
            select(Document).filter(Document.id == request.doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove old index
        rag_engine.remove_document_from_index(doc.id)
        
        # Reprocess
        background_tasks.add_task(process_document, doc.id, doc.file_path)
        
        return {"message": f"Reindexing document {doc.id}"}
    else:
        # Reindex all documents
        result = await db.execute(select(Document))
        docs = result.scalars().all()
        
        for doc in docs:
            rag_engine.remove_document_from_index(doc.id)
            background_tasks.add_task(process_document, doc.id, doc.file_path)
        
        return {"message": f"Reindexing {len(docs)} documents"}


@app.get("/api/conversations/{conv_id}/export/{format}")
async def export_conversation(
    conv_id: int,
    format: str,
    db: AsyncSession = Depends(get_db)
):
    """Export conversation in specified format."""
    from export import ConversationExporter
    
    if format not in ['json', 'html', 'markdown']:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    # Get conversation
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    result = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.timestamp)
    )
    messages = result.scalars().all()
    
    conversation_data = {
        'title': conv.title,
        'created_at': conv.created_at.isoformat(),
        'messages': [
            {
                'sender': msg.sender,
                'text': msg.text,
                'timestamp': msg.timestamp.isoformat(),
                'citations': msg.citations or []
            }
            for msg in messages
        ]
    }
    
    # Export
    exporter = ConversationExporter()
    export_dir = settings.data_dir / "exports"
    export_dir.mkdir(exist_ok=True)
    
    filename = f"conversation_{conv_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    output_path = export_dir / filename
    
    if format == 'json':
        exporter.export_json(conversation_data, output_path)
    elif format == 'html':
        exporter.export_html(conversation_data, output_path)
    elif format == 'markdown':
        exporter.export_markdown(conversation_data, output_path)
    
    return FileResponse(
        output_path,
        media_type='application/octet-stream',
        filename=filename
    )


@app.get("/api/documents/{doc_id}/images")
async def get_document_images(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Get extracted images from document."""
    result = await db.execute(
        select(ExtractedImage).filter(ExtractedImage.doc_id == doc_id)
    )
    images = result.scalars().all()
    
    return {
        "images": [
            {
                "id": img.id,
                "page_number": img.page_number,
                "image_path": img.image_path,
                "width": img.width,
                "height": img.height
            }
            for img in images
        ]
    }


@app.get("/api/documents/{doc_id}/tables")
async def get_document_tables(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Get extracted tables from document."""
    result = await db.execute(
        select(ExtractedTable).filter(ExtractedTable.doc_id == doc_id)
    )
    tables = result.scalars().all()
    
    return {
        "tables": [
            {
                "id": tbl.id,
                "page_number": tbl.page_number,
                "csv_path": tbl.csv_path,
                "excel_path": tbl.excel_path
            }
            for tbl in tables
        ]
    }


@app.get("/api/download/{file_type}/{file_id}")
async def download_file(file_type: str, file_id: int, db: AsyncSession = Depends(get_db)):
    """Download extracted files (images, tables)."""
    if file_type == "image":
        result = await db.execute(
            select(ExtractedImage).filter(ExtractedImage.id == file_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Image not found")
        file_path = item.image_path
    elif file_type == "table_csv":
        result = await db.execute(
            select(ExtractedTable).filter(ExtractedTable.id == file_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Table not found")
        file_path = item.csv_path
    elif file_type == "table_excel":
        result = await db.execute(
            select(ExtractedTable).filter(ExtractedTable.id == file_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Table not found")
        file_path = item.excel_path
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
