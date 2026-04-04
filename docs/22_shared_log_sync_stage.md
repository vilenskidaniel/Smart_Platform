# Stage 22 - Shared Log Sync Contour

Этот этап закрывает первый двусторонний контур общего журнала между `ESP32` и `Raspberry Pi`.

## Что сделано

- На стороне `ESP32` добавлен `PlatformEventLog` с локальными и зеркалированными записями.
- `ESP32 shell` теперь отдает `GET /api/v1/logs` и принимает зеркалированные записи через
  `POST /api/v1/sync/logs/push`.
- Ключевые команды shell и sync-операции на `ESP32` теперь пишут события в platform log.
- На стороне `Raspberry Pi` общий журнал узла научился:
  - хранить `origin_node`;
  - хранить `origin_event_id`;
  - помечать зеркалированные записи;
  - дедуплицировать повторные remote push-записи.
- `sync_client.py` теперь не только отправляет heartbeat и module push, но и:
  - отправляет локальные log entry в `ESP32`;
  - забирает `/api/v1/logs` с `ESP32`;
  - зеркалирует их в локальный `PlatformEventLog`.
- Оба shell-интерфейса теперь показывают общий `Platform Log`, а не только локальные события.

## Какие файлы появились

- `firmware_esp32/include/core/PlatformEventLog.h`
- `firmware_esp32/src/core/PlatformEventLog.cpp`
- `docs/22_shared_log_sync_stage.md`

## Какие файлы изменились

- `firmware_esp32/include/web/WebShellServer.h`
- `firmware_esp32/src/web/WebShellServer.cpp`
- `firmware_esp32/src/main.cpp`
- `firmware_esp32/data/index.html`
- `raspberry_pi/platform_event_log.py`
- `raspberry_pi/bridge_state.py`
- `raspberry_pi/sync_client.py`
- `raspberry_pi/web/index.html`
- `raspberry_pi/tests/test_turret_runtime_and_scenarios.py`
- `shared_contracts/api_contracts.md`

## Новый API слоя синхронизации логов

- `GET /api/v1/logs`
- `POST /api/v1/sync/logs/push`

## Что теперь можно проверять

1. Как локальные сервисные действия `ESP32` попадают в platform log.
2. Как события `Raspberry Pi` отправляются в `ESP32` и появляются там как `mirrored`.
3. Как `ESP32`-события подтягиваются обратно в `Raspberry Pi shell`.
4. Как дедупликация защищает журнал от повторной доставки одного и того же remote event.

## Что пока еще не закрыто

- Полный merge настроек и сценариев между узлами.
- Экспорт журнала на диск в едином формате платформы.
- Приоритеты хранения и очистки long-term history.
- Живая обкатка двустороннего log sync на реальных двух узлах в одной сети.

## Почему этот этап важен

До этого момента shell и sync уже умели:

- показывать состояние peer-узла;
- передавать heartbeat;
- публиковать module state.

Но общей наблюдаемости еще не было. Теперь у платформы появился первый общий диагностический канал,
который одинаково полезен и для сервисных тестов, и для последующей интеграции реального железа.

## Проверки этапа

- `py -3 -m py_compile ...` для `raspberry_pi` прошел успешно.
- `py -3 -m unittest discover tests -v` прошел успешно, `5 tests OK`.
- `pio run` для `firmware_esp32` прошел успешно.
- `pio run -t buildfs` для `firmware_esp32` прошел успешно.
