# GitHub Pages

Это статическая web-версия ZZZWishCalculator на Pyodide. Python-расчёты выполняются в браузере,
настройки не сохраняются: после перезагрузки значения сбрасываются.

## Публикация

В GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**:

- Branch: `master`
- Folder: `/docs`

Файл `.nojekyll` уже добавлен, поэтому GitHub Pages не пытается обрабатывать `docs/` через Jekyll.

URL после публикации:

```text
https://<username>.github.io/ZZZWishCalculator/
```

## Обновление

После изменения `core/*.py` или `web_bridge.py` пересоберите копии и снимок ивентов:

```bash
.\.venv\Scripts\python.exe tools\build_web.py
```

Затем закоммитьте изменения в `docs/`. Тест `tests/test_web_build.py` проверяет, что копии
`docs/py/core` совпадают с `core/`.

Если сеть недоступна, можно собрать без ивентов:

```bash
.\.venv\Scripts\python.exe tools\build_web.py --no-events
```

## Локальная проверка

```bash
.\.venv\Scripts\python.exe -m http.server 8765 --directory docs
```

Откройте `http://127.0.0.1:8765/`.

Pyodide загружается с CDN, поэтому для работы нужен интернет. HoYoLAB не отдаёт CORS-заголовки
для браузера, поэтому ивенты — снимок `data/events.json` на дату сборки, а не live-запрос.
