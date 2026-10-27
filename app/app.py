from typing import Any

import flet as ft

from core import ZZZGachaCalculator, ZZZPullCalculator, storage

# ZZZ (Zenless Zone Zero) Cyberpunk/Neon Color Palette
COLORS: dict[str, str] = {
    "bg": "#0A0A0A",
    "bg_secondary": "#0F0F0F",
    "card_bg": "#121212",
    "primary": "#FF6B00",
    "primary_glow": "#FF8C00",
    "primary_dim": "#CC5500",
    "secondary": "#00E5FF",
    "secondary_glow": "#00FFFF",
    "secondary_dim": "#00B4D8",
    "accent": "#A855F7",
    "text": "#FFFFFF",
    "text_secondary": "#A0A0A0",
    "text_muted": "#666666",
    "success": "#22C55E",
    "error": "#EF4444",
    "warning": "#FBBF24",
    "border": "#2A2A2A",
}


class ZZZGachaApp:
    """Главное представление приложения."""

    def __init__(self, page: ft.Page) -> None:
        self.page: ft.Page = page
        self.wish_settings: dict[str, Any]
        self.pull_settings: dict[str, Any]
        self._load_settings()
        self._setup_page()
        self._build_ui()

    def _load_settings(self) -> None:
        """Загружает сохраненные настройки."""
        self.wish_settings = storage.get_wish_settings()
        self.pull_settings = storage.get_pull_settings()

    def _setup_page(self) -> None:
        """Настройка страницы: заголовок, размер, тема."""
        self.page.title = "⚡ ZZZ Wish Simulator ⚡"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.padding = 14
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLORS["bg"]
        self.page.window.width = 520
        self.page.window.height = 720
        self.page.window.min_width = 480
        self.page.window.min_height = 600

        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=COLORS["primary"],
                secondary=COLORS["secondary"],
                tertiary=COLORS["accent"],
                surface=COLORS["card_bg"],
                on_surface=COLORS["text"],
                error=COLORS["error"],
                on_error=COLORS["bg"],
                primary_container=COLORS["primary_glow"],
                secondary_container=COLORS["secondary_glow"],
            ),
            text_theme=ft.TextTheme(
                headline_large=ft.TextStyle(
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["primary"],
                    font_family="Segoe UI",
                ),
                headline_medium=ft.TextStyle(size=20, weight=ft.FontWeight.W_600, color=COLORS["text"]),
                body_large=ft.TextStyle(size=16, color=COLORS["text"]),
                body_medium=ft.TextStyle(size=14, color=COLORS["text_secondary"]),
                label_large=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD, color=COLORS["bg"]),
            ),
        )

    def _build_ui(self) -> None:
        """Сборка интерфейса."""
        self._build_wish_tab()
        self._build_pull_tab()

        self.tabs = ft.Tabs(
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.TabBar(
                        tab_alignment=ft.TabAlignment.CENTER,
                        indicator_color=COLORS["primary"],
                        indicator_thickness=2,
                        divider_color=COLORS["border"],
                        label_color=COLORS["text"],
                        unselected_label_color=COLORS["text_muted"],
                        label_padding=ft.Padding(18, 8, 18, 8),
                        tabs=[
                            ft.Tab(label="ШАНС", icon=ft.Icons.CASINO),
                            ft.Tab(label="КРУТКИ", icon=ft.Icons.CALCULATE),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._tab_page(self.wish_tab_content),
                            self._tab_page(self.pull_tab_content),
                        ],
                    ),
                ],
            ),
            length=2,
            selected_index=0,
            animation_duration=250,
            expand=True,
        )

        main_column = ft.SafeArea(
            expand=True,
            content=ft.Column(
                spacing=0,
                controls=[
                    self._build_header(),
                    ft.Container(content=self.tabs, expand=True, padding=ft.Padding(2, 0, 2, 0)),
                ],
            ),
        )

        self.page.add(main_column)

    def _build_header(self) -> ft.Control:
        """Компактная шапка с брендом и подсказкой."""
        logo = ft.Container(
            content=ft.Text("Z", size=24, weight=ft.FontWeight.BOLD, color=COLORS["bg"]),
            width=44,
            height=44,
            border_radius=13,
            alignment=ft.Alignment.CENTER,
            gradient=ft.LinearGradient(
                colors=[COLORS["primary_glow"], COLORS["primary"], COLORS["primary_dim"]],
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
            ),
            shadow=ft.BoxShadow(
                blur_radius=18,
                spread_radius=1,
                color=COLORS["primary_glow"],
                offset=ft.Offset(0, 4),
            ),
        )

        title = ft.Column(
            spacing=1,
            expand=True,
            controls=[
                ft.Text("ZZZ SIGNAL LAB", size=20, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                ft.Text(
                    "Zenless Zone Zero · калькулятор круток",
                    size=10,
                    color=COLORS["text_secondary"],
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

        badge = ft.Container(
            content=ft.Row(
                spacing=5,
                controls=[
                    ft.Container(width=6, height=6, border_radius=3, bgcolor=COLORS["success"]),
                    ft.Text("LOCAL", size=9, weight=ft.FontWeight.BOLD, color=COLORS["success"]),
                ],
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border=ft.Border.all(1, COLORS["border"]),
            border_radius=20,
            bgcolor=COLORS["bg_secondary"],
        )

        return ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[logo, title, badge],
                    ),
                    ft.Container(
                        height=2,
                        border_radius=1,
                        gradient=ft.LinearGradient(
                            colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["bg"]],
                        ),
                    ),
                ],
            ),
            padding=ft.Padding(2, 0, 2, 8),
        )

    def _tab_page(self, content: ft.Control) -> ft.Container:
        """Обёртка вкладки: прокрутка и компактные отступы."""
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[content],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.Padding(0, 10, 0, 8),
        )

    def _section_header(self, title: str, subtitle: str, icon: ft.IconData) -> ft.Control:
        """Заголовок секции с акцентной иконкой."""
        return ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Icon(icon, size=14, color=COLORS["primary"]),
                    width=28,
                    height=28,
                    border_radius=8,
                    bgcolor=COLORS["bg_secondary"],
                    alignment=ft.Alignment.CENTER,
                    border=ft.Border.all(1, COLORS["border"]),
                ),
                ft.Column(
                    spacing=1,
                    expand=True,
                    controls=[
                        ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                        ft.Text(subtitle, size=9, color=COLORS["text_muted"], max_lines=1),
                    ],
                ),
            ],
        )

    def _card(self, content: ft.Control, padding: int = 14) -> ft.Container:
        """Стандартная карточка интерфейса."""
        return ft.Container(
            content=content,
            padding=padding,
            border_radius=16,
            bgcolor=COLORS["card_bg"],
            gradient=ft.LinearGradient(
                colors=[COLORS["card_bg"], COLORS["bg_secondary"]],
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
            ),
            border=ft.Border.all(1, COLORS["border"]),
            shadow=ft.BoxShadow(blur_radius=14, color="#00000066", offset=ft.Offset(0, 4)),
        )

    def _build_wish_tab(self) -> None:
        """Сборка вкладки калькулятора шансов."""
        self.pity_field = self._create_neon_textfield(
            label="ТЕКУЩИЙ ПИТИ",
            value=str(self.wish_settings.get("pity", 30)),
            hint="0–89",
            col={"xs": 6},
        )

        self.pulls_field = self._create_neon_textfield(
            label="КРУТОК (N)",
            value=str(self.wish_settings.get("pulls", 50)),
            hint="план",
            col={"xs": 6},
        )

        self.copies_field = self._create_neon_textfield(
            label="КОПИЙ (K)",
            value=str(self.wish_settings.get("copies", 1)),
            hint="0 = хотя бы 1",
            col={"xs": 6},
        )

        self.guarantee_switch = ft.Container(
            content=ft.Switch(
                value=self.wish_settings.get("guarantee", False),
                active_color=COLORS["primary"],
                inactive_thumb_color=COLORS["text_muted"],
                inactive_track_color=COLORS["bg"],
                scale=0.9,
            ),
            padding=0,
        )
        guarantee_card = ft.Container(
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.VERIFIED_USER, size=18, color=COLORS["secondary"]),
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text("ГАРАНТ", size=10, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                            ft.Text("следующий S — ивент", size=9, color=COLORS["text_muted"]),
                        ],
                    ),
                    self.guarantee_switch,
                ],
            ),
            padding=ft.Padding(10, 6, 8, 6),
            border_radius=12,
            bgcolor=COLORS["bg_secondary"],
            border=ft.Border.all(1, COLORS["border"]),
            col={"xs": 6},
        )

        self.wish_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ ШАНС",
            on_click=self._on_wish_calculate,
            icon=ft.Icons.AUTO_GRAPH,
        )

        self.wish_result_text = ft.Text(
            "",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
            font_family="Consolas",
        )
        self.wish_result_bar = ft.ProgressBar(
            value=0,
            height=6,
            color=COLORS["success"],
            bgcolor=COLORS["border"],
            border_radius=3,
        )
        self.wish_result_details = ft.Text(
            "",
            size=12,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.CENTER,
        )
        self.wish_result_card = self._build_result_card(
            title="РЕЗУЛЬТАТ",
            icon=ft.Icons.QUERY_STATS,
            value_text=self.wish_result_text,
            details_text=self.wish_result_details,
            bar=self.wish_result_bar,
        )

        fields = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10,
            controls=[
                self.pity_field,
                self.pulls_field,
                self.copies_field,
                guarantee_card,
            ],
        )

        self.wish_tab_content = ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._section_header(
                    "ШАНС НА ИВЕНТ",
                    "канал агентов · 50/50 · hard pity 90",
                    ft.Icons.CASINO,
                ),
                self._card(ft.Column(spacing=12, controls=[fields])),
                self.wish_calc_button,
                self.wish_result_card,
                ft.Text(
                    "Soft pity — оценка сообщества: ~74-я крутка, +6 п.п. за крутку.",
                    size=9,
                    color=COLORS["text_muted"],
                    text_align=ft.TextAlign.CENTER,
                ),
                self._build_wish_stats(),
            ],
        )

    def _build_wish_stats(self) -> ft.Control:
        """Короткие ориентиры по pity под формой."""
        return ft.Container(
            content=ft.Row(
                spacing=8,
                controls=[
                    self._stat_tile("90", "HARD PITY", COLORS["primary"]),
                    self._stat_tile("180", "ГАРАНТ ИВЕНТА", COLORS["secondary"]),
                    self._stat_tile("0.6%", "БАЗА", COLORS["accent"]),
                ],
            ),
            padding=10,
            border_radius=14,
            bgcolor=COLORS["card_bg"],
            border=ft.Border.all(1, COLORS["border"]),
        )

    def _stat_tile(self, value: str, label: str, color: str) -> ft.Container:
        """Мини-плитка со значением и подписью."""
        return ft.Container(
            content=ft.Column(
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=color, font_family="Consolas"),
                    ft.Text(label, size=8, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                ],
            ),
            padding=ft.Padding(6, 8, 6, 8),
            border_radius=10,
            bgcolor=COLORS["bg_secondary"],
            border=ft.Border.all(1, COLORS["border"]),
            expand=True,
        )

    def _create_neon_textfield(
        self,
        label: str,
        value: str,
        hint: str = "",
        col: dict[str, int] | None = None,
    ) -> ft.Container:
        """Создает текстовое поле в неоновом стиле ZZZ."""
        textfield = ft.TextField(
            label=label,
            value=value,
            height=54,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border=self._input_border(COLORS["border"]),
            label_style=ft.TextStyle(
                color=COLORS["text_secondary"],
                size=9,
                weight=ft.FontWeight.W_600,
            ),
            text_style=ft.TextStyle(
                color=COLORS["text"],
                size=15,
                weight=ft.FontWeight.W_500,
                font_family="Consolas",
            ),
            hint_text=hint,
            hint_style=ft.TextStyle(color=COLORS["text_muted"], size=10),
            bgcolor=COLORS["bg_secondary"],
            content_padding=ft.Padding(14, 6, 14, 6),
            cursor_color=COLORS["primary"],
            selection_color=COLORS["primary_glow"],
        )

        return ft.Container(
            content=textfield,
            col=col,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._on_textfield_hover(e, textfield),
        )

    def _build_result_card(
        self,
        title: str,
        icon: ft.IconData,
        value_text: ft.Text,
        details_text: ft.Text,
        bar: ft.ProgressBar | None = None,
    ) -> ft.Container:
        """Карточка результата, общая для обеих вкладок."""
        controls: list[ft.Control] = [
            ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(icon, size=13, color=COLORS["secondary"]),
                    ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color=COLORS["text_secondary"]),
                ],
            ),
            value_text,
        ]
        if bar is not None:
            controls.append(bar)
        controls.append(
            ft.Container(
                content=details_text,
                padding=10,
                bgcolor=COLORS["bg"],
                border_radius=10,
                border=ft.Border.all(1, COLORS["border"]),
            )
        )
        return ft.Container(
            content=ft.Column(spacing=10, controls=controls),
            padding=16,
            border=ft.Border.all(1, COLORS["border"]),
            border_radius=16,
            bgcolor=COLORS["card_bg"],
            gradient=ft.LinearGradient(
                colors=[COLORS["card_bg"], COLORS["bg_secondary"]],
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
            ),
            visible=False,
            shadow=ft.BoxShadow(blur_radius=18, color="#00000088", offset=ft.Offset(0, 6)),
        )

    def _create_neon_button(
        self,
        text: str,
        on_click: ft.ControlEvent | None,
        icon: ft.IconData | None = None,
    ) -> ft.Container:
        """Создает кнопку в неоновом киберпанк стиле."""
        button_content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icon, size=18, color=COLORS["bg"]) if icon else ft.Container(),
                ft.Text(
                    text,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["bg"],
                ),
            ],
        )

        button = ft.Button(
            content=button_content,
            on_click=on_click,
            height=50,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                bgcolor=COLORS["primary"],
                color=COLORS["bg"],
                elevation=0,
                overlay_color=COLORS["primary_glow"],
                shadow_color=COLORS["primary_glow"],
                padding=ft.Padding(20, 0, 20, 0),
                animation_duration=180,
            ),
        )

        container = ft.Container(
            content=ft.Row(spacing=0, controls=[button]),
            border_radius=14,
            expand=True,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._on_button_hover(e, button, container),
        )

        return container

    @staticmethod
    def _input_border(color: str, width: float = 1.5) -> dict[ft.ControlState, ft.OutlineInputBorder]:
        """Рамка поля ввода: обычное и фокусированное состояние (Flet 1.0)."""
        return {
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=10,
                side=ft.BorderSide(width, color),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=10,
                side=ft.BorderSide(2, COLORS["primary"]),
            ),
        }

    def _on_textfield_hover(self, e: ft.ControlEvent, textfield: ft.TextField) -> None:
        """Эффект при наведении на текстовое поле."""
        if e.data == "true":
            textfield.border = self._input_border(COLORS["secondary_dim"])
            textfield.bgcolor = COLORS["card_bg"]
        else:
            textfield.border = self._input_border(COLORS["border"])
            textfield.bgcolor = COLORS["bg_secondary"]
        textfield.update()

    def _create_neon_button(
        self,
        text: str,
        on_click: ft.ControlEvent | None,
        icon: ft.IconData | None = None,
    ) -> ft.Container:
        """Создает кнопку в неоновом киберпанк стиле."""
        button_content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icon, size=18, color=COLORS["bg"]) if icon else ft.Container(),
                ft.Text(
                    text,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["bg"],
                ),
            ],
        )

        button = ft.Button(
            content=button_content,
            on_click=on_click,
            height=50,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                bgcolor=COLORS["primary"],
                color=COLORS["bg"],
                elevation=0,
                overlay_color=COLORS["primary_glow"],
                shadow_color=COLORS["primary_glow"],
                padding=ft.Padding(20, 0, 20, 0),
                animation_duration=180,
            ),
        )

        container = ft.Container(
            content=ft.Row(spacing=0, controls=[button]),
            border_radius=14,
            expand=True,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._on_button_hover(e, button, container),
        )

        return container

    def _on_button_hover(self, e: ft.ControlEvent, button: ft.Button, container: ft.Container) -> None:
        """Эффект наведения на неоновую кнопку."""
        if e.data == "true":
            container.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=COLORS["primary_glow"],
                offset=ft.Offset(0, 0),
            )
            container.scale = ft.Scale(1.02)
            button.style.bgcolor = COLORS["primary_glow"]
        else:
            container.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=COLORS["primary_glow"],
                offset=ft.Offset(0, 4),
            )
            container.scale = ft.Scale(1.0)
            button.style.bgcolor = COLORS["primary"]
        container.update()
        button.update()

    def _on_wish_calculate(self, e: ft.ControlEvent) -> None:
        """Обработчик расчёта шансов."""
        try:
            pity = int(self.pity_field.content.value)
            pulls = int(self.pulls_field.content.value)
            k = int(self.copies_field.content.value)
            guarantee = self.guarantee_switch.content.value

            if not (0 <= pity <= 89):
                self._show_wish_error("⚠️ ОШИБКА: ПИТИ ОТ 0 ДО 89")
                return

            storage.save_wish_settings(pity, guarantee, pulls, k)

            calc = ZZZGachaCalculator(current_pity=pity, guarantee=guarantee)

            if k == 0:
                prob = calc.probability_at_least_one(pulls)
                self.wish_result_text.value = f"ШАНС ≥1 КОПИИ: {prob * 100:.2f}%"
            else:
                prob = calc.probability_k(pulls, k)
                self.wish_result_text.value = f"ШАНС ≥{k} КОПИЙ: {prob * 100:.2f}%"

            self.wish_result_text.color = COLORS["success"]
            self.wish_result_bar.value = prob
            self.wish_result_bar.color = COLORS["success"]
            self.wish_result_card.border = ft.Border.all(1, COLORS["success"])
            self.wish_result_card.shadow = ft.BoxShadow(
                blur_radius=22,
                color="#22C55E33",
                offset=ft.Offset(0, 6),
            )

            dist = calc.get_distribution(pulls)
            if pulls <= 20:
                lines = [f"k={i}: {p * 100:.2f}%" for i, p in enumerate(dist) if p > 0.0001]
                self.wish_result_details.value = "ПОЛНОЕ РАСПРЕДЕЛЕНИЕ:\n" + "\n".join(lines)
            else:
                at_least_1 = 1.0 - dist[0]
                at_least_2 = 1.0 - (dist[0] + dist[1]) if len(dist) > 1 else 0.0
                self.wish_result_details.value = (
                    f"ХОТЯ БЫ 1: {at_least_1 * 100:.2f}%\nХОТЯ БЫ 2: {at_least_2 * 100:.2f}%"
                )

            self.wish_result_card.visible = True
            self.page.update()

        except ValueError:
            self._show_wish_error("⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА")

    def _show_wish_error(self, message: str) -> None:
        """Показывает ошибку в карточке результата."""
        self.wish_result_text.value = message
        self.wish_result_text.color = COLORS["error"]
        self.wish_result_bar.value = 0
        self.wish_result_bar.color = COLORS["error"]
        self.wish_result_details.value = "Проверьте введённые значения и попробуйте снова."
        self.wish_result_card.border = ft.Border.all(1, COLORS["error"])
        self.wish_result_card.shadow = ft.BoxShadow(
            blur_radius=22,
            color="#EF444433",
            offset=ft.Offset(0, 6),
        )
        self.wish_result_card.visible = True
        self.page.update()

    def _on_pull_calculate(self, e: ft.ControlEvent) -> None:
        """Обработчик расчёта круток."""
        try:
            current_pulls = int(self.pull_current_pulls.content.value)
            current_polychromes = int(self.pull_current_polychromes.content.value)
            current_monochromes = int(self.pull_current_monochromes.content.value)
            subscription_days = int(self.pull_subscription_days.content.value)
            days = int(self.pull_days.content.value)

            if days <= 0:
                self._show_pull_error("⚠️ ДНЕЙ ДОЛЖНО БЫТЬ БОЛЬШЕ 0")
                return

            storage.save_pull_settings(
                current_pulls,
                current_polychromes,
                current_monochromes,
                subscription_days,
                days,
            )

            calc = ZZZPullCalculator(
                current_pulls=current_pulls,
                current_polychromes=current_polychromes,
                current_monochromes=current_monochromes,
                subscription_days=subscription_days,
                days=days,
            )

            result = calc.calculate()

            self.pull_result_text.value = f"🎯 ИТОГО КРУТОК: {result.total_pulls}"
            self.pull_result_text.color = COLORS["success"]
            self.pull_result_card.border = ft.Border.all(1, COLORS["success"])
            self.pull_result_card.shadow = ft.BoxShadow(
                blur_radius=22,
                color="#22C55E33",
                offset=ft.Offset(0, 6),
            )

            breakdown = calc.get_detailed_breakdown()
            lines = [f"{k}: {v}" for k, v in breakdown.items()]
            self.pull_result_details.value = "\n".join(lines)

            self.pull_result_card.visible = True
            self.page.update()

        except ValueError:
            self._show_pull_error("⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА")

    def _show_pull_error(self, message: str) -> None:
        """Показывает ошибку в карточке прогноза."""
        self.pull_result_text.value = message
        self.pull_result_text.color = COLORS["error"]
        self.pull_result_details.value = "Проверьте введённые значения и попробуйте снова."
        self.pull_result_card.border = ft.Border.all(1, COLORS["error"])
        self.pull_result_card.shadow = ft.BoxShadow(
            blur_radius=22,
            color="#EF444433",
            offset=ft.Offset(0, 6),
        )
        self.pull_result_card.visible = True
        self.page.update()

    def _build_pull_tab(self) -> None:
        """Сборка вкладки калькулятора круток."""
        self.pull_current_pulls = self._create_neon_textfield(
            label="ТЕКУЩИЕ КРУТКИ",
            value=str(self.pull_settings.get("current_pulls", 0)),
            hint="шт.",
            col={"xs": 6},
        )

        self.pull_current_polychromes = self._create_neon_textfield(
            label="ПОЛИХРОМЫ",
            value=str(self.pull_settings.get("current_polychromes", 0)),
            hint="в инвентаре",
            col={"xs": 6},
        )

        self.pull_current_monochromes = self._create_neon_textfield(
            label="МОНОХРОМЫ",
            value=str(self.pull_settings.get("current_monochromes", 0)),
            hint="1:1 к поли",
            col={"xs": 6},
        )

        self.pull_subscription_days = self._create_neon_textfield(
            label="ДНИ ПОДПИСКИ",
            value=str(self.pull_settings.get("subscription_days", 0)),
            hint="остаток",
            col={"xs": 6},
        )

        self.pull_days = self._create_neon_textfield(
            label="ПЕРИОД, ДНЕЙ",
            value=str(self.pull_settings.get("days", 30)),
            hint="прогноз",
            col={"xs": 6},
        )

        self.pull_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ КРУТКИ",
            on_click=self._on_pull_calculate,
            icon=ft.Icons.TRENDING_UP,
        )

        self.pull_result_text = ft.Text(
            "",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
            font_family="Consolas",
        )
        self.pull_result_details = ft.Text(
            "",
            size=11,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.LEFT,
            font_family="Consolas",
        )
        self.pull_result_card = self._build_result_card(
            title="ПРОГНОЗ",
            icon=ft.Icons.TRENDING_UP,
            value_text=self.pull_result_text,
            details_text=self.pull_result_details,
        )

        fields = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10,
            controls=[
                self.pull_current_pulls,
                self.pull_current_polychromes,
                self.pull_current_monochromes,
                self.pull_subscription_days,
                self.pull_days,
            ],
        )

        self.rates_info = ft.ExpansionTile(
            title=ft.Text("КУРСЫ И ИСТОЧНИКИ", size=12, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
            subtitle=ft.Text(
                "проверенные значения · события не включены",
                size=9,
                color=COLORS["text_muted"],
            ),
            leading=ft.Icon(ft.Icons.CURRENCY_EXCHANGE, size=16, color=COLORS["accent"]),
            controls=[self._build_rates_content()],
            expanded=False,
            tile_padding=ft.Padding(12, 2, 12, 2),
            controls_padding=ft.Padding(12, 0, 12, 10),
            bgcolor=COLORS["card_bg"],
            collapsed_bgcolor=COLORS["card_bg"],
            text_color=COLORS["text"],
            collapsed_text_color=COLORS["text"],
            icon_color=COLORS["accent"],
            collapsed_icon_color=COLORS["accent"],
            shape=ft.RoundedRectangleBorder(radius=16),
            collapsed_shape=ft.RoundedRectangleBorder(radius=16),
        )

        self.pull_tab_content = ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._section_header(
                    "ПРОГНОЗ КРУТОК",
                    "daily · weekly · endgame · магазин",
                    ft.Icons.CALENDAR_MONTH,
                ),
                self._card(ft.Column(spacing=12, controls=[fields])),
                self.pull_calc_button,
                self.pull_result_card,
                self.rates_info,
            ],
        )

    def _build_rates_content(self) -> ft.Control:
        """Содержимое раскрывающейся справки по курсам и источникам."""
        return ft.Column(
            spacing=6,
            controls=[
                ft.Divider(height=1, color=COLORS["border"]),
                self._rate_row("1 КРУТКА", "160 ПОЛИХРОМОВ", COLORS["primary"]),
                self._rate_row("1 МОНОХРОМ", "1 ПОЛИХРОМ"),
                ft.Divider(height=1, color=COLORS["border"]),
                self._rate_row("ЕЖЕДНЕВКИ", "60 / ДЕНЬ"),
                self._rate_row("ПОДПИСКА", "90 / ДЕНЬ"),
                self._rate_row("RIDU WEEKLY", "60 / НЕД"),
                self._rate_row("HOLLOW ZERO", "160 / НЕД"),
                self._rate_row("SHIYU DEFENSE", "780 / 14 ДН"),
                self._rate_row("DEADLY ASSAULT", "300 / 14 ДН"),
                self._rate_row("SIGNAL SHOP", "5 КРУТОК / МЕС"),
                ft.Divider(height=1, color=COLORS["border"]),
                self._rate_row("АГЕНТ", "90 ПИТИ · 50/50", COLORS["secondary"]),
                self._rate_row("W-ENGINE", "80 ПИТИ · 75/25", COLORS["secondary"]),
                self._rate_row("SOFT PITY", "~74 · +6 П.П.", COLORS["warning"]),
                ft.Text(
                    "События, компенсации и разовые награды не учтены. "
                    "Shiyu Defense и Deadly Assault считаются по полной 14-дневной ротации.",
                    size=9,
                    color=COLORS["text_muted"],
                ),
            ],
        )

    def _rate_row(self, label: str, value: str, color: str | None = None) -> ft.Control:
        """Строка справки: название слева, значение справа."""
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(label, size=9, color=COLORS["text_secondary"]),
                ft.Text(
                    value,
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=color or COLORS["text"],
                    font_family="Consolas",
                ),
            ],
        )
