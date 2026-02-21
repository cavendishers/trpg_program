"""Tests for skill check and sanity systems."""

from backend.rules.skill_check import perform_check, push_roll
from backend.rules.sanity import san_check, MadnessType


def _make_rng(values):
    it = iter(values)

    class MockRng:
        def randint(self, a, b):
            return next(it)

    return MockRng()


# roll_d100 call order: units, tens
class TestSkillCheck:
    def test_success(self):
        outcome = perform_check("侦查", 55, rng=_make_rng([0, 3]))  # units=0, tens=3 -> 30
        assert outcome.success
        assert outcome.skill_name == "侦查"

    def test_failure_can_push(self):
        outcome = perform_check("侦查", 30, rng=_make_rng([0, 5]))  # units=0, tens=5 -> 50
        assert not outcome.success
        assert outcome.can_push

    def test_fumble_cannot_push(self):
        outcome = perform_check("侦查", 30, rng=_make_rng([8, 9]))  # units=8, tens=9 -> 98
        assert not outcome.success
        assert not outcome.can_push

    def test_cthulhu_mythos_cannot_push(self):
        outcome = perform_check("Cthulhu Mythos", 30, rng=_make_rng([0, 5]))  # 50
        assert not outcome.can_push


class TestPushRoll:
    def test_pushed_roll_marked(self):
        result = push_roll("侦查", 55, rng=_make_rng([0, 3]))  # 30
        assert result.roll_result.is_pushed
        assert result.success

    def test_pushed_fumble(self):
        result = push_roll("侦查", 30, rng=_make_rng([8, 9]))  # 98
        assert result.fumbled


class TestSanityCheck:
    def test_success_no_loss(self):
        result = san_check(50, "0", "1d6", rng=_make_rng([30]))
        assert result.success
        assert result.san_lost == 0
        assert result.new_san == 50

    def test_failure_with_loss(self):
        result = san_check(50, "0", "1d6", rng=_make_rng([60, 4]))
        assert not result.success
        assert result.san_lost == 4
        assert result.new_san == 46

    def test_bout_of_madness(self):
        result = san_check(50, "0", "1d6", rng=_make_rng([60, 5]))
        assert result.madness == MadnessType.BOUT_REAL_TIME

    def test_zero_san_indefinite(self):
        result = san_check(3, "0", "1d6", rng=_make_rng([60, 5]))
        assert result.new_san == 0
        assert result.madness == MadnessType.INDEFINITE
