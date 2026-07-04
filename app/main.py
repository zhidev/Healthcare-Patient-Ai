# FastAPI backend for the healthcare patient QA bot.
import os

from fastapi import FastAPI, Form, HTTPException, Response
from pydantic import BaseModel, Field

from app import llm_patient, patient_bot
from app.scenarios import load_scenario
from app.twiml import build_start_twiml, build_turn_twiml

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
            return patient_bot.get_patient_reply(
                agent_text=agent_text,
                scenario=scenario,
                state=state,
            )

    return patient_bot.get_patient_reply(
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


# Opening twilio
@app.post("/twilio/start/{scenario_id}")
def twilio_start(
    scenario_id: str,
    CallSid: str = Form(default="local-test-call"),
):
    """Return TwiML for the first patient message."""

    try:
        scenario = load_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    CALL_STATES[CallSid] = {}

    xml = build_start_twiml(
        scenario_id=scenario_id,
        first_patient_message=scenario["first_patient_message"],
    )

    return Response(content=xml, media_type="application/xml")


# Individual twilio turns
@app.post("/twilio/turn/{scenario_id}")
def twilio_turn(
    scenario_id: str,
    SpeechResult: str = Form(default=""),
    CallSid: str = Form(default="local-test-call"),
):
    """Return TwiML for the next patient reply."""

    try:
        scenario = load_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    state = CALL_STATES.setdefault(CallSid, {})

    reply, should_end = generate_patient_reply(
        agent_text=SpeechResult,
        scenario=scenario,
        state=state,
    )

    if should_end:
        CALL_STATES.pop(CallSid, None)

    xml = build_turn_twiml(
        scenario_id=scenario_id,
        patient_reply=reply,
        should_end=should_end,
    )

    return Response(content=xml, media_type="application/xml")
