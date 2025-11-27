"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Document Schemas
class DocumentUpload(BaseModel):
    """Document upload response."""
    id: int
    name: str
    page_count: int
    file_size: int
    upload_date: datetime


class DocumentInfo(BaseModel):
    """Document information."""
    id: int
    name: str
    original_filename: str
    page_count: int
    file_size: int
    upload_date: datetime
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    processed: bool = False
    thumbnail_path: Optional[str] = None


class DocumentList(BaseModel):
    """List of documents."""
    documents: List[DocumentInfo]
    total: int


# Query Schemas
class QueryRequest(BaseModel):
    """Query request."""
    question: str = Field(..., min_length=1, max_length=1000)
    doc_id: Optional[int] = None
    conversation_id: Optional[int] = None
    stream: bool = False
    # Optional custom API configuration (overrides backend defaults)
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class ChunkInfo(BaseModel):
    """Retrieved chunk information."""
    id: str
    text: str
    page_number: int
    distance: float


class QueryResponse(BaseModel):
    """Query response."""
    answer: str
    chunks: List[Dict] = []
    citations: List[int] = []


# Conversation Schemas
class MessageInfo(BaseModel):
    """Message information."""
    sender: str
    text: str
    timestamp: datetime
    citations: List[int] = []


class ConversationInfo(BaseModel):
    """Conversation information."""
    id: int
    title: str
    doc_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageInfo] = []


class ConversationCreate(BaseModel):
    """Create conversation request."""
    title: str
    doc_id: Optional[int] = None


# Settings Schemas
class SystemSettings(BaseModel):
    """System settings."""
    embedding_model: str
    llm_model_type: str
    llm_model_path: Optional[str]
    chunk_size: int
    chunk_overlap: int
    top_k_results: int
    allow_cloud_models: bool


class SystemStats(BaseModel):
    """System statistics."""
    total_documents: int
    total_chunks: int
    total_conversations: int
    disk_usage_mb: float
    vector_store_stats: Dict[str, Any]


# Export Schemas
class ExportRequest(BaseModel):
    """Export request."""
    format: str = Field(..., pattern="^(json|html|pdf)$")
    conversation_id: Optional[int] = None


# Reindex Schema
class ReindexRequest(BaseModel):
    """Reindex request."""
    doc_id: Optional[int] = None


# Error Schema
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
