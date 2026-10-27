# AGENTS.md — ZZZWishCalculator

## Development Model — Trunk-based

`master` — единственная долгоживущая ветка и всегда зелёный релизный ствол. Работа идёт короткими
ветками (обычно < 1–2 дней), которые вливаются в `master` только через pull request.

- Ветки: `feat/<slug>`, `fix/<slug>`, `chore/<slug>` (например `feat/pity-table`, `fix/zero-days`).
- Прямых коммитов в `master` нет. Исключение — аварийный hotfix, который сразу закрывается PR/ревертом.
- Перед PR ветка ребейзится на свежий `master`; `master` в feature-ветку не мержится.
- PR — одна логическая задача. Слияние — **squash merge**, после merge ветка удаляется.
- Агент (OpenCode) — владелец приёмки PR: проверяет scope и дифф, гоняет гейты, разрешает конфликты
  ребейзом, принимает решение ACCEPT/REJECT и выполняет squash merge. Человек может вмешаться в любой момент.
- Merge разрешён только при зелёном CI и выполненных локальных гейтах (pytest + ruff + скриншоты для UI).

## Architecture

Однопользовательское десктопное приложение на Flet: два независимых калькулятора для Zenless Zone Zero —
вероятность выпадения ивентового персонажа (гача) и прогноз количества круток за период. Сети и БД нет:
вся логика локальная, настройки — JSON в домашней директории.

```text
ZZZWishCalculator/
├── main.py                      # точка входа: ft.run(main) → ZZZGachaApp(page)
├── app/
│   └── app.py                   # весь UI: ZZZGachaApp, палитра COLORS, вкладки, обработчики, hover
├── core/
│   ├── wish_calculator.py       # ZZZGachaCalculator — DP по состояниям (pity, guarantee)
│   ├── pull_calculator.py       # ZZZPullCalculator + Currency / PullCalculationResult
│   ├── storage.py               # JSON-настройки в ~/.zzz_wish_calculator/settings.json
│   └── __init__.py              # реэкспорт публичного API core (+ __all__)
├── tests/
│   ├── test_calculators.py      # 46 тестов: гача, экономика, edge cases
│   ├── test_storage.py          # 13 тестов: JSON-хранилище, миграция дефолтов, ошибки
│   ├── test_app.py              # 10 тестов Flet-слоя на MagicMock page (без окна)
│   ├── test_screenshot_tool.py  # 5 тестов чистых helper'ов скриншот-инструмента
│   └── test_environment.py      # 2 теста версий flet/ruff (гейт миграции)
├── tools/
│   └── screenshots.py           # boot приложения, обход вкладок, PNG в tools/screenshots/
├── docs/
│   └── events-research.md       # отчёт по источникам ивентов/дохода (не интегрирован)
├── .github/workflows/ci.yml     # ruff + pytest на push в master и на PR
├── requirements.txt             # flet==1.0.5, flet-desktop==1.0.5
├── requirements-dev.txt         # pytest==9.1.1, ruff==0.17.3
├── ruff.toml                    # единая конфигурация линтера/форматтера
├── opencode.json                # локальный MCP context7 (в .gitignore)
└── .venv/                       # Python 3.12.6
```

Слои: `core/` не импортирует Flet и полностью тестируется; `app/` — только Flet-слой (бизнес-логики нет);
`main.py` — тонкая точка входа. Новую математику добавлять в `core/`, виджеты — в `app/app.py`.

## Design Documents

| Документ | Расположение | Назначение |
|----------|--------------|------------|
| Правила агента | `AGENTS.md` | этот файл |
| Механика гачи | `core/wish_calculator.py` (docstring класса) | base/soft/hard pity, 50/50, гарант |
| Экономика круток | `core/pull_calculator.py` (docstring + константы) | источники дохода, конвертация |
| Схема настроек | `core/storage.py` (`DEFAULT_SETTINGS`) | ключи и дефолты JSON |
| Палитра и стили | `app/app.py` (`COLORS`) | цвета, тема, размеры окна |
| Источники ивентов | `docs/events-research.md` | HoYoLAB/HYP API, надёжность, ограничения |
| CI-гейт | `.github/workflows/ci.yml` | ruff + pytest |

Отдельного README нет; исследование источников ивентов — `docs/events-research.md`, источник правды
по формулам — код и тесты.

## Commands

Из корня проекта, без активации venv:

```bash
# Окружение (один раз)
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt -r requirements-dev.txt

# Приложение
.\.venv\Scripts\python.exe main.py

# Тесты (76)
.\.venv\Scripts\python.exe -m pytest -q -p no:warnings
.\.venv\Scripts\python.exe -m pytest tests/test_app.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_calculators.py::TestZZZGachaCalculator -q
.\.venv\Scripts\python.exe -m pytest -q -k "monthly"

# Линтер и форматтер
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\ruff.exe format .          # автоисправление форматирования

# UI-приёмка: PNG по вкладкам в tools/screenshots/
.\.venv\Scripts\python.exe tools\screenshots.py
.\.venv\Scripts\python.exe tools\screenshots.py wish pulls
```

- Версии зафиксированы: Python 3.12.6, `flet==1.0.5` (`flet-desktop==1.0.5`), `pytest==9.1.1`, `ruff==0.17.3`.
- Пользовательские настройки: `~/.zzz_wish_calculator/settings.json`. Удалить файл — сбросить к дефолтам.
- `tools/screenshots/` и `.ruff_cache/` в `.gitignore`; PNG не коммитятся.
- Первый запуск Flet 1.0.5 может скачать desktop-runtime («Preparing Flet ... for the first use»).

## Client Stack

| Слой | Технология | Заметки |
|------|------------|---------|
| UI | Flet 1.0.5 (desktop) | дарк-тема, неоновая палитра, кастомный `Theme` |
| Домен | чистый Python 3.12 | dataclass, `Final`, без внешних зависимостей |
| Хранение | JSON | `~/.zzz_wish_calculator/settings.json`, UTF-8, indent 2 |
| Тесты | pytest 9.1.1 | `unittest.mock` + `tempfile`, без сети и окна |
| Линт | ruff 0.17.3 | `ruff.toml`, line-length 120, double quotes, preview |
| Сеть | отсутствует | всё считается и хранится локально |

Окно: 520×720, минимум 480×600. UI-тексты — русские, КАПСОМ. Вкладки: «ШАНС ВЫПАДЕНИЯ» и «РАСЧЁТ КРУТОК».

## Key Quirks

### Flet 1.0.5

- `main.py` использует `ft.run(main)`; `ft.app(...)` не применять.
- Кнопки — `ft.Button` (не `ElevatedButton`; он deprecated с 0.80 и удалён в 1.0).
- Геометрия — `ft.Padding` / `ft.Alignment` / `ft.Margin`; legacy-модули `ft.padding` / `ft.alignment` не использовать.
- Окно — только через `page.window`: `width`, `height`, `min_width`, `min_height`; `page.window_width` и т.п. удалены.
- Границы `TextField` — через `border=`, а не loose-свойства `border_color` / `border_radius` / `border_width`
  (deprecated, удаление в 1.3). В проекте используется dict состояний:
  `{ft.ControlState.DEFAULT: ft.OutlineInputBorder(...), ft.ControlState.FOCUSED: ...}`.
  Цвет/толщина — `ft.BorderSide(width, color)`; радиус — `border_radius=`.
- Вкладки: `ft.Tabs(content=ft.Column([ft.TabBar(...), ft.TabBarView(...)]), length=2, selected_index=0)`;
  число `Tab` и `length` держать синхронными.
- UI строится один раз в `__init__`: `_load_settings()` → `_setup_page()` → `_build_ui()`. `_build_ui` вызывает
  `_build_wish_tab()` / `_build_pull_tab()`, которые создают `self.wish_tab_content` / `self.pull_tab_content`.
- Поля ввода обёрнуты в `ft.Container` ради hover-эффекта, поэтому значение читается как
  `self.<field>.content.value` (не `self.<field>.value`). `guarantee_switch` — тоже контейнер со `Switch`.
- После изменения `value` / `visible` нужен `page.update()`. В hover-хендлерах обновлять точечно:
  `textfield.update()`, `container.update()` + `button.update()`.
- `ft.NumbersOnlyInputFilter()` не пропускает минус — отрицательные значения из UI не приходят.
- `_on_textfield_hover` пересобирает `border` и меняет `bgcolor`; `_on_button_hover` — `shadow`, `scale`
  и `style.bgcolor`.

### Механика гачи

- Базовый шанс 0.6% на крутках 1..73; soft pity с 74-й — оценка сообщества: +6 п.п. за крутку
  (6.6%, 12.6%, …, 96.6% на 89-й); 90-я крутка — 100%. Официально HoYoverse публикует только
  базовую ставку и hard pity, точная кривая не раскрыта.
- W-Engine (справочно, в калькуляторе пока не считается): 80 hard pity, 75% на ивентовый, гарант после промаха.
- Легендарный без гаранта: 50% ивентовый (pity → 0, гарант off) / 50% не-ивентовый (pity → 0, гарант on).
- С гарантом: legendary всегда ивентовый, гарант снимается.
- `_compute_distribution(pulls)` — DP по состояниям `(pity, guarantee)` с массивами длиной `pulls + 1`;
  стоимость растёт как O(pulls² × состояний). Для UI (≤ 90 круток) нормально, большие `pulls` не подавать.
- `probability_k(pulls, k)` возвращает **P(≥ k)** (`sum(dist[k:])`); docstring и UI-подпись «ШАНС ≥K КОПИЙ»
  это отражают.
- `current_pity` валиден 0..89 (90 запрещён: на 90-й срабатывает гарант). `pulls < 0` → `ValueError`.
- `probability_at_least_one(0) == 0.0`; при pity=89 и одной крутке без гаранта результат 0.5 (50/50).

### Экономика круток

| Константа | Значение |
|-----------|----------|
| `POLYCHROMES_PER_PULL` | 160 |
| `DAILY_TASK_POLYCHROMES` | 60 / день |
| `SUBSCRIPTION_POLYCHROMES_PER_DAY` | 90 / день (не дольше остатка подписки) |
| `RIDU_WEEKLY_POLYCHROMES` | 60 / неделя |
| `HOLLOW_ZERO_POLYCHROMES` | 160 / неделя |
| `SHIYU_DEFENSE_POLYCHROMES` | 780 / 14-дневная ротация |
| `DEADLY_ASSAULT_POLYCHROMES` | 300 / 14-дневная ротация |
| `MONTHLY_SHOP_PULLS` | 5 круток 1-го числа (за Residual Signal) |

- `weeks = days // 7` — неполная неделя не даёт недельный доход.
- `rotations = days // 14` — Shiyu Defense и Deadly Assault считаются только полными ротациями.
- Магазин: обход `start_date..start_date + days` включительно. 30 дней с 15 января всё равно задевают 1 февраля.
- Полихромы и монохромы складываются (1:1), остаток меньше 160 отбрасывается.
- `total_monochromes_used = min(monochromes, earned + polychromes)` — историческая формула «для отображения»,
  не равна фактическому расходу; не менять без отдельной задачи.
- `start_date` по умолчанию `date.today()`, `end_date = start_date + timedelta(days=days)`.
- События, компенсации и разовые награды в калькулятор не входят: их суммы официально не публикуются.

### Хранилище настроек

- `load_settings()` мержит сохранённые секции с `DEFAULT_SETTINGS` по верхнему уровню; битый JSON или `OSError`
  → дефолты. `save_settings()` возвращает `bool` и не пробрасывает `OSError`.
- `DEFAULT_SETTINGS.copy()` — **поверхностная** копия: вложенные dict'ы общие. `result[key].update(...)`
  и мутация результата `load_settings()` на месте меняют сами дефолты в пределах процесса.
  `save_*_settings` заменяют секцию целиком, поэтому сейчас это не проявляется.
- UI сохраняет настройки **до** расчёта, после успешной валидации (`save_wish_settings` / `save_pull_settings`).
- `save_settings` ловит только `OSError`; несериализуемые значения дадут `TypeError`.

### Валидация UI

- `pity` вне 0..89 и `days <= 0` → отдельные сообщения об ошибке.
- Прочие некорректные числа (`int("")`, отрицательные из кода) → `ValueError` → «ВВЕДИТЕ КОРРЕКТНЫЕ ЧИСЛА».
- `k == 0` трактуется как «хотя бы 1 копия» (`probability_at_least_one`), `k > 0` — как «≥ k копий».
- Результирующие карточки скрыты (`visible=False`) и показываются после расчёта или ошибки.

### Screenshot tool

- `tools/screenshots.py` поднимает настоящее приложение (не моки), включает `page.enable_screenshots = True`,
  переключает `app.tabs.selected_index`, ждёт перерисовку и вызывает `await page.take_screenshot()`.
- Артефакты: `tools/screenshots/01-wish.png`, `02-pulls.png`; папка в `.gitignore`.
- Имена табов и индексы — в `TABS`; `parse_selection()` и `screenshot_path()` чистые и покрыты тестами.
- Скрипт сам добавляет корень репозитория в `sys.path`, поэтому запускается из любого CWD.
- Скриншоты — локальная UI-приёмка; в CI их не снимают (нужен desktop-дисплей).

## Testing

- Всего **76** тестов, ~1 с, без сети, внешних сервисов и открытия окна.
- `tests/test_calculators.py` — 46 тестов: `TestZZZGachaCalculator` (18), `TestZZZPullCalculator` (23),
  `TestEdgeCases` (5). Проверяют soft pity с 74-й, доход, Ridu/Hollow/Shiyu/Deadly, месячный магазин.
- `tests/test_storage.py` — 13 тестов: patch `core.storage._get_config_dir` / `_get_config_file` на временную
  директорию, битый JSON, `OSError`, merge с дефолтами, round-trip.
- `tests/test_app.py` — 10 тестов: `ZZZGachaApp` на `MagicMock` page, вкладки, `page.window`, `OutlineInputBorder`,
  расчёты, ошибки валидации, сохранение настроек, свёрнутая справка по источникам.
- `tests/test_screenshot_tool.py` — 5 тестов чистых helper'ов без запуска Flet.
- `tests/test_environment.py` — 2 гейта: flet 1.x и установленный ruff.
- Тесты импортируют `core.*` / `app.*`, поэтому запускать из корня (отдельного `conftest.py`/`pyproject.toml` нет).
- Тесты, зависящие от даты, обязаны передавать `start_date` явно — `date.today()` делает их плавающими.
- UI проверяется запуском `main.py` и `tools/screenshots.py` (обе вкладки, hover, ошибки ввода,
  сохранение настроек между запусками).

### CI

`.github/workflows/ci.yml` — на push в `master` и на каждый PR: Python 3.12, установка
`requirements.txt` + `requirements-dev.txt`, `ruff check .`, `ruff format --check .`, `pytest -q`.
PR не принимается при красном CI по коду. Если CI не стартует по инфраструктурной причине
(биллинг/лимиты Actions), приёмка идёт по локальным гейтам с явной пометкой в PR.

## Task Workflow — обязательный порядок

1. **Ветка.** `git switch master && git pull --ff-only && git switch -c feat/<slug>`. Одна задача — одна ветка.
2. **Тесты (TDD).** Сначала падающие тесты на новое поведение (red). Для UI — тесты helper'ов/логики и сценарий
   скриншотов; для домена — unit-тесты в `tests/`.
3. **Решение.** Минимальная реализация до зелёных тестов (green). Без попутных фич.
4. **Рефакторинг.** Отдельный проход по диффу: дублирование, мёртвый код, длинные функции, имена, Flet-ловушки.
   Поведение не меняется, тесты не удаляются.
5. **Проверка.** `pytest -q -p no:warnings` + `ruff check .` + `ruff format --check .`; для UI — `tools/screenshots.py`
   и визуальная сверка PNG. Гейты должны быть не хуже, чем до задачи.
6. **Pull request.** Push ветки, PR в `master` с описанием: что/зачем/как проверено/скриншоты. Дождаться зелёного CI.

Шаги 2–4 можно распараллеливать агентами (например, тесты и миграция UI), но **тесты всегда появляются раньше
реализации**, а конфликты и приёмка остаются за основным агентом.

### Приёмка PR и конфликты (делает агент)

- Прочитать дифф и сверить с формулировкой задачи; отклонить лишний scope, секреты, отладочный код.
- Прогнать локально те же гейты, что в CI; для UI — скриншоты до/после.
- Конфликты решаются **rebase на master**, затем повторный прогон гейтов и `push --force-with-lease`.
  Merge-коммиты из `master` в ветку не делать.
- Принять PR (squash merge) только при зелёном CI и отсутствии замечаний; ветку удалить.
- Если PR отклонён — оставить конкретные замечания и вернуть в работу.

## Code Style

- Python 3.12+, type hints обязательны: `dict[str, Any]`, `list[float]`, `X | None`, `Final`.
- `ruff.toml` — единственный источник стиля: line-length 120, double quotes, indent 4, preview-правила.
- Подавления — именами правил (`# ruff: ignore[...]`), не кодами `noqa`.
- Docstrings и комментарии — по-русски, короткие; UI-строки — по-русски, КАПСОМ.
- `core/` не импортирует Flet; единственный побочный эффект — файловые операции в `storage.py`.
- Результаты расчётов — dataclass'ы с явными типами (`Currency`, `PullCalculationResult`).
- Публичный API `core` реэкспортируется в `core/__init__.py` и перечисляется в `__all__`.

## Рефакторинг после выполнения задачи (правило от пользователя)

Каждый принятый таск/слайс проходит рефакторинг-проход по диффу **до** PR/merge:
- scope — только файлы, изменённые задачей; без новых фич и без изменения поведения;
- убрать дублирование (в общий helper того же слоя), мёртвый код, длинные функции, несогласованные имена, Flet-ловушки;
- ворота: `pytest` + `ruff check` + `ruff format --check` до/после — не хуже, число тестов не уменьшается;
  для UI-слайсов — повторные скриншоты;
- отчёт: список правок + тест-счётчики; «рефакторинг не требуется» — валидный результат, искусственных правок не делать.

## Task Intake (правило от пользователя — не нарушать)

Когда пользователь даёт **новую** задачу, пока идёт другая работа: **не бросать текущую работу**. Параллельно —
исследовать и оценить сложность/приоритет новой задачи (SP), добавить её в backlog (GitHub Issues; либо
`docs/kanban.md`, если файл существует) и лишь затем, в порядке приоритета и WIP-лимита, брать в работу.
Текущую ветку/PR доводить до приёмки.

## Common Pitfalls

1. **`probability_k` — это «≥ k»**, а не «ровно k». Не «исправлять» UI-подпись, не меняя одновременно и тесты.
2. **`load_settings()` возвращает поверхностную копию дефолтов** — не мутировать вложенные dict'ы на месте.
3. **Поля обёрнуты в `Container`** — обращаться к `self.<field>.content.value`, иначе `AttributeError`.
4. **`page.update()` обязателен** после смены `value` / `visible`; точечные `control.update()` — только для hover.
5. **Лимиты дублируются** в UI (`_on_wish_calculate`, `_on_pull_calculate`) и в домене (`ValueError` в конструкторах) —
   менять согласованно.
6. **`days=0` допустим в домене**, но UI его отклоняет (`days <= 0`). Не переносить UI-правило в калькулятор без задачи.
7. **Дата в тестах** — только через `start_date`; `date.today()` даёт нестабильные тесты на границе месяца.
8. **Flet 1.0**: не возвращать `ElevatedButton`, loose-свойства `border_*`, `page.window_width` и `ft.app`;
   границы полей — только через `border=`.
9. **Настройки сохраняются до расчёта** — при ошибке валидации старые значения остаются, новые не пишутся.
10. **Скриншоты** — только через `tools/screenshots.py`; папка `tools/screenshots/` не коммитится, а скрипт
    требует desktop-окружение (в headless CI не запускается).
11. **Версии**: `flet==1.0.5`, `pytest==9.1.1`, `ruff==0.17.3`; не смешивать 1.0.x с 0.8x API и не обновлять
    одну зависимость без прогона приложения.
12. **Soft pity — оценка, а не официальная ставка**: 74-я крутка, +6 п.п. за крутку. Не выдавать это за
    опубликованную HoYoverse кривую; в UI есть пометка.
13. **Эндгейм считается полными 14-дневными ротациями** (`days // 14`); Ridu Weekly — 60/неделю, а не 420.
    Не возвращать старые значения при «упрощении» прогноза.
14. **Магазин — не бесплатные крутки**: 5 Encrypted Master Tapes в месяц стоят Residual Signal. Если их нет,
    прогноз завышен; это известное допущение, а не баг.
