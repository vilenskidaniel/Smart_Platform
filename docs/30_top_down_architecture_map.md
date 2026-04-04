# Top-Down Architecture Map

Этот документ нужен, чтобы не теряться в глубине реализации.

Он фиксирует:

- какие крупные сущности вообще существуют;
- кто чем владеет;
- какие классы уже есть;
- какие классы мы планируем;
- в каком порядке их имеет смысл наполнять.

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

## 2. Сколько больших этапов реально осталось

Если смотреть не по мелким техническим слоям, а по крупным продуктовым работам, то от текущей точки остаются примерно 7 больших шагов:

1. зафиксировать skeleton архитектуры и имена крупных классов;
2. довести `System Shell v1` до понятного продуктового состояния;
3. довести `Irrigation v1` как локальный автономный контур `ESP32`;
4. довести `Turret v1` как turret-owner на `Raspberry Pi`;
5. довести `Gallery v1` как глобальный content explorer;
6. довести `Laboratory / Service/Test v1` как отдельный тестовый контур;
7. пройти hardware/power/wake интеграцию и живую обкатку.

То есть этапов еще много, но они уже должны управляться не десятками внутренних сущностей, а этими шестью крупными направлениями.

## 3. Верхний уровень продукта

У продукта есть только 5 верхних блоков:

1. `System Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Все остальное — это platform services или implementation layers.

## 4. Карта ownership

### `ESP32`

Роль:

- always-on sentinel;
- владелец `Irrigation`;
- локальный `Service/Test` для своей зоны;
- power/wake supervisor;
- хранение локальных данных на `SD`;
- fallback shell.

### `Raspberry Pi`

Роль:

- turret-owner;
- vision/analysis node;
- heavy-content mirror;
- быстрый к жизни вычислительный узел для турели;
- владелец turret-family service/test сценариев.

### Shared Virtual Sections

- `Gallery` не привязывается к одному owner как shell-page;
- shell открывает общую explorer-страницу, а ownership у файлов и отчетов остается на уровне источников данных;
- `Laboratory` остается user-facing именем единого diagnostics/test-bench контура, даже если внутренний route пока `/service`.

## 5. Что уже реально существует

### Уже есть на `ESP32`

- `SystemCore`
- `PlatformEventLog`
- `WiFiBootstrap`
- `WebShellServer`
- `IrrigationController`
- `StrobeBenchController`
- `StorageManager`

### Уже есть на `Raspberry Pi`

- `BridgeState`
- `SyncClient`
- `TurretRuntime`
- `TurretDriverLayer`
- `TurretEventLog`
- `PlatformEventLog`
- `TurretServiceScenarioRunner`
- shell server

## 6. Какие крупные классы стоит считать целевыми

### `ESP32` target skeleton

- `Esp32DutyNodeBlueprint`
- `LocalTriggerHubBlueprint`
- `PeerWakeCoordinatorBlueprint`
- `PowerSupervisorBlueprint`
- `IrrigationCoordinatorBlueprint`
- `ServiceTestCoordinatorBlueprint`
- `ContentStorageCoordinatorBlueprint`
- `PeerShellClientBlueprint`

### `Raspberry Pi` target skeleton

- `RaspberryPiTurretNodeBlueprint`
- `TurretStandbyManagerBlueprint`
- `VisionSessionManagerBlueprint`
- `TargetDecisionEngineBlueprint`
- `TurretActionCoordinatorBlueprint`
- `TurretServiceCoordinatorBlueprint`
- `ContentMirrorCoordinatorBlueprint`
- `PeerStateBridgeBlueprint`

## 7. Почему это лучше текущего хаоса глубины

Такой подход дает:

- понятную карту, что вообще существует;
- контроль глубины проработки;
- возможность обсуждать архитектуру без чтения десятков runtime-деталей;
- более безопасную работу из других чатов и по отдельным модулям.

## 8. Где смотреть skeleton

Skeleton-файлы для этого этапа:

- [esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/esp32_blueprint.h)
- [raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/raspberry_pi_blueprint.py)
- [README.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/README.md)

## 9. Следующий правильный ход

После этого документа уже можно безопасно идти не во все стороны сразу, а по одному крупному блоку:

1. уточнить skeleton для `System Shell v1`;
2. затем для `Irrigation v1`;
3. затем для `Turret v1`;
4. затем для `Gallery v1`;
5. затем для `Laboratory / Service/Test v1`.

Для `System Shell v1` следующий уровень детализации уже вынесен отдельно:

- [31_system_shell_class_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/31_system_shell_class_map.md)
- [system_shell_esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/system_shell_esp32_blueprint.h)
- [system_shell_raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/system_shell_raspberry_pi_blueprint.py)
