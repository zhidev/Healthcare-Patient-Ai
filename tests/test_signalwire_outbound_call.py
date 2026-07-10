"""Tests for outbound SignalWire call helper."""

import pytest

from app import signalwire_outbound_call
from app.safety import UnsafePhoneNumberError
from app.signalwire_outbound_call import create_signalwire_patient_bot_call


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"sid": "SW_fake_call_sid"}


def fake_post(*args, **kwargs):
    fake_post.called_args = args
    fake_post.called_kwargs = kwargs
    return FakeResponse()


def test_create_signalwire_patient_bot_call_uses_safe_number_and_webhook(monkeypatch):
    monkeypatch.setenv("SIGNALWIRE_PROJECT_ID", "fake_project_id")
    monkeypatch.setenv("SIGNALWIRE_API_TOKEN", "fake_api_token")
    monkeypatch.setenv("SIGNALWIRE_SPACE_URL", "https://example.signalwire.com")
    monkeypatch.setenv("SIGNALWIRE_FROM_NUMBER", "+14155550000")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.trycloudflare.com")

    monkeypatch.setattr(signalwire_outbound_call.requests, "post", fake_post)

    call_id = create_signalwire_patient_bot_call(
        to_number="+1-805-439-8008",
        scenario_id="01_simple_scheduling",
    )

    assert call_id == "SW_fake_call_sid"

    call_url = fake_post.called_args[0]
    request_kwargs = fake_post.called_kwargs

    assert call_url == (
        "https://example.signalwire.com/api/laml/2010-04-01/"
        "Accounts/fake_project_id/Calls.json"
    )

    assert request_kwargs["auth"] == ("fake_project_id", "fake_api_token")
    assert request_kwargs["data"]["To"] == "+18054398008"
    assert request_kwargs["data"]["From"] == "+14155550000"
    assert request_kwargs["data"]["Url"] == (
        "https://example.trycloudflare.com/signalwire/start/01_simple_scheduling#rt=15000"
    )
    assert request_kwargs["data"]["Method"] == "POST"
    assert request_kwargs["data"]["Record"] == "true"
    assert request_kwargs["timeout"] == 15


def test_create_signalwire_patient_bot_call_blocks_unapproved_number(monkeypatch):
    monkeypatch.setattr(signalwire_outbound_call.requests, "post", fake_post)

    with pytest.raises(UnsafePhoneNumberError):
        create_signalwire_patient_bot_call(
            to_number="+1-800-123-1234",
            scenario_id="01_simple_scheduling",
        )
