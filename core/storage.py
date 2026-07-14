import json
from pathlib import Path
from typing import Any, Dict


CONFIG_DIR = Path.home() / ".zzz_wish_calculator"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "wish": {
        "pity": 30,
        "guarantee": False,
        "pulls": 50,
        "copies": 1,
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
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> Dict[str, Any]:
    """Загружает настройки из файла."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Объединяем с дефолтами на случай новых полей
        result = DEFAULT_SETTINGS.copy()
        for key, value in data.items():
            if key in result and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
    except (json.JSONDecodeError, IOError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> bool:
    """Сохраняет настройки в файл."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_wish_settings() -> Dict[str, Any]:
    """Получает настройки калькулятора шансов."""
    return load_settings().get("wish", DEFAULT_SETTINGS["wish"])


def save_wish_settings(pity: int, guarantee: bool, pulls: int, copies: int) -> bool:
    """Сохраняет настройки калькулятора шансов."""
    settings = load_settings()
    settings["wish"] = {
        "pity": pity,
        "guarantee": guarantee,
        "pulls": pulls,
        "copies": copies,
    }
    return save_settings(settings)


def get_pull_settings() -> Dict[str, Any]:
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