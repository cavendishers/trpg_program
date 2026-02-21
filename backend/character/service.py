"""Character management service with in-memory storage."""

import random
from typing import Optional

from backend.character.models import CoCCharacter, COC_DEFAULT_SKILLS, Skill
from backend.rules.character_calc import (
    Characteristics,
    calculate_derived_stats,
    roll_characteristics,
)


class CharacterService:
    def __init__(self):
        self._characters: dict[str, CoCCharacter] = {}

    def create_pc(
        self,
        name: str,
        player_name: str,
        occupation: str = "",
        age: int = 25,
        characteristics: Optional[Characteristics] = None,
        rng: Optional[random.Random] = None,
    ) -> CoCCharacter:
        r = rng or random.Random()
        chars = characteristics or roll_characteristics(rng=r)
        luck = sum(r.randint(1, 6) for _ in range(3)) * 5

        derived = calculate_derived_stats(chars, luck)

        # Initialize default skills, dodge = DEX/2
        skills = {}
        for skill_name, base in COC_DEFAULT_SKILLS.items():
            val = base
            if skill_name == "闪避":
                val = chars.DEX // 2
            skills[skill_name] = Skill(
                name=skill_name, base_value=base, current_value=val
            )

        char = CoCCharacter(
            name=name,
            player_name=player_name,
            occupation=occupation,
            age=age,
            characteristics=chars,
            derived=derived,
            skills=skills,
        )
        self._characters[char.id] = char
        return char

    def create_npc_from_template(self, template: dict) -> CoCCharacter:
        """Create NPC from scenario template data."""
        combat_stats = template.get("combat_stats", {})
        chars = Characteristics(
            STR=combat_stats.get("STR", 50),
            CON=combat_stats.get("CON", 50),
            SIZ=combat_stats.get("SIZ", 50),
            DEX=combat_stats.get("DEX", 50),
            APP=combat_stats.get("APP", 50),
            INT=combat_stats.get("INT", 50),
            POW=combat_stats.get("POW", 50),
            EDU=combat_stats.get("EDU", 50),
        )
        derived = calculate_derived_stats(chars, luck=50)
        if "HP" in combat_stats:
            derived.hp = combat_stats["HP"]
            derived.hp_max = combat_stats["HP"]

        char = CoCCharacter(
            name=template["name"],
            is_npc=True,
            occupation=template.get("role", ""),
            characteristics=chars,
            derived=derived,
            disposition=template.get("disposition", 0),
            known_info=template.get("knows", []),
            dialogue_style=template.get("dialogue_style"),
        )
        self._characters[char.id] = char
        return char

    def get_character(self, character_id: str) -> Optional[CoCCharacter]:
        return self._characters.get(character_id)

    def update_stat(self, character_id: str, stat_name: str, delta: int) -> CoCCharacter:
        char = self._characters[character_id]
        if stat_name in ("hp", "san", "mp", "luck"):
            current = getattr(char.derived, stat_name)
            max_val = getattr(char.derived, f"{stat_name}_max", 999)
            setattr(char.derived, stat_name, max(0, min(max_val, current + delta)))
        return char

    def add_item(self, character_id: str, item: str) -> None:
        self._characters[character_id].inventory.append(item)

    def add_condition(self, character_id: str, condition: str) -> None:
        char = self._characters[character_id]
        if condition not in char.conditions:
            char.conditions.append(condition)

    def remove_condition(self, character_id: str, condition: str) -> None:
        char = self._characters[character_id]
        if condition in char.conditions:
            char.conditions.remove(condition)

    def list_party(self) -> list[CoCCharacter]:
        return [c for c in self._characters.values() if not c.is_npc]

    def list_active_npcs(self) -> list[CoCCharacter]:
        return [c for c in self._characters.values() if c.is_npc]
