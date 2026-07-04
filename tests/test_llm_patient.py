"""Tests for LLM patient prompt building."""

import pytest

from app.llm_patient import build_patient_prompt, get_llm_patient_reply

SCENARIO = {
    "id": "01_simple_scheduling",
    "type": "appointment_scheduling",
    "first_patient_message": "Hi, I would like to schedule an appointment.",
    "patient": {
        "name": "Jane Doe",
        "dob": "January 1st, 1990",
        "member_id": "M123456789",
    },
    "goal": "Schedule the earliest available appointment",
    "reason": "Routine checkup",
    "final_response": "No, thank you. That's all.",
    "min_turns": 5,
    "max_turns": 14,
}


def test_build_patient_prompt_includes_scenario_and_agent_message():
    state = {
        "turn_count": 1,
        "history": [
            {
                "speaker": "patient",
                "text": "Hi, I would like to schedule an appointment.",
            }
        ],
    }

    prompt = build_patient_prompt(
        scenario=SCENARIO,
        state=state,
        agent_text="May I have your name?",
    )

    assert "You are acting as a fake patient/member" in prompt
    assert "Jane Doe" in prompt
    assert "M123456789" in prompt
    assert "May I have your name?" in prompt
    assert "Return JSON only" in prompt


def test_llm_patient_disabled_raises_error(monkeypatch):
    monkeypatch.setenv("LLM_PATIENT_ENABLED", "false")

    with pytest.raises(RuntimeError):
        get_llm_patient_reply(
            agent_text="May I have your name?",
            scenario=SCENARIO,
            state={},
        )
