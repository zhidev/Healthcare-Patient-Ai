from app.signalwire_xml import build_turn_cxml


def test_build_turn_cxml_converts_pause_marker():
    xml = build_turn_cxml(
        scenario_id="03_start_and_cancel_appointment",
        patient_reply="Hold on one second. [PAUSE:2] Actually, something came up.",
        should_end=False,
    )

    assert "<Say>Hold on one second.</Say>" in xml
    assert '<Pause length="2"/>' in xml
    assert "<Say>Actually, something came up.</Say>" in xml
    assert "[PAUSE:2]" not in xml