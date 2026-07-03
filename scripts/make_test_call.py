"""Start one approved patient-bot test call."""

import os

from app.outbound_call import create_patient_bot_call


PGAI_TEST_NUMBER = "+1-805-439-8008"
DRY_RUN_NUMBER = "+1-800-123-1234"


def main():
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    if dry_run:
        print("DRY RUN ONLY - no call placed.")
        print(f"Would call: {DRY_RUN_NUMBER}")
        print("Scenario: 01_simple_scheduling")
        return

    call_sid = create_patient_bot_call(
        to_number=PGAI_TEST_NUMBER,
        scenario_id="01_simple_scheduling",
    )

    print(f"Started call: {call_sid}")


if __name__ == "__main__":
    main()