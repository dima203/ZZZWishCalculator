"""Поведенческие тесты Flet-слоя без запуска окна."""

import asyncio
from datetime import date
from unittest.mock import MagicMock, patch

import flet as ft

from app import ZZZGachaApp
from core.events import EventIncome
from core.pull_calculator import ZZZPullCalculator
from core.wish_calculator import ZZZGachaCalculator

WISH_DEFAULTS = {"pity": 30, "guarantee": False, "pulls": 50, "copies": 1, "banner": "agent"}
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


def run(coro):
    return asyncio.run(coro)


def _collect_text(control: ft.Control) -> list[str]:
    """Collect text values from a control tree for structural assertions."""
    values: list[str] = []
    if isinstance(control, ft.Text) and control.value:
        values.append(control.value)
    content = getattr(control, "content", None)
    if isinstance(content, ft.Control):
        values.extend(_collect_text(content))
    for child in getattr(control, "controls", None) or []:
        values.extend(_collect_text(child))
    title = getattr(control, "title", None)
    if isinstance(title, ft.Control):
        values.extend(_collect_text(title))
    return values


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
    assert app.pity_field.content.label == "КРУТОК БЕЗ S-РАНГА"


def test_banner_selector_defaults_to_agent_and_switches() -> None:
    app = make_app()

    assert isinstance(app.banner_select, ft.SegmentedButton)
    assert app.banner_select.selected == ["agent"]
    assert app.banner == "agent"

    app.banner_select.selected = ["w_engine"]
    app._on_banner_change(None)

    assert app.banner == "w_engine"
    assert "W-ENGINE" in app.wish_section_subtitle.value


def test_rates_panel_is_collapsed_and_lists_verified_sources() -> None:
    app = make_app()

    assert isinstance(app.rates_info, ft.ExpansionTile)
    assert app.rates_info.expanded is False
    text = " ".join(_collect_text(app.rates_info))
    for expected in ("RIDU", "HOLLOW ZERO", "SHIYU", "DEADLY ASSAULT", "780", "300"):
        assert expected in text


def test_wish_calculation_reports_at_least_k_copies() -> None:
    app = make_app()
    set_text_field(app.pity_field, "30")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    expected = ZZZGachaCalculator(current_pity=30, guarantee=False).probability_k(50, 1)
    with patch("app.app.storage.save_wish_settings") as save:
        run(app._on_wish_calculate(None))

    assert save.call_args.args == (30, False, 50, 1, "agent")
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
        run(app._on_wish_calculate(None))

    assert app.wish_result_text.value == f"ШАНС ≥1 КОПИИ: {expected * 100:.2f}%"


def test_wish_calculation_rejects_pity_out_of_range() -> None:
    app = make_app()
    set_text_field(app.pity_field, "90")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    with patch("app.app.storage.save_wish_settings") as save:
        run(app._on_wish_calculate(None))

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
        run(app._on_wish_calculate(None))

    assert app.wish_result_text.value == "⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА"
    assert app.wish_result_card.visible is True


def test_w_engine_calculation_uses_75_25() -> None:
    app = make_app()
    app.banner_select.selected = ["w_engine"]
    app._on_banner_change(None)
    set_text_field(app.pity_field, "0")
    set_text_field(app.pulls_field, "1")
    set_text_field(app.copies_field, "1")

    expected = ZZZGachaCalculator(current_pity=0, banner="w_engine").probability_k(1, 1)
    with patch("app.app.storage.save_wish_settings") as save:
        run(app._on_wish_calculate(None))

    assert save.call_args.args == (0, False, 1, 1, "w_engine")
    assert app.wish_result_text.value == f"ШАНС ≥1 W-ENGINE: {expected * 100:.2f}%"


def test_w_engine_pity_validation() -> None:
    app = make_app()
    app.banner_select.selected = ["w_engine"]
    app._on_banner_change(None)
    set_text_field(app.pity_field, "80")
    set_text_field(app.pulls_field, "10")
    set_text_field(app.copies_field, "1")

    with patch("app.app.storage.save_wish_settings") as save:
        run(app._on_wish_calculate(None))

    assert app.wish_result_text.value == "⚠️ ОШИБКА: ПИТИ ОТ 0 ДО 79"
    save.assert_not_called()


def test_progress_is_visible_while_wish_calculates() -> None:
    app = make_app()
    set_text_field(app.pity_field, "30")
    set_text_field(app.pulls_field, "50")
    set_text_field(app.copies_field, "1")

    async def scenario() -> None:
        task = asyncio.create_task(app._on_wish_calculate(None))
        await asyncio.sleep(0)
        assert app.wish_progress.visible is True
        assert app.wish_button.disabled is True
        await task
        assert app.wish_progress.visible is False
        assert app.wish_button.disabled is False

    with patch("app.app.storage.save_wish_settings"):
        asyncio.run(scenario())


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

    with (
        patch("app.app.events.get_event_income", return_value=EventIncome.empty()),
        patch("app.app.storage.save_pull_settings") as save,
    ):
        run(app._on_pull_calculate(None))

    assert save.call_args.args == (5, 320, 160, 30, 30)
    assert app.pull_result_text.value == f"🎯 ИТОГО КРУТОК: {expected.total_pulls_min}–{expected.total_pulls_max}"
    assert f"Итого круток (мин.): {expected.total_pulls_min}" in app.pull_result_details.value
    assert f"Итого круток (макс.): {expected.total_pulls_max}" in app.pull_result_details.value
    assert app.pull_result_card.visible is True


def test_pull_calculation_includes_event_income() -> None:
    app = make_app()
    set_text_field(app.pull_current_pulls, "0")
    set_text_field(app.pull_current_polychromes, "0")
    set_text_field(app.pull_current_monochromes, "0")
    set_text_field(app.pull_subscription_days, "0")
    set_text_field(app.pull_days, "30")

    income = EventIncome(polychromes_min=900, polychromes_max=900, tapes=10)
    expected = ZZZPullCalculator(days=30, start_date=date.today()).calculate()

    with patch("app.app.events.get_event_income", return_value=income):
        run(app._on_pull_calculate(None))

    event_pulls = income.max_pulls
    assert event_pulls == 15
    assert app.pull_result_text.value == (
        f"🎯 ИТОГО КРУТОК: {expected.total_pulls_min + event_pulls}–{expected.total_pulls_max + event_pulls}"
    )
    assert f"Ивенты (макс.): {event_pulls}" in app.pull_result_details.value
    assert f"+{event_pulls}–{event_pulls}" in app.events_status.value


def test_events_toggle_disables_automatic_income() -> None:
    app = make_app()
    set_text_field(app.pull_days, "30")
    app.events_switch.value = False
    app._on_events_toggle(None)

    with patch("app.app.events.get_event_income") as fetch:
        run(app._on_pull_calculate(None))

    fetch.assert_not_called()
    assert app.events_status.value == "Ивенты: отключены"


def test_pull_calculation_rejects_zero_days() -> None:
    app = make_app()
    set_text_field(app.pull_current_pulls, "0")
    set_text_field(app.pull_current_polychromes, "0")
    set_text_field(app.pull_current_monochromes, "0")
    set_text_field(app.pull_subscription_days, "0")
    set_text_field(app.pull_days, "0")

    with (
        patch("app.app.events.get_event_income", return_value=EventIncome.empty()),
        patch("app.app.storage.save_pull_settings") as save,
    ):
        run(app._on_pull_calculate(None))

    assert app.pull_result_text.value == "⚠️ ДНЕЙ ДОЛЖНО БЫТЬ БОЛЬШЕ 0"
    assert app.pull_result_card.visible is True
    save.assert_not_called()
