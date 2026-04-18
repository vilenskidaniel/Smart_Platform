# Design Decisions And Screen Map

Этот документ собирает в одном месте уже согласованные дизайнерские решения, которые напрямую влияют на функционал.

Важно:

- это не декоративный moodboard;
- это рабочий product-level источник истины по экранной структуре;
- внутренний stage name `Service/Test v1` сохраняется, но user-facing имя страницы фиксируем как `Laboratory`.

## 1. Главные принципы

- интерфейс должен ощущаться как приложение, а не как набор HTML-страниц;
- весь интерфейс должен держать единый Android-like control language, а не только отдельные service-экраны;
- переходы между разделами и режимами должны быть плавными и не создавать ощущение браузерного reload-flow;
- пользователь всегда видит полную структуру системы, даже если часть модулей недоступна;
- нижняя часть экрана в `FPV/manual` резервируется под боевые и операторские controls, поэтому глобальную нижнюю навигацию как основной паттерн не выбираем;
- основной shell-routing строится вокруг главной страницы и полноэкранных разделов, а не вокруг постоянного bottom-nav.

## 2. Выбранная навигационная модель

### Главная страница

Главная страница остается launcher-экраном системы.

С нее пользователь открывает:

- `Полив`
- `Турель`
- `Gallery`
- `Laboratory`
- `Settings`
- `Gallery > Reports` как главный просмотрщик истории действий и отчетов

### Desktop

- сверху статус-бар системы;
- слева навигационная область/дерево;
- основная рабочая зона справа.

### Mobile

- сверху статус-бар;
- вход в разделы через главный launcher и контекстные страницы;
- внутри сложных разделов используем верхнюю левую область под tabs/drawer entry;
- не опираемся на постоянный bottom-nav, чтобы не отнимать место у FPV и manual controls.

## 3. Правило недоступных модулей

Если модуль, правило или подсистема недоступны:

- они остаются видимыми;
- становятся серыми;
- сверху появляется серый кликабельный слой;
- при нажатии пользователь получает сообщение:
  - почему блокировано
  - что нужно сделать

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
- ручные action-controls не выдаются как основной способ взаимодействия;
- переход в opposite mode происходит сразу;
- policy toggles живут не здесь, а в `Settings`.

## 7. Laboratory Page

Пользовательское имя:

- `Laboratory`

Внутренний route:

- `/service`

Alias-имена той же сущности:

- `Diagnostics`
- `Test Bench`
- `Service/Test`

Структура страницы:

- в верхней левой части - первый уровень tab-bar по модулям;
- сверху - системный status-bar с участием плат;
- ниже - рабочая область выбранной вкладки.

Базовый набор вкладок `v1`:

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

Важно:

- вкладка `Motion Sensor` должна сразу проектироваться под wake-testing turret-контура при обнаружении движения объекта в радиусе до примерно `20 m` днем или ночью;
- вкладка `Servos` фиксируется вокруг рабочего turret-baseline `MG996R + PCA9685`;
- вкладка `Stepper Motor / Drives` существует только для `Laboratory` и не подменяет turret motion UX;
- вкладка `Lidar` должна уметь тестировать как `TFmini Plus`, так и `HC-SR04`-class laboratory-профиль;
- `Laboratory` должна уметь принимать и внеплановые / неизвестные модули без слома tab-based навигации;

Каждая вкладка должна содержать:

- состояние модуля;
- structured status cards как основной верхний слой быстрой диагностики;
- элементы взаимодействия:
  - кнопки
  - чекбоксы
  - поля ввода
  - индикаторы
- окно текстовых отчетов и реакции системы;
- расширенную terminal-like панель.

Визуальный стиль:

- ближе к Android control language;
- понятная плотная инженерная компоновка;
- без ощущения сырого backend-экрана.
- это должен быть app-like workspace “программа внутри программы”, а не набор разрозненных utility screens.

## 8. Gallery Page

`Gallery` - это отдельная глобальная страница, открываемая с главной.
Это shared virtual explorer без одного owner на уровне самой страницы.

Базовая верхняя структура:

1. `Plants`
2. `Media`
3. `Reports`

### `Plants`

Содержит:

- каталог растений;
- описания;
- параметры ухода;
- будущую привязку к правилам полива и садовым сценариям.

### `Media`

Внутри как минимум два подраздела:

- `Videos`
- `Pictures`

Содержит:

- записи при активации турели;
- пользовательские видео из manual-режима;
- фотографии растений;
- снимки с камеры и связанные media-артефакты.
- режимы просмотра:
  - video
  - image

### `Reports`

Содержит:

- экспортированные логи;
- service snapshots;
- diagnostic reports;
- другие сохраняемые артефакты Laboratory;
- каноническую историю действий из `Laboratory` и ручных режимов.

Базовое представление:

- хронологический список карточек разных типов;
- карточка может содержать:
  - видео
  - изображение
  - текст
- каждая карточка маркируется:
  - событием
  - временем
  - длительностью инцидента, если она применима;
- источником действия и кратким parameter summary;
- должна существовать фильтрация по типу данных.
- при отсутствии peer-owner `Gallery` должна открывать local slice и явно маркировать недоступные внешние источники.

Для action/history cards обязательны как минимум:

- `source_surface`
- `source_mode`
- `action_type`
- `owner_node_id`
- `started_at`
- `duration_ms`, если применимо
- `result`
- `parameter_summary`

Типовые записи:

- перемещение сервоприводов в координаты;
- запуск стробоскопа с рабочими параметрами;
- включение распылителя с длительностью и контуром;
- фото и видео из ручного режима.

## 9. Settings Page

`Settings` фиксируем как одну глобальную страницу с секциями:

- `System`
- `Synchronization`
- `Interface`
- `Turret Policies`
- `Irrigation`
- `Style`

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
- default language:
  - `EN`

Неподдерживаемые правила:

- видимы;
- disabled;
- не скрываются.

Важно:

- `Settings` не должны дублировать `Laboratory`;
- `Settings` не должны управлять набором laboratory tabs и локальными экспериментальными controls;
- `Laboratory` нужен для изолированных тестов, а `Settings` — для persistent system-wide choices.

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
