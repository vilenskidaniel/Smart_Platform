# Проектные решения и карта экранов

Этот документ собирает в одном месте уже согласованные дизайнерские решения, которые напрямую влияют на функционал.

Важно:

- это не декоративный набор образов;
- это рабочий источник истины продуктового уровня по экранной структуре;
- исторический alias стадии `service_test` может сохраняться в заметках совместимости, но пользовательское имя страницы фиксируем как `Laboratory`.

Важно дополнительно:

- подробная информационная архитектура, модель полей и семантика сессий и свидетельств для `Laboratory`, `Gallery` и `Settings` теперь живут в `docs/50_laboratory_v1_workspace_spec.md`, `docs/51_gallery_v1_content_and_reports_spec.md` и `docs/52_settings_v1_persistent_system_spec.md`;
- общий язык состояний, блокировок, tooltip/fullscreen/input contract и граница между bar, `Settings`, `Laboratory` и `Reports` живут в `docs/53_shared_ui_state_and_interaction_contract.md`;
- этот документ должен держать решения по карте экранов и соглашения продуктового уровня, а не заново становиться слоем глубокой спецификации.

## 1. Главные принципы

- интерфейс должен ощущаться как приложение, а не как набор HTML-страниц;
- весь интерфейс должен держать единый язык управления в стиле Android, а не только отдельные сервисные экраны;
- переходы между разделами и режимами должны быть плавными и не создавать ощущение браузерного потока полной перезагрузки;
- пользователь всегда видит полную структуру системы, даже если часть модулей недоступна;
- нижняя часть экрана в `FPV/manual` резервируется под боевые и операторские controls, поэтому глобальную нижнюю навигацию как основной паттерн не выбираем;
- основной shell-routing строится вокруг главной страницы и полноэкранных разделов, а не вокруг постоянного bottom-nav.

## 1.1. Visual system

Нужен не просто удобный layout, а узнаваемый характер интерфейса.

Базовые решения:

- фоновые поверхности могут быть атмосферными и живыми, но рабочие панели должны оставаться читаемыми через полупрозрачные слои и blur;
- сами интерактивные surfaces должны ощущаться как frosted panels / cards, а не как голые браузерные блоки;
- shell и `Gallery` допускают более воздушную и product-like подачу;
- `Laboratory` и `FPV/manual` должны быть плотнее, серьезнее и инженернее;
- `Settings` тоже остается глубоким рабочим пространством, а не облегченной прослойкой между home и diagnostics;
- `Turret Manual` должен стремиться к гибриду `FPV for drones` + `smartphone shooter HUD`, но без нарушения safety, blocked-state truth и owner visibility;
- единая iconography и смысл состояний обязательны для `online / active / attention / neutral / blocked / locked / fault`.

### Operator HUD Standard

- `FPV/manual`, `Automatic FPV` and future `Laboratory` operator panels use a
  dedicated `operator-hud` visual family: tactical typography, compact OSD,
  circular/action controls, local radii, local panel opacity and local telemetry
  spacing.
- Global page themes may affect the page background and ordinary shell pages,
  but must not accidentally recolor operator HUD controls into a mismatched
  card UI. Bar-panel remains neutral and separate.
- Ordinary pages (`Home`, `Gallery`, `Settings`, content lists) remain
  theme-driven card/workspace surfaces. Operator HUD screens are allowed to be
  denser, darker and more game-like if they keep truthful state and safety
  visibility.
- Shared settings may expose durable operator preferences, but the HUD visual
  token set itself should be reusable as a module rather than copied per page.
- The current reusable CSS entry point is
  `raspberry_pi/web/static/operator_hud.css`; pages opt in with
  `class="operator-hud"` and keep page-specific geometry next to the page.

### Темы

- shell поддерживает именованные темы `Meadow`, `Dawn`, `Studio`, `Midnight`, `Sunlit`, `Night`, `Minimal`, `Contrast`;
- каждая тема может иметь собственный характер цвета и атмосферы, но обязана сохранять одинаковый язык состояний, читаемость и уровни контраста;
- тема переключается быстро и применяется ко всем shell-страницам, а не только к `Settings`;
- bar-панель не обязана повторять page theme и может оставаться нейтральной shell-surface;
- поверх темы действует отдельный density-layer:
  - `Comfortable` — обычная продуктовая плотность;
  - `Compact` — заметно более плотная рабочая раскладка для маленьких экранов и узких окон;
- смена density не должна превращаться в декоративный микроэффект: карточки, поля, gaps и высота controls должны реально меняться.

## 1.2. Interaction feedback

Фиксируем единый contract обратной связи:

- активная кнопка: краткий pressed-state без грубой анимационной перегрузки;
- blocked control: не имитирует успех, а дает blocked-feedback и объяснение;
- blocked и locked элементы сначала показывают короткую причину и следующий шаг прямо в интерфейсе, а tooltip или modal только добавляют подробности;
- short feedback: `toast`;
- confirmation / warning: modal window;
- pairing / connecting / handoff: blocking overlay с явным transitional смыслом;
- long-press tooltip допустим как secondary layer, но не как единственный способ объяснить смысл control.
- pressed-state лучше удерживать в коридоре примерно `150-220 ms`;
- hover tooltip появляется с задержкой около `500 ms`;
- tooltip располагается рядом с курсором или местом наведения;
- сдвиг курсора больше чем на `3 px` немедленно отменяет или закрывает hover tooltip;
- без движения курсора tooltip может оставаться видимым до `6 s`, затем закрывается автоматически;
- длинное наведение или зажатие не должны тихо переводить tooltip в другой режим без явного pinned-индикатора;
- мигание разрешается только по whitelist из `docs/53_shared_ui_state_and_interaction_contract.md`, а не как произвольный декоративный эффект;
- повторяющийся helper text не должен одновременно жить под control и в tooltip.
- интерактивные настройки применяются optimistic-first: UI меняется сразу, сохранение идёт в debounce/background и не блокирует клики, ввод или смену секций.
- выбранный язык применяется ко всему видимому тексту; смешение языков допустимо только для собственных имен, URL, аппаратных названий и устойчивых технических идентификаторов.

## 1.3. Transition language

- при обычной навигации используем короткие fade / slide переходы;
- резкие page reload feelings считаются дефектом UX;
- тяжелый spinner показываем только при реальном ожидании owner, pairing или remote content.

## 2. Выбранная навигационная модель

### Главная страница

Главная страница остается launcher-экраном системы.

С нее пользователь открывает:

- `Полив`
- `Турель`
- `Gallery`
- `Laboratory`
- `Settings`

`Gallery > Reports` остается главным просмотрщиком краткой рабочей истории системы, но не отдельной карточкой launcher-уровня.

Bar-панель при этом сохраняет обязательную кнопку `Home` как экстренный возврат на главную страницу с переходом к дефолтному состоянию оболочки, выбранному в `Settings`.

### Desktop

- сверху статус-бар системы;
- слева навигационная область/дерево;
- основная рабочая зона справа.
- status-bar на desktop тянется почти на всю ширину окна с равным внешним отступом с обеих сторон;
- если bar умещается, свободная ширина перераспределяется между group blocks, а не остается пустыми краями.

### Mobile

- сверху статус-бар;
- вход в разделы через главный launcher и контекстные страницы;
- внутри сложных разделов используем собственные локальные левые меню или drawer-entry по месту, а не одну универсальную локальную навигацию для всех deep-pages;
- не опираемся на постоянный bottom-nav, чтобы не отнимать место у FPV и manual controls.
- при узкой ширине status-bar может переходить в dense stacked mode вместо постоянного горизонтального скролла;
- mobile adaptation в первую очередь уменьшает secondary values и плотность chips, а не скрывает важные группы статусов.

### Touch behavior

- mobile-first layout должен избегать случайного pinch-zoom и double-tap frustration там, где экран используется как quasi-app workspace;
- ключевые actions и статусы должны читаться без горизонтального скролла;
- fullscreen для `Laboratory` и `FPV/manual` считается основным, а не дополнительным режимом.

## 3. Правило недоступных модулей

Если модуль, правило или подсистема недоступны:

- они остаются видимыми;
- становятся серыми;
- сверху появляется серый кликабельный слой;
- рядом или внутри control-а остается короткая причина блокировки;
- при нажатии пользователь получает сообщение:
  - почему блокировано
  - что нужно сделать

Подробное объяснение можно раскрывать в tooltip или detail-layer, но не прятать весь смысл только туда.

Это правило относится и к shell-карточкам, и к controls внутри модулей.

## 4. Physical Emergency Power Interlock

Базовая интерпретация для `v1`, которую сейчас фиксируем как рабочую:

- на turret-side есть физическая latching emergency button / safety chain;
- она определяет, подается ли питание на чувствительные turret-группы;
- в released / raised состоянии питание подается, а UI может показывать derived статус `ARMED / POWER ENABLED`;
- в pressed / open состоянии чувствительные ветви физически обесточены;
- baseline safety-chain должна покрывать:
  - servo motion
  - strobe
  - ultrasonic / piezo
  - sprayer
  - активные deterrence channels, если они заведены в тот же power profile

UI-следствия:

- состояние emergency power interlock должно отображаться явным значком в shell, turret HUD и `Laboratory`;
- в `manual` недоступные из-за power cut действия должны быть серыми;
- попытка использовать их должна писать понятный лог:
  - `Emergency power interlock active, <function> unpowered`
- если interlock срабатывает во время активной работы, software входит в latched emergency state до ручного возврата и явного `clear`.

Фиксированная семантика:

- `POWER ENABLED / ARMED = emergency chain closed, питание подано`
- `POWER CUT / DISARMED = emergency chain open, чувствительные ветви обесточены`

## 5. FPV / Manual Screen

`FPV/manual` - это не просто окно видео.

Это operator HUD со следующей компоновкой:

- верхний статус-бар:
  - arm / emergency power state
  - current mode
  - connected devices
  - battery level
  - turret water level
  - irrigation water level
  - temperature
  - humidity
  - time
- верхняя левая часть:
  - кнопка `Automatic`
- нижняя левая часть:
  - стик управления осями
- нижняя центральная/нижняя полоска:
  - irrigation overlay с рядом клапанов
- нижняя правая часть:
  - `sprayer`
  - `strobe`
  - `piezo`

Дополнительно:

- должны быть кнопки `Запись видео` и `Фото`;
- irrigation overlay в manual должен быть постоянным;
- fullscreen является штатным способом использования.

## 6. Automatic Screen

`Automatic` должен использовать тот же FPV-базис, но как другой операторский режим:

- video остается live;
- crosshair и detection-box остаются;
- ручные элементы действия не выдаются как основной способ взаимодействия;
- переход в противоположный режим происходит сразу;
- переключатели политик живут не здесь, а в `Settings`.

## 7. Laboratory Page

Подробная спецификация рабочего пространства `Laboratory`, модель полей, слой сессий и свидетельств и семантика сохранения живут в `docs/50_laboratory_v1_workspace_spec.md`.

Здесь фиксируем только решения по карте экранов, которые должны быть видны на уровне структуры страницы и рабочего ритма.

Заметка по текущей реализации:

- `/service` является единым рабочим пространством `Laboratory` и должен рассматриваться как
  каноническая цель реализации.
- `Turret Service Lane` доступен через `/service?tool=turret_service`.
- `Raspberry Pi Touch Display` доступен через
  `/service?tool=rpi_touch_display`.
- старые страницы `/service/turret` и `/service/displays` являются только
  поверхностями совместимости; не проектируйте новые функции вокруг них.

Пользовательское имя:

- `Laboratory`

Внутренний route:

- `/service`

Alias-имена той же сущности:

- `Diagnostics`
- `Test Bench`
- `Laboratory`

Структура страницы:

- сверху остается профильная шапка `Laboratory` с названием страницы и только теми статусами, которые нужны почти для любого инженерного блока;
- эта шапка не дублирует общую bar-панель, а держит owner/access активного среза, выбранный power-context, источник профиля и статус несохраненных изменений;
- внутри `Laboratory` живет собственное локальное левое меню;
- первый уровень меню строится по инженерным задачам и типам компонентов, а не по owner/vendor сущностям;
- справа открывается рабочая область выбранной карточки;
- сверху - системный status-bar с участием плат;
- ниже - рабочая область выбранной вкладки.

Первый уровень категорий `v1`:

- `Обзор`
- `Питание и интерфейсы`
- `Датчики`
- `Приводы и механика`
- `Клапаны, насосы и жидкостные узлы`
- `Свет и звук`
- `Камеры и дисплеи`
- `Пользовательские и неизвестные компоненты`

Начальный набор карточек `v1`:

- `Strobe`
- `Ultrasonic / Tweeter`
- `Servos`
- `Stepper Motor / Drives`
- `Sprayer / Water`
- `Audio / Piezo`
- `Air Temperature / Humidity`
- `Soil Moisture + Valves + Peristaltic`
- `LED`
- `Lidar`
- `Camera`
- `Motion Sensor`
- `Raspberry Pi Touch Display`

Важно:

- `Ultrasonic` здесь означает tweeter / emitter laboratory slice;
- `HC-SR04`-class range sensors живут внутри `Lidar` как experimental profile, а не как переименование `Ultrasonic`;
- карточка `Raspberry Pi Touch Display` держит owner-side screen qualification отдельно от `Camera` и остается visibly blocked в `ESP32`-only shell, пока `Raspberry Pi` не доступен;
- карточка `Motion Sensor` должна сразу проектироваться под wake-testing turret-контура при обнаружении движения объекта в радиусе до примерно `20 m` днем или ночью;
- карточка `Servos` фиксируется вокруг рабочего turret-baseline `MG996R + PCA9685`;
- карточка `Stepper Motor / Drives` существует только для `Laboratory` и не подменяет turret motion UX;
- карточка `Lidar` должна уметь тестировать как `TFmini Plus`, так и `HC-SR04`-class laboratory-профиль;
- один и тот же тип компонента может тестироваться через разные controller-paths, если это допускает архитектура;
- `Laboratory` должна уметь принимать и внеплановые / неизвестные модули без слома навигации;
- карточки допускают разные field-sets и controls в зависимости от типа компонента;
- фото компонентов и схемы подключения должны приходить из `Gallery`, а не дублироваться как отдельный laboratory-only storage-world;
- browser mode и fullscreen mode должны иметь разную плотность chrome и controls, но одинаковую owner/status visibility;
- полный global bar должен оставаться видимым и в fullscreen; fullscreen уплотняет рабочую область, а не прячет bar;
- bench-sensitive slices должны показывать явный power-context chip и честно блокировать PSU-dependent calibration flow при battery-context.

На уровне screen map для любой laboratory-карточки важно сохранить один и тот же рабочий ритм:

- верхний status/context слой;
- основной region controls и forms;
- state-table region только там, где она реально помогает тесту;
- console или diagnostic trace только как редкий secondary foldout, а не обязательный постоянный блок;
- явное действие `Сохранить выбор`, которое ведет в persistent truth через `Settings`, а не автоматически переписывает product surfaces.

`Обзор` при этом остается summary-слоем: он показывает готовность, активные предупреждения, черновики и общую степень доступности групп компонентов, но не должен становиться главным местом работы вместо профильных карточек.

Пользовательский слой `evidence` здесь больше не нужен: в интерфейсе используется термин `Записи сессии`, а слово `evidence` остается только внутренним техническим alias.

Подробный состав полей, zones и session/evidence semantics определяется deep-spec документацией `Laboratory`.

## 8. Gallery Page

Подробная content-model, структура вкладок, entry types `Reports` и обязательные поля уже живут в `docs/51_gallery_v1_content_and_reports_spec.md`.

На уровне screen map здесь фиксируем только то, что должно быть видно в общей экранной структуре:

- `Gallery` остается отдельной глобальной страницей и shared virtual explorer без одного owner на уровне самой страницы;
- верхняя структура остается `Plants`, `Media`, `Reports`;
- `Media` должна ощущаться как visual/reference layer, а `Reports` как быстрая chronological feed surface;
- при отсутствии peer-owner `Gallery` не ломается и открывает local slice с явной маркировкой недоступных внешних источников;
- `Gallery > Reports` не заменяет собой инженерное рабочее пространство `Laboratory`.

## 9. Settings Page

`Settings` фиксируем как одну глобальную страницу с секциями:

- `Appearance`
- `Runtime`
- `Sync`
- `Storage`
- `Modules`
- `Components`
- `System Services`
- `Policies`
- `Constructor`
- `Diagnostics`

Видимый header страницы короткий: только `Settings` / `Настройки`.
Status summary остается в bar-панели; внутри `Settings` оно повторяется только
если дает расширенный контекст или control. Быстрые действия живут в одном
месте, в нижней части левого меню. `Diagnostics` по умолчанию закрыта.

Именно здесь должны жить:

- глобальный выбор языка интерфейса;
- mode-related toggles;
- policy rules;
- android-like switches вроде:
  - `не стрелять в людей`
  - `silent observation`
  - другие safety/policy правила

Языковая модель:

- весь интерфейс поддерживает два языка;
- язык меняется глобально в `Settings`;
- дополнительные локали (`HE`, `DE`, `FR`, `ES`, `ZH`, `AR`) могут быть selectable TODO-заглушками до отдельного translation-модуля;
- default language:
  - `EN`
- выбранный язык применяется ко всем видимым заголовкам, подсказкам, состояниям и действиям;
- русская локаль не оставляет `host/viewer/runtime/fallback/staged` как обычные пользовательские подписи, если это не технический идентификатор.

Неподдерживаемые правила:

- видимы;
- disabled;
- не скрываются.

Важно:

- `Modules` описывают функциональные системы: `Турель`, `Ирригация`, `Питание`;
- `Components` описывают железо: камера, стробоскоп, пьезо, насосы, клапаны, датчики, сервоприводы, солнечная панель, конвертер;
- software-сущности (`Shell`, `Sync Core`, `Storage Service`) живут в `System Services`, не в hardware module registry;
- `Constructor` — отдельный modal wizard для persistent-создания или редактирования модуля, компонента и системного профиля; laboratory-oriented конструирование и первичная квалификация остаются в `Laboratory`;
- storage-карточки дают `Copy path`, `Open folder`, `Open in app`, preview cleanup и подтвержденное удаление; backend обязан проверять root-boundary перед удалением;
- keyboard action keys работают только на `Turret Manual`; вне control-page клавиши остаются текстовым вводом;
- disabled `Keyboard controls` не скрывает настройки клавиш: поля остаются видимыми, серыми и объясняют в tooltip, что сначала нужно включить режим;
- `Shift` является модификатором мощности: default `50%`, shift `100%`, оба значения переназначаются в `Settings`;
- `Settings` не должны дублировать `Laboratory`;
- `Settings` не должны управлять набором laboratory tabs и локальными экспериментальными controls;
- `Laboratory` нужен для изолированных тестов, а `Settings` — для persistent system-wide choices;
- подтвержденный результат `Сохранить выбор` из `Laboratory` должен становиться видимым и управляемым именно в `Settings`.

### Внешний характер `Settings`

- `Settings` должны ощущаться как спокойная persistent page, а не как engineering console;
- sections и switches читаются как platform-wide policy and preference layer;
- блокировки и недоступные policy-flags остаются видимыми и disabled, а не пропадают.
- `Runtime` не дублирует одну и ту же идею несколькими строками: launch context объединяет host kind, viewer kind и runtime profile.
- `Platform Nodes` как отдельная секция удаляется из `Settings`; физический quick status живёт в bar-панели, а product-level связь с платами отображается через `Modules`.
- `Sync` имеет список `selected_domains`; `Auto` включает все пункты, любое ручное изменение переводит режим в `Manual review`.
- утверждённый sync-набор: service link, module state, shared preferences, reports/logs, plant library, media content (`photo/video/audio/gallery reports`), component registry, software versions (`RPi/ESP/Web UI`).
- `offline`/`not connected` отображается серым/neutral во всех shell-поверхностях; красный используется только для `fault/error/blocked`.
- `Plant Library` является irrigation-linked storage slice и должна вести к irrigation/library context.
- `Components` показываются отдельными карточками с правильными статусами и запоминаемыми вариантами для однотипных инженерных полей.

## 10. Product Target Vs Software Baseline

Для дальнейшей документации фиксируем два разных статуса:

- `product target`
  - что пользователь должен получить в полном смысле `v1`
- `software baseline`
  - что уже собрано и подтверждено на текущем этапе без полного hardware/media closure

Это обязательное различие для `Turret`, `Gallery`, `Laboratory` и `Settings`.

Важно:

- software baseline может временно сохранять route вроде `/logs`;
- но product target viewer для истории действий фиксируется как `Gallery > Reports`.
