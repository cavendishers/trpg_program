"""Anthropic Claude AI provider."""

from typing import AsyncIterator

import httpx

from backend.ai.providers.base import AIMessage, AIProviderBase, AIResponse, make_async_client


class ClaudeProvider(AIProviderBase):
    def __init__(self, api_key: str = "", model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self._base_url = "https://api.anthropic.com/v1"

    async def generate(
        self,
        messages: list[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        system_msg = ""
        chat_msgs = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                chat_msgs.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_msgs,
        }
        if system_msg:
            payload["system"] = system_msg

        async with make_async_client() as client:
            resp = await client.post(
                f"{self._base_url}/messages",
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["content"][0]["text"] if data.get("content") else ""
        return AIResponse(
            content=content,
            model=data.get("model", self.model),
            usage=data.get("usage", {}),
        )

    async def stream(
        self,
        messages: list[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        system_msg = ""
        chat_msgs = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                chat_msgs.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_msgs,
            "stream": True,
        }
        if system_msg:
            payload["system"] = system_msg

        async with make_async_client() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/messages",
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "content_block_delta":
                                text = event.get("delta", {}).get("text", "")
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            continue
