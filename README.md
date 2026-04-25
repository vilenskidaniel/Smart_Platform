# Smart Platform

`Smart Platform` — это общая платформа для двух узлов:

- `ESP32` как локальный автономный контур полива, части сервисных функций и fallback shell;
- `Raspberry Pi` как владелец турели, камеры, media и тяжелой логики.

Главная идея платформы:

- оба узла поднимают browser-first интерфейс с единым визуальным языком;
- пользователь видит одну систему, а не два разных сайта;
- пользователь может зайти через `ESP32`, `Raspberry Pi` или локальный laptop smoke path, но shell обязан честно объяснить этот entry context;
- каждый модуль имеет понятного владельца;
- при появлении второго узла интерфейс не ломается, а мягко открывает peer-owned разделы через federated handoff;
- при потере одного узла система уходит в предсказуемую деградацию.

Аппаратный источник истины для текущего проекта:

- [docs/smart_platform_workshop_inventory.xlsx](docs/smart_platform_workshop_inventory.xlsx)
- именно этот workbook фиксирует подтвержденное наличие, ownership, power baseline и закупочные обновления;
- старые preliminary inventory-заметки больше не считаем источником истины.

## Что считать продуктом

На верхнем уровне продукт делится на:

1. `System Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Важно:

- `logs`, `diagnostics`, `sync` — это platform services;
- `Settings` не выделяется в отдельный product block, но остается обязательной persistent platform-page:
  здесь пользователь видит truthful platform state, shared preferences, storage/sync semantics и policy baselines;
- `camera_stack`, `driver layer`, `water path`, `sensor pack` — внутренние технические слои;
- внутреннее stage-name `Service/Test v1` можно сохранять в roadmap, но user-facing имя страницы фиксируется как `Laboratory`.

## Кто чем владеет

### `ESP32`

Локальная зона `ESP32`:

- полив;
- локальные датчики среды и почвы;
- SD-модуль как расширение хранения и приемник резервных копий synced turret-файлов;
- часть power/service диагностики;
- fallback shell;
- локальный `strobe_bench`, если он живет отдельно от turret-контура.

### `Raspberry Pi`

Локальная зона `Raspberry Pi`:

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
- полностью завершенного product-level `System Shell v1`;
- полной обкатки связки `ESP32 + Raspberry Pi` на реальном железе.

Важно:

- это не означает, что работа должна снова застрять в shell-refactor;
- текущий `System Shell` уже достаточно зрел как platform foundation;
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

Практическая модель входа для всех устройств описана в [docs/48_browser_entry_and_host_launch.md](docs/48_browser_entry_and_host_launch.md).

## С чего начинать

Если работа идет из другого чата, сначала читать в таком порядке:

1. [docs/smart_platform_workshop_inventory.xlsx](docs/smart_platform_workshop_inventory.xlsx)
2. [docs/26_v1_product_spec.md](docs/26_v1_product_spec.md)
3. [docs/01_product_decisions.md](docs/01_product_decisions.md)
4. [docs/02_system_architecture.md](docs/02_system_architecture.md)
5. [docs/05_ui_shell_and_navigation.md](docs/05_ui_shell_and_navigation.md)
6. [docs/39_design_decisions_and_screen_map.md](docs/39_design_decisions_and_screen_map.md)
7. [docs/40_system_shell_navigation_alignment.md](docs/40_system_shell_navigation_alignment.md)
8. [docs/09_master_design_plan.md](docs/09_master_design_plan.md)
9. [docs/28_legacy_migration_map.md](docs/28_legacy_migration_map.md)
10. [docs/30_top_down_architecture_map.md](docs/30_top_down_architecture_map.md)
11. [docs/27_system_shell_v1_spec.md](docs/27_system_shell_v1_spec.md)
12. [docs/31_system_shell_class_map.md](docs/31_system_shell_class_map.md)
13. [docs/32_current_shell_role_mapping.md](docs/32_current_shell_role_mapping.md)
14. [docs/33_shell_snapshot_schema.md](docs/33_shell_snapshot_schema.md)
15. [shared_contracts/shell_snapshot_contract.md](shared_contracts/shell_snapshot_contract.md)

Stage-документы `12+` читать уже после этого, когда нужен исторический и технический контекст.

## Рекомендуемый ход работы

Платформу лучше развивать по продуктовым блокам:

1. `System Shell v1`
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

- [docs/34_modular_chat_transition_plan.md](docs/34_modular_chat_transition_plan.md)
- [docs/35_irrigation_v1_software_stage.md](docs/35_irrigation_v1_software_stage.md)
- [docs/36_turret_v1_software_stage.md](docs/36_turret_v1_software_stage.md)
- [docs/37_turret_product_context_map.md](docs/37_turret_product_context_map.md)
- [briefs/README.md](briefs/README.md)
- [WORKFLOW_FOR_OTHER_CHATS.md](WORKFLOW_FOR_OTHER_CHATS.md)

## Напоминание по контексту

На этом этапе уже не стоит тащить все большие направления подряд в одном длинном чате.

Практический режим такой:

1. этот чат подходит для координации, синтеза и сверки документации;
2. глубокую разработку лучше вести по одному product-level блоку за чат;
3. после завершения отдельных блоков нужно возвращаться сюда для синтеза и интеграции.

Если новый чат одновременно начинает подробно тянуть `System Shell`, `Irrigation` и `Turret`, это сигнал снова разделить работу.

Важно:

- отдельная user-facing страница `Logs` больше не считается product target;
- канонический просмотр истории действий и отчетов идет через `Gallery > Reports`;
- shell может показывать только короткие activity summaries и быстрый вход в `Gallery > Reports`.
