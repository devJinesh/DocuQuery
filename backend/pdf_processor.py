import io
import fitz
import pdfplumber
from PIL import Image
from pathlib import Path
from typing import List, Dict
import pandas as pd
from loguru import logger


class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = fitz.open(str(self.pdf_path))
        
    def get_metadata(self) -> Dict:
        metadata = self.doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "page_count": len(self.doc),
        }
    
    def extract_text(self) -> List[Dict]:
        pages_text = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text("text")
            
            pages_text.append({
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text)
            })
        
        return pages_text
    
    def extract_images(self, output_dir: Path) -> List[Dict]:
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted_images = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = output_dir / image_filename
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                # Get image dimensions
                img = Image.open(io.BytesIO(image_bytes))
                width, height = img.size
                
                extracted_images.append({
                    "page_number": page_num + 1,
                    "image_path": str(image_path),
                    "width": width,
                    "height": height,
                    "bbox": img_info[1:5] if len(img_info) > 4 else None
                })
        
        return extracted_images
    
    def extract_tables(self, output_dir: Path) -> List[Dict]:
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted_tables = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    for idx, table in enumerate(tables):
                        if not table:
                            continue
                        
                        df = pd.DataFrame(table[1:], columns=table[0])
                        
                        csv_filename = f"page_{page_num + 1}_table_{idx + 1}.csv"
                        csv_path = output_dir / csv_filename
                        df.to_csv(csv_path, index=False)
                        
                        excel_filename = f"page_{page_num + 1}_table_{idx + 1}.xlsx"
                        excel_path = output_dir / excel_filename
                        df.to_excel(excel_path, index=False)
                        
                        extracted_tables.append({
                            "page_number": page_num + 1,
                            "table_data": table,
                            "csv_path": str(csv_path),
                            "excel_path": str(excel_path),
                            "bbox": None
                        })
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
        
        return extracted_tables
    
    def generate_thumbnail(self, output_path: Path, page_num: int = 0) -> str:
        try:
            page = self.doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img.thumbnail((300, 400))
            img.save(output_path)
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return ""
    
    def close(self):
        if self.doc:
            self.doc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
