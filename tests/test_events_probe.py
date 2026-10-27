"""Тесты парсинга официальных новостей ZZZ (без сетевых вызовов)."""

import json

from tools.events_probe import (
    build_event_rows,
    event_url,
    extract_event_duration,
    is_official,
    parse_post_items,
)

OFFICIAL_ITEM = {
    "post": {
        "post_id": "47208493",
        "subject": '"Cyber Miracle Healer, on Duty!" Event Details',
        "created_at": 1789441202,
        "lang": "en-us",
    },
    "user": {
        "uid": "219270333",
        "certification": {"desc": "ZZZ Official"},
    },
}

FAN_ITEM = {
    "post": {
        "post_id": "999",
        "subject": "My fan theory",
        "created_at": 1789441202,
        "lang": "en-us",
    },
    "user": {"uid": "123456", "certification": {"desc": "HoYoLAB User"}},
}

STRUCTURED_CONTENT = json.dumps(
    [
        {"insert": "Event Duration"},
        {"insert": "\n", "attributes": {"header": 4}},
        {"insert": "2026/10/28 10:00 (server time) – 2026/11/16 03:59 (server time)\n\nRequirements"},
    ]
)


def test_is_official_accepts_uid_or_certification() -> None:
    assert is_official(OFFICIAL_ITEM) is True
    assert is_official({"user": {"certification": {"desc": "ZZZ Official"}}}) is True
    assert is_official(FAN_ITEM) is False


def test_event_url() -> None:
    assert event_url("47208493") == "https://www.hoyolab.com/article/47208493"


def test_extract_event_duration() -> None:
    assert extract_event_duration(STRUCTURED_CONTENT) == (
        "2026/10/28 10:00 (server time) – 2026/11/16 03:59 (server time)"
    )
    assert extract_event_duration("not json") is None
    assert extract_event_duration("[]") is None


def test_extract_event_duration_handles_colon_and_garbage() -> None:
    with_colon = json.dumps([{"insert": "Event Duration: 2026/10/28 10:00 – 2026/11/16 03:59"}])
    assert extract_event_duration(with_colon) == "2026/10/28 10:00 – 2026/11/16 03:59"
    assert extract_event_duration(json.dumps([{"insert": "Event Duration\n] "}])) is None


def test_parse_post_items_reads_both_types() -> None:
    payload = {"data": {"list": [OFFICIAL_ITEM]}}
    assert parse_post_items(payload) == [OFFICIAL_ITEM]


def test_build_event_rows_filters_official_and_sorts() -> None:
    newer = json.loads(json.dumps(OFFICIAL_ITEM))
    newer["post"]["post_id"] = "500"
    newer["post"]["created_at"] = 1789530000
    payload = {"data": {"list": [OFFICIAL_ITEM, FAN_ITEM, newer]}}

    rows = build_event_rows([payload])

    assert [row["post_id"] for row in rows] == ["500", "47208493"]
    assert rows[0]["url"] == "https://www.hoyolab.com/article/500"
    assert rows[0]["duration"] is None


def test_build_event_rows_attaches_duration() -> None:
    payload = {"data": {"list": [OFFICIAL_ITEM]}}

    rows = build_event_rows([payload], details={"47208493": STRUCTURED_CONTENT})

    assert rows[0]["duration"].startswith("2026/10/28 10:00")
