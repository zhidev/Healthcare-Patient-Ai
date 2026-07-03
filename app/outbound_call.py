"""Outbound Twilio call helper."""

import os

from dotenv import load_dotenv
from twilio.rest import Client

from app.safety import assert_allowed_number

load_dotenv()


def create_patient_bot_call(
    to_number: str,
    scenario_id: str,
):
    """Create an outbound call to the approved assessment number only."""

    safe_to_number = assert_allowed_number(to_number)

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_FROM_NUMBER"]
    public_base_url = os.environ["PUBLIC_BASE_URL"].rstrip("/")

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        to=safe_to_number,
        from_=from_number,
        url=f"{public_base_url}/twilio/start/{scenario_id}",
        method="POST",
        record=True,
    )

    return call.sid