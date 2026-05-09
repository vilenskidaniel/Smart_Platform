# 09. Repository Layout And Code Map

## Роль Файла

Этот файл должен объяснять, где в репозитории лежит активный код, где лежит документация, где prompt-слой и как быстро находить нужную implementation surface.

## Статус

- текущий статус: `active draft`

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `README.md` остается active companion entry file для repo-level onboarding.

## Settled Truths

- человек должен быстро понимать, где docs, prompts и code
- donor-layer и active-layer должны быть явно разделены

## 1. Корень Репозитория

Рабочий корень проекта — сам репозиторий `Smart_Platform`.

На верхнем уровне сейчас важно различать:

- активный human-facing canon;
- donor documentation layer;
- prompt-layer для AI workflows;
- working code для `ESP32`, `Raspberry Pi`, web surfaces и shared contracts.

Главное правило:

- не считать target layout и current implementation baseline одной и той же вещью;
- не читать legacy donor layer как active truth, если новый canon уже перенесен в `knowledge_base/`.

## 2. Где Лежит Активный Код

Текущий working code живет прежде всего в этих каталогах:

- `firmware_esp32/` — PlatformIO firmware side;
- `raspberry_pi/` — Python runtime, shell server, sync, registry, reports, laboratory and turret layers;
- `shared_contracts/` — общие machine/human-readable contracts;
- `tools/` — host launchers и supporting entry tooling.

Важно:

- каталог `web_ui/` существует как target/future layout marker, но current working web surfaces сегодня в основном живут в `raspberry_pi/web/` и `firmware_esp32/data/`;
- это нужно читать честно, а не делать вид, что target structure уже полностью материализована.

## 3. Где Лежит Новый Канон

### Target Layout Direction And Ownership Rules

Target layout нужен как directional map для cleanup и refactor work, даже если current implementation еще не полностью совпадает с ним.

Верхнеуровневой целевой структурой считаем:

- `firmware_esp32/` для `ESP32` firmware, embedded assets и platform-side tests;
- `raspberry_pi/` для turret/runtime/server layers, host-side services и tests;
- `shared_contracts/` для общих contracts, schema-like interfaces и machine/human-readable agreements;
- `web_ui/` как future shared shell/frontend home, когда current web surfaces будут достаточно отделены от host-specific runtimes.

Ownership rules для repo cleanup и будущего layout alignment:

- `ESP32`-specific implementation не должна расползаться за пределы `firmware_esp32/`;
- `Raspberry Pi` runtime and service logic не должна расползаться за пределы `raspberry_pi/`;
- shared contracts описываются один раз в `shared_contracts/`, а не копируются в platform-specific trees;
- visual language, page composition и reusable UI pieces должны сходиться в `web_ui/` или в явно временном current web layer, но не смешиваться с hardware-specific runtime files.

Что нельзя считать допустимым target state:

- дублирование одного и того же контракта по нескольким каталогам;
- дублирование business logic между shell surfaces разных host trees;
- постоянное хранение UI-specific решений внутри hardware modules;
- смешение service interface, runtime orchestration и safety logic в одном большом transport-oriented файле.

Новый активный documentation layer живет в `knowledge_base/`.

Порядок чтения идет сверху вниз:

1. `knowledge_base/README.md`
2. `knowledge_base/01-09`
3. `knowledge_base/10-16`
4. `knowledge_base/17_open_questions_and_migration.md`

Этот слой отвечает за active human truth и должен обновляться раньше donor-слоя.

## 4. Где Лежит Donor Слой

Legacy donor material больше не считается частью active reading path; его mapping и residue-status фиксируются в `knowledge_base/17_open_questions_and_migration.md`.

Его роль теперь:

- donor source для вырезания смысла в новый canon;
- historical/detail layer;
- supporting inventory для того, что еще не перенесено.

legacy archive residue, пока оно еще физически существует, — это historical snapshots, а не active reading path.

## 5. Где Лежит Prompt-Слой

Prompt-layer живет в `chat_prompts/`.

Его задача:

- не быть вторым product manual;
- направлять новые чаты к правильному active canon;
- фиксировать cross-chat operating rules и модульные AI guardrails.

Стартовые файлы:

- `chat_prompts/README.md`
- `chat_prompts/foundation_prompt.md`
- `chat_prompts/cross_module_prompt.md`
- модульные prompt-файлы для `Irrigation`, `Turret`, `Laboratory`, `Gallery`, `Settings`, `Platform Shell`.

Default modular chat flow:

- один рабочий чат должен держать один product-level block;
- рекомендуемая sequence текущего этапа: `Platform Shell -> Irrigation -> Turret -> Gallery -> Laboratory`;
- после завершения одного блока или при смене ownership/handoff/sync semantics нужно возвращаться в coordination or cross-module layer для синтеза, а не тащить второй большой блок в тот же поток;
- `Этап 2` master-plan и `второй пункт` модульной очереди — не одно и то же: второй модуль после shell здесь считается `Irrigation`.

## 6. Быстрые Code Anchors По Модулям

`ESP32 / firmware baseline`:

- `firmware_esp32/src/`
- `firmware_esp32/include/`
- `firmware_esp32/lib/`
- `firmware_esp32/data/` для current shell/static assets on firmware side.

Practical `ESP32` shell deployment note:

- current shell pages on firmware side are served `LittleFS`-first from `firmware_esp32/data/`;
- firmware keeps only safe fallback pages and startup/runtime logic, not the full shell HTML as giant string literals;
- for a truthful shell pass on device, baseline cycle is `pio run -t upload` plus `pio run -t uploadfs`.

`Raspberry Pi / runtime and shell`:

- `raspberry_pi/app.py`
- `raspberry_pi/server.py`
- `raspberry_pi/bridge_state.py`
- `raspberry_pi/sync_client.py`
- `raspberry_pi/shell_snapshot_facade.py`
- `raspberry_pi/shell_viewer_presence.py`

`Registry, settings, reports, storage`:

- `raspberry_pi/platform_registry_store.py`
- `raspberry_pi/settings_store.py`
- `raspberry_pi/report_feed.py`
- `raspberry_pi/report_archive.py`
- `raspberry_pi/storage_status.py`

`Laboratory`:

- `raspberry_pi/laboratory_readiness.py`
- `raspberry_pi/laboratory_session.py`
- `raspberry_pi/web/service.html`
- `raspberry_pi/web/service_displays.html`
- `raspberry_pi/web/service_turret.html`

`Turret`:

- `raspberry_pi/turret_runtime.py`
- `raspberry_pi/turret_driver_layer.py`
- `raspberry_pi/turret_service_scenarios.py`
- `raspberry_pi/turret_event_log.py`
- `raspberry_pi/turret_capture_store.py`
- `raspberry_pi/web/turret.html`

`Shared shell and current web surfaces`:

- `raspberry_pi/web/index.html`
- `raspberry_pi/web/gallery.html`
- `raspberry_pi/web/settings.html`
- `raspberry_pi/web/content.html`
- `raspberry_pi/web/static/`

`Contracts`:

- `shared_contracts/module_registry_contract.md`
- `shared_contracts/shell_snapshot_contract.md`
- `shared_contracts/content_library_contract.md`
- `shared_contracts/system_core_contract.md`

### Role-First Architecture Inventory Anchors

Для быстрых architecture lookups полезно отдельно держать инвентарь уже существующих surfaces и target role-first skeleton names, не подменяя ими active product/service canon.

Current baseline surfaces today:

- always-on `I/O` side: `SystemCore`, `PlatformEventLog`, `WiFiBootstrap`, `WebShellServer`, `IrrigationController`, `StrobeBenchController`, `StorageManager`;
- turret compute side: `BridgeState`, `SyncClient`, `TurretRuntime`, `TurretDriverLayer`, `TurretEventLog`, `PlatformEventLog`, `TurretServiceScenarioRunner` и shell server.

Target role-first skeleton inventory:

- always-on `I/O`: `AlwaysOnIoNodeBlueprint`, `LocalTriggerHubBlueprint`, `PeerWakeCoordinatorBlueprint`, `PowerSupervisorBlueprint`, `IrrigationCoordinatorBlueprint`, `LocalLaboratoryCoordinatorBlueprint`, `ContentStorageCoordinatorBlueprint`, `PeerShellClientBlueprint`;
- turret compute: `TurretComputeNodeBlueprint`, `TurretStandbyManagerBlueprint`, `VisionSessionManagerBlueprint`, `TargetDecisionEngineBlueprint`, `TurretActionCoordinatorBlueprint`, `TurretLaboratoryCoordinatorBlueprint`, `ContentMirrorCoordinatorBlueprint`, `PeerStateBridgeBlueprint`.

Skeleton entrypoints этого этапа:

- `skeletons/esp32_blueprint.h`;
- `skeletons/raspberry_pi_blueprint.py`;
- `skeletons/README.md`;
- `skeletons/platform_shell_esp32_blueprint.h`;
- `skeletons/platform_shell_raspberry_pi_blueprint.py`.

### Current Shell Refactor Anchors

Для shell важно отдельно различать product/service canon и текущую карту refactor-pressure в коде.

Текущие transport entrypoints today-baseline:

- `firmware_esp32` shell transport физически входит через `WebShellServer`;
- `raspberry_pi` shell transport физически входит через `server.py`.

Эти entrypoints нужно читать как `ShellHttpAdapter`-подобный слой, а не как вечное место для всей shell-логики.

Текущая зона наибольшего смешения:

- на `ESP32` shell snapshot и related shell truth размазаны между `SystemCore`, `WebShellServer`, `StorageManager` и частично `PlatformEventLog`;
- на `Raspberry Pi` shell snapshot и handoff logic размазаны между `BridgeState`, `server.py` и отдельными runtime builders.

Безопасный short-term refactor order:

1. сначала выравнивать shell-level snapshot/facade layer;
2. затем выносить owner-aware navigation/handoff coordinator;
3. только после этого отдельно усиливать page-level presenters, если transport entrypoints снова начинают толстеть.

Практический вывод:

- `ShellSnapshotFacade`, `ShellNavigationCoordinator` и похожие названия нужно читать как implementation role names, а не как product vocabulary;
- `ShellContentPresenter` уже выглядит относительно отделенным и не является первым refactor priority;
- `ShellSettingsPresenter` нельзя считать зрелым сервисом только потому, что в коде уже появились `settings.html` и `GET /api/v1/settings`.

## 7. Как Читать Репозиторий Сверху Вниз

Практический reading order для нового человека или нового чата:

1. понять продуктовый и архитектурный canon через `knowledge_base/README.md` и `knowledge_base/01-08`;
2. открыть этот файл и понять, где лежит active code для нужного среза;
3. при необходимости подключить нужный модульный prompt из `chat_prompts/`;
4. только потом уходить в legacy donor residue, если в active canon еще остались пробелы;
5. после этого открывать code anchor, а не делать широкий repo tour без цели.

Если нужен только current implementation baseline, а не вся история проекта, legacy donor residue можно вообще не открывать до первого реального knowledge gap.

## Open Questions

- нужен ли отдельный human onboarding map вне этого файла

## TODO

- собрать короткую code-map без повторения всего дерева

## TBD

- итоговый формат clickable code anchor maps для VS Code и GitHub
