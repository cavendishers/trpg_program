"""Abstract base for AI providers."""

import os
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

import httpx
from pydantic import BaseModel


def _get_proxy() -> Optional[str]:
    """Get proxy URL from env, normalizing socks:// to socks5://."""
    for var in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy"):
        url = os.environ.get(var, "")
        if url:
            if url.startswith("socks://"):
                url = "socks5://" + url[len("socks://"):]
            return url
    return None


def make_async_client(**kwargs) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient with proper proxy handling."""
    proxy = _get_proxy()
    defaults = {"timeout": 120}
    if proxy:
        defaults["proxy"] = proxy
    defaults.update(kwargs)
    return httpx.AsyncClient(**defaults)


class AIMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class AIResponse(BaseModel):
    content: str
    model: str = ""
    usage: dict = {}


class AIProviderBase(ABC):
    """All AI backends must implement this interface."""

    @abstractmethod
    async def generate(
        self,
        messages: list[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse: ...

    @abstractmethod
    async def stream(
        self,
        messages: list[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]: ...


def create_provider(name: str, **config) -> AIProviderBase:
    """Factory function to create an AI provider by name."""
    if name == "claude":
        from backend.ai.providers.claude import ClaudeProvider
        return ClaudeProvider(**config)
    elif name == "openai":
        from backend.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(**config)
    else:
        raise ValueError(f"Unknown AI provider: {name}")
