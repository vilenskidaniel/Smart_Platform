# 03. Platform Architecture And Module Relationships

## Роль Файла

Этот файл должен объяснять архитектуру системы глазами человека: какие есть слои, какие есть модули и как они связаны.

## Статус

- текущий статус: `active draft`

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- specific legacy donor paths больше не считаются обязательным reading path для этого active file.

## Settled Truths

- связи между модулями описываются как связи ролей и потоков, а не как жесткая привязка к одной плате

## 1. Архитектурные Слои Платформы

Архитектуру `Smart Platform` в активном каноне читаем сверху вниз через четыре слоя:

1. user-facing product surfaces;
2. shared platform services;
3. runtime and control layer;
4. component and hardware layer.

`User-facing product surfaces` — это `Platform Shell`, `Irrigation`, `Turret`, `Laboratory`, `Gallery` и `Settings`.

`Shared platform services` — это синхронизация, хранение, общие registries, event/report plumbing, shell snapshots, диагностика и другие поддерживающие контуры.

`Runtime and control layer` — это coordinators, safety checks, drivers, wake/power logic, command execution и inter-node transport.

`Component and hardware layer` — это реальные платы, сенсоры, приводы, камеры, дисплеи, насосы, клапаны и другие физические элементы.

Главное правило: нижний слой реализует верхний, но не должен подменять собой продуктовый язык.

### Product-First Expansion Rule

Архитектурное развитие проекта нужно читать и разворачивать product-first, а не через рост внутренних слоев ради самих слоев.

Historical sequencing reminder, который остается полезным и после migration:

1. `Platform Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Shared platform services развиваются только в той мере, в какой они нужны этим user-facing blocks.

Практический engineering rule этого режима:

- сначала фиксировать архитектуру сверху вниз;
- затем обозначать роли, ownership и крупные class surfaces;
- после этого добавлять skeletons и короткие обязанности;
- и только потом углубляться в большие runtime methods.

Это не заменяет current delivery plan, но защищает active architecture canon от возврата к layer-first sprawl.

## 2. Главные Модули И Их Роли

`Platform Shell`:

- единая точка входа;
- общий визуальный язык;
- owner-aware доступность, handoff и объяснение деградации.

`Irrigation`:

- пользовательский модуль ухода и полива;
- работает с зонами, датчиками, water paths, ручным и базовым automatic behavior.

`Turret`:

- модуль наблюдения, операторского управления и реагирования;
- объединяет sensing, operator surfaces, motion/action families и policy-sensitive behavior.

`Laboratory`:

- инженерное рабочее пространство для тестирования, квалификации и ввода в работу;
- не подменяет `Settings` и не является пользовательской отчетной лентой.

`Gallery`:

- shared user-facing explorer для контента и краткой истории реальных действий;
- не зависит от одного вечного owner как product page.

`Settings`:

- постоянная системная истина для правил, профилей, shared preferences и registries;
- получает инженерные результаты только через явный путь подтверждения.

## 3. Shared Services И Общие Контуры

В архитектуре есть общие контуры, которые поддерживают модули, но не являются отдельными продуктами:

- `sync core` и inter-node exchange;
- storage, content library и mirror logic;
- shell snapshot и heartbeat/state distribution;
- persistent registries и settings application;
- event logging и report plumbing;
- diagnostics, power/wake supervision и safety-support services.

Эти сервисы существуют для модулей и оболочки. Они не должны разрастаться в параллельную продуктовую навигацию.

## 4. Связи Между Модулями

- `Platform Shell` знает доступность всех user-facing контуров и показывает их единым языком состояний.
- `Irrigation` и `Turret` отдают shell-слою свои truth, статусы и причины блокировок, но не теряют модульную автономию.
- `Laboratory` использует component and module profiles, может брать справочные изображения и схемы из `Gallery`, но не выгружает туда автоматически свою сессионную хронологию.
- `Settings` хранит persistent truth для shared preferences, policies и подтвержденных профилей; `Laboratory` может только подготовить или проверить эти значения перед явным сохранением.
- `Gallery > Reports` получает короткие product-level события от модулей и системных сценариев, а не полный лабораторный журнал.

## 5. Временные Controller Profiles И Заменяемость Центральных Узлов

Активный канон строится role-first, а не board-first.

Для текущего baseline используем две центральные роли:

- `always-on I/O role` для дешевых по энергии задач, локального полива, wake-supervision и fallback shell;
- `turret compute role` для тяжелой turret-family логики, vision/analysis и media-heavy workflows.

Сегодня эти роли физически реализованы как:

- `ESP32` для `always-on I/O role`;
- `Raspberry Pi` для `turret compute role`.

Но это implementation baseline, а не вечное определение архитектуры. Если физический host поменяется, модульные роли, user-facing разделы и общая ownership-модель не должны переписываться заново.

## 6. Линии Данных, Состояния И Команд

Командная линия:

1. viewer отправляет действие через текущий host;
2. host маршрутизирует действие owner-side runtime соответствующего модуля;
3. owner-side runtime выполняет safety checks, принимает решение и возвращает результат.

Линия состояния:

1. owner-side runtime формирует truthful module state;
2. shell snapshots, heartbeat и sync разносят эту truth по другим поверхностям;
3. viewer видит одинаковую смысловую картину независимо от host-side entrypoint.

Линия контента и истории:

1. модуль или сервис пишет локальный content/event artifact;
2. shared storage/sync слой публикует его в общую картину доступности;
3. `Gallery` показывает локальный или смешанный срез в зависимости от доступности источников.

## 7. Где Граница Между Модулем И Платформой

`Модуль` отвечает за:

- свой пользовательский сценарий;
- свои safety-sensitive команды;
- свою runtime truth;
- свои component profiles и режимы исполнения.

`Платформа` отвечает за:

- общую оболочку и навигацию;
- shared UI language;
- persistent settings/registries;
- sync, storage, shell snapshots и межмодульную согласованность;
- объяснение деградации и handoff между owner-side routes.

Пограничное правило:

- если сущность выражает пользовательский смысл и командный контур, это модуль;
- если она обслуживает несколько модулей и не должна жить отдельной user-facing жизнью, это platform service или implementation layer.

## Open Questions

- какие связи стоит оформить как отдельные схемы Mermaid прямо в файле

## TODO

- перенести архитектурный каркас без migration-waterfall

## TBD

- глубина визуальных схем для человека вне кода
