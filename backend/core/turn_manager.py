"""Turn management for multi-character party system."""

from enum import Enum
from typing import Optional

from backend.character.models import CoCCharacter


class TurnMode(str, Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"


class TurnManager:
    def __init__(self):
        self.mode: TurnMode = TurnMode.EXPLORATION
        self.turn_queue: list[str] = []
        self.current_index: int = 0
        self.actions_remaining: dict[str, int] = {}
        self.round_number: int = 0
        self._active_character_id: Optional[str] = None

    @property
    def current_actor_id(self) -> Optional[str]:
        if self.mode == TurnMode.COMBAT and self.turn_queue:
            return self.turn_queue[self.current_index]
        return self._active_character_id

    def init_combat(self, party: list[CoCCharacter]) -> str:
        """Enter combat mode. Sort by DEX descending, return first actor ID."""
        self.mode = TurnMode.COMBAT
        self.round_number = 1
        self.current_index = 0
        sorted_party = sorted(party, key=lambda c: c.characteristics.DEX, reverse=True)
        self.turn_queue = [c.id for c in sorted_party]
        self.actions_remaining = {c.id: 1 for c in sorted_party}
        return self.turn_queue[0] if self.turn_queue else ""

    def end_combat(self) -> None:
        """Exit combat, return to exploration mode."""
        self.mode = TurnMode.EXPLORATION
        self.turn_queue.clear()
        self.actions_remaining.clear()
        self.round_number = 0
        self.current_index = 0

    def can_act(self, character_id: str) -> bool:
        """Check if a character can act right now."""
        if self.mode == TurnMode.EXPLORATION:
            return True
        if not self.turn_queue:
            return False
        return (
            self.turn_queue[self.current_index] == character_id
            and self.actions_remaining.get(character_id, 0) > 0
        )

    def consume_action(self, character_id: str) -> None:
        """Use one action for the character."""
        remaining = self.actions_remaining.get(character_id, 0)
        if remaining > 0:
            self.actions_remaining[character_id] = remaining - 1

    def advance_turn(self) -> Optional[str]:
        """Move to next character in combat queue. Returns next actor ID."""
        if self.mode != TurnMode.COMBAT or not self.turn_queue:
            return None
        self.current_index += 1
        if self.current_index >= len(self.turn_queue):
            self.current_index = 0
            self.round_number += 1
            self.actions_remaining = {cid: 1 for cid in self.turn_queue}
        return self.turn_queue[self.current_index]

    def grant_extra_action(self, character_id: str, count: int = 1) -> None:
        """KP grants extra actions to a character this round."""
        current = self.actions_remaining.get(character_id, 0)
        self.actions_remaining[character_id] = current + count

    def force_switch(self, character_id: str) -> None:
        """Exploration mode: KP forces switch to a specific character."""
        self._active_character_id = character_id

    def set_active(self, character_id: str) -> None:
        """Player selects active character (exploration mode only)."""
        if self.mode == TurnMode.EXPLORATION:
            self._active_character_id = character_id

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "turn_queue": self.turn_queue,
            "current_index": self.current_index,
            "actions_remaining": self.actions_remaining,
            "round_number": self.round_number,
            "active_character_id": self._active_character_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TurnManager":
        tm = cls()
        tm.mode = TurnMode(data.get("mode", "exploration"))
        tm.turn_queue = data.get("turn_queue", [])
        tm.current_index = data.get("current_index", 0)
        tm.actions_remaining = data.get("actions_remaining", {})
        tm.round_number = data.get("round_number", 0)
        tm._active_character_id = data.get("active_character_id")
        return tm
