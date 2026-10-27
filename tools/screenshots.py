"""Boot the real ZZZWishCalculator app and save one PNG per tab.

Usage (from the repository root):

    .\\.venv\\Scripts\\python.exe tools\\screenshots.py [wish pulls]

No arguments captures every tab. PNGs land in tools/screenshots/NN-<tab>.png.
Tabs are switched through ``ZZZGachaApp.tabs.selected_index`` because the app
has no routes. A failure on one tab does not discard already captured PNGs;
a summary table is printed at the end.
"""

import asyncio
import sys
import time
from pathlib import Path

import flet as ft

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import ZZZGachaApp

TABS: list[tuple[str, int]] = [
    ("wish", 0),
    ("pulls", 1),
]
OUT_DIR = Path(__file__).resolve().parent / "screenshots"
BOOT_SETTLE = 1.5
NAV_SETTLE = 0.8
GLOBAL_TIMEOUT = 60.0

RESULTS: list[tuple[str, str, int]] = []
FAILURES: list[str] = []


def parse_selection(names: list[str]) -> list[tuple[str, int]]:
    """Return requested (name, tab index) pairs; empty input means all tabs."""
    known = dict(TABS)
    unknown = [name for name in names if name not in known]
    if unknown:
        raise ValueError(f"unknown tabs: {', '.join(unknown)}")
    if not names:
        return list(TABS)
    return [(name, known[name]) for name in names]


def screenshot_path(out_dir: Path, index: int, name: str) -> Path:
    """Build the zero-padded PNG path for a tab."""
    return out_dir / f"{index:02d}-{name}.png"


async def capture_tab(
    page: ft.Page,
    app: ZZZGachaApp,
    name: str,
    tab_index: int,
    index: int,
    deadline: float,
) -> None:
    """Switch to a tab, let Flet repaint, and store its screenshot."""
    app.tabs.selected_index = tab_index
    page.update()
    await asyncio.sleep(min(NAV_SETTLE, max(deadline - time.monotonic(), 0.1)))
    data = await page.take_screenshot()
    path = screenshot_path(OUT_DIR, index, name)
    path.write_bytes(data)
    RESULTS.append((name, str(path), len(data)))
    print(f"{name} -> {path} ({len(data)} bytes)")


def print_summary() -> None:
    """Print captured files and failures."""
    print("-" * 60)
    for name, path, size in RESULTS:
        print(f"{name:<20} {path} ({size} bytes)")
    print(f"saved: {len(RESULTS)}, failed: {len(FAILURES)}")
    for failure in FAILURES:
        print(f"  FAIL {failure}")


async def main(page: ft.Page) -> None:
    """Capture the selected tabs of a freshly booted app."""
    page.enable_screenshots = True
    selected = parse_selection(sys.argv[1:])
    deadline = time.monotonic() + GLOBAL_TIMEOUT

    app = ZZZGachaApp(page)
    page.update()
    await asyncio.sleep(min(BOOT_SETTLE, max(deadline - time.monotonic(), 0.1)))

    for index, (name, tab_index) in enumerate(selected, start=1):
        if time.monotonic() > deadline - 1.0:
            FAILURES.append(f"{name}: global {int(GLOBAL_TIMEOUT)}s timeout reached")
            continue
        try:
            await capture_tab(page, app, name, tab_index, index, deadline)
        except Exception as exc:
            FAILURES.append(f"{name}: {exc}")
            print(f"{name}: FAILED ({exc})")

    print_summary()
    await page.window.close()


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        parse_selection(sys.argv[1:])
    except ValueError as exc:
        print(exc)
        print(f"available tabs: {', '.join(name for name, _ in TABS)}")
        sys.exit(2)
    ft.run(main)
    sys.exit(1 if FAILURES else 0)
