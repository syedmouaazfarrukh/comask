"""Vector database integration (ChromaDB)."""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
from app.config import settings
import structlog
from app.processing.embedder import Embedder

logger = structlog.get_logger()


class VectorDB:
    """ChromaDB wrapper for vector storage and search."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        # Disable telemetry to avoid errors
        import os
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection_name = "comask_documents"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = Embedder()
        logger.info("Vector DB initialized", collection=self.collection_name)
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        """
        Add documents to vector database.
        
        Args:
            documents: List of document dicts with 'id', 'content', 'metadata'
            embeddings: Optional pre-computed embeddings
        
        Returns:
            True if successful
        """
        try:
            if not documents:
                return True
            
            # Extract data
            ids = [doc["id"] for doc in documents]
            contents = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # Generate embeddings if not provided
            if embeddings is None:
                embeddings = await self.embedder.embed_texts(contents)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info("Documents added to vector DB", count=len(documents))
            return True
            
        except Exception as e:
            logger.error("Error adding documents to vector DB", error=str(e))
            return False
    
    async def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            query_embedding: Optional pre-computed query embedding
            n_results: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of document results with 'id', 'content', 'metadata', 'distance'
        """
        try:
            # Generate query embedding if not provided
            if query_embedding is None:
                query_embedding = await self.embedder.embed_text(query)
            
            # Build where clause for filtering
            where = None
            if filter_dict:
                where = filter_dict
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            # Format results
            documents = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    }
                    documents.append(doc)
            
            logger.debug("Vector search completed", query=query[:50], results_count=len(documents))
            return documents
            
        except Exception as e:
            logger.error("Vector search error", error=str(e), query=query[:50])
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from vector DB."""
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug("Document deleted from vector DB", doc_id=doc_id)
            return True
        except Exception as e:
            logger.error("Error deleting document", doc_id=doc_id, error=str(e))
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count
            }
        except Exception as e:
            logger.error("Error getting collection stats", error=str(e))
            return {"error": str(e)}


# Global vector DB instance
_vector_db: Optional[VectorDB] = None


def get_vector_db() -> VectorDB:
    """Get or create vector DB instance."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDB()
    return _vector_db

