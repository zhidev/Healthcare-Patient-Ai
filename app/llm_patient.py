"""LLM-powered patient reply generation."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from app.patient_bot import add_history

load_dotenv()


def build_patient_prompt(
    scenario: dict,
    state: dict,
    agent_text: str,
) -> str:
    """Build the prompt for the LLM patient."""

    history = state.get("history", [])

    return f"""
You are acting as a fake patient/member in a healthcare phone call.

Your job:
- Stay in character as the patient.
- Answer only using the scenario facts.
- Do not invent new medical facts, IDs, dates, addresses, insurance info, or appointments.
- Keep replies short and natural for a phone call.
- If the healthcare agent asks for information you have, provide it.
- If the healthcare agent asks something unclear, ask them to repeat or clarify.
- If the agent tries to end the call too early, politely keep going until the goal is complete.
- If the goal is complete and the agent asks if anything else is needed, say the final response.

Return JSON only in this format:
{{
  "reply": "patient reply here",
  "should_end": false
}}

Scenario:
{json.dumps(scenario, indent=2)}

State:
{json.dumps(state, indent=2)}

Conversation history:
{json.dumps(history, indent=2)}

Latest healthcare agent message:
{agent_text}
""".strip()


def get_llm_patient_reply(
    agent_text: str,
    scenario: dict,
    state: dict,
) -> tuple[str, bool]:
    """Generate a patient reply using an LLM."""

    if os.getenv("LLM_PATIENT_ENABLED", "false").lower() != "true":
        raise RuntimeError("LLM patient mode is disabled.")

    next_turn_count = state.get("turn_count", 0) + 1

    min_turns = scenario.get("min_turns", 5)
    max_turns = scenario.get("max_turns", 14)

    # Safety guard: do not let the call run forever.
    # This also avoids spending another LLM call when we already hit max turns.
    if next_turn_count >= max_turns:
        reply = scenario["final_response"]

        state["turn_count"] = next_turn_count
        add_history(state, "agent", agent_text)
        add_history(state, "patient", reply)

        return reply, True

    client = OpenAI()

    prompt = build_patient_prompt(
        scenario=scenario,
        state=state,
        agent_text=agent_text,
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        input=prompt,
        max_output_tokens=80,
    )

    raw_text = response.output_text.strip()

    try:
        data = json.loads(raw_text)
        reply = data.get("reply", "").strip()
        should_end = bool(data.get("should_end", False))
    except json.JSONDecodeError:
        reply = raw_text
        should_end = False

    if not reply:
        reply = "Sorry, could you repeat that?"
        should_end = False

    # Do not let the LLM end too early.
    if should_end and next_turn_count < min_turns:
        reply = "I just want to make sure everything is set before we finish."
        should_end = False

    # Save memory after we know the final reply.
    state["turn_count"] = next_turn_count
    add_history(state, "agent", agent_text)
    add_history(state, "patient", reply)

    return reply, should_end
