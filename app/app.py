import flet as ft

from core import ZZZGachaCalculator


# Акцентные цвета ZZZ (на основе фирменного стиля)
COLORS = {
    "bg": "#0D0D0D",          # тёмный фон
    "primary": "#FF6B00",      # оранжевый – основной акцент
    "secondary": "#00B4D8",    # голубой – вторичный
    "accent": "#8B5CF6",       # фиолетовый – для выделений
    "text": "#FFFFFF",
    "text_secondary": "#B0B0B0",
    "success": "#4ADE80",      # зелёный для успешных результатов
    "error": "#FF4444",        # красный для ошибок
    "card_bg": "#1A1A1A",      # фон карточек
}

class ZZZGachaApp:
    """Главное представление приложения."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        self._build_ui()

    def _setup_page(self):
        """Настройка страницы: заголовок, размер, тема."""
        self.page.title = "ZZZ Gacha Calculator"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = 40
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLORS["bg"]

        # Обновляем тему для цветовых акцентов
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.ORANGE_700,
                secondary=ft.Colors.LIGHT_BLUE_400,
                tertiary=ft.Colors.PURPLE_400,
            )
        )

    def _build_ui(self):
        """Сборка интерфейса."""
        # Поля ввода
        self.pity_field = ft.TextField(
            label="Текущий счётчик (pity)",
            value="30",
            width=220,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=COLORS["secondary"],
            focused_border_color=COLORS["primary"],
            label_style=ft.TextStyle(color=COLORS["text_secondary"]),
            text_style=ft.TextStyle(color=COLORS["text"]),
        )

        self.guarantee_switch = ft.Switch(
            label="Гарант включён",
            value=False,
            active_color=COLORS["primary"],
            inactive_thumb_color=COLORS["text_secondary"],
            inactive_track_color=COLORS["card_bg"],
            label_text_style=ft.TextStyle(color=COLORS["text_secondary"]),
        )

        self.pulls_field = ft.TextField(
            label="Количество круток (N)",
            value="50",
            width=220,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=COLORS["secondary"],
            focused_border_color=COLORS["primary"],
            label_style=ft.TextStyle(color=COLORS["text_secondary"]),
            text_style=ft.TextStyle(color=COLORS["text"]),
        )

        self.copies_field = ft.TextField(
            label="Желаемое количество копий (k)",
            value="1",
            width=220,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=COLORS["secondary"],
            focused_border_color=COLORS["primary"],
            label_style=ft.TextStyle(color=COLORS["text_secondary"]),
            text_style=ft.TextStyle(color=COLORS["text"]),
        )

        # Кнопка расчёта в стиле ZZZ
        self.calc_button = ft.Button(
            "Рассчитать",
            on_click=self._on_calculate,
            width=220,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor=COLORS["primary"],
                color=COLORS["bg"],
                padding=ft.Padding(20, 12, 20, 12),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
            ),
        )

        # Поля для результатов
        self.result_text = ft.Text(
            "",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
        )
        self.result_details = ft.Text(
            "",
            size=16,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.CENTER,
        )

        # Карточка для результата (обёртка с фоном и границей)
        result_card = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    self.result_text,
                    self.result_details,
                ],
            ),
            padding=20,
            border=ft.Border.all(1, COLORS["secondary"]),
            border_radius=12,
            bgcolor=COLORS["card_bg"],
            width=400,
            visible=False,  # будет показан после первого расчёта
        )
        self.result_card = result_card

        # Заголовок
        title = ft.Text(
            "⚡ ZZZ Wish Simulator ⚡",
            size=34,
            weight=ft.FontWeight.BOLD,
            color=COLORS["primary"],
            text_align=ft.TextAlign.CENTER,
        )
        subtitle = ft.Text(
            "Рассчитай шанс выпадения ивентового персонажа",
            size=16,
            color=COLORS["text_secondary"],
            text_align=ft.TextAlign.CENTER,
        )

        # Основная колонка
        main_column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                title,
                subtitle,
                ft.Divider(height=1, color=COLORS["text_secondary"]),
                self.pity_field,
                self.guarantee_switch,
                self.pulls_field,
                self.copies_field,
                self.calc_button,
                result_card,
            ],
        )

        # Центрируем всё на странице
        self.page.add(main_column)

    def _on_calculate(self, e):
        """Обработчик нажатия кнопки."""
        try:
            pity = int(self.pity_field.value)
            pulls = int(self.pulls_field.value)
            k = int(self.copies_field.value)
            guarantee = self.guarantee_switch.value

            if not (0 <= pity <= 89):
                self.result_text.value = "⚠️ Ошибка: pity от 0 до 89"
                self.result_text.color = COLORS["error"]
                self.result_card.visible = True
                self.page.update()
                return

            calc = ZZZGachaCalculator(current_pity=pity, guarantee=guarantee)

            if k == 0:
                # При k=0 считаем "хотя бы одну" (по умолчанию)
                prob = calc.probability_at_least_one(pulls)
                self.result_text.value = f"Шанс ≥1 копии: {prob*100:.2f}%"
            else:
                prob = calc.probability_k(pulls, k)
                self.result_text.value = f"Шанс ≥{k} копий: {prob*100:.2f}%"

            self.result_text.color = COLORS["success"]

            # Дополнительная информация
            dist = calc.get_distribution(pulls)
            if pulls <= 20:
                lines = [f"k={i}: {p*100:.2f}%" for i, p in enumerate(dist) if p > 0.0001]
                self.result_details.value = "Полное распределение:\n" + "\n".join(lines)
            else:
                at_least_1 = 1.0 - dist[0]
                at_least_2 = 1.0 - (dist[0] + dist[1]) if len(dist) > 1 else 0.0
                self.result_details.value = (
                    f"Хотя бы 1: {at_least_1*100:.2f}%\n"
                    f"Хотя бы 2: {at_least_2*100:.2f}%"
                )

            self.result_card.visible = True
            self.page.update()

        except ValueError:
            self.result_text.value = "⚠️ Введите корректные числа"
            self.result_text.color = COLORS["error"]
            self.result_card.visible = True
            self.page.update()
