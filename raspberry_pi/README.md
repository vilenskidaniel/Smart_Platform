# raspberry_pi

Здесь живет логика `Raspberry Pi` для `Smart Platform`.

На текущем этапе это уже не только shell и turret runtime bootstrap,
а software-level `Turret v1` с отдельными product/service страницами и двумя новыми слоями:

- `TurretEventLog` для локального журнала событий;
- `TurretDriverLayer` для будущих аппаратных binding'ов.

## Что уже есть

- локальный shell `/`;
- turret-страница `/turret`;
- отдельная service/test страница `/service/turret`;
- runtime-подсистемы:
  - `motion`
  - `strobe`
  - `water`
  - `audio`
  - `camera`
  - `range`
  - `vision`
- product-level snapshot с:
  - `manual console`
  - `automatic defense`
  - `service lane`
  - `camera/range availability`
  - `action readiness`
- фоновые heartbeat и push состояния в `ESP32`;
- флаги:
  - `automation_ready`
  - `target_locked`
  - `vision_tracking`
- interlock-команды:
  - `fault`
  - `emergency`
  - `clear`
- локальный журнал событий turret-runtime;
- заглушечный слой будущих драйверов.

## Чего пока нет

- реальной камеры;
- реального дальномерного канала;
- машинного зрения;
- баллистики и наведения;
- реальных драйверов исполнительных устройств турели;
- полного merge логов и настроек между узлами.

## Как запустить

Из каталога `raspberry_pi`:

```bash
python3 app.py
```

По умолчанию сервер поднимается на:

- `http://0.0.0.0:8080/`

Основные страницы:

- `/`
- `/turret`
- `/service/turret`

Полезные API:

- `/api/v1/turret/status`
- `/api/v1/turret/runtime`
- `/api/v1/turret/events`
- `/api/v1/turret/drivers`
- `/api/v1/turret/scenarios`
- `/api/v1/content/status`

## Переменные окружения

- `SMART_PLATFORM_RPI_HOST`
- `SMART_PLATFORM_RPI_PORT`
- `SMART_PLATFORM_RPI_PUBLIC_BASE_URL`
- `SMART_PLATFORM_RPI_CONTENT_ROOT`
- `SMART_PLATFORM_RPI_NODE_ID`
- `SMART_PLATFORM_ESP32_BASE_URL`
- `SMART_PLATFORM_SYNC_INTERVAL_SEC`
- `SMART_PLATFORM_SYNC_ENABLED`

## Что важно помнить

- `Raspberry Pi` — владелец турели.
- `ESP32` не должен напрямую перетирать runtime турели.
- shell на `Raspberry Pi` и `ESP32` должен оставаться визуально согласованным.
- текущий driver layer еще не управляет железом, а только держит каркас binding'ов.
- peer-owned модули теперь открываются через federated handoff flow, а не через слепое локальное управление чужой страницей.
- тяжелый контент и крупные библиотеки данных на этой стороне должны жить в `content_root`, зеркально к `ESP32 SD`.

`TODO(stage-rpi-real-devices-and-vision)`

## Latest Stage

Теперь в ветке `raspberry_pi` уже есть software-level `Turret v1`
поверх первого общего log/sync-контура с `ESP32`.

Что это значит practically:

- `Turret` больше не выглядит как набор внутренних runtime-флагов;
- `/turret` показывает продуктовый модульный обзор, а `/service/turret` держит service/test инструменты;
- `camera` и `range` уже присутствуют в owner-модели как software-level availability channels;
- action channels и automatic gates публикуются как понятные product-level состояния;
- локальные события `Raspberry Pi` отправляются в `ESP32`;
- `Raspberry Pi` умеет забирать `/api/v1/logs` у `ESP32`;
- общий shell показывает смешанный platform log с локальными и зеркалированными записями;
- повторные remote log entry дедуплицируются по `origin_node + origin_event_id`.

Это еще не real-device turret integration, но уже рабочее software-level продуктовое состояние
для следующего модульного шага: `Service/Test v1`.
