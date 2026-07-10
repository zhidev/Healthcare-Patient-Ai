from app import transcript_logger


def test_add_history_skips_blank_and_duplicate_messages():
    state = {}

    transcript_logger.add_history(state, "agent", "")
    transcript_logger.add_history(state, "agent", "   ")

    assert state.get("history") is None

    transcript_logger.add_history(state, "agent", "How may I help you?")
    transcript_logger.add_history(state, "agent", "How may I help you?")

    assert state["history"] == [
        {
            "speaker": "agent",
            "text": "How may I help you?",
        }
    ]


def test_save_transcript_writes_agent_and_patient(tmp_path, monkeypatch):
    monkeypatch.setattr(transcript_logger, "TRANSCRIPT_DIR", tmp_path)

    state = {
        "history": [
            {"speaker": "agent", "text": "How may I help you?"},
            {"speaker": "patient", "text": "I need to schedule an appointment."},
        ]
    }

    path = transcript_logger.save_transcript(
        provider="signalwire",
        scenario_id="01_simple_scheduling",
        call_id="test-call-123",
        state=state,
    )

    content = path.read_text(encoding="utf-8")

    assert "Provider: signalwire" in content
    assert "Scenario: 01_simple_scheduling" in content
    assert "Call ID: test-call-123" in content
    assert "Agent: How may I help you?" in content
    assert "Patient: I need to schedule an appointment." in content