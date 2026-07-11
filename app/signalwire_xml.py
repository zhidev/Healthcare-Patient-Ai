"""SignalWire cXML generation for patient bot voice calls."""

import re
from xml.sax.saxutils import escape

SIGNALWIRE_READ_TIMEOUT_MS = 15000
START_GATHER_TIMEOUT_SECONDS = 18
TURN_GATHER_TIMEOUT_SECONDS = 8
WAIT_GATHER_TIMEOUT_SECONDS = 4
FINAL_INQUIRY_TIMEOUT_SECONDS = 5
MAX_PAUSE_SECONDS = 5


def build_start_cxml(scenario_id: str) -> str:
    """Build cXML that waits for the healthcare agent to speak first."""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/signalwire/turn/{scenario_id}#rt={SIGNALWIRE_READ_TIMEOUT_MS}" method="POST" speechTimeout="2" timeout="{START_GATHER_TIMEOUT_SECONDS}"/>
    <Redirect method="POST">/signalwire/wait/{scenario_id}</Redirect>
</Response>"""


# Pause support. [PAUSE:2] causes a 2 second pause
def build_turn_cxml(
    scenario_id: str,
    patient_reply: str,
    should_end: bool,
) -> str:
    """Build cXML for a follow-up patient reply."""

    pause_marker_re = re.compile(r"\[PAUSE:(\d+)\]")

    xml_parts = []
    last_index = 0

    for match in pause_marker_re.finditer(patient_reply):
        before_pause = patient_reply[last_index : match.start()].strip()

        if before_pause:
            xml_parts.append(f"    <Say>{escape(before_pause)}</Say>")

        pause_seconds = int(match.group(1))
        pause_seconds = max(1, min(pause_seconds, MAX_PAUSE_SECONDS))

        xml_parts.append(f'    <Pause length="{pause_seconds}"/>')

        last_index = match.end()

    remaining_text = patient_reply[last_index:].strip()

    if remaining_text:
        xml_parts.append(f"    <Say>{escape(remaining_text)}</Say>")

    say_xml = "\n".join(xml_parts)

    if not say_xml:
        say_xml = "    <Say>Sorry, could you repeat that?</Say>"

    if should_end:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
{say_xml}
    <Hangup/>
</Response>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
{say_xml}
    <Gather input="speech" action="/signalwire/turn/{scenario_id}#rt={SIGNALWIRE_READ_TIMEOUT_MS}" method="POST" speechTimeout="auto" timeout="{TURN_GATHER_TIMEOUT_SECONDS}"/>
    <Redirect method="POST">/signalwire/wait/{scenario_id}</Redirect>
</Response>"""


def build_wait_cxml(
    scenario_id: str,
    wait_count: int = 0,
    pause_seconds: int = 1,
) -> str:
    """Build cXML that briefly waits and listens again."""

    next_wait_count = wait_count + 1

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="{pause_seconds}"/>
    <Gather input="speech" action="/signalwire/turn/{scenario_id}#rt={SIGNALWIRE_READ_TIMEOUT_MS}" method="POST" speechTimeout="auto" timeout="{WAIT_GATHER_TIMEOUT_SECONDS}"/>
    <Redirect method="POST">/signalwire/wait/{scenario_id}?wait_count={next_wait_count}</Redirect>
</Response>"""


def build_no_input_goodbye_cxml() -> str:
    """Build cXML that ends the call after repeated silence."""

    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>I am hanging up now. Goodbye.</Say>
    <Hangup/>
</Response>"""


def build_final_inquiry_cxml(scenario_id: str, wait_count: int) -> str:
    """Ask one final question before hanging up for no input."""

    next_wait_count = wait_count + 1

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/signalwire/turn/{scenario_id}#rt={SIGNALWIRE_READ_TIMEOUT_MS}" method="POST" speechTimeout="auto" timeout="{FINAL_INQUIRY_TIMEOUT_SECONDS}">
        <Say>Are you still there?</Say>
    </Gather>
    <Redirect method="POST">/signalwire/wait/{scenario_id}?wait_count={next_wait_count}</Redirect>
</Response>"""
