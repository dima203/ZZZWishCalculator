"""Тесты адаптера для статической web-версии (Pyodide)."""

from datetime import date

import pytest

from core.pull_calculator import ZZZPullCalculator
from core.wish_calculator import ZZZGachaCalculator
from web_bridge import event_income, mixed_chance, pull_forecast, wish_chance


def test_wish_chance_matches_core() -> None:
    expected = ZZZGachaCalculator(current_pity=30).probability_k(50, 2)
    assert wish_chance(30, 50, 2) == pytest.approx(expected)


def test_wish_chance_respects_banner_and_guarantee() -> None:
    expected = ZZZGachaCalculator(banner="w_engine", guarantee=True).probability_k(10, 1)
    assert wish_chance(0, 10, 1, banner="w_engine", guarantee=True) == pytest.approx(expected)


def test_pull_forecast_adds_event_pulls() -> None:
    base = ZZZPullCalculator(days=30, start_date=date.today()).calculate()
    forecast = pull_forecast(0, 0, 0, 0, 30, event_pulls_min=3, event_pulls_max=5)

    assert forecast["base_min"] == base.total_pulls_min
    assert forecast["base_max"] == base.total_pulls_max
    assert forecast["total_pulls_min"] == base.total_pulls_min + 3
    assert forecast["total_pulls_max"] == base.total_pulls_max + 5
    assert forecast["events_min"] == 3
    assert forecast["events_max"] == 5


def test_event_income_filters_by_period_and_confidence() -> None:
    events = [
        {
            "title": "Active",
            "start": "2026-10-01",
            "end": "2026-11-30",
            "polychromes": 900,
            "tapes": 10,
            "confidence": "catalog",
        },
        {
            "title": "Estimated",
            "start": "2026-10-20",
            "end": "2026-11-10",
            "polychromes": 300,
            "tapes": 0,
            "confidence": "estimate",
        },
        {
            "title": "Expired",
            "start": "2026-08-01",
            "end": "2026-08-10",
            "polychromes": 500,
            "tapes": 0,
            "confidence": "catalog",
        },
    ]

    income = event_income(events, "2026-10-27", 30)

    assert income["count"] == 2
    assert income["polychromes_min"] == 900
    assert income["polychromes_max"] == 1200
    assert income["tapes"] == 10
    assert income["pulls_min"] == (900 + 1600) // 160
    assert income["pulls_max"] == (1200 + 1600) // 160


def test_event_income_ignores_bad_dates() -> None:
    events = [{"start": "bad", "end": "2026-10-01", "polychromes": 100}]
    assert event_income(events, date.today().isoformat(), 30)["count"] == 0


def test_mixed_chance_returns_expected_shape() -> None:
    result = mixed_chance(180, 2, 1)

    assert result["total_pulls"] == 180
    assert result["agent_copies"] == 2
    assert result["engine_copies"] == 1
    assert result["agent_pulls"] + result["engine_pulls"] == 180
    assert result["both_probability"] == pytest.approx(result["agent_probability"] * result["engine_probability"])
