# tests/test_reader.py
from backend.reader import parse_bugcheck, group_incidents


def make_event(time, event_id):
    return {"Time": time, "Id": event_id, "ProviderName": "test", "Message": ""}


def test_parse_bugcheck_extracts_code_and_params():
    message = (
        "Компьютер был перезагружен после критической ошибки. "
        "Код ошибки: 0x0000000a (0x0000000000002028, 0x00000000000000ff, "
        "0x0000000000000000, 0xfffff80062c3f8a6). Дамп памяти сохранён"
    )
    result = parse_bugcheck(message)
    assert result["code"] == 10
    assert len(result["params"]) == 4


def test_parse_bugcheck_returns_none_without_code():
    assert parse_bugcheck("просто текст без кода") is None


def test_incident_is_bsod_when_1001_present():
    events = [
        make_event("2026-10-24T16:02:29.9026535+05:00", 41),
        make_event("2026-10-24T16:02:39.2368771+05:00", 1001),
    ]
    incidents = group_incidents(events)
    assert len(incidents) == 1
    assert incidents[0]["type"] == "bsod"


def test_incident_is_unexpected_shutdown_when_only_41():
    events = [make_event("2026-10-24T18:47:21.9491036+05:00", 41)]
    assert group_incidents(events)[0]["type"] == "unexpected_shutdown"


def test_distant_events_become_separate_incidents():
    events = [
        make_event("2026-10-24T16:02:29.9026535+05:00", 41),
        make_event("2026-10-24T18:47:21.9491036+05:00", 41),
    ]
    assert len(group_incidents(events)) == 2