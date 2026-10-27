"""Мост между статической web-версией и Python-ядром калькулятора.

Загружается в Pyodide на GitHub Pages. Не использует файлы/сеть, кроме
переданного JSON с ивентами, поэтому конфиги нигде не сохраняются.
"""

from datetime import date, timedelta

from core.mixed_calculator import calculate_mixed
from core.pull_calculator import ZZZPullCalculator
from core.wish_calculator import BANNERS, ZZZGachaCalculator


def banner_specs() -> dict[str, dict[str, int | float | str]]:
    return {
        key: {
            "label": spec.label,
            "hard_pity": spec.hard_pity,
            "featured_rate": spec.featured_rate,
        }
        for key, spec in BANNERS.items()
    }


def wish_chance(
    pity: int,
    pulls: int,
    copies: int,
    banner: str = "agent",
    guarantee: bool = False,
) -> float:
    calc = ZZZGachaCalculator(current_pity=pity, guarantee=guarantee, banner=banner)
    return calc.probability_k(pulls, copies)


def pull_forecast(
    current_pulls: int,
    current_polychromes: int,
    current_monochromes: int,
    subscription_days: int,
    days: int,
    event_pulls_min: int = 0,
    event_pulls_max: int = 0,
) -> dict[str, int]:
    calc = ZZZPullCalculator(
        current_pulls=current_pulls,
        current_polychromes=current_polychromes,
        current_monochromes=current_monochromes,
        subscription_days=subscription_days,
        days=days,
    )
    result = calc.calculate()
    return {
        "total_pulls_min": result.total_pulls_min + max(0, event_pulls_min),
        "total_pulls_max": result.total_pulls_max + max(0, event_pulls_max),
        "base_min": result.total_pulls_min,
        "base_max": result.total_pulls_max,
        "events_min": max(0, event_pulls_min),
        "events_max": max(0, event_pulls_max),
        "polychromes_earned": result.total_polychromes_earned,
        **calc.get_detailed_breakdown(),
    }


def event_income(events: list[dict], start_iso: str, days: int) -> dict[str, int]:
    start = date.fromisoformat(start_iso)
    period_end = start + timedelta(days=days)
    active = []
    for event in events:
        try:
            event_start = date.fromisoformat(event["start"])
            event_end = date.fromisoformat(event["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if event_start <= period_end and event_end >= start:
            active.append(event)

    polychromes_min = sum(int(event.get("polychromes", 0)) for event in active if event.get("confidence") != "estimate")
    polychromes_max = sum(int(event.get("polychromes", 0)) for event in active)
    tapes = sum(int(event.get("tapes", 0)) for event in active)
    return {
        "polychromes_min": polychromes_min,
        "polychromes_max": polychromes_max,
        "tapes": tapes,
        "pulls_min": (polychromes_min + tapes * 160) // 160,
        "pulls_max": (polychromes_max + tapes * 160) // 160,
        "count": len(active),
    }


def mixed_chance(
    total_pulls: int,
    agent_copies: int,
    engine_copies: int,
    agent_pity: int = 0,
    agent_guarantee: bool = False,
    engine_pity: int = 0,
    engine_guarantee: bool = False,
) -> dict[str, int | float]:
    result = calculate_mixed(
        total_pulls=total_pulls,
        agent_copies=agent_copies,
        engine_copies=engine_copies,
        agent_pity=agent_pity,
        agent_guarantee=agent_guarantee,
        engine_pity=engine_pity,
        engine_guarantee=engine_guarantee,
    )
    return {
        "total_pulls": result.total_pulls,
        "agent_pulls": result.agent_pulls,
        "engine_pulls": result.engine_pulls,
        "agent_copies": result.agent_copies,
        "engine_copies": result.engine_copies,
        "agent_probability": result.agent_probability,
        "engine_probability": result.engine_probability,
        "both_probability": result.both_probability,
    }
