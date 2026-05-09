# 05. Shell Navigation And Screen Map

## Роль Файла

Этот файл должен описывать shell, navigation и карту экранов в порядке от самых общих поверхностей к более глубоким.

## Статус

- текущий статус: `active draft`

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- specific legacy donor paths больше не считаются обязательным reading path для этого active file.

## Settled Truths

- порядок экранов и reading order должны идти от общего к частному
- `Home` и shell стоят выше локальных модульных поверхностей

## 1. Роль Shell И Home

`Shell` в активном каноне — это общая оболочка и navigation language платформы.

`Home` — это пользовательская домашняя страница `Smart Platform`, а не технический dashboard и не экран сырых runtime-деталей.

Базовые правила:

- пользовательское имя домашней страницы фиксируется как `Smart Platform`;
- внутреннее имя `Platform Shell` не должно выходить на лицевую сторону UI;
- `Home` стоит выше локальных модульных поверхностей и всегда остается понятной точкой возврата;
- верхняя bar-панель является главным носителем global status и entry-context сигналов.

## 2. Глобальная Навигация

Канонический верхний navigation order для `v1`:

1. `Home`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`
6. `Settings`

Допустимый быстрый user-facing entry:

- `Gallery > Reports`

Не считаются отдельными верхнеуровневыми пользовательскими страницами:

- `Logs`
- `Diagnostics`
- `Content Storage`
- старые `service`- и compatibility-surfaces.

## 3. Роли Главных Пользовательских Разделов

- `Irrigation`: product entry в полив и связанные user scenarios.
- `Turret`: owner-aware entry в manual/automatic/operator surfaces.
- `Gallery`: shared explorer для контента, медиа и reports.
- `Laboratory`: инженерное рабочее пространство, а не скрытая service-ветка.
- `Settings`: постоянная системная страница, а не декоративный переходный экран.

`Gallery`, `Laboratory` и `Settings` являются полноценными пользовательскими разделами и должны проектироваться как самостоятельные глубокие пространства, а не как вторичные сервисные вставки.

## 4. Локальные Навигации Модулей

После входа в модуль каждая крупная surface получает собственную локальную навигацию.

Правила:

- нельзя переиспользовать одну и ту же локальную left-nav модель для всех deep-pages;
- `Gallery`, `Laboratory` и `Settings` должны иметь собственные локальные меню и порядок пунктов;
- `Turret` может иметь mode-entry внутри своего модуля, например `Manual Control` и `Automatic Control`, не превращая их в отдельные верхние shell-sections;
- route alias допустим как implementation compatibility layer, но user-facing label должен следовать активному канону.

## 5. Screen Map От Общего К Глубокому Срезу

Shell reading path должен выглядеть так:

1. `Home / Smart Platform`
2. вход в один из главных user-facing разделов
3. локальная навигация выбранного раздела
4. глубокий рабочий срез или профильный workflow внутри модуля

Типичные переходы:

- `Home -> Irrigation`
- `Home -> Turret -> Manual Control`
- `Home -> Turret -> Automatic Control`
- `Home -> Gallery -> Reports`
- `Home -> Laboratory -> локальная группа инструментов`
- `Home -> Settings -> нужный persistent section`

Глубокие diagnostics, storage inspection и legacy service-surfaces могут существовать как внутренние маршруты, но не должны конкурировать с этой картой экранов.

### Implementation-Level Shell Obligations

На уровне active canon shell обязан материализовать эту карту экранов так, чтобы она работала как продуктовая оболочка, а не как техническая панель.

Минимальные implementation-level обязательства:

- `Home` должен работать как product launcher, а не как raw runtime dashboard;
- shell должен показывать оба узла и их честную availability-картину без смены архитектуры при деградации;
- handoff hints, block reasons и короткие shell summaries должны появляться прямо в shell-layer, а не прятаться в service-only surfaces;
- `Settings` обязаны оставаться отдельной persistent page и получать truthful shell/platform state, а не дублировать laboratory controls;
- shell обязан давать короткую activity summary, но не подменять ей `Gallery > Reports`, `Laboratory` или deep diagnostics;
- shell всегда показывает продуктовый раздел даже при недоступности owner и выбирает только один из честных route modes: local, handoff или blocked/degraded.

### Home Launcher Composition

`Home` materializes one launcher surface per top-level product section:

- `Irrigation`
- `Turret`
- `Gallery`
- `Laboratory`
- `Settings`

Launcher rules for the current baseline:

- `Turret` launcher может показывать внутренние actions `Manual Control` и `Automatic Control`, не превращая их в отдельные top-level shell sections;
- `Irrigation` на `Home` остается одной launcher card, а не набором внутренних режимов;
- `Reports` открываются через `Gallery`, а не как отдельная home destination;
- launcher cards и их внутренние actions должны ужиматься до tablet/mobile widths без горизонтального скролла и без anchor-jumps внутри `Home`.

### Minimum Shell-Visible Data

Чтобы shell мог материализовать эту модель без домысливания, ему нужен минимальный shell-visible data set:

- `node status`;
- `module registry`;
- `owner_node_id`;
- `owner_available`;
- `canonical_url`;
- `federated_access`;
- `active mode`;
- `fault summary`;
- `gallery source availability`;
- `recent activity summary`;
- `emergency power interlock state`.

Эти поля должны быть достаточными для `Home`, shell-level handoff language и quick entry в `Gallery > Reports`, не заставляя shell собирать product truth из множества несвязанных service endpoints.

### Shared Bar Slot Contract

Чтобы bar действительно работал как product shell, а не как рыхлый набор badges, его layout contract должен оставаться предсказуемым.

Нормативный baseline слотов:

- слева: компактный `Home / Smart Platform` logomark, desktop interaction toggle, fullscreen toggle и current viewer/client indicator;
- в центре: постоянные node-presence labels для `Raspberry Pi` и `ESP32`, mode-chips только для реально доступных owner modules и moisture strip по `5` irrigation groups;
- справа: `Wi-Fi`, `Sync`, environmental/system indicators, language, time и date.

Дополнительные правила этого shell-visible слоя:

- safety interlocks, active failures и locked/degraded states должны быть видимы через shell-level summaries, а не жить только в deep diagnostics;
- если для slot нет truth-data, место не исчезает, а переходит в честное серое состояние `no data`;
- bar не должен вываливать raw transport detail вроде `node_id`, `base_url` или низкоуровневые booleans как будто это пользовательский язык оболочки;
- desktop baseline держит global bar в одной строке с симметричным внешним padding, а не раскладывает ее на постоянный detail-strip;
- длинные объяснения открываются через tooltip, status-sheet или другой on-demand layer, а не через вторую постоянную строку под bar;
- при нехватке ширины bar сначала уходит в более плотный compact mode с меньшими chips, icons и gaps, а не ломает slot order;
- compact global bar не оправдывает превращение `Settings` или `Laboratory` в shallow summary-pages;
- исчезновение одного сигнала не должно заставлять соседние группы прыгать и перестраиваться как новый layout;
- узкие layout-режимы могут stack/collapse группы, но shell не должен требовать горизонтальный scroll и должен сохранять понятную left-center-right ordering logic.

## 6. Fullscreen И Continuity Между Поверхностями

- интерфейс должен ощущаться как приложение, а не как поток полных page reload;
- обычная навигация должна сохранять continuity между поверхностями;
- `fullscreen` считается shell-level shared preference и особенно важен для `Laboratory` и operator surfaces;
- потеря fullscreen браузером при переходе не должна ломать navigation language или тихо переписывать пользовательский выбор;
- fullscreen continuity across navigation остается best-effort browser behavior, а не магической гарантией shell;
- если restore-path требует interaction, он не должен красть первый пользовательский клик у ссылки, кнопки или другого control;
- shell не должен одновременно показывать native browser tooltip и custom tooltip на одном и том же control;
- shared bar и связанные shell tokens нужно проверять не только на `Home`, но и на `Gallery`, `Laboratory`, `Settings` и `Turret`;
- `Home` через bar остается обязательной экстренной точкой возврата.

## 7. Handoff И Переход Между Context-ами

- peer-owned route не должен притворяться локальным исполнением;
- owner-local route открывается локально;
- peer-owned route переводит пользователя в handoff flow или в честное blocked explanation;
- прямой ввод логичного адреса не должен падать в сырой `404`, если shell знает модуль и его canonical route;
- historical alias routes допустимы как compatibility layer, но новые решения строятся вокруг канонических section names.

## Open Questions

- какой объем визуальных screen-map примеров держать прямо здесь, а какой переносить в модульные файлы

## TODO

- собрать общую карту без service-page legacy шума

## TBD

- финальный набор launcher и deep-link patterns
