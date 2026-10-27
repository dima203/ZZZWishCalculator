"""Тесты автоматической оценки доходов с ивентов."""

import json
from datetime import date

from core.events import (
    EventIncome,
    EventReward,
    estimate_post,
    parse_duration,
    parse_rewards,
    summarize_events,
)

OFFICIAL_USER = {"uid": "219270333", "certification": {"desc": "ZZZ Official"}}


def item(post_id: str, subject: str, created_at: int = 1792548000) -> dict:
    return {
        "post": {"post_id": post_id, "subject": subject, "created_at": created_at},
        "user": OFFICIAL_USER,
    }


def structured(*lines: str) -> str:
    return json.dumps([{"insert": line} for line in lines])


def test_parse_rewards_sums_explicit_amounts() -> None:
    text = "Rewards: Polychromes ×300, Encrypted Master Tape ×10, upgrade materials."
    assert parse_rewards(text) == (300, 10)

    compensation = "Compensation: Polychrome ×300\nCompensation: Polychrome ×300"
    assert parse_rewards(compensation) == (600, 0)
    assert parse_rewards("Polychromes and more") == (0, 0)


def test_parse_duration_iso_and_month_name() -> None:
    fallback = date(2026, 10, 27)
    iso = "2026/10/22 10:00 (server time) – 2026/11/30 03:59 (server time)"
    assert parse_duration(iso, fallback) == (date(2026, 10, 22), date(2026, 11, 30))

    month_name = "October 2 – October 8"
    assert parse_duration(month_name, fallback) == (date(2026, 10, 2), date(2026, 10, 8))


def test_parse_duration_after_update_uses_fallback_start() -> None:
    fallback = date(2026, 10, 19)
    text = "After the Version 3.3 update – 2026/12/01 03:59 (server time)"
    assert parse_duration(text, fallback) == (fallback, date(2026, 12, 1))
    assert parse_duration("no dates here", fallback) is None


def test_estimate_post_uses_catalog_for_known_event() -> None:
    detail = structured(
        "Event Duration\n2026/10/22 10:00 – 2026/11/30 03:59",
        "\nAdvance event commissions to obtain Polychromes and materials.",
    )
    reward = estimate_post(
        item("1", '"Spooky Funhouse Tales" Event Details'),
        detail,
        date(2026, 10, 27),
    )

    assert isinstance(reward, EventReward)
    assert reward.polychromes == 900
    assert reward.tapes == 0
    assert reward.start == date(2026, 10, 22)
    assert reward.end == date(2026, 11, 30)
    assert reward.confidence == "catalog"


def test_estimate_post_parses_login_tapes_and_compensation() -> None:
    login = estimate_post(
        item("2", "All-New Program Event Details"),
        structured("Log in for 7 days to obtain Encrypted Master Tape ×10!"),
        date(2026, 10, 27),
    )
    assert login is not None
    assert (login.polychromes, login.tapes) == (0, 10)

    compensation = estimate_post(
        item("3", "Version 3.3 Update Announcement"),
        structured("Compensation: Polychrome ×300", "Compensation: Polychrome ×300"),
        date(2026, 10, 27),
    )
    assert compensation is not None
    assert compensation.polychromes == 600
    assert compensation.tapes == 0


def test_update_announcement_does_not_duplicate_event_tapes() -> None:
    announcement = estimate_post(
        item("6", "Version 3.3 Update Announcement"),
        structured(
            "Compensation: Polychrome ×300",
            "Compensation: Polychrome ×300",
            "All-New Program: log in for 7 days to obtain Encrypted Master Tape ×10!",
        ),
        date(2026, 10, 27),
    )

    assert announcement is not None
    assert (announcement.polychromes, announcement.tapes) == (600, 0)


def test_estimate_post_falls_back_for_unknown_event() -> None:
    reward = estimate_post(
        item("4", "Mystery Event Details"),
        structured("Event Duration\n2026/10/20 10:00 – 2026/11/10 03:59", "Polychromes and more"),
        date(2026, 10, 27),
    )

    assert reward is not None
    assert reward.polychromes == 300
    assert reward.confidence == "estimate"


def test_estimate_post_skips_paid_city_fund() -> None:
    reward = estimate_post(
        item("5", "Version 3.3 New Eridu City Fund Details"),
        structured("Unlock the Growth Plan to instantly receive Polychrome ×680."),
        date(2026, 10, 27),
    )
    assert reward is None


def test_summarize_events_filters_by_period_and_builds_range() -> None:
    events = [
        EventReward("1", "Active", date(2026, 10, 22), date(2026, 11, 30), 900, 0, "catalog", "u1"),
        EventReward("2", "Expired", date(2026, 9, 1), date(2026, 9, 10), 300, 0, "catalog", "u2"),
        EventReward("3", "Estimated", date(2026, 11, 10), date(2026, 12, 1), 300, 0, "estimate", "u3"),
    ]

    income = summarize_events(events, date(2026, 10, 27), 30)

    assert [event.title for event in income.events] == ["Active", "Estimated"]
    assert income.polychromes_min == 900
    assert income.polychromes_max == 1200
    assert income.tapes == 0
    assert (income.min_pulls, income.max_pulls) == (5, 7)


def test_summarize_events_counts_tapes_as_pulls() -> None:
    events = [
        EventReward("1", "Login", date(2026, 10, 1), date(2026, 11, 1), 0, 10, "catalog", "u1"),
    ]

    income = summarize_events(events, date(2026, 10, 27), 30)

    assert (income.min_pulls, income.max_pulls) == (10, 10)
    assert EventIncome.empty().max_pulls == 0
