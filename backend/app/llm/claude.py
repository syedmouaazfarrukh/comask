"""Claude (Anthropic) LLM implementation."""

import anthropic
from typing import List, Dict, Any, Optional, Callable, AsyncIterator
import structlog
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.config import settings

logger = structlog.get_logger()


class ClaudeLLM(BaseLLM):
    """Claude API implementation using Anthropic SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        max_tokens: int = 4096,
    ):
        """
        Initialize Claude LLM client.

        Args:
            api_key: Anthropic API key (defaults to settings)
            default_model: Default model to use (defaults to fast model from settings)
            max_tokens: Default max tokens for responses
        """
        self.api_key = api_key or settings.claude_api_key
        if not self.api_key:
            raise ValueError("Claude API key is required. Set CLAUDE_API_KEY environment variable.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.async_client = anthropic.AsyncAnthropic(api_key=self.api_key)

        self.default_model = default_model or settings.claude_model_fast
        self.max_tokens = max_tokens or settings.claude_max_tokens

        # Model aliases for easy switching
        self.model_aliases = {
            "fast": settings.claude_model_fast,
            "sonnet": settings.claude_model_fast,
            "complex": settings.claude_model_complex,
            "opus": settings.claude_model_complex,
        }

    def _resolve_model(self, model: Optional[str] = None) -> str:
        """Resolve model alias to actual model name."""
        if model is None:
            return self.default_model
        return self.model_aliases.get(model, model)

    def _convert_messages(self, messages: List[LLMMessage]) -> tuple[Optional[str], List[Dict[str, str]]]:
        """
        Convert messages to Anthropic format, extracting system message.

        Returns:
            Tuple of (system_message, messages_list)
        """
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return system_message, anthropic_messages

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
    )
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion using Claude.

        Args:
            messages: List of messages in conversation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            model: Model to use (can be alias like 'fast' or 'complex')
            **kwargs: Additional parameters passed to API

        Returns:
            LLMResponse with generated content
        """
        resolved_model = self._resolve_model(model)
        system_message, anthropic_messages = self._convert_messages(messages)

        try:
            response = await self.async_client.messages.create(
                model=resolved_model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                messages=anthropic_messages,
                **kwargs
            )

            # Extract text content
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
            )

        except anthropic.APIError as e:
            logger.error("Claude API error", error=str(e), model=resolved_model)
            raise

    async def chat_completion_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion using Claude.

        Args:
            messages: List of messages in conversation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            model: Model to use
            on_chunk: Optional callback for each chunk
            **kwargs: Additional parameters

        Yields:
            Text chunks as they are generated
        """
        resolved_model = self._resolve_model(model)
        system_message, anthropic_messages = self._convert_messages(messages)

        try:
            async with self.async_client.messages.stream(
                model=resolved_model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                messages=anthropic_messages,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    if on_chunk:
                        on_chunk(text)
                    yield text

        except anthropic.APIError as e:
            logger.error("Claude streaming error", error=str(e), model=resolved_model)
            raise

    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Claude does not have an embeddings API.
        Use VoyageEmbeddings instead.

        Raises:
            NotImplementedError: Always, as Claude doesn't support embeddings
        """
        raise NotImplementedError(
            "Claude does not have an embeddings API. "
            "Use VoyageEmbeddings from app.llm.embeddings instead."
        )

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "claude"

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using Claude's tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return self.client.count_tokens(text)

    async def analyze_for_complexity(self, query: str) -> str:
        """
        Analyze a query to determine if it needs the complex model.

        Args:
            query: User query to analyze

        Returns:
            'fast' or 'complex' recommendation
        """
        # Simple heuristics for model selection
        complex_indicators = [
            "analyze",
            "compare",
            "evaluate",
            "implications",
            "comprehensive",
            "detailed",
            "relationship between",
            "how does",
            "why does",
            "what are the consequences",
            "multi-jurisdictional",
        ]

        query_lower = query.lower()
        complexity_score = sum(1 for indicator in complex_indicators if indicator in query_lower)

        # Also check length - longer queries often need more reasoning
        if len(query) > 500:
            complexity_score += 2

        return "complex" if complexity_score >= 2 else "fast"
