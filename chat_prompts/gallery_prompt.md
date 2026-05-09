# Gallery Prompt

Используй этот файл для работы только с `Gallery`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за shared virtual section `Gallery`.

Он покрывает:

- `Plants`;
- `Media`;
- `Reports`;
- mixed feed;
- provenance и mirrored visibility;
- связь со storage contract без превращения в storage inspector.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/13_gallery_module.md`
4. `knowledge_base/07_data_registry_storage_and_persistence.md`
5. `knowledge_base/15_platform_services_and_shared_content.md`
6. `knowledge_base/08_safety_acceptance_and_field_operations.md`
7. `knowledge_base/17_open_questions_and_migration.md`, если нужен explicit donor status или unresolved residue map

Практическое правило:

- legacy donor sources для `Gallery` больше не входят в primary reading order;
- если active canon still has a concrete gap around report detail, mirrored storage residue or safety wording, сначала смотреть migration ledger и только потом открывать donor residue точечно;
- если donor detail расходится с active canon, сильнее становятся `knowledge_base/13_gallery_module.md`, `knowledge_base/07_data_registry_storage_and_persistence.md` и `knowledge_base/15_platform_services_and_shared_content.md`.

## Установленные Истины

- `Gallery` — shared virtual section без одного owner на уровне shell-page.
- User-facing tabs:
  - `Plants`
  - `Media`
  - `Reports`
- Весь user-facing сохраняемый контент открывается через `Gallery`.
- `Gallery > Reports` — канонический viewer автономно и системно зафиксированной пользовательской истории продукта, а не ручных laboratory-записей.
- При отсутствии peer-owner `Gallery` не исчезает, а честно показывает локальный slice и отсутствие peer-content.
- `Gallery` не должен превращаться в raw storage inspector.

## Активный Опрос Пользователя

Иди от общего к частному:

1. Что человек пытается найти: растение, media artifact, отчет или mixed history.
2. Что он должен понимать о происхождении записи без чтения сырой технической metadata.
3. Что делать в single-node и peer-missing состоянии.
4. Какие типы карточек должны быть самыми понятными на телефоне.
5. Что является автономно или системно зафиксированным product-level report, а что остается локальной laboratory-записью сессии.
6. Какие части уже хороши и идут в `keep`.
7. Что оставить как `TODO` или `TBD`.

## Каркас Работы

Сначала удерживать skeleton:

- tab model;
- provenance model;
- local vs mirrored visibility;
- report card hierarchy;
- plants/media families;
- degraded and empty states.

Затем наращивать filters, detail views, browsing patterns и richer collections.

## Keep / Adapt / Rewrite

- `keep`: то, что уже дает shared explorer и честную историю действий;
- `adapt`: то, что полезно, но требует лучшей card hierarchy, provenance wording или mobile readability;
- `rewrite`: то, что сводит `Gallery` к storage/debug page или теряет source metadata.

## Open TODO / TBD

### TODO

- довести mixed feed до еще более читаемой user-facing ленты;
- материализовать richer `Plants` и `Media` browsing beyond raw lists;
- укрепить provenance wording для mirrored entries.

### TBD

- окончательная модель preview для audio и других non-photo media families;
- будущая глубина curated collections и saved filters.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если изменение задевает:

- sync and mirrored content contracts;
- `Laboratory` export rules;
- shared settings for media or library behavior;
- shell summaries and quick links into `Reports`.
