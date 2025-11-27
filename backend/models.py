"""Database models for the application."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Document(Base):
    """Document entity."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    page_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    upload_date = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON, default=list)
    doc_metadata = Column(JSON, default=dict)  # author, title, etc.
    thumbnail_path = Column(String(512), nullable=True)
    processed = Column(Boolean, default=False)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    images = relationship("ExtractedImage", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("ExtractedTable", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """Text chunk entity."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    embedding_id = Column(String(255), nullable=True)  # ID in vector store
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class ExtractedImage(Base):
    """Extracted image entity."""
    __tablename__ = "extracted_images"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String(512), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    bbox = Column(JSON, nullable=True)  # [x0, y0, x1, y1]
    caption = Column(Text, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="images")


class ExtractedTable(Base):
    """Extracted table entity."""
    __tablename__ = "extracted_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    table_data = Column(JSON, nullable=False)  # 2D array
    csv_path = Column(String(512), nullable=True)
    excel_path = Column(String(512), nullable=True)
    bbox = Column(JSON, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="tables")


class Conversation(Base):
    """Conversation entity."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    doc_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message entity."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(50), nullable=False)  # user or assistant
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    retrieved_chunks = Column(JSON, default=list)  # List of chunk IDs
    citations = Column(JSON, default=list)  # Page numbers cited
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class SystemLog(Base):
    """System log entity."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, default=dict)
