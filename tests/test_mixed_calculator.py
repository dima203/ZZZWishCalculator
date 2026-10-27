"""Тесты смешанного расчёта агент + W-Engine."""

import pytest

from core.mixed_calculator import (
    AGENT_COPIES_MAX,
    ENGINE_COPIES_MAX,
    _target_probabilities,
    calculate_mixed,
)
from core.wish_calculator import ZZZGachaCalculator


def test_target_probabilities_match_full_distribution() -> None:
    calc = ZZZGachaCalculator(current_pity=10, guarantee=False)
    probabilities = _target_probabilities(calc, target_copies=2, max_pulls=50)

    for pulls in (0, 1, 10, 50):
        assert probabilities[pulls] == pytest.approx(calc.probability_k(pulls, 2))


def test_best_split_for_one_copy_each() -> None:
    result = calculate_mixed(total_pulls=2, agent_copies=1, engine_copies=1)

    assert result.agent_pulls + result.engine_pulls == 2
    assert result.agent_pulls == 1
    assert result.engine_pulls == 1
    assert result.agent_probability == pytest.approx(0.003)
    assert result.engine_probability == pytest.approx(0.0045)
    assert result.both_probability == pytest.approx(0.0000135)


def test_agent_is_prioritized_on_equal_split_value() -> None:
    result = calculate_mixed(total_pulls=3, agent_copies=1, engine_copies=1)

    assert result.agent_pulls + result.engine_pulls == 3
    assert result.both_probability == pytest.approx(result.agent_probability * result.engine_probability)


def test_caps_m6_and_r5() -> None:
    assert AGENT_COPIES_MAX == 7
    assert ENGINE_COPIES_MAX == 5

    with pytest.raises(ValueError, match="agent_copies"):
        calculate_mixed(total_pulls=10, agent_copies=8, engine_copies=1)
    with pytest.raises(ValueError, match="engine_copies"):
        calculate_mixed(total_pulls=10, agent_copies=1, engine_copies=6)


def test_zero_pulls_has_zero_chance() -> None:
    result = calculate_mixed(total_pulls=0, agent_copies=1, engine_copies=1)

    assert result.both_probability == 0.0
    assert result.agent_pulls == 0
    assert result.engine_pulls == 0


def test_total_pulls_is_capped() -> None:
    with pytest.raises(ValueError, match="total_pulls"):
        calculate_mixed(total_pulls=361, agent_copies=1, engine_copies=1)


def test_mixed_result_keeps_requested_targets() -> None:
    result = calculate_mixed(
        total_pulls=180,
        agent_copies=2,
        engine_copies=1,
        agent_pity=30,
        agent_guarantee=False,
        engine_pity=20,
        engine_guarantee=True,
    )

    assert result.agent_copies == 2
    assert result.engine_copies == 1
    assert result.total_pulls == 180
    assert 0.0 < result.both_probability <= 1.0
