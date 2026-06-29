import json
from pathlib import Path

from app.patient_bot import get_patient_reply


def load_scenario(path: str) -> dict:
    scenario_path = Path(path)

    with scenario_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    scenario = load_scenario("data/scenarios/01_simple_scheduling.json")
    state = {}

    print("Patient Bot:", scenario["first_patient_message"])
    print()

    while True:
        agent_text = input("Agent: ")

        if agent_text.lower() in ["quit", "exit"]:
            break

        reply, should_end = get_patient_reply(
            agent_text=agent_text,
            scenario=scenario,
            state=state
        )

        print("Patient Bot:", reply)
        print()

        if should_end:
            break


if __name__ == "__main__":
    main()