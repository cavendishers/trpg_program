"""KP Engine - orchestrates AI calls for the Keeper."""

from typing import AsyncIterator, Optional

from backend.ai.prompt_builder import build_messages
from backend.ai.providers.base import AIProviderBase, AIResponse
from backend.ai.response_parser import KPResponse, parse_response
from backend.character.models import CoCCharacter
from backend.scenario.models import Scenario


class KeeperEngine:
    def __init__(self, provider: AIProviderBase, scenario: Scenario):
        self.provider = provider
        self.scenario = scenario
        self.history: list[dict] = []
        self._total_tokens = 0

    async def generate_response(
        self,
        player_input: str,
        characters: list[CoCCharacter],
        plot_progress: str = "",
    ) -> KPResponse:
        messages = build_messages(
            scenario=self.scenario,
            characters=characters,
            plot_progress=plot_progress,
            history=self.history,
            player_input=player_input,
        )

        ai_resp = await self.provider.generate(messages)
        self._total_tokens += ai_resp.usage.get("input_tokens", 0)
        self._total_tokens += ai_resp.usage.get("output_tokens", 0)

        kp_resp = parse_response(ai_resp.content)

        # Update conversation history
        self.history.append({"role": "user", "content": player_input})
        self.history.append({"role": "assistant", "content": ai_resp.content})

        return kp_resp

    async def stream_response(
        self,
        player_input: str,
        characters: list[CoCCharacter],
        plot_progress: str = "",
    ) -> AsyncIterator[str]:
        """Stream raw text chunks from the AI. Parse after collection."""
        messages = build_messages(
            scenario=self.scenario,
            characters=characters,
            plot_progress=plot_progress,
            history=self.history,
            player_input=player_input,
        )

        full_text = ""
        async for chunk in self.provider.stream(messages):
            full_text += chunk
            yield chunk

        self.history.append({"role": "user", "content": player_input})
        self.history.append({"role": "assistant", "content": full_text})

    async def feed_result(self, result_text: str) -> KPResponse:
        """Feed a game result (e.g. dice roll) back to AI for continuation."""
        messages = build_messages(
            scenario=self.scenario,
            characters=[],
            plot_progress="",
            history=self.history,
            player_input=result_text,
        )
        ai_resp = await self.provider.generate(messages)
        kp_resp = parse_response(ai_resp.content)

        self.history.append({"role": "user", "content": result_text})
        self.history.append({"role": "assistant", "content": ai_resp.content})
        return kp_resp

    def get_token_usage(self) -> int:
        return self._total_tokens
