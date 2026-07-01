import json
from pathlib import Path

from app.patient_bot import get_patient_reply


def load_scenario(path: str) -> dict:
    scenario_path = Path(path)

    with scenario_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def add_transcript_line(transcript: list[str], speaker: str, text: str) -> None:
    transcript.append(f"{speaker}: {text}")


def save_transcript(transcript: list[str], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write("\n".join(transcript))


def main():
    scenario = load_scenario("data/scenarios/01_simple_scheduling.json")
    state = {}
    transcript = []

    first_message = scenario["first_patient_message"]

    print("Patient Bot:", first_message)
    add_transcript_line(transcript, "Patient Bot", first_message)
    print()

    try:
        while True:
            agent_text = input("Agent: ")

            if agent_text.lower() in ["quit", "exit"]:
                break

            add_transcript_line(transcript, "Agent", agent_text)

            reply, should_end = get_patient_reply(
                agent_text=agent_text, scenario=scenario, state=state
            )

            print("Patient Bot:", reply)
            add_transcript_line(transcript, "Patient Bot", reply)
            print()

            if should_end:
                break

    except KeyboardInterrupt:
        print("\nConversation interrupted by user.")

    finally:
        save_transcript(
            transcript, "outputs/transcripts/01_simple_scheduling_local.txt"
        )
        print("Transcript saved.")


if __name__ == "__main__":
    main()
