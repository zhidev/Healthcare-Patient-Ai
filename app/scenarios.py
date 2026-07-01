"""Scenario loading helpers."""

import json
from pathlib import Path


SCENARIO_DIR = Path("data/scenarios")


def load_scenario(scenario_id: str) -> dict:
    """Load a scenario JSON file by scenario id."""
    path = SCENARIO_DIR / f"{scenario_id}.json"

    if not path.exists():
        raise FileNotFoundError(f"Scenario not found: {scenario_id}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)