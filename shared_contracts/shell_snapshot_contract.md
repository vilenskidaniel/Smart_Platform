# Shell Snapshot Contract

Этот документ описывает технический контракт `Shell Snapshot v1`.

Важно:

- это shell-level contract;
- он не заменяет `system snapshot` и другие runtime endpoint;
- он нужен специально для `System Shell v1` и truthful `Settings`.

Базовый endpoint для него:

- `GET /api/v1/shell/snapshot`

## Snapshot Envelope

```json
{
  "schema_version": "shell-snapshot.v1",
  "generated_by": "esp32-main",
  "generated_at_ms": 12345,
  "current_shell": {},
  "runtime": {},
  "viewers": [],
  "nodes": {},
  "sync": {},
  "storage": {},
  "module_cards": [],
  "navigation": {},
  "summaries": {}
}
```

## `current_shell`

```json
{
  "node_id": "esp32-main",
  "node_type": "esp32",
  "shell_base_url": "http://192.168.4.1",
  "ui_shell_version": "0.1.0",
  "active_mode": "manual",
  "service_mode": false,
  "runtime_profile": "owner_device"
}
```

`current_shell` описывает shell-surface, а не physical host-machine.

## `runtime`

```json
{
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
}
```

Это отдельный слой от `current_shell` и `nodes`.
Именно он объясняет, где реально поднят backend/server.

## `viewers`

```json
[
  {
    "viewer_id": "viewer-123",
    "viewer_kind": "desktop",
    "title": "Desktop",
    "value": "PC",
    "page": "/settings",
    "address": "127.0.0.1"
  }
]
```

Snapshot не обязан публиковать один заранее выбранный `current_viewer`,
потому что это client-relative truth. Shell должен:

- читать массив `viewers`;
- сопоставлять локальный `viewer_id`;
- на этой основе вычислять `current browser client`.

## `nodes`

```json
{
  "current": {
    "node_id": "esp32-main",
    "title": "ESP32",
    "reachable": false,
    "health": "offline",
    "wifi_ready": false,
    "shell_ready": false,
    "sync_ready": false,
    "summary": "Owner board is offline. The shell is running from a desktop host."
  },
  "peer": {
    "node_id": "rpi-turret",
    "title": "Raspberry Pi",
    "reachable": false,
    "health": "offline",
    "wifi_ready": false,
    "shell_ready": false,
    "sync_ready": false,
    "reported_mode": "manual",
    "shell_base_url": "http://raspberrypi.local:8080",
    "summary": "Peer owner is offline"
  }
}
```

Важно:

- `nodes` описывает physical platform nodes;
- `runtime.host` описывает host-machine;
- в `desktop_smoke` обе платы могут быть `offline`, даже если shell server жив.

### Допустимые `health`

- `online`
- `degraded`
- `locked`
- `fault`
- `offline`

## `sync`

```json
{
  "enabled": false,
  "state": "local_only",
  "peer_reachable": false,
  "peer_sync_ready": false,
  "last_sync_ms": 0,
  "last_error": "",
  "summary": "Optional background sync is disabled on this host."
}
```

### Допустимые `state`

- `local_only`
- `remote_unavailable`
- `never_synced`
- `pending`
- `ready`
- `error`

## `storage`

```json
{
  "storage_kind": "filesystem",
  "content_root": "/opt/smart-platform/content",
  "content_root_state": "ready",
  "paths": [
    {
      "id": "content_root",
      "title": "Content Root",
      "path": "/opt/smart-platform/content",
      "state": "ready",
      "exists": true,
      "file_count": 124,
      "copy_supported": true,
      "open_supported": true
    }
  ]
}
```

### Допустимые `storage.paths[*].state`

- `ready`
- `missing`
- `not_configured`
- `unavailable`

## `module_cards`

```json
[
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
  }
]
```

### Допустимые `product_block`

- `system_shell`
- `irrigation`
- `turret`
- `service_test`

### Допустимые `owner_scope`

- `esp32`
- `rpi`
- `shared`

### Допустимые `route_mode`

- `local`
- `handoff`
- `blocked`

Важно:

- `service_test` можно сохранять как internal engineering alias;
- user-facing label для него в shell должен быть `Laboratory`;
- `owner_scope = shared` не должен маскироваться как ownership конкретной платой;
- в `desktop_smoke` preview-path может оставаться `local`, но `owner_available`
  и `summary` обязаны честно отражать отсутствие реального owner-device.

## `navigation`

```json
{
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
}
```

Важно:

- текущий software baseline может временно продолжать отдавать transitional routes;
- client-side shell logic должна предпочитать canonical keys:
  - `navigation.gallery`
  - `navigation.laboratory`
  - `navigation.settings`
  - `summaries.activity`

## `summaries`

```json
{
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
```

## Минимальные правила

1. Snapshot должен быть пригоден для `Главной`, shell-level diagnostics summary,
   owner-aware navigation и truthful `Settings` без сборки смысла из пяти endpoint.
2. Snapshot обязан отдельно различать:
   - shell surface;
   - runtime host;
   - current browser viewers;
   - physical platform nodes.
3. В `desktop_smoke` snapshot не должен создавать ложное состояние
   `Raspberry Pi online`, если физическая плата не подключена.
4. Для `Settings` snapshot должен отдавать достаточный truthful state по
   `runtime`, `viewers`, `nodes`, `sync` и `storage`.
5. Snapshot не должен содержать тяжелые данные, полные логи или полные runtime
   dump модулей.
6. Peer-owned модуль в shell snapshot обязан иметь:
   - `owner_node_id`
   - `owner_available`
   - `canonical_url`
   - `route_mode`
7. Если модуль недоступен, shell snapshot должен объяснять это через
   `state`, `block_reason` и `summary`.
8. Для user-facing истории действий snapshot должен давать только краткую
   activity summary и pointer на `Gallery > Reports`, а не сам mixed feed отчетов.

## Связанные документы

- [../docs/26_v1_product_spec.md](../docs/26_v1_product_spec.md)
- [../docs/27_system_shell_v1_spec.md](../docs/27_system_shell_v1_spec.md)
- [../docs/33_shell_snapshot_schema.md](../docs/33_shell_snapshot_schema.md)
