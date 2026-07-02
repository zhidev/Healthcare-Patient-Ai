"""Tests for Twilio TwiML endpoints."""

from fastapi.testclient import TestClient

from app.main import app, CALL_STATES

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
    #confirms Gather so theres a listen for speech instruction  
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

    response_2 = client.post(
        "/twilio/turn/01_simple_scheduling",
        data={
            "SpeechResult": "May I have your member ID?",
            "CallSid": call_sid,
        },
    )

    assert response_2.status_code == 200
    assert "<Say>My member ID is M123456789.</Say>" in response_2.text


def test_twilio_start_missing_scenario_returns_404():
    response = client.post(
        "/twilio/start/missing_scenario",
        data={
            "CallSid": "test-call-missing",
        },
    )

    assert response.status_code == 404
    