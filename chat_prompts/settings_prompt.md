# Settings Prompt

Используй этот файл для работы только с `Settings`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за `Settings` как центральную постоянную страницу состояния и конфигурации платформы.

Он покрывает:

- shared preferences;
- separation между host, viewer, platform nodes, modules, components и services;
- sync configuration;
- storage actions;
- constructor and registry flows;
- clear disabled and blocked explanations.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/14_settings_module.md`
4. `knowledge_base/06_shared_ui_contract.md`
5. `knowledge_base/07_data_registry_storage_and_persistence.md`
6. `knowledge_base/08_safety_acceptance_and_field_operations.md`
7. `knowledge_base/15_platform_services_and_shared_content.md`
8. `knowledge_base/17_open_questions_and_migration.md`, если нужен historical migration status или карта прошлых переносов

Практическое правило:

- legacy donor sources для `Settings` больше не входят в active workspace и primary reading order;
- если в active canon еще есть конкретный пробел вокруг save/apply detail, storage residue или safety wording, сначала смотреть migration ledger, а затем текущие storage, shell и settings contracts;
- если historical migration note расходится с active canon, сильнее становятся `knowledge_base/14_settings_module.md`, `knowledge_base/06_shared_ui_contract.md` и `knowledge_base/07_data_registry_storage_and_persistence.md`.

## Установленные Истины

- `Settings` — постоянная системная страница, а не свалка runtime diagnostics.
- Нужно отдельно различать:
  - host
  - viewer device
  - platform nodes
  - modules
  - components
  - system services
- Отдельной секции `Platform Nodes` в `Settings` быть не должно.
- Краткий физический статус плат живет в bar-панели.
- `Modules`, `Components` и `System Services` не смешиваются.
- Constructor — не декоративная заглушка: он должен вести к реальному registry/config flow.
- Shared preference `fullscreen` живет в `Settings`, но отражается и в bar-панели как та же самая истина.
- `Input helpers` или `ARM`-подобный режим тоже живут в `Settings` и bar-панели как общее состояние, но функционально относятся только к FPV- и operator-поверхностям и не должны отключать `Laboratory`.
- Новый constructor scaffold по умолчанию остается `simulated` или неподтвержденным, пока он не прошел явный путь подтверждения и применения.
- `Sync` управляется через `selected_domains`, `Auto` и `Manual review`.
- Storage actions идут только через preview/confirm и backend root-boundary checks.
- Настройки применяются optimistic-first.

## Активный Опрос Пользователя

Иди от общего к частному:

1. Что пользователь хочет изменить: вид интерфейса, поведение системы, модульную конфигурацию, storage или sync.
2. Что должно быть видно как текущее состояние, а что как редактируемая настройка.
3. Где нужно ясное disabled-state explanation.
4. Что должно оставаться локальным, а что общим.
5. Что уже работает хорошо и идет в `keep`.
6. Что оставить как `TODO` или `TBD`.

## Каркас Работы

Сначала удерживать skeleton:

- page role;
- information architecture;
- separation между runtime truth и persistent choices;
- shared preferences между `Settings`, bar-панелью и рабочими страницами;
- modules/components/services split;
- sync and storage sections;
- constructor and save/apply semantics.

Затем наращивать детали controls, suggestions, tooltips и copy.

## Keep / Adapt / Rewrite

- `keep`: то, что уже честно держит persistent system role `Settings`;
- `adapt`: то, что полезно, но требует лучшего разделения сущностей, clearer wording или stronger apply semantics;
- `rewrite`: то, что смешивает hardware owners, runtime diagnostics и persistent choices.

## Open TODO / TBD

### TODO

- довести финальную IA `Settings` без возврата технической свалки;
- укрепить `Constructor -> registry -> applied settings` contract;
- довести shared-vs-local wording для sync and settings continuity.

### TBD

- окончательная multi-node precedence model для некоторых shared preferences;
- полная audit-trail модель для больших registry- и profile-изменений.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если изменение задевает:

- shared preferences across nodes;
- `Laboratory -> Settings` save/apply semantics;
- настройки `Gallery` и provenance для `Reports`;
- shell-level language, theme, fullscreen, input-helper or launch-context contracts.
