"""Tests for FastAPI chat endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_returns_patient_reply(monkeypatch):
    def fake_generate_patient_reply(agent_text, scenario, state):
        state["turn_count"] = state.get("turn_count", 0) + 1
        return "Jane Doe", False

    monkeypatch.setattr(
        "app.main.generate_patient_reply",
        fake_generate_patient_reply,
    )

    response = client.post(
        "/chat",
        json={
            "scenario_id": "01_simple_scheduling",
            "agent_text": "May I have your name?",
            "state": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reply"] == "Jane Doe"
    assert data["should_end"] is False
    assert data["state"]["turn_count"] == 1


def test_chat_endpoint_blocks_missing_scenario():
    response = client.post(
        "/chat",
        json={
            "scenario_id": "missing_scenario",
            "agent_text": "May I have your name?",
            "state": {},
        },
    )

    assert response.status_code == 404


def test_chat_endpoint_preserves_state_across_turns(monkeypatch):
    def fake_generate_patient_reply(agent_text, scenario, state):
        state["turn_count"] = state.get("turn_count", 0) + 1

        if "member id" in agent_text.lower():
            return "My member ID is M123456789.", False

        return "Jane Doe", False

    monkeypatch.setattr(
        "app.main.generate_patient_reply",
        fake_generate_patient_reply,
    )

    state = {}

    response_1 = client.post(
        "/chat",
        json={
            "scenario_id": "01_simple_scheduling",
            "agent_text": "May I have your name?",
            "state": state,
        },
    )

    assert response_1.status_code == 200
    data_1 = response_1.json()

    assert data_1["reply"] == "Jane Doe"
    assert data_1["state"]["turn_count"] == 1

    response_2 = client.post(
        "/chat",
        json={
            "scenario_id": "01_simple_scheduling",
            "agent_text": "May I have your member ID?",
            "state": data_1["state"],
        },
    )

    assert response_2.status_code == 200
    data_2 = response_2.json()

    assert data_2["reply"] == "My member ID is M123456789."
    assert data_2["state"]["turn_count"] == 2