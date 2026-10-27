"""Смешанный расчёт: цель по агенту и W-Engine при общем бюджете круток."""

from dataclasses import dataclass
from typing import Final

from .wish_calculator import ZZZGachaCalculator

MAX_TOTAL_PULLS: Final[int] = 360
AGENT_COPIES_MAX: Final[int] = 7  # M6 = 1 база + 6 дублей
ENGINE_COPIES_MAX: Final[int] = 5  # R5


@dataclass(frozen=True)
class MixedResult:
    """Результат смешанного расчёта и выбранный сплит."""

    total_pulls: int
    agent_pulls: int
    engine_pulls: int
    agent_copies: int
    engine_copies: int
    agent_probability: float
    engine_probability: float
    both_probability: float


def _target_probabilities(calc: ZZZGachaCalculator, target_copies: int, max_pulls: int) -> list[float]:
    """P(≥ target_copies) для каждого числа круток 0..max_pulls.

    DP по (pity, guarantee, copies), где copies ограничены целью. Это намного
    дешевле, чем считать полное распределение отдельно для каждого n.
    """
    states: dict[tuple[int, bool, int], float] = {(calc.current_pity, calc.guarantee, 0): 1.0}
    probabilities = [0.0] * (max_pulls + 1)
    probabilities[0] = 1.0 if target_copies <= 0 else 0.0

    for pulls in range(1, max_pulls + 1):
        new_states: dict[tuple[int, bool, int], float] = {}
        for (pity, guarantee, copies), state_probability in states.items():
            p_legendary = calc.prob_legendary[pity + 1]
            p_no = 1.0 - p_legendary

            if p_no > 0:
                key = (pity + 1, guarantee, copies)
                new_states[key] = new_states.get(key, 0.0) + state_probability * p_no

            if p_legendary > 0:
                if guarantee:
                    key = (0, False, min(copies + 1, target_copies))
                    new_states[key] = new_states.get(key, 0.0) + state_probability * p_legendary
                else:
                    featured_key = (0, False, min(copies + 1, target_copies))
                    new_states[featured_key] = new_states.get(featured_key, 0.0) + (
                        state_probability * p_legendary * calc.featured_rate
                    )
                    non_featured_key = (0, True, copies)
                    new_states[non_featured_key] = new_states.get(non_featured_key, 0.0) + (
                        state_probability * p_legendary * (1.0 - calc.featured_rate)
                    )

        states = new_states
        probabilities[pulls] = sum(
            probability for (_, _, copies), probability in states.items() if copies >= target_copies
        )

    return probabilities


def calculate_mixed(
    total_pulls: int,
    agent_copies: int,
    engine_copies: int,
    agent_pity: int = 0,
    agent_guarantee: bool = False,
    engine_pity: int = 0,
    engine_guarantee: bool = False,
) -> MixedResult:
    """
    Максимизирует P(агент ≥ A и W-Engine ≥ E) по фиксированному сплиту круток.

    Баннеры независимы, поэтому для сплита a/e вероятность обоих целей равна
    P_agent(a) * P_engine(e). Игрок выбирает лучший фиксированный сплит заранее.
    """
    if not (1 <= agent_copies <= AGENT_COPIES_MAX):
        raise ValueError(f"agent_copies must be between 1 and {AGENT_COPIES_MAX}")
    if not (1 <= engine_copies <= ENGINE_COPIES_MAX):
        raise ValueError(f"engine_copies must be between 1 and {ENGINE_COPIES_MAX}")
    if not (0 <= total_pulls <= MAX_TOTAL_PULLS):
        raise ValueError(f"total_pulls must be between 0 and {MAX_TOTAL_PULLS}")

    agent_calc = ZZZGachaCalculator(current_pity=agent_pity, guarantee=agent_guarantee, banner="agent")
    engine_calc = ZZZGachaCalculator(current_pity=engine_pity, guarantee=engine_guarantee, banner="w_engine")

    agent_by_pulls = _target_probabilities(agent_calc, agent_copies, total_pulls)
    engine_by_pulls = _target_probabilities(engine_calc, engine_copies, total_pulls)

    best = MixedResult(
        total_pulls=total_pulls,
        agent_pulls=0,
        engine_pulls=total_pulls,
        agent_copies=agent_copies,
        engine_copies=engine_copies,
        agent_probability=0.0,
        engine_probability=engine_by_pulls[total_pulls],
        both_probability=0.0,
    )
    for agent_pulls in range(total_pulls + 1):
        engine_pulls = total_pulls - agent_pulls
        agent_probability = agent_by_pulls[agent_pulls]
        engine_probability = engine_by_pulls[engine_pulls]
        both_probability = agent_probability * engine_probability
        if both_probability > best.both_probability or (
            both_probability == best.both_probability and agent_probability > best.agent_probability
        ):
            best = MixedResult(
                total_pulls=total_pulls,
                agent_pulls=agent_pulls,
                engine_pulls=engine_pulls,
                agent_copies=agent_copies,
                engine_copies=engine_copies,
                agent_probability=agent_probability,
                engine_probability=engine_probability,
                both_probability=both_probability,
            )
    return best
