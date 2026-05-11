# Platform Shell Prompt

Используй этот файл для работы только с `Platform Shell`.

Читать вместе с `foundation_prompt.md`.

## Роль Модуля

Этот prompt отвечает за:

- домашнюю страницу `Smart Platform`;
- верхнюю bar-панель;
- launcher-карточки;
- shell navigation;
- truthful status language;
- entry context, host/viewer distinction и continuity между страницами.

Он не должен утягивать в глубокую проработку `Irrigation`, `Turret`, `Gallery`, `Laboratory` или `Settings`, если shell-слой можно улучшить отдельно.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/05_shell_navigation_and_screen_map.md`
4. `knowledge_base/06_shared_ui_contract.md`
5. `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`
6. `shared_contracts/shell_snapshot_contract.md`
7. `knowledge_base/17_open_questions_and_migration.md`, если нужен historical migration status или карта прошлых shell-переносов

Практическое правило:

- legacy donor sources для `Platform Shell` больше не входят в active workspace и основной порядок чтения;
- если в active canon еще есть конкретный пробел вокруг shell alignment, compatibility routes или implementation residue, сначала смотреть migration ledger, а затем текущий shell contract и реальные code anchors;
- если donor detail расходится с active canon, сильнее становятся `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/06_shared_ui_contract.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md` и `shared_contracts/shell_snapshot_contract.md`.

## Установленные Истины

- Домашняя страница называется `Smart Platform`, а не `Platform Shell`.
- Bar-панель несет правдивые статусы и быстрые действия.
- Полный bar остается видимым на рабочих страницах и во fullscreen-режиме; fullscreen уплотняет рабочую область, а не прячет shell.
- Laptop или desktop launch не считается отдельным hardware owner.
- Нужно честно различать `host launch`, `browser entry`, `module owner` и `current browser client`.
- Home surface показывает только главные пользовательские действия:
  - `Irrigation`
  - `Turret`
  - `Gallery`
  - `Laboratory`
  - `Settings`
- `Reports` открываются через `Gallery`, а не живут отдельной карточкой на home.
- Недоступные модули не скрываются, а остаются видимыми и объяснимыми.
- Bar-панель должна быть общей инфраструктурой для нескольких страниц, а не частным декором home screen.
- Кнопка `Home` в bar-панели остается всегда доступной как экстренный возврат на главную страницу и переход к дефолтному состоянию оболочки, заданному в `Settings`.
- Общие настройки `fullscreen` и `input helpers` живут и в `Settings`, и в bar-панели, а deep-pages должны читать их как одну истину.

## Активный Опрос Пользователя

Используй вопросы от общего к частному:

1. Что пользователь должен понимать на home сразу после открытия.
2. Какие статусы критичны в bar, а какие вторичны.
3. Что является action, а что только status.
4. Как вести себя на desktop, mobile и в fullscreen.
5. Какие blocked и degraded состояния обязаны объяснять себя сами.
6. Какие детали уже работают хорошо и должны попасть в `keep`.
7. Какие места лучше честно оставить как `TODO` или `TBD`.

Если вопрос не блокирует путь, предложи варианты, объясни последствия и выбери рекомендуемый default.

## Каркас Работы

Сначала собрать и удерживать skeleton:

- роль home page;
- роль bar-панели;
- home return contract;
- launcher hierarchy;
- статусные группы;
- поведение tooltip и fullscreen;
- общее поведение input-helper;
- continuity между страницами.

Затем наращивать детализацию.

## Keep / Adapt / Rewrite

- `keep`: то, что уже дает truthful status model и не ломает навигацию;
- `adapt`: то, что полезно, но требует перестройки wording, группировки, layout или continuity;
- `rewrite`: то, что держит старые diagnostic cards, ложные owner-эвристики или дублирующий UI-смысл.

## Open TODO / TBD

### TODO

- зафиксировать окончательный каркас launcher-card hierarchy;
- довести единый bar contract до всех deep-pages;
- зафиксировать чистые формулировки для laptop/local launch states.

### TBD

- финальные breakpoint rules для dense и stacked bar;
- долгосрочный набор home-level quick actions без разрастания bar-панели.

## Cross-Module Trigger

Переходить в `cross_module_prompt.md`, если меняется хотя бы одно из условий:

- owner semantics;
- shared blocked-state wording;
- shell snapshot contract;
- fullscreen behavior, которое должны использовать и другие модули;
- shared input-helper behavior или default return-state semantics;
- общие status chips, которые читают несколько страниц.
