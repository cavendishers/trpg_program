"""Game phase state machine."""

from enum import Enum


class GamePhase(str, Enum):
    LOBBY = "lobby"              # Waiting for players, character creation
    SCENARIO_INTRO = "intro"     # KP introduces the scenario
    EXPLORATION = "exploration"  # Free exploration, investigation
    COMBAT = "combat"            # Combat encounter
    ENDING = "ending"            # Scenario conclusion
    FINISHED = "finished"        # Game over


# Valid transitions
_TRANSITIONS: dict[GamePhase, set[GamePhase]] = {
    GamePhase.LOBBY: {GamePhase.SCENARIO_INTRO},
    GamePhase.SCENARIO_INTRO: {GamePhase.EXPLORATION},
    GamePhase.EXPLORATION: {GamePhase.COMBAT, GamePhase.ENDING},
    GamePhase.COMBAT: {GamePhase.EXPLORATION, GamePhase.ENDING},
    GamePhase.ENDING: {GamePhase.FINISHED},
    GamePhase.FINISHED: set(),
}


class StateMachine:
    def __init__(self):
        self.phase = GamePhase.LOBBY

    def can_transition(self, target: GamePhase) -> bool:
        return target in _TRANSITIONS.get(self.phase, set())

    def transition(self, target: GamePhase) -> GamePhase:
        if not self.can_transition(target):
            raise ValueError(
                f"Cannot transition from {self.phase} to {target}"
            )
        self.phase = target
        return self.phase

    @property
    def is_active(self) -> bool:
        return self.phase not in (GamePhase.LOBBY, GamePhase.FINISHED)
