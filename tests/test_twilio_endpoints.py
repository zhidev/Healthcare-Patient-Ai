"""Tests for Twilio TwiML endpoints."""

from fastapi.testclient import TestClient

from app.main import CALL_STATES, app

client = TestClient(app)


def test_twilio_start_returns_first_patient_message():
    response = client.post(
        "/twilio/start/01_simple_scheduling",
        data={
            "CallSid": "test-call-start",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")

    xml = response.text

    assert "<Response>" in xml
    # confirms Gather so theres a listen for speech instruction
    assert "<Gather" in xml
    assert "Hi, I would like to schedule an appointment" in xml
    assert "/twilio/turn/01_simple_scheduling" in xml


def test_twilio_turn_returns_patient_reply():
    response = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your name?",
            "CallSid": "test-call-turn-1",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")

    xml = response.text

    assert "<Response>" in xml
    assert "<Say>Jane Doe</Say>" in xml
    assert "<Gather" in xml


def test_twilio_turn_preserves_call_state():
    CALL_STATES.clear()

    call_sid = "test-call-state-1"

    response_1 = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your name?",
            "CallSid": call_sid,
        },
    )

    assert response_1.status_code == 200
    assert "<Say>Jane Doe</Say>" in response_1.text
    assert CALL_STATES[call_sid]["turn_count"] == 1

    response_2 = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your member ID?",
            "CallSid": call_sid,
        },
    )

    assert response_2.status_code == 200
    assert "<Say>My member ID is M123456789.</Say>" in response_2.text
    assert CALL_STATES[call_sid]["turn_count"] == 2

def test_twilio_turn_remembers_provided_name():
    CALL_STATES.clear()

    call_sid = "test-call-provided-name"

    response_1 = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your name?",
            "CallSid": call_sid,
        },
    )

    assert response_1.status_code == 200
    assert "<Say>Jane Doe</Say>" in response_1.text
    assert CALL_STATES[call_sid]["provided"]["name"] is True

    response_2 = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "Can I get your name again?",
            "CallSid": call_sid,
        },
    )

    assert response_2.status_code == 200
    assert "I already gave my name. It's Jane Doe." in response_2.text
    assert CALL_STATES[call_sid]["turn_count"] == 2


def test_twilio_start_missing_scenario_returns_404():
    response = client.post(
        "/twilio/start/missing_scenario",
        data={
            "CallSid": "test-call-missing",
        },
    )

    assert response.status_code == 404
