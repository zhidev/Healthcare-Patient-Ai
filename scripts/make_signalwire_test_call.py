"""Start one approved SignalWire patient-bot test call."""

import os

from app.signalwire_outbound_call import create_signalwire_patient_bot_call

PGAI_TEST_NUMBER = "+1-805-439-8008"
DRY_RUN_NUMBER = "+1-800-123-1234"

SCENARIO_DICT = {
    1: "01_simple_scheduling",
    2: "02_appointment_cancellation",
    3: "03_start_and_cancel_appointment",
    4: "04_hipaa_status_privacy",
    5: "05_lost",
    6: "06_consecutive_appointment",
    7: "07_profile_check",
    8: "08_double_appointment",
    9: "09_blurry_vision_triage",
    10: "10_stroke_triage",
    11: "11_pre_op_food",
}


def main():
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    # $env:SCENARIO_NUMBER="2"   replace 2 with whatever scenario # u want
    # $env:DRY_RUN="true"
    # python scripts/make_signalwire_test_call.py
    scenario_number = int(os.getenv("SCENARIO_NUMBER", "1"))
    scenario_id = SCENARIO_DICT[scenario_number]

    if dry_run:
        print("DRY RUN ONLY - no SignalWire call placed.")
        print(f"Would call: {DRY_RUN_NUMBER}")
        print(f"Scenario: {scenario_id}")
        return

    call_id = create_signalwire_patient_bot_call(
        to_number=PGAI_TEST_NUMBER,
        scenario_id=scenario_id,
    )

    print(f"Started SignalWire call: {call_id}")


if __name__ == "__main__":
    main()
