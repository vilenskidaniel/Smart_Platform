# Правила Работы Из Других Чатов

Этот файл нужен, чтобы разные чаты не тянули проект в разные стороны и не смешивали product-level блоки с внутренними техническими слоями.

## Где Лежат Координационные Prompt-Файлы

Канонические вводные prompt-файлы для новых модульных чатов хранятся в каталоге:

- `chat_prompts/`

Первый такой файл:

- `chat_prompts/laboratory_chat_bootstrap_prompt.md`

Если координационный чат создает новый prompt для отдельного продуктового блока, он должен попадать именно туда, а не смешиваться с постоянными product briefs.

## Что читать в первую очередь

Перед любыми изменениями нужно открыть:

1. [README.md](README.md)
2. [docs/smart_platform_workshop_inventory.xlsx](docs/smart_platform_workshop_inventory.xlsx)
3. [docs/26_v1_product_spec.md](docs/26_v1_product_spec.md)
4. [docs/01_product_decisions.md](docs/01_product_decisions.md)
5. [docs/02_system_architecture.md](docs/02_system_architecture.md)
6. [docs/05_ui_shell_and_navigation.md](docs/05_ui_shell_and_navigation.md)
7. [docs/39_design_decisions_and_screen_map.md](docs/39_design_decisions_and_screen_map.md)
8. [docs/40_system_shell_navigation_alignment.md](docs/40_system_shell_navigation_alignment.md)
9. [docs/09_master_design_plan.md](docs/09_master_design_plan.md)
10. [docs/34_modular_chat_transition_plan.md](docs/34_modular_chat_transition_plan.md)
11. [briefs/README.md](briefs/README.md)
12. только после этого нужный brief-файл

## Главные правила

- Один отдельный чат = один product-level блок.
- Если задача начинает тянуть второй большой блок, нужно остановиться, зафиксировать решение в docs и вынести следующий блок в отдельный чат.
- Для новой разработки `Smart Platform` рабочий корень — сам этот репозиторий.
- Для `ESP32` использовать `firmware_esp32/platformio.ini`.
- Для `Raspberry Pi` использовать каталог `raspberry_pi/`.
- Legacy bench/donor-репозитории использовать только как источник идей и выборочной миграции, а не как основной рабочий корень.
- Не склеивать старые проекты напрямую.
- Не переносить код без понимания его владельца и зоны ответственности.
- Аппаратный источник истины по наличию, ownership и power baseline - `docs/smart_platform_workshop_inventory.xlsx`.
- Не ломать правило одинакового дизайна на `ESP32` и `Raspberry Pi`.
- Не прятать недоступные разделы полностью: лучше показывать их как серые, но кликабельные с объяснением.
- User-facing имя инженерного контура — `Laboratory`.
- Внутреннее stage-name `Service/Test v1` можно сохранять в roadmap и техдоках.
- Отдельная user-facing страница `Logs` больше не считается product target:
  основной просмотр истории действий и отчетов идет через `Gallery > Reports`.
- Обязательно различать `product target` и `software baseline`.

## Что считается основными продуктовыми блоками

На верхнем уровне продукта основными считаются:

1. `System Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

А вот `sync`, `logs`, `settings`, `diagnostics`, `system core`, `driver layer`, `sensor pack` и похожие сущности нужно рассматривать как support-слои, а не как самостоятельные roadmap-направления.

Важно:

- `logs` как backend/service слой сохраняется;
- но user-facing история действий и отчетов должна собираться в `Gallery > Reports`, а не в отдельной верхнеуровневой странице.

## Когда нужно обновлять документы

Документы нужно обновлять, если меняется хотя бы одно из условий:

- владелец модуля;
- приоритет команд;
- синхронизация;
- состав страниц;
- доступность разделов на `ESP32` и `Raspberry Pi`;
- режимы `manual`, `automatic`, `service`, `fault`;
- hardware interlock и safety-логика;
- media/gellery/report структура.

## Как не потеряться в глубине

- Если речь идет о “втором пункте” модульной очереди, это `Irrigation v1`.
- Если речь идет про `Этап 2` master-plan, это `System Shell v1`.
- Если чат начинает уходить в слишком много внутренних сущностей, вернуться к [docs/26_v1_product_spec.md](docs/26_v1_product_spec.md).
- Если работа идет по shell/navigation drift, открыть [docs/40_system_shell_navigation_alignment.md](docs/40_system_shell_navigation_alignment.md).
- Если нужна карта перехода между чатами, открыть [docs/34_modular_chat_transition_plan.md](docs/34_modular_chat_transition_plan.md).
- Stage-документы и узкие контракты читать только после базовых product-level файлов.

## Полезная практика

- Добавлять пометки `TODO(stage-x)` там, где код еще не завершен.
- Указывать, какая часть пришла из старого проекта, а какая переписана заново.
- Для сложных мест писать не только что происходит, но и почему это так устроено.

## Guardrails Для Активных UI/Shell Чатов

- До работы по shell/home/bar сначала открыть [docs/48_browser_entry_and_host_launch.md](docs/48_browser_entry_and_host_launch.md) и [docs/49_shell_runtime_and_chat_guardrails.md](docs/49_shell_runtime_and_chat_guardrails.md).
- В runtime-модели всегда отдельно различать host node, module owner, current browser client и entry context.
- Не смешивать `host launch` и `browser entry` в одну сущность даже тогда, когда на `Windows` они выглядят как один пользовательский сценарий.
- При shared UI edits проверять не только source-файл, но и live-served asset на рабочем порту.
- Длинные JS-файлы править маленькими hunks в порядке следования кода, а не большими смешанными patch-блоками.
- После regression сначала вернуть рабочее поведение в этом же slice, и только потом расширять scope.
- Если пользователь ограничил задачу до конкретного runtime slice, например только PC/browser path, сначала закрыть именно его.
