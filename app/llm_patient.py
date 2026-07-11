"""LLM-powered patient reply generation."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.scenarios import load_clinic_profile, load_patient_profile

load_dotenv()

CLINIC_PROFILE = load_clinic_profile()
PATIENT_PROFILE = load_patient_profile()


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
-Stay in character as the patient.
-If the latest agent message is only a recording notice, language notice, hold message, short silence, or other non-actionable system message, do not treat it as the start of the conversation.

-Answer only using the scenario facts and clinic profile.
-Do not invent new medical facts, IDs, dates, addresses, insurance info, office hours, clinic details, or appointments.
-Keep replies short, polite, natural, and conversational for a phone call. Do not sound scripted or overly formal.
-If the healthcare agent asks for information you have, provide it.
-If the healthcare agent asks something unclear or unrelated, ask them to repeat, clarify, or politely redirect back to the scenario goal.
-If the goal is complete and the agent asks if anything else is needed, say the final response.
-If the agent asks how they can help, use the scenario goal to respond naturally.
-Follow the scenario-specific instructions exactly.
-Do not repeatedly ask the same question if it has already been answered.
-If the agent offers to have someone else assist, accept the offer and wait.
-If you are giving the scenario final_response or any clear closing reply with the scenario goal reasonably accomplished, return action "end", not "reply".

Return JSON only in this format:
{{
  "action": "reply",
  "reply": "patient reply here"
}}

The action value must be exactly one of: "wait", "reply", or "end".

Use action="wait" if the latest agent message is only a recording notice, language notice, hold message, silence, background message, or does not invite the patient to speak.
Use action="reply" if the agent asks a question, asks how they can help, asks for patient information, asks for confirmation, or otherwise invites the patient to respond.
Use action="end" if the scenario goal is reasonably complete and the patient is giving the final_response or any clear closing reply.

Scenario:
{json.dumps(scenario, indent=2)}

Patient info:
{json.dumps(PATIENT_PROFILE, indent=2)}

Clinic profile:
{json.dumps(CLINIC_PROFILE, indent=2)}

State:
{json.dumps(state, indent=2)}

Conversation history:
{json.dumps(history, indent=2)}

Latest healthcare agent message:
{agent_text}
""".strip()


def parse_llm_response(raw_text: str) -> tuple[str, str, bool]:
    """Parse the LLM JSON response into action, reply, and should_end."""

    try:
        data = json.loads(raw_text)
        action = data.get("action", "reply").strip().lower()
        reply = data.get("reply", "").strip()
    except json.JSONDecodeError:
        print("LLM returned invalid JSON:")
        print(raw_text)

        action = "reply"
        reply = "Sorry, could you repeat that?"

    if action not in {"wait", "reply", "end"}:
        action = "reply"

    should_end = action == "end"

    return action, reply, should_end


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
        reply = (
            scenario.get("final_response") or "No, thank you. I appreciate your help."
        )

        state["turn_count"] = next_turn_count

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
        max_output_tokens=180,
    )

    raw_text = response.output_text.strip()

    # Parse llm response
    action, reply, should_end = parse_llm_response(raw_text)

    if action == "wait":
        return "__WAIT__", False

    if not reply:
        reply = "Sorry, could you repeat that?"
        should_end = False

    # Save memory after we know the final reply.
    state["turn_count"] = next_turn_count

    return reply, should_end
