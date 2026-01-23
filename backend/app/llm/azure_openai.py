"""Azure OpenAI LLM implementation."""

from typing import List, Optional, Dict, Any
from openai import AsyncAzureOpenAI
from app.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.config import settings
import structlog

logger = structlog.get_logger()


class AzureOpenAILLM(BaseLLM):
    """Azure OpenAI LLM provider."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.deployment_name = settings.azure_openai_deployment_name
        # Use embedding deployment if specified, otherwise fall back to embedding model name
        self.embedding_deployment = settings.azure_openai_embedding_deployment or settings.embedding_model
        self.embedding_model = settings.embedding_model
        logger.info(
            "Azure OpenAI LLM initialized",
            deployment=self.deployment_name,
            embedding_deployment=self.embedding_deployment
        )
    
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Azure OpenAI."""
        try:
            # Convert Pydantic models to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error("Azure OpenAI chat completion error", error=str(e))
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings using Azure OpenAI."""
        try:
            # Use provided model, or embedding deployment, or fall back to embedding model name
            embedding_deployment = model or self.embedding_deployment
            response = await self.client.embeddings.create(
                model=embedding_deployment,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error("Azure OpenAI embedding error", error=str(e))
            raise
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "azure_openai"

