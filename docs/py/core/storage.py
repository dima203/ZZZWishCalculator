import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def _get_config_dir() -> Path:
    """Возвращает директорию конфигурации."""
    return Path.home() / ".zzz_wish_calculator"


def _get_config_file() -> Path:
    """Возвращает путь к файлу настроек."""
    return _get_config_dir() / "settings.json"


DEFAULT_SETTINGS: dict[str, dict[str, Any]] = {
    "wish": {
        "pity": 30,
        "guarantee": False,
        "pulls": 50,
        "copies": 1,
        "banner": "agent",
    },
    "pull": {
        "current_pulls": 0,
        "current_polychromes": 0,
        "current_monochromes": 0,
        "subscription_days": 0,
        "days": 30,
    },
}


def ensure_config_dir() -> None:
    """Создает директорию конфигурации, если её нет."""
    _get_config_dir().mkdir(parents=True, exist_ok=True)


def load_settings() -> dict[str, Any]:
    """Загружает настройки из файла."""
    ensure_config_dir()
    config_file = _get_config_file()
    if not config_file.exists():
        return deepcopy(DEFAULT_SETTINGS)

    try:
        with open(config_file, encoding="utf-8") as f:
            data = json.load(f)

        result = deepcopy(DEFAULT_SETTINGS)
        for key, value in data.items():
            if key in result and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
    except (OSError, json.JSONDecodeError):
        return deepcopy(DEFAULT_SETTINGS)


def save_settings(settings: dict[str, Any]) -> bool:
    """Сохраняет настройки в файл."""
    ensure_config_dir()
    config_file = _get_config_file()
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def get_wish_settings() -> dict[str, Any]:
    """Получает настройки калькулятора шансов."""
    return load_settings().get("wish", DEFAULT_SETTINGS["wish"])


def save_wish_settings(
    pity: int,
    guarantee: bool,
    pulls: int,
    copies: int,
    banner: str = "agent",
) -> bool:
    """Сохраняет настройки калькулятора шансов."""
    settings = load_settings()
    settings["wish"] = {
        "pity": pity,
        "guarantee": guarantee,
        "pulls": pulls,
        "copies": copies,
        "banner": banner,
    }
    return save_settings(settings)


def get_pull_settings() -> dict[str, Any]:
    """Получает настройки калькулятора круток."""
    return load_settings().get("pull", DEFAULT_SETTINGS["pull"])


def save_pull_settings(
    current_pulls: int,
    current_polychromes: int,
    current_monochromes: int,
    subscription_days: int,
    days: int,
) -> bool:
    """Сохраняет настройки калькулятора круток."""
    settings = load_settings()
    settings["pull"] = {
        "current_pulls": current_pulls,
        "current_polychromes": current_polychromes,
        "current_monochromes": current_monochromes,
        "subscription_days": subscription_days,
        "days": days,
    }
    return save_settings(settings)
