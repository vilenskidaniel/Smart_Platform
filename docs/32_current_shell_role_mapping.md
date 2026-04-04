# Current Shell To Role Mapping

Этот документ связывает:

- текущий shell-код;
- целевые 8 ролей из `System Shell v1`;
- и первый безопасный порядок рефакторинга.

Он нужен, чтобы мы не обсуждали shell абстрактно.

## 1. Короткий диагноз

Сейчас shell уже работает, но реализован как bootstrap-монолит:

- на `ESP32` почти все собрано в `WebShellServer`;
- на `Raspberry Pi` почти все собрано в `server.py` и частично в `BridgeState`.

Это нормально для ранних этапов, но уже плохо масштабируется:

- transport и shell-смыслы смешаны;
- сборка snapshot смешана с HTML и JSON-ответами;
- owner-aware навигация смешана с маршрутизацией;
- страницы shell и продуктовые API лежат слишком близко друг к другу.

## 2. Mapping по ролям

| Целевая роль | Что ее покрывает сейчас на `ESP32` | Что ее покрывает сейчас на `Raspberry Pi` | Состояние |
|---|---|---|---|
| `ShellSnapshotFacade` | `SystemCore::buildSystemSnapshotJson()`, `WebShellServer::buildModulesJson()`, `buildDiagnosticsJson()`, `buildSyncStateJson()`, `StorageManager::buildContentStatusJson()` | `BridgeState::build_system_snapshot()`, `build_platform_log()`, `build_sync_status()`, частично `build_turret_status()` | Есть, но размазано |
| `ShellNavigationCoordinator` | `WebShellServer::buildFederatedRouteInfoJson()`, `canonicalPathForModuleId()`, часть `handleFederatedHandoffPage()` | `BridgeState::build_module_route_info()`, handoff page в `server.py` | Есть, но смешано с transport |
| `ShellHomePresenter` | `data/index.html` + fallback `buildIndexHtml()` | `web/index.html` | Есть, но зависит от сырого API |
| `ShellSettingsPresenter` | Почти отсутствует как отдельная сущность | Почти отсутствует как отдельная сущность | Надо проектировать |
| `ShellDiagnosticsPresenter` | `handleDiagnostics()` + `buildDiagnosticsJson()` + клиентская логика в shell page | `/api/v1/sync/status`, `build_sync_status()`, часть snapshot в `BridgeState` | Частично есть |
| `ShellLogPresenter` | `handleLogs()` + `PlatformEventLog::buildSnapshotJson()` | `/api/v1/logs` + `BridgeState::build_platform_log()` | Есть, но не отделен от log backend |
| `ShellContentPresenter` | `/content`, `/api/v1/content/status`, fallback `buildContentHtml()` + `data/content/index.html` | `/content`, `/api/v1/content/status`, `web/content.html` | Уже хорошо выделяется |
| `ShellHttpAdapter` | `WebShellServer` | `server.py` | Есть, но слишком жирный |

Важно:

- `ShellLogPresenter` в текущем software baseline остается transitional adapter-слоем;
- product target viewer для глубокой истории действий теперь фиксируется как `Gallery > Reports`;
- `ShellContentPresenter` тоже остается service/storage diagnostics surface и не должен считаться user-facing заменой `Gallery`.

## 3. Что уже выглядит удачно

### 1. `ShellContentPresenter`

Это сейчас самый чистый кусок shell.

Почему:
- есть отдельная страница;
- есть отдельный status endpoint;
- смысл понятен пользователю;
- storage backend уже отделен лучше, чем в других местах.

### 2. `ShellNavigationCoordinator`

Логика handoff уже есть и правильно согласуется с ownership-моделью.

Проблема только в том, что она пока живет прямо внутри transport entrypoint.

### 3. `ShellLogPresenter`

Страница логов еще не доведена как UI, но логический слой уже понятен:
- shell показывает журнал;
- backend логирования живет отдельно.

Это хорошая основа.

Но по product target:

- глубокая история действий из `Laboratory` и ручных режимов должна уходить в `Gallery > Reports`;
- shell может оставлять только короткий activity summary и быстрый вход в `Reports`.

## 4. Что сейчас самое смешанное

### 1. `ShellSnapshotFacade`

Это сейчас самый размазанный слой.

На `ESP32` snapshot-смысл разделен между:
- `SystemCore`;
- `WebShellServer`;
- `StorageManager`;
- частично `PlatformEventLog`.

На `Raspberry Pi` он размазан между:
- `BridgeState`;
- `server.py`;
- turret-specific builders.

Именно поэтому shell пока трудно читать и трудно развивать без риска.

### 2. `ShellHttpAdapter`

Оба transport entrypoint сейчас слишком толстые:

- `WebShellServer` знает про страницы, JSON, sync, irrigation, strobe bench,
  file serving и fallback shell;
- `server.py` знает про shell, turret runtime, sync refresh, content serving,
  federated handoff и peer state.

То есть transport-слой уже давно выполняет лишнюю работу.

### 3. `ShellSettingsPresenter`

По сути его пока еще нет.

Это нормально, но важно честно это признать: `Settings` пока не продуктовый
модуль shell, а лишь обещание в spec.

## 5. Что выносить первым

Первый безопасный кандидат на вынос:

### `ShellSnapshotFacade`

Почему именно он:
- он не должен ломать transport;
- он нужен сразу всем shell-страницам;
- он уменьшит дублирование между `ESP32` и `Raspberry Pi`;
- он позволит перестать собирать shell-картину кусками в разных местах.

Что это даст:
- `WebShellServer` и `server.py` смогут стать тоньше;
- `Home`, shell summaries, `Gallery > Reports` entrypoints и `Content Storage` начнут получать более ровный набор данных;
- следующий рефакторинг не будет “переписыванием всего shell”.

## 6. Что выносить вторым

После `ShellSnapshotFacade` логично выносить:

### `ShellNavigationCoordinator`

Потому что:
- federated handoff уже есть;
- ownership-модель уже стабилизировалась;
- эту логику лучше централизовать до того, как shell-страницы начнут множиться.

## 7. Что пока не трогать

Пока не нужно первым делом выносить:

- `ShellContentPresenter`
  причина: он уже относительно чистый
- `ShellLogPresenter`
  причина: без общего snapshot он все равно останется привязан к backend
- `ShellSettingsPresenter`
  причина: его лучше проектировать уже после стабилизации snapshot-модели

## 8. Практический следующий шаг

Следующий разумный этап уже не “новая абстракция ради абстракции”, а:

1. спроектировать shell-level snapshot schema;
2. определить, какие данные в него входят всегда;
3. сделать skeleton `ShellSnapshotFacade` для `ESP32` и `Raspberry Pi`;
4. не переписывать все страницы сразу, а сначала перевести на него
   `Главную` и `Диагностику`.

## 9. Связанные документы

- [27_system_shell_v1_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/27_system_shell_v1_spec.md)
- [31_system_shell_class_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/31_system_shell_class_map.md)
- [33_shell_snapshot_schema.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/33_shell_snapshot_schema.md)
- [shell_snapshot_contract.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/shared_contracts/shell_snapshot_contract.md)
- [09_master_design_plan.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/09_master_design_plan.md)
