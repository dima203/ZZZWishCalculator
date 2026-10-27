"""Тесты чистых helper'ов инструмента скриншотов (без запуска окна)."""

from pathlib import Path

import pytest

from tools.screenshots import TABS, parse_selection, screenshot_path


def test_tabs_cover_all_application_tabs() -> None:
    assert [name for name, _ in TABS] == ["wish", "pulls", "mix"]
    assert [index for _, index in TABS] == [0, 1, 2]


def test_parse_selection_defaults_to_all_tabs() -> None:
    assert parse_selection([]) == TABS


def test_parse_selection_keeps_requested_order() -> None:
    assert parse_selection(["pulls", "wish"]) == [("pulls", 1), ("wish", 0)]
    assert parse_selection(["pulls"]) == [("pulls", 1)]


def test_parse_selection_rejects_unknown_tab() -> None:
    with pytest.raises(ValueError, match="unknown tabs: settings"):
        parse_selection(["wish", "settings"])


def test_screenshot_path_uses_zero_padded_index() -> None:
    assert screenshot_path(Path("out"), 1, "wish") == Path("out") / "01-wish.png"
    assert screenshot_path(Path("out"), 12, "pulls") == Path("out") / "12-pulls.png"
