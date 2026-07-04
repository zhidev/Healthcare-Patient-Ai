"""Run one local LLM patient test without Twilio."""

import os

from dotenv import load_dotenv

from app.main import generate_patient_reply
from app.scenarios import load_scenario


def main():
    load_dotenv()

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

    agent_text = "May I have your name?"

    reply, should_end = generate_patient_reply(
        agent_text=agent_text,
        scenario=scenario,
        state=state,
    )

    print("Agent:", agent_text)
    print("LLM Patient:", reply)
    print("Should end:", should_end)


if __name__ == "__main__":
    main()