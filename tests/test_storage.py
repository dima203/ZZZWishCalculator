import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.storage import (
    DEFAULT_SETTINGS,
    ensure_config_dir,
    get_pull_settings,
    get_wish_settings,
    load_settings,
    save_pull_settings,
    save_settings,
    save_wish_settings,
)


class TestStorage:
    """Тесты для модуля сохранения настроек."""

    def setup_method(self):
        """Создает временную директорию для тестов."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config_dir = Path(self.temp_dir) / ".zzz_wish_calculator"
        self.temp_config_file = self.temp_config_dir / "settings.json"

    def teardown_method(self):
        """Удаляет временные файлы после тестов."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_config_dir_creates_directory(self):
        """Проверяет создание директории конфигурации."""
        with patch("core.storage._get_config_dir", return_value=self.temp_config_dir):
            ensure_config_dir()
            assert self.temp_config_dir.exists()
            assert self.temp_config_dir.is_dir()

    def test_load_settings_returns_defaults_when_no_file(self):
        """Проверяет возврат дефолтных настроек, если файл не существует."""
        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            settings = load_settings()
            assert settings == DEFAULT_SETTINGS

    def test_load_settings_loads_from_file(self):
        """Проверяет загрузку настроек из файла."""
        test_settings = {
            "wish": {"pity": 50, "guarantee": True, "pulls": 100, "copies": 2, "banner": "w_engine"},
            "pull": {
                "current_pulls": 10,
                "current_polychromes": 1600,
                "current_monochromes": 80,
                "subscription_days": 15,
                "days": 60,
            },
        }

        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.temp_config_file, "w", encoding="utf-8") as f:
                json.dump(test_settings, f)

            settings = load_settings()
            assert settings == test_settings

    def test_load_settings_merges_with_defaults(self):
        """Проверяет слияние загруженных настроек с дефолтами."""
        partial_settings = {
            "wish": {"pity": 75},
        }

        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.temp_config_file, "w", encoding="utf-8") as f:
                json.dump(partial_settings, f)

            settings = load_settings()
            assert settings["wish"]["pity"] == 75
            assert settings["wish"]["guarantee"] == DEFAULT_SETTINGS["wish"]["guarantee"]
            assert settings["wish"]["banner"] == "agent"
            assert settings["pull"] == DEFAULT_SETTINGS["pull"]

    def test_load_settings_does_not_mutate_defaults(self):
        """Загрузка не должна менять общий DEFAULT_SETTINGS."""
        custom = {"wish": {"banner": "w_engine"}}

        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            self.temp_config_file.write_text(json.dumps(custom), encoding="utf-8")
            assert load_settings()["wish"]["banner"] == "w_engine"

        assert DEFAULT_SETTINGS["wish"]["banner"] == "agent"

    def test_load_settings_handles_corrupted_json(self):
        """Проверяет обработку поврежденного JSON файла."""
        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            Path(self.temp_config_file).write_text("{ invalid json }", encoding="utf-8")

            settings = load_settings()
            assert settings == DEFAULT_SETTINGS

    def test_save_settings_creates_file(self):
        """Проверяет создание файла при сохранении."""
        test_settings = {"wish": {"pity": 10}, "pull": {"days": 7}}

        with (
            patch("core.storage._get_config_dir", return_value=self.temp_config_dir),
            patch("core.storage._get_config_file", return_value=self.temp_config_file),
        ):
            result = save_settings(test_settings)
            assert result is True
            assert self.temp_config_file.exists()

            with open(self.temp_config_file, encoding="utf-8") as f:
                saved = json.load(f)
            assert saved == test_settings

    def test_save_settings_returns_false_on_error(self):
        """Проверяет возврат False при ошибке сохранения."""
        # На Windows невозможно создать файл в несуществующем пути без прав
        # Используем мок для симуляции ошибки IOError
        with (
            patch("core.storage._get_config_dir", return_value=Path("/invalid/path")),
            patch("core.storage._get_config_file", return_value=Path("/invalid/path/settings.json")),
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            result = save_settings({"test": "value"})
            assert result is False

    def test_get_wish_settings(self):
        """Проверяет получение настроек wish калькулятора."""
        test_settings = {
            "wish": {"pity": 25, "guarantee": True, "pulls": 30, "copies": 1, "banner": "agent"},
            "pull": DEFAULT_SETTINGS["pull"],
        }

        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.temp_config_file, "w", encoding="utf-8") as f:
                json.dump(test_settings, f)

            wish_settings = get_wish_settings()
            assert wish_settings == test_settings["wish"]

    def test_save_wish_settings(self):
        """Проверяет сохранение настроек wish калькулятора."""
        with (
            patch("core.storage._get_config_dir", return_value=self.temp_config_dir),
            patch("core.storage._get_config_file", return_value=self.temp_config_file),
        ):
            result = save_wish_settings(pity=40, guarantee=True, pulls=80, copies=3, banner="w_engine")
            assert result is True

            settings = load_settings()
            assert settings["wish"] == {
                "pity": 40,
                "guarantee": True,
                "pulls": 80,
                "copies": 3,
                "banner": "w_engine",
            }
            assert settings["pull"] == DEFAULT_SETTINGS["pull"]

    def test_get_pull_settings(self):
        """Проверяет получение настроек pull калькулятора."""
        test_settings = {
            "wish": DEFAULT_SETTINGS["wish"],
            "pull": {
                "current_pulls": 5,
                "current_polychromes": 800,
                "current_monochromes": 40,
                "subscription_days": 10,
                "days": 45,
            },
        }

        with patch("core.storage._get_config_file", return_value=self.temp_config_file):
            self.temp_config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.temp_config_file, "w", encoding="utf-8") as f:
                json.dump(test_settings, f)

            pull_settings = get_pull_settings()
            assert pull_settings == test_settings["pull"]

    def test_save_pull_settings(self):
        """Проверяет сохранение настроек pull калькулятора."""
        with (
            patch("core.storage._get_config_dir", return_value=self.temp_config_dir),
            patch("core.storage._get_config_file", return_value=self.temp_config_file),
        ):
            result = save_pull_settings(
                current_pulls=20,
                current_polychromes=3200,
                current_monochromes=160,
                subscription_days=30,
                days=90,
            )
            assert result is True

            settings = load_settings()
            assert settings["pull"] == {
                "current_pulls": 20,
                "current_polychromes": 3200,
                "current_monochromes": 160,
                "subscription_days": 30,
                "days": 90,
            }
            assert settings["wish"] == DEFAULT_SETTINGS["wish"]

    def test_default_settings_structure(self):
        """Проверяет структуру дефолтных настроек."""
        assert "wish" in DEFAULT_SETTINGS
        assert "pull" in DEFAULT_SETTINGS
        assert set(DEFAULT_SETTINGS["wish"].keys()) == {"pity", "guarantee", "pulls", "copies", "banner"}
        assert set(DEFAULT_SETTINGS["pull"].keys()) == {
            "current_pulls",
            "current_polychromes",
            "current_monochromes",
            "subscription_days",
            "days",
        }

    def test_settings_persistence_roundtrip(self):
        """Проверяет полный цикл сохранения и загрузки."""
        with (
            patch("core.storage._get_config_dir", return_value=self.temp_config_dir),
            patch("core.storage._get_config_file", return_value=self.temp_config_file),
        ):
            # Сохраняем настройки
            save_wish_settings(pity=60, guarantee=False, pulls=120, copies=2, banner="agent")
            save_pull_settings(
                current_pulls=15,
                current_polychromes=2400,
                current_monochromes=120,
                subscription_days=20,
                days=50,
            )

            # Загружаем и проверяем
            loaded = load_settings()
            assert loaded["wish"] == {
                "pity": 60,
                "guarantee": False,
                "pulls": 120,
                "copies": 2,
                "banner": "agent",
            }
            assert loaded["pull"] == {
                "current_pulls": 15,
                "current_polychromes": 2400,
                "current_monochromes": 120,
                "subscription_days": 20,
                "days": 50,
            }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
