# 02. System Terms And Design Rules

## Роль Файла

Этот файл должен зафиксировать единый словарь сущностей, ролей и проектных правил, чтобы человек и чат не плодили несколько смыслов для одной вещи.

## Статус

- текущий статус: `active draft`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/foundation_prompt.md` остается prompt-layer companion source для синхронизации терминов и prompt-layer wording.

## Установленные Истины

- идти от общего к частному
- один термин = один смысл
- controller profile не равен вечному owner модуля

## 1. Сущности Платформы

В активном каноне различаем следующие сущности:

- `product module`: пользовательский смысловой контур, например `Irrigation` или `Turret`;
- `user-facing section`: страница или раздел оболочки, например `Gallery`, `Laboratory`, `Settings`;
- `platform service`: поддерживающий слой, который нужен нескольким модулям, но не считается отдельным продуктом;
- `component`: физический или логический узел, который тестируется, подключается или используется внутри модуля;
- `controller profile`: текущий способ управления компонентом или модулем через конкретный runtime-host;
- `registry entry`: сохраненная системная запись, профиль или scaffold, который живет в persistent truth;
- `session record`: временная инженерная запись внутри `Laboratory`;
- `report record`: краткое product-level событие в `Gallery > Reports`.

## 2. Различие Между Модулем, Компонентом, Сервисом И Controller Profile

`Модуль`:

- выражает пользовательскую цель и сценарий;
- живет на уровне продукта и навигации;
- не равен конкретной плате, библиотеке или временному runtime-host.

`Компонент`:

- это сенсор, привод, камера, дисплей, насос, клапан или другой building block;
- он может входить в разные модули или тестироваться отдельно в `Laboratory`.

`Platform service`:

- дает общую функцию нескольким контурам;
- не должен разрастаться в отдельный user-facing продукт без отдельного решения.

`Controller profile`:

- описывает текущий способ исполнения, подключения и управления;
- может быть временным;
- не должен подменять собой смысл модуля.

Правило для нового канона:

- нельзя писать `Irrigation = ESP32` или `Turret = Raspberry Pi` как вечную архитектурную истину;
- правильно писать, что текущий implementation baseline использует controller profile на соответствующем runtime-host.

## 3. Host, Viewer И Runtime Topology

В активной терминологии различаем:

- `viewer`: устройство и браузерная сессия, через которые пользователь видит платформу;
- `host`: узел, который в данный момент отдает shell или страницу viewer-у;
- `owner-side runtime`: сторона, которая реально исполняет команду и отвечает за truth данного модуля в текущей topology;
- `peer`: соседний runtime-host, который может быть доступен, недоступен или деградирован.

Из этого следуют правила:

- viewer может быть один, а host и owner-side runtime могут различаться;
- host не должен притворяться owner-side runtime, если команда реально исполняется на peer-стороне;
- peer-owned разделы остаются видимыми даже при недоступности owner-side runtime;
- полная topology и handoff-модель описываются глубже в `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`.

## 4. Product Truth vs Implementation Baseline vs Temporary Profile

`Product truth`:

- пользовательские роли модулей;
- границы `v1`;
- owner-aware shell behavior;
- разделение между `Laboratory`, `Settings` и `Gallery > Reports`.

`Implementation baseline`:

- текущая подтвержденная рабочая сборка;
- текущие runtime-hosts, платы, hardware combinations и software routes;
- то, что уже реально собрано и проверено.

`Temporary profile`:

- экспериментальный, bench, laboratory или переходный способ управления;
- допустим как рабочий этап, но не должен автоматически становиться каноном.

Практическое правило:

- если что-то нужно для сегодняшнего bring-up, это еще не делает его вечным архитектурным смыслом;
- если что-то выражает устойчивую пользовательскую роль и системное правило, это должно быть поднято в active canon.

## 5. Общие Правила Именования

- один термин = один смысл;
- user-facing имя приоритетнее legacy stage-alias;
- `Laboratory` является каноническим пользовательским именем;
- `service_test`, `diagnostics`, `test bench` и похожие названия допустимы только как historical или implementation aliases;
- `blocked` означает внешнюю недоступность по контексту;
- `locked` означает явный policy/access/safety запрет;
- `offline` означает физически или runtime-недоступный node, owner или hardware family и не должен подменять `blocked`, `locked` или более точное degraded explanation;
- `service` не должен становиться отдельной shell-state семантикой, даже если service/test workflow существует как режим работы;
- historical wording вроде `Service / Test` и `Background Sync / Telemetry` допустимо только как compatibility reminder для priority/order discussions, а не как новая active shell-state vocabulary;
- `persistent truth` живет в `Settings` и registries;
- временное инженерное знание живет в `Laboratory`;
- краткие product-level event records живут в `Gallery > Reports`.

## 6. Регистры, Индексы И Идентификаторы

На уровне активного канона используем следующие классы записей:

- `registry`: persistent system truth, профили, scaffolds, подтвержденные значения;
- `index`: навигационный или обзорный список сущностей, доступных системе;
- `session record`: временная laboratory-запись;
- `report record`: короткая запись о реально выполненном автономном или системно зафиксированном действии;
- `content/media entry`: пользовательский или справочный файл с owner/storage provenance.

Базовые правила идентификаторов:

- идентификатор должен быть стабильным и machine-readable;
- display label и stable id не должны смешиваться;
- временный laboratory session id не должен автоматически становиться persistent registry id;
- owner/storage provenance должен храниться отдельно от user-facing названия.

## 7. Правила Donor-Thinning И Единого Канона

- новый активный смысл переносится в `knowledge_base/`, а не остается жить только в переписке или старом доноре;
- после переноса donor-источник нужно удалить, сократить до заглушки или явно пометить как donor-only/historical;
- нельзя оставлять старый файл рядом как будто он все еще равноправен новому канону;
- перенос делается через вырезание и замещение, а не через бесконечное копирование поверх старого слоя;
- при конфликте между active canon и donor-источником активной истиной считается `knowledge_base/`.

## 8. Пограничные Правила Для Состояний И Переходов

- единая shell-правда идет backend-first;
- `active` не подменяет `online / ready`;
- `pending` обычно выражается через `attention` с явной причиной, а не через отдельное состояние-государство;
- `blocked` и `locked` различаются и текстом, и визуально;
- короткая причина и следующий шаг должны быть видны на экране, а не прятаться только в hover;
- `Laboratory` не должен молча менять persistent truth;
- `Settings` получает результат `Laboratory` только через явный `save/apply` path;
- `Gallery > Reports` не должен автоматически становиться хранилищем полной laboratory-хронологии.

## Open Questions

- какие registry namespaces стоит зафиксировать уже на уровне документа, а не только в коде

## TODO

- собрать единый словарь без повторов и stage-алиасов как живой правды

## TBD

- финальный формат human-readable vs machine-readable naming conventions
