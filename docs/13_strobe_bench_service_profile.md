# Strobe Bench Service Profile

Этот документ фиксирует текущий software-stage для `strobe_bench` внутри `Smart_Platform`.

## Главная идея

В системе существуют две разные роли одного семейства `strobe`:

- `strobe`
  - turret/product profile
  - владелец: `Raspberry Pi`
  - используется как action-channel турели
  - продуктовый доступ идет через `FPV/manual` слой турели
- `strobe_bench`
  - service/bench profile
  - владелец: `ESP32`
  - используется для локальной лабораторной проверки и безопасного bring-up
  - доступ идет через `/service/strobe`

Это разделение остается обязательным: `ESP32` не подменяет owner-side боевой `strobe`, а обслуживает только локальный сервисный контур.

## Что уже реализовано

- отдельный `ESP32` controller для bench-режима;
- безопасный старт пина управления;
- service-gated команды:
  - `arm`
  - `disarm`
  - `stop`
  - `abort`
  - `pulse`
  - `burst`
  - `loop`
  - `continuous on`
  - `preset`
- API-маршруты:
  - `/api/v1/strobe_bench/status`
  - `/api/v1/strobe_bench/presets`
  - `/api/v1/strobe_bench/arm`
  - `/api/v1/strobe_bench/disarm`
  - `/api/v1/strobe_bench/stop`
  - `/api/v1/strobe_bench/abort`
  - `/api/v1/strobe_bench/pulse`
  - `/api/v1/strobe_bench/burst`
  - `/api/v1/strobe_bench/loop`
  - `/api/v1/strobe_bench/continuous`
  - `/api/v1/strobe_bench/preset`
- tab-based service page `/service/strobe`
  - `Overview`
  - `Pulse`
  - `Burst`
  - `Loop`
  - `Continuous`
  - `Presets`
- live status window без reload страницы;
- окно последнего ответа команды и история текущей сессии;
- safe preset запуск прямо из service-страницы;
- отображение `strobe_bench` в общем `Laboratory` контуре.

## Что это означает для Laboratory

`strobe_bench` больше не является просто набором отдельных POST-команд.

Текущая страница уже считается первым углубленным laboratory slice внутри `Laboratory`:

- переключение между вкладками происходит внутри одной страницы;
- пользователь одновременно видит controls, поля ввода и живой статус;
- `burst` теперь доведен до UI-уровня, а не только существует в controller;
- donor-режимы `loop` и timed `continuous on` теперь тоже живут внутри platform laboratory surface, а не остаются в старом bench-repo;
- инженерный сервисный контур остается отделенным от продуктового `FPV/manual` доступа к боевому `strobe`.

## Что пока еще не закрыто

- сохранение подобранных bench-параметров как рабочего профиля;
- перенос этих параметров в общий profile/preset contract платформы;
- отдельный platform-level event log именно для `strobe_bench`;
- owner-side handoff между turret product-layer и service-layer;
- более глубокие диагностические сценарии beyond `pulse/burst/loop/continuous/preset`.

## Правило безопасности

`strobe_bench` не должен размывать ownership boundary.

Это означает:

- `ESP32` управляет только bench/service профилем;
- turret `strobe` на `ESP32` остается только видимым shell-объектом, а не локально-владельческим модулем;
- любые будущие автоматические turret-команды по боевому `strobe` должны идти только через `Raspberry Pi`.
