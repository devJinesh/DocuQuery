"""Utility functions for the application."""
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 200:
        name = name[:200]
    return f"{name}.{ext}" if ext else name


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def calculate_directory_size(path: Path) -> int:
    """Calculate total size of a directory."""
    total_size = 0
    for item in path.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
    return total_size


def clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove null bytes
    text = text.replace('\x00', '')
    # Strip
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_pdf(file_path: Path) -> bool:
    """Validate if file is a valid PDF."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'
    except Exception:
        return False


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def parse_page_ranges(page_ranges: str) -> List[int]:
    """Parse page ranges string into list of page numbers.
    
    Examples:
        "1,3,5" -> [1, 3, 5]
        "1-5" -> [1, 2, 3, 4, 5]
        "1-3,7,9-11" -> [1, 2, 3, 7, 9, 10, 11]
    """
    pages = []
    for part in page_ranges.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide, returning default if denominator is zero."""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def create_backup(file_path: Path) -> Path:
    """Create a backup of a file."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
    counter = 1
    while backup_path.exists():
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak{counter}")
        counter += 1
    
    import shutil
    shutil.copy2(file_path, backup_path)
    return backup_path
