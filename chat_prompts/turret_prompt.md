# Turret Prompt

Используй этот файл для работы только с `Turret`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за модуль `Turret`.

Текущий implementation baseline использует временный controller profile на `Raspberry Pi`, но это не считается вечной архитектурной истиной модуля.

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
2. `knowledge_base/README.md`
3. `knowledge_base/11_turret_module.md`
4. `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`
5. `knowledge_base/08_safety_acceptance_and_field_operations.md`
6. `knowledge_base/16_hardware_component_profiles.md`
7. `knowledge_base/17_open_questions_and_migration.md`, если нужен historical migration status или карта прошлых переносов

Практическое правило:

- legacy donor sources для `Turret` больше не входят в active workspace и primary reading order;
- если в `knowledge_base/11_turret_module.md` и `knowledge_base/16_hardware_component_profiles.md` все еще есть конкретный unresolved gap, сначала смотреть migration ledger, а затем текущий код, тесты и hardware companion sources;
- если historical migration note расходится с active canon, сильнее становится `knowledge_base/11_turret_module.md` и связанный hardware canon.

## Установленные Истины

- `Turret` не привязан навсегда к `Raspberry Pi`.
- Текущий временный controller profile для `Turret` = `Raspberry Pi`.
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
  - attack_audio
  - voice_fx
  - water

- `attack_audio` и `voice_fx` являются раздельными contour-ами, а не одним плоским `audio` actuator.
- legacy alias `piezo` допустим только как compatibility binding name для `attack_audio`, а не как отдельная active family.

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

## Focused Audio Trigger

Если задача уходит в один из следующих срезов, после этого prompt-а переходить в `turret_audio_prompt.md`:

- split contract `attack_audio / voice_fx`;
- saved baseline vs local draft для audio внутри `Laboratory`;
- `Settings` truth для attack scenario, channel levels, talkback и effect baseline;
- FPV talkback/effect UX, operator HUD audio summaries или shell audio token;
- detailed audio scenario matrix, transport closure или storage/source contract для turret audio assets.

## Keep / Adapt / Rewrite

- `keep`: то, что уже держит truthful turret ownership, safety и mode semantics;
- `adapt`: то, что полезно, но требует лучшей ясности manual/automatic или readiness wording;
- `rewrite`: то, что имитирует магическую готовность, ломает interlock truth или разрывает связь между mode UX и runtime model.

## Open TODO / TBD

### TODO

- довести product-ready объяснение readiness и blocked reasons;
- укрепить связь capture -> `Gallery > Media` -> `Gallery > Reports`;
- довести unified mode-switch contract между `Manual` и `Automatic`.
- не возвращаться к flat `sound / piezo / audio` wording в docs, prompts и коде; split audio truth углублять через `turret_audio_prompt.md`.

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
