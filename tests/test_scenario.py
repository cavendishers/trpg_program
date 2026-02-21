"""Tests for the scenario loader and plot guardian."""

import tempfile
from pathlib import Path

import yaml

from backend.scenario.loader import ScenarioLoader
from backend.scenario.models import Scenario
from backend.scenario.plot_guardian import PlotGuardian


SAMPLE_SCENARIO = {
    "meta": {
        "id": "test_scenario",
        "title": "测试剧本",
        "era": "1920s",
        "player_count": {"min": 1, "max": 4},
        "difficulty": "introductory",
        "synopsis": "测试用剧本",
    },
    "keeper_guide": "这是一个测试剧本。",
    "key_plot_points": [
        {"id": "start", "description": "开始调查"},
        {"id": "middle", "description": "深入调查", "depends_on": ["start"]},
    ],
    "endings": [
        {"id": "victory", "condition": "完成所有调查", "san_reward": "1d6"},
    ],
    "npcs": {
        "npc1": {
            "name": "测试NPC",
            "role": "witness",
            "knows": ["关键信息"],
        },
    },
    "locations": {
        "loc1": {"name": "测试地点", "atmosphere": "阴森"},
    },
    "clues": {
        "clue1": {"description": "关键线索", "importance": "critical"},
        "clue2": {"description": "普通线索", "importance": "normal"},
    },
}


class TestScenarioLoader:
    def test_load_scenario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario_dir = Path(tmpdir) / "test_scenario"
            scenario_dir.mkdir()
            yaml_path = scenario_dir / "scenario.yaml"
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(SAMPLE_SCENARIO, f, allow_unicode=True)

            loader = ScenarioLoader(tmpdir)
            scenario = loader.load("test_scenario")
            assert scenario.meta.title == "测试剧本"
            assert len(scenario.key_plot_points) == 2
            assert "npc1" in scenario.npcs

    def test_list_scenarios(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario_dir = Path(tmpdir) / "test_scenario"
            scenario_dir.mkdir()
            with open(scenario_dir / "scenario.yaml", "w", encoding="utf-8") as f:
                yaml.dump(SAMPLE_SCENARIO, f, allow_unicode=True)

            loader = ScenarioLoader(tmpdir)
            results = loader.list_scenarios()
            assert len(results) == 1
            assert results[0]["title"] == "测试剧本"


class TestPlotGuardian:
    def _make_scenario(self) -> Scenario:
        return Scenario(**SAMPLE_SCENARIO)

    def test_progress_prompt_initial(self):
        guardian = PlotGuardian(self._make_scenario())
        prompt = guardian.generate_progress_prompt()
        assert "未发现关键线索" in prompt
        assert "关键线索" in prompt

    def test_discover_clue(self):
        guardian = PlotGuardian(self._make_scenario())
        guardian.update_clue_status("clue1")
        prompt = guardian.generate_progress_prompt()
        assert "已发现线索" in prompt

    def test_complete_plot_point(self):
        guardian = PlotGuardian(self._make_scenario())
        guardian.update_plot_point("start")
        prompt = guardian.generate_progress_prompt()
        assert "深入调查" in prompt  # Next available point

    def test_ending_not_triggered_early(self):
        guardian = PlotGuardian(self._make_scenario())
        assert guardian.check_ending_conditions() is None

    def test_ending_triggered(self):
        guardian = PlotGuardian(self._make_scenario())
        guardian.update_clue_status("clue1")
        guardian.update_plot_point("start")
        guardian.update_plot_point("middle")
        ending = guardian.check_ending_conditions()
        assert ending is not None
        assert ending.id == "victory"
