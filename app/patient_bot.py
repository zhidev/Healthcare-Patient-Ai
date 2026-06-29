INTENT_PATTERNS = {
    "ask_member_id": [
        "member id",
        "member number",
        "id number",
        "insurance id"
    ],
    "ask_name": [
        "your name",
        "patient name",
        "member name"
    ],
    "ask_dob": [
        "date of birth",
        "dob",
        "birthday",
        "birth date"
    ],
    "ask_reason": [
        "reason",
        "nature",
        "appointment for",
        "seen for",
        "what brings you in"
    ],
    "ask_time": [
        "when",
        "what time",
        "what day",
        "availability",
        "schedule your appointment"
    ],
    "confirm_time": [
        "is this alright",
        "does that work",
        "is that okay",
        "will schedule you",
        "scheduled for",
        "confirm"
    ],
    "end_call": [
        "anything else",
        "assist you with",
        "help you with anything else"
    ]
}



def detect_intent(agent_text: str) -> str:
    text = agent_text.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            return intent

    return "unknown"



# functions to match intents
def reply_name(scenario: dict, state: dict) -> tuple[str, bool]:
    return scenario["patient"]["name"], False


def reply_member_id(scenario: dict, state: dict) -> tuple[str, bool]:
    return f"My member ID is {scenario['patient']['member_id']}.", False


def reply_dob(scenario: dict, state: dict) -> tuple[str, bool]:
    return scenario["patient"]["dob"], False


def reply_reason(scenario: dict, state: dict) -> tuple[str, bool]:
    return scenario["reason"], False


def reply_time(scenario: dict, state: dict) -> tuple[str, bool]:
    return "When is your earliest availability?", False


def reply_confirm(scenario: dict, state: dict) -> tuple[str, bool]:
    return "Yes, that works.", False


def reply_end(scenario: dict, state: dict) -> tuple[str, bool]:
    return scenario["final_response"], True


def reply_unknown(scenario: dict, state: dict) -> tuple[str, bool]:
    return "Sorry, could you repeat that?", False


#Matching intent with the functions above
INTENT_HANDLERS = {
    "ask_name": reply_name,
    "ask_member_id": reply_member_id,
    "ask_dob": reply_dob,
    "ask_reason": reply_reason,
    "ask_time": reply_time,
    "confirm_time": reply_confirm,
    "end_call": reply_end
}


# agent_text = what the agent just said
# scenario = the JSON facts
# state = conversation memory

# return (reply_text, should_end_call)
def get_patient_reply(
    agent_text: str,
    scenario: dict,
    state: dict
) -> tuple[str, bool]:
    state["turn_count"] = state.get("turn_count", 0) + 1

    if state["turn_count"] >= scenario.get("max_turns", 8):
        return scenario["final_response"], True

    intent = detect_intent(agent_text)
    handler = INTENT_HANDLERS.get(intent, reply_unknown)

    #runs and returns the handler function ie reply_name(scenario,state) = "Jane Doe"
    return handler(scenario, state)