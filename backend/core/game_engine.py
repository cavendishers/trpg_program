"""Game engine - main loop orchestration."""

import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.ai.keeper_engine import KeeperEngine
from backend.ai.providers.base import AIProviderBase
from backend.ai.response_parser import GameDirective, KPResponse
from backend.character.models import CoCCharacter
from backend.character.service import CharacterService
from backend.core.state_machine import GamePhase, StateMachine
from backend.core.turn_manager import TurnManager, TurnMode
from backend.rules.dice import roll_d100, is_success, roll_damage
from backend.rules.sanity import san_check
from backend.rules.skill_check import perform_check
from backend.scenario.loader import ScenarioLoader
from backend.scenario.models import Scenario
from backend.scenario.plot_guardian import PlotGuardian

SAVES_DIR = Path(__file__).resolve().parent.parent.parent / "saves"


class GameSession(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    scenario_id: str = ""
    phase: GamePhase = GamePhase.LOBBY


class DirectiveResult(BaseModel):
    directive_type: str
    description: str
    details: dict = {}


class GameEngine:
    def __init__(
        self,
        provider: AIProviderBase,
        scenario: Scenario,
        characters: Optional[CharacterService] = None,
    ):
        self.scenario = scenario
        self.characters = characters or CharacterService()
        self.state = StateMachine()
        self.guardian = PlotGuardian(scenario)
        self.keeper = KeeperEngine(provider, scenario)
        self.session = GameSession(scenario_id=scenario.meta.id)
        self.turn_manager = TurnManager()

    def start_game(self) -> GamePhase:
        self.state.transition(GamePhase.SCENARIO_INTRO)
        self.session.phase = self.state.phase
        return self.state.phase

    def begin_exploration(self) -> GamePhase:
        self.state.transition(GamePhase.EXPLORATION)
        self.session.phase = self.state.phase
        return self.state.phase

    async def generate_opening(self) -> dict:
        """Generate the AI KP's opening narrative for the scenario."""
        party = self.characters.list_party()
        progress = self.guardian.generate_progress_prompt()

        opening_prompt = (
            "[系统] 游戏开始。请作为守密人介绍剧本开场：\n"
            "1. 描述故事背景和初始场景\n"
            "2. 营造氛围，引导玩家进入角色\n"
            "3. 给出玩家可以采取的初始行动提示\n"
            "不要请求任何检定，这是纯叙事开场。"
        )

        kp_resp = await self.keeper.generate_response(
            player_input=opening_prompt,
            characters=party,
            plot_progress=progress,
            turn_state=self.turn_manager.to_dict(),
        )

        return {
            "narrative": kp_resp.narrative,
            "atmosphere": kp_resp.atmosphere,
            "npc_actions": [a.model_dump() for a in kp_resp.npc_actions],
            "phase": self.state.phase.value,
            "turn_state": self.turn_manager.to_dict(),
        }

    async def generate_party(self, count: int = 3) -> list:
        """Use AI to generate a party of investigators suited for the scenario."""
        era = getattr(self.scenario.meta, "era", "1920s")
        title = self.scenario.meta.title
        prompt = (
            f"[系统] 请为剧本《{title}》（{era}）生成 {count} 名调查员。\n"
            "对每个角色，只返回 JSON 数组，每个元素包含：\n"
            '{"name": "角色名", "occupation": "职业", "age": 年龄}\n'
            "角色应该职业互补，适合这个剧本的背景。只返回 JSON 数组，不要其他内容。"
        )
        ai_resp = await self.keeper.provider.generate([
            {"role": "user", "content": prompt}
        ])
        import re
        match = re.search(r"\[.*\]", ai_resp.content, re.DOTALL)
        if not match:
            return [self.characters.create_pc(
                name=f"调查员{i+1}", player_name="Player 1", occupation="侦探"
            ) for i in range(count)]
        try:
            specs = json.loads(match.group())
        except json.JSONDecodeError:
            return [self.characters.create_pc(
                name=f"调查员{i+1}", player_name="Player 1", occupation="侦探"
            ) for i in range(count)]
        result = []
        for spec in specs[:count]:
            char = self.characters.create_pc(
                name=spec.get("name", f"调查员{len(result)+1}"),
                player_name="Player 1",
                occupation=spec.get("occupation", ""),
                age=spec.get("age", 25),
            )
            result.append(char)
        return result

    async def process_player_input(
        self, player_input: str, character_id: str = ""
    ) -> dict:
        """Main game loop: player input -> AI -> directives -> results."""
        # Validate actor turn in combat mode
        if (
            self.turn_manager.mode == TurnMode.COMBAT
            and character_id
            and not self.turn_manager.can_act(character_id)
        ):
            return {
                "narrative": "",
                "directives": [],
                "continuation": None,
                "atmosphere": None,
                "npc_actions": [],
                "clues_discovered": [],
                "phase": self.state.phase.value,
                "turn_state": self.turn_manager.to_dict(),
                "error": "not_your_turn",
            }

        party = self.characters.list_party()
        progress = self.guardian.generate_progress_prompt()

        # Step 1: Get AI response
        kp_resp = await self.keeper.generate_response(
            player_input=player_input,
            characters=party,
            plot_progress=progress,
            turn_state=self.turn_manager.to_dict(),
        )

        # Step 2: Execute game directives
        results = []
        for directive in kp_resp.game_directives:
            result = self._execute_directive(directive, character_id)
            if result:
                results.append(result)

        # Step 2.5: Handle turn-related directives
        self._handle_turn_directives(kp_resp.game_directives, party)

        # Consume action in combat mode
        if self.turn_manager.mode == TurnMode.COMBAT and character_id:
            self.turn_manager.consume_action(character_id)
            if self.turn_manager.actions_remaining.get(character_id, 0) <= 0:
                self.turn_manager.advance_turn()

        # Step 3: If directives produced results, feed back to AI
        continuation = None
        if results:
            result_text = self._format_results(results)
            continuation = await self.keeper.feed_result(result_text)

        # Step 4: Check for clue discoveries
        discovered = []
        for directive in kp_resp.game_directives:
            if directive.type == "clue_discovered" and directive.clue_id:
                self.guardian.update_clue_status(directive.clue_id)
                clue = self.scenario.clues.get(directive.clue_id)
                discovered.append({
                    "clue_id": directive.clue_id,
                    "description": clue.description if clue else directive.clue_id,
                })

        # Step 5: Check ending conditions
        ending = self.guardian.check_ending_conditions()
        if ending:
            if self.state.can_transition(GamePhase.ENDING):
                self.state.transition(GamePhase.ENDING)
                self.session.phase = self.state.phase

        return {
            "narrative": kp_resp.narrative,
            "directives": [r.model_dump() for r in results],
            "continuation": continuation.narrative if continuation else None,
            "atmosphere": kp_resp.atmosphere,
            "npc_actions": [a.model_dump() for a in kp_resp.npc_actions],
            "clues_discovered": discovered,
            "phase": self.state.phase.value,
            "turn_state": self.turn_manager.to_dict(),
        }

    def _execute_directive(
        self, directive: GameDirective, character_id: str
    ) -> Optional[DirectiveResult]:
        if directive.type == "skill_check":
            return self._handle_skill_check(directive, character_id)
        elif directive.type == "san_check":
            return self._handle_san_check(directive, character_id)
        return None

    def _handle_turn_directives(
        self, directives: list[GameDirective], party: list[CoCCharacter]
    ) -> None:
        """Process turn-related AI directives (mode switch, character switch, etc.)."""
        for d in directives:
            if d.type == "mode_switch":
                if d.mode == "combat":
                    self.turn_manager.init_combat(party)
                elif d.mode == "exploration":
                    self.turn_manager.end_combat()
            elif d.type == "switch_character":
                if d.next_character_id and self.characters.get_character(d.next_character_id):
                    self.turn_manager.force_switch(d.next_character_id)
            elif d.type == "grant_extra_action":
                target = d.target_character or d.next_character_id
                if target:
                    self.turn_manager.grant_extra_action(target, d.action_count)

    def _handle_skill_check(
        self, directive: GameDirective, character_id: str
    ) -> Optional[DirectiveResult]:
        char = self.characters.get_character(character_id)
        if not char:
            return None
        skill = char.skills.get(directive.skill)
        skill_value = skill.current_value if skill else 50
        outcome = perform_check(
            directive.skill, skill_value, directive.difficulty
        )
        return DirectiveResult(
            directive_type="skill_check",
            description=(
                f"{char.name} 进行 {directive.skill} 检定: "
                f"{outcome.roll_result.roll}/{outcome.roll_result.target} "
                f"{'成功' if outcome.success else '失败'}"
            ),
            details={
                "skill": directive.skill,
                "roll": outcome.roll_result.roll,
                "target": outcome.roll_result.target,
                "result": outcome.roll_result.result.value,
                "success": outcome.success,
                "can_push": outcome.can_push,
            },
        )

    def _handle_san_check(
        self, directive: GameDirective, character_id: str
    ) -> Optional[DirectiveResult]:
        char = self.characters.get_character(character_id)
        if not char:
            return None
        result = san_check(
            char.derived.san,
            directive.san_loss_success,
            directive.san_loss_failure,
        )
        self.characters.update_stat(character_id, "san", -result.san_lost)
        return DirectiveResult(
            directive_type="san_check",
            description=(
                f"{char.name} 理智检定: {result.roll}/{result.current_san} "
                f"{'成功' if result.success else '失败'}, "
                f"失去 {result.san_lost} 点理智"
            ),
            details={
                "roll": result.roll,
                "current_san": result.current_san,
                "success": result.success,
                "san_lost": result.san_lost,
                "new_san": result.new_san,
                "madness": result.madness.value if result.madness else None,
            },
        )

    def _format_results(self, results: list[DirectiveResult]) -> str:
        lines = ["[系统] 判定结果："]
        for r in results:
            lines.append(f"- {r.description}")
        return "\n".join(lines)

    def to_save_data(self) -> dict:
        """Serialize full game state for saving."""
        chars_data = {}
        for cid, char in self.characters._characters.items():
            chars_data[cid] = char.model_dump()
        return {
            "session": self.session.model_dump(),
            "phase": self.state.phase.value,
            "scenario_id": self.scenario.meta.id,
            "scenario_title": self.scenario.meta.title,
            "characters": chars_data,
            "keeper_history": self.keeper.history,
            "keeper_tokens": self.keeper._total_tokens,
            "discovered_clues": list(self.guardian.discovered_clues),
            "completed_points": list(self.guardian.completed_points),
            "turn_state": self.turn_manager.to_dict(),
        }

    def load_save_data(self, data: dict) -> None:
        """Restore game state from saved data."""
        self.state.phase = GamePhase(data["phase"])
        self.session.phase = self.state.phase
        # Restore characters
        self.characters._characters.clear()
        for cid, cdata in data.get("characters", {}).items():
            self.characters._characters[cid] = CoCCharacter(**cdata)
        # Restore keeper state
        self.keeper.history = data.get("keeper_history", [])
        self.keeper._total_tokens = data.get("keeper_tokens", 0)
        # Restore guardian state
        self.guardian.discovered_clues = set(data.get("discovered_clues", []))
        self.guardian.completed_points = set(data.get("completed_points", []))
        # Restore turn state (default to exploration if absent for old saves)
        turn_data = data.get("turn_state")
        if turn_data:
            self.turn_manager = TurnManager.from_dict(turn_data)
        else:
            self.turn_manager = TurnManager()

    def save_to_file(self, slot: str = "auto") -> Path:
        """Save game state to a JSON file."""
        SAVES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{self.session.id}_{slot}.json"
        path = SAVES_DIR / filename
        path.write_text(json.dumps(self.to_save_data(), ensure_ascii=False, indent=2))
        return path

    @staticmethod
    def list_saves(session_id: str) -> list[dict]:
        """List available save files for a session."""
        if not SAVES_DIR.exists():
            return []
        saves = []
        for f in SAVES_DIR.glob(f"{session_id}_*.json"):
            slot = f.stem.split("_", 1)[1]
            stat = f.stat()
            saves.append({
                "slot": slot,
                "filename": f.name,
                "modified": stat.st_mtime,
            })
        return sorted(saves, key=lambda s: s["modified"], reverse=True)

    @staticmethod
    def list_all_saves() -> list[dict]:
        """List all save files across all sessions."""
        if not SAVES_DIR.exists():
            return []
        results = []
        for f in SAVES_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            pc_names = [
                c.get("name", "")
                for c in data.get("characters", {}).values()
                if not c.get("is_npc", False)
            ]
            results.append({
                "filename": f.name,
                "session_id": data.get("session", {}).get("id", ""),
                "scenario_id": data.get("scenario_id", ""),
                "scenario_title": data.get("scenario_title", data.get("scenario_id", "")),
                "phase": data.get("phase", ""),
                "slot": f.stem.split("_", 1)[1] if "_" in f.stem else "unknown",
                "characters": pc_names,
                "modified": f.stat().st_mtime,
            })
        return sorted(results, key=lambda s: s["modified"], reverse=True)

    @staticmethod
    def find_latest_save(scenario_id: str) -> Optional[dict]:
        """Find the most recent auto-save for a given scenario."""
        if not SAVES_DIR.exists():
            return None
        best = None
        best_mtime = 0.0
        for f in SAVES_DIR.glob("*_auto.json"):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if data.get("scenario_id") == scenario_id:
                mtime = f.stat().st_mtime
                if mtime > best_mtime:
                    best_mtime = mtime
                    best = {"filename": f.name, "data": data}
        return best

    def load_from_file(self, slot: str = "auto") -> bool:
        """Load game state from a JSON file. Returns True if successful."""
        filename = f"{self.session.id}_{slot}.json"
        path = SAVES_DIR / filename
        if not path.exists():
            return False
        data = json.loads(path.read_text())
        self.load_save_data(data)
        return True

