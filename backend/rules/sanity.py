"""CoC 7e sanity check system."""

import random as _random
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from backend.rules.dice import roll_damage


class MadnessType(str, Enum):
    BOUT_REAL_TIME = "bout_real_time"
    BOUT_SUMMARY = "bout_summary"
    INDEFINITE = "indefinite"


class SanityResult(BaseModel):
    roll: int
    current_san: int
    success: bool
    san_lost: int
    new_san: int
    madness: Optional[MadnessType] = None


def san_check(
    current_san: int,
    san_loss_success: str,
    san_loss_failure: str,
    rng: Optional[_random.Random] = None,
) -> SanityResult:
    """Perform a sanity check.

    Args:
        current_san: Character's current SAN value.
        san_loss_success: Damage formula on success (e.g. "0", "1d4").
        san_loss_failure: Damage formula on failure (e.g. "1d6", "1d10").
    """
    r = rng or _random.Random()
    roll = r.randint(1, 100)
    success = roll <= current_san

    loss_formula = san_loss_success if success else san_loss_failure
    san_lost = 0 if loss_formula == "0" else roll_damage(loss_formula, rng=r)
    new_san = max(0, current_san - san_lost)

    madness = None
    if san_lost >= 5:
        madness = MadnessType.BOUT_REAL_TIME
    if new_san == 0:
        madness = MadnessType.INDEFINITE

    return SanityResult(
        roll=roll,
        current_san=current_san,
        success=success,
        san_lost=san_lost,
        new_san=new_san,
        madness=madness,
    )


def check_indefinite_insanity(current_san: int, starting_san: int) -> bool:
    """Check if character has lost 1/5 of starting SAN in 24h (simplified)."""
    return (starting_san - current_san) >= (starting_san // 5)
