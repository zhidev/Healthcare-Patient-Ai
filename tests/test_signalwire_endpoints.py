"""Tests for SignalWire cXML endpoints."""

from fastapi.testclient import TestClient

from app.main import app, CALL_STATES


client = TestClient(app)


def test_signalwire_start_listens_first():
    response = client.post(
        "/signalwire/start/01_simple_scheduling",
        data={"CallSid": "signalwire-test-start"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")

    xml = response.text

    assert "<Response>" in xml
    assert "<Gather" in xml
    assert "/signalwire/turn/01_simple_scheduling" in xml

    # The patient should not speak first anymore.
    assert "Hi, I would like to schedule an appointment" not in xml


def test_signalwire_turn_returns_patient_reply():
    response = client.post(
        "/signalwire/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your name?",
            "CallSid": "signalwire-test-turn-1",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")

    xml = response.text

    assert "<Response>" in xml
    assert "<Say>Jane Doe.</Say>" in xml
    assert "<Gather" in xml
    assert "/signalwire/turn/01_simple_scheduling" in xml


def test_signalwire_turn_preserves_call_state(monkeypatch):
    def fake_generate_patient_reply(agent_text, scenario, state, patient_profile=None):
        state["turn_count"] = state.get("turn_count", 0) + 1

        if "member id" in agent_text.lower():
            return "My member ID is M123456789.", False

        return "Jane Doe", False

    monkeypatch.setattr(
        "app.main.generate_patient_reply",
        fake_generate_patient_reply,
    )

    call_sid = "test-call-123"

    response_1 = client.post(
        "/signalwire/turn/01_simple_scheduling",
        data={
            "CallSid": call_sid,
            "SpeechResult": "May I have your name?",
        },
    )

    assert response_1.status_code == 200
    assert "<Say>Jane Doe</Say>" in response_1.text

    response_2 = client.post(
        "/signalwire/turn/01_simple_scheduling",
        data={
            "CallSid": call_sid,
            "SpeechResult": "May I have your member ID?",
        },
    )

    assert response_2.status_code == 200
    assert "<Say>My member ID is M123456789.</Say>" in response_2.text


def test_signalwire_turn_stores_history():
    CALL_STATES.clear()

    call_sid = "signalwire-test-history"

    response = client.post(
        "/signalwire/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your name?",
            "CallSid": call_sid,
        },
    )

    assert response.status_code == 200
    assert CALL_STATES[call_sid]["history"] == [
        {"speaker": "agent", "text": "May I have your name?"},
        {"speaker": "patient", "text": "Jane Doe."},
    ]


def test_signalwire_start_missing_scenario_returns_404():
    response = client.post(
        "/signalwire/start/missing_scenario",
        data={"CallSid": "signalwire-test-missing"},
    )

    assert response.status_code == 404