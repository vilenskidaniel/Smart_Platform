# Stage 16 - Sync Bootstrap For ESP32 Shell

Этот этап добавляет первый рабочий слой синхронизации между `ESP32` и будущим `Raspberry Pi`.

## Что сделано

- `System Core` теперь хранит не только `reachable`, но и:
  - `sync_ready`
  - `reported_mode`
- Добавлены sync-endpoint'ы:
  - `/api/v1/sync/state`
  - `/api/v1/sync/heartbeat`
  - `/api/v1/sync/modules/push`
- Реестр удаленных модулей теперь может обновляться через отдельный push-механизм.
- `sync_core` стал честно отражать состояние связи:
  - `degraded / owner_unavailable`, если peer недоступен
  - `degraded / peer_sync_pending`, если heartbeat есть, но синхронизация еще не завершена
  - `online / none`, если peer на связи и sync подтвержден

## Почему это важно

До этого этапа `ESP32` знала только одно: peer либо есть, либо его нет.

Этого недостаточно для корректного shell:

- нельзя честно различить "Raspberry Pi уже на связи, но еще не синхронизировал модули"
- нельзя аккуратно разблокировать турельные разделы
- нельзя показать тестировщику, что интерфейс уже видит второй узел, но еще не получил runtime-состояние его модулей

Теперь этот промежуточный слой появился.

## Что уже может делать Raspberry Pi в будущем

Даже без полного `Raspberry Pi bridge` уже заложены простые сценарии:

1. Послать heartbeat:

`POST /api/v1/sync/heartbeat?node_id=rpi-turret&wifi_ready=1&shell_ready=1&sync_ready=1&reported_mode=manual`

2. Послать runtime-состояние удаленного модуля:

`POST /api/v1/sync/modules/push?id=strobe&state=online&block_reason=none`

или

`POST /api/v1/sync/modules/push?id=turret_bridge&state=degraded&block_reason=peer_sync_pending`

## Ограничения этапа

- Это еще не полный двусторонний sync engine.
- Пока нет pull/merge настроек, логов и сценариев.
- Пока не реализована защита по аутентификации.
- Пока `ESP32` принимает push только для peer-owned модулей `Raspberry Pi`.

## Почему push ограничен только peer-owned модулями

Это сознательная мера безопасности.

На этом этапе sync API не должен случайно переписать локальные модули `ESP32`, такие как:

- `irrigation`
- `strobe_bench`

Поэтому `System Core` отклоняет попытку обновить через sync API модуль, который не принадлежит `rpi`.

## Что дальше

`TODO(stage-rpi-bridge-bootstrap)`

Следующий логичный шаг — сделать минимальный `Raspberry Pi turret bridge`, который:

- отправляет heartbeat;
- публикует runtime-состояние `turret_bridge` и `strobe`;
- поднимает такой же shell по внешнему виду;
- показывает `ESP32`-модули как remote-backed разделы.
