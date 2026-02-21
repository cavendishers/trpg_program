"""Quick API connectivity test."""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.ai.providers.base import AIMessage, make_async_client, create_provider
from backend.config import settings


async def test_proxy():
    """Test basic HTTPS connectivity through proxy."""
    print("=== Step 1: Test proxy/network ===")
    try:
        async with make_async_client() as client:
            resp = await client.get("https://httpbin.org/ip")
            print(f"  Network OK. Your IP: {resp.json().get('origin', '?')}")
    except Exception as e:
        print(f"  Network FAILED: {e}")
        return False
    return True


async def test_provider():
    """Test AI provider connectivity."""
    print(f"\n=== Step 2: Test AI Provider ({settings.ai_provider}) ===")
    print(f"  Model: {settings.ai_model}")

    key = ""
    extra = {}
    if settings.ai_provider == "claude":
        key = settings.anthropic_api_key
    elif settings.ai_provider == "openai":
        key = settings.openai_api_key
        extra["base_url"] = settings.openai_base_url
        print(f"  Base URL: {settings.openai_base_url}")

    print(f"  API Key: {'SET (' + key[:8] + '...)' if key else 'NOT SET'}")

    if not key:
        print("  SKIP: No API key configured.")
        return False

    try:
        provider = create_provider(
            settings.ai_provider,
            api_key=key,
            model=settings.ai_model,
            **extra,
        )
        messages = [AIMessage(role="user", content="Say 'hello' in one word.")]
        resp = await provider.generate(messages, max_tokens=10)
        print(f"  AI Response: {resp.content.strip()}")
        print(f"  Provider OK!")
        return True
    except Exception as e:
        print(f"  Provider FAILED: {e}")
        return False


async def main():
    print(f"Provider: {settings.ai_provider}")
    print(f"Proxy env: {os.environ.get('ALL_PROXY', os.environ.get('HTTPS_PROXY', 'none'))}")
    print()

    net_ok = await test_proxy()
    if net_ok:
        await test_provider()


if __name__ == "__main__":
    asyncio.run(main())
