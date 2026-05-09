# 15. Platform Services And Shared Content

## Роль Файла

Этот файл должен описывать общие сервисы и shared content layers, которые не являются отдельными продуктами, но определяют работу всей платформы.

## Статус

- текущий статус: `active draft`
- этот файл задает новый active canon для platform services, shell snapshot vocabulary и shared content boundary; donor docs ниже остаются contract/detail residue

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `shared_contracts/shell_snapshot_contract.md` остается active companion contract for shell snapshot vocabulary.

## Settled Truths

- platform services не должны маскироваться под product modules
- shared content layer должен быть описан отдельно от raw storage implementation

## Canon

### 1. Какие Есть Platform Services

`Platform services` - это общие инфраструктурные слои, которые обслуживают все product surfaces, но сами не являются отдельными пользовательскими продуктами.

К устойчивым platform services `v1` относятся:

1. `Shell Snapshot` как overview truth source для shell surfaces.
2. `Shell Navigation And Handoff` как слой owner-aware routing.
3. `Sync Core` как платформа обмена и continuity, а не модульная логика.
4. `Registry Service` как persistent identity and metadata layer.
5. `Storage And Shared Content Service` как mirrored-content and readiness layer.
6. `Activity And Reports Plumbing` как platform event/report path.
7. `Diagnostics Surfaces` как deep inspection layer.

Эти слои:

- влияют на `Home`, `Settings`, `Gallery`, `Laboratory` и module pages;
- не должны переименовываться в product modules;
- не должны прятаться внутри одной owner-page как будто это локальная логика одного модуля.

Current implementation detail may still use names like `ShellSnapshotFacade`, `ShellContentPresenter` or `ShellHttpAdapter`, but active canon here describes the stable service roles, not refactoring class names.

### 2. Shell Snapshot And Shared Runtime Truth

`Shell Snapshot` - это один truthful shell-level source для обзорной картины платформы.

Он нужен, чтобы:

- `Home` не домысливал runtime model;
- `Settings` не склеивал truthful state из нескольких unrelated endpoints;
- `Gallery` и `Laboratory` могли читать owner-aware shell context без дублирования transport logic;
- `ESP32` и `Raspberry Pi` baselines materialized the same shell truth even with different runtime adapters.

Минимальный scope `Shell Snapshot v1`:

- `current_shell`
- `runtime`
- `viewers`
- `nodes.current`
- `nodes.peer`
- `sync`
- `storage`
- `module_cards`
- `navigation`
- `summaries`

`Shell Snapshot` должен различать:

- runtime host;
- current viewer;
- platform nodes;
- sync state;
- storage overview;
- module cards and route modes;
- shell summaries.

Каноническая state vocabulary для module cards в shell-level truth:

- `online`
- `degraded`
- `blocked`
- `locked`
- `fault`

`offline` остается vocabulary для node/owner availability внутри `nodes.*`, `owner_available` и связанных `block_reason`/summary fields, а не отдельным module-card state.

`service` и другие engineering compatibility labels могут жить в legacy aliases, `product_block` mapping или `block_reason`, но не как `module_cards[*].state`.

Канонический baseline `block_reason` vocabulary:

- `none`
- `owner_unavailable`
- `peer_sync_pending`
- `safety_interlock`
- `module_fault`
- `service_session_active`
- `service_mode_required`
- `emergency_state`
- `module_offline`
- `unknown`

`Shell Snapshot` does not replace every specialized endpoint. It gives one overview truth, while deeper services remain available where needed.

### Historical `ESP32` Bootstrap Baseline

Ранний bring-up baseline полезно фиксировать отдельно, чтобы bootstrap logic не потерялся при cleanup donor-layer.

Для первого `ESP32`-side shell bootstrap baseline считалось нормой, что:

- локальный узел уже виден как `online` даже до полного peer-side handoff;
- локально доступны `shell`, `settings`, `logs`, `diagnostics` и `irrigation`;
- peer-owned contours вроде `turret_bridge` и `strobe` остаются видимыми, но стартуют в `locked` с причиной `owner_unavailable`;
- после появления `Raspberry Pi` heartbeat эти contours могут перейти в `degraded` или `online` только по мере подтверждения sync depth, а не просто по факту reachability.

Historical bring-up boundary этого этапа:

- уже считались обязательными перечисления состояний, node-health/module-descriptor types, локальный module registry и минимальный `system snapshot` debug output;
- еще не считались реализованными real web shell, real Wi-Fi/heartbeat exchange, full bidirectional sync, real irrigation/strobe module invocation и heavy auth/serialization layers.

Эту заметку нужно читать как historical bootstrap reference, а не как ограничение текущего `v1` scope.

### 3. Shared Content And Media Strategy

`Shared content layer` - это platform service for mirrored heavy content, reference media and gallery-backed artifacts.

Он должен оставаться отдельным от:

- raw storage implementation details;
- user-facing `Gallery` IA;
- `Laboratory` session evidence layer;
- module-specific runtime commands.

Общий logical content tree `v1`:

- `/assets`
- `/audio`
- `/animations`
- `/libraries`
- `/gallery`

Baseline today:

- lightweight shell pages stay available without heavy content;
- `ESP32` uses `LittleFS` for shell/fallback surfaces and `SD` for heavy mirrored content baseline;
- `Raspberry Pi` uses local filesystem content roots;
- both sides must understand the same logical paths even when physical backend differs.

Important boundary:

- user-facing content opens through `Gallery`;
- raw storage inspection stays in service diagnostics surfaces like `Storage Diagnostics` and `GET /api/v1/content/status`;
- `Gallery` is shared content presentation, not storage diagnostics with cosmetic relabeling.

### 4. Registry, Sync Core, Storage Service And Related Layers

`Registry Service` stores durable system identities and metadata.

It is the persistent truth for:

- module entries;
- component entries;
- service entries;
- profile references and related ownership metadata.

`Sync Core` is a platform service, not a hidden detail inside one controller page.

Its stable concerns include:

- service link continuity;
- module state exchange;
- shared preferences propagation;
- reports history transport;
- plant library transport;
- media content transport;
- component registry transport;
- software version exchange.

`Storage Service` handles:

- content-root readiness;
- mirrored storage truth;
- safe path actions;
- cleanup guardrails;
- overview data surfaced into shell snapshot.

`Activity And Reports Plumbing` handles:

- short shell activity summaries;
- quick entry into `Gallery > Reports`;
- typed product-level report entries;
- separation between reports and raw/internal logs.

Engineering trace boundary:

- owner-side logs вроде turret runtime event log остаются local engineering traces, а не автоматически promoted reports;
- driver-binding summaries и low-level adapter status допустимы в diagnostics/service surfaces, но не должны подменять `Gallery > Reports` или product module summaries.

Platform log baseline:

- node-level `Platform Log` может агрегировать локальные platform/service events и mirrored peer events;
- shell может показывать short recent entries этого platform log как overview signal, не превращая home surface в diagnostics console;
- mirrored log entries должны хранить origin metadata вроде `origin_node`, `origin_event_id` и mirrored marker;
- deduplication обязательна, чтобы repeated remote delivery не раздувала журнал;
- текущие implementation surfaces могут использовать `GET /api/v1/logs` и `POST /api/v1/sync/logs/push`, но active canon здесь про shared diagnostic continuity, а не про вечный endpoint naming.

These related layers must cooperate, but they must not collapse into one undifferentiated `system core` blob.

### 5. Что Видит Пользователь, А Что Остается Infrastructure Layer

Пользователь видит:

- `Home` cards and summaries;
- `Gallery` as shared content viewer;
- `Settings` as persistent preferences and system-truth page;
- `Laboratory` with shell context and service-aware constraints;
- module pages with owner-aware routing;
- dedicated diagnostics pages only when explicitly entered.

Infrastructure layer keeps:

- `GET /api/v1/shell/snapshot` as overview truth contract;
- `GET /api/v1/content/status` as storage diagnostics contract;
- `GET /api/v1/settings` as persistent settings payload;
- internal sync and registry endpoints;
- transport adapters that serve HTML/JSON on `ESP32` and `Raspberry Pi`.

Boundary rules:

- `Settings` should read runtime/platform overview from `Shell Snapshot` and persistent preferences from `Settings` payload, not synthesize meaning from four separate diagnostics calls;
- `Storage Diagnostics` may explain readiness and raw paths, but must not replace `Gallery`;
- shell activity summaries may point to `Gallery > Reports`, but they do not become the full report store;
- transport adapters remain implementation detail and must not redefine product/service vocabulary.

### 6. Нормативные Форматы И Примеры

Нормативные service endpoints:

- shell snapshot: `/api/v1/shell/snapshot`
- storage diagnostics: `/api/v1/content/status`
- settings payload: `/api/v1/settings`

Пример shell snapshot slice:

```json
{
  "schema_version": "shell-snapshot.v1",
  "current_shell": {
    "node_id": "rpi-turret",
    "runtime_profile": "desktop_smoke"
  },
  "sync": {
    "state": "local_only",
    "peer_reachable": false
  },
  "navigation": {
    "gallery": {
      "path": "/gallery",
      "route_mode": "virtual",
      "tabs": ["plants", "media", "reports"]
    },
    "laboratory": {
      "path": "/service"
    },
    "settings": "/settings"
  }
}
```

Пример module card shell truth:

```json
{
  "id": "irrigation",
  "owner_node_id": "esp32-main",
  "state": "locked",
  "block_reason": "owner_unavailable",
  "canonical_path": "/irrigation",
  "route_mode": "blocked"
}
```

Пример shared content overview slice:

```json
{
  "storage_kind": "filesystem",
  "content_root_state": "ready",
  "paths": [
    {
      "id": "content_root",
      "path": "C:/SmartPlatform/content",
      "state": "ready",
      "open_supported": true
    }
  ]
}
```

## Open Questions

- какие platform services стоит выделить в явный long-lived public contract уже сейчас
- где кончается human-facing service canon и начинается purely technical contract layer в `shared_contracts/`

## TODO

- после стабилизации active draft переаудировать service-layer donor residue в migration ledger и оставить только historical bootstrap/detail reminders
- проверить, что storage/service residue уже выражено active layer terms and no longer depends on donor-specific file authority
- отдельно зафиксировать переход от current mirrored logical paths к реальной automatic sync цепочке между `ESP32 SD` и `Raspberry Pi` content roots

## TBD

- глубина future service boundaries для расширяемых модулей
