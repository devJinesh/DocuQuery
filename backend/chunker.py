import re
from typing import List, Dict
from loguru import logger
from config import settings


class SemanticChunker:
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str, page_number: int) -> List[Dict]:
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return []
        
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current = ""
        current_tokens = 0
        chunk_idx = 0
        
        for para in paragraphs:
            para_tokens = len(para.split())
            
            if para_tokens > self.chunk_size:
                if current:
                    chunks.append({
                        "text": current.strip(),
                        "tokens": current_tokens,
                        "page_number": page_number,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
                    current = ""
                    current_tokens = 0
                
                para_chunks = self._split_large_paragraph(para, page_number, chunk_idx)
                chunks.extend(para_chunks)
                chunk_idx += len(para_chunks)
            
            elif current_tokens + para_tokens > self.chunk_size:
                if current:
                    chunks.append({
                        "text": current.strip(),
                        "tokens": current_tokens,
                        "page_number": page_number,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
                
                if self.chunk_overlap > 0:
                    overlap = self._get_overlap(current)
                    current = overlap + " " + para
                    current_tokens = len(current.split())
                else:
                    current = para
                    current_tokens = para_tokens
            else:
                if current:
                    current += " " + para
                else:
                    current = para
                current_tokens += para_tokens
        
        if current:
            chunks.append({
                "text": current.strip(),
                "tokens": current_tokens,
                "page_number": page_number,
                "chunk_index": chunk_idx
            })
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        paragraphs = re.split(r'\n\n+|\.\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_paragraph(
        self,
        paragraph: str,
        page_number: int,
        start_index: int
    ) -> List[Dict]:
        words = paragraph.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "tokens": len(chunk_words),
                "page_number": page_number,
                "chunk_index": start_index + len(chunks)
            })
        
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        words = text.split()
        if len(words) <= self.chunk_overlap:
            return text
        return " ".join(words[-self.chunk_overlap:])
    
    def chunk_document(self, pages_text: List[Dict]) -> List[Dict]:
        all_chunks = []
        
        for page_data in pages_text:
            page_number = page_data["page_number"]
            text = page_data["text"]
            
            chunks = self.chunk_text(text, page_number)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(pages_text)} pages")
        return all_chunks
