"""Scenario loading helpers."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SCENARIO_DIR = BASE_DIR / "data" / "scenarios"
CLINIC_PROFILE_PATH = SCENARIO_DIR / "clinic_profile.json"
PATIENT_PROFILE_PATH = SCENARIO_DIR / "patient_profile.json"


def load_scenario(scenario_id: str) -> dict:
    """Load a scenario JSON file by scenario id."""
    path = SCENARIO_DIR / f"{scenario_id}.json"

    if not path.exists():
        raise FileNotFoundError(f"Scenario not found: {scenario_id}")

    with path.open("r", encoding="utf-8") as file:
        scenario = json.load(file)

    patient_profile = load_patient_profile()
    scenario["patient"] = patient_profile["patient"]

    return scenario


def load_clinic_profile() -> dict:
    """Load shared clinic profile JSON."""

    if not CLINIC_PROFILE_PATH.exists():
        raise FileNotFoundError(f"Clinic profile not found: {CLINIC_PROFILE_PATH}")

    with CLINIC_PROFILE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_patient_profile() -> dict:
    """Load shared patient profile JSON."""

    if not PATIENT_PROFILE_PATH.exists():
        raise FileNotFoundError(f"Patient profile not found: {PATIENT_PROFILE_PATH}")

    with PATIENT_PROFILE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
