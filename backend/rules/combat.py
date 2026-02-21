"""CoC 7e combat system."""

from typing import Optional

from pydantic import BaseModel

from backend.rules.dice import (
    CheckResult,
    DiceRollResult,
    is_success,
    opposed_roll,
    roll_damage,
    roll_d100,
)


class AttackResult(BaseModel):
    attacker_roll: DiceRollResult
    hit: bool
    damage: int = 0


class CombatRoundResult(BaseModel):
    turn_order: list[str]
    actions: list[dict]


def calculate_turn_order(combatants: list[dict]) -> list[str]:
    """Sort combatants by DEX descending. Each dict needs 'id' and 'dex'."""
    sorted_c = sorted(combatants, key=lambda c: c["dex"], reverse=True)
    return [c["id"] for c in sorted_c]


def resolve_attack(
    attack_skill: int,
    damage_formula: str,
    bonus_dice: int = 0,
    rng=None,
) -> AttackResult:
    result = roll_d100(attack_skill, bonus_dice, rng=rng)
    hit = is_success(result.result)
    damage = roll_damage(damage_formula, rng=rng) if hit else 0
    return AttackResult(attacker_roll=result, hit=hit, damage=damage)


def resolve_opposed_attack(
    attack_skill: int,
    defend_skill: int,
    damage_formula: str,
    attack_bonus: int = 0,
    defend_bonus: int = 0,
    rng=None,
) -> tuple[DiceRollResult, DiceRollResult, bool, int]:
    """Opposed attack (e.g. Fighting vs Dodge). Returns (atk_roll, def_roll, hit, damage)."""
    atk, dfn, winner = opposed_roll(
        attack_skill, defend_skill, attack_bonus, defend_bonus, rng=rng
    )
    hit = winner == "active"
    damage = roll_damage(damage_formula, rng=rng) if hit else 0
    return atk, dfn, hit, damage
