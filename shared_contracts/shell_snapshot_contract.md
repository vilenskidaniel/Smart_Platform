# Shell Snapshot Contract

Этот документ описывает технический контракт `Shell Snapshot v1`.

Важно:

- это shell-level contract;
- он не заменяет `system snapshot` и другие runtime endpoint;
- он нужен специально для `System Shell v1`.

Базовый endpoint для него:

- `GET /api/v1/shell/snapshot`

## Snapshot Envelope

```json
{
  "schema_version": "shell-snapshot.v1",
  "generated_by": "esp32-main",
  "generated_at_ms": 12345,
  "current_shell": {},
  "nodes": {},
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
  "service_mode": false
}
```

## `nodes`

```json
{
  "current": {
    "node_id": "esp32-main",
    "title": "ESP32",
    "reachable": true,
    "health": "online",
    "wifi_ready": true,
    "shell_ready": true,
    "sync_ready": true,
    "summary": "Irrigation owner available"
  },
  "peer": {
    "node_id": "rpi-turret",
    "title": "Raspberry Pi",
    "reachable": true,
    "health": "online",
    "wifi_ready": true,
    "shell_ready": true,
    "sync_ready": true,
    "reported_mode": "manual",
    "shell_base_url": "http://raspberrypi.local:8080",
    "summary": "Turret owner available"
  }
}
```

### Допустимые `health`

- `online`
- `degraded`
- `locked`
- `fault`
- `offline`

## `module_cards`

```json
[
  {
    "id": "irrigation",
    "title": "Irrigation",
    "product_block": "irrigation",
    "owner_node_id": "esp32-main",
    "owner_available": true,
    "state": "online",
    "block_reason": "none",
    "canonical_path": "/irrigation",
    "canonical_url": "http://192.168.4.1/irrigation",
    "route_mode": "local",
    "summary": "Local irrigation owner is ready"
  }
]
```

### Допустимые `product_block`

- `system_shell`
- `irrigation`
- `turret`
- `service_test`

Важно:

- `service_test` можно сохранять как internal engineering alias;
- user-facing label для него в shell должен быть `Laboratory`.

### Допустимые `route_mode`

- `local`
- `handoff`
- `blocked`

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

- текущий software baseline может временно продолжать отдавать transitional routes вроде `/content` и `/#diagnostics`;
- текущий software baseline может временно сохранять compatibility keys:
  - `service`
  - `content`
  - `diagnostics`
  - `logs`
  - `service_test`
- product target navigation должна мыслиться через `Gallery` и `Laboratory`;
- `Gallery` может быть shared virtual section без одного owner, поэтому она живет в `navigation`, а не обязана выглядеть как peer-owned `module_card`.
- deep activity/history viewer должен открываться через `Gallery > Reports`, а не через отдельную product-page `Logs`.
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
    "message": "One peer-owned block is degraded"
  },
  "diagnostics": {
    "sync_state": "ready",
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
    "storage_kind": "sd",
    "ready": true,
    "libraries_ready": true
  }
}
```

## Минимальные правила

1. Snapshot должен быть пригоден для `Главной`, shell-level diagnostics summary и входа в `Gallery` / `Laboratory` без сборки
   данных из пяти разных endpoint на клиенте.
2. Snapshot не должен содержать тяжелые данные, полные логи или полные runtime
   dump модулей.
3. Peer-owned модуль в shell snapshot обязан иметь:
   - `owner_node_id`
   - `owner_available`
   - `canonical_url`
   - `route_mode`
4. Если модуль недоступен, shell snapshot должен объяснять это через
   `state`, `block_reason` и `summary`.
5. Для user-facing истории действий snapshot должен давать только краткую activity summary и pointer на `Gallery > Reports`,
   а не сам полный mixed feed отчетов.

## Связанные документы

- [../docs/26_v1_product_spec.md](../docs/26_v1_product_spec.md)
- [../docs/27_system_shell_v1_spec.md](../docs/27_system_shell_v1_spec.md)
- [../docs/33_shell_snapshot_schema.md](../docs/33_shell_snapshot_schema.md)
