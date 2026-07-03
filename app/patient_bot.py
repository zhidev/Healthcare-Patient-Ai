"""Rule-based fake patient bot for healthcare voice QA scenarios."""

INTENT_PATTERNS = {
    "ask_member_id": ["member id", "member number", "id number", "insurance id"],
    "ask_name": ["your name", "patient name", "member name"],
    "ask_dob": ["date of birth", "dob", "birthday", "birth date"],
    "ask_reason": [
        "reason",
        "nature",
        "appointment for",
        "seen for",
        "what brings you in",
    ],
    "ask_time": [
        "when",
        "what time",
        "what day",
        "availability",
        "schedule your appointment",
    ],
    "confirm_time": [
        "is this alright",
        "does that work",
        "is that okay",
        "will schedule you",
        "scheduled for",
        "confirm",
    ],
    "ask_medication": [
        "which medication",
        "what medication",
        "medication do you need",
        "need refilled",
        "refill for",
    ],
    "ask_pharmacy": [
        "which pharmacy",
        "what pharmacy",
        "preferred pharmacy",
        "pharmacy is most convenient",
        "where should we send",
    ],
    "end_call": ["anything else", "assist you with", "help you with anything else"],
}

def mark_provided(state: dict, field: str) -> None:
    """Remember that the patient already provided a field."""
    provided = state.setdefault("provided", {})
    provided[field] = True


def was_provided(state: dict, field: str) -> bool:
    """Check whether the patient already provided a field."""
    return state.get("provided", {}).get(field, False)


# Detects intent with given str
def detect_intent(agent_text: str) -> str:
    text = agent_text.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            return intent

    return "unknown"


# functions to match intents
def reply_name(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "name"):
        return f"I already gave my name. It's {scenario['patient']['name']}.", False

    mark_provided(state, "name")
    return scenario["patient"]["name"], False


def reply_member_id(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "member_id"):
        return (
            f"I already gave my member ID. It's {scenario['patient']['member_id']}.",
            False,
        )

    mark_provided(state, "member_id")
    return f"My member ID is {scenario['patient']['member_id']}.", False

def reply_dob(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "dob"):
        return (
            f"I already gave my date of birth. It's {scenario['patient']['dob']}.",
            False,
        )

    mark_provided(state, "dob")
    return scenario["patient"]["dob"], False

def reply_reason(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "reason"):
        return f"I already said it is for a {scenario['reason']}.", False

    mark_provided(state, "reason")
    return scenario["reason"], False

def reply_time(scenario: dict, state: dict) -> tuple[str, bool]:
    return "When is your earliest availability?", False


def reply_confirm(scenario: dict, state: dict) -> tuple[str, bool]:
    return "Yes, that works.", False


def reply_medication(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "medication"):
        return f"I already told you. It's my {scenario['medication']}.", False

    mark_provided(state, "medication")
    return f"I need a refill for my {scenario['medication']}.", False


def reply_pharmacy(scenario: dict, state: dict) -> tuple[str, bool]:
    if was_provided(state, "pharmacy"):
        return f"I already gave the pharmacy. It's {scenario['pharmacy']}.", False

    mark_provided(state, "pharmacy")
    return scenario["pharmacy"], False


def reply_end(scenario: dict, state: dict) -> tuple[str, bool]:
    return scenario["final_response"], True


def reply_unknown(scenario: dict, state: dict) -> tuple[str, bool]:
    return "Sorry, could you repeat that?", False


# Matching intent with the functions above
INTENT_HANDLERS = {
    "ask_name": reply_name,
    "ask_member_id": reply_member_id,
    "ask_dob": reply_dob,
    "ask_reason": reply_reason,
    "ask_time": reply_time,
    "confirm_time": reply_confirm,
    "ask_medication": reply_medication,
    "ask_pharmacy": reply_pharmacy,
    "end_call": reply_end,
}


# agent_text = what the agent just said
# scenario = the JSON facts
# state = conversation memory


# return (reply_text, should_end_call)
def get_patient_reply(agent_text: str, scenario: dict, state: dict) -> tuple[str, bool]:
    state["turn_count"] = state.get("turn_count", 0) + 1

    if state["turn_count"] >= scenario.get("max_turns", 8):
        return scenario["final_response"], True

    intent = detect_intent(agent_text)
    handler = INTENT_HANDLERS.get(intent, reply_unknown)

    # runs and returns the handler function ie reply_name(scenario,state) = "Jane Doe"
    return handler(scenario, state)
