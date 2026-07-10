# FastAPI backend for the healthcare patient QA bot.
import os
import time

from fastapi import FastAPI, Form, HTTPException, Response
from pydantic import BaseModel, Field

from app import llm_patient, transcript_logger
from app.scenarios import load_scenario

# SignalWire
from app.signalwire_xml import (
    build_final_inquiry_cxml,
    build_no_input_goodbye_cxml,
    build_start_cxml,
    build_turn_cxml,
    build_wait_cxml,
)
from app.transcript_logger import save_transcript

# Twilio

app = FastAPI(title="Healthcare Voice QA Bot")

CALL_STATES: dict[str, dict] = {}


def generate_patient_reply(
    agent_text: str,
    scenario: dict,
    state: dict,
) -> tuple[str, bool]:
    """Generate patient reply using LLM mode if enabled, otherwise rules."""

    if os.getenv("LLM_PATIENT_ENABLED", "false").lower() == "true":
        try:
            return llm_patient.get_llm_patient_reply(
                agent_text=agent_text,
                scenario=scenario,
                state=state,
            )
        except Exception:
            return llm_patient.get_llm_patient_reply(
                agent_text=agent_text,
                scenario=scenario,
                state=state,
            )

    return llm_patient.get_llm_patient_reply(
        agent_text=agent_text,
        scenario=scenario,
        state=state,
    )


# Request body for one patient-bot conversation turn.
class ChatRequest(BaseModel):
    scenario_id: str
    agent_text: str
    state: dict = Field(default_factory=dict)


# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


# Return the next patient-bot reply for a given agent message.
@app.post("/chat")
def chat(request: ChatRequest):
    """load up scenario based off id to get reply"""
    try:
        scenario = load_scenario(request.scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    reply, should_end = generate_patient_reply(
        agent_text=request.agent_text,
        scenario=scenario,
        state=request.state,
    )

    return {"reply": reply, "should_end": should_end, "state": request.state}


# SignalWire counterpart
# Start endpoint
@app.post("/signalwire/start/{scenario_id}")
def signalwire_start(
    scenario_id: str,
    CallSid: str = Form(default="local-signalwire-test-call"),
):
    """Return SignalWire cXML for the first patient message."""

    try:
        scenario = load_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    CALL_STATES[CallSid] = {}

    save_transcript(
        provider="signalwire",
        scenario_id=scenario_id,
        call_id=CallSid,
        state=CALL_STATES[CallSid],
    )

    xml = build_start_cxml(scenario_id=scenario_id)
    # print("\n--- SignalWire Start XML ---")
    # print(xml)
    print("\n--- SignalWire Start ---")
    print(f"Scenario: {scenario_id}")
    print(f"CallSid: {CallSid}")
    print("\n--- SignalWire Start XML ---")
    print(xml)
    return Response(content=xml, media_type="application/xml")


# Turns endpoint
@app.post("/signalwire/turn/{scenario_id}")
def signalwire_turn(
    scenario_id: str,
    SpeechResult: str = Form(default=""),
    CallSid: str = Form(default="local-signalwire-test-call"),
):
    """Return SignalWire cXML for the next patient reply."""

    try:
        scenario = load_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    state = CALL_STATES.setdefault(CallSid, {})

    turn_started = time.perf_counter()

    print("\n--- SignalWire Turn ---")
    print(f"CallSid: {CallSid}")
    print(f"Agent said: {SpeechResult}")

    agent_text = SpeechResult.strip()

    if agent_text:
        transcript_logger.add_history(state, "agent", agent_text)

        save_transcript(
            provider="signalwire",
            scenario_id=scenario_id,
            call_id=CallSid,
            state=state,
        )

    reply, should_end = generate_patient_reply(
        agent_text=agent_text,
        scenario=scenario,
        state=state,
    )

    if reply == "__WAIT__":
        print("LLM chose to wait and listen again.")

        xml = build_wait_cxml(
            scenario_id=scenario_id,
            wait_count=0,
            pause_seconds=1,
        )

        return Response(content=xml, media_type="application/xml")

    print(f"Patient replied: {reply}")
    print(f"Should end: {should_end}")

    transcript_logger.add_history(state, "patient", reply)

    save_transcript(
        provider="signalwire",
        scenario_id=scenario_id,
        call_id=CallSid,
        state=state,
    )

    if should_end:
        state["bot_requested_hangup"] = True

    xml = build_turn_cxml(
        scenario_id=scenario_id,
        patient_reply=reply,
        should_end=should_end,
    )

    turn_elapsed = time.perf_counter() - turn_started
    print(f"SignalWire turn response time: {turn_elapsed:.2f} seconds")

    return Response(content=xml, media_type="application/xml")


# Call Status update
@app.post("/signalwire/status/{scenario_id}")
def signalwire_status(
    scenario_id: str,
    CallSid: str = Form(default=""),
    CallStatus: str = Form(default=""),
):
    """Log SignalWire call status updates."""

    print("\n--- SignalWire Call Status ---")
    print(f"Scenario: {scenario_id}")
    print(f"CallSid: {CallSid}")
    print(f"CallStatus: {CallStatus}")

    if CallStatus in {"completed", "failed", "busy", "no-answer", "canceled"}:
        print("CALL ENDED")

        state = CALL_STATES.setdefault(CallSid, {})

        if state.get("bot_requested_hangup"):
            end_text = f"CALL ENDED - CallStatus: {CallStatus} - bot requested hangup"
        else:
            end_text = (
                f"CALL ENDED - CallStatus: {CallStatus} - "
                "call ended before bot requested hangup"
            )

        transcript_logger.add_history(state, "system", end_text)

        save_transcript(
            provider="signalwire",
            scenario_id=scenario_id,
            call_id=CallSid,
            state=state,
        )

        CALL_STATES.pop(CallSid, None)

    return Response(content="", media_type="text/plain")


@app.post("/signalwire/wait/{scenario_id}")
def signalwire_wait(
    scenario_id: str,
    wait_count: int = 0,
    CallSid: str = Form(default="local-signalwire-test-call"),
):
    print("\n--- SignalWire Wait ---")
    print(f"Scenario: {scenario_id}")
    print(f"CallSid: {CallSid}")
    print(f"Wait count: {wait_count}")

    if wait_count >= 4:
        xml = build_no_input_goodbye_cxml()
        print("Max wait count reached. Hanging up.")
        print(xml)
        return Response(content=xml, media_type="application/xml")

    if wait_count == 3:
        xml = build_final_inquiry_cxml(
            scenario_id=scenario_id,
            wait_count=wait_count,
        )
        print("Final inquiry before hangup.")
        print(xml)
        return Response(content=xml, media_type="application/xml")

    xml = build_wait_cxml(
        scenario_id=scenario_id,
        wait_count=wait_count,
        pause_seconds=1,
    )

    print(xml)
    return Response(content=xml, media_type="application/xml")
