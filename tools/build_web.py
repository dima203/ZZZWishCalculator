"""Собрать статическую web-версию в docs/ (GitHub Pages, Pyodide).

Запуск:

    .\\.venv\\Scripts\\python.exe tools\\build_web.py
    .\\.venv\\Scripts\\python.exe tools\\build_web.py --no-events

Скрипт копирует Python-ядро в docs/py/core, web_bridge.py и (опционально)
снимок ивентов в docs/data/events.json. Настройки не сохраняются.
"""

import argparse
import json
import shutil
import sys
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import events as event_module

DOCS = ROOT / "docs"
CORE_DEST = DOCS / "py" / "core"
CORE_FILES = ("__init__.py", "wish_calculator.py", "pull_calculator.py", "mixed_calculator.py", "storage.py")


def copy_core() -> None:
    CORE_DEST.mkdir(parents=True, exist_ok=True)
    for name in CORE_FILES:
        shutil.copy2(ROOT / "core" / name, CORE_DEST / name)
    shutil.copy2(ROOT / "web_bridge.py", DOCS / "py" / "web_bridge.py")


def write_events() -> None:
    data_dir = DOCS / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    try:
        events = event_module.load_events()
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "error": None,
            "events": [
                {
                    "post_id": event.post_id,
                    "title": event.title,
                    "start": event.start.isoformat() if event.start else None,
                    "end": event.end.isoformat() if event.end else None,
                    "polychromes": event.polychromes,
                    "tapes": event.tapes,
                    "confidence": event.confidence,
                    "url": event.url,
                }
                for event in events
            ],
        }
    except event_module.EventsError as exc:
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "error": str(exc),
            "events": [],
        }
    (data_dir / "events.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Собрать docs/ для GitHub Pages")
    parser.add_argument("--no-events", action="store_true", help="не ходить в HoYoLAB, записать пустой снимок")
    args = parser.parse_args(argv)

    copy_core()
    if args.no_events:
        (DOCS / "data").mkdir(parents=True, exist_ok=True)
        (DOCS / "data" / "events.json").write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(UTC).isoformat(),
                    "error": "events disabled at build",
                    "events": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    else:
        write_events()
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"web build ready: {DOCS}")
    print(f"events snapshot date: {date.today().isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
