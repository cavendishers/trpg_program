"""Tests for the character service."""

import random

from backend.character.service import CharacterService
from backend.rules.character_calc import Characteristics


class TestCharacterService:
    def test_create_pc(self):
        svc = CharacterService()
        rng = random.Random(42)
        pc = svc.create_pc("张三", "player1", "侦探", rng=rng)
        assert pc.name == "张三"
        assert pc.player_name == "player1"
        assert not pc.is_npc
        assert pc.derived.hp > 0
        assert pc.derived.san > 0
        assert "侦查" in pc.skills

    def test_create_npc(self):
        svc = CharacterService()
        template = {
            "name": "Arnold Knott",
            "role": "patron",
            "combat_stats": {"STR": 40, "CON": 50, "HP": 10},
            "knows": ["房子闹鬼"],
        }
        npc = svc.create_npc_from_template(template)
        assert npc.is_npc
        assert npc.name == "Arnold Knott"
        assert npc.derived.hp == 10

    def test_update_stat(self):
        svc = CharacterService()
        pc = svc.create_pc("李四", "player2", rng=random.Random(1))
        original_hp = pc.derived.hp
        svc.update_stat(pc.id, "hp", -3)
        assert pc.derived.hp == original_hp - 3

    def test_stat_cannot_go_below_zero(self):
        svc = CharacterService()
        pc = svc.create_pc("王五", "player3", rng=random.Random(2))
        svc.update_stat(pc.id, "hp", -999)
        assert pc.derived.hp == 0

    def test_inventory_and_conditions(self):
        svc = CharacterService()
        pc = svc.create_pc("赵六", "player4", rng=random.Random(3))
        svc.add_item(pc.id, "手电筒")
        assert "手电筒" in pc.inventory
        svc.add_condition(pc.id, "frightened")
        assert "frightened" in pc.conditions
        svc.remove_condition(pc.id, "frightened")
        assert "frightened" not in pc.conditions

    def test_list_party_and_npcs(self):
        svc = CharacterService()
        svc.create_pc("PC1", "p1", rng=random.Random(1))
        svc.create_npc_from_template({"name": "NPC1"})
        assert len(svc.list_party()) == 1
        assert len(svc.list_active_npcs()) == 1
