# Turret Prompt

Используй этот файл для работы только с `Turret`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за owner-side turret module на `Raspberry Pi`.

Он покрывает:

- `Manual`;
- `Automatic`;
- readiness и degraded states;
- action families;
- media capture;
- связь с shell, `Laboratory`, `Gallery > Reports` и safety.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `docs/26_v1_product_spec.md`
3. `docs/37_turret_product_context_map.md`
4. `docs/39_design_decisions_and_screen_map.md`
5. `docs/45_rpi_turret_hardware_and_io_map.md`
6. `docs/46_safety_risk_and_failure_matrix.md`
7. `docs/47_acceptance_and_validation_matrix.md`
8. `briefs/turret_bridge_module.md`

## Установленные Истины

- Owner `Turret` = `Raspberry Pi`.
- Product route = `/turret`.
- Service route = `/service/turret`.
- `Manual`, `Automatic`, `Laboratory` и `warm standby` — части одной owner-side модели.
- Physical emergency interlock — источник истины для turret-sensitive branches.
- Primary camera baseline = `IMX219 130°`.
- Owner-side range baseline = `TFmini Plus`.
- `HC-SR04`-class — только laboratory profile, а не owner-side замена.
- Базовые action families:
  - motion
  - strobe
  - sound / piezo / audio
  - water

## Активный Опрос Пользователя

Иди от общего к частному:

1. Что пользователь или оператор хочет получить: наблюдение, ручное управление, automatic policy, readiness explanation или safety clarity.
2. Что должно быть видно при degraded или blocked состоянии.
3. Как объяснять readiness по camera, range, vision и action families.
4. Что должно считаться product-level consequence для `Gallery > Reports`.
5. Что должно оставаться внутри `Laboratory`.
6. Что уже хорошо работает и идет в `keep`.
7. Что пока оставить как `TODO` или `TBD`.

## Каркас Работы

Сначала удерживать skeleton:

- mode model;
- readiness model;
- interlock semantics;
- owner-aware handoff;
- action family visibility;
- capture/report consequences.

Затем наращивать UX, HUD, policies и детализацию состояний.

## Keep / Adapt / Rewrite

- `keep`: то, что уже держит truthful turret ownership, safety и mode semantics;
- `adapt`: то, что полезно, но требует лучшей ясности manual/automatic или readiness wording;
- `rewrite`: то, что имитирует магическую готовность, ломает interlock truth или разрывает связь между mode UX и runtime model.

## Open TODO / TBD

### TODO

- довести product-ready объяснение readiness и blocked reasons;
- укрепить связь capture -> `Gallery > Media` -> `Gallery > Reports`;
- довести unified mode-switch contract между `Manual` и `Automatic`.

### TBD

- финальная product-level форма FPV transport на реальном железе;
- будущая policy-матрица для richer automatic behavior;
- окончательный motion wake sensor baseline.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если изменение задевает:

- shell handoff;
- `Gallery > Reports` provenance;
- `Laboratory` service/qualification semantics;
- shared settings и policies;
- irrigation overlay или cross-module operator HUD language.