"""Tests for the AI response parser."""

from backend.ai.response_parser import (
    GameDirective,
    KPResponse,
    parse_response,
    _extract_json,
)


class TestParseResponse:
    def test_valid_json(self):
        raw = '''{
            "narrative": "你推开大门...",
            "game_directives": [
                {"type": "skill_check", "skill": "侦查", "difficulty": "regular", "reason": "观察"}
            ],
            "npc_actions": [],
            "atmosphere": "tense"
        }'''
        resp = parse_response(raw)
        assert resp.narrative == "你推开大门..."
        assert len(resp.game_directives) == 1
        assert resp.game_directives[0].skill == "侦查"
        assert resp.atmosphere == "tense"

    def test_json_in_code_block(self):
        raw = '''Here is my response:
```json
{
    "narrative": "黑暗中传来声响...",
    "game_directives": [],
    "npc_actions": [],
    "atmosphere": "horror"
}
```'''
        resp = parse_response(raw)
        assert resp.narrative == "黑暗中传来声响..."
        assert resp.atmosphere == "horror"

    def test_fallback_plain_text(self):
        raw = "你走进了一间昏暗的房间，空气中弥漫着霉味。"
        resp = parse_response(raw)
        assert resp.narrative == raw
        assert resp.game_directives == []

    def test_partial_json(self):
        raw = '{"narrative": "测试叙事"}'
        resp = parse_response(raw)
        assert resp.narrative == "测试叙事"
        assert resp.game_directives == []
