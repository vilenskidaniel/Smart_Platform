# Master Design Plan

Этот план теперь ведется от уровня продукта, а не от списка внутренних технических слоев.

## 1. Принцип планирования

Сначала проектируем и доводим продуктовые блоки:

1. `System Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Параллельно поддерживаем минимально необходимые platform services:

- `sync`
- `logs`
- `settings`
- `diagnostics`

Внутренние технические слои развиваем только в той мере, в какой они нужны этим четырем блокам.

## 1.1. Текущий режим дальнейшей работы

Исследовательская фаза уже дала нам каркас, но начала разрастаться в глубину.

Дальше лучше работать так:

1. сначала фиксировать архитектуру сверху вниз;
2. затем обозначать крупные классы, ownership и роли;
3. после этого добавлять заглушки и короткие обязанности;
4. и только потом уходить в глубокую реализацию методов.

Это означает:

- не плодить новые глубокие runtime-слои без прямой пользы для ближайшего продуктового блока;
- не писать большие методы раньше, чем у нас появилась понятная карта классов;
- сначала делать понятный skeleton, потом наполнять его поведением.

Артефакты этого режима:

- [30_top_down_architecture_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/30_top_down_architecture_map.md)
- [skeletons/README.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/README.md)

## 2. Этап 1. Зафиксировать `v1` как продукт

Результат этапа:

- есть короткий документ уровня продукта;
- согласован `v1 scope`;
- верхняя документация не путает продуктовые модули и внутренние сервисы.

Артефакты:

- [26_v1_product_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/26_v1_product_spec.md)
- [01_product_decisions.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/01_product_decisions.md)
- [02_system_architecture.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/02_system_architecture.md)
- [05_ui_shell_and_navigation.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/05_ui_shell_and_navigation.md)
- [28_legacy_migration_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/28_legacy_migration_map.md)
- [29_shared_content_and_sd_strategy.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/29_shared_content_and_sd_strategy.md)
- [content_library_contract.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/shared_contracts/content_library_contract.md)

## 3. Этап 2. `System Shell v1`

Цель:

- сделать понятную единую точку входа в систему.

Что должно быть:

- mobile-first shell;
- одинаковый дизайн на `ESP32` и `Raspberry Pi`;
- owner-aware handoff;
- статус узлов;
- общие настройки;
- диагностика;
- общий обзор доступности модулей.

Что не должно разрастаться:

- shell не должен превращаться в отдельный “технический продукт”;
- shell не должен светить внутренние runtime-слои пользователю.

Следующий правильный шаг внутри этого этапа:

- сделать управляемую карту архитектуры и имен классов для `System Shell v1`;
- не уходить сразу в глубокую реализацию всех методов.

Артефакты этого шага:

- [27_system_shell_v1_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/27_system_shell_v1_spec.md)
- [31_system_shell_class_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/31_system_shell_class_map.md)
- [32_current_shell_role_mapping.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/32_current_shell_role_mapping.md)
- [33_shell_snapshot_schema.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/33_shell_snapshot_schema.md)
- [shell_snapshot_contract.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/shared_contracts/shell_snapshot_contract.md)
- [system_shell_esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/system_shell_esp32_blueprint.h)
- [system_shell_raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/system_shell_raspberry_pi_blueprint.py)
- [shell_snapshot_facade_esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/shell_snapshot_facade_esp32_blueprint.h)
- [shell_snapshot_facade_raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/skeletons/shell_snapshot_facade_raspberry_pi_blueprint.py)

## 4. Этап 3. `Irrigation v1`

Цель:

- довести полив до первого реального продуктового состояния на `ESP32`.

Что должно быть:

- зоны растений;
- датчики влажности;
- датчики среды;
- ручной запуск;
- базовый авто-режим;
- логирование;
- SD-данные;
- сервисные тесты полива.

Главное:

- полив должен мыслиться растениями, зонами и состояниями, а не только насосом и клапанами.

## 5. Этап 4. `Turret v1`

Цель:

- довести турель до первого понятного пользовательского состояния на `Raspberry Pi`.

Что должно быть:

- manual mode;
- automatic defense baseline;
- live FPV/manual operator entry;
- camera availability;
- range availability;
- turret actions: motion, sound, strobe, water;
- policy rules in `Settings`;
- `silent observation` and human-protection-ready policy hooks;
- блокировки и fault-поведение;
- связь с общим shell.

Важно:

- `Turret v1` не обязан сразу включать весь будущий vision-stack по максимуму;
- но должен быть понятен пользователю как модуль, а не как набор абстрактных runtime-флагов.

## 6. Этап 5. `Gallery v1`

Цель:

- дать единый user-facing explorer для всего сохраняемого контента и отчетов платформы.

Что должно быть:

- `Plants`;
- `Media`;
- `Reports`;
- shared virtual section без одного owner;
- mixed feed карточек из manual/laboratory истории;
- фильтры и owner-aware деградация при отсутствии peer-content.

Важно:

- отдельная user-facing страница `Logs` больше не считается продуктовым блоком;
- глубокая история действий должна собираться в `Gallery > Reports`.

## 7. Этап 6. `Laboratory v1`

Цель:

- дать тестировщикам и разработчикам отдельный безопасный контур проверки модулей.

Что должно быть:

- `Strobe` и `strobe_bench` как разные laboratory-входы одного семейства;
- сервисные тесты полива;
- сервисные сценарии турели;
- ручные диагностические команды;
- понятные блокировки и предупреждения;
- deep `Laboratory / Test Bench` contour;
- grouped tabs по hardware/function groups, а не по owner-level страницам;
- terminal, logs, graphs and reports.

## 8. Этап 7. Минимальные platform services для `v1`

Это не отдельные продуктовые направления, а поддержка продукта:

- минимальный sync;
- общий журнал событий;
- настройки;
- диагностика;
- задел под авторизацию.

Здесь важно не переусложнить:

- не строить “идеальную платформу на будущее” раньше времени;
- не плодить внутренние сущности без прямой пользы для `v1`.

## 9. Этап 8. Уточнение железа под реальную интеграцию

После продуктовой фиксации:

- подтверждаем workbook `docs/smart_platform_workshop_inventory.xlsx` как hardware source of truth;
- подтверждаем `v1` набор компонентов;
- делаем локальный `ESP32` pin/power scope;
- делаем turret hardware map для `Raspberry Pi`;
- подключаем реальные драйверы по подтвержденной схеме.

Только на этом этапе hardware-документы становятся обязательными.

## 10. Этап 9. Сквозная интеграция и проверка

Финальная цель:

- оба узла работают в одной локальной сети;
- shell выглядит одинаково;
- handoff работает предсказуемо;
- `Irrigation`, `Turret`, `Gallery` и `Laboratory` проверены по сценариям;
- деградация и аварийные блокировки ведут себя понятно.

## 11. Что считать перегибом

Признаки, что мы снова уходим не туда:

- верхний roadmap состоит из внутренних слоев, а не из пользовательских блоков;
- простая задача требует обсуждения пяти backend-сущностей;
- один и тот же смысл дублируется как “модуль”, “runtime”, “service”, “hardware profile” на одном уровне;
- пользователю сложно понять, что вообще войдет в `v1`.

Если это происходит, нужно возвращаться к `26_v1_product_spec.md`.

## 12. Практический вывод для текущего этапа

Да, на этом этапе уже имеет смысл:

- сначала обозначить архитектуру и крупные классы;
- сделать skeleton-файлы и короткие описания обязанностей;
- и только после этого продолжать глубокую разработку.

То есть текущий режим, в котором мы сразу глубоко реализуем очередной внутренний слой, больше не оптимален.

## 13. Переход К Модульной Разработке

После фиксации skeleton-слоя и product-level `v1` документации дальнейшая глубокая работа должна идти по одному продуктовому блоку за чат.

Рекомендуемый порядок:

1. `System Shell v1`
2. `Irrigation v1`
3. `Turret v1`
4. `Gallery v1`
5. `Laboratory v1`

После этого:

6. возврат к общей координации;
7. real hardware docs;
8. live integration;
9. итоговая уборка проекта и donor-layer cleanup после подтвержденной выборочной миграции.

Переходный документ для этого режима:

- [34_modular_chat_transition_plan.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/34_modular_chat_transition_plan.md)
