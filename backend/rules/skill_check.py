"""CoC 7e skill check system."""

from typing import Optional

from pydantic import BaseModel

from backend.rules.dice import (
    CheckResult,
    DiceRollResult,
    is_success,
    roll_d100,
)


class SkillCheckOutcome(BaseModel):
    roll_result: DiceRollResult
    skill_name: str
    difficulty: str
    success: bool
    can_push: bool


NON_PUSHABLE_SKILLS = {"Cthulhu Mythos", "克苏鲁神话"}


def perform_check(
    skill_name: str,
    skill_value: int,
    difficulty: str = "regular",
    bonus_dice: int = 0,
    rng=None,
) -> SkillCheckOutcome:
    result = roll_d100(skill_value, bonus_dice, difficulty, rng=rng)
    success = is_success(result.result)
    can_push = not success and skill_name not in NON_PUSHABLE_SKILLS and result.result != CheckResult.FUMBLE
    return SkillCheckOutcome(
        roll_result=result,
        skill_name=skill_name,
        difficulty=difficulty,
        success=success,
        can_push=can_push,
    )


class PushedRollOutcome(BaseModel):
    roll_result: DiceRollResult
    skill_name: str
    success: bool
    fumbled: bool


def push_roll(
    skill_name: str,
    skill_value: int,
    difficulty: str = "regular",
    bonus_dice: int = 0,
    rng=None,
) -> PushedRollOutcome:
    result = roll_d100(skill_value, bonus_dice, difficulty, rng=rng)
    result.is_pushed = True
    return PushedRollOutcome(
        roll_result=result,
        skill_name=skill_name,
        success=is_success(result.result),
        fumbled=result.result == CheckResult.FUMBLE,
    )
