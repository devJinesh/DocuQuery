"""Application configuration management."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "DocuQuery"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Paths
    data_dir: Path = Path("../data")
    upload_dir: Path = Path("../data/uploads")
    vector_store_dir: Path = Path("../data/vector_store")
    database_path: Path = Path("../data/app.db")
    logs_dir: Path = Path("../data/logs")
    
    # Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Chunking Settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # RAG Settings
    top_k_results: int = 5
    max_context_length: int = 2000
    
    # Performance
    max_file_size_mb: int = 500
    max_concurrent_uploads: int = 5
    
    # Privacy
    allow_cloud_models: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
