"""Проверки синхронизации статической web-версии с Python-ядром."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CORE_FILES = ("__init__.py", "wish_calculator.py", "pull_calculator.py", "mixed_calculator.py", "storage.py")


def test_generated_core_copies_match_source() -> None:
    for name in CORE_FILES:
        assert (DOCS / "py" / "core" / name).read_text(encoding="utf-8") == (ROOT / "core" / name).read_text(
            encoding="utf-8"
        )


def test_web_bridge_copy_matches_source() -> None:
    assert (DOCS / "py" / "web_bridge.py").read_text(encoding="utf-8") == (ROOT / "web_bridge.py").read_text(
        encoding="utf-8"
    )


def test_web_assets_exist() -> None:
    for name in ("index.html", "styles.css", "app.js", ".nojekyll"):
        assert (DOCS / name).exists()


def test_events_snapshot_is_valid_json() -> None:
    payload = json.loads((DOCS / "data" / "events.json").read_text(encoding="utf-8"))
    assert "generated_at" in payload
    assert isinstance(payload["events"], list)


def test_index_uses_relative_assets() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    assert "./styles.css" in html
    assert "./app.js" in html
    assert "pyodide" in html
