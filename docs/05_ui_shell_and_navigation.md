# UI Shell And Navigation

Этот документ фиксирует product-level поведение интерфейса `Smart Platform`.
Он описывает не backend-слои, а пользовательскую структуру экранов, переходов и состояний.

## 1. Главная цель интерфейса

Нужен единый browser-first интерфейс, который:

- одинаково узнается на `ESP32` и `Raspberry Pi`;
- работает на телефоне и на компьютере;
- ощущается как приложение, а не как россыпь html-страниц;
- держит единый Android-like visual language на всех разделах, а не на одной отдельной странице;
- по максимуму избегает полного page reload при обычной навигации;
- использует плавные переходы между экранами, состояниями и режимами, чтобы не ощущаться как браузерный набор ссылок;
- умеет переходить в fullscreen и на мобильном, и на ПК;
- показывает все разделы даже при частичном отсутствии модулей;
- честно объясняет, почему модуль недоступен и что нужно сделать.

## 2. Продуктовые разделы shell

В `v1` в навигации должны быть понятные продуктовые разделы:

1. `Главная`
2. `Полив`
3. `Турель`
4. `Gallery`
5. `Laboratory`
6. `Настройки`

Важно:

- `Настройки` остаются общим platform-разделом;
- глубокая история действий и отчетов открывается через `Gallery > Reports`, а не через отдельную верхнеуровневую страницу `Логи`;
- `Gallery` и `Laboratory` уже являются полноценными user-facing разделами, а не скрытыми служебными ветками;
- `Diagnostics`, `Test Bench` и `Service/Test` на текущем этапе считаем разными именами одной и той же user-facing страницы;
- внутреннее stage-name `Service/Test v1` можно сохранять в roadmap и технических brief-файлах, но user-facing имя страницы фиксируется как `Laboratory`.

## 3. Общая модель shell

На обоих узлах должны быть одинаковые базовые элементы:

- верхняя статусная полоса;
- entry-context bar с иконками runtime/client/input/layout;
- карточки статуса `ESP32` и `Raspberry Pi`;
- глобальная навигация;
- зона системных уведомлений и handoff-подсказок;
- индикаторы `online`, `degraded`, `locked`, `fault`, `service`;
- единая визуальная система состояний.

Shell должен выглядеть одинаково независимо от точки входа:

- если открыт `ESP32`, структура остается той же;
- если открыт `Raspberry Pi`, структура остается той же;
- если owner-модуль отсутствует, интерфейс не меняет архитектуру, а показывает деградацию.

### 3.0 Entry Context Strip

Верхняя bar-строка должна не только показывать board ownership, но и объяснять контекст запуска.

Минимальный набор entry-context icons:

- host runtime: `ESP32 shell`, `Raspberry Pi shell` или `Laptop smoke`;
- launch client: `Phone`, `Tablet`, `Desktop/Laptop`, `Raspberry Pi display`;
- topology: `single-board`, `dual-board` или `laptop-only`;
- input profile: `touch`, `keyboard + mouse` или смешанный режим;
- layout helper: `rotate / fullscreen / browser mode`.

Правила для этого слоя:

- hover, focus или tap по иконке должны раскрывать короткое понятное объяснение;
- иконки не заменяют device ribbon, а добавляют контекст запуска поверх owner model;
- browser-side device detection считается эвристикой и не должна притворяться hardware truth там, где браузер не дает точного сигнала;
- `Laptop smoke` обязан быть честно обозначен как testing path, а не как production-equivalent runtime.

### 3.0.1 Launch Profiles And Behavior

На уровне shell фиксируем три большие entry-семантики:

1. `ESP32 shell`
2. `Raspberry Pi shell`
3. `Laptop smoke path`

При этом отдельно от host runtime должен определяться launch client.

Что это означает practically:

- смартфон, открывающий `ESP32` или `Raspberry Pi`, остается phone-client поверх owner shell;
- встроенный `Raspberry Pi` display считается отдельным owner-side display profile, а не просто generic desktop browser;
- ноутбук с локальным запуском должен маркироваться как `Laptop smoke`, даже если backend сейчас исполняет `Raspberry Pi`-ветку.

Поведение по client profile:

- phone: доступен layout helper для перехода в landscape/fullscreen там, где браузер это разрешает;
- desktop/laptop: доступны keyboard shortcuts, hover hints и pointer-oriented interactions;
- Raspberry Pi display: упор на touch/fullscreen density и owner-side screen qualification;
- любой профиль должен честно показывать, какие affordances реально доступны, а какие только желательны.

### 3.1 Visual language baseline

Для `v1` фиксируем не только структуру экранов, но и общие пожелания к внешке.

- интерфейс должен использовать атмосферный fullscreen background, но blur должен лежать на панелях и overlay-поверхностях, а не на самом фоне;
- panel/card surfaces должны быть полупрозрачными и читаемыми поверх фона;
- theme model остается двухрежимной:
  - светлая
  - тёмная
- переключение темы должно происходить быстро и без архитектурной перестройки экрана;
- язык и тема считаются shell-level choice и не должны визуально вести себя как отдельный reload-flow;
- крупные launcher-card surfaces должны ощущаться продуктово, а `Laboratory` и `FPV/manual` могут быть плотнее и инженернее.

Важно:

- не фиксируем конкретные filenames или обязательные JPG/WebP-ассеты как часть product contract;
- если тяжелый фон или media-asset отсутствуют, shell должен деградировать к чистому графическому фону, а не ломать layout.

### 3.2 Feedback and overlays

В `v1` нужен единый набор визуальной обратной связи:

- `question modal` для подтверждений;
- `warning modal` для блокировок и опасных состояний;
- `toast` для коротких уведомлений;
- blocking overlay для pairing, connecting, handoff и других явных transitional состояний;
- optional tooltip / long-press hint только как вторичный helper, а не как единственный способ объяснения.

Правило для действий:

- доступный control может иметь краткий pressed-state и depth effect;
- заблокированный control не должен имитировать успешную активацию;
- после нажатия на blocked-state пользователь должен получить понятную причину и expected next step.

### 3.3 Motion and page transitions

- обычная навигация должна ощущаться как app-like screen transition, а не как набор резких page reload;
- допустимы короткие fade / slide transitions в пределах примерно `150-500 ms`;
- тяжелые loading overlays показываем только там, где реально есть ожидание peer, pairing или content fetch;
- fullscreen считается нормальным способом использования `Laboratory` и `FPV/manual`, а не экспериментальной опцией.

## 4. Поведение peer-owned разделов

### Если владелец раздела недоступен

- раздел остается видимым;
- поверх модуля появляется серый кликабельный слой;
- интерактивные команды блокируются;
- по нажатию показывается всплывающее объяснение:
  - почему модуль недоступен;
  - какие компоненты отсутствуют;
  - что нужно сделать для разблокировки;
- локальный узел не пытается притворяться владельцем чужого модуля.

### Если владелец доступен

- открывается canonical owner route;
- handoff должен быть мягким и визуально согласованным;
- пользователь не должен чувствовать, что его перебросили на “другой сайт”.

### Если пользователь вводит логичный route напрямую

- логичные product/service адреса (`/irrigation`, `/turret`, `/service/irrigation`, `/service/turret`) не должны уходить в raw `404`, если модуль известен shell;
- если route локальный, открывается локальная страница;
- если route peer-owned, открывается owner-aware handoff или blocked explanation;
- `404` допустим только для реально неизвестного route, а не для известного продуктового входа.

## 5. Роль `System Shell`

`System Shell` отвечает за:

- вход в продукт;
- показ доступности узлов;
- handoff между владельцами модулей;
- общую навигацию;
- общие предупреждения;
- shell-level статусные summary и аварийные индикаторы;
- точку входа в `Gallery`, `Laboratory`, `Settings` и быстрый переход в `Gallery > Reports`.

## 6. `Irrigation` в UI

Раздел `Полив` должен мыслить не пинами и драйверами, а пользовательскими сущностями:

- растения;
- зоны;
- датчики;
- текущее и рекомендуемое состояние;
- ручной запуск;
- авто-режим;
- история, предупреждения и статусы.

`Irrigation` также должен уметь появляться как overlay-контур внутри `Turret Manual FPV`, если доступен `ESP32`.

## 7. `Turret` в UI

Раздел `Турель` должен мыслить не runtime-флагами, а сценариями:

- `Manual FPV`
- `Automatic`
- `locked / degraded / fault`
- доступность `camera / range / vision`
- действия:
  - `sprayer`
  - `strobe`
  - `piezo / audio`
  - motion

### Главные правила turret UX

- `Manual` и `Automatic` должны быть live FPV-экранами;
- переход между ними должен происходить сразу, без confirmation dialog;
- системные mode toggles и policy switches живут в `Settings`;
- внутри экранов должен быть быстрый переход в opposite mode;
- неподдерживаемые правила должны быть видимыми, но disabled;
- UI обязан показывать readiness каждого важного элемента.

### Physical Emergency Power Interlock

Для turret-sensitive power branches источником истины считаем аппаратную emergency-chain с физической кнопкой аварийного отключения.

- в released / raised состоянии питание подается, а UI может показывать derived статус `armed / power enabled`;
- в pressed / open состоянии чувствительные ветви физически обесточены;
- базово в safety-chain должны входить:
  - servo motion
  - `strobe`
  - ultrasonic / piezo
  - `sprayer`
  - другие активные deterrence channels, если они заведены в тот же power profile
- sensing и разрешенные диагностические части могут оставаться живыми отдельно, если hardware profile это допускает.

Это влияет на UI так:

- состояние emergency power interlock должно быть видно в shell, `Manual FPV` и `Laboratory`;
- в `Manual FPV` обесточенные группы серые;
- при попытке взаимодействия пользователь получает явное сообщение;
- в лог пишется человеко-читаемая причина:
  - `Emergency power interlock active, <function> unpowered`
- если interlock срабатывает во время работы, software защелкивает `emergency`-state до ручного возврата и явного `clear`.

Важно:

- старое предположение про “виртуальный arming внутри FPV” больше не считаем источником истины;
- источником истины теперь является аппаратный power cut и его UI-репрезентация;
- если турель начинает вести себя некорректно, надежный путь остановки должен быть аппаратным, а не зависеть от корректности ПО.

### Layout `Manual FPV`

В `Manual FPV` должны быть:

- live video;
- crosshair;
- box автообнаружения;
- верхняя правая строка статусов:
  - `arm / emergency power`
  - `manual`
  - подключенные устройства
  - батарея
  - уровень воды распылителя
  - уровень воды irrigation
  - температура
  - влажность
  - время
- верхняя левая часть:
  - кнопка `Automatic`
- нижняя левая часть:
  - стик управления осями
- нижняя часть:
  - постоянная irrigation overlay-панель с рядом клапанов
- нижняя правая часть:
  - `sprayer`
  - `strobe`
  - `piezo`
- кнопки `Запись видео` и `Фото`

### Layout `Automatic`

`Automatic` использует тот же FPV-базис, но в другом режиме:

- live video и наблюдение остаются;
- ручные controls скрыты или недоступны;
- turret действует по выбранной policy;
- `silent observation` должен быть доступен как одно из правил;
- возвращение в `Manual` должно происходить быстрым переключением.

## 8. `Laboratory`

`Laboratory`, `Diagnostics`, `Test Bench` и `Service/Test` на текущем этапе считаем одной сущностью.

User-facing имя:

- `Laboratory`

Внутренний route/stage-term:

- `/service`
- `Service/Test v1`

Это первая страница для изолированной проверки модулей по отдельности.
По ощущению это должна быть “программа внутри программы”: глубокий app-like workspace внутри общей оболочки.

### Общая структура

- в верхней левой части экрана расположен category bar;
- первый уровень строится по понятным user-facing категориям, а не по владельцам;
- второй уровень внутри категории строится по module slices и hardware families;
- сверху всегда есть статус-бар системы;
- статус-бар показывает, какие платы участвуют в системе;
- неучаствующие модули видимы, но серые и блокируются так же, как в shell.
- навигация внутри `Laboratory` должна быть tab-based и без полного reload.

### Первый уровень категорий `v1`

- `Light`
- `Drives`
- `Water`
- `Audio`
- `Sensors`
- `Camera`
- `Displays`
- `Experimental`

### Второй уровень module slices `v1`

- `Strobe`
- `Ultrasonic`
- `Servos`
- `Stepper Motor / Drives`
- `Sprayer / Water`
- `Audio`
- `Air Temperature / Humidity`
- `Soil Moisture + Valves + Peristaltic`
- `LED`
- `Lidar`
- `Camera`
- `Motion Sensor`
- `Raspberry Pi Touch Display`

Важно:

- `Ultrasonic` в этом контуре означает laboratory slice для tweeter / emitter family;
- range-oriented experimental profiles вроде `HC-SR04`-class остаются частью `Lidar`, а не переименовывают `Ultrasonic`;
- `Motion Sensor` может оставаться зарезервированной вкладкой, даже если конкретный датчик еще не выбран;
- вкладка `Motion Sensor` должна сразу проектироваться под wake-testing turret-контура при обнаружении движения объекта в радиусе до примерно `20 m` днем или ночью;
- вкладка `Displays` держит owner-side screen qualification отдельно от `Camera`; `ESP32`-only shell должен показывать ее как blocked до появления `Raspberry Pi` owner-side узла;
- вкладка `Servos` фиксируется вокруг рабочего turret-baseline `MG996R + PCA9685`;
- вкладка `Stepper Motor / Drives` существует только для `Laboratory` и не считается частью turret motion UX;
- вкладка `Lidar` должна уметь тестировать как `TFmini Plus`, так и `HC-SR04`-class laboratory-профиль;
- `Laboratory` должна уметь принимать и внеплановые / неизвестные модули, не ломая общую tab-based структуру;
- вкладки строятся по hardware/function groups;
- peer-owned вкладки остаются видимыми и объясняют блокировку через owner/status.

### Что показывает экран вкладки

При переключении вкладки нижняя рабочая область должна показывать:

- состояние;
- structured status cards;
- элементы взаимодействия:
  - кнопки
  - чекбоксы
  - поля ввода
  - индикаторы
  - ползунки
- окно с текстовыми отчетами и реакцией системы;
- расширенную terminal-like зону;
- явную подсказку, что именно выбирает оператор и какой результат ожидается от тестируемого модуля;
- power-context visibility для bench-sensitive модулей;
- при необходимости графики и дополнительные отчеты.

### Принципы UX

- интерфейс должен ощущаться app-like;
- навигация внутри `Laboratory` не должна требовать полного reload;
- должен быть fullscreen workspace;
- визуальный стиль надо держать ближе к Android UI-языку.
- обычный browser mode и fullscreen mode считаются двумя разными layout-режимами одной страницы;
- в browser mode интерфейс может оставлять больше explanatory cards и shell framing;
- в fullscreen mode chrome уплотняется и ведет себя ближе к приложению, освобождая вертикальное пространство под controls, feedback и evidence;
- важные owner/status/power chips не должны исчезать при переходе между browser и fullscreen режимами.

### Граница `Laboratory` и `Settings`

- `Settings` хранит persistent system/sync/interface/function/style choices;
- `Laboratory` не заменяет `Settings`, а дает изолированный контур экспериментов и bring-up;
- product-level policies и user choices из `Settings` не должны скрывать или переписывать laboratory controls;
- общие shell-токены языка и app chrome могут оставаться едиными, но лабораторные тестовые параметры не должны автоматически становиться системными настройками.
- при этом laboratory profiles и presets должны проектироваться так, чтобы позже оператор мог явно повысить их до системных настроек через отдельный confirm/apply flow, а не через неявную синхронизацию.

## 9. `Gallery`

`Gallery` — отдельный глобальный раздел shell, открываемый с главной страницы.

Это не часть turret-page и не вложенный служебный экран.
Это user-facing explorer всего сохраняемого контента платформы.
Весь контент должен открываться через `Gallery`, а не через отдельный storage-инспектор.

### Внешний характер `Gallery`

- `Gallery` должна ощущаться как explorer, а не как backend file browser;
- `Reports` должны визуально читаться как mixed feed карточек, а не как сырая таблица логов;
- `Plants` и `Media` могут быть визуально более спокойными и catalog-like;
- недоступность peer-content должна маркироваться честно, но без ощущения поломанной страницы.

`Gallery` считаем shared virtual section без одного owner:

- shell открывает единую explorer-страницу;
- локальный узел показывает доступный local slice;
- peer-content подключается как дополнительный источник, а не как “владелец всей страницы”;
- если peer-owner отсутствует, локальный контент остается доступным, а недоступные источники явно маркируются.

Страница `Gallery` должна иметь вкладки:

1. `Plants`
2. `Media`
3. `Reports`

### `Plants`

- каталог растений сада;
- описания;
- параметры ухода;
- правила и рекомендации;
- дальнейшая масштабируемость до большой plant-library.

### `Media`

- видео с камеры;
- изображения с камеры;
- записи при активации турели;
- фотографии растений;
- пользовательские видео из ручного режима;
- пользовательские фото из ручного режима.
- explorer-доступ к файлам в видео- и фото-режимах.

### `Reports`

- экспортированные логи;
- сервисные снимки;
- отчеты диагностики;
- другие сохраняемые laboratory-артефакты;
- каноническую историю действий из `Laboratory` и ручных режимов.
- explorer-доступ к файлам в текстовом, фото- или видео-режиме.

По умолчанию `Reports` должен показывать:

- хронологический список карточек из сущностей разных типов;
- карточки с видео, изображением или текстом;
- маркировку:
  - событие
  - время
  - длительность инцидента, если применимо
- источник действия:
  - `Laboratory`
  - `Manual FPV`
  - другие operator-facing режимы при необходимости
- краткую сводку параметров действия;
- фильтрацию по типу данных.

Для action/history-карточек обязательны как минимум:

- `source_surface`
- `source_mode`
- `action_type`
- `owner_node_id`
- `started_at`
- `duration_ms`, если применимо
- `result`
- `parameter_summary`

Примеры таких записей:

- перемещение сервоприводов в координаты `x/y`;
- запуск `strobe` с профилем, длительностью и power-parameter summary;
- запуск `sprayer` с длительностью и рабочим контуром;
- сохранение фото или видео из `Manual FPV`.

## 10. `Settings`

`Settings` должны быть одной глобальной страницей с секциями:

- `System`
- `Synchronization`
- `Interface`
- `Irrigation`
- `Turret Policies`
- `Style`

Там же живет языковая модель интерфейса:

- глобальное переключение `EN / RU`
- default:
  - `EN`

Там живут:

- system toggles;
- sync parameters;
- rule switches;
- сценарные ограничения;
- будущие настройки safety, target classification и fallback behavior;
- persistent параметры и выборы, которые должны распространяться на продуктовые разделы.

Важно:

- `Settings` не должны дублировать laboratory controls;
- `Settings` не должны определять, какие тестовые вкладки видны в `Laboratory`;
- `Laboratory` нужен именно для экспериментов, bring-up и модульной проверки “не прыгая между приложениями”.

## 11. Что обязательно для `v1`

### Обязательные страницы

- `Главная`
- `Полив`
- `Турель`
- `Gallery`
- `Laboratory`
- `Настройки`

Диагностические summary должны жить:

- на `Главной`;
- в `Laboratory`;
- в коротких shell activity summaries;
- в `Gallery > Reports`;
- но не как отдельный глобальный product-page раздел.

### Допустимые упрощения

- без идеального proxy UI;
- без идеального media transport;
- без полной финализации всех hardware branches;
- без тяжелого визуального декора, если продуктовая структура уже ясна.

## 12. Главное правило навигации

Если пользователь думает:

- “я хочу открыть турель”
- “я хочу посмотреть галерею”
- “я хочу перейти в лабораторию”
- “я хочу настроить правила”

интерфейс должен вести его по понятному продуктово-ориентированному пути.

Если для простой задачи пользователь вынужден понимать:

- `sync_core`
- `driver layer`
- `camera stack`
- `turret water path`

значит навигация спроектирована неправильно.

## 13. Product Target vs Software Baseline

Нужно явно различать:

- `product target v1`
- `software baseline`

`product target v1` — это то, каким должен быть пользовательский опыт.

`software baseline` — это то, что уже доведено до рабочего software-level состояния в текущем репозитории.

Это различие обязательно для:

- `Turret`
- `Gallery`
- `Laboratory`
- `Settings`
