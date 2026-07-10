"""Outbound SignalWire call helper."""

import os

import requests
from dotenv import load_dotenv

from app.safety import assert_allowed_number

load_dotenv()


def create_signalwire_patient_bot_call(
    to_number: str,
    scenario_id: str,
) -> str:
    """Create an outbound SignalWire call to the approved assessment number only."""

    safe_to_number = assert_allowed_number(to_number)

    project_id = os.environ["SIGNALWIRE_PROJECT_ID"]
    api_token = os.environ["SIGNALWIRE_API_TOKEN"]
    space_url = os.environ["SIGNALWIRE_SPACE_URL"].rstrip("/")
    from_number = os.environ["SIGNALWIRE_FROM_NUMBER"]
    public_base_url = (
        os.environ["PUBLIC_BASE_URL"].strip().strip('"').strip("'").rstrip("/")
    )
    call_url = f"{space_url}/api/laml/2010-04-01/" f"Accounts/{project_id}/Calls.json"

    webhook_url = f"{public_base_url}/signalwire/start/{scenario_id}#rt=15000"
    status_callback_url = f"{public_base_url}/signalwire/status/{scenario_id}"

    print("Remove later. Within app/signalwire_outbound_call")
    print(f"SignalWire webhook URL: {webhook_url}")
    print(f"Calling: {safe_to_number}")
    print(f"From: {from_number}")

    response = requests.post(
        call_url,
        auth=(project_id, api_token),
        data={
            "To": safe_to_number,
            "From": from_number,
            "Url": webhook_url,
            "Method": "POST",
            "Record": "true",
            "StatusCallback": status_callback_url,
            "StatusCallbackMethod": "POST",
            "StatusCallbackEvent": [
                "initiated",
                "ringing",
                "answered",
                "completed",
            ],
        },
        timeout=15,
    )

    response.raise_for_status()
    # if response.status_code >= 400:
    #     print("SignalWire error status:", response.status_code)
    #     print("SignalWire error response:", response.text)
    #     print("Webhook URL:", webhook_url)
    #     print("From:", from_number)
    #     print("To:", safe_to_number)
    #     response.raise_for_status()

    data = response.json()

    call_id = data.get("sid") or data.get("call_sid") or data.get("id")

    if not call_id:
        raise RuntimeError(f"SignalWire call created but no call id returned: {data}")

    return call_id
