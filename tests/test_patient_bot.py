"""Tests for rule-based patient bot replies."""

from app.patient_bot import get_patient_reply


#Copy of data\scenarios 02
SCENARIO = {
    "id": "02_medication_refill",
    "type": "medication_refill",
    "first_patient_message": "Hi, I would like to get a medication refill.",
    "patient": {
        "name": "Jane Doe",
        "dob": "January 1st, 1990",
        "member_id": "M123456789",
    },
    "goal": "Request a medication refill",
    "medication": "allergy medication",
    "pharmacy": "Fake Pharmacy on 123 Fake Street",
    "final_response": "No, thank you. That's all.",
    "max_turns": 8,
}


def test_reply_name():
    state = {}

    reply, should_end = get_patient_reply(
        "Can I get your name?",
        SCENARIO,
        state,
    )

    assert reply == "Jane Doe"
    assert should_end is False


def test_reply_member_id():
    state = {}

    reply, should_end = get_patient_reply(
        "Can I get your member ID?",
        SCENARIO,
        state,
    )

    assert reply == "My member ID is M123456789."
    assert should_end is False


def test_reply_dob():
    state = {}

    reply, should_end = get_patient_reply(
        "And birthday?",
        SCENARIO,
        state,
    )

    assert reply == "January 1st, 1990"
    assert should_end is False


def test_reply_medication():
    state = {}

    reply, should_end = get_patient_reply(
        "Which medication do you need refilled?",
        SCENARIO,
        state,
    )

    assert reply == "I need a refill for my allergy medication."
    assert should_end is False


def test_reply_pharmacy():
    state = {}

    reply, should_end = get_patient_reply(
        "Which pharmacy is most convenient for you?",
        SCENARIO,
        state,
    )

    assert reply == "Fake Pharmacy on 123 Fake Street"
    assert should_end is False


def test_unknown_reply():
    state = {}

    reply, should_end = get_patient_reply(
        "Can you explain more?",
        SCENARIO,
        state,
    )

    assert reply == "Sorry, could you repeat that?"
    assert should_end is False


def test_bot_remembers_name_was_provided():
    state = {}

    reply_1, should_end_1 = get_patient_reply(
        "Can I get your name?",
        SCENARIO,
        state,
    )

    assert reply_1 == "Jane Doe"
    assert should_end_1 is False
    assert state["provided"]["name"] is True

    reply_2, should_end_2 = get_patient_reply(
        "Can I get your name again?",
        SCENARIO,
        state,
    )

    assert reply_2 == "I already gave my name. It's Jane Doe."
    assert should_end_2 is False
    assert state["turn_count"] == 2