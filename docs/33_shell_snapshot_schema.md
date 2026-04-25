# Shell Snapshot Schema

Этот документ фиксирует shell-level snapshot как общий truthful state source
для `Home`, `Settings`, shell summaries и owner-aware navigation.

Его задача:

- определить один минимальный shell-level snapshot;
- прекратить сборку shell-картины разрозненными кусками;
- отделить `runtime host`, `current viewer`, `platform nodes`, `sync` и `storage`;
- дать опору для `ShellSnapshotFacade`.

## 1. Зачем нужен отдельный shell snapshot

Сейчас shell может получать данные из нескольких мест сразу:

- `system snapshot`;
- `module registry`;
- `content status`;
- `sync status`;
- `logs` / activity backend;
- частично из продуктовых runtime endpoint.

Это работает, но заставляет client-side shell собирать смысл вручную.

`Shell Snapshot` нужен, чтобы:

- `Главная` страница не домысливала runtime model;
- `Settings` не склеивал truthful state из четырех разных endpoint;
- обе стороны (`ESP32` и `Raspberry Pi`) показывали одну и ту же картину;
- `desktop_smoke` не притворялся `Raspberry Pi online`;
- owner-aware handoff и shell summaries жили на одном contract.

## 2. Что должен покрывать shell snapshot

Минимально он должен быть достаточен для:

1. `Главная`
2. shell-level status summaries
3. shell-level навигации
4. owner-aware handoff
5. входа в `Gallery`
6. краткого activity summary
7. truthful state модели страницы `Settings`

Важно:

- это не замена всех endpoint продукта;
- это не полный runtime dump;
- это не transport-протокол для команд модулей.

## 3. Минимальная структура `Shell Snapshot v1`

```json
{
  "schema_version": "shell-snapshot.v1",
  "generated_by": "rpi-turret",
  "generated_at_ms": 12345,
  "current_shell": {
    "node_id": "rpi-turret",
    "node_type": "raspberry_pi",
    "shell_base_url": "http://192.168.1.227:8091",
    "ui_shell_version": "0.1.0",
    "active_mode": "manual",
    "service_mode": false,
    "runtime_profile": "desktop_smoke"
  },
  "runtime": {
    "profile": "desktop_smoke",
    "host": {
      "kind": "desktop_host",
      "title": "Windows desktop host",
      "platform": "Windows",
      "is_owner_device": false,
      "summary": "The Raspberry Pi shell is currently served from a desktop host."
    },
    "viewer_count": 1,
    "viewer_hint": "The current browser client is resolved by matching the local viewer_id against viewers[]."
  },
  "viewers": [
    {
      "viewer_id": "viewer-123",
      "viewer_kind": "desktop",
      "title": "Desktop",
      "value": "PC",
      "page": "/settings",
      "address": "127.0.0.1"
    }
  ],
  "nodes": {
    "current": {
      "node_id": "rpi-turret",
      "title": "Raspberry Pi",
      "reachable": false,
      "health": "offline",
      "wifi_ready": false,
      "shell_ready": false,
      "sync_ready": false,
      "summary": "Owner board is offline. The shell is running from a desktop host."
    },
    "peer": {
      "node_id": "esp32-main",
      "title": "ESP32",
      "reachable": false,
      "health": "offline",
      "wifi_ready": false,
      "shell_ready": false,
      "sync_ready": false,
      "reported_mode": "manual",
      "shell_base_url": "http://192.168.4.1",
      "summary": "Peer owner is offline"
    }
  },
  "sync": {
    "enabled": false,
    "state": "local_only",
    "peer_reachable": false,
    "peer_sync_ready": false,
    "last_sync_ms": 0,
    "last_error": "",
    "summary": "Optional background sync is disabled on this host."
  },
  "storage": {
    "storage_kind": "filesystem",
    "content_root": "C:/SmartPlatform/raspberry_pi/content",
    "content_root_state": "ready",
    "paths": [
      {
        "id": "content_root",
        "title": "Content Root",
        "path": "C:/SmartPlatform/raspberry_pi/content",
        "state": "ready",
        "exists": true,
        "file_count": 124,
        "copy_supported": true,
        "open_supported": true
      }
    ]
  },
  "module_cards": [
    {
      "id": "irrigation",
      "title": "Irrigation",
      "product_block": "irrigation",
      "owner_scope": "esp32",
      "owner_title": "ESP32",
      "owner_node_id": "esp32-main",
      "owner_available": false,
      "state": "locked",
      "block_reason": "owner_unavailable",
      "canonical_path": "/irrigation",
      "canonical_url": "",
      "route_mode": "blocked",
      "summary": "Peer owner is not available"
    },
    {
      "id": "turret_bridge",
      "title": "Turret",
      "product_block": "turret",
      "owner_scope": "rpi",
      "owner_title": "Raspberry Pi",
      "owner_node_id": "rpi-turret",
      "owner_available": false,
      "state": "online",
      "block_reason": "none",
      "canonical_path": "/turret",
      "canonical_url": "http://192.168.1.227:8091/turret",
      "route_mode": "local",
      "summary": "Preview path from desktop host; owner device is offline"
    }
  ],
  "navigation": {
    "home": "/",
    "gallery": {
      "path": "/gallery",
      "route_mode": "virtual",
      "owner_scope": "shared",
      "tabs": ["plants", "media", "reports"],
      "default_tab": "reports"
    },
    "laboratory": {
      "path": "/service",
      "user_facing_title": "Laboratory",
      "internal_stage_name": "Service/Test v1"
    },
    "settings": "/settings"
  },
  "summaries": {
    "faults": {
      "has_fault": false,
      "has_degraded": true,
      "message": "Some modules are degraded or blocked"
    },
    "diagnostics": {
      "sync_state": "local_only",
      "ownership_summary": "ESP32 owns irrigation, Raspberry Pi owns turret",
      "content_ready": true
    },
    "activity": {
      "recent_visible": 42,
      "warning_count": 1,
      "error_count": 0,
      "primary_viewer": "gallery.reports"
    },
    "content": {
      "storage_kind": "filesystem",
      "ready": true,
      "libraries_ready": true
    }
  }
}
```

## 4. Что в snapshot должно быть всегда

Обязательные поля `v1`:

- `schema_version`
- `generated_by`
- `generated_at_ms`
- `current_shell`
- `runtime`
- `viewers`
- `nodes.current`
- `nodes.peer`
- `sync`
- `storage`
- `module_cards`
- `navigation`
- `summaries.faults`
- `summaries.diagnostics`
- `summaries.activity`
- `summaries.content`

Текущий software baseline при этом может временно продолжать отдавать
compatibility keys вроде `/content` и `/#diagnostics`, но новые shell surfaces
и `Settings` должны мыслиться через:

- `runtime`
- `viewers`
- `nodes`
- `sync`
- `storage`
- `navigation.gallery`
- `navigation.laboratory`
- `navigation.settings`
- `summaries.activity`

## 5. Что не нужно тащить в snapshot

Не нужно включать:

- полный журнал событий;
- все записи `/logs`;
- весь mixed feed `Gallery > Reports`;
- полный turret runtime;
- все настройки модулей;
- полный список capability флагов низкого уровня;
- бинарные данные или тяжелый контент.

Для этого остаются отдельные endpoint.

## 6. Правила для `module_cards`

`module_cards` — это shell-friendly слой, а не raw runtime dump.

Каждая карточка должна:

- быть привязана к одному продуктовому блоку;
- иметь понятный `title`;
- показывать ожидаемого владельца;
- отделять `owner_scope` от текущего runtime host;
- показывать состояние;
- давать route semantics: `local`, `handoff`, `blocked`;
- иметь краткое человеческое `summary`.

### Допустимые `route_mode`

- `local`
- `handoff`
- `blocked`

### Допустимые `product_block`

- `system_shell`
- `irrigation`
- `turret`
- `service_test`

### Допустимые `owner_scope`

- `esp32`
- `rpi`
- `shared`

Важно:

- `service_test` в contract можно сохранять как internal engineering alias;
- user-facing label для него в shell должен быть `Laboratory`;
- `owner_scope = shared` не должен маскироваться под ownership конкретной платой;
- в `desktop_smoke` preview-path может оставаться `local`, но `owner_available`
  и `summary` обязаны честно отражать отсутствие реального owner-device.

## 7. Статусы верхнего уровня

### Для `nodes[*].health`

- `online`
- `degraded`
- `locked`
- `fault`
- `offline`

### Для `sync.state`

- `local_only`
- `remote_unavailable`
- `never_synced`
- `pending`
- `ready`
- `error`

### Для `storage.paths[*].state`

- `ready`
- `missing`
- `not_configured`
- `unavailable`

## 8. Отношение к текущим endpoint

`Shell Snapshot v1` не заменяет:

- `/api/v1/system`
- `/api/v1/modules`
- `/api/v1/logs`
- `/api/v1/content/status`
- `/api/v1/sync/state`

Но он может быть собран из них внутри `ShellSnapshotFacade`.

То есть shell получает:

- один snapshot для общей картины;
- и специализированные endpoint только там, где нужна глубина.

Для страницы `Settings` целевая модель теперь такая:

- truthful runtime / host / viewer / node / sync / storage state приходит из
  `GET /api/v1/shell/snapshot`;
- shared preferences и policy baselines приходят из `GET /api/v1/settings`;
- `content/status` и `/api/v1/sync/state` остаются internal/service surfaces,
  а не главным способом собрать смысл на клиенте.

## 9. Первый порядок внедрения

1. Сначала описать contract и skeleton facade.
2. Затем собрать `Shell Snapshot v1` на `ESP32`.
3. Затем собрать такой же `Shell Snapshot v1` на `Raspberry Pi`.
4. После этого перевести на него:
   - `Главную`
   - `Settings`
   - shell-level summaries
5. Только затем углубляться в отдельные diagnostics pages и richer module UIs.

## 10. Связанные артефакты

- [31_system_shell_class_map.md](31_system_shell_class_map.md)
- [32_current_shell_role_mapping.md](32_current_shell_role_mapping.md)
- [../shared_contracts/shell_snapshot_contract.md](../shared_contracts/shell_snapshot_contract.md)
- [../skeletons/shell_snapshot_facade_esp32_blueprint.h](../skeletons/shell_snapshot_facade_esp32_blueprint.h)
- [../skeletons/shell_snapshot_facade_raspberry_pi_blueprint.py](../skeletons/shell_snapshot_facade_raspberry_pi_blueprint.py)
