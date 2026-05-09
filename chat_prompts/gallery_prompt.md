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
2. `docs/26_v1_product_spec.md`
3. `docs/29_shared_content_and_sd_strategy.md`
4. `docs/39_design_decisions_and_screen_map.md`
5. `docs/51_gallery_v1_content_and_reports_spec.md`
6. `docs/46_safety_risk_and_failure_matrix.md`
7. `docs/47_acceptance_and_validation_matrix.md`

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
