"""Tests for the game state machine."""

import pytest

from backend.core.state_machine import GamePhase, StateMachine


class TestStateMachine:
    def test_initial_state(self):
        sm = StateMachine()
        assert sm.phase == GamePhase.LOBBY

    def test_valid_transition(self):
        sm = StateMachine()
        sm.transition(GamePhase.SCENARIO_INTRO)
        assert sm.phase == GamePhase.SCENARIO_INTRO

    def test_invalid_transition(self):
        sm = StateMachine()
        with pytest.raises(ValueError):
            sm.transition(GamePhase.COMBAT)

    def test_full_game_flow(self):
        sm = StateMachine()
        assert not sm.is_active
        sm.transition(GamePhase.SCENARIO_INTRO)
        assert sm.is_active
        sm.transition(GamePhase.EXPLORATION)
        assert sm.is_active
        sm.transition(GamePhase.ENDING)
        assert sm.is_active
        sm.transition(GamePhase.FINISHED)
        assert not sm.is_active

    def test_combat_to_exploration(self):
        sm = StateMachine()
        sm.transition(GamePhase.SCENARIO_INTRO)
        sm.transition(GamePhase.EXPLORATION)
        sm.transition(GamePhase.COMBAT)
        sm.transition(GamePhase.EXPLORATION)
        assert sm.phase == GamePhase.EXPLORATION
