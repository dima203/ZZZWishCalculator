import asyncio
from datetime import date
from typing import Any

import flet as ft

from core import BANNERS, ZZZGachaCalculator, ZZZPullCalculator, events, storage
from core.events import EventIncome
from core.mixed_calculator import calculate_mixed

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
        if self.banner not in BANNERS:
            self.banner = "agent"
        self._setup_page()
        self._build_ui()

    def _load_settings(self) -> None:
        """Загружает сохраненные настройки."""
        self.wish_settings = storage.get_wish_settings()
        self.pull_settings = storage.get_pull_settings()
        self.banner: str = self.wish_settings.get("banner", "agent")

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
        self._build_mix_tab()

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
                            ft.Tab(label="МИКС", icon=ft.Icons.AUTO_AWESOME),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._tab_page(self.wish_tab_content),
                            self._tab_page(self.pull_tab_content),
                            self._tab_page(self.mix_tab_content),
                        ],
                    ),
                ],
            ),
            length=3,
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

    def _section_header(self, title: str, subtitle: str | ft.Control, icon: ft.IconData) -> ft.Control:
        """Заголовок секции с акцентной иконкой."""
        subtitle_control = (
            ft.Text(subtitle, size=9, color=COLORS["text_muted"], max_lines=1)
            if isinstance(subtitle, str)
            else subtitle
        )
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
                        subtitle_control,
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
        spec = BANNERS[self.banner]
        self.pity_field = self._create_neon_textfield(
            label="КРУТОК БЕЗ S-РАНГА",
            value=str(self.wish_settings.get("pity", 30)),
            hint=f"0–{spec.hard_pity - 1}",
            col={"xs": 6},
        )

        self.pulls_field = self._create_neon_textfield(
            label="КРУТОК (N)",
            value=str(self.wish_settings.get("pulls", 50)),
            hint="план",
            col={"xs": 6},
        )

        max_copies = 7 if self.banner == "agent" else 5
        copies_value = max(1, min(int(self.wish_settings.get("copies", 1)), max_copies))
        self.copies_field, self.copies_slider, self.copies_caption = self._create_target_slider(
            label="КОПИЙ",
            minimum=1,
            maximum=max_copies,
            value=copies_value,
            on_change=self._on_copies_change,
            col={"xs": 12},
        )
        self._update_copies_caption()

        self.banner_select = ft.SegmentedButton(
            segments=[
                ft.Segment(value="agent", label=ft.Text("АГЕНТ · 90")),
                ft.Segment(value="w_engine", label=ft.Text("W-ENGINE · 80")),
            ],
            selected=[self.banner],
            allow_multiple_selection=False,
            show_selected_icon=False,
            on_change=self._on_banner_change,
            style=ft.ButtonStyle(
                color=COLORS["text_secondary"],
                bgcolor=COLORS["bg_secondary"],
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            expand=True,
        )

        self.guarantee_hint = ft.Text(
            "следующий S — ивент" if self.banner == "agent" else "следующий S — оружие",
            size=9,
            color=COLORS["text_muted"],
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
                            self.guarantee_hint,
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
        self.wish_button = self.wish_calc_button.content.controls[0]
        self.wish_progress = ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False,
            controls=[
                ft.ProgressRing(width=14, height=14, stroke_width=2, color=COLORS["primary"]),
                ft.Text("СЧИТАЕМ...", size=9, color=COLORS["text_secondary"]),
            ],
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

        self.wish_section_subtitle = ft.Text(
            self._banner_subtitle(),
            size=9,
            color=COLORS["text_muted"],
            max_lines=1,
        )

        self.wish_tab_content = ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._section_header(
                    "ШАНС НА ИВЕНТ",
                    self.wish_section_subtitle,
                    ft.Icons.CASINO,
                ),
                self._card(
                    ft.Column(
                        spacing=12,
                        controls=[
                            self.banner_select,
                            fields,
                        ],
                    )
                ),
                self.wish_calc_button,
                self.wish_progress,
                self.wish_result_card,
                ft.Text(
                    "Soft pity — оценка сообщества: агент ~74-я, W-Engine ~65-я; +6 п.п. за крутку.",
                    size=9,
                    color=COLORS["text_muted"],
                    text_align=ft.TextAlign.CENTER,
                ),
                self._build_wish_stats(),
            ],
        )

    def _build_wish_stats(self) -> ft.Control:
        """Короткие ориентиры по pity под формой."""
        spec = BANNERS[self.banner]
        self.wish_stat_hard = ft.Text(
            str(spec.hard_pity),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["primary"],
            font_family="Consolas",
        )
        self.wish_stat_guarantee = ft.Text(
            str(spec.hard_pity * 2),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["secondary"],
            font_family="Consolas",
        )
        return ft.Container(
            content=ft.Row(
                spacing=8,
                controls=[
                    self._stat_tile(self.wish_stat_hard, "HARD PITY"),
                    self._stat_tile(self.wish_stat_guarantee, "ГАРАНТ ИВЕНТА"),
                    self._stat_tile(
                        ft.Text(
                            "0.6%", size=16, weight=ft.FontWeight.BOLD, color=COLORS["accent"], font_family="Consolas"
                        ),
                        "БАЗА",
                    ),
                ],
            ),
            padding=10,
            border_radius=14,
            bgcolor=COLORS["card_bg"],
            border=ft.Border.all(1, COLORS["border"]),
        )

    def _stat_tile(self, value: ft.Text, label: str) -> ft.Container:
        """Мини-плитка со значением и подписью."""
        return ft.Container(
            content=ft.Column(
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    value,
                    ft.Text(label, size=8, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                ],
            ),
            padding=ft.Padding(6, 8, 6, 8),
            border_radius=10,
            bgcolor=COLORS["bg_secondary"],
            border=ft.Border.all(1, COLORS["border"]),
            expand=True,
        )

    def _banner_subtitle(self) -> str:
        """Подпись выбранного канала."""
        spec = BANNERS[self.banner]
        rate = "50/50" if self.banner == "agent" else "75/25"
        return f"канал {spec.label.upper()} · {rate} · hard pity {spec.hard_pity}"

    def _on_copies_change(self, e: ft.ControlEvent | None) -> None:
        """Обновляет подпись слайдера копий."""
        self._update_copies_caption()
        self.wish_result_card.visible = False
        self.page.update()

    def _update_copies_caption(self) -> None:
        value = int(self.copies_slider.value or 1)
        if self.banner == "agent":
            self.copies_caption.value = f"M{value - 1} · {value} {self._copies_word(value)}"
        else:
            self.copies_caption.value = f"R{value} · {value} {self._copies_word(value)}"

    @staticmethod
    def _copies_word(value: int) -> str:
        """Русская форма слова «копия» для подписи."""
        if value % 10 == 1 and value % 100 != 11:
            return "копия"
        if 2 <= value % 10 <= 4 and not 12 <= value % 100 <= 14:
            return "копии"
        return "копий"

    def _on_banner_change(self, e: ft.ControlEvent | None) -> None:
        """Переключает канал агента/W-Engine и обновляет подсказки."""
        selected = self.banner_select.selected
        if selected:
            self.banner = selected[0]
        if self.banner not in BANNERS:
            self.banner = "agent"
        spec = BANNERS[self.banner]

        maximum = 7 if self.banner == "agent" else 5
        self.copies_slider.max = maximum
        self.copies_slider.divisions = maximum - 1
        self.copies_slider.value = max(1, min(int(self.copies_slider.value or 1), maximum))
        self._update_copies_caption()

        self.wish_section_subtitle.value = self._banner_subtitle()
        self.guarantee_hint.value = "следующий S — ивент" if self.banner == "agent" else "следующий S — оружие"
        self.pity_field.content.label = "КРУТОК БЕЗ S-РАНГА"
        self.pity_field.content.hint_text = f"0–{spec.hard_pity - 1}"
        self.wish_stat_hard.value = str(spec.hard_pity)
        self.wish_stat_guarantee.value = str(spec.hard_pity * 2)
        self.wish_result_card.visible = False
        self.page.update()

    def _create_target_slider(
        self,
        label: str,
        minimum: int,
        maximum: int,
        value: int,
        on_change: ft.ControlEvent | None = None,
        col: dict[str, int] | None = None,
    ) -> tuple[ft.Container, ft.Slider, ft.Text]:
        """Слайдер цели с подписью текущего M/R и количества копий."""
        caption = ft.Text("", size=9, color=COLORS["text_muted"])
        slider = ft.Slider(
            min=minimum,
            max=maximum,
            divisions=maximum - minimum,
            value=value,
            label="{value}",
            active_color=COLORS["primary"],
            inactive_color=COLORS["border"],
            thumb_color=COLORS["primary_glow"],
            on_change=on_change,
        )
        container = ft.Container(
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, size=9, weight=ft.FontWeight.W_600, color=COLORS["text_secondary"]),
                            caption,
                        ],
                    ),
                    slider,
                ],
            ),
            col=col,
        )
        return container, slider, caption

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
        hint: ft.Text | None = None,
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
        if hint is not None:
            controls.append(hint)
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

    async def _on_wish_calculate(self, e: ft.ControlEvent | None) -> None:
        """Обработчик расчёта шансов с индикатором прогресса."""
        self._set_busy(self.wish_button, self.wish_progress, True)
        self.page.update()
        await asyncio.sleep(0.15)
        try:
            self._calculate_wish()
        finally:
            self._set_busy(self.wish_button, self.wish_progress, False)
            self.page.update()

    def _calculate_wish(self) -> None:
        """Считает шанс и обновляет карточку результата."""
        try:
            pity = int(self.pity_field.content.value)
            pulls = int(self.pulls_field.content.value)
            k = int(self.copies_slider.value)
            guarantee = self.guarantee_switch.content.value
            spec = BANNERS[self.banner]

            if not (0 <= pity < spec.hard_pity):
                self._show_wish_error(f"⚠️ ОШИБКА: ПИТИ ОТ 0 ДО {spec.hard_pity - 1}")
                return

            storage.save_wish_settings(pity, guarantee, pulls, k, self.banner)

            calc = ZZZGachaCalculator(current_pity=pity, guarantee=guarantee, banner=self.banner)

            unit = "КОПИЙ" if self.banner == "agent" else "W-ENGINE"
            prob = calc.probability_k(pulls, k)
            self.wish_result_text.value = f"ШАНС ≥{k} {unit}: {prob * 100:.2f}%"

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

    @staticmethod
    def _set_busy(button: ft.Button, progress: ft.Control, busy: bool) -> None:
        """Блокирует кнопку и показывает/скрывает индикатор."""
        button.disabled = busy
        progress.visible = busy

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

    async def _on_pull_calculate(self, e: ft.ControlEvent | None) -> None:
        """Обработчик расчёта круток с индикатором прогресса."""
        self._set_busy(self.pull_button, self.pull_progress, True)
        self.page.update()
        await asyncio.sleep(0.15)
        try:
            event_income = await self._get_event_income()
            self._calculate_pull(event_income)
        finally:
            self._set_busy(self.pull_button, self.pull_progress, False)
            self.page.update()

    async def _get_event_income(self) -> EventIncome:
        """Загружает оценку ивентов из кэша/сети, не ломая расчёт при сбое."""
        if not self.include_events:
            return EventIncome.empty()
        try:
            days = int(self.pull_days.content.value)
        except ValueError:
            return EventIncome.empty()
        try:
            income = await asyncio.to_thread(events.get_event_income, date.today(), days)
        except events.EventsError:
            self._events_error = True
            return EventIncome.empty()
        self._events_error = False
        return income

    def _on_events_toggle(self, e: ft.ControlEvent | None) -> None:
        """Включает/выключает учёт ивентов."""
        self.include_events = bool(self.events_switch.value)
        self.events_status.value = "Ивенты: загрузятся при расчёте" if self.include_events else "Ивенты: отключены"
        self.page.update()

    def _calculate_pull(self, event_income: EventIncome | None = None) -> None:
        """Считает прогноз и обновляет карточку результата."""
        event_income = event_income or EventIncome.empty()
        event_min = event_income.min_pulls
        event_max = event_income.max_pulls
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
            total_min = result.total_pulls_min + event_min
            total_max = result.total_pulls_max + event_max

            if total_min == total_max:
                total_text = str(total_max)
                self.pull_result_hint.value = "фиксированный доход за выбранный период"
            else:
                total_text = f"{total_min}–{total_max}"
                suffix = "эндгейм + ивенты" if self.include_events else "эндгейм"
                self.pull_result_hint.value = f"{total_min} — минимум · {total_max} — максимум ({suffix})"
            self.pull_result_text.value = f"🎯 ИТОГО КРУТОК: {total_text}"
            self.pull_result_text.color = COLORS["success"]
            self.pull_result_card.border = ft.Border.all(1, COLORS["success"])
            self.pull_result_card.shadow = ft.BoxShadow(
                blur_radius=22,
                color="#22C55E33",
                offset=ft.Offset(0, 6),
            )

            if not self.include_events:
                self.events_status.value = "Ивенты: отключены"
            elif self._events_error:
                self.events_status.value = "Ивенты: нет данных (офлайн или ошибка сети)"
            elif event_income.polychromes_max or event_income.tapes:
                count = f" · {len(event_income.events)} событий" if event_income.events else ""
                self.events_status.value = f"Ивенты (по анонсам): +{event_min}–{event_max} круток{count}"
            else:
                self.events_status.value = "Ивенты: активных анонсов не найдено"

            breakdown = calc.get_detailed_breakdown()
            lines = [
                f"Ивенты (мин.): {event_min}",
                f"Ивенты (макс.): {event_max}",
                f"Ивенты, Polychrome: {event_income.polychromes_min}–{event_income.polychromes_max}",
                f"Ивенты, талоны: {event_income.tapes}",
                *(f"{k}: {v}" for k, v in breakdown.items()),
            ]
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

        self.include_events = True
        self._events_error = False
        self.events_switch = ft.Switch(
            value=True,
            active_color=COLORS["primary"],
            inactive_thumb_color=COLORS["text_muted"],
            inactive_track_color=COLORS["bg"],
            scale=0.9,
            on_change=self._on_events_toggle,
        )
        events_row = ft.Container(
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.EVENT, size=18, color=COLORS["secondary"]),
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text("УЧИТЫВАТЬ ИВЕНТЫ", size=10, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                            ft.Text("авто-оценка из официальных постов", size=9, color=COLORS["text_muted"]),
                        ],
                    ),
                    self.events_switch,
                ],
            ),
            padding=ft.Padding(10, 6, 8, 6),
            border_radius=12,
            bgcolor=COLORS["bg_secondary"],
            border=ft.Border.all(1, COLORS["border"]),
        )

        self.pull_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ КРУТКИ",
            on_click=self._on_pull_calculate,
            icon=ft.Icons.TRENDING_UP,
        )
        self.pull_button = self.pull_calc_button.content.controls[0]
        self.pull_progress = ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False,
            controls=[
                ft.ProgressRing(width=14, height=14, stroke_width=2, color=COLORS["primary"]),
                ft.Text("СЧИТАЕМ...", size=9, color=COLORS["text_secondary"]),
            ],
        )
        self.events_status = ft.Text(
            "Ивенты: загрузятся при расчёте",
            size=9,
            color=COLORS["text_muted"],
            text_align=ft.TextAlign.CENTER,
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
        self.pull_result_hint = ft.Text("", size=10, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER)
        self.pull_result_card = self._build_result_card(
            title="ПРОГНОЗ",
            icon=ft.Icons.TRENDING_UP,
            value_text=self.pull_result_text,
            details_text=self.pull_result_details,
            hint=self.pull_result_hint,
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
                "проверенные значения · ивенты — авто-оценка",
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
                self._card(ft.Column(spacing=12, controls=[fields, events_row])),
                self.pull_calc_button,
                self.pull_progress,
                self.events_status,
                self.pull_result_card,
                self.rates_info,
            ],
        )

    def _build_mix_tab(self) -> None:
        """Сборка вкладки смешанной цели: агент + W-Engine."""
        self.mix_total_field = self._create_neon_textfield(
            label="ВСЕГО КРУТОК",
            value="180",
            hint="общий бюджет",
            col={"xs": 12},
        )
        self.mix_agent_pity = self._create_neon_textfield(
            label="ПИТИ АГЕНТА",
            value="0",
            hint="0–89",
            col={"xs": 6},
        )
        self.mix_engine_pity = self._create_neon_textfield(
            label="ПИТИ W-ENGINE",
            value="0",
            hint="0–79",
            col={"xs": 6},
        )

        self.mix_agent_guarantee = ft.Container(
            content=ft.Switch(
                value=False,
                active_color=COLORS["primary"],
                inactive_thumb_color=COLORS["text_muted"],
                inactive_track_color=COLORS["bg"],
                scale=0.9,
            ),
            padding=0,
        )
        self.mix_engine_guarantee = ft.Container(
            content=ft.Switch(
                value=False,
                active_color=COLORS["primary"],
                inactive_thumb_color=COLORS["text_muted"],
                inactive_track_color=COLORS["bg"],
                scale=0.9,
            ),
            padding=0,
        )
        agent_guarantee_card = self._guarantee_card("ГАРАНТ АГЕНТА", "следующий S — ивент", self.mix_agent_guarantee)
        engine_guarantee_card = self._guarantee_card(
            "ГАРАНТ W-ENGINE", "следующий S — оружие", self.mix_engine_guarantee
        )

        self.mix_agent_field, self.mix_agent_slider, self.mix_agent_caption = self._create_target_slider(
            label="КОПИЙ АГЕНТА",
            minimum=1,
            maximum=7,
            value=2,
            on_change=self._on_mix_agent_slider,
            col={"xs": 6},
        )
        self.mix_engine_field, self.mix_engine_slider, self.mix_engine_caption = self._create_target_slider(
            label="КОПИЙ W-ENGINE",
            minimum=1,
            maximum=5,
            value=1,
            on_change=self._on_mix_engine_slider,
            col={"xs": 6},
        )
        self._update_mix_captions()

        self.mix_calc_button = self._create_neon_button(
            text="РАССЧИТАТЬ МИКС",
            on_click=self._on_mix_calculate,
            icon=ft.Icons.AUTO_AWESOME,
        )
        self.mix_button = self.mix_calc_button.content.controls[0]
        self.mix_progress = ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False,
            controls=[
                ft.ProgressRing(width=14, height=14, stroke_width=2, color=COLORS["primary"]),
                ft.Text("СЧИТАЕМ...", size=9, color=COLORS["text_secondary"]),
            ],
        )

        self.mix_result_text = ft.Text(
            "",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=COLORS["success"],
            text_align=ft.TextAlign.CENTER,
            font_family="Consolas",
        )
        self.mix_result_bar = ft.ProgressBar(
            value=0,
            height=6,
            color=COLORS["success"],
            bgcolor=COLORS["border"],
            border_radius=3,
        )
        self.mix_result_details = ft.Text(
            "",
            size=11,
            color=COLORS["text_secondary"],
            selectable=True,
            text_align=ft.TextAlign.LEFT,
            font_family="Consolas",
        )
        self.mix_result_hint = ft.Text(
            "лучший фиксированный сплит · баннеры независимы",
            size=9,
            color=COLORS["text_muted"],
            text_align=ft.TextAlign.CENTER,
        )
        self.mix_result_card = self._build_result_card(
            title="СМЕШАННАЯ ЦЕЛЬ",
            icon=ft.Icons.AUTO_AWESOME,
            value_text=self.mix_result_text,
            details_text=self.mix_result_details,
            bar=self.mix_result_bar,
            hint=self.mix_result_hint,
        )

        fields = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10,
            controls=[
                self.mix_total_field,
                self.mix_agent_pity,
                self.mix_engine_pity,
                agent_guarantee_card,
                engine_guarantee_card,
                self.mix_agent_field,
                self.mix_engine_field,
            ],
        )

        self.mix_tab_content = ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._section_header(
                    "АГЕНТ + W-ENGINE",
                    "общий бюджет · независимые баннеры · лучший сплит",
                    ft.Icons.AUTO_AWESOME,
                ),
                self._card(ft.Column(spacing=12, controls=[fields])),
                self.mix_calc_button,
                self.mix_progress,
                self.mix_result_card,
                ft.Text(
                    "Слайдер копий: агент до M6 (7 копий), W-Engine до R5 (5 копий).",
                    size=9,
                    color=COLORS["text_muted"],
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )

    def _guarantee_card(self, title: str, hint: str, switch: ft.Control) -> ft.Container:
        """Карточка гаранта для смешанной вкладки."""
        return ft.Container(
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.VERIFIED_USER, size=18, color=COLORS["secondary"]),
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                            ft.Text(hint, size=9, color=COLORS["text_muted"]),
                        ],
                    ),
                    switch,
                ],
            ),
            padding=ft.Padding(10, 6, 8, 6),
            border_radius=12,
            bgcolor=COLORS["bg_secondary"],
            border=ft.Border.all(1, COLORS["border"]),
            col={"xs": 6},
        )

    def _on_mix_agent_slider(self, e: ft.ControlEvent | None) -> None:
        self._update_mix_captions()
        self.mix_result_card.visible = False
        self.page.update()

    def _on_mix_engine_slider(self, e: ft.ControlEvent | None) -> None:
        self._update_mix_captions()
        self.mix_result_card.visible = False
        self.page.update()

    def _update_mix_captions(self) -> None:
        agent_copies = int(self.mix_agent_slider.value or 1)
        engine_copies = int(self.mix_engine_slider.value or 1)
        self.mix_agent_caption.value = f"M{agent_copies - 1} · {agent_copies} {self._copies_word(agent_copies)}"
        self.mix_engine_caption.value = f"R{engine_copies} · {engine_copies} {self._copies_word(engine_copies)}"

    async def _on_mix_calculate(self, e: ft.ControlEvent | None) -> None:
        """Считает вероятность обеих целей при общем бюджете."""
        self._set_busy(self.mix_button, self.mix_progress, True)
        self.page.update()
        await asyncio.sleep(0.15)
        try:
            self._calculate_mix()
        finally:
            self._set_busy(self.mix_button, self.mix_progress, False)
            self.page.update()

    def _calculate_mix(self) -> None:
        try:
            total_pulls = int(self.mix_total_field.content.value)
            agent_pity = int(self.mix_agent_pity.content.value)
            engine_pity = int(self.mix_engine_pity.content.value)
            agent_copies = int(self.mix_agent_slider.value)
            engine_copies = int(self.mix_engine_slider.value)
            if total_pulls <= 0:
                self._show_mix_error("⚠️ КРУТОК ДОЛЖНО БЫТЬ БОЛЬШЕ 0")
                return
            if not (0 <= agent_pity <= 89):
                self._show_mix_error("⚠️ ПИТИ АГЕНТА ОТ 0 ДО 89")
                return
            if not (0 <= engine_pity <= 79):
                self._show_mix_error("⚠️ ПИТИ W-ENGINE ОТ 0 ДО 79")
                return

            result = calculate_mixed(
                total_pulls=total_pulls,
                agent_copies=agent_copies,
                engine_copies=engine_copies,
                agent_pity=agent_pity,
                agent_guarantee=self.mix_agent_guarantee.content.value,
                engine_pity=engine_pity,
                engine_guarantee=self.mix_engine_guarantee.content.value,
            )
            self.mix_result_text.value = f"ШАНС НА ОБА: {result.both_probability * 100:.2f}%"
            self.mix_result_text.color = COLORS["success"]
            self.mix_result_bar.value = result.both_probability
            self.mix_result_bar.color = COLORS["success"]
            self.mix_result_details.value = (
                f"Агент: {result.agent_probability * 100:.2f}% · {result.agent_pulls} круток · "
                f"{result.agent_copies} коп.\n"
                f"W-Engine: {result.engine_probability * 100:.2f}% · {result.engine_pulls} круток · "
                f"{result.engine_copies} коп.\n"
                f"Сплит: {result.agent_pulls} / {result.engine_pulls}"
            )
            self.mix_result_card.border = ft.Border.all(1, COLORS["success"])
            self.mix_result_card.shadow = ft.BoxShadow(
                blur_radius=22,
                color="#22C55E33",
                offset=ft.Offset(0, 6),
            )
            self.mix_result_card.visible = True
            self.page.update()
        except ValueError:
            self._show_mix_error("⚠️ ПРОВЕРЬТЕ ЗНАЧЕНИЯ")

    def _show_mix_error(self, message: str) -> None:
        self.mix_result_text.value = message
        self.mix_result_text.color = COLORS["error"]
        self.mix_result_bar.value = 0
        self.mix_result_bar.color = COLORS["error"]
        self.mix_result_details.value = "Проверьте введённые значения."
        self.mix_result_card.border = ft.Border.all(1, COLORS["error"])
        self.mix_result_card.shadow = ft.BoxShadow(
            blur_radius=22,
            color="#EF444433",
            offset=ft.Offset(0, 6),
        )
        self.mix_result_card.visible = True
        self.page.update()

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
                    "Ивенты считаются отдельной авто-оценкой: подтверждённые суммы + запас для неизвестных. "
                    "Shiyu Defense и Deadly Assault дают диапазон: без эндгейма — полный клир.",
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
