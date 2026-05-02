# Smart Platform — Settings Architecture Refactor Chat Bootstrap Prompt

Используй этот prompt как стартовый рабочий контракт для отдельной Codex-сессии в VS Code по странице `Settings` проекта `Smart_Platform`.

Рабочий корень локального проекта:

`C:\Users\vilen\OneDrive\Dokumentumok\PlatformIO\Projects\Smart_Platform`

Не начинай с GitHub. GitHub используется как backup/remote, а активная работа должна идти в локальной папке проекта через VS Code.

---

## Контекст

Этот prompt должен заменить/дополнить отдельный bootstrap prompt для направления `Settings` в папке `chat_prompts`.

При подготовке проверены существующие prompt-файлы:

- `chat_prompts/README.md` задаёт общие guardrails для новых модульных чатов;
- `chat_prompts/gallery_settings_sync_chat_bootstrap_prompt.md` сейчас является ближайшим prompt-файлом к теме Settings, но его основной фокус — cross-node sync между `Gallery` и `Settings`, а не полная переархитектура Settings page.

Уникальную полезную информацию из этих prompt-файлов нужно сохранить, но при конфликтах приоритет имеют требования из этого нового prompt и решения, принятые в текущем обсуждении.

Актуальные решения после UI cleanup:

- видимый header Settings короткий: только `Settings` / `Настройки`;
- верхний dashboard как отдельный слой удалён из Settings, потому что краткий статус уже живёт в bar-панели;
- hover tooltip появляется примерно через `500 ms`, располагается рядом с курсором/местом наведения, закрывается/отменяется сразу при движении курсора больше `3 px` и не держится дольше `6 s`;
- интерактивные настройки применяются optimistic-first: UI меняется сразу, сохранение уходит в debounce/background и не должно блокировать клики, ввод или переключение секций;
- helper text не дублируется под control, если он уже есть в tooltip/status-sheet;
- `EN` и `RU` являются рабочими локалями, а `HE`, `DE`, `FR`, `ES`, `ZH`, `AR` могут быть selectable TODO-заглушками до отдельного translation-модуля;
- `Modules` — функциональные hardware-level системы (`Турель`, `Ирригация`, `Питание`);
- `Components` — конкретные железные элементы с инженерными полями: питание, распиновка, допуски, режимы, статус проверки;
- `System Services` содержит software-сущности вроде `Shell`, `Sync Core`, `Storage Service`; их нельзя смешивать с hardware modules/components;
- `Constructor` — отдельный modal wizard для черновика модуля или компонента; сначала UI-модель, затем сохранение в JSON/config через приложение;
- текущий рабочий этап конструктора уже пишет в `raspberry_pi/content/.system/platform_registry.v1.json` через `/api/v1/platform/registry/constructor`; не возвращать его в декоративную local-only заглушку;
- пример `Cat Feeder` строится вокруг `Motion Sensor`, камеры идентификации и `Servo dispenser`; не использовать `Light Sensor` как компонент кормушки, потому что кот не является источником изменения освещённости;
- отдельная секция `Platform Nodes` удалена из Settings; краткий статус `RPi/ESP` остаётся в bar-панели, а смысловая связь с платами показывается через `Modules`;
- `Runtime` сокращает `host kind / viewer kind / runtime profile` до одного launch context, если отдельные строки не добавляют смысла;
- `Sync` хранит утверждённый список `selected_domains`: service link, module state, shared preferences, reports/logs, plant library, media content (`photo/video/audio/gallery reports`), component registry, software versions (`RPi/ESP/Web UI`); `Auto` выбирает все пункты, ручное изменение любого пункта переводит режим в `Manual review`;
- storage cards сортируются от глобального к прикладному: project root, plant library, video, audio, reports, gallery, assets, animations, content root;
- `Plant Library` связана с irrigation и JSON-библиотеками `content/libraries/plant_profiles.v1.json`, `plant_state_rules.v1.json`, `care_scenarios.v1.json`;
- однотипные инженерные поля компонентов должны показывать ранее введённые значения как suggestions;
- storage actions включают `Copy path`, `Open folder`, `Open in app`, cleanup preview и подтвержденное удаление, а backend обязан проверять, что путь не выходит за разрешенный root;
- keyboard action keys работают только на `Turret Manual`; вне control-page клавиши остаются обычным вводом текста;
- при выключенном `Keyboard controls` поля карты клавиш/мощности остаются видимыми, но disabled/серыми и объясняют в tooltip, что сначала нужно включить режим;
- базовая мощность action key по умолчанию `50%`, при удержании `Shift` — `100%`, оба значения переназначаются в Settings.

Сохранить из старых prompt-файлов следующие правила:

- активный source of truth — только локальный репозиторий `Smart_Platform`;
- не считать laptop/desktop запуск отдельным hardware owner;
- сначала отделять `host launch`, `browser entry`, `module owner` и `current browser client`;
- при отсутствии truthful data показывать нейтральное/честное состояние, а не выдумывать positive/online status;
- `offline`/`not connected` отображается серым/neutral во всех shell-поверхностях; красный остаётся для настоящих `fault/error/blocked`;
- нельзя создавать ложную pseudo-master / master-node модель;
- нельзя терять origin/source-owner metadata;
- нельзя молча терять logs/reports/history;
- нельзя позволять remote node снимать local fault без правил;
- нельзя делать silent overwrite пользовательских настроек;
- `Gallery > Reports` остаётся каноническим viewer истории действий и report provenance;
- storage diagnostics не должен подменять собой `Gallery`;
- после UI/JS edits проверять не только source file, но и live-served asset на реальном порту;
- длинные JS-файлы править маленькими hunks в порядке следования кода;
- не переносить большие куски между Raspberry Pi и ESP32 implementations как будто это один и тот же implementation generation;
- не строить fullscreen/tooltips так, чтобы первый клик пользователя тратился на побочный эффект и ломал основное действие;
- если браузер сбросил fullscreen после навигации, bar-control может показывать pending state, но восстановление делается явным нажатием на fullscreen control, а не кликом по пустой области страницы;
- `Settings` хранит желаемый fullscreen preference, а bar-панель показывает фактический fullscreen/pending restore; browser-exit во время навигации не должен сам менять durable preference на `false`;
- не оставлять browser-native tooltip параллельно custom tooltip;
- после regression сначала восстановить рабочее поведение на live page, а уже потом расширять scope.

---

## Главная цель

Пересобрать страницу `Settings` не как набор случайных карточек, а как центральную страницу состояния и конфигурации Smart Platform.

Цель не в косметическом переименовании строк. Нужно исправить модель отображения:

- где запущена система;
- с какого устройства пользователь смотрит интерфейс;
- какие физические узлы доступны;
- какие модули назначены узлам;
- какие компоненты реально обнаружены;
- что синхронизируется;
- где лежат данные;
- какие настройки являются пользовательскими;
- какие действия безопасны, а какие требуют режима редактирования.

Settings должен быть одновременно:

- страницей состояния платформы;
- страницей пользовательских настроек;
- страницей конфигурации модулей/компонентов;
- точкой диагностики причин, но без превращения страницы в техническую свалку.

---

## Текущая проблема

Сейчас Settings смешивает разные сущности:

1. физические узлы: Raspberry Pi, ESP32;
2. текущий host, где запущен backend/server;
3. текущее устройство просмотра;
4. модульное владение;
5. sync status;
6. storage paths;
7. пользовательские настройки;
8. developer/internal status.

Из-за этого возникают ложные состояния.

Например: система запущена с ноутбука, Raspberry Pi и ESP32 не подключены, но Settings может показывать `Raspberry Pi online` или помещать `Desktop Smoke` внутрь карточки Raspberry Pi. Это неверно.

Запуск с ноутбука — это не Raspberry Pi online.

Правильная формулировка для такого состояния:

`Локальный запуск, платы offline`

---

## Обязательная модель терминов

Используй следующую модель.

### Host

Устройство, на котором запущен backend/server Smart Platform.

Примеры:

- Windows laptop / desktop;
- Raspberry Pi;
- ESP32 fallback shell;
- unknown host.

Пользовательское объяснение:

`Host — устройство, на котором запущен сервер Smart Platform.`

### Viewer device

Устройство, с которого пользователь сейчас смотрит web UI.

Примеры:

- этот же ноутбук;
- смартфон;
- планшет;
- экран Raspberry Pi;
- другой browser client в LAN.

Viewer device — технический сигнал для launch context и bar-панели. Не делать для него
отдельную карточку настроек, если она только дублирует текущую страницу или heartbeat.

### Platform Node

Физический узел платформы.

Примеры:

- Raspberry Pi;
- ESP32;
- future controller board;
- future power controller.

### Module

Функциональный блок системы.

Примеры:

- Irrigation;
- Turret;
- Gallery;
- Laboratory;
- Power / Solar / Wind;
- Cat Feeder;
- custom module.

### Component

Физическая или логическая часть модуля.

Примеры:

- камера;
- насос;
- клапан;
- серво;
- стробоскоп;
- датчик влажности;
- контроллер заряда;
- солнечная панель;
- ветряк;
- конвертер.

### Module Ownership

Ожидаемое распределение модулей по узлам.

Пример:

- Irrigation → ESP32;
- Turret → Raspberry Pi;
- Gallery → platform service;
- Laboratory → platform service;
- Power / Solar / Wind → выбранный power/controller node;
- Cat Feeder → выбранный node.

Важно: ownership не означает, что узел сейчас online.

---

## Запрещённые или нежелательные формулировки

Убрать из user-facing UI:

- `neighbor node`;
- `соседний узел`;
- формулировки, где ESP32 выглядит вторичным только потому, что Raspberry Pi мощнее;
- `Raspberry Pi online`, если backend просто запущен с ноутбука;
- `Desktop Smoke` как основной пользовательский режим;
- “локально” без объяснения, что именно локально;
- browser-native `title` tooltip как основной способ подсказок.

`Desktop Smoke` может остаться только как internal technical profile id в Advanced/Debug, но не как основной текст для пользователя.

---

## Offline и Not Detected

Разделяй статусы разных уровней.

### Для узлов

Используй:

- `online`;
- `offline`;
- `degraded`;
- `fault`;
- `unknown`.

### Для компонентов

Используй:

- `ready`;
- `not detected`;
- `missing`;
- `disabled`;
- `fault`;
- `simulated`;
- `verification pending`.

Правило:

- Raspberry Pi / ESP32 offline.
- Камера / клапан / стробоскоп / серво not detected.
- Если компонент ожидается по конфигу, но отсутствует — missing.
- Если компонент найден, но работает неправильно — fault.
- Если модуль добавлен в конфиг, это не значит, что железо найдено.

---

## Smart Bar как UX-эталон

Smart Bar / Compact Bar уже проработан лучше, чем Settings.

Settings должен наследовать или переиспользовать:

- status colors;
- status chips;
- tooltip style;
- tooltip delay;
- tooltip border/background/radius;
- tooltip structure;
- логику online/offline/degraded;
- fullscreen/settings/bar behavior.

Не ломай Smart Bar ради Settings.

Сначала изучи:

`raspberry_pi/web/static/smart_bar.js`

Особенно:

- tooltip DOM;
- `.sp-tooltip`;
- status token styles;
- fullscreen behavior;
- settings cache;
- viewer heartbeat.

Если нужно, вынеси общий tooltip/status helper или создай совместимый helper для Settings. Не оставляй параллельно слабые browser-native подсказки.

---

## Общий источник состояния

Runtime/node/viewer/platform status должен приходить из общего snapshot/status источника, желательно:

`/api/v1/shell/snapshot`

User preferences должны идти из:

`/api/v1/settings`

Не смешивай эти два слоя.

`/api/v1/settings` — это пользовательские настройки и политики.

`/api/v1/shell/snapshot` — это состояние системы, узлов, viewer, runtime, modules, summaries.

---

## Shared Preferences Contract

Fullscreen, language, theme, density, Smart Bar behavior и другие shared UI preferences не должны жить независимо в разных местах.

Требования:

1. Один источник состояния для shared UI preferences.
2. Settings меняет состояние через этот источник.
3. Smart Bar читает тот же источник.
4. Другие страницы shell читают тот же источник.
5. После изменения настройки UI должен обновляться согласованно во всех местах.
6. Не должно быть ситуации, когда fullscreen включён в одном месте, а другой control показывает другое.
7. Browser localStorage может быть cache/fallback, но не должен становиться конкурирующим source of truth.
8. Если используется cached settings, UI должен честно показывать stale/fallback state, если backend недоступен.

Особенно проверить:

- fullscreen;
- desktop controls;
- language;
- theme;
- density;
- compact bar behavior;
- tooltip behavior, если будет настраиваться.

---

## Каноническая структура Settings

Ниже идёт уже не historical appendix, а актуальный канон для будущих сессий.
Если старые prompt-файлы, заметки или doc-snippets противоречат этому блоку,
они считаются устаревшими.

### Разделы страницы

1. `Interface`
   - язык;
   - theme;
   - density;
   - fullscreen;
   - keyboard controls;
   - advanced diagnostics toggle.
2. `Launch and Runtime`
   - один launch context вместо россыпи дублирующих host/viewer/profile полей;
   - краткое truthful explanation, где запущен backend и кто сейчас смотрит UI.
3. `Synchronization`
   - `Auto` / `Manual review`;
   - список `selected_domains`;
   - last sync time;
   - per-domain status рядом с выбранными пунктами;
   - continuity preference и poll interval.
4. `Storage`
   - project root;
   - plant library;
   - video;
   - audio;
   - reports;
   - gallery/content roots;
   - действия `Copy path`, `Open folder`, `Open in app`, cleanup preview,
     подтвержденное удаление в разрешенных пределах.
5. `Modules`
   - продуктовые hardware-level системы: `Turret`, `Irrigation`, `Power`;
   - ownership показывается через логические роли узлов, а не через brand платы;
   - truthful hardware profile при необходимости показывается отдельно.
6. `Components`
   - каждый компонент живёт в собственной карточке;
   - инженерные поля, suggestions, pinout/power/tolerance/modes;
   - статусы честные, нейтральные при offline.
7. `System Services`
   - `Platform Shell`, `Sync Core`, `Storage Service` и другие software-сущности;
   - не смешивать с modules/components.
8. `Policies`
   - turret policies;
   - irrigation policies;
   - keyboard action semantics;
   - безопасные правила, которые пользователь действительно может менять.
9. `Constructor`
   - отдельный modal wizard;
   - создаёт scaffold будущего module/component registry entry;
   - сначала проверяем UI-flow, затем сохраняем в JSON/config через приложение.
10. `Diagnostics`
   - secondary section;
   - по умолчанию под спойлером;
   - не раскрывается сам по себе.

### Канон терминов

- `Platform Shell` — каноническое имя shell-блока;
- `Laboratory` — каноническое имя инженерного сервисного блока;
- `compute_node`, `io_node`, `shared` — канонические логические роли узлов;
- `Raspberry Pi`, `ESP32` и будущие платы — truthful board profiles, а не
  универсальные owner-термины для всей архитектуры;
- legacy alias `system_shell`, `service_test`, `rpi`, `esp32` допускаются только
  как compatibility-layer в старых payload, логах и bridge-stage документах.

### Что удалено из канона

- отдельный `Overview` dashboard в Settings;
- отдельная секция `Platform Nodes`;
- дублирующие quick actions в нескольких местах;
- helper text, который повторяет tooltip;
- user-facing текст, показывающий историю рефакторинга вместо смысла функции.

### Правила truthful-state

- runtime truth приходит из `/api/v1/shell/snapshot`;
- редактируемые предпочтения и policies приходят из `/api/v1/settings`;
- offline / not connected отображается нейтрально серым;
- красный используется только для реальных `fault / error / blocked`;
- desktop/laptop host не должен маскироваться под `Raspberry Pi online`;
- host launch, viewer device, module ownership и hardware presence всегда
  разделяются как разные сущности.

### Правила UX

- page header короткий: только `Settings` / `Настройки`;
- tooltip появляется примерно через `500 ms`;
- tooltip закрывается/отменяется сразу при смещении курсора больше `3 px`;
- без движения tooltip живёт не дольше `6 s`;
- tooltip располагается рядом с курсором или местом наведения;
- custom tooltip не должен конфликтовать с browser-native tooltip;
- optimistic-first update: UI реагирует сразу, сохранение уходит в debounce/background;
- выбранный язык применяется ко всему user-facing тексту страницы;
- theme и density распространяются на все shell-страницы, кроме нейтральной bar-панели.

### Приоритет реализации

1. Сначала поддерживать skeleton, который можно честно тестировать с ноутбука.
2. Не связывать progress с наличием реального железа, если задача касается:
   - docs;
   - settings persistence;
   - constructor registry scaffold;
   - sync/storage semantics;
   - UI vocabulary и navigation alignment.
3. Hardware-required behaviour расширять только после того, как laptop-testable
   слой стал truthful и непротиворечивым.

### Требования к Constructor

- это не должен быть бессмысленный placeholder;
- нужен полноценный scaffold flow хотя бы с тремя реальными примерами:
  - `Cat Feeder` как новый модуль;
  - `Servo Dispenser` как компонент для нового модуля;
  - `Light Sensor` как компонент для существующего модуля;
- flow должен удерживать разделение между:
  - controller node role;
  - assigned module;
  - component kind;
  - engineering fields;
- пользователь не должен терять введённые значения и suggestions для типовых полей.

### Что проверять после каждой итерации

- `Settings` страница жива на реальном порту и не падает до первого render;
- theme/density/language/fullscreen работают согласованно между Settings и shell;
- tooltip contract одинаков в Settings и bar-панели;
- sync/storage actions не выходят за разрешённые roots;
- docs, prompt-файлы и UI vocabulary не спорят между собой.

### Основные файлы для старта новой сессии

1. `chat_prompts/README.md`
2. `docs/05_ui_shell_and_navigation.md`
3. `docs/27_platform_shell_v1_spec.md`
4. `docs/33_shell_snapshot_schema.md`
5. `docs/39_design_decisions_and_screen_map.md`
6. `docs/40_platform_shell_navigation_alignment.md`
7. `shared_contracts/shell_snapshot_contract.md`
8. `shared_contracts/api_contracts.md`
9. `briefs/laboratory.md`

### Инструкция для следующей Codex-сессии

1. Сначала сравнить текущий `Settings` UI с этим каноном.
2. Затем найти все residual contradictions в docs/prompts/contracts.
3. Исправлять сначала truthful-state и shared semantics, а уже потом косметику.
4. Если встречаются старые указания про `Overview`, `Platform Nodes`,
   старые shell/laboratory aliases, light/dark-only theme model или
   brand-based ownership semantics, считать их устаревшими и мигрировать на
   канон выше.
## Тон интерфейса

Интерфейс должен быть:

- пользовательским, но точным;
- визуально приятным, но не игрушечным;
- инженерно честным;
- компактным сверху и подробным ниже;
- без случайного смешения русского и английского;
- без дублирующих строк;
- с понятной причиной каждого статуса и следующего действия.
