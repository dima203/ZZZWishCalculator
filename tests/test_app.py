"""Поведенческие тесты Flet-слоя без запуска окна."""

from datetime import date
from unittest.mock import MagicMock, patch

import flet as ft

from app import ZZZGachaApp
from core.pull_calculator import ZZZPullCalculator
from core.wish_calculator import ZZZGachaCalculator

WISH_DEFAULTS = {"pity": 30, "guarantee": False, "pulls": 50, "copies": 1}
PULL_DEFAULTS = {
    "current_pulls": 0,
    "current_polychromes": 0,
    "current_monochromes": 0,
    "subscription_days": 0,
    "days": 30,
}


def make_app(wish: dict | None = None, pull: dict | None = None) -> ZZZGachaApp:
    page = MagicMock()
    page.window = MagicMock()
    with (
        patch("app.app.storage.get_wish_settings", return_value=wish or WISH_DEFAULTS),
        patch("app.app.storage.get_pull_settings", return_value=pull or PULL_DEFAULTS),
    ):
        return ZZZGachaApp(page)


def set_text_field(field: ft.Container, value: str) -> None:
    field.content.value = value


def test_tabs_are_built_with_two_tabs() -> None:
    app = make_app()

    assert app.tabs.length == 2
    assert app.tabs.selected_index == 0


def test_window_uses_flet_1_window_api() -> None:
    app = make_app()

    assert app.page.window.width == 520
    assert app.page.window.height == 720
    assert app.page.window.min_width == 480
    assert app.page.window.min_height == 600


def test_text_fields_use_outline_input_border() -> None:
    app = make_app()

    field = app.pity_field.content
    assert isinstance(field, ft.TextField)
    assert isinstance(field.border, dict)
    default_border = field.border[ft.ControlState.DEFAULT]
    assert isinstance(default_border, ft.OutlineInputBorder)
    assert default_border.border_radius == 10
    assert default_border.side.width == 1.5
    assert app.guarantee_switch.content.value is False


def test_wish_calculation_reports_at_least_k_copies() -> None:
    app = make_app()
    set_text_field(app.pity_field, "30")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    expected = ZZZGachaCalculator(current_pity=30, guarantee=False).probability_k(50, 1)
    with patch("app.app.storage.save_wish_settings") as save:
        app._on_wish_calculate(None)

    assert save.call_args.args == (30, False, 50, 1)
    assert app.wish_result_text.value == f"ШАНС ≥1 КОПИЙ: {expected * 100:.2f}%"
    assert app.wish_result_card.visible is True
    assert app.page.update.called


def test_wish_calculation_with_zero_copies_means_at_least_one() -> None:
    app = make_app()
    set_text_field(app.pity_field, "0")
    set_text_field(app.pulls_field, "10")
    set_text_field(app.copies_field, "0")

    expected = ZZZGachaCalculator(current_pity=0).probability_at_least_one(10)
    with patch("app.app.storage.save_wish_settings"):
        app._on_wish_calculate(None)

    assert app.wish_result_text.value == f"ШАНС ≥1 КОПИИ: {expected * 100:.2f}%"


def test_wish_calculation_rejects_pity_out_of_range() -> None:
    app = make_app()
    set_text_field(app.pity_field, "90")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    with patch("app.app.storage.save_wish_settings") as save:
        app._on_wish_calculate(None)

    assert app.wish_result_text.value == "⚠️ ОШИБКА: ПИТИ ОТ 0 ДО 89"
    assert app.wish_result_text.color == "#EF4444"
    assert app.wish_result_card.visible is True
    save.assert_not_called()


def test_wish_calculation_rejects_non_numeric_input() -> None:
    app = make_app()
    set_text_field(app.pity_field, "")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    with patch("app.app.storage.save_wish_settings"):
        app._on_wish_calculate(None)

    assert app.wish_result_text.value == "⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА"
    assert app.wish_result_card.visible is True


def test_pull_calculation_shows_total_and_breakdown() -> None:
    app = make_app()
    set_text_field(app.pull_current_pulls, "5")
    set_text_field(app.pull_current_polychromes, "320")
    set_text_field(app.pull_current_monochromes, "160")
    set_text_field(app.pull_subscription_days, "30")
    set_text_field(app.pull_days, "30")

    expected = ZZZPullCalculator(
        current_pulls=5,
        current_polychromes=320,
        current_monochromes=160,
        subscription_days=30,
        days=30,
        start_date=date.today(),
    ).calculate()

    with patch("app.app.storage.save_pull_settings") as save:
        app._on_pull_calculate(None)

    assert save.call_args.args == (5, 320, 160, 30, 30)
    assert app.pull_result_text.value == f"🎯 ИТОГО КРУТОК: {expected.total_pulls}"
    assert f"Итого круток: {expected.total_pulls}" in app.pull_result_details.value
    assert app.pull_result_card.visible is True


def test_pull_calculation_rejects_zero_days() -> None:
    app = make_app()
    set_text_field(app.pull_current_pulls, "0")
    set_text_field(app.pull_current_polychromes, "0")
    set_text_field(app.pull_current_monochromes, "0")
    set_text_field(app.pull_subscription_days, "0")
    set_text_field(app.pull_days, "0")

    with patch("app.app.storage.save_pull_settings") as save:
        app._on_pull_calculate(None)

    assert app.pull_result_text.value == "⚠️ ДНЕЙ ДОЛЖНО БЫТЬ БОЛЬШЕ 0"
    assert app.pull_result_card.visible is True
    save.assert_not_called()
