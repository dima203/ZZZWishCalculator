"""Проверки версии ключевых зависимостей (гейт миграции)."""

from importlib.metadata import version


def _version_tuple(package: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version(package).split(".")[:2])


def test_flet_is_major_version_one() -> None:
    assert _version_tuple("flet") >= (1, 0), f"flet {version('flet')} — нужна ветка 1.x"


def test_ruff_is_current() -> None:
    assert _version_tuple("ruff") >= (0, 17), f"ruff {version('ruff')} устарел"
