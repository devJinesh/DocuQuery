import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
from config import settings

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available")

CHROMA_AVAILABLE = False


class EmbeddingGenerator:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        logger.info(f"Loading model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    
    def encode_single(self, text: str) -> np.ndarray:
        return self.model.encode([text], convert_to_numpy=True)[0]


class VectorStore:
    def __init__(self, store_type: str = "faiss", persist_dir: Path = None):
        self.store_type = store_type
        self.persist_dir = persist_dir or settings.vector_store_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_generator = EmbeddingGenerator()
        self.dimension = self.embedding_generator.dimension
        
        if store_type == "faiss":
            self._init_faiss()
        elif store_type == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
    
    def _init_faiss(self):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not installed")
        
        index_path = self.persist_dir / "faiss.index"
        metadata_path = self.persist_dir / "faiss_metadata.json"
        
        if index_path.exists():
            logger.info("Loading FAISS index")
            self.index = faiss.read_index(str(index_path))
            with open(metadata_path) as f:
                self.metadata = json.load(f)
        else:
            logger.info("Creating new FAISS index")
            # Using L2 distance
            self.index = faiss.IndexFlatL2(self.dimension)
            # Wrap with IDMap for ID management
            self.index = faiss.IndexIDMap(self.index)
            self.metadata = {}
    
    def _init_chroma(self):
        """Initialize ChromaDB - Disabled (using FAISS only)."""
        raise NotImplementedError("ChromaDB support disabled. Use FAISS backend.")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to vector store."""
        if not texts:
            return []
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        embeddings = self.embedding_generator.encode(texts)
        
        # Add text to metadata for retrieval
        enhanced_metadatas = []
        for text, meta in zip(texts, metadatas):
            enhanced_meta = {"text": text, **meta}
            enhanced_metadatas.append(enhanced_meta)
        
        if self.store_type == "faiss":
            return self._add_to_faiss(embeddings, ids, enhanced_metadatas)
        elif self.store_type == "chroma":
            return self._add_to_chroma(texts, embeddings, ids, enhanced_metadatas)
    
    def _add_to_faiss(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: List[Dict]
    ) -> List[str]:
        """Add to FAISS index."""
        # Convert string IDs to integers (use hash)
        int_ids = np.array([hash(id_) % (2**31) for id_ in ids])
        
        # Add to index
        self.index.add_with_ids(embeddings.astype('float32'), int_ids)
        
        # Store metadata with int_id mapping
        for int_id, id_, metadata in zip(int_ids, ids, metadatas):
            # Store both the string ID and int ID for reverse lookup
            self.metadata[str(int_id)] = {
                "string_id": id_,
                **metadata
            }
        
        # Persist
        self._persist_faiss()
        
        return ids
    
    def _add_to_chroma(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: List[Dict]
    ) -> List[str]:
        """Add to ChromaDB."""
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents."""
        # Generate query embedding
        query_embedding = self.embedding_generator.encode_single(query)
        
        if self.store_type == "faiss":
            return self._search_faiss(query_embedding, k, filter_metadata)
        elif self.store_type == "chroma":
            return self._search_chroma(query_embedding, k, filter_metadata)
    
    def _search_faiss(
        self,
        query_embedding: np.ndarray,
        k: int,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        logger.info(f"Searching FAISS index with {self.index.ntotal} vectors, k={k}")
        
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            min(k, self.index.ntotal)
        )
        
        results = []
        filtered_count = 0
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            meta = self.metadata.get(str(idx))
            if meta:
                if filter_metadata:
                    match = all(meta.get(k) == v for k, v in filter_metadata.items())
                    if not match:
                        filtered_count += 1
                        continue
                
                results.append({
                    "id": meta.get("string_id", str(idx)),
                    "distance": float(dist),
                    "metadata": meta,
                    "text": meta.get("text", "")
                })
        
        logger.info(f"Found {len(results)} results ({filtered_count} filtered out)")
        return results
        
        return results
    
    def _search_chroma(
        self,
        query_embedding: np.ndarray,
        k: int,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            where=filter_metadata
        )
        
        formatted_results = []
        if results['ids']:
            for i, id_ in enumerate(results['ids'][0]):
                formatted_results.append({
                    "id": id_,
                    "distance": results['distances'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "text": results['documents'][0][i]
                })
        
        return formatted_results
    
    def delete_by_doc_id(self, doc_id: int):
        """Delete all vectors for a document."""
        if self.store_type == "faiss":
            # Rebuild index without this doc
            ids_to_keep = [
                id_ for id_, meta in self.metadata.items()
                if meta.get('doc_id') != doc_id
            ]
            
            if len(ids_to_keep) < len(self.metadata):
                # Rebuild needed
                old_metadata = self.metadata.copy()
                self._init_faiss()  # Reset
                
                # Re-add kept vectors
                for id_ in ids_to_keep:
                    self.metadata[id_] = old_metadata[id_]
                
                self._persist_faiss()
        
        elif self.store_type == "chroma":
            # Delete from ChromaDB
            ids_to_delete = self.collection.get(
                where={"doc_id": doc_id}
            )['ids']
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
    
    def _persist_faiss(self):
        """Persist FAISS index and metadata."""
        index_path = self.persist_dir / "faiss.index"
        metadata_path = self.persist_dir / "faiss_metadata.json"
        
        faiss.write_index(self.index, str(index_path))
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        if self.store_type == "faiss":
            return {
                "total_vectors": self.index.ntotal,
                "dimension": self.dimension,
                "store_type": "faiss"
            }
        elif self.store_type == "chroma":
            return {
                "total_vectors": self.collection.count(),
                "dimension": self.dimension,
                "store_type": "chroma"
            }
