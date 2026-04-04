# Stage 18 - Raspberry Pi Turret Bridge Bootstrap

Этот этап добавляет первую живую сторону `Raspberry Pi` в `Smart Platform`.

## Что сделано

- Поднят минимальный локальный web server на `Python stdlib`.
- Добавлен shell в стиле `ESP32`.
- Добавлена страница `/turret`.
- Появилась локальная модель узла `Raspberry Pi`.
- Появилась локальная модель модулей:
  - `turret_bridge`
  - `strobe`
- Появился фоновый sync-клиент, который:
  - шлет heartbeat в `ESP32`;
  - шлет push-состояние `turret_bridge` и `strobe`;
  - читает `ESP32` snapshot и зеркалит peer-модули.

## Какие файлы появились

- `app.py`
- `bridge_config.py`
- `bridge_state.py`
- `server.py`
- `sync_client.py`
- `web/index.html`
- `web/turret.html`

## Почему используется Python stdlib

На этом этапе это сознательный выбор.

Причины:

- не тянуть лишние зависимости;
- быстрее получить рабочий bootstrap;
- проще запускать на разных системах;
- не блокировать следующий этап из-за выбора web-фреймворка.

`TODO(stage-rpi-web-framework)`

Позже можно решить, нужен ли более удобный framework, но foundation лучше сначала проверить на простом и прозрачном коде.

## Что уже можно делать

1. Запустить локальный shell `Raspberry Pi`.
2. Открыть страницу `/turret`.
3. Менять локальный mode:
   - `manual`
   - `automatic`
   - `service_test`
   - `emergency`
4. Переключать состояние:
   - `turret_bridge`
   - `strobe`
5. Принудительно запускать sync.
6. Смотреть, как `ESP32` начинает видеть peer-узел и удаленные turret-модули.

## Что пока еще заглушка

- реальной камеры нет;
- машинного зрения нет;
- наведения нет;
- реальных actuator driver'ов нет;
- локальная turret-страница пока имитирует runtime вручную.

Это намеренная стадия.

Нам сначала нужно проверить:

- что shell действительно одинаков по виду и логике;
- что sync-контракт живет в обе стороны;
- что ownership модулей не ломается;
- что `ESP32` и `Raspberry Pi` начинают видеть друг друга как peer-узлы.

## Полезные маршруты

### Shell

- `/`
- `/turret`

### API

- `/api/v1/system`
- `/api/v1/modules`
- `/api/v1/turret/status`
- `/api/v1/turret/mode`
- `/api/v1/turret/module`
- `/api/v1/sync/status`
- `/api/v1/sync/refresh`

## Что дальше

`TODO(stage-rpi-runtime-integration)`

Следующий логичный шаг:

- подключить реальную модель turret runtime;
- вынести ручные имитации состояния в отдельный service/test профиль;
- начать готовить bridge к настоящим actuator и vision-модулям.
