# Источники данных об ивентах и крутках ZZZ

Дата проверки: 2026-10-27. Версия игры на момент проверки: 3.3.
Документ фиксирует результаты исследования. С 2026-10-27 автоматическая оценка ивентов
интегрирована в калькулятор (см. раздел 6).

## 1. Что уже исправлено в приложении

| Параметр | Было | Стало | Статус |
|----------|------|-------|--------|
| Soft pity агента | 75-я крутка, 20% | 74-я крутка, +6 п.п. за крутку | оценка сообщества, не официальная ставка |
| Ridu Weekly | 420/неделя | 60/неделя | in-game reward table |
| Hollow Zero | «нулевая каверна», 160/неделя | Hollow Zero, 160/неделя | in-game reward table |
| Shiyu Defense | не учитывался | 780 за 14-дневную ротацию | in-game reward table |
| Deadly Assault | не учитывался | 300 за 14-дневную ротацию | in-game reward table |
| Магазин | «5 круток/мес» без пояснения | 5 круток/мес за Residual Signal | не бесплатные |

Базовые значения: 0.6% S-ранг, hard pity 90, 50/50 для агента, гарант после проигрыша 50/50.
W-Engine: 80 hard pity, 75/25. Оба канала доступны в калькуляторе.

## 2. Надёжный источник ивентов

### Рекомендуемый основной канал: официальный аккаунт ZZZ на HoYoLAB

Публичный endpoint (без авторизации):

```text
GET https://bbs-api-os.hoyolab.com/community/post/wapi/getNewsList?gids=8&page_size=20&type=1
GET https://bbs-api-os.hoyolab.com/community/post/wapi/getNewsList?gids=8&page_size=20&type=2
```

- `gids=8` — Zenless Zone Zero.
- `type=1` — новости/анонсы (включая «Event Details», патчноуты, баннеры).
- `type=2` — события сообщества/награды (Twitch Drops, розыгрыши, веб-ивенты).
- Проверено 2026-10-27: `retcode=0`, ответ содержит `data.list[].post` и `data.list[].user`.

Фильтр официальности:

```text
user.certification.desc == "ZZZ Official"
или
user.uid == "219270333"
```

Примеры официальных публикаций из выдачи: `Cyber Miracle Healer, on Duty! Event Details`,
`Version 3.3 "Journey to the Sky" Update Announcement`, `V3.3 Limited-Time Channels (Phase I)`.

Детали публикации:

```text
GET https://bbs-api-os.hoyolab.com/community/post/wapi/getPostFull?post_id=<id>
```

Особенности:

- `post.event_start_date` / `post.event_end_date` в проверенных ответах были `"0"` — на них нельзя полагаться.
- Реальные даты обычно лежат в `post.structured_content` (JSON-массив Quill-ops) текстом:
  `Event Duration` → `2026/10/28 10:00 (server time) – 2026/11/16 03:59 (server time)`.
- Нужен парсер с ручной проверкой; формат текста может меняться.
- Endpoint публичный, но **недокументированный**: возможны лимиты, смена схемы и требования к заголовкам.
  Нужны кэш (например, 15–30 минут), `User-Agent`, `Referer: https://www.hoyolab.com/` и fallback.
- Контент — first-party (аккаунт HoYoverse), но сам API не является официально гарантированным контрактом.

### Дополнительный официальный канал: сайт ZZZ

```text
https://zenless.hoyoverse.com/en-us/news
https://zenless.hoyoverse.com/en-us/news/<id>
```

- Стабильные HTML-страницы с официальными новостями и датами.
- Публичного документированного API у сайта нет; HTML/JS может меняться, поэтому это fallback,
  а не основной автоматический источник.
- Категории сайта: `NEWS=295`, `ANNOUNCE=296`, `EVENT=297` (видны в JS сайта).

### Официальный launcher-канал: HoyoPlay API

```text
GET https://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api/getGameContent
    ?launcher_id=VYTpXlbWo8&language=en-us&game_id=U5hbdsT9W7
```

- Официальный API лаунчера; возвращает `banners` и `posts` (до 5 постов).
- `game_id` ZZZ: `U5hbdsT9W7`; `biz`: `nap_global`.
- Плюс: стабильная официальная выдача, удобно для «что нового».
- Минус: мало постов, дата в формате `MM/DD` без года, нет диапазона ивента.
- Годится как supplement, не как полный календарь.

### Что не использовать как источник истины

- Fan-wiki, агрегаторы, «leaks», YouTube-гайды — только для обнаружения события.
- Любые суммы Polychrome из ивентов на сторонних сайтах — оценки, а не официальные данные.
- Не парсить ивенты на каждом запуске приложения: кэш + ручное подтверждение.

### Рекомендуемая схема на будущее (не реализована)

1. `core/news_client.py`: HTTP-клиент HoYoLAB с кэшем и таймаутом.
2. Забирать `type=1` и `type=2`, фильтровать по `uid` официального аккаунта.
3. Для каждой публикации сохранять `post_id`, `subject`, `created_at`, ссылку.
4. Даты ивента парсить из `structured_content`; при неудаче — оставлять «дата не определена»,
   а не выдумывать.
5. Показывать ивенты в UI отдельным списком/календарём, **не добавляя их автоматически** в прогноз круток.
6. Суммы Polychrome из ивентов вводить вручную после просмотра официального поста.

## 3. Источники дохода: что считается надёжным

| Источник | Значение | Уверенность |
|----------|----------|-------------|
| 1 крутка | 160 Polychrome | официально, in-game |
| Ежедневки (Engagement 400) | 60/день | in-game reward table |
| Ridu Weekly | 60/неделя | in-game reward table |
| Hollow Zero Bounty | 160/неделя | in-game reward table |
| Shiyu Defense: Critical Node | 780 за 14-дневную ротацию (B+A+S стаки) | in-game reward table |
| Deadly Assault | 300 за 14-дневную ротацию (6 звёзд) | in-game reward table |
| Inter-Knot Membership | 90/день + 300 Monochrome сразу | официально |
| Signal Shop | 5 Encrypted Master Tapes/мес за Residual Signal | in-game shop; не «бесплатные» |
| События | официально не публикуется точная сумма; ~2000/патч — оценка | низкая для точного планирования |
| Компенсации/коды/Twitch/HoYoLAB check-in | разовые, зависят от патча | средняя, требуют ручной проверки |
| Сюжет/исследование/достижения/Trust | разовые, не повторяются | высокая, но не для прогноза |

Примечания:

- Shiyu Defense и Deadly Assault чередуются с шагом 7 дней, но каждая ротация длится 14 дней.
  Текущий калькулятор считает по `days // 14` для каждого режима — консервативно.
- Полный S-ранг Shiyu даёт 780, а не 720: B/A/S-награды складываются. S+ дополнительных
  Polychrome не даёт.
- Deadly Assault: только первые 6 звёзд дают Polychrome, 7–9 — материалы/Denny.
- Магазин: 5 Encrypted Master Tapes стоят Residual Signal; если их нет, эти 5 круток не появятся.
  Это допущение нужно либо показать в UI, либо сделать переключателем.
- Inter-Knot Membership: 300 Monochrome сразу + 90/день за 30 дней. В прогнозе учитывается
  только 90/день по остатку подписки; 300 — разовая выплата при покупке.

## 4. Ссылки

- Официальные ставки Signal Search: https://zenless.hoyoverse.com/en-us/news/public
- Официальный сайт, новости: https://zenless.hoyoverse.com/en-us/news
- HoYoLAB, канал ZZZ: https://www.hoyolab.com/circles/8
- HoYoLAB news API (публичный, недокументированный):
  https://bbs-api-os.hoyolab.com/community/post/wapi/getNewsList?gids=8&page_size=20&type=1
- HoyoPlay launcher API (game content):
  https://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api/getGameContent?launcher_id=VYTpXlbWo8&language=en-us&game_id=U5hbdsT9W7
- Описание HoyoPlay API: https://gist.github.com/DynamiByte/0ad250bbe1930e2736a6d4e6e842bcb2
- Prydwen, gacha system: https://www.prydwen.gg/zenless/guides/gacha-system
- Timesaver, pity system: https://timesaver.gg/blog/zzz-pity-system
- Timesaver, polychrome farming: https://timesaver.gg/blog/zzz-polychrome-farming
- ZZZ Poly Calculator: https://zzz-poly-cal.vercel.app/
- Lootbar, 2.7 pull count: https://lootbar.gg/blog/en/zenless-zone-zero-2-7-pull-count.html

## 5. Пробный прогон 2026-10-27

Скрипт: `tools/events_probe.py` (только чтение, без записи настроек).

```bash
.\.venv\Scripts\python.exe tools\events_probe.py --details
```

Запрос: `gids=8`, по 8 публикаций из `type=1` и `type=2`, фильтр официального аккаунта.
Получено 16 официальных публикаций. Примеры:

| Публикация | Event Duration |
|------------|----------------|
| "Cyber Miracle Healer, on Duty!" Event Details | 2026/10/28 10:00 – 2026/11/16 03:59 (server time) |
| "Spooky Funhouse Tales" Event Details | 2026/10/22 10:00 – 2026/11/30 03:59 (server time) |
| "All-New Program" Event Details | After the Version 3.3 update – 2026/12/01 03:59 (server time) |
| Version 3.3 New Eridu City Fund Details | After the Version 3.3 update – 2026/11/30 03:59 (server time) |
| "Arm Wrestle with Roxy" | October 2 – October 8 |
| "Vyrium Vacation Album" | September 9 – October 10 |

Наблюдения:

- `Event Duration` есть не у всех публикаций; для части новостей/патчноутов поле отсутствует.
- Формат дат разный: `YYYY/MM/DD HH:MM (server time)`, `October 2 – October 8`, `After the update – …`.
  Нужен нормализатор и ручная проверка, автоматически доверять нельзя.
- Часть старых событий уже завершилась; при интеграции нужно фильтровать по `event_end`/текущей дате.
- `type=2` содержит не только игровые ивенты, но и розыгрыши/Twitch Drops/веб-активности.

## 6. Автоматическая оценка в приложении

Реализовано в `core/events.py`:

- загрузка официальной ленты HoYoLAB (`gids=8`, типы 1/2);
- фильтр по аккаунту `ZZZ Official`;
- парсинг `Event Duration` и явных наград (`Polychrome ×N`, `Encrypted Master Tape ×N`);
- каталог подтверждённых наград текущего патча (3.3), чтобы не терять суммы, которые
  в тексте поста не указаны, а видны только на официальном арте;
- fallback: неизвестный `Event Details` получает оценку 300 Polychrome и попадает только
  в верхнюю границу диапазона;
- кэш `~/.zzz_wish_calculator/events_cache.json`, TTL 6 часов;
- фильтрация по периоду прогноза и сложение с общим результатом.

Проверка на 2026-10-27 (30 дней, кэш):

- 6 опубликованных событий;
- 21 крутка (все известные награды + 10 талонов All-New Program);
- это только уже опубликованные события: будущие ивенты появятся в ленте после анонсов
  и будут добавлены при следующем обновлении кэша.

В UI есть переключатель «УЧИТЫВАТЬ ИВЕНТЫ» и строка статуса:
`Ивенты: +21–21 круток · 6 событий`. При офлайне/ошибке сети расчёт продолжается без ивентов,
а статус показывает, что данных нет.

Важно: 21 крутка — не «все ивенты патча», а сумма по текущим официальным публикациям.
По мере выхода анонсов оценка растёт; кэш обновляется автоматически раз в 6 часов.

## 7. Вывод

Для автоматического обнаружения ивентов лучший компромисс — **официальный аккаунт ZZZ на HoYoLAB**
через `getNewsList?gids=8` + `getPostFull` с фильтром `uid=219270333` и кэшем.
Официальный сайт — fallback, HoyoPlay API — supplement. Точные суммы Polychrome из ивентов
официально не публикуются, поэтому в калькуляторе они подаются как диапазон/оценка:
подтверждённые суммы идут в минимум, неизвестные — только в максимум.
