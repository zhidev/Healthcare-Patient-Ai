"""TwiML generation for patient bot voice calls."""

from twilio.twiml.voice_response import Gather, VoiceResponse


def build_start_twiml(scenario_id: str, first_patient_message: str) -> str:
    """Build TwiML for the first patient message."""

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action=f"/twilio/turn/{scenario_id}",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(first_patient_message)
    response.append(gather)

    response.say("I did not hear anything. Goodbye.")
    response.hangup()

    return str(response)


def build_turn_twiml(
    scenario_id: str,
    patient_reply: str,
    should_end: bool,
) -> str:
    """Build TwiML for a follow-up patient reply."""

    response = VoiceResponse()
    response.say(patient_reply)

    if should_end:
        response.hangup()
        return str(response)

    gather = Gather(
        input="speech",
        action=f"/twilio/turn/{scenario_id}",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    response.append(gather)

    response.say("I did not hear anything. Goodbye.")
    response.hangup()

    return str(response)