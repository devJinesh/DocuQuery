from typing import List, Dict, Optional, Tuple
from loguru import logger
from config import settings
from vector_store import VectorStore
from llm import get_llm, BaseLLM


class RAGEngine:
    def __init__(self, vector_store: VectorStore = None, llm: BaseLLM = None,
                 top_k: int = None, max_context_length: int = None):
        self.vector_store = vector_store or VectorStore()
        self.llm = llm or get_llm()
        self.top_k = top_k or settings.top_k_results
        self.max_context_length = max_context_length or settings.max_context_length
    
    def query(self, question: str, doc_id: Optional[int] = None, stream: bool = False) -> Dict:
        logger.info(f"Query: {question[:100]}...")
        
        expanded_query = self._expand_query(question)
        
        filter_meta = {"doc_id": doc_id} if doc_id else None
        logger.info(f"Searching with filter: {filter_meta}, top_k: {self.top_k}")
        
        chunks = self.vector_store.search(expanded_query, k=self.top_k * 2, filter_metadata=filter_meta)
        
        if chunks:
            chunks = self._rerank_chunks(question, chunks)[:self.top_k]
        
        logger.info(f"Found {len(chunks)} chunks after reranking")
        if not chunks:
            logger.warning("No chunks found for query")
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "chunks": [],
                "citations": []
            }
        
        context, citations = self._prepare_context(chunks)
        logger.info(f"Context length: {len(context.split())} words, Citations: {citations}")
        prompt = self._build_prompt(question, context)
        
        logger.info("Generating answer...")
        answer = self.llm.generate(prompt, max_tokens=512, temperature=0.7, stream=stream)
        
        return {
            "answer": answer if not stream else None,
            "answer_stream": answer if stream else None,
            "chunks": chunks,
            "citations": citations,
            "context": context
        }
    
    def _rerank_chunks(self, question: str, chunks: List[Dict]) -> List[Dict]:
        question_lower = question.lower()
        question_words = set(question_lower.split())
        
        for chunk in chunks:
            text = chunk.get('metadata', {}).get('text', '').lower()
            text_words = set(text.split())
            
            overlap = len(question_words & text_words)
            chunk['relevance_score'] = overlap / len(question_words) if question_words else 0
        
        return sorted(chunks, key=lambda x: (x.get('relevance_score', 0), -x.get('distance', float('inf'))), reverse=True)
    
    def _expand_query(self, question: str) -> str:
        question = question.strip()
        if len(question.split()) < 3:
            return question
        return question
    
    def _prepare_context(self, chunks: List[Dict]) -> Tuple[str, List[int]]:
        parts = []
        citations = set()
        current_len = 0
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            text = metadata.get('text', '')
            page_num = metadata.get('page_number', 0)
            
            text_length = len(text.split())
            if current_len + text_length > self.max_context_length:
                break
            
            parts.append(
                f"[Page {page_num}] {text}"
            )
            citations.add(page_num)
            current_len += text_length
        
        context = "\n\n".join(parts)
        return context, sorted(list(citations))
    
    def _build_prompt(self, question: str, context: str) -> str:
        prompt = f"""Answer the question using the context below. Extract and synthesize relevant information to provide a complete answer.

If the context contains partial information, provide what is available and note what's missing.
Always cite the page numbers in [Page X] format.

Context:
{context}

Question: {question}

Answer:"""        
        return prompt
    
    def add_document_to_index(
        self,
        doc_id: int,
        chunks: List[Dict]
    ) -> List[str]:
        """Add document chunks to vector store."""
        if not chunks:
            return []
        
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'doc_id': doc_id,
                'page_number': chunk['page_number'],
                'chunk_index': chunk['chunk_index'],
                'tokens': chunk['tokens'],
                'text': chunk['text']
            }
            for chunk in chunks
        ]
        
        logger.info(f"Adding {len(texts)} chunks to vector store for doc {doc_id}")
        embedding_ids = self.vector_store.add_documents(
            texts=texts,
            metadatas=metadatas
        )
        
        return embedding_ids
    
    def remove_document_from_index(self, doc_id: int):
        """Remove document from vector store."""
        logger.info(f"Removing doc {doc_id} from vector store")
        self.vector_store.delete_by_doc_id(doc_id)
    
    def get_stats(self) -> Dict:
        """Get RAG engine statistics."""
        return self.vector_store.get_stats()


class ConversationManager:
    """Manage conversation history and context."""
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.conversations = {}  # conversation_id -> messages
    
    def create_conversation(self, conversation_id: int) -> Dict:
        """Create a new conversation."""
        self.conversations[conversation_id] = []
        return {
            "conversation_id": conversation_id,
            "messages": []
        }
    
    def add_message(
        self,
        conversation_id: int,
        sender: str,
        text: str,
        chunks: List[Dict] = None,
        citations: List[int] = None
    ):
        """Add message to conversation."""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            "sender": sender,
            "text": text,
            "chunks": chunks or [],
            "citations": citations or []
        }
        
        self.conversations[conversation_id].append(message)
    
    def get_conversation(self, conversation_id: int) -> List[Dict]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])
    
    def query_with_history(
        self,
        conversation_id: int,
        question: str,
        doc_id: Optional[int] = None
    ) -> Dict:
        """Query with conversation context."""
        # Get conversation history
        history = self.get_conversation(conversation_id)
        
        # Build contextualized question
        if history:
            context_question = self._contextualize_question(question, history)
        else:
            context_question = question
        
        # Query RAG engine
        response = self.rag_engine.query(context_question, doc_id)
        
        # Add to conversation
        self.add_message(
            conversation_id,
            "user",
            question
        )
        
        self.add_message(
            conversation_id,
            "assistant",
            response["answer"],
            response["chunks"],
            response["citations"]
        )
        
        return response
    
    def _contextualize_question(
        self,
        question: str,
        history: List[Dict]
    ) -> str:
        """Contextualize question with conversation history."""
        # Use last 2 exchanges for context
        recent_history = history[-4:] if len(history) > 4 else history
        
        if not recent_history:
            return question
        
        context_parts = []
        for msg in recent_history:
            sender = msg['sender']
            text = msg['text'][:200]  # Limit length
            context_parts.append(f"{sender}: {text}")
        
        context = "\n".join(context_parts)
        
        contextualized = f"""Previous conversation:
{context}

Current question: {question}

Reformulated question considering the conversation context:"""
        
        return contextualized
