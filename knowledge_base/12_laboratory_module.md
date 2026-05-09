# 12. Laboratory Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Laboratory` как единого инженерного workspace.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный active canon для `Laboratory`; donor docs ниже остаются deep-spec и readiness residue

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `briefs/laboratory.md` и `chat_prompts/laboratory_prompt.md` остаются active companion sources для module framing and workflow sync.

## Settled Truths

- `Laboratory` — единое workspace, а не набор старых service pages
- пользовательский слой называется `Записи сессии`
- `Laboratory` не имеет прямого export-path в `Gallery > Reports`

## Canon

### 1. Роль И Пользовательский Итог

`Laboratory` - это user-facing инженерный workspace платформы для bring-up, qualification, diagnostics, profile tuning и owner-aware проверки компонентов и модульных срезов через само приложение.

Для пользователя `Laboratory` должен давать такой итог:

- единый вход в инженерную работу без прыжков между legacy service pages;
- понятную категорийную IA для телефона, `8-inch` дисплея и desktop browser;
- честную видимость owner context, power context и blocked behavior;
- рабочие карточки компонентов с expected-result guidance, реакцией системы и записью локального результата;
- явный review/apply path в `Settings` без молчаливого повышения laboratory values до system truth.

`Laboratory` не является:

- пользовательским `Reports` viewer;
- заменой `Settings`;
- отдельной верхнеуровневой `Diagnostics` page;
- launcher-страницей для старых `/service/*` routes.

### 2. IA И Группы Компонентов

Канонический route для workspace:

- `/service`

Нормативная IA:

- одна страница в app-like стиле;
- category-first rail на первом уровне;
- second-level slice rail внутри выбранной категории;
- рабочая область справа или ниже, в зависимости от density/layout mode;
- без полного page reload при переключении категорий и slices.

Current active category rail должен следовать реальному shared hub contract:

1. `Обзор`
2. `Свет`
3. `Приводы`
4. `Вода`
5. `Аудио`
6. `Датчики`
7. `Камера`
8. `Дисплеи`
9. `Экспериментальное`

Representative second-level slices текущего baseline:

- `Строб`
- `ESP32 / Стендовый строб`
- `Сервоприводы`
- `Шаговый двигатель / приводы`
- `Распыление / вода`
- `Инженерный срез полива`
- `Влажность почвы + клапаны + перистальтика`
- `Пьезо / ультразвук`
- `Голос / динамик`
- `Лидар`
- `Датчик движения`
- `Температура и влажность воздуха`
- `Камера`
- `Контур зрения`
- `Сенсорный дисплей Raspberry Pi`
- `Профиль дальномера HC-SR04`
- `Прием нового модуля`

Категории и slices не должны строиться по owner/vendor map. Owner truth отражается статусом, blocked behavior и handoff semantics, а не названием rail.

### Bench Profiles Inside Laboratory

`Laboratory` должен уметь держать owner-side engineering profiles внутри общего workspace, не превращая каждый такой профиль в отдельную top-level product page.

Первый зафиксированный baseline этого класса:

- семейство `strobe` уже разведено на product/turret `strobe` и laboratory/bench `strobe_bench`;
- `strobe_bench` считается owner-side engineering profile на стороне текущего `ESP32`-based bench/runtime path;
- engineering-gated command family для такого slice может включать `arm`, `disarm`, `stop`, `abort`, `pulse`, `burst`, `loop`, `continuous on` и `preset`;
- safe preset run и live status допускаются как часть одной рабочей card, а не как набор разрозненных POST methods.

При этом active canon не фиксирует как вечную истину:

- legacy compatibility route вроде `/service/strobe`;
- конкретный tab set `Overview`, `Pulse`, `Burst`, `Loop`, `Continuous`, `Presets`;
- текущую форму первого software-stage как окончательную IA всей laboratory-секции `Свет`.

### 3. Обзор, Header И Screen Flow

`Обзор` - это summary-only slice, а не центр всей работы.

На `Обзоре` должны быть:

- сводка топологии стенда и board visibility;
- readiness summary и preflight snapshot;
- bring-up order с текущим статусом;
- видимость доступных и blocked групп;
- сводка локального session context и draft state;
- быстрый вход в `Constructor` и review layer без подмены реальных карточек.

На `Обзоре` не должны жить:

- полные controls всех cards;
- большой backend-log dump;
- императивный `next_action` как главный рабочий центр страницы.

`Laboratory` header должен оставаться видимым при смене активного тела и держать:

- название страницы;
- active owner/access status;
- выбранный power context;
- profile source state: default from `Settings`, local draft, saved profile;
- индикатор unsaved changes.

Screen-flow baseline:

1. `Home -> Laboratory`
2. выбор категории
3. выбор slice
4. работа в card
5. локальная запись результата в `Записи сессии`
6. при необходимости explicit `Сохранить выбор` -> `Settings`

Browser mode и fullscreen mode - это два layout modes одной и той же страницы. Они должны менять плотность и компоновку, но не терять shell status, owner context, power context или local session visibility.

### 4. Working Card Skeleton

Каждая рабочая card должна иметь единый базовый каркас, даже если controls у component families разные.

Обязательные зоны:

1. card title;
2. owner/status/power/context chips;
3. component selection и specification block;
4. wiring/power instruction block;
5. structured status cards;
6. scenario-specific controls и forms;
7. current default profile from `Settings` и local draft block;
8. visible system reaction / result area;
9. `Сохранить выбор` action.

Optional zones:

- state table, если она реально помогает тесту;
- console or diagnostic trace foldout;
- graphs;
- photos and wiring diagrams;
- calibration hints;
- preview of future runtime profile.

Practical rule:

- card получает tools под тип компонента, а не один универсальный control set;
- blocked reason и next step должны быть видимы в card до tooltip/detail layer;
- expected-result hints и system reaction area нужны прямо в рабочей области, а не только в hidden logs.

### Repeatable Engineering Scenarios

`Laboratory` может держать repeatable browser-driven scenario packs еще до появления полного hardware binding слоя.

Нормативный смысл:

- scenario run остается частью конкретной working card или component slice, а не отдельной top-level page;
- dry-run scenarios допустимы как подготовка и verification layer до live hardware execution;
- compatibility names конкретных scenario packs не считаются вечной vocabulary-истиной;
- результат scenario run должен писаться в `Записи сессии` как `pass`, `warn`, `fail`, `blocked`, `skipped` или `note`, а не растворяться в безымянном raw log dump.

### 5. Session Notes, Drafts And Save To Settings

У `Laboratory` есть lightweight session layer с пользовательским именем:

- `Записи сессии`

Этот слой должен хранить как минимум:

- operator;
- objective;
- selected power context;
- hardware profile;
- external module label, если он участвует;
- active category и active slice;
- local notes и результаты pass;
- local draft до promotion в `Settings`.

Минимальные session entry types `v1`:

- `pass`
- `warn`
- `fail`
- `blocked`
- `skipped`
- `note`

Нормативные правила:

- `Записи сессии` остаются локальным рабочим следом `Laboratory`;
- они могут восстанавливаться после reload;
- по умолчанию они не синхронизируются между узлами;
- они не уходят напрямую в `Gallery > Reports`.

Current backend/session profile:

- canonical session backend сейчас держится на `Raspberry Pi` через `/api/v1/laboratory/session*` и `/api/v1/laboratory/event`;
- mirrored shells, например `ESP32`, могут держать local-draft fallback, но UX-смысл остается тем же: легкий local working context, а не heavy session console.

`Сохранить выбор` -> `Settings` является explicit promotion path:

1. берутся только подтвержденные поля текущей card;
2. показывается diff против persistent profile;
3. выбирается persistent target;
4. результат записывается в `Settings`;
5. new or updated profile становится default next entry point для этой card.

Никакой отдельный slider change inside `Laboratory` не должен автоматически становиться system truth.

### 6. Power Context, Owner Context And Blocked Behavior

Минимальный visible power context `v1`:

- `Bench PSU`
- `LiFePO4 battery`

Если slice зависит от voltage-sensitive или bench-sensitive flow, battery context должен:

- либо переводить часть controls в advisory-only state;
- либо честно блокировать unsafe calibration path;
- всегда оставлять operator-visible reason и путь возврата к bench mode.

Owner-context rules:

- peer-owned slices остаются видимыми;
- local shell не притворяется owner-side executor;
- blocked slice обязан показывать причину и next step до глубокого tooltip;
- `Displays` slice остается visibly blocked в `ESP32`-only shell, пока `Raspberry Pi` не доступен.

Shared contract rule:

- browser mode и fullscreen mode должны сохранять owner/status visibility;
- Home-to-Laboratory navigation должна сохранять board context, а не терять его внутри workspace.

### 7. Reference Media, Reports Boundary And Shared UI Rules

`Laboratory` не ведет изолированный media world. Он подтягивает из `Gallery`:

- reference photos;
- wiring diagrams;
- other useful visual reference artifacts.

Boundary with `Reports`:

- console lines, calibration notes, state-table comparisons, local operator notes и вся последовательность laboratory passes не уходят по умолчанию в `Gallery > Reports`;
- `Reports` живут для автономно и системно зафиксированных product events;
- useful media artifacts могут потом быть attached through `Gallery > Media`, но engineering result itself остается anchored to `Laboratory` session record.

Shared UI rules, important specifically for `Laboratory`:

- global bar остается видимым и в fullscreen;
- fullscreen уплотняет рабочую область, а не скрывает shell truth;
- blocked and locked slices stay visible and explained;
- unsupported or planned slices stay visible as honest placeholders.

### 8. Controller Profiles И Работа С Компонентами

`Laboratory` работает с component slices в трех базовых профилях:

- owner-side slices;
- peer-owned slices с owner-aware handoff or blocked behavior;
- laboratory-local experimental profiles.

Current shared hub contract, который должен считаться active baseline:

- source of the shared workspace lives in `raspberry_pi/web/service.html` and is mirrored to `firmware_esp32/data/service/index.html`;
- при изменении IA этого workspace mirror behavior должен оставаться выровненным между двумя shell implementations;
- fallback hub text на `ESP32` не должен откатываться к старому flat launcher, если LittleFS page missing.

Experimental profile rule:

- `HC-SR04`-class range profiles, stepper drives, motion wake experiments, unknown/custom module intake и часть audio profiles остаются laboratory-local до explicit review/apply promotion;
- они не должны притворяться product-ready module controls.

`Displays` rule:

- `Displays` является first-level Laboratory category;
- owner-side `Raspberry Pi Touch Display` qualification остается отдельным slice и не смешивается с `Camera` UX.

### 9. Acceptance Hooks

Минимальные acceptance hooks текущего этапа:

1. `Laboratory` открывается как unified `/service` workspace и на `ESP32`, и на `Raspberry Pi`;
2. category rail и second-level slice rail переключаются in-page без full reload;
3. `Home -> Laboratory` сохраняет board visibility и owner context;
4. readiness summary и bring-up sequence видимы на `Обзоре`, но не подменяют рабочие cards;
5. peer-owned slices остаются visibly blocked и explained вместо fake ownership;
6. browser/fullscreen modes оба пригодны к работе и сохраняют одинаковую context truth;
7. operator может записать `pass / warn / fail / blocked / skipped / note` из активного slice без перехода в `Reports`;
8. explicit `Сохранить выбор` дает review/apply path в `Settings`.

Практические readiness passes, которые остаются важными:

- `ESP32` only phone pass;
- `Raspberry Pi` only phone pass;
- dual-board phone pass;
- dedicated `Raspberry Pi Touch Display` pass with pattern and touch-grid checks.

### 10. Нормативные Примеры И Форматы

Нормативные route examples:

- workspace: `/service`
- current turret compatibility slice: `/service?tool=turret_service`
- current display compatibility slice: `/service?tool=rpi_touch_display`

Пример lightweight session context payload:

```json
{
  "operator": "bench_operator",
  "objective": "display_smoke",
  "power_context": "Bench PSU",
  "hardware_profile": "rpi_touch_display_v1",
  "view_mode": "fullscreen",
  "active_category": "displays",
  "active_slice": "rpi_touch_display"
}
```

Пример session note entry:

```json
{
  "kind": "warn",
  "slice": "rpi_touch_display",
  "summary": "grid pattern shows slight corner clipping",
  "next_change": "review fullscreen density and edge padding"
}
```

Пример minimal readiness sequence:

1. shell and readiness smoke
2. peer link and owner handoff
3. `ESP32 / Strobe Bench`
4. `ESP32 / Irrigation Service`
5. `Raspberry Pi / Turret Service`
6. `Laboratory / Experimental Profiles`
7. `Laboratory` session review before the next bundle

## Open Questions

- какая глубина сценарных ladder-проходов нужна прямо в файле, а какая должна жить в acceptance и field layers
- где именно провести будущую границу между reusable generic card skeleton и module-specific card templates без перегруза `Laboratory`

## TODO

- после стабилизации active draft переаудировать laboratory donor residue в migration ledger и оставить только deep implementation/readiness detail without active authority role
- после следующего pass проверить, можно ли дальше схлопнуть readiness residue без потери practical testing detail

## TBD

- итоговая форма reusable component-card templates
- future equivalent session contract on direct `ESP32` shell beyond local-draft fallback
