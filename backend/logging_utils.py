"""Logging utilities."""
from pathlib import Path
from datetime import datetime
from loguru import logger
from config import settings


def setup_logging():
    """Setup application logging."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sink=lambda msg: print(msg, end=''),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.debug else "INFO",
        colorize=True
    )
    
    # Add file handler for all logs
    logger.add(
        settings.logs_dir / "app_{time}.log",
        rotation="100 MB",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        encoding="utf-8"
    )
    
    # Add error-specific file handler
    logger.add(
        settings.logs_dir / "errors_{time}.log",
        rotation="50 MB",
        retention="60 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    logger.info("Logging initialized")


def log_document_processing(doc_id: int, operation: str, status: str, details: str = ""):
    """Log document processing events."""
    logger.info(f"Document {doc_id} | {operation} | {status} | {details}")


def log_query(question: str, doc_id: int = None, response_time: float = None):
    """Log query events."""
    logger.info(f"Query | Doc: {doc_id} | Time: {response_time}s | Question: {question[:100]}")


def log_error(module: str, error: Exception, context: dict = None):
    """Log errors with context."""
    logger.error(f"Error in {module}: {str(error)}")
    if context:
        logger.error(f"Context: {context}")


def log_system_stats(stats: dict):
    """Log system statistics."""
    logger.info(f"System Stats | {stats}")
