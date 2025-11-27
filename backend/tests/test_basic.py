"""Tests for PDF processing functionality."""
import pytest
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_processor import PDFProcessor
from chunker import SemanticChunker
from utils import sanitize_filename, format_file_size, clean_text


class TestPDFProcessor:
    """Tests for PDF processing."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("test<file>.pdf") == "test_file_.pdf"
        assert sanitize_filename("normal.pdf") == "normal.pdf"
        assert sanitize_filename("file:with:colons.pdf") == "file_with_colons.pdf"
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(100) == "100.00 B"
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1024 * 1024) == "1.00 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"
    
    def test_clean_text(self):
        """Test text cleaning."""
        assert clean_text("  multiple   spaces  ") == "multiple spaces"
        assert clean_text("text\x00with\x00nulls") == "textwithnulls"
        assert clean_text("\n\n\ntext\n\n") == "text"


class TestSemanticChunker:
    """Tests for semantic chunking."""
    
    def test_chunking(self):
        """Test basic chunking."""
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
        
        text = " ".join(["word"] * 100)
        chunks = chunker.chunk_text(text, page_number=1)
        
        assert len(chunks) > 1
        assert all(chunk['page_number'] == 1 for chunk in chunks)
        assert all(chunk['tokens'] <= 50 for chunk in chunks)
    
    def test_empty_text(self):
        """Test chunking with empty text."""
        chunker = SemanticChunker()
        chunks = chunker.chunk_text("", page_number=1)
        assert len(chunks) == 0
    
    def test_small_text(self):
        """Test chunking with text smaller than chunk size."""
        chunker = SemanticChunker(chunk_size=100)
        text = "This is a small text."
        chunks = chunker.chunk_text(text, page_number=1)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text


class TestUtils:
    """Tests for utility functions."""
    
    def test_truncate_text(self):
        """Test text truncation."""
        from utils import truncate_text
        
        long_text = "a" * 200
        truncated = truncate_text(long_text, max_length=50)
        assert len(truncated) == 50
        assert truncated.endswith("...")
    
    def test_chunk_list(self):
        """Test list chunking."""
        from utils import chunk_list
        
        lst = list(range(10))
        chunks = chunk_list(lst, 3)
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[-1] == [9]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
