# Shell Snapshot Schema

Этот документ фиксирует следующий шаг после `System Shell` class map.

Его задача:

- определить один минимальный shell-level snapshot;
- прекратить сборку shell-картины разрозненными кусками;
- дать опору для будущего `ShellSnapshotFacade`.

## 1. Зачем нужен отдельный shell snapshot

Сейчас shell получает данные из нескольких мест сразу:

- `system snapshot`;
- `module registry`;
- `content status`;
- `sync status`;
- `logs` / activity backend;
- частично из продуктовых runtime endpoint.

Это работает, но плохо управляется.

Проблема не только в количестве endpoint, а в том, что shell сам вынужден
собирать смысл из разрозненных частей.

`Shell Snapshot` нужен, чтобы:

- `Главная` страница не думала о внутреннем устройстве runtime;
- shell-level diagnostics summary не собирались из случайных кусочков;
- обе стороны (`ESP32` и `Raspberry Pi`) показывали одну и ту же картину;
- transport entrypoint перестал быть местом, где вручную сшивается вся shell-логика.

## 2. Что должен покрывать shell snapshot

Минимально он должен быть достаточен для:

1. `Главная`
2. shell-level status summaries
3. shell-level навигации
4. owner-aware handoff
5. входа в `Gallery`
6. краткого activity summary

Важно:
- это не замена всех endpoint продукта;
- это не полный runtime dump;
- это не transport-протокол для команд модулей.

## 3. Минимальная структура `Shell Snapshot v1`

```json
{
  "schema_version": "shell-snapshot.v1",
  "generated_by": "esp32-main",
  "generated_at_ms": 12345,
  "current_shell": {
    "node_id": "esp32-main",
    "node_type": "esp32",
    "shell_base_url": "http://192.168.4.1",
    "ui_shell_version": "0.1.0",
    "active_mode": "manual",
    "service_mode": false
  },
  "nodes": {
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
  },
  "module_cards": [
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
    },
    {
      "id": "turret_bridge",
      "title": "Turret",
      "product_block": "turret",
      "owner_node_id": "rpi-turret",
      "owner_available": true,
      "state": "online",
      "block_reason": "none",
      "canonical_path": "/turret",
      "canonical_url": "http://raspberrypi.local:8080/turret",
      "route_mode": "handoff",
      "summary": "Peer-owned turret page is available"
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
}
```

## 4. Что в snapshot должно быть всегда

Обязательные поля `v1`:

- `schema_version`
- `generated_by`
- `generated_at_ms`
- `current_shell`
- `nodes.current`
- `nodes.peer`
- `module_cards`
- `navigation`
- `summaries.faults`
- `summaries.diagnostics`
- `summaries.activity`
- `summaries.content`

Текущий software baseline при этом может временно продолжать отдавать transitional routes вроде `/content` и `/#diagnostics`,
но product target navigation должна мыслиться через `Gallery` и `Laboratory`.

При этом допустим временный compatibility-layer:

- `navigation.service`
- `navigation.content`
- `navigation.diagnostics`
- `navigation.logs`
- `navigation.service_test`

Но новые shell surfaces и tests должны постепенно переключаться на:

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
- показывать владельца;
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

Важно:

- `service_test` в contract можно сохранять как internal engineering alias;
- user-facing label для него в shell должен быть `Laboratory`.

## 7. Отношение к текущим endpoint

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

## 8. Первый порядок внедрения

1. Сначала описать contract и skeleton facade.
2. Затем собрать `Shell Snapshot v1` на `ESP32`.
3. Затем собрать такой же `Shell Snapshot v1` на `Raspberry Pi`.
4. После этого перевести на него:
   - `Главную`
   - shell-level summaries
5. Только затем решать, нужно ли подтягивать на него `Gallery > Reports` и `Content Storage` глубже.

## 9. Связанные артефакты

- [31_system_shell_class_map.md](31_system_shell_class_map.md)
- [32_current_shell_role_mapping.md](32_current_shell_role_mapping.md)
- [../shared_contracts/shell_snapshot_contract.md](../shared_contracts/shell_snapshot_contract.md)
- [../skeletons/shell_snapshot_facade_esp32_blueprint.h](../skeletons/shell_snapshot_facade_esp32_blueprint.h)
- [../skeletons/shell_snapshot_facade_raspberry_pi_blueprint.py](../skeletons/shell_snapshot_facade_raspberry_pi_blueprint.py)
