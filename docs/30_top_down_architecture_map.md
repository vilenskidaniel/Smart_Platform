# Top-Down Architecture Map

Этот документ нужен, чтобы не теряться в глубине реализации.

Статус документа:

- supporting map, а не primary product spec;
- читать после `docs/README.md` и canonical core, когда уже понятны продуктовая модель и navigation vocabulary;
- не использовать как самостоятельный источник product-level терминологии, если она уже зафиксирована в `26_v1_product_spec.md` и `05_ui_shell_and_navigation.md`.

Он фиксирует:

- какие крупные сущности вообще существуют;
- кто чем владеет;
- какие классы уже есть;
- какие классы мы планируем;
- в каком порядке их имеет смысл наполнять.

Важно:

- актуальный execution-order и крупный product roadmap уже живут в `docs/09_master_design_plan.md`;
- этот документ сохраняем как role-first architecture snapshot, а не как второй мастер-план проекта.

## 1. Главный принцип

На этом этапе мы больше не идем путем:

- сначала очередной глубокий runtime-слой;
- потом еще один внутренний service;
- потом еще один transport-adapter.

Теперь идем так:

1. карта системы сверху вниз;
2. крупные классы и ownership;
3. skeleton и короткие обязанности;
4. только потом глубокая реализация.

## 2. Что здесь действительно фиксируется

Здесь не ведем live-roadmap по этапам. Этот файл нужен только для двух вещей:

- держать role-first карту крупных сущностей, ownership и skeleton-level ролей;
- не давать текущему physical baseline (`ESP32` и `Raspberry Pi`) подменять собой язык всей архитектуры.

## 3. Верхний уровень продукта

У продукта есть только 5 верхних блоков:

1. `Platform Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Все остальное — это platform services или implementation layers.

Важно:

- `Settings` остается отдельной user-facing persistent page, но не считается самостоятельным продуктовым блоком;
- логическая архитектурная карта не должна зависеть от vendor-названий плат там, где речь идет о ролях, ownership и пользовательских поверхностях.

## 4. Логическая Карта Ownership

Сначала фиксируем роли. Уже потом привязываем их к сегодняшнему железу.

### `Always-On I/O Node`

Роль:

- always-on sentinel;
- владелец `Irrigation`;
- локальное выполнение `Laboratory`-карточек для своей зоны и своих подключенных компонентов;
- power/wake supervisor;
- хранение локальных данных на `SD`;
- fallback shell.

### `Turret Compute Node`

Роль:

- turret-owner;
- vision/analysis node;
- heavy-content mirror;
- быстрый к жизни вычислительный узел для турели;
- владелец turret-family runtime и engineering-сценариев.

### Shared And Virtual Surfaces

- `Gallery` не привязывается к одному owner как shell-page;
- shell открывает общую explorer-страницу, а ownership у файлов и отчетов остается на уровне источников данных;
- `Laboratory` остается user-facing именем единой инженерной среды тестирования и квалификации компонентов, даже если внутренний route пока `/service`;
- `Settings` остается общей persistent surface для system-level choices и не должен смешиваться с naming-моделью физических узлов.

### Физический Baseline Today

- `ESP32` сегодня является физической реализацией роли `Always-On I/O Node`;
- `Raspberry Pi` сегодня является физической реализацией роли `Turret Compute Node`.

Если физическое распределение позже изменится, логические product-roles, ownership-модель и названия крупных архитектурных сущностей не должны переписываться заново.

## 5. Что уже реально существует

### Уже есть в always-on `I/O` baseline today (`ESP32`)

- `SystemCore`
- `PlatformEventLog`
- `WiFiBootstrap`
- `WebShellServer`
- `IrrigationController`
- `StrobeBenchController`
- `StorageManager`

### Уже есть в turret compute baseline today (`Raspberry Pi`)

- `BridgeState`
- `SyncClient`
- `TurretRuntime`
- `TurretDriverLayer`
- `TurretEventLog`
- `PlatformEventLog`
- `TurretServiceScenarioRunner`
- shell server

## 6. Какие крупные классы стоит считать целевыми

Ниже идут именно логические target names.

Названия файлов skeleton пока могут оставаться board-labeled, но названия крупных ролей и coordinator-классов лучше уже переводить в role-first модель.

### Always-on `I/O` node target skeleton

- `AlwaysOnIoNodeBlueprint`
- `LocalTriggerHubBlueprint`
- `PeerWakeCoordinatorBlueprint`
- `PowerSupervisorBlueprint`
- `IrrigationCoordinatorBlueprint`
- `LocalLaboratoryCoordinatorBlueprint`
- `ContentStorageCoordinatorBlueprint`
- `PeerShellClientBlueprint`

### Turret compute node target skeleton

- `TurretComputeNodeBlueprint`
- `TurretStandbyManagerBlueprint`
- `VisionSessionManagerBlueprint`
- `TargetDecisionEngineBlueprint`
- `TurretActionCoordinatorBlueprint`
- `TurretLaboratoryCoordinatorBlueprint`
- `ContentMirrorCoordinatorBlueprint`
- `PeerStateBridgeBlueprint`

## 7. Зачем файл сохраняем

Этот supporting-map нужен, чтобы другие чаты могли быстро понять role-first архитектурную карту, не перечитывая десятки runtime-деталей и не подменяя ее физическим baseline-языком.

## 8. Где смотреть skeleton

Skeleton-файлы для этого этапа:

- [esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/esp32_blueprint.h)
- [raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/raspberry_pi_blueprint.py)
- [README.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/README.md)

## 9. Где смотреть следующий уровень детализации

Для `Platform Shell v1` следующий уровень детализации уже вынесен отдельно:

- [31_platform_shell_class_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/31_platform_shell_class_map.md)
- [platform_shell_esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/platform_shell_esp32_blueprint.h)
- [platform_shell_raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/platform_shell_raspberry_pi_blueprint.py)
