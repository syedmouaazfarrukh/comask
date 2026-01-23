"""Voyage AI embeddings implementation for legal/technical text."""

import httpx
from typing import List, Optional, Dict, Any
import structlog
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import hashlib
import json

from app.config import settings

logger = structlog.get_logger()

# Simple in-memory cache for embeddings
_embedding_cache: Dict[str, List[float]] = {}
_cache_max_size = 10000  # Maximum number of cached embeddings


class VoyageEmbeddings:
    """
    Voyage AI embeddings client.

    Voyage AI provides state-of-the-art embeddings optimized for legal and technical text.
    The voyage-law-2 model is specifically trained on legal documents.
    """

    API_URL = "https://api.voyageai.com/v1/embeddings"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        batch_size: int = 128,
        use_cache: bool = True,
    ):
        """
        Initialize Voyage AI embeddings client.

        Args:
            api_key: Voyage AI API key (defaults to settings)
            model: Model name (defaults to voyage-law-2 for legal text)
            batch_size: Maximum texts per API call
            use_cache: Whether to cache embeddings
        """
        self.api_key = api_key or settings.voyage_api_key
        if not self.api_key:
            raise ValueError("Voyage AI API key is required. Set VOYAGE_API_KEY environment variable.")

        self.model = model or settings.voyage_model
        self.batch_size = batch_size or settings.voyage_batch_size
        self.use_cache = use_cache

        # HTTP client with timeout and retry settings
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(f"{self.model}:{text}".encode()).hexdigest()

    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if available."""
        if not self.use_cache:
            return None
        key = self._get_cache_key(text)
        return _embedding_cache.get(key)

    def _add_to_cache(self, text: str, embedding: List[float]):
        """Add embedding to cache."""
        if not self.use_cache:
            return

        # Simple cache eviction when full
        if len(_embedding_cache) >= _cache_max_size:
            # Remove oldest 10% of cache
            keys_to_remove = list(_embedding_cache.keys())[:_cache_max_size // 10]
            for key in keys_to_remove:
                del _embedding_cache[key]

        key = self._get_cache_key(text)
        _embedding_cache[key] = embedding

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
    )
    async def _call_api(self, texts: List[str]) -> List[List[float]]:
        """
        Make API call to Voyage AI.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "input": texts,
            "input_type": "document",  # or "query" for search queries
        }

        try:
            response = await self.client.post(
                self.API_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]

            logger.debug(
                "Voyage AI embeddings generated",
                model=self.model,
                count=len(texts),
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
            )

            return embeddings

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Voyage AI rate limit hit, will retry")
            else:
                logger.error(
                    "Voyage AI API error",
                    status_code=e.response.status_code,
                    detail=e.response.text,
                )
            raise
        except Exception as e:
            logger.error("Voyage AI request failed", error=str(e))
            raise

    async def generate(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache first
        cached = self._get_from_cache(text)
        if cached is not None:
            return cached

        embeddings = await self._call_api([text])
        embedding = embeddings[0]

        # Cache the result
        self._add_to_cache(text, embedding)

        return embedding

    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Separate cached and uncached texts
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached is not None:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # If all cached, return early
        if not uncached_texts:
            return results

        # Process uncached texts in batches
        all_new_embeddings = []
        for i in range(0, len(uncached_texts), self.batch_size):
            batch = uncached_texts[i:i + self.batch_size]
            batch_embeddings = await self._call_api(batch)
            all_new_embeddings.extend(batch_embeddings)

            # Small delay between batches to respect rate limits
            if i + self.batch_size < len(uncached_texts):
                await asyncio.sleep(0.1)

        # Place new embeddings in results and cache them
        for idx, (text_idx, text) in enumerate(zip(uncached_indices, uncached_texts)):
            embedding = all_new_embeddings[idx]
            results[text_idx] = embedding
            self._add_to_cache(text, embedding)

        return results

    async def generate_for_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Uses 'query' input_type which is optimized for retrieval.

        Args:
            query: Search query text

        Returns:
            Embedding vector
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "input": [query],
            "input_type": "query",  # Optimized for search queries
        }

        response = await self.client.post(
            self.API_URL,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        return data["data"][0]["embedding"]

    def get_dimension(self) -> int:
        """
        Get the embedding dimension for the current model.

        Returns:
            Embedding dimension (1024 for most Voyage models)
        """
        # Voyage AI models have fixed dimensions
        model_dimensions = {
            "voyage-3": 1024,
            "voyage-3-lite": 512,
            "voyage-law-2": 1024,
            "voyage-2": 1024,
            "voyage-large-2": 1024,
            "voyage-code-2": 1536,
            "voyage-finance-2": 1024,
        }
        return model_dimensions.get(self.model, 1024)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_embeddings_instance: Optional[VoyageEmbeddings] = None
_embeddings_available: Optional[bool] = None


def get_embeddings() -> Optional[VoyageEmbeddings]:
    """Get the global embeddings instance, or None if not configured."""
    global _embeddings_instance, _embeddings_available

    # If we already have an instance, return it
    if _embeddings_instance is not None:
        return _embeddings_instance

    # If we know embeddings aren't available and settings haven't changed, return None
    if _embeddings_available is False and not settings.voyage_api_key:
        return None

    # Try to initialize (or retry if settings might have changed)
    try:
        _embeddings_instance = VoyageEmbeddings()
        _embeddings_available = True
        logger.info("Voyage AI embeddings initialized", model=settings.voyage_model)
        return _embeddings_instance
    except ValueError as e:
        # API key not configured
        logger.info("Voyage AI embeddings not available - will use keyword search", reason=str(e))
        _embeddings_available = False
        return None


def embeddings_available() -> bool:
    """Check if embeddings are available."""
    global _embeddings_available
    if _embeddings_available is None or (_embeddings_available is False and settings.voyage_api_key):
        get_embeddings()  # This will set the flag
    return _embeddings_available or False


async def generate_embedding(text: str) -> List[float]:
    """
    Convenience function to generate a single embedding.

    Args:
        text: Text to embed

    Returns:
        Embedding vector, or empty list if embeddings not available
    """
    embeddings = get_embeddings()
    if embeddings is None:
        return []
    return await embeddings.generate(text)


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors, or empty list if embeddings not available
    """
    embeddings = get_embeddings()
    if embeddings is None:
        return [[] for _ in texts]
    return await embeddings.generate_batch(texts)


async def generate_query_embedding(query: str) -> List[float]:
    """
    Convenience function to generate a query embedding.

    Args:
        query: Search query

    Returns:
        Embedding vector optimized for retrieval, or empty list if not available
    """
    embeddings = get_embeddings()
    if embeddings is None:
        return []
    return await embeddings.generate_for_query(query)
