# Gallery Prompt

Используй этот файл для работы только с `Gallery`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за общий виртуальный раздел `Gallery`.

Он покрывает:

- `Plants`;
- `Media`;
- `Reports`;
- смешанную ленту;
- provenance и видимость зеркальных источников;
- связь с storage-contract без превращения `Gallery` в storage-inspector.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/13_gallery_module.md`
4. `knowledge_base/07_data_registry_storage_and_persistence.md`
5. `knowledge_base/15_platform_services_and_shared_content.md`
6. `knowledge_base/08_safety_acceptance_and_field_operations.md`
7. `knowledge_base/17_open_questions_and_migration.md`, если нужен historical migration status или карта прошлых переносов

Практическое правило:

- legacy donor sources для `Gallery` больше не входят в active workspace и primary reading order;
- если в active canon еще есть конкретный пробел вокруг report detail, mirrored storage residue или safety wording, сначала смотреть migration ledger, а затем текущие storage и content contracts;
- если historical migration note расходится с active canon, сильнее становятся `knowledge_base/13_gallery_module.md`, `knowledge_base/07_data_registry_storage_and_persistence.md` и `knowledge_base/15_platform_services_and_shared_content.md`.

## Установленные Истины

- `Gallery` — общий виртуальный раздел без одного владельца на уровне shell-page.
- Пользовательские вкладки:
  - `Plants`
  - `Media`
  - `Reports`
- Весь пользовательский сохраняемый контент открывается через `Gallery`.
- `Gallery > Reports` — канонический обозреватель автономно и системно зафиксированной пользовательской истории продукта, а не ручных laboratory-записей.
- При отсутствии peer-owner `Gallery` не исчезает, а честно показывает локальный срез и отсутствие peer-content.
- `Gallery` не должен превращаться в сырой storage-inspector.

## Активный Опрос Пользователя

Иди от общего к частному:

1. Что человек пытается найти: растение, media artifact, отчет или mixed history.
2. Что он должен понимать о происхождении записи без чтения сырой технической метадаты.
3. Что делать в single-node и peer-missing состоянии.
4. Какие типы карточек должны быть самыми понятными на телефоне.
5. Что является автономно или системно зафиксированным product-level report, а что остается локальной записью сессии `Laboratory`.
6. Какие части уже хороши и идут в `keep`.
7. Что оставить как `TODO` или `TBD`.

## Каркас Работы

Сначала удерживать skeleton:

- модель вкладок;
- модель provenance;
- локальная и зеркальная видимость;
- иерархия report-карточек;
- семейства `Plants` и `Media`;
- degraded- и empty-состояния.

Затем наращивать фильтры, detail-view слои, browsing-patterns и более богатые collections.

## Keep / Adapt / Rewrite

- `keep`: то, что уже дает shared explorer и честную историю действий;
- `adapt`: то, что полезно, но требует лучшей card hierarchy, provenance wording или mobile readability;
- `rewrite`: то, что сводит `Gallery` к storage/debug page или теряет source metadata.

## Open TODO / TBD

### TODO

- довести mixed feed до еще более читаемой пользовательской ленты;
- материализовать более богатый browsing для `Plants` и `Media` поверх сырого списка;
- укрепить provenance wording для mirrored entries.

### TBD

- окончательная модель preview для audio и других non-photo media families;
- будущая глубина curated collections и saved filters.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если изменение задевает:

- контракты синхронизации и зеркального контента;
- `Laboratory` export rules;
- общие настройки для media или library behavior;
- shell summaries и быстрые входы в `Reports`.
