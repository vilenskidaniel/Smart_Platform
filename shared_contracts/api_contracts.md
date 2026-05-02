# API Contracts

Этот документ описывает технические API-контракты между узлами и модулями.

Важно:

- это не документ уровня продукта;
- состав API не равен списку пользовательских модулей `v1`;
- для продуктового scope сначала читать [26_v1_product_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/26_v1_product_spec.md).
- для shell-level snapshot читать отдельный [shell_snapshot_contract.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/shared_contracts/shell_snapshot_contract.md).

Это черновой, но уже рабочий словарь сущностей для новой платформы.

`TODO(stage-contracts-v1)`

Когда начнется перенос кода, этот файл нужно будет превратить в формальный контракт версий `v1`.

## System Snapshot

Каждый узел должен уметь отдавать снимок системы в одном и том же виде.

```json
{
  "node_id": "esp32-main",
  "node_type": "esp32",
  "ui_shell_version": "0.1.0",
  "active_mode": "manual",
  "service_mode": false,
  "emergency_state": false,
  "peer": {
    "reachable": true,
    "node_id": "rpi-turret",
    "last_seen_ms": 820
  },
  "modules": [
    {
      "id": "irrigation",
      "owner": "esp32",
      "state": "online",
      "locked_reason": ""
    },
    {
      "id": "turret",
      "owner": "rpi",
      "state": "locked",
      "locked_reason": "owner_unavailable"
    }
  ]
}
```

## Module Descriptor

```json
{
  "id": "strobe",
  "title": "Strobe",
  "owner": "rpi",
  "owner_node_id": "rpi-turret",
  "owner_available": true,
  "profile": "turret",
  "state": "online",
  "canonical_path": "/turret#strobe",
  "canonical_url": "http://raspberrypi.local:8080/turret#strobe",
  "federated_access": "peer_owner_available",
  "capabilities": ["arm", "abort", "preset_run", "service_page"],
  "locked_reason": "",
  "service_available": true
}
```

## Общие состояния модуля

- `online`
- `degraded`
- `locked`
- `fault`
- `service`
- `offline`

## Общая команда

```json
{
  "command_id": "cmd-0001",
  "target_module": "strobe",
  "action": "preset_run",
  "params": {
    "preset_id": "bench_safe"
  },
  "source_node": "rpi",
  "requested_mode": "service"
}
```

## Общий ответ

```json
{
  "command_id": "cmd-0001",
  "accepted": true,
  "executed_by": "rpi",
  "target_module": "strobe",
  "result_state": "running",
  "message": "preset started"
}
```

## Общий event log формат

```json
{
  "event_id": "evt-0001",
  "timestamp_ms": 123456,
  "source_node": "esp32",
  "module": "irrigation",
  "level": "info",
  "type": "manual_command",
  "message": "zone 1 started",
  "sync_status": "local_only"
}
```

## Первые обязательные endpoint-группы

Для пользовательского shell и особенно `Settings` главным контрактом является
`GET /api/v1/shell/snapshot` плюс `GET /api/v1/settings`. Остальные endpoint
остаются специализированными surfaces: они могут питать snapshot внутри backend
или открываться как service/diagnostics views, но клиент `Settings` не должен
собирать truthful-state картину из разрозненных `content` и `sync` запросов.

- `/api/v1/system`
- `/api/v1/shell/snapshot`
- `/api/v1/modules`
- `/api/v1/federation/route`
- `/api/v1/modules/{id}/status`
- `/api/v1/modules/{id}/command`
- `/api/v1/logs`
- `/api/v1/reports`
- `/api/v1/reports/testcase`
- `/api/v1/reports/note`
- `/api/v1/content/status`
- `/api/v1/content/cleanup?target={whitelisted_target}&confirm=0|1`
- `/api/v1/settings`
- `/api/v1/platform/registry`
- `/api/v1/platform/registry/constructor`
- `/api/v1/host/open?target={whitelisted_target}`
- `/api/v1/sync/heartbeat`
- `/api/v1/sync/state`
- `/api/v1/sync/modules/push`

## Content Status Snapshot

Оба узла должны уметь честно сообщать, готов ли их storage слой heavy-content.
Для `Settings` эта информация должна приходить как `snapshot.storage`; прямой
`GET /api/v1/content/status` остается service/storage diagnostics endpoint.

```json
{
  "storage": "filesystem",
  "storage_kind": "filesystem",
  "content_root": "/opt/smart-platform/content",
  "content_root_exists": true,
  "content_root_state": "ready",
  "paths": [
    {
      "id": "audio",
      "title": "Audio",
      "path": "/opt/smart-platform/content/audio",
      "state": "ready",
      "exists": true,
      "file_count": 12,
      "dir_count": 2,
      "total_bytes": 73400320,
      "copy_supported": true,
      "open_supported": true,
      "open_target": "audio",
      "app_supported": true,
      "app_url": "/gallery?tab=media&kind=audio",
      "cleanup_supported": true,
      "cleanup_reason": "",
      "metadata": {}
    }
  ]
}
```

Для `ESP32` `storage_kind` может быть `sd`, а отдельные paths могут указывать
на SD-backed content slices. `LittleFS` не считается главным хранилищем heavy
content.

Legacy boolean поля вроде `assets_ready`, `audio_ready`, `animations_ready` и
`libraries_ready` можно сохранять как compatibility summary, но UI не должен
подменять ими component/path-level readiness.

Рекомендуемый порядок user-facing storage cards: `project_root`, `libraries`
или plant library, `video`, `audio`, `gallery_reports`, `gallery`, `assets`,
`animations`, `content_root`.

`libraries` / `Plant Library` является irrigation-linked slice. Для него
`app_url` должен вести в irrigation/library context, а `metadata` может
публиковать `plant_profile_count`, полученный из
`content/libraries/plant_profiles.v1.json`.

## Settings Sync And Component Options

`GET/POST /api/v1/settings` хранит не только внешний вид, но и durable UI
модель для sync и component engineering fields:

```json
{
  "synchronization": {
    "preferred_mode": "auto",
    "selected_domains": {
      "service_link": true,
      "module_state": true,
      "shared_preferences": true,
      "reports_history": true,
      "plant_library": true,
      "media_content": true,
      "component_registry": true,
      "software_versions": true
    }
  },
  "component_field_options": {
    "component_kind": ["sensor", "actuator"],
    "pinout": ["TBD", "ESP32 GPIO TBD"]
  }
}
```

Если `preferred_mode = auto`, backend/client нормализуют все
`selected_domains` в `true`. Если пользователь вручную меняет любой пункт и
выбран не весь список, UI переводит `preferred_mode` в `manual_review`.
`media_content` включает фото, видео, аудио и gallery reports.
`software_versions` в первом рабочем варианте сравнивает версии RPi, ESP и
Web UI, без попытки выдавать доменные версии там, где нет truthful scan.
`component_field_options` используется как список подсказок для всех полей
того же инженерного типа.

Settings UI применяет изменения optimistic-first: клиент сразу обновляет
локальную модель и внешний вид, а `POST /api/v1/settings` выполняется
debounce/background. Backend должен быть идемпотентным к частым частичным
изменениям одной durable settings-модели.

## Platform Registry And Constructor

`GET /api/v1/platform/registry` возвращает host-side JSON-реестр
`platform_registry.v1`, где hardware modules, components, assignments и
templates разделены явно.

`POST /api/v1/platform/registry/constructor` принимает draft из modal wizard
`Settings > Constructor` и создаёт/обновляет записи модуля, компонента и связи
между ними. Endpoint не должен требовать подключённого железа: новые записи
могут быть `simulated` или `not_detected`, пока runtime-проверки не добавлены.

Пример Cat Feeder фиксируется через датчик движения, а не через датчик
освещённости: motion sensor будит камеру, после чего видеоидентификация и
событие запроса могут уведомить владельца или запустить выдачу корма.

## Host Path Actions

`POST /api/v1/host/open?target={whitelisted_target}` открывает папку на host,
где запущен backend. Это не viewer-side file open. Endpoint обязан принимать
только whitelisted target ids из snapshot storage/runtime paths.

```json
{
  "command": "host_open",
  "accepted": true,
  "target": "content_root",
  "path": "/opt/smart-platform/content"
}
```

`POST /api/v1/content/cleanup?target={whitelisted_target}&confirm=0|1`
используется storage cards в `Settings`:

- `confirm=0` возвращает preview по файлам, папкам и байтам;
- `confirm=1` удаляет содержимое выбранного slice после подтверждения в UI;
- endpoint обязан отказать, если target не cleanup-enabled, не находится внутри
  `content_root`, равен самому `content_root` или указывает на project/runtime root;
- удаляется содержимое директории, а не сама директория target.

```json
{
  "command": "content_cleanup",
  "accepted": true,
  "preview": true,
  "target": "audio",
  "path": "/opt/smart-platform/content/audio",
  "file_count": 12,
  "dir_count": 2,
  "total_bytes": 73400320
}
```

## Turret Runtime Snapshot

На стороне `Raspberry Pi` турельный UI и sync теперь работают не с прямыми флагами модулей,
а через отдельный runtime-слой.

```json
{
  "active_mode": "automatic",
  "automation_ready": true,
  "target_locked": false,
  "vision_tracking": false,
  "service_session_active": false,
  "interlocks": {
    "emergency_latched": false,
    "fault_latched": false,
    "fault_reason": "none"
  },
  "subsystems": [
    {
      "id": "motion",
      "title": "Motion",
      "kind": "actuator",
      "enabled": false,
      "state": "online",
      "block_reason": "none"
    },
    {
      "id": "vision",
      "title": "Vision Pipeline",
      "kind": "sensor",
      "enabled": true,
      "state": "online",
      "block_reason": "none"
    }
  ]
}
```

## Turret Runtime Endpoints

- `GET /api/v1/turret/status`
- `GET /api/v1/turret/runtime`
- `GET /api/v1/turret/events`
- `GET /api/v1/turret/drivers`
- `GET /api/v1/turret/scenarios`
- `GET /api/v1/turret/captures`
- `POST /api/v1/turret/runtime/mode`
- `POST /api/v1/turret/runtime/subsystem`
- `POST /api/v1/turret/runtime/flag`
- `POST /api/v1/turret/runtime/interlock`
- `POST /api/v1/turret/scenarios/run`
- `POST /api/v1/turret/capture`

`POST /api/v1/turret/capture` records a Manual FPV media artifact before the real
camera transport is wired. `kind=photo&phase=photo` creates a Gallery photo
metadata artifact. `kind=video&phase=video_start` creates a Video metadata
artifact with `status=recording`; `kind=video&phase=video_stop&capture_id=...`
finalizes it with `duration_ms`. Each accepted capture also writes a
`media_capture` report entry so Gallery can show the operator history.

Manual FPV video UX uses `turret_policies.max_recording_seconds` from
`GET /api/v1/settings` as the browser-side auto-stop limit. The setting is
normalized to `30` seconds by default, clamped to a minimum of `5` seconds and a
maximum of `36000` seconds.
`turret_policies.allow_auto_capture` controls whether the shared photo/video
capture button remains available in Automatic FPV. Manual weapon, valve, and
aim controls stay hidden in Automatic regardless of that policy.

## Platform Log Snapshot

```json
{
  "count": 14,
  "limit": 18,
  "entries": [
    {
      "event_id": "platform-00014",
      "timestamp_ms": 312,
      "source": "turret_scenarios",
      "level": "info",
      "type": "scenario_finished",
      "message": "turret service scenario finished",
      "details": {
        "scenario_id": "service_safe_idle",
        "accepted": true,
        "failed_steps": []
      }
    }
  ]
}
```

## Turret Event Log Snapshot

```json
{
  "count": 3,
  "limit": 40,
  "entries": [
    {
      "event_id": "turret-00003",
      "timestamp_ms": 84,
      "level": "info",
      "type": "runtime_subsystem_changed",
      "message": "subsystem state updated",
      "details": {
        "subsystem_id": "vision",
        "enabled": true
      }
    }
  ]
}
```

## Turret Driver Bindings Snapshot

```json
{
  "count": 5,
  "bindings": [
    {
      "id": "strobe",
      "title": "Strobe",
      "driver_kind": "stub",
      "binding_state": "unbound",
      "hardware_ready": false,
      "last_apply_ms": 120,
      "last_enabled": false,
      "last_runtime_state": "online",
      "last_result": "deferred",
      "note": "awaiting turret strobe wiring"
    }
  ]
}
```

## Turret Scenario Catalog Snapshot

```json
{
  "count": 3,
  "scenarios": [
    {
      "id": "service_safe_idle",
      "title": "Service Safe Idle",
      "category": "service",
      "description": "Переводит turret runtime в безопасный сервисный idle и очищает interlock."
    }
  ]
}
```

## Shared Log Sync Endpoints

- `GET /api/v1/logs`
- `POST /api/v1/sync/logs/push`

`GET /api/v1/logs` теперь считается общим endpoint узла. Он должен возвращать как локальные записи,
так и зеркалированные записи peer-узла, если они уже приняты через sync-контур.

`POST /api/v1/sync/logs/push` используется для мягкого зеркалирования событий между узлами.
Запрос обязан нести идентификатор исходного узла и исходного события, чтобы принимающая сторона
могла дедуплицировать повторные push-записи.

## Shared Platform Log Snapshot

```json
{
  "count": 18,
  "limit": 18,
  "entries": [
    {
      "event_id": "platform-00018",
      "origin_node": "rpi-turret",
      "origin_event_id": "platform-00007",
      "mirrored": true,
      "timestamp_ms": 812,
      "source": "turret_runtime",
      "level": "info",
      "type": "runtime_mode_changed",
      "message": "turret runtime mode updated",
      "details": {
        "active_mode": "laboratory"
      }
    },
    {
      "event_id": "platform-00019",
      "origin_node": "esp32-main",
      "origin_event_id": "platform-00019",
      "mirrored": false,
      "timestamp_ms": 845,
      "source": "sync_core",
      "level": "info",
      "type": "peer_heartbeat",
      "message": "peer heartbeat accepted",
      "details": {
        "peer": "rpi-turret",
        "sync_ready": true
      }
    }
  ]
}
```

## Reports Feed Snapshot

- `GET /api/v1/reports`

This endpoint is the current user-facing baseline for `Gallery > Reports`.
It is not yet the final persistent reports model. For now it is a normalized feed
built on top of the shared platform log so the shell and gallery can move to the
canonical `Reports` vocabulary before the richer storage layer is finished.

Current query filters:

- `surface`
- `entry_type`
- `severity`
- `origin_node`

```json
{
  "schema_version": "reports-feed.v1",
  "source_kind": "platform_log_baseline",
  "count": 18,
  "limit": 20,
  "filters": {
    "surface": "laboratory"
  },
  "summary": {
    "warning_count": 1,
    "error_count": 0,
    "surfaces": {
      "laboratory": 6,
      "system": 2
    },
    "entry_types": {
      "scenario": 2,
      "sync": 1,
      "action": 5
    },
    "origin_nodes": {
      "rpi-turret": 6
    }
  },
  "entries": [
    {
      "report_id": "report-platform-00018",
      "event_id": "platform-00018",
      "timestamp_ms": 812,
      "origin_node": "rpi-turret",
      "mirrored": true,
      "source": "turret_runtime",
      "entry_type": "mode_change",
      "source_surface": "turret",
      "source_mode": "laboratory",
      "module_id": "turret_bridge",
      "title": "Runtime Mode Changed",
      "message": "turret runtime mode updated",
      "severity": "info",
      "result": "recorded",
      "duration_ms": null,
      "parameters": {
        "active_mode": "laboratory"
      },
      "raw_type": "runtime_mode_changed"
    }
  ]
}
```

## Testcase Report Capture

- `POST /api/v1/reports/testcase`

This is the current minimal write path for hardware bring-up evidence.
It does not create a separate testcase subsystem yet.
It writes one typed entry into the same `Gallery > Reports` feed.

Required query parameters:

- `case_id`
- `module_id`
- `result=pass|fail|warn`

Optional query parameters:

- `board`
- `note`

Minimal response:

```json
{
  "command": "reports_testcase",
  "accepted": true,
  "message": "testcase result recorded"
}
```

Recorded entries currently appear in the reports feed as:

- `entry_type = testcase`
- `source_surface = laboratory`
- `raw_type = testcase_result_recorded`

and carry typed parameters such as:

- `case_id`
- `module_id`
- `board`
- `test_result`
- `note`

## Operator Note Capture

- `POST /api/v1/reports/note`

This is the minimal typed note path for bring-up sessions.
It keeps operator remarks in the same chronological feed instead of creating a
separate notes surface.

Required query parameters:

- `note`
- `module_id`

Optional query parameters:

- `board`
- `case_id`

Minimal response:

```json
{
  "command": "reports_note",
  "accepted": true,
  "message": "operator note recorded"
}
```

Recorded entries currently appear in the reports feed as:

- `entry_type = operator_note`
- `source_surface = laboratory`
- `raw_type = operator_note`

## Laboratory Readiness Snapshot

- `GET /api/v1/laboratory/readiness`

This endpoint is the current coordination baseline for sequential hardware bring-up.
It does not replace testcase execution or final reports. It answers a smaller question:
is the shell in a sane state for the next board/module step, and what should happen next?

```json
{
  "schema_version": "laboratory-readiness.v1",
  "overall_status": "attention",
  "summary": "Testing can continue with caution. Attention is required for: Persistent reports history is available, Peer owner link is ready for ESP32-owned tests",
  "active_mode": "manual",
  "reports_source_kind": "platform_log_baseline",
  "next_action": {
    "kind": "preflight",
    "id": "reports_archive",
    "title": "Persistent reports history is available",
    "status": "attention",
    "action": "Use Raspberry Pi with content storage enabled so each test pass survives restart."
  },
  "preflight": [
    {
      "id": "local_shell_ready",
      "title": "Coordinator shell is reachable",
      "status": "ready",
      "summary": "Local shell is ready for the next test step.",
      "action": "Open the current shell and confirm the local node is reachable before wiring the next board."
    }
  ],
  "bringup_sequence": [
    {
      "id": "esp32_strobe_bench",
      "title": "ESP32 / Strobe Bench",
      "owner_scope": "io_node",
      "route": "/service?tool=strobe_bench",
      "status": "blocked",
      "summary": "Short pulse and preset bring-up for the bench strobe should happen before integrated turret tests.",
      "action": "Begin with the lowest-energy pulse testcase and keep the hardware emergency chain available."
    }
  ]
}
```

## Federated Shell Heartbeat Fields

В heartbeat узла теперь допускается поле:

- `shell_base_url`

Пример:

```json
{
  "node_id": "rpi-turret",
  "shell_base_url": "http://raspberrypi.local:8080",
  "wifi_ready": "1",
  "shell_ready": "1",
  "sync_ready": "1",
  "reported_mode": "manual"
}
```

## Federated Route Info

`GET /api/v1/federation/route?module_id=strobe`

Минимальный ответ:

```json
{
  "module_id": "strobe",
  "module_found": true,
  "owner": "rpi",
  "owner_node_id": "rpi-turret",
  "owner_available": true,
  "state": "online",
  "block_reason": "none",
  "canonical_path": "/turret#strobe",
  "canonical_url": "http://raspberrypi.local:8080/turret#strobe",
  "federated_access": "peer_owner_available",
  "current_shell_node_id": "esp32-main",
  "current_shell_base_url": "http://192.168.4.1"
}
```

Это endpoint мягкого handoff-этапа.
На нем shell еще не делает полный reverse-proxy, но уже умеет:

- понять, найден ли модуль;
- проверить, доступен ли owner;
- показать canonical owner page;
- безопасно увести пользователя к владельцу peer-owned модуля.
