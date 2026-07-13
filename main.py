import flet as ft

from app import ZZZGachaApp


def main(page: ft.Page):
    # Инициализация приложения с передачей страницы
    app = ZZZGachaApp(page)


if __name__ == "__main__":
    # Запуск с использованием актуального ft.run() для Flet 0.85.3
    ft.run(main)
