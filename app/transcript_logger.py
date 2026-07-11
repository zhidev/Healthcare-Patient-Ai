"""Helpers for saving call transcripts."""

import re
from pathlib import Path


TRANSCRIPT_DIR = Path("outputs/transcripts")


def safe_filename(value: str) -> str:
    """Convert call id into a safe filename."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value)



def add_history(state: dict, speaker: str, text: str) -> None:
    """Add one clean message to call history."""

    clean_text = text.strip()

    if not clean_text:
        return

    history = state.setdefault("history", [])

    # Avoid duplicate consecutive messages.
    if history:
        last_message = history[-1]
        if (
            last_message.get("speaker") == speaker
            and last_message.get("text") == clean_text
        ):
            return

    history.append(
        {
            "speaker": speaker,
            "text": clean_text,
        }
    )


def save_transcript(
    provider: str,
    scenario_id: str,
    call_id: str,
    state: dict,
) -> Path:
    """Save the current call history to a transcript text file."""

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    safe_provider = safe_filename(provider)
    safe_scenario_id = safe_filename(scenario_id)
    safe_call_id = safe_filename(call_id)

    path = TRANSCRIPT_DIR / f"{safe_provider}_{safe_scenario_id}_{safe_call_id}.txt"

    history = state.get("history", [])

    lines = [
        f"Provider: {provider}",
        f"Scenario: {scenario_id}",
        f"Call ID: {call_id}",
        "",
        "Transcript:",
    ]

    for message in history:
        speaker = message.get("speaker", "unknown").title()
        text = message.get("text", "")
        lines.append(f"{speaker}: {text}")

    path.write_text("\n".join(lines), encoding="utf-8")

    return path