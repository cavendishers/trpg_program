"""Plot guardian - tracks scenario progress and generates AI prompts."""

from typing import Optional

from backend.scenario.models import Scenario, Ending


class PlotGuardian:
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.discovered_clues: set[str] = set()
        self.completed_points: set[str] = set()

    def update_clue_status(self, clue_id: str, discovered: bool = True):
        if discovered:
            self.discovered_clues.add(clue_id)
        else:
            self.discovered_clues.discard(clue_id)

    def update_plot_point(self, point_id: str, completed: bool = True):
        if completed:
            self.completed_points.add(point_id)
        else:
            self.completed_points.discard(point_id)

    def generate_progress_prompt(self) -> str:
        all_clues = set(self.scenario.clues.keys())
        critical = {
            cid for cid, c in self.scenario.clues.items()
            if c.importance == "critical"
        }
        missing_critical = critical - self.discovered_clues
        discovered_names = [
            self.scenario.clues[c].description
            for c in self.discovered_clues if c in self.scenario.clues
        ]
        missing_names = [
            self.scenario.clues[c].description
            for c in missing_critical if c in self.scenario.clues
        ]

        # Current plot point (first uncompleted with satisfied dependencies)
        current_point = None
        for pp in self.scenario.key_plot_points:
            if pp.id in self.completed_points:
                continue
            deps_met = all(d in self.completed_points for d in pp.depends_on)
            if deps_met:
                current_point = pp
                break

        lines = ["[剧情进度]"]
        if discovered_names:
            lines.append(f"已发现线索：{', '.join(discovered_names)}")
        if missing_names:
            lines.append(f"未发现关键线索：{', '.join(missing_names)}")
        if current_point:
            lines.append(f"当前剧情节点：{current_point.description}")
        if missing_critical and current_point:
            lines.append("建议适时引导玩家发现关键线索。")

        return "\n".join(lines)

    def check_ending_conditions(self) -> Optional[Ending]:
        """Simple check - returns first matching ending or None.
        Actual condition evaluation is left to the AI KP."""
        all_critical = {
            cid for cid, c in self.scenario.clues.items()
            if c.importance == "critical"
        }
        all_points = {pp.id for pp in self.scenario.key_plot_points}

        if all_critical <= self.discovered_clues and all_points <= self.completed_points:
            for ending in self.scenario.endings:
                if ending.id == "victory":
                    return ending
        return None
