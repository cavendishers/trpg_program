"""Tests for the CoC 7e dice system."""

import random

from backend.rules.dice import (
    CheckResult,
    is_success,
    opposed_roll,
    roll_d100,
    roll_damage,
)


# roll_d100 call order: units first, then tens dice(s)
# _make_rng values: [units, tens1, tens2, ...]

class TestRollD100:
    def test_critical_success(self):
        result = roll_d100(50, rng=_make_rng([1, 0]))  # units=1, tens=0 -> 01
        assert result.roll == 1
        assert result.result == CheckResult.CRITICAL_SUCCESS

    def test_fumble_low_skill(self):
        result = roll_d100(30, rng=_make_rng([6, 9]))  # units=6, tens=9 -> 96
        assert result.roll == 96
        assert result.result == CheckResult.FUMBLE

    def test_fumble_high_skill(self):
        result = roll_d100(60, rng=_make_rng([6, 9]))  # 96, skill>=50 -> failure
        assert result.roll == 96
        assert result.result == CheckResult.FAILURE

        result = roll_d100(60, rng=_make_rng([0, 0]))  # 00+0 = 100
        assert result.roll == 100
        assert result.result == CheckResult.FUMBLE

    def test_regular_success(self):
        result = roll_d100(55, rng=_make_rng([0, 4]))  # units=0, tens=4 -> 40
        assert result.roll == 40
        assert result.result == CheckResult.REGULAR_SUCCESS

    def test_hard_success(self):
        result = roll_d100(60, rng=_make_rng([5, 2]))  # units=5, tens=2 -> 25
        assert result.roll == 25
        assert result.result == CheckResult.HARD_SUCCESS

    def test_extreme_success(self):
        result = roll_d100(60, rng=_make_rng([0, 1]))  # units=0, tens=1 -> 10
        assert result.roll == 10
        assert result.result == CheckResult.EXTREME_SUCCESS

    def test_failure(self):
        result = roll_d100(30, rng=_make_rng([0, 5]))  # units=0, tens=5 -> 50
        assert result.roll == 50
        assert result.result == CheckResult.FAILURE

    def test_hard_difficulty(self):
        result = roll_d100(60, difficulty="hard", rng=_make_rng([5, 2]))  # 25, target=30
        assert result.target == 30
        assert is_success(result.result)

    def test_extreme_difficulty(self):
        result = roll_d100(60, difficulty="extreme", rng=_make_rng([5, 1]))  # 15, target=12
        assert result.target == 12
        assert not is_success(result.result)

    def test_bonus_dice_takes_lower(self):
        # bonus=1: units first, then 2 tens dice
        result = roll_d100(50, bonus_dice=1, rng=_make_rng([5, 7, 2]))
        # units=5, tens_rolls=[7,2], pick min=2 -> 25
        assert result.roll == 25
        assert len(result.all_tens_dice) == 2

    def test_penalty_dice_takes_higher(self):
        result = roll_d100(50, bonus_dice=-1, rng=_make_rng([5, 2, 7]))
        # units=5, tens_rolls=[2,7], pick max=7 -> 75
        assert result.roll == 75
        assert len(result.all_tens_dice) == 2


class TestOpposedRoll:
    def test_higher_success_wins(self):
        # Active: units=0, tens=1 -> 10 (extreme@60)
        # Passive: units=5, tens=3 -> 35 (regular@40)
        active, passive, winner = opposed_roll(
            60, 40, rng=_make_rng([0, 1, 5, 3]),
        )
        assert winner == "active"

    def test_tie_goes_to_higher_skill(self):
        # Active: units=0, tens=4 -> 40 (regular@60)
        # Passive: units=0, tens=3 -> 30 (regular@40)
        active, passive, winner = opposed_roll(
            60, 40, rng=_make_rng([0, 4, 0, 3]),
        )
        assert winner == "active"


class TestRollDamage:
    def test_simple(self):
        rng = random.Random(42)
        result = roll_damage("1d6", rng=rng)
        assert 1 <= result <= 6

    def test_complex_formula(self):
        rng = random.Random(42)
        result = roll_damage("2d6+1", rng=rng)
        assert result >= 3

    def test_zero(self):
        assert roll_damage("0") == 0

    def test_constant(self):
        assert roll_damage("3") == 3


def _make_rng(values: list[int]):
    """Create a mock RNG that returns values in sequence."""
    it = iter(values)

    class MockRng:
        def randint(self, a, b):
            return next(it)

    return MockRng()
