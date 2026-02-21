"""YAML scenario loader with validation."""

from pathlib import Path

import yaml

from backend.scenario.models import Scenario


class ScenarioLoader:
    def __init__(self, scenarios_dir: str = "scenarios"):
        self.base_dir = Path(scenarios_dir)

    def load(self, scenario_id: str) -> Scenario:
        scenario_dir = self.base_dir / scenario_id
        yaml_path = scenario_dir / "scenario.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Scenario not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return Scenario(**data)

    def list_scenarios(self) -> list[dict]:
        results = []
        if not self.base_dir.exists():
            return results
        for d in sorted(self.base_dir.iterdir()):
            yaml_path = d / "scenario.yaml"
            if d.is_dir() and yaml_path.exists():
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                meta = data.get("meta", {})
                meta["id"] = meta.get("id", d.name)
                results.append(meta)
        return results
