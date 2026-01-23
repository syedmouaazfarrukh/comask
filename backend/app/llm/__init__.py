"""LLM provider factory and embeddings."""

from typing import Optional
import structlog

from app.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.llm.claude import ClaudeLLM
from app.llm.embeddings import (
    VoyageEmbeddings,
    get_embeddings,
    generate_embedding,
    generate_embeddings_batch,
    generate_query_embedding,
)
from app.config import settings

logger = structlog.get_logger()

# Lazy imports for optional providers
_AzureOpenAILLM = None
_GroqLLM = None


def _get_azure_openai():
    """Lazy load Azure OpenAI to avoid import errors if not configured."""
    global _AzureOpenAILLM
    if _AzureOpenAILLM is None:
        from app.llm.azure_openai import AzureOpenAILLM
        _AzureOpenAILLM = AzureOpenAILLM
    return _AzureOpenAILLM


def _get_groq():
    """Lazy load Groq to avoid import errors if not configured."""
    global _GroqLLM
    if _GroqLLM is None:
        from app.llm.groq import GroqLLM
        _GroqLLM = GroqLLM
    return _GroqLLM


def get_llm_provider(provider: Optional[str] = None) -> BaseLLM:
    """
    Get LLM provider based on configuration.

    Args:
        provider: Optional provider override (defaults to settings.llm_provider)

    Returns:
        BaseLLM instance for the specified provider
    """
    provider = provider or settings.llm_provider

    if provider == "claude":
        return ClaudeLLM()
    elif provider == "azure_openai":
        AzureOpenAILLM = _get_azure_openai()
        return AzureOpenAILLM()
    elif provider == "groq":
        GroqLLM = _get_groq()
        return GroqLLM()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# Global LLM instance
_llm_instance: Optional[BaseLLM] = None


def get_llm() -> BaseLLM:
    """Get or create global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_llm_provider()
        logger.info("LLM provider initialized", provider=_llm_instance.get_provider_name())
    return _llm_instance


def reset_llm():
    """Reset the global LLM instance (useful for testing)."""
    global _llm_instance
    _llm_instance = None


# Export all public interfaces
__all__ = [
    # Base classes
    "BaseLLM",
    "LLMMessage",
    "LLMResponse",
    # LLM providers
    "ClaudeLLM",
    "get_llm",
    "get_llm_provider",
    "reset_llm",
    # Embeddings
    "VoyageEmbeddings",
    "get_embeddings",
    "generate_embedding",
    "generate_embeddings_batch",
    "generate_query_embedding",
]
