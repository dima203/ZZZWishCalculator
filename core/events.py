"""Официальные новости ZZZ и автоматическая оценка дохода с ивентов.

Модуль использует публичную ленту HoYoLAB (gids=8) и фильтрует публикации
официального аккаунта. Суммы, которые не удаётся прочитать из текста, берутся
из каталога известных ивентов или помечаются как estimate (только max).
"""

import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

import httpx

API_BASE = "https://bbs-api-os.hoyolab.com/community/post/wapi"
GIDS = 8
OFFICIAL_UID = "219270333"
OFFICIAL_CERT = "ZZZ Official"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (ZZZWishCalculator events)",
    "Referer": "https://www.hoyolab.com/",
}
CACHE_TTL_SECONDS = 6 * 60 * 60
CACHE_DIR = Path.home() / ".zzz_wish_calculator"
CACHE_FILE = CACHE_DIR / "events_cache.json"

FALLBACK_EVENT_POLYCHROMES = 300
FALLBACK_EVENT_DAYS = 42


class EventsError(RuntimeError):
    """Не удалось получить официальные ивенты и нет кэша."""


# Опубликованные/подтверждённые суммы текущих ивентов 3.3.
# Ключ — фрагмент названия в нижнем регистре; значение — (Polychrome, Encrypted Master Tapes).
EVENT_REWARD_CATALOG: Final[dict[str, tuple[int, int]]] = {
    "spooky funhouse tales": (900, 0),
    "cyber miracle healer": (300, 0),
    "trails of the hobbling crow": (300, 0),
    "repair! drifting art": (300, 0),
    "annihilation simulacrum": (600, 0),
    "enigma of the labyrinth": (1250, 0),
    "all-new program": (0, 10),
    "twitch drops": (50, 0),
    "special program": (300, 0),
    "into your lap": (0, 0),
    "angels support operation": (0, 0),
}

POLY_RE = re.compile(r"Polychrome(?:s)?\s*[×xX]\s*([\d,]+)")
TAPE_RE = re.compile(r"Encrypted Master Tape(?:s)?\s*[×xX]\s*(\d+)")
ISO_DATE_RE = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")
MONTH_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:,\s*(\d{4}))?"
)
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


@dataclass(frozen=True)
class EventReward:
    """Оценка дохода одного ивента."""

    post_id: str
    title: str
    start: date | None
    end: date | None
    polychromes: int
    tapes: int
    confidence: str
    url: str = ""


@dataclass(frozen=True)
class EventIncome:
    """Суммарный доход с ивентов за период."""

    events: tuple[EventReward, ...] = ()
    polychromes_min: int = 0
    polychromes_max: int = 0
    tapes: int = 0

    @property
    def min_pulls(self) -> int:
        return (self.polychromes_min + self.tapes * 160) // 160

    @property
    def max_pulls(self) -> int:
        return (self.polychromes_max + self.tapes * 160) // 160

    @classmethod
    def empty(cls) -> "EventIncome":
        return cls()


def is_official(item: dict[str, Any]) -> bool:
    """Проверяет, что публикация принадлежит официальному аккаунту ZZZ."""
    user = item.get("user") or {}
    certification = user.get("certification") or {}
    return user.get("uid") == OFFICIAL_UID or certification.get("desc") == OFFICIAL_CERT


def parse_post_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Достаёт список публикаций из ответа getNewsList."""
    return list((payload.get("data") or {}).get("list") or [])


def event_url(post_id: str) -> str:
    """Ссылка на официальную публикацию."""
    return f"https://www.hoyolab.com/article/{post_id}"


def structured_text(structured_content: str) -> str:
    """Превращает Quill-ops в плоский текст; обычный текст возвращает как есть."""
    try:
        operations = json.loads(structured_content)
    except (json.JSONDecodeError, TypeError):
        return structured_content
    if not isinstance(operations, list):
        return structured_content
    return "".join(
        operation.get("insert", "")
        for operation in operations
        if isinstance(operation, dict) and isinstance(operation.get("insert"), str)
    )


def extract_event_duration(structured_content: str) -> str | None:
    """Достаёт строку Event Duration из Quill-ops публикации."""
    text = structured_text(structured_content)
    match = re.search(r"Event Duration\s*([^\n]+)", text)
    if match:
        value = match.group(1).strip().lstrip(":：").strip()
        if len(value) >= 6 and re.search(r"\d", value):
            return value
    return None


def parse_rewards(text: str) -> tuple[int, int]:
    """Суммирует явно указанные Polychrome и Encrypted Master Tapes."""
    polychromes = sum(int(match.replace(",", "")) for match in POLY_RE.findall(text))
    tapes = sum(int(match) for match in TAPE_RE.findall(text))
    return polychromes, tapes


def parse_duration(text: str, fallback_date: date) -> tuple[date, date] | None:
    """Парсит диапазон дат ивента; поддерживает ISO и Month Day – Month Day."""
    iso_matches = ISO_DATE_RE.findall(text)
    if len(iso_matches) >= 2:
        start = date(int(iso_matches[0][0]), int(iso_matches[0][1]), int(iso_matches[0][2]))
        end = date(int(iso_matches[1][0]), int(iso_matches[1][1]), int(iso_matches[1][2]))
        return start, end
    if len(iso_matches) == 1 and "after" in text.lower():
        end = date(int(iso_matches[0][0]), int(iso_matches[0][1]), int(iso_matches[0][2]))
        return fallback_date, end

    month_matches = MONTH_RE.findall(text)
    if len(month_matches) >= 2:
        start_month, start_day, _ = month_matches[0]
        end_month, end_day, _ = month_matches[1]
        start = date(fallback_date.year, MONTHS[start_month.lower()], int(start_day))
        end = date(fallback_date.year, MONTHS[end_month.lower()], int(end_day))
        if end < start:
            end = end.replace(year=end.year + 1)
        return start, end
    if len(month_matches) == 1 and "after" in text.lower():
        month, day, _ = month_matches[0]
        end = date(fallback_date.year, MONTHS[month.lower()], int(day))
        return fallback_date, end
    return None


def _catalog_reward(title: str) -> tuple[int, int] | None:
    lowered = title.lower()
    for fragment, reward in EVENT_REWARD_CATALOG.items():
        if fragment in lowered:
            return reward
    return None


def estimate_post(item: dict[str, Any], detail_text: str, fallback_date: date) -> EventReward | None:
    """Оценивает один официальный пост; None — если это не доход с ивента."""
    if not is_official(item):
        return None
    post = item.get("post") or {}
    title = post.get("subject") or ""
    post_id = str(post.get("post_id", ""))
    lowered = title.lower()
    if not post_id or "city fund" in lowered:
        return None

    text = structured_text(detail_text)
    if "update announcement" in lowered:
        # В патчноуте перечислены награды других ивентов; считаем только компенсации.
        polychromes = sum(
            int(match.replace(",", ""))
            for match in re.findall(r"Compensation:\s*Polychrome(?:s)?\s*[×xX]\s*([\d,]+)", text)
        )
        tapes = 0
    else:
        polychromes, tapes = parse_rewards(text)
    catalog = _catalog_reward(title)
    confidence = "explicit"

    if catalog is not None:
        polychromes = max(polychromes, catalog[0])
        tapes = max(tapes, catalog[1])
        confidence = "catalog"
    elif polychromes == 0 and tapes == 0:
        if "event details" in lowered:
            polychromes = FALLBACK_EVENT_POLYCHROMES
            confidence = "estimate"
        else:
            return None

    duration_text = extract_event_duration(detail_text)
    parsed_duration = parse_duration(duration_text or text, fallback_date)
    if parsed_duration is None:
        if not any(word in lowered for word in ("event", "twitch", "update announcement", "compensation")):
            return None
        parsed_duration = (fallback_date, fallback_date + timedelta(days=FALLBACK_EVENT_DAYS))

    start, end = parsed_duration
    return EventReward(
        post_id=post_id,
        title=title,
        start=start,
        end=end,
        polychromes=polychromes,
        tapes=tapes,
        confidence=confidence,
        url=event_url(post_id),
    )


def summarize_events(events: list[EventReward], start_date: date, days: int) -> EventIncome:
    """Суммирует ивенты, пересекающиеся с периодом прогноза."""
    period_end = start_date + timedelta(days=days)
    active = [
        event
        for event in events
        if event.start is not None and event.end is not None and event.start <= period_end and event.end >= start_date
    ]
    polychromes_min = sum(event.polychromes for event in active if event.confidence != "estimate")
    polychromes_max = sum(event.polychromes for event in active)
    tapes = sum(event.tapes for event in active)
    return EventIncome(
        events=tuple(sorted(active, key=lambda event: event.start or date.min)),
        polychromes_min=polychromes_min,
        polychromes_max=polychromes_max,
        tapes=tapes,
    )


def _created_date(post: dict[str, Any]) -> date:
    timestamp = post.get("created_at") or 0
    if not timestamp:
        return date.today()
    return datetime.fromtimestamp(int(timestamp), tz=UTC).date()


def _fetch_news(client: httpx.Client, news_type: int, limit: int) -> dict[str, Any]:
    response = client.get(
        f"{API_BASE}/getNewsList",
        params={"gids": GIDS, "page_size": limit, "type": news_type},
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("retcode") != 0:
        raise RuntimeError(f"HoYoLAB error: {payload.get('retcode')} {payload.get('message')}")
    return payload


def _fetch_detail(client: httpx.Client, post_id: str) -> str:
    response = client.get(f"{API_BASE}/getPostFull", params={"post_id": post_id})
    response.raise_for_status()
    payload = response.json()
    post = ((payload.get("data") or {}).get("post") or {}).get("post") or {}
    return post.get("structured_content") or ""


def fetch_official_events(limit: int = 30) -> list[EventReward]:
    """Загружает официальные ивенты и оценивает их доход."""
    candidates: dict[str, dict[str, Any]] = {}
    with httpx.Client(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
        for news_type in (1, 2):
            payload = _fetch_news(client, news_type, limit)
            for item in parse_post_items(payload):
                if not is_official(item):
                    continue
                post = item.get("post") or {}
                title = (post.get("subject") or "").lower()
                if not any(
                    keyword in title
                    for keyword in ("event", "twitch", "all-new program", "update announcement", "special program")
                ):
                    continue
                post_id = str(post.get("post_id", ""))
                if post_id:
                    candidates[post_id] = item

        events: list[EventReward] = []
        for post_id, item in list(candidates.items())[:30]:
            post = item.get("post") or {}
            try:
                detail = _fetch_detail(client, post_id)
            except httpx.HTTPError:
                detail = ""
            reward = estimate_post(item, detail, _created_date(post))
            if reward is not None:
                events.append(reward)
    return sorted(events, key=lambda event: event.start or date.min)


def _read_cache() -> tuple[list[EventReward], float] | None:
    if not CACHE_FILE.exists():
        return None
    try:
        payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        fetched_at = float(payload.get("fetched_at", 0))
        events = []
        for raw in payload.get("events", []):
            events.append(
                EventReward(
                    post_id=raw["post_id"],
                    title=raw["title"],
                    start=date.fromisoformat(raw["start"]) if raw.get("start") else None,
                    end=date.fromisoformat(raw["end"]) if raw.get("end") else None,
                    polychromes=int(raw.get("polychromes", 0)),
                    tapes=int(raw.get("tapes", 0)),
                    confidence=raw.get("confidence", "estimate"),
                    url=raw.get("url", ""),
                )
            )
        return events, fetched_at
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _write_cache(events: list[EventReward]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": time.time(),
        "events": [
            {
                **asdict(event),
                "start": event.start.isoformat() if event.start else None,
                "end": event.end.isoformat() if event.end else None,
            }
            for event in events
        ],
    }
    CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_events(force: bool = False) -> list[EventReward]:
    """Возвращает ивенты из кэша или сети; при сбое — устаревший кэш."""
    cached = _read_cache()
    if cached is not None:
        events, fetched_at = cached
        if not force and time.time() - fetched_at < CACHE_TTL_SECONDS:
            return events
    try:
        events = fetch_official_events()
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        if cached is not None:
            return cached[0]
        raise EventsError(str(exc)) from exc
    _write_cache(events)
    return events


def get_event_income(start_date: date, days: int, force: bool = False) -> EventIncome:
    """Суммарный доход с ивентов, пересекающихся с периодом."""
    return summarize_events(load_events(force=force), start_date, days)
