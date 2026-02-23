"""Parse structured JSON responses from the AI KP."""

import json
import re
from typing import Optional

from pydantic import BaseModel


class GameDirective(BaseModel):
    type: str  # "skill_check" | "san_check" | "combat" | "clue_discovered" | "mode_switch" | "switch_character" | "grant_extra_action"
    skill: str = ""
    difficulty: str = "regular"
    reason: str = ""
    target_character: str = ""
    # san_check fields
    san_loss_success: str = "0"
    san_loss_failure: str = "1d6"
    # clue fields
    clue_id: str = ""
    # turn management fields
    mode: str = ""  # "combat" | "exploration" (for mode_switch)
    next_character_id: str = ""  # for switch_character
    action_count: int = 1  # for grant_extra_action


class NPCAction(BaseModel):
    npc_id: str
    action: str  # "dialogue" | "move" | "attack"
    content: str = ""


class KPResponse(BaseModel):
    narrative: str
    game_directives: list[GameDirective] = []
    npc_actions: list[NPCAction] = []
    atmosphere: str = "calm"
    raw: str = ""


def parse_response(raw: str) -> KPResponse:
    """Parse AI response, trying JSON first then fallback."""
    # Try to extract JSON from the response
    json_str = _extract_json(raw)
    if json_str:
        try:
            data = json.loads(json_str)
            return KPResponse(
                narrative=data.get("narrative", ""),
                game_directives=[
                    GameDirective(**d) for d in data.get("game_directives", [])
                ],
                npc_actions=[
                    NPCAction(**a) for a in data.get("npc_actions", [])
                ],
                atmosphere=data.get("atmosphere", "calm"),
                raw=raw,
            )
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # Fallback: treat entire response as narrative
    return _fallback_parse(raw)


def _extract_json(text: str) -> Optional[str]:
    """Extract JSON object from text, handling markdown code blocks."""
    # Try markdown code block first
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return match.group(1)

    # Try raw JSON object
    match = re.search(r'\{[^{}]*"narrative"[^{}]*\}', text, re.DOTALL)
    if match:
        return match.group(0)

    # Try finding outermost braces
    start = text.find('{')
    if start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return None


def _fallback_parse(raw: str) -> KPResponse:
    """When JSON parsing fails, treat the whole response as narrative."""
    return KPResponse(narrative=raw.strip(), raw=raw)
