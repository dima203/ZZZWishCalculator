#!/usr/bin/env python3
"""Приложение Flet для ZZZ Wish Calculator."""

import flet as ft


class ZzzWishCalculatorApp:
    """Основное приложение калькулятора гача ZZZ."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.calculator = None  # Будет инициализирована при старте

        # Настройка страницы
        page.title = "ZZZ Wish Calculator"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#1a1a2e"
        page.padding = 0
        page.scroll = None

    def create_ui(self) -> ft.Container:
        """Создаёт UI приложения."""
        # Заголовок
        title = ft.Text(
            "ZZZ Wish Calculator",
            size=32,
            weight=ft.FontWeight.BOLD,
            color="#ffd700",  # Золотистый цвет
            text_align=ft.TextAlign.CENTER,
        )

        # Описание
        description = ft.Text(
            "Симулятор гача для Honkai: Star Rail / Zenless Zone Zero",
            size=14,
            color="#888888",
            text_align=ft.TextAlign.CENTER,
        )

        # Контейнер для полей ввода
        input_container = ft.Column(
            controls=[
                self._create_input_field("Текущий pity (current_pity)", "0"),
                self._create_switch("Последний был стандартным?", True),
                self._create_input_field("Количество круток (num_pulls)", "10"),
            ],
            spacing=16,
        )

        # Кнопка расчёта
        calculate_button = ft.Container(
            content=ft.Text("Рассчитать вероятность"),
            alignment=ft.Alignment.CENTER,
        )

        # Контейнер для результатов
        result_container = ft.Container(
            content=self._create_result_display(),
            alignment=ft.Alignment.CENTER_LEFT,
        )

        # Сводка состояния (Summary)
        summary_container = ft.Container(
            content=self._create_summary_display(),
            alignment=ft.Alignment.CENTER_LEFT,
        )

        # Основной контейнер
        main_container = ft.Column(
            controls=[
                title,
                description,
                ft.Row(controls=[input_container], alignment=ft.MainAxisAlignment.CENTER),
                calculate_button,
                result_container,
                summary_container,
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return main_container

    def _create_input_field(self, label: str, initial_value: str) -> ft.Container:
        """Создаёт поле ввода числа."""
        text_field = ft.TextField(
            value=initial_value,
            label=label,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            border_radius=8,
            bgcolor="#16213e",
            color="#ffffff",
            hint_text="Введите число",
        )

        return ft.Container(
            content=text_field,
        )

    def _create_switch(self, label: str, initial_value: bool) -> ft.Container:
        """Создаёт переключатель."""
        switch = ft.Switch(
            value=initial_value,
            label=label,
            track_color="#ff6b00",  # Оранжевый цвет для трека
        )

        return ft.Container(
            content=switch,
        )

    def _create_result_display(self) -> ft.Text:
        """Создаёт отображение результата."""
        text = ft.Text(
            "Вероятность получения ивентового персонажа:\n",
            size=20,
            weight=ft.FontWeight.BOLD,
            color="#ffd700",  # Золотистый цвет
        )

        return text

    def _create_summary_display(self) -> ft.Text:
        """Создаёт отображение сводки состояния."""
        text = ft.Text(
            "Сводка:\n",
            size=16,
            color="#888888",
        )

        return text

    def _handle_calculate(self, e: ft.ControlEvent) -> None:
        """Обработчик нажатия кнопки расчёта."""
        # Получаем значения из полей ввода (через input_container)
        input_container = self.page.controls[2].content  # Column с controls
        current_pity_text = input_container.controls[0].value  # TextField для pity
        last_was_standard_switch = input_container.controls[1].value  # Switch
        num_pulls_text = input_container.controls[2].value  # TextField для num_pulls

        try:
            # Преобразуем строки в целые числа
            current_pity = int(current_pity_text) if current_pity_text else 0
            num_pulls = int(num_pulls_text) if num_pulls_text else 10

            # Валидация ввода
            if current_pity < 0:
                self._show_error("Текущий pity не может быть отрицательным!")
                return

            if num_pulls <= 0:
                self._show_error("Количество круток должно быть больше 0!")
                return

            # Создаём калькулятор и выполняем симуляцию
            from core.wish import WishCalculator

            self.calculator = WishCalculator(
                current_pity=current_pity,
                last_was_standard=last_was_standard_switch
            )

            probability = self.calculator.simulate_pulls(num_pulls=num_pulls)

            # Обновляем отображение результата (result_container - index 4 в main_container)
            result_text = (
                f"Вероятность получения ивентового персонажа:\n"
                f"{probability:.4f} ({probability * 100:.2f}%)"
            )
            self.page.controls[4].content.value = result_text

            # Обновляем сводку состояния (summary_container - index 5 в main_container)
            summary_data = self.calculator.get_summary()
            summary_text = (
                f"Сводка:\n"
                f"Текущий pity: {summary_data['pity']}\n"
                f"is_guaranteed_event: {summary_data['is_guaranteed_event']}"
            )
            self.page.controls[5].content.value = summary_text

        except ValueError:
            self._show_error("Пожалуйста, введите корректные числа!")
        except Exception as ex:
            self._show_error(f"Ошибка при расчёте: {str(ex)}")

    def _show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке."""
        error_text = ft.Text(
            message,
            color="#ff4444",  # Красный цвет для ошибок
            size=16,
            text_align=ft.TextAlign.CENTER,
        )

        # Добавляем контейнер с ошибкой перед последним элементом
        self.page.insert(error_text, index=-2)


def main(page: ft.Page) -> None:
    """Точка входа в приложение."""
    app = ZzzWishCalculatorApp(page)
    page.add(app.create_ui())

    # Отключаем скроллинг для более чистого UI
    page.scroll = None


if __name__ == "__main__":
    ft.run(main=main)
