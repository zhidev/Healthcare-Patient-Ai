"""Tests for outbound Twilio call helper."""

import pytest

from app import outbound_call
from app.outbound_call import create_patient_bot_call
from app.safety import UnsafePhoneNumberError


class FakeCall:
    sid = "CA_fake_call_sid"


class FakeCalls:
    def __init__(self):
        self.created_call_args = None

    def create(self, **kwargs):
        self.created_call_args = kwargs
        return FakeCall()


class FakeClient:
    last_instance = None

    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.calls = FakeCalls()
        FakeClient.last_instance = self


def test_create_patient_bot_call_uses_safe_number_and_twiml_url(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "fake_sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "fake_token")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+14155550000")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.trycloudflare.com")

    monkeypatch.setattr(outbound_call, "Client", FakeClient)

    call_sid = create_patient_bot_call(
        to_number="+1-805-439-8008",
        scenario_id="01_simple_scheduling",
    )

    assert call_sid == "CA_fake_call_sid"

    fake_client = FakeClient.last_instance
    created_call_args = fake_client.calls.created_call_args

    assert created_call_args["to"] == "+18054398008"
    assert created_call_args["from_"] == "+14155550000"
    assert created_call_args["url"] == (
        "https://example.trycloudflare.com/twilio/start/01_simple_scheduling"
    )
    assert created_call_args["method"] == "POST"
    assert created_call_args["record"] is True


def test_create_patient_bot_call_blocks_unapproved_number(monkeypatch):
    monkeypatch.setattr(outbound_call, "Client", FakeClient)

    with pytest.raises(UnsafePhoneNumberError):
        create_patient_bot_call(
            to_number="+1-800-123-1234",
            scenario_id="01_simple_scheduling",
        )