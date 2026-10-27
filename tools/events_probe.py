"""Пробный скрипт: официальные новости/ивенты ZZZ через HoYoLAB.

Запуск из корня проекта:

    .\\.venv\\Scripts\\python.exe tools\\events_probe.py --details
    .\\.venv\\Scripts\\python.exe tools\\events_probe.py --type 2 --limit 5
    .\\.venv\\Scripts\\python.exe tools\\events_probe.py --json

Скрипт только читает публичный endpoint HoYoLAB и печатает отчёт. Он ничего не
записывает в настройки приложения и не добавляет доходы в калькулятор.
"""

import argparse
import json
import sys
from operator import itemgetter
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.events import (
    API_BASE,
    GIDS,
    HEADERS,
    event_url,
    extract_event_duration,
    is_official,
    parse_post_items,
)

NEWS_TYPE_LABELS = {1: "новости/анонсы", 2: "события/награды"}


def build_event_rows(
    payloads: list[dict[str, Any]],
    details: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Фильтрует официальные публикации, сортирует и добавляет duration."""
    details = details or {}
    rows: dict[str, dict[str, Any]] = {}
    for payload in payloads:
        for item in parse_post_items(payload):
            if not is_official(item):
                continue
            post = item.get("post") or {}
            post_id = str(post.get("post_id", ""))
            if not post_id:
                continue
            rows[post_id] = {
                "post_id": post_id,
                "subject": post.get("subject") or "",
                "created_at": post.get("created_at") or 0,
                "url": event_url(post_id),
                "duration": extract_event_duration(details.get(post_id, "")),
            }
    return sorted(rows.values(), key=itemgetter("created_at"), reverse=True)


def fetch_news(news_type: int, limit: int) -> dict[str, Any]:
    """Загружает официальную ленту HoYoLAB."""
    response = httpx.get(
        f"{API_BASE}/getNewsList",
        params={"gids": GIDS, "page_size": limit, "type": news_type},
        headers=HEADERS,
        timeout=20.0,
        follow_redirects=True,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("retcode") != 0:
        raise RuntimeError(f"HoYoLAB error: {payload.get('retcode')} {payload.get('message')}")
    return payload


def fetch_detail(post_id: str) -> str:
    """Возвращает structured_content публикации."""
    response = httpx.get(
        f"{API_BASE}/getPostFull",
        params={"post_id": post_id},
        headers=HEADERS,
        timeout=20.0,
        follow_redirects=True,
    )
    response.raise_for_status()
    payload = response.json()
    post = ((payload.get("data") or {}).get("post") or {}).get("post") or {}
    return post.get("structured_content") or ""


def print_report(rows: list[dict[str, Any]]) -> None:
    """Печатает человекочитаемый отчёт."""
    print(f"Официальные публикации ZZZ: {len(rows)}")
    for index, row in enumerate(rows, start=1):
        print(f"{index:>2}. {row['subject']}")
        print(f"    id={row['post_id']}  {row['url']}")
        if row["duration"]:
            print(f"    duration: {row['duration']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Пробный просмотр официальных новостей ZZZ")
    parser.add_argument("--type", choices=("1", "2", "all"), default="all", help="тип ленты HoYoLAB")
    parser.add_argument("--limit", type=int, default=10, help="сколько публикаций запросить на тип")
    parser.add_argument("--details", action="store_true", help="загрузить Event Duration из каждой публикации")
    parser.add_argument("--json", action="store_true", help="вывести JSON вместо текста")
    args = parser.parse_args(argv)

    types = (1, 2) if args.type == "all" else (int(args.type),)
    payloads: list[dict[str, Any]] = []
    try:
        for news_type in types:
            payloads.append(fetch_news(news_type, args.limit))
        rows = build_event_rows(payloads)
        if args.details:
            details = {row["post_id"]: fetch_detail(row["post_id"]) for row in rows}
            rows = build_event_rows(payloads, details)
    except (httpx.HTTPError, RuntimeError, ValueError) as exc:
        print(f"Не удалось получить данные: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print_report(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
