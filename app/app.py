from typing import Any

import flet as ft

from core import ZZZGachaCalculator, ZZZPullCalculator, storage

# ZZZ (Zenless Zone Zero) Cyberpunk/Neon Color Palette
COLORS: dict[str, str] = {
    "bg": "#0A0A0A",
    "bg_secondary": "#0F0F0F",
    "card_bg": "#121212",
    "card_bg_hover": "#1A1A1A",
    "primary": "#FF6B00",
    "primary_glow": "#FF8C00",
    "primary_dim": "#CC5500",
    "secondary": "#00E5FF",
    "secondary_glow": "#00FFFF",
    "secondary_dim": "#00B4D8",
    "accent": "#A855F7",
    "accent_glow": "#C084FC",
    "accent_dim": "#8B5CF6",
    "text": "#FFFFFF",
    "text_secondary": "#A0A0A0",
    "text_muted": "#666666",
    "text_on_primary": "#0A0A0A",
    "success": "#22C55E",
    "success_glow": "#4ADE80",
    "error": "#EF4444",
    "error_glow": "#F87171",
    "warning": "#FBBF24",
    "border": "#2A2A2A",
    "border_accent": "#FF6B00",
    "border_secondary": "#00E5FF",
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
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = 30
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLORS["bg"]
        self.page.window_width = 520
        self.page.window_height = 720
        self.page.window_min_width = 480
        self.page.window_min_height = 600

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
                    size=36, weight=ft.FontWeight.BOLD, color=COLORS["primary"],
                    font_family="Segoe UI",
                ),
                headline_medium=ft.TextStyle(
                    size=20, weight=ft.FontWeight.W_600, color=COLORS["text"]
                ),
                body_large=ft.TextStyle(size=16, color=COLORS["text"]),
                body_medium=ft.TextStyle(size=14, color=COLORS["text_secondary"]),
                label_large=ft.TextStyle(
                    size=16, weight=ft.FontWeight.BOLD, color=COLORS["bg"]
                ),
            ),
        )

    def _build_ui(self) -> None:
        """Сборка интерфейса."""
        self._build_wish_tab()
        self._build_pull_tab()

        # Заголовок с неоновым эффектом
        title = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "⚡ ZZZ WISH SIMULATOR ⚡",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["primary"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
                    ),
                    ft.Text(
                        "⚡ ZZZ WISH SIMULATOR ⚡",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text"],
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(
                            shadow=ft.BoxShadow(
                                spread_radius=2,
                                blur_radius=15,
                                color=COLORS["primary_glow"],
                                offset=ft.Offset(0, 0),
                            )
                        ),
                    ),
                ],
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding(0, 0, 0, 20),
        )

        # Декоративная линия под заголовком
        title_divider = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=60,
                        height=2,
                        gradient=ft.LinearGradient(
                            colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"]],
                        ),
                        border_radius=1,
                    ),
                    ft.Container(width=20),
                    ft.Icon(
                        ft.Icons.BOLT,
                        size=16,
                        color=COLORS["primary"],
                    ),
                    ft.Container(width=20),
                    ft.Container(
                        width=60,
                        height=2,
                        gradient=ft.LinearGradient(
                            colors=[COLORS["accent"], COLORS["secondary"], COLORS["primary"]],
                        ),
                        border_radius=1,
                    ),
                ],
            ),
            padding=ft.Padding(0, 0, 0, 20),
        )

        # Вкладки с неоновым стилем
        self.tabs = ft.Tabs(
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tab_alignment=ft.TabAlignment.CENTER,
                        tabs=[
                            ft.Tab(label="ШАНС ВЫПАДЕНИЯ", icon=ft.Icons.CASINO),
                            ft.Tab(label="РАСЧЁТ КРУТОК", icon=ft.Icons.CALCULATE),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column(
                                    controls=[self.wish_tab_content],
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column(
                                    controls=[self.pull_tab_content],
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True,
                                ),
                                expand=True,
                            ),
                        ],
                    ),
                ],
            ),
            length=2,
            selected_index=0,
            animation_duration=300,
            expand=True,
        )

        # Основная колонка
        main_column = ft.SafeArea(
            expand=True,
            content=ft.Column(
                spacing=0,
                controls=[
                    title,
                    title_divider,
                    ft.Container(
                        content=self.tabs,
                        expand=True,
                        padding=ft.Padding(10, 0, 10, 10),
                    ),
                ],
            ),
        )

        self.page.add(main_column)

    def _build_wish_tab(self) -> None:
        """Сборка вкладки калькулятора шансов."""
        self.pity_field = self._create_neon_textfield(
            label="ТЕКУЩИЙ ПИТИ (0-89)",
            value=str(self.wish_settings.get("pity", 30)),
            width=320,
            hint="Сколько круток после последнего легендарного",
        )

        self.guarantee_switch = ft.Container(
            content=ft.Switch(
                label="ГАРАНТ ИВЕНТОВОГО ПЕРСОНАЖА АКТИВЕН",
                value=self.wish_settings.get("guarantee", False),
                active_color=COLORS["primary"],
                inactive_thumb_color=COLORS["text_muted"],
                inactive_track_color=COLORS["card_bg"],
            ),
            padding=ft.Padding(0, 8, 0, 8),
        )

        self.pulls_field = self._create_neon_textfield(
            label="КОЛИЧЕСТВО КРУТОК (N)",
            value=str(self.wish_settings.get("pulls", 50)),
            width=320,
            hint="Сколько круток планируете сделать",
        )

        self.copies_field = self._create_neon_textfield(
            label="ЖЕЛАЕМОЕ КОЛИЧЕСТВО КОПИЙ (K)",
            value=str(self.wish_settings.get("copies", 1)),
            width=320,
            hint="Минимальное количество копий для расчёта",
        )

        self.wish_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ ШАНС",
            on_click=self._on_wish_calculate,
            width=320,
            icon=ft.Icons.CALCULATE,
        )

        self.wish_result_text = ft.Text(
            "",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=COLORS["success_glow"],
                    offset=ft.Offset(0, 0),
                )
            ),
        )
        self.wish_result_details = ft.Text(
            "",
            size=14,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.CENTER,
        )

        wish_result_card = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    self.wish_result_text,
                    ft.Container(
                        content=self.wish_result_details,
                        padding=12,
                        bgcolor=COLORS["bg"],
                        border_radius=8,
                        border=ft.Border.all(1, COLORS["border"]),
                        width=360,
                    ),
                ],
            ),
            padding=20,
            border=ft.Border.all(1, COLORS["secondary"]),
            border_radius=16,
            bgcolor=COLORS["card_bg"],
            width=400,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=COLORS["secondary_glow"],
                offset=ft.Offset(0, 4),
            ),
        )
        self.wish_result_card = wish_result_card

        subtitle = ft.Container(
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        "КАЛЬКУЛЯТОР ШАНСА ВЫПАДЕНИЯ ИВЕНТОВОГО ПЕРСОНАЖА",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=COLORS["text_secondary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Механика: 0.6% базовый • 50/50 пити • Гардиан на 90-й",
                        size=11,
                        color=COLORS["accent"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            padding=ft.Padding(0, 0, 0, 10),
        )

        divider = self._create_neon_divider()

        self.wish_tab_content = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18,
                controls=[
                    subtitle,
                    divider,
                    self.pity_field,
                    self.guarantee_switch,
                    self.pulls_field,
                    self.copies_field,
                    self.wish_calc_button,
                    wish_result_card,
                ],
            ),
            padding=ft.Padding(20, 10, 20, 20),
            alignment=ft.Alignment.CENTER,
        )

    def _create_neon_textfield(self, label: str, value: str, width: int, hint: str = "") -> ft.Container:
        """Создает текстовое поле в неоновом стиле ZZZ."""
        textfield = ft.TextField(
            label=label,
            value=value,
            width=width,
            height=56,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
            border_radius=10,
            border_width=1.5,
            focused_border_width=2,
            label_style=ft.TextStyle(
                color=COLORS["text_secondary"],
                size=11,
                weight=ft.FontWeight.W_500,
            ),
            text_style=ft.TextStyle(
                color=COLORS["text"],
                size=16,
                weight=ft.FontWeight.W_500,
            ),
            hint_text=hint,
            hint_style=ft.TextStyle(color=COLORS["text_muted"], size=13),
            bgcolor=COLORS["bg_secondary"],
            content_padding=ft.Padding(16, 8, 16, 8),
            cursor_color=COLORS["primary"],
            selection_color=COLORS["primary_glow"],
        )

        return ft.Container(
            content=textfield,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._on_textfield_hover(e, textfield),
        )

    def _on_textfield_hover(self, e: ft.ControlEvent, textfield: ft.TextField) -> None:
        """Эффект при наведении на текстовое поле."""
        if e.data == "true":
            textfield.border_color = COLORS["secondary_dim"]
            textfield.border_width = 1.5
            textfield.bgcolor = COLORS["card_bg"]
        else:
            textfield.border_color = COLORS["border"]
            textfield.border_width = 1.5
            textfield.bgcolor = COLORS["bg_secondary"]
        textfield.update()

    def _create_neon_button(self, text: str, on_click: ft.ControlEvent | None, width: int,
                            icon: ft.IconData | None = None) -> ft.Container:
        """Создает кнопку в неоновом киберпанк стиле."""
        button_content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(icon, size=20, color=COLORS["bg"]) if icon else ft.Container(),
                ft.Text(
                    text,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["bg"],
                ),
            ],
        )

        button = ft.ElevatedButton(
            content=button_content,
            on_click=on_click,
            width=width,
            height=52,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor=COLORS["primary"],
                color=COLORS["bg"],
                elevation=0,
                overlay_color=COLORS["primary_glow"],
                shadow_color=COLORS["primary_glow"],
                padding=ft.Padding(24, 0, 24, 0),
                animation_duration=200,
            ),
        )

        container = ft.Container(
            content=button,
            border_radius=12,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._on_button_hover(e, button, container),
        )

        return container

    def _on_button_hover(self, e: ft.ControlEvent, button: ft.ElevatedButton, container: ft.Container) -> None:
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

    def _create_neon_divider(self) -> ft.Container:
        """Создает неоновый декоративный разделитель."""
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        expand=True,
                        height=1,
                        gradient=ft.LinearGradient(
                            colors=[
                                COLORS["border"],
                                COLORS["primary_dim"],
                                COLORS["primary"],
                                COLORS["secondary"],
                                COLORS["accent"],
                                COLORS["secondary"],
                                COLORS["primary"],
                                COLORS["primary_dim"],
                                COLORS["border"],
                            ],
                            stops=[0, 0.2, 0.35, 0.45, 0.5, 0.55, 0.65, 0.8, 1.0],
                        ),
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.BOLT, size=12, color=COLORS["primary"]),
                        padding=ft.Padding(12, 0, 12, 0),
                    ),
                    ft.Container(
                        expand=True,
                        height=1,
                        gradient=ft.LinearGradient(
                            colors=[
                                COLORS["border"],
                                COLORS["primary_dim"],
                                COLORS["primary"],
                                COLORS["secondary"],
                                COLORS["accent"],
                                COLORS["secondary"],
                                COLORS["primary"],
                                COLORS["primary_dim"],
                                COLORS["border"],
                            ],
                            stops=[0, 0.2, 0.35, 0.45, 0.5, 0.55, 0.65, 0.8, 1.0],
                        ),
                    ),
                ],
            ),
            padding=ft.Padding(0, 8, 0, 8),
        )

    def _on_wish_calculate(self, e: ft.ControlEvent) -> None:
        """Обработчик расчёта шансов."""
        try:
            pity = int(self.pity_field.content.value)
            pulls = int(self.pulls_field.content.value)
            k = int(self.copies_field.content.value)
            guarantee = self.guarantee_switch.content.value

            if not (0 <= pity <= 89):
                self.wish_result_text.value = "⚠️ ОШИБКА: ПИТИ ОТ 0 ДО 89"
                self.wish_result_text.color = COLORS["error"]
                self.wish_result_card.visible = True
                self.page.update()
                return

            storage.save_wish_settings(pity, guarantee, pulls, k)

            calc = ZZZGachaCalculator(current_pity=pity, guarantee=guarantee)

            if k == 0:
                prob = calc.probability_at_least_one(pulls)
                self.wish_result_text.value = f"ШАНС ≥1 КОПИИ: {prob*100:.2f}%"
            else:
                prob = calc.probability_k(pulls, k)
                self.wish_result_text.value = f"ШАНС ≥{k} КОПИЙ: {prob*100:.2f}%"

            self.wish_result_text.color = COLORS["success"]

            dist = calc.get_distribution(pulls)
            if pulls <= 20:
                lines = [f"k={i}: {p*100:.2f}%" for i, p in enumerate(dist) if p > 0.0001]
                self.wish_result_details.value = "ПОЛНОЕ РАСПРЕДЕЛЕНИЕ:\n" + "\n".join(lines)
            else:
                at_least_1 = 1.0 - dist[0]
                at_least_2 = 1.0 - (dist[0] + dist[1]) if len(dist) > 1 else 0.0
                self.wish_result_details.value = (
                    f"ХОТЯ БЫ 1: {at_least_1*100:.2f}%\n"
                    f"ХОТЯ БЫ 2: {at_least_2*100:.2f}%"
                )

            self.wish_result_card.visible = True
            self.page.update()

        except ValueError:
            self.wish_result_text.value = "⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА"
            self.wish_result_text.color = COLORS["error"]
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
                self.pull_result_text.value = "⚠️ ДНЕЙ ДОЛЖНО БЫТЬ БОЛЬШЕ 0"
                self.pull_result_text.color = COLORS["error"]
                self.pull_result_card.visible = True
                self.page.update()
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

            breakdown = calc.get_detailed_breakdown()
            lines = [f"{k}: {v}" for k, v in breakdown.items()]
            self.pull_result_details.value = "\n".join(lines)

            self.pull_result_card.visible = True
            self.page.update()

        except ValueError:
            self.pull_result_text.value = "⚠️ ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА"
            self.pull_result_text.color = COLORS["error"]
            self.pull_result_card.visible = True
            self.page.update()

    def _build_pull_tab(self) -> None:
        """Сборка вкладки калькулятора круток."""
        self.pull_current_pulls = self._create_neon_textfield(
            label="ТЕКУЩИЕ КРУТКИ",
            value=str(self.pull_settings.get("current_pulls", 0)),
            width=320,
            hint="Количество готовых круток",
        )

        self.pull_current_polychromes = self._create_neon_textfield(
            label="ТЕКУЩИЕ ПОЛИХРОМЫ",
            value=str(self.pull_settings.get("current_polychromes", 0)),
            width=320,
            hint="Полихромы в инвентаре",
        )

        self.pull_current_monochromes = self._create_neon_textfield(
            label="ТЕКУЩИЕ МОНОХРОМЫ",
            value=str(self.pull_settings.get("current_monochromes", 0)),
            width=320,
            hint="Монохромы в инвентаре",
        )

        self.pull_subscription_days = self._create_neon_textfield(
            label="ОСТАТОК ДНЕЙ ПОДПИСКИ",
            value=str(self.pull_settings.get("subscription_days", 0)),
            width=320,
            hint="Дней до окончания Интервью/подписки",
        )

        self.pull_days = self._create_neon_textfield(
            label="ДНЕЙ ДЛЯ РАСЧЁТА",
            value=str(self.pull_settings.get("days", 30)),
            width=320,
            hint="Период прогноза в днях",
        )

        self.pull_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ КРУТКИ",
            on_click=self._on_pull_calculate,
            width=320,
            icon=ft.Icons.ANALYTICS,
        )

        self.pull_result_text = ft.Text(
            "",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=COLORS["success_glow"],
                    offset=ft.Offset(0, 0),
                )
            ),
        )
        self.pull_result_details = ft.Text(
            "",
            size=13,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.LEFT,
            font_family="Consolas, monospace",
        )

        pull_result_card = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    self.pull_result_text,
                    ft.Container(
                        content=self.pull_result_details,
                        padding=16,
                        bgcolor=COLORS["bg"],
                        border_radius=8,
                        border=ft.Border.all(1, COLORS["border"]),
                        width=360,
                    ),
                ],
            ),
            padding=20,
            border=ft.Border.all(1, COLORS["secondary"]),
            border_radius=16,
            bgcolor=COLORS["card_bg"],
            width=400,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=COLORS["secondary_glow"],
                offset=ft.Offset(0, 4),
            ),
        )
        self.pull_result_card = pull_result_card

        subtitle = ft.Container(
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        "ПРОГНОЗ КОЛИЧЕСТВА КРУТОК ЗА ПЕРИОД",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=COLORS["text_secondary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Учитывает: ежедневки, неделю, нулевую каверну, магазин, подписку",
                        size=11,
                        color=COLORS["accent"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            padding=ft.Padding(0, 0, 0, 10),
        )

        rates_info = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CURRENCY_EXCHANGE, size=14, color=COLORS["accent"]),
                            ft.Text(
                                "КУРСЫ ОБМЕНА",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["accent"],
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=COLORS["border"]),
                    ft.Text("1 КРУТКА = 160 ПОЛИХРОМОВ", size=11, color=COLORS["text_secondary"]),
                    ft.Text("1 МОНОХРОМ = 1 ПОЛИХРОМ", size=11, color=COLORS["text_secondary"]),
                    ft.Divider(height=1, color=COLORS["border"]),
                    ft.Text("ЕЖЕДНЕВКИ: 60 ПОЛИХРОМ/ДЕНЬ", size=11, color=COLORS["text_secondary"]),
                    ft.Text("ПОДПИСКА: 90 ПОЛИХРОМ/ДЕНЬ", size=11, color=COLORS["text_secondary"]),
                    ft.Divider(height=1, color=COLORS["border"]),
                    ft.Text("НЕДЕЛЬНИКИ: 420 ПОЛИХРОМ", size=11, color=COLORS["text_secondary"]),
                    ft.Text("НУЛЕВАЯ КАВЕРНА: 160 ПОЛИХРОМ", size=11, color=COLORS["text_secondary"]),
                    ft.Divider(height=1, color=COLORS["border"]),
                    ft.Text("МАГАЗИН 1 ЧИСЛА: 5 КРУТОК/МЕС", size=11, color=COLORS["text_secondary"]),
                ],
            ),
            padding=ft.Padding(16, 12, 16, 12),
            border_radius=12,
            border=ft.Border.all(1, COLORS["border"]),
            bgcolor=COLORS["card_bg"],
            width=400,
        )

        divider = self._create_neon_divider()

        self.pull_tab_content = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    subtitle,
                    rates_info,
                    divider,
                    ft.Container(
                        content=ft.Text(
                            "ТЕКУЩИЕ РЕСУРСЫ",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_secondary"],
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),
                    self.pull_current_pulls,
                    self.pull_current_polychromes,
                    self.pull_current_monochromes,
                    self.pull_subscription_days,
                    divider,
                    ft.Container(
                        content=ft.Text(
                            "ПЕРИОД РАСЧЁТА",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_secondary"],
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),
                    self.pull_days,
                    self.pull_calc_button,
                    pull_result_card,
                ],
            ),
            padding=ft.Padding(20, 10, 20, 20),
            alignment=ft.Alignment.CENTER,
        )