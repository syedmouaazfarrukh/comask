"""Embedding generation for vector search using Voyage AI."""

from typing import List
from app.llm.embeddings import get_embeddings, generate_query_embedding, generate_embeddings_batch
import structlog

logger = structlog.get_logger()


class Embedder:
    """Handles text embedding generation using Voyage AI."""

    def __init__(self):
        # Don't cache embeddings instance - check dynamically each time
        pass

    @property
    def is_available(self) -> bool:
        """Check if embeddings are available (dynamically checks each time)."""
        embeddings = get_embeddings()
        return embeddings is not None

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (optimized for queries).

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = get_embeddings()
        if embeddings is None:
            raise ValueError("Voyage AI embeddings not configured")

        return await generate_query_embedding(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings_client = get_embeddings()
        if embeddings_client is None:
            raise ValueError("Voyage AI embeddings not configured")

        result = await generate_embeddings_batch(texts)
        logger.debug("Generated Voyage AI embeddings", count=len(result))
        return result

