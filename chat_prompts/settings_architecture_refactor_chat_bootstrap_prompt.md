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
- Overview как отдельный верхний dashboard удалён из Settings, потому что краткий статус уже живёт в bar-панели;
- hover tooltip появляется примерно через `500 ms` и закрывается/отменяется при движении курсора больше `3 px`;
- helper text не дублируется под control, если он уже есть в tooltip/status-sheet;
- `EN` и `RU` являются рабочими локалями, а `HE`, `DE`, `FR`, `ES`, `ZH`, `AR` могут быть selectable TODO-заглушками до отдельного translation-модуля;
- `Modules` — функциональные hardware-level системы (`Турель`, `Ирригация`, `Питание`);
- `Components` — конкретные железные элементы с инженерными полями: питание, распиновка, допуски, режимы, статус проверки;
- `System Services` содержит software-сущности вроде `Shell`, `Sync Core`, `Storage Service`; их нельзя смешивать с hardware modules/components;
- `Constructor` — отдельный modal wizard для черновика модуля или компонента; сначала UI-модель, затем сохранение в JSON/config через приложение;
- storage cards сортируются от глобального к прикладному: project root, plant library, video, audio, reports, gallery, assets, animations, content root;
- storage actions включают `Copy path`, `Open folder`, `Open in app`, cleanup preview и подтвержденное удаление, а backend обязан проверять, что путь не выходит за разрешенный root;
- keyboard action keys работают только на `Turret Manual`; вне control-page клавиши остаются обычным вводом текста;
- базовая мощность action key по умолчанию `50%`, при удержании `Shift` — `100%`, оба значения переназначаются в Settings.

Сохранить из старых prompt-файлов следующие правила:

- активный source of truth — только локальный репозиторий `Smart_Platform`;
- не считать laptop/desktop запуск отдельным hardware owner;
- сначала отделять `host launch`, `browser entry`, `module owner` и `current browser client`;
- при отсутствии truthful data показывать нейтральное/честное состояние, а не выдумывать positive/online status;
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
- точкой диагностики причин, но без превращения Overview в техническую свалку.

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

### Viewer / Current device

Устройство, с которого пользователь сейчас смотрит web UI.

Примеры:

- этот же ноутбук;
- смартфон;
- планшет;
- экран Raspberry Pi;
- другой browser client в LAN.

Пользовательское объяснение:

`Текущее устройство — устройство, с которого вы сейчас открыли интерфейс.`

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

## Историческая структура Settings Ниже

Следующий раздел оставлен как context/history старого refactor-плана. При
конфликте использовать актуальные решения выше: короткий header, без отдельного
Overview dashboard, секции `Appearance`, `Runtime`, `Platform Nodes`, `Sync`,
`Storage`, `Modules`, `Components`, `System Services`, `Policies`, `Constructor`,
`Diagnostics`.

## Предлагаемая структура Settings

## 1. Overview

Верхний Overview должен состоять примерно из 4–5 компактных карточек.

Первая карточка — `System Status`.

Для запуска с ноутбука без подключённых плат:

`Локальный запуск, платы offline`

Overview должен быть dashboard: компактный, практичный, без технической энциклопедии.

### Карточка 1: System Status

Показывает общую правду о системе.

Примеры:

- `Локальный запуск, платы offline`;
- `Система работает на Raspberry Pi, ESP32 offline`;
- `Система работает на Raspberry Pi, ESP32 online`;
- `Система degraded: backend отвечает, часть узлов недоступна`.

Критерии:

- `System online` = backend отвечает + snapshot API отвечает.
- `Platform ready` = готовы обязательные узлы/модули для выбранного сценария.

### Карточка 2: Current Runtime

Показывает, где сейчас работает backend/server.

Поля:

- Host;
- Host type;
- OS/device label, если известно;
- server status;
- URL / port;
- runtime/launcher folder;
- Copy path;
- Open folder, если поддерживается trusted desktop host.

Если host и viewer совпадают:

`Вы управляете системой с того же устройства, где она запущена.`

### Карточка 3: Current Viewer

Показывает устройство, с которого открыт интерфейс.

Поля:

- Viewer / текущее устройство;
- тип: desktop / phone / tablet / Raspberry display / unknown;
- текущая страница;
- viewer heartbeat status.

Если host и viewer разные:

`Host: ноутбук. Viewer: телефон.`

### Карточка 4: Platform Nodes

Показывает краткие статусы узлов:

- Raspberry Pi — status, role, last seen;
- ESP32 — status, role, last seen;
- future nodes — если есть.

Статусы должны совпадать с bar-панелью.

Если узел offline, не повторяй это в трёх строках. Используй corner badge + tooltip.

### Карточка 5: Sync

Синхронизация — отдельный platform process, не часть карточки ESP32 или Raspberry Pi.

Показывать:

- режим;
- последнее время синхронизации;
- human-readable время;
- remote availability;
- sync domains;
- что работает только локально;
- что отключено.

Формулировки:

- `Синхронизация ещё не выполнялась` — история.
- `Local only` / `только локально` — режим.
- `Remote unavailable` — причина.
- `Базовая связь узлов недоступна: remote node offline`.

### Quick actions в Overview

В Overview можно показывать быстрые действия:

- Refresh status;
- Open phone entry / QR;
- Copy LAN URL.

Если функция или настройка повторяется в нескольких местах, изменение должно отражаться везде.

---

## 2. Appearance & Interface

Пользовательские настройки:

- язык;
- тема;
- density;
- fullscreen;
- desktop controls;
- Smart Bar / Compact Bar behavior;
- tooltip behavior, если будет настройка;
- accessibility options, если появятся.

При русском языке не оставлять случайные английские labels вроде `Assets`, `Audio`, `Libraries`, если это не internal technical id в Advanced.

Не дублировать язык и тему в трёх местах как статичный шум. Они должны быть:

- видны в bar;
- редактируемы в Settings;
- возможно доступны через quick link из Overview.

---

## 3. Runtime & Entry

Секция объясняет:

- где запущен backend/server;
- с какого устройства открыт UI;
- LAN URL;
- loopback или LAN;
- можно ли открыть интерфейс с телефона;
- QR / phone entry;
- current host;
- current viewer.

Home уже имеет логику входа/подключения. Settings не должен дублировать хаотично, а должен использовать общую модель Entry Context.

Пример:

```text
Host: ноутбук
Viewer: этот же ноутбук
Entry: LAN URL доступен
Raspberry Pi: offline
ESP32: offline
```

Если открыт телефон:

```text
Host: ноутбук
Viewer: телефон
Entry: подключён через LAN URL
Raspberry Pi: offline
ESP32: offline
```

---

## 4. Platform Nodes & Components

Нужны интерактивные карточки узлов, не простая таблица.

### Карточка узла

Каждый физический узел:

- Raspberry Pi;
- ESP32;
- future controller board.

В карточке:

- corner badge статуса;
- роль/назначение;
- online/offline/degraded;
- last seen;
- IP/API/version, если известно;
- первые 3 модуля;
- show more / переход в подробности;
- список компонентов в подробной секции;
- кнопка `+ Add module`.

`+ Add module` может быть видна всегда, но если edit mode выключен, tooltip объясняет, что нужно включить режим редактирования.

### Модель вложенности

Использовать:

`Node → Modules → Components`

Примеры:

```text
Node: Raspberry Pi
  Module: Turret
    Components: camera, servo, strobe, pump, lidar
```

```text
Node: ESP32
  Module: Irrigation
    Components: valves, moisture sensors, pump relay
```

```text
Node: Power Controller
  Module: Power / Solar / Wind
    Components: solar panel, wind turbine, converter, charge controller, battery sensor
```

```text
Node: selected controller
  Module: Cat Feeder
    Components: valve/servo, food sensor, schedule logic
```

### Добавление модулей

Wizard добавления:

1. выбрать тип модуля;
2. выбрать узел-владелец;
3. выбрать/уточнить компоненты.

Первый этап:

- открыть выбор типа модуля;
- затем добавить модуль в локальный registry/config;
- offline-узлу можно заранее назначить planned/expected module;
- проверка железа выполняется только когда узел/компонент реально доступен.

Категории модулей:

- Irrigation;
- Turret;
- Power / Solar / Wind;
- Feeding;
- Sensing;
- Media;
- Service;
- Custom.

---

## 5. Sync & Storage

Sync и Storage связаны, но это не одно и то же.

### 5.1 Базовая связь узлов

Показывать отдельным блоком.

Предпочтительное название:

`Базовая связь узлов`

Это обязательная служебная связность, которая не должна отключаться обычным пользовательским тумблером.

Сюда входят:

- язык/тема baseline;
- критичные safety/fault статусы;
- capability/heartbeat узлов;
- минимальный settings baseline;
- данные, необходимые для восстановления управления.

### 5.2 Опциональные sync-домены

Показывать карточками с тумблерами.

Опционально управляемые домены:

- media/content sync;
- report/log mirroring;
- scenario sync;
- большие файлы;
- backup/mirror behavior.

Не делать один тупой тумблер `Sync on/off`.

Если media sync отключена, но служебная связь активна:

`Базовая связь узлов активна, media sync отключена.`

### 5.3 Manual review для конфликтов

Обычная синхронизация идёт автоматически.

Если есть конфликт, система показывает review.

Пример:

```text
Конфликт синхронизации:
- локальная версия: RU, theme A
- remote version: EN, theme B

Действие:
[Оставить локальную] [Принять remote] [Слить вручную]
```

До решения конфликта статус:

`needs review`

Нельзя делать silent overwrite пользовательских настроек.

### 5.4 Storage

Показывать:

- Launcher/runtime folder;
- Logs folder;
- Content root;
- Assets;
- Audio;
- Libraries;
- Reports/data folders, если применимо.

Для каждого пути:

- readable display;
- полный путь в tooltip;
- Copy path;
- Open folder, если поддерживается;
- status: ready / missing / not configured / unavailable;
- file count, если папка существует.

Длинные пути не должны вылезать за карточки.

---

## 6. Open Folder Security

`Open folder` нельзя реализовывать как произвольное открытие любого пути из браузера.

Разрешить только whitelist-пути проекта:

- launcher/runtime folder;
- logs folder;
- content root;
- assets;
- audio;
- libraries;
- reports/data folders, если они являются частью проекта.

Условия доступности:

- backend запущен на trusted desktop host;
- путь принадлежит текущему проекту `Smart_Platform`;
- backend endpoint явно поддерживает действие;
- viewer понимает, что папка открывается на host-устройстве.

Если viewer — телефон или другой не-host клиент:

- показывать `Copy path`;
- `Open folder` скрывать или делать disabled;
- tooltip объясняет:

`Папка находится на host-устройстве. С этого экрана можно скопировать путь, но не открыть Explorer напрямую.`

---

## 7. Module Ownership

Создать отдельную секцию:

`Распределение модулей по узлам`

Не держать ownership внутри карточки ESP32.

Показывать expected/planned ownership отдельно от live availability.

Пример:

- Irrigation → ESP32;
- Turret → Raspberry Pi;
- Gallery → platform service;
- Laboratory → platform service;
- Power / Solar / Wind → selected power/controller node;
- Cat Feeder → selected node.

Если узел offline, ownership всё равно можно показывать как expected/planned ownership, но не как live status.

---

## 8. Advanced / Developer Details

Технические детали доступны, но не в главном Overview.

Возможное содержимое:

- raw shell snapshot;
- registry count;
- API status;
- technical runtime profile id;
- debug payloads;
- owner routing;
- sync details;
- stale/cache state;
- deprecated old fields if needed for debug.

Не выносить сырую внутреннюю архитектуру в основной пользовательский обзор.

---

## Tooltip Requirements

Settings должен использовать tooltip-систему уровня Smart Bar.

Подсказки должны:

- открываться по hover;
- открываться по keyboard focus;
- открываться по tap на mobile;
- иметь задержку и поведение как в Smart Bar;
- быть структурными, не сплошным полотном текста;
- не повторять видимый текст;
- объяснять причину состояния;
- объяснять, что делать дальше;
- показывать troubleshooting hints;
- работать для status badges, disabled controls, paths, sync states, node/component statuses.

Структура tooltip:

- title;
- short explanation;
- status/reason;
- next action;
- technical details if needed;
- related path/API/last seen if relevant.

Пример для offline Raspberry Pi:

```text
Title:
Raspberry Pi offline

Reason:
Узел сейчас не отвечает на heartbeat/API.

What to check:
- питание;
- сеть;
- IP/URL;
- запущен ли backend на Raspberry Pi;
- последний ответ, если известен.
```

---

## Control Semantics

Использовать единые типы контролов.

### Status badge

Только отображает состояние.

Примеры:

- online;
- offline;
- degraded;
- local only;
- not detected;
- fault.

### Checkmark

Подтверждает готовность/валидность.

### Toggle switch

Включает/выключает опциональную функцию.

Примеры:

- media sync enabled;
- desktop controls enabled;
- fullscreen enabled.

### Segmented control

Выбор одного режима из нескольких взаимоисключающих вариантов.

Примеры:

- Manual / Automatic;
- Comfortable / Compact;
- Auto / Manual Review.

### Button

Выполняет действие.

Примеры:

- Open folder;
- Copy path;
- Refresh node status;
- Add module.

### Disabled control

Обязан иметь tooltip:

- почему недоступен;
- что нужно подключить/включить;
- какой profile/host поддерживает действие.

---

## Edit Mode

Для структурных и потенциально опасных изменений нужен режим редактирования.

По умолчанию Settings показывает состояние и безопасные quick actions.

Edit mode нужен для:

- Add module;
- bind module to node;
- change module ownership;
- change storage path;
- change optional sync domains;
- create missing folder;
- change hardware/component config.

Логика:

```text
[Edit configuration]

после включения:
[+ Add module]
[Change owner]
[Create missing folder]
[Save] [Cancel]
```

Опасные действия требуют отдельного confirmation.

---

## Уровни действий

### Safe action

Безопасны без edit mode:

- Refresh status;
- Copy path;
- Copy LAN URL;
- Open phone entry / QR;
- открыть подробности;
- перейти к секции.

### Local host action

Выполняются на host-устройстве:

- Open folder;
- open runtime logs;
- open launcher folder.

Требуют trusted desktop host.

### Config action

Меняют конфигурацию:

- Add module;
- bind module to node;
- change ownership;
- change storage path;
- change optional sync domains.

Требуют edit mode + Save/Cancel.

### Dangerous action

Могут повлиять на данные/безопасность:

- reset sync state;
- clear local storage;
- force accept remote settings;
- override conflict;
- clear logs/reports;
- disable critical safety-related behavior.

Требуют confirmation.

---

## Empty States

Settings должен хорошо выглядеть в нормальных промежуточных состояниях.

### Нет подключённых плат

Показывать:

`Локальный запуск, платы offline.`

Дать действия:

- Refresh status;
- Copy LAN URL;
- Open phone entry / QR;
- подсказка, как подключить Raspberry Pi/ESP32.

### Sync ещё не выполнялась

Показывать:

`Синхронизация ещё не выполнялась.`

Не путать с `Local only`.

### Remote node unavailable

Показывать:

`Базовая связь узлов недоступна: remote node offline.`

Tooltip:

- какой узел недоступен;
- что проверить;
- last seen;
- какие sync domains работают только локально.

### Папка missing / not configured

Показывать:

- `missing`, если путь ожидается, но папки нет;
- `not configured`, если путь не задан;
- `unavailable`, если путь есть, но host/viewer не может его открыть.

Действия:

- Copy path;
- Create folder, если безопасно и путь в whitelist;
- Open folder, если доступно.

### У узла нет модулей

Показывать:

`Для этого узла пока нет назначенных модулей.`

`+ Add module` видна всегда, но если edit mode выключен, tooltip объясняет, что нужно включить режим редактирования.

### Модуль добавлен, но железо не найдено

Разделять:

- module planned/configured;
- component not detected;
- node offline;
- verification pending.

---

## Mobile / Responsive Behavior

Settings должен быть usable на desktop, phone, tablet и Raspberry display.

На mobile:

- карточки складываются вертикально;
- длинные пути показываются компактно;
- `Open folder` скрывается или disabled, если viewer не является host;
- `Copy path` остаётся доступным;
- tooltip работает по tap;
- hover-only логика недопустима;
- status chips не должны переполнять карточки;
- add module/edit controls не должны быть слишком мелкими;
- QR/phone entry не должен показываться бессмысленно, если пользователь уже на телефоне.

---

## Layout Exploration

Codex должен предложить 2–3 layout-варианта, но реализовывать один выбранный default, а не кодить сразу три разных дизайна.

Варианты:

### Вариант A — Compact Dashboard

- 4–5 верхних карточек;
- минимальный текст;
- status badges;
- quick actions.

### Вариант B — Runtime-first

- первая крупная карточка объясняет текущий запуск;
- рядом узлы и sync;
- полезно для debugging laptop/phone/Raspberry entry.

### Вариант C — Modular Constructor

- Overview сверху компактный;
- ниже сильный акцент на Node → Module → Component;
- удобно для будущего добавления solar/wind/cat feeder/extra valves.

Рекомендуемый default:

- Overview как Compact Dashboard;
- подробные секции как Modular Constructor.

---

## Known Issues To Fix

1. `Desktop Smoke` не должен отображаться как пользовательский профиль Raspberry Pi.
2. При запуске с ноутбука не показывать Raspberry Pi online.
3. Убрать `neighbor node` / `соседний узел` из user-facing UI.
4. Sync status не должен жить внутри ESP32 card.
5. Слово `локально` в sync должно быть заменено на ясные состояния.
6. `Visible modules: 11` должно быть переименовано как `Модули в registry`, либо перенесено в System/Registry/Advanced.
7. Module ownership вынести в отдельную секцию.
8. Длинные пути не должны ломать карточки.
9. Для путей нужны `Copy path` и, где возможно, `Open folder`.
10. `Assets`, `Audio`, `Libraries` должны быть переведены и показывать status/path/count.
11. Не дублировать язык/тему как статичный шум.
12. Tooltip в Settings привести к качеству Smart Bar.
13. Settings и Smart Bar должны использовать общие статусы, цвета и форматирование.
14. Overview должен быть компактным и практичным.
15. Fullscreen, bar behavior и другие интерактивные настройки не должны работать независимо в разных местах.
16. Кликабельные элементы, которые затрагивают другие классы/modules/backend, должны исправляться не только в `settings.html`, но и в связанных JS/backend местах.

---

## Required Files To Inspect First

Сначала открыть и изучить:

1. `README.md`
2. `chat_prompts/README.md`
3. `chat_prompts/gallery_settings_sync_chat_bootstrap_prompt.md`
4. `docs/48_browser_entry_and_host_launch.md`
5. `docs/49_shell_runtime_and_chat_guardrails.md`
6. `docs/33_shell_snapshot_schema.md`
7. `docs/40_system_shell_navigation_alignment.md`
8. `briefs/sync_and_storage.md`
9. `raspberry_pi/web/static/smart_bar.js`
10. `raspberry_pi/web/settings.html`
11. `raspberry_pi/server.py`
12. `raspberry_pi/settings_store.py`
13. `raspberry_pi/shell_snapshot_facade.py`

---

## Implementation Stage 1

Не переписывать всё хаотично.

Stage 1:

1. Пересобрать верхний Overview вокруг:
   - System Status;
   - Current Runtime;
   - Current Viewer;
   - Platform Nodes;
   - Sync;
   - quick links к пользовательским настройкам.
2. Убрать ложную Raspberry/ESP hierarchy.
3. Убрать/перенести misleading strings из старого UI.
4. Подготовить или переиспользовать shared tooltip/status helpers из Smart Bar.
5. Оставить часть старых секций ниже только если они не вводят в заблуждение.
6. Удалить явно ошибочный или дублирующий контент.
7. Если интерактив связан с backend/shared state, править не только HTML, но и связанные JS/backend modules.
8. Начать выравнивать fullscreen/bar/settings behavior вокруг общего settings state.
9. После изменений проверить live page, а не только source file.

---

## Documentation Requirement

После изменения Settings обновить документацию.

Обязательные действия:

1. Обновить docs, которые описывают runtime, entry, shell, settings, sync, ownership, storage и status semantics.
2. Если новая терминология меняет старую модель, заменить устаревшие термины.
3. Убрать или пометить deprecated формулировки вроде `neighbor node`, ложного Raspberry-as-current-host, pseudo-master semantics.
4. Зафиксировать новую модель:
   - Host;
   - Viewer/current browser client;
   - Platform Node;
   - Module;
   - Component;
   - Module Ownership;
   - Sync domains;
   - Service connectivity;
   - Optional sync;
   - Storage paths.
5. Размножить лучшие решения на всю документацию и UI:
   - общий status model;
   - единая tooltip-система;
   - единые chips/badges;
   - одинаковая логика fullscreen/settings/bar state;
   - одинаковые названия online/offline/not detected/missing/fault/simulated;
   - одинаковая логика Open folder / Copy path / unsupported viewer.
6. Если меняется API/snapshot/settings semantics — обновить contracts/shared docs.
7. Документацию обновлять в том же PR/коммите, не отдельной задачей.

Особенно проверить:

- `README.md`;
- `chat_prompts/README.md`;
- этот Settings bootstrap prompt;
- `docs/48_browser_entry_and_host_launch.md`;
- `docs/49_shell_runtime_and_chat_guardrails.md`;
- `docs/33_shell_snapshot_schema.md`;
- `docs/40_system_shell_navigation_alignment.md`;
- `briefs/sync_and_storage.md`;
- shared contracts, если меняется API/snapshot/settings semantics.

---

## Chat Prompts Update

Создать новый файл:

`chat_prompts/settings_architecture_refactor_chat_bootstrap_prompt.md`

Старый файл:

`chat_prompts/gallery_settings_sync_chat_bootstrap_prompt.md`

оставить для задач Gallery/Settings sync-continuity.

Обновить:

`chat_prompts/README.md`

Добавить туда новый пункт:

```markdown
- `settings_architecture_refactor_chat_bootstrap_prompt.md` — Settings page architecture refactor: runtime/viewer/node model, shared Smart Bar status/tooltip behavior, sync/storage/preferences separation, module/component configuration.
```

---

## Acceptance Criteria

После первого прохода пользователь, открывший Settings с ноутбука без подключённых Raspberry Pi и ESP32, должен ясно видеть:

- система запущена локально с ноутбука/desktop host;
- backend и snapshot API отвечают;
- текущее устройство просмотра определено корректно;
- Raspberry Pi offline;
- ESP32 offline;
- offline относится к узлам, а not detected — к компонентам;
- sync находится в local-only/remote unavailable/never synced состоянии с ясным текстом;
- базовая связь узлов отделена от отключаемой расширенной sync;
- module count относится к registry, а не к физически найденному железу;
- module ownership показан как ожидаемая архитектура, а не live status;
- язык/тема редактируются в правильной секции и не повторяются как статичный шум;
- длинные пути не ломают layout;
- tooltip выглядят и работают как в Smart Bar;
- статусы в Settings совпадают с bar-панелью;
- интерактивные элементы используют единую семантику и не конфликтуют между страницами;
- документация обновлена вместе с изменениями.

---

## Рабочий режим Codex

При старте сессии:

1. Прочитай этот prompt полностью.
2. Открой связанные файлы и docs.
3. Смоделируй практический user flow:
   - пользователь запускает систему с ноутбука;
   - Raspberry Pi и ESP32 offline;
   - пользователь смотрит Settings;
   - bar показывает статусы честно;
   - Settings должен показать ту же truth model.
4. Сопоставь Settings с Smart Bar и найди расхождения.
5. Сначала исправь model/skeleton/status semantics.
6. Затем добавляй интерактив, layout и визуальные улучшения.
7. Если что-то кликабельное затрагивает другие классы/modules/backend, правь связанные места, а не только HTML.
8. После изменений проверь live page.
9. Обнови документацию и prompt/contract files.

---

## Тон интерфейса

Интерфейс должен быть:

- пользовательским, но точным;
- визуально приятным, но не игрушечным;
- инженерно честным;
- компактным сверху и подробным ниже;
- без случайного смешения русского и английского;
- без дублирующих строк;
- с понятной причиной каждого статуса и следующего действия.
