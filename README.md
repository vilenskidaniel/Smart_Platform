# Smart Platform

`Smart Platform` — это общая платформа для двух узлов:

- текущий `ESP32` baseline как always-on I/O и controller profile для полива, части сервисных функций и fallback shell;
- текущий `Raspberry Pi` baseline как turret-compute и controller profile для турели, камеры, media и тяжелой логики.

Главная идея платформы:

- оба узла поднимают browser-first интерфейс с единым визуальным языком;
- пользователь видит одну систему, а не два разных сайта;
- пользователь может зайти через `ESP32`, `Raspberry Pi` или локальный laptop smoke path, но shell обязан честно объяснить этот entry context;
- каждый модуль имеет понятного владельца;
- при появлении второго узла интерфейс не ломается, а мягко открывает peer-owned разделы через federated handoff;
- при потере одного узла система уходит в предсказуемую деградацию.

Аппаратный источник истины для текущего проекта:

- [knowledge_base/resources/smart_platform_workshop_inventory.xlsx](knowledge_base/resources/smart_platform_workshop_inventory.xlsx)
- именно этот workbook фиксирует подтвержденное наличие, ownership, power baseline и закупочные обновления;
- старые preliminary inventory-заметки больше не считаем источником истины.

## Что считать продуктом

На верхнем уровне продукт делится на:

1. `Platform Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Важно:

- `logs`, `diagnostics`, `sync` — это platform services;
- `Settings` не выделяется в отдельный product block, но остается обязательной persistent platform-page:
  здесь пользователь видит truthful platform state, shared preferences, storage/sync semantics и policy baselines;
- `camera_stack`, `driver layer`, `water path`, `sensor pack` — внутренние технические слои;
- legacy alias `service_test` можно сохранять в roadmap, но user-facing имя страницы фиксируется как `Laboratory`.

## Кто чем владеет

Ниже зафиксирован текущий working baseline, а не вечная архитектурная привязка модулей к конкретным платам.

### `ESP32`

Текущий controller profile на `ESP32`:

- полив;
- локальные датчики среды и почвы;
- SD-модуль как расширение хранения и приемник резервных копий synced turret-файлов;
- часть power/service диагностики;
- fallback shell;
- локальный `strobe_bench`, если он живет отдельно от turret-контура.

### `Raspberry Pi`

Текущий controller profile на `Raspberry Pi`:

- турель;
- основная камера `IMX219 130°`;
- range / lidar направление;
- боевой `strobe`;
- audio / piezo;
- motion;
- turret water path `SEAFLO 12V`;
- vision, tracking и logic layer.

## Текущее состояние

Сейчас уже есть рабочий платформенный каркас:

- поднят `ESP32` shell по `Wi-Fi`;
- shell вынесен в `LittleFS`;
- `irrigation` доведен до software-level `Irrigation v1`;
- `turret` доведен до software-level `Turret v1`;
- есть sync bootstrap между узлами;
- есть owner-aware routing и federated handoff;
- `Laboratory` уже существует как единый service-entry contour с маршрутом `/service`.

Чего пока нет как полностью закрытого software/hardware результата:

- реальной камеры и production-ready FPV transport;
- полного hardware-backed turret stack;
- полного live irrigation hardware-loop;
- полностью завершенного product-level `Platform Shell`;
- полной обкатки связки `ESP32 + Raspberry Pi` на реальном железе.

Важно:

- это не означает, что работа должна снова застрять в shell-refactor;
- текущий `Platform Shell` уже достаточно зрел как platform foundation;
- поэтому дальнейшую работу можно вести по модульным блокам и по product-context, а не только по внутренним слоям.

## Где именно работать

Для новой разработки рабочим корнем считается сам этот репозиторий `Smart Platform`.

Практически это значит:

- `ESP32`-сторону собирать и развивать из `firmware_esp32/`;
- `Raspberry Pi`-сторону развивать из `raspberry_pi/`;
- legacy bench/donor-слой теперь живет вне этого репозитория и должен подтягиваться только осознанной выборочной миграцией, а не как основной рабочий корень.

## Быстрый Host Launch На Windows

Если нужен быстрый запуск `Raspberry Pi` shell с Windows-хоста, в репозитории теперь есть launcher:

- [tools/Launch-SmartPlatformShell.vbs](tools/Launch-SmartPlatformShell.vbs)
- [tools/Launch-SmartPlatformShell.cmd](tools/Launch-SmartPlatformShell.cmd)
- [tools/Launch-SmartPlatformShell.ps1](tools/Launch-SmartPlatformShell.ps1)

Что он делает:

- поднимает `raspberry_pi/app.py` с правильными env-переменными;
- по умолчанию запускает shell в `LAN`-режиме на `8091`;
- держит host-side server скрытым, без постоянного терминала на рабочем столе;
- открывает shell в app-like окне браузера;
- может быть использован как основная точка входа для тестирования на `Windows PC`.

Практическая модель входа для всех устройств описана в [knowledge_base/04_runtime_topology_controller_profiles_and_sync.md](knowledge_base/04_runtime_topology_controller_profiles_and_sync.md) и [knowledge_base/05_shell_navigation_and_screen_map.md](knowledge_base/05_shell_navigation_and_screen_map.md).

## С чего начинать

Если работа идет из другого чата, сначала читать в таком порядке:

1. [knowledge_base/README.md](knowledge_base/README.md)
2. [knowledge_base/01_project_scope_and_goals.md](knowledge_base/01_project_scope_and_goals.md)
3. [knowledge_base/02_system_terms_and_design_rules.md](knowledge_base/02_system_terms_and_design_rules.md)
4. [knowledge_base/03_platform_architecture_and_module_relationships.md](knowledge_base/03_platform_architecture_and_module_relationships.md)
5. [knowledge_base/04_runtime_topology_controller_profiles_and_sync.md](knowledge_base/04_runtime_topology_controller_profiles_and_sync.md)
6. [knowledge_base/05_shell_navigation_and_screen_map.md](knowledge_base/05_shell_navigation_and_screen_map.md)
7. [knowledge_base/06_shared_ui_contract.md](knowledge_base/06_shared_ui_contract.md)
8. [knowledge_base/07_data_registry_storage_and_persistence.md](knowledge_base/07_data_registry_storage_and_persistence.md)
9. [knowledge_base/08_safety_acceptance_and_field_operations.md](knowledge_base/08_safety_acceptance_and_field_operations.md)
10. [knowledge_base/09_repository_layout_and_code_map.md](knowledge_base/09_repository_layout_and_code_map.md)
11. [knowledge_base/resources/smart_platform_workshop_inventory.xlsx](knowledge_base/resources/smart_platform_workshop_inventory.xlsx)

Если в active canon обнаружен knowledge gap, сначала сверяться с [knowledge_base/17_open_questions_and_migration.md](knowledge_base/17_open_questions_and_migration.md), а не возвращаться к legacy reading order вслепую.

## Рекомендуемый ход работы

Платформу лучше развивать по продуктовым блокам:

1. `Platform Shell`
2. `Irrigation v1`
3. `Turret v1`
4. `Gallery v1`
5. `Laboratory v1`

После этого уже углубляться в:

- расширенный sync;
- сложные proxy-flow;
- hardware abstraction;
- pin/power документы.

Подробный переходный план:

- [knowledge_base/17_open_questions_and_migration.md](knowledge_base/17_open_questions_and_migration.md)
- [knowledge_base/10_irrigation_module.md](knowledge_base/10_irrigation_module.md)
- [knowledge_base/11_turret_module.md](knowledge_base/11_turret_module.md)
- [briefs/README.md](briefs/README.md)
- [WORKFLOW_FOR_OTHER_CHATS.md](WORKFLOW_FOR_OTHER_CHATS.md)

## Напоминание по контексту

На этом этапе уже не стоит тащить все большие направления подряд в одном длинном чате.

Практический режим такой:

1. этот чат подходит для координации, синтеза и сверки документации;
2. глубокую разработку лучше вести по одному product-level блоку за чат;
3. после завершения отдельных блоков нужно возвращаться сюда для синтеза и интеграции.

Если новый чат одновременно начинает подробно тянуть `Platform Shell`, `Irrigation` и `Turret`, это сигнал снова разделить работу.

Важно:

- отдельная user-facing страница `Logs` больше не считается product target;
- канонический просмотр истории действий и отчетов идет через `Gallery > Reports`;
- shell может показывать только короткие activity summaries и быстрый вход в `Gallery > Reports`.
