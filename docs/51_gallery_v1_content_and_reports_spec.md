# Спецификация контента и отчетов `Gallery v1`

Этот документ фиксирует подробную спецификацию для `Gallery`.

Его задача:

- отделить `Gallery` от низкоуровневой диагностики хранилища;
- зафиксировать структуру `Plants`, `Media`, `Reports`;
- перестать смешивать `Reports` со свидетельствами `Laboratory`;
- описать модель общего обозревателя так, чтобы она оставалась правдивой и в single-node, и в dual-node режимах.

## 1. Роль `Gallery`

`Gallery` — это глобальный пользовательский обозреватель сохраняемого контента платформы.

Он должен:

- открывать весь пользовательский контент через одну понятную поверхность;
- собирать local и peer sources в один понятный обозреватель;
- быть общим виртуальным разделом без одного owner на уровне самой страницы;
- оставаться работоспособным даже если доступен только один узел.

`Gallery` не является:

- сырой браузер хранилища;
- заменой `Content Storage` diagnostics surface;
- просмотрщиком полного дампа backend-логов;
- рабочим пространством свидетельств `Laboratory`.

## 2. Модель маршрутов и shell

Фиксируем:

- пользовательская страница: `Gallery`;
- канонический путь: `/gallery`;
- семантика владельца: общий / виртуальный раздел;
- top-level tabs: `Plants`, `Media`, `Reports`.

Если peer-source отсутствует:

- `Gallery` не скрывается;
- локальный срез остается доступным;
- недоступные source groups маркируются явно и спокойно.

## 3. `Plants`

`Plants` — это не только список имен растений.

Этот раздел должен включать:

- plant catalog;
- care profiles;
- descriptive notes;
- plant-related reference data;
- базу для irrigation recommendations и future garden scenarios.

`Plants` должен ощущаться скорее как curated library, чем как file browser.

## 4. `Media`

`Media` объединяет:

- camera captures;
- медиа, созданные оператором;
- plant photos;
- turret-related recordings;
- engineering reference materials для `Laboratory`.

Внутри `v1` минимум нужны подгруппы:

- `Videos`
- `Pictures`

В `Media` должны жить:

- user-facing фото и видео из `Manual FPV`;
- записи product-level событий, если они действительно создают media artifact;
- справочные фото компонентов;
- схемы подключения и другие визуальные справочные материалы.

Последние две группы важны, потому что `Gallery > Media` является слоем визуальных справочных материалов для `Laboratory`.

## 5. `Reports`

`Reports` — это краткая пользовательская история реально выполненных системой действий.

Это не:

- laboratory session archive;
- state-table storage;
- console feed;
- backend log dump.

`Reports` должны показывать:

- короткую хронологическую ленту;
- семантику действия и результата;
- семантику причины и триггера;
- необязательный прикрепленный артефакт, если действие действительно создало медиа или текстовый артефакт.

## 6. Типы записей в `Reports`

Минимальный набор entry types для `v1`:

- irrigation action result;
- turret action result;
- manual operator action result;
- media capture result;
- заметку оператора как часть общей ленты.

`operator note` не выделяется в отдельный модуль.

Он живет как тип report entry.

## 7. Обязательные Поля `Reports`

Обязательный минимум:

- `action_type`
- `owner_node_id`
- `started_at`
- `trigger_reason`
- `result`
- `parameter_summary`, если применимо

Допустимые дополнительные поля:

- `entry_type`
- `source_surface`
- `source_mode`
- `related_action_id`
- attached artifact metadata
- short duration, если она действительно полезна пользователю

## 8. Что Не Должно Попадать В `Reports` По Умолчанию

Не должны автоматически материализоваться как записи отчетов:

- laboratory console output;
- intermediate calibration values;
- pass/warn/fail notes каждого bench-step;
- internal state-table rows;
- каждое service/engineering действие только потому, что оно произошло внутри `Laboratory`.

Если событие не имеет смысла на уровне продукта для пользовательской истории, его место остается внутри сессионного слоя `Laboratory` или во внутреннем platform log.

## 9. Explorer And Filter Model

`Gallery` не должен быть плоской лентой всего подряд.

Нужны:

- разделение по вкладкам между `Plants`, `Media`, `Reports`;
- filters внутри `Reports` по типу события;
- source availability markers;
- модель поиска и сортировки, не разрушающая понятность хронологии;
- честная смешанная подача local и peer content.

`Reports` должны читаться быстро:

- сначала действие;
- затем время;
- затем причина или триггер;
- затем результат.

## 10. Модель хранения и честность владельца

`Gallery` как страница общего и виртуального уровня, но каждый объект хранения сохраняет своего фактического owner.

Это означает:

- local slice и peer slice могут сосуществовать в одном explorer;
- интерфейс может показывать общий вид без потери правдивых метаданных владельца;
- недоступный peer не должен маскироваться под empty local state.

`Gallery` использует зеркальную модель хранения контента из общей content-стратегии, но пользовательская страница не должна выглядеть как техническая проверка `content_root`.

## 11. Граница `Gallery` и диагностики хранилища

`Content Storage` или аналогичная diagnostics surface могут существовать.

Но они нужны для:

- readiness check;
- copy/open/path operations;
- low-level storage inspection.

Они не должны становиться:

- главным пользовательским разделом контента;
- top-level shell page вместо `Gallery`.

## 12. Mobile And Desktop Expectations

`Gallery` должен работать и на телефоне, и на настольном экране, но с разным ощущением плотности.

Нужно сохранить:

- более библиотечную подачу для `Plants` и `Media`;
- быструю модель просмотра для `Reports`;
- отсутствие ощущения поломанной страницы, когда peer content недоступен.

## 13. Связь С `Laboratory`

Связь между `Gallery` и `Laboratory` двусторонняя, но не симметричная.

`Gallery` помогает `Laboratory` через:

- reference photos;
- wiring diagrams;
- optional media artifacts.

`Laboratory` помогает `Gallery` только там, где инженерное действие создает пользовательский артефакт или продуктово значимую короткую запись.

## 14. Что Нельзя Потерять При Дальнейшей Переписи

- Нельзя упрощать `Gallery` до:

- сырого файлового браузера;
- single-owner page;
- приемника отчетов для всей laboratory-телеметрии;
- страницы диагностики хранилища с косметическим переименованием.

Если новый документ или новый UI делает что-то из этого, он конфликтует с canonical model `Gallery`.
