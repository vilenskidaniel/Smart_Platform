# Irrigation Prompt

Используй этот файл для работы только с `Irrigation`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за продуктовый модуль полива.

Текущий implementation baseline использует временный controller profile на `ESP32`, но это не считается вечной архитектурной истиной модуля.

Он покрывает:

- зоны;
- датчики почвы и среды;
- ручной полив;
- базовый automatic baseline;
- границу между product page и service slice;
- reports и overlay-последствия.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/10_irrigation_module.md`
4. `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`
5. `knowledge_base/08_safety_acceptance_and_field_operations.md`
6. `knowledge_base/16_hardware_component_profiles.md`
7. `knowledge_base/17_open_questions_and_migration.md`, если нужен historical migration status или карта прошлых переносов

Практическое правило:

- legacy donor sources для `Irrigation` больше не входят в active workspace и primary reading order;
- если в active canon еще есть конкретный пробел вокруг stage behavior, software baseline или current electrical residue, сначала смотреть migration ledger, а затем текущий код, тесты и hardware companion sources;
- если historical migration note расходится с active canon, сильнее становятся `knowledge_base/10_irrigation_module.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md` и `knowledge_base/16_hardware_component_profiles.md`.

## Установленные Истины

- `Irrigation` не привязан навсегда к `ESP32`.
- Текущий временный controller profile для `Irrigation` = `ESP32`.
- Product route = `/irrigation`.
- Service route = `/service/irrigation`.
- Подтвержденный baseline: `5` зон, `5` клапанов, `5` датчиков влажности почвы.
- Water path `Irrigation` = малый перистальтический насос + клапанный каскад растений.
- `Irrigation` не владеет turret water path `SEAFLO`.
- Модуль должен оставаться понятным и рабочим даже без `Raspberry Pi`.
- Automatic baseline выбирает самую сухую допустимую зону.
- Service/test действия не должны ломать product UX.

## Активный Опрос Пользователя

Иди от общего к частному:

1. Какой пользовательский результат нужен: быстрый ручной полив, понимание состояния зон, автоматизация или сервисная калибровка.
2. Что пользователь должен понимать о зоне без чтения raw diagnostics.
3. Как объяснять выбор automatic baseline.
4. Что должно считаться fault, degraded или blocked.
5. Что должно попадать в `Gallery > Reports`.
6. Что должно оставаться только service или laboratory-слоем.
7. Что уже хорошо работает и идет в `keep`.
8. Что пока оставить как `TODO` или `TBD`.

## Каркас Работы

Сначала удерживать skeleton:

- zone model;
- sensor truth;
- active run source;
- manual vs automatic behavior;
- service isolation;
- shell visibility;
- reports and overlay implications.

Затем наращивать детализацию UI, wording и сценариев.

## Keep / Adapt / Rewrite

- `keep`: то, что уже честно отражает зоны, сенсоры и owner behavior;
- `adapt`: то, что полезно, но требует лучшего объяснения automatic, faults или service boundary;
- `rewrite`: то, что смешивает product page с service console или ломает water-path truth.

## Open TODO / TBD

### TODO

- довести объяснение automatic decisions до user-facing уровня;
- укрепить границу `/irrigation` vs `/service/irrigation`;
- довести export product-level irrigation actions в reports trail.

### TBD

- глубина будущих plant-aware сценариев поверх current zone model;
- окончательная форма calibration UX для сенсоров и зон.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если изменение задевает:

- shell summaries;
- turret overlay;
- shared reports semantics;
- settings-backed irrigation profiles;
- sync или mirrored irrigation data.
