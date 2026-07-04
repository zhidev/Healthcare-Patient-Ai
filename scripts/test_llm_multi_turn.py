"""Run a short multi-turn LLM patient test without Twilio."""

import os

from dotenv import load_dotenv

from app.main import generate_patient_reply
from app.scenarios import load_scenario

MAX_TEST_TURNS = 3


AGENT_MESSAGES = [
    "May I have your name?",
    "May I have your member ID?",
    "What is your date of birth?",
]


def main():
    load_dotenv(override=True)

    os.environ["LLM_PATIENT_ENABLED"] = "true"

    scenario = load_scenario("01_simple_scheduling")

    state = {
        "turn_count": 0,
        "history": [
            {
                "speaker": "patient",
                "text": scenario["first_patient_message"],
            }
        ],
    }

    print("Patient:", scenario["first_patient_message"])
    print()

    for agent_text in AGENT_MESSAGES[:MAX_TEST_TURNS]:
        print("Agent:", agent_text)

        reply, should_end = generate_patient_reply(
            agent_text=agent_text,
            scenario=scenario,
            state=state,
        )

        print("LLM Patient:", reply)
        print("Should end:", should_end)
        print("Turn count:", state.get("turn_count"))

        print()

        # Store history manually for this local test.
        # state["history"].append(
        #     {
        #         "speaker": "agent",
        #         "text": agent_text,
        #     }
        # )
        # state["history"].append(
        #     {
        #         "speaker": "patient",
        #         "text": reply,
        #     }
        # )

        # state["turn_count"] = state.get("turn_count", 0) + 1

        if should_end:
            print("Final state, Breaking:", state)
            break

    print("Final turn count:", state.get("turn_count"))
    print("History length:", len(state.get("history", [])))


if __name__ == "__main__":
    main()
