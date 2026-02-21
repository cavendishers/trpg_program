"""CoC 7e D100 dice system with bonus/penalty dice."""

import random
import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CheckResult(str, Enum):
    CRITICAL_SUCCESS = "critical_success"
    EXTREME_SUCCESS = "extreme_success"
    HARD_SUCCESS = "hard_success"
    REGULAR_SUCCESS = "regular_success"
    FAILURE = "failure"
    FUMBLE = "fumble"


class DiceRollResult(BaseModel):
    roll: int
    target: int
    skill_value: int
    result: CheckResult
    bonus_dice: int = 0
    all_tens_dice: list[int] = []
    is_pushed: bool = False


def roll_d100(
    skill_value: int,
    bonus_dice: int = 0,
    difficulty: str = "regular",
    rng: Optional[random.Random] = None,
) -> DiceRollResult:
    """Roll D100 against a skill value.

    Args:
        skill_value: The character's skill value (1-99).
        bonus_dice: Positive = bonus dice, negative = penalty dice.
        difficulty: "regular", "hard", or "extreme".
        rng: Optional Random instance for deterministic testing.
    """
    r = rng or random.Random()
    units = r.randint(0, 9)
    num_tens = 1 + abs(bonus_dice)
    tens_rolls = [r.randint(0, 9) for _ in range(num_tens)]

    if bonus_dice > 0:
        chosen_tens = min(tens_rolls)
    elif bonus_dice < 0:
        chosen_tens = max(tens_rolls)
    else:
        chosen_tens = tens_rolls[0]

    roll = chosen_tens * 10 + units
    if roll == 0:
        roll = 100

    target = skill_value
    if difficulty == "hard":
        target = skill_value // 2
    elif difficulty == "extreme":
        target = skill_value // 5

    result = _evaluate_result(roll, skill_value, target)

    return DiceRollResult(
        roll=roll,
        target=target,
        skill_value=skill_value,
        result=result,
        bonus_dice=bonus_dice,
        all_tens_dice=tens_rolls,
    )


def _evaluate_result(roll: int, skill: int, target: int) -> CheckResult:
    if roll == 1:
        return CheckResult.CRITICAL_SUCCESS
    if roll >= 100 or (roll >= 96 and skill < 50):
        return CheckResult.FUMBLE
    if roll > target:
        return CheckResult.FAILURE
    if roll <= skill // 5:
        return CheckResult.EXTREME_SUCCESS
    if roll <= skill // 2:
        return CheckResult.HARD_SUCCESS
    return CheckResult.REGULAR_SUCCESS


RESULT_RANK = {
    CheckResult.FUMBLE: 0,
    CheckResult.FAILURE: 1,
    CheckResult.REGULAR_SUCCESS: 2,
    CheckResult.HARD_SUCCESS: 3,
    CheckResult.EXTREME_SUCCESS: 4,
    CheckResult.CRITICAL_SUCCESS: 5,
}


def is_success(result: CheckResult) -> bool:
    return RESULT_RANK[result] >= 2


def opposed_roll(
    active_skill: int,
    passive_skill: int,
    active_bonus: int = 0,
    passive_bonus: int = 0,
    rng: Optional[random.Random] = None,
) -> tuple[DiceRollResult, DiceRollResult, str]:
    """CoC 7e opposed roll. Higher success level wins; ties go to higher skill."""
    active = roll_d100(active_skill, active_bonus, rng=rng)
    passive = roll_d100(passive_skill, passive_bonus, rng=rng)

    a_rank = RESULT_RANK[active.result]
    p_rank = RESULT_RANK[passive.result]

    if a_rank > p_rank:
        winner = "active"
    elif p_rank > a_rank:
        winner = "passive"
    else:
        winner = "active" if active_skill >= passive_skill else "passive"

    return active, passive, winner


def roll_damage(formula: str, rng: Optional[random.Random] = None) -> int:
    """Parse and roll a damage formula like '2d6+1', '1d4', '1d6+1d4'."""
    r = rng or random.Random()
    total = 0
    for part in re.split(r'(?=[+-])', formula.replace(" ", "")):
        if not part:
            continue
        match = re.match(r'^([+-]?)(\d+)d(\d+)$', part)
        if match:
            sign = -1 if match.group(1) == '-' else 1
            count, sides = int(match.group(2)), int(match.group(3))
            total += sign * sum(r.randint(1, sides) for _ in range(count))
        else:
            total += int(part)
    return max(0, total)
