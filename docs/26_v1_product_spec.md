# V1 Product Spec

Это верхняя продуктовая точка входа в `Smart Platform`.

Документ нужен, чтобы дальше работать не от внутренних слоев, а от понятного пользовательского продукта.

## 1. Что такое `Smart Platform v1`

`Smart Platform v1` — это локальная browser-first система из двух узлов:

- `ESP32` для полива, локальных датчиков, SD и части service/fallback функций;
- `Raspberry Pi` для турели, камеры, тяжелой логики, media и machine-vision roadmap.

Пользователь должен видеть одну систему с единым визуальным языком на обоих узлах.

Языковая модель `v1`:

- интерфейс двуязычный;
- язык меняется глобально в `Settings`;
- default language:
  - `EN`

## 1.1 Энергетическая модель `v1`

Базовое правило:

- `ESP32` — дежурный и более экономичный узел;
- `Raspberry Pi` — turret-owner и более дорогой по энергии узел.

Для turret-owner baseline-моделью считаем:

- `warm standby`

То есть быстрый выход в рабочее состояние обязателен, а постоянная ставка на полный cold boot не считается нормальным основным путем.

## 2. Что пользователь должен уметь в `v1`

### Базовые сценарии

1. Открыть shell с телефона или компьютера через браузер.
2. Увидеть тот же интерфейс независимо от точки входа.
3. Понять, какие узлы и модули доступны.
4. Открыть `Полив` и работать с irrigation-owner.
5. Открыть `Турель`, если доступен `Raspberry Pi`.
6. Перейти в `Laboratory` и проверить отдельный модуль.
7. Открыть `Gallery`.
8. Открыть `Settings` и поменять глобальные параметры системы и интерфейса.
9. Понять, почему раздел недоступен, если владелец отсутствует.

## 3. Основные продуктовые блоки `v1`

### `System Shell`

Что это:

- единая оболочка;
- главная страница системы;
- статусы узлов и модулей;
- handoff между владельцами модулей;
- общая навигация, настройки и диагностика.

### `Irrigation`

Что это:

- продуктовый модуль полива на `ESP32`.

Что входит в `v1`:

- зоны полива;
- датчики почвы;
- датчики среды;
- малый peristaltic pump через клапанный каскад растений;
- ручной запуск;
- базовый авто-режим;
- service/test проверка зон и датчиков;
- данные на SD и mirrored content layout.

### `Turret`

Что это:

- продуктовый модуль турели на `Raspberry Pi`.

Что входит в `product target v1`:

- `Manual FPV`
- базовый `Automatic`
- live FPV entry point
- `IMX219 130°` как primary camera baseline;
- camera / range / vision readiness model
- `TFmini Plus` как owner-side range profile;
- `HC-SR04`-class profile как laboratory/bench-дополнение, а не замена owner-side дальномеру;
- action-family:
  - motion
  - strobe
  - sound / piezo
  - water
- `SEAFLO 12V` как turret-owned water path;
- `MG996R + PCA9685` как рабочий motion baseline;
- rules/policy switches в `Settings`
- `silent observation`
- owner-aware открытие из любого shell
- readiness и деградация по подключенным компонентам
- media capture из manual режима
- integration с `Gallery`
- hardware emergency power interlock как источник истины для чувствительных turret-групп
- отображение emergency / power state в shell, turret HUD и `Laboratory`
- надежный hard-stop путь вне зависимости от корректности ПО
- motion wake path для выхода turret-контура из `warm standby`, даже если конкретный датчик еще не выбран

### `Laboratory`

Что это:

- безопасный инженерный контур платформы.

Что входит в `v1`:

- `Laboratory`, `Diagnostics`, `Test Bench` и `Service/Test` считаем одной сущностью
- гибридная navigation model для телефона:
  - первый уровень: category tabs
  - второй уровень: module slices
- первый уровень категорий:
  - `Light`
  - `Drives`
  - `Water`
  - `Audio`
  - `Sensors`
  - `Camera`
  - `Displays`
  - `Experimental`
- второй уровень module slices:
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
- structured status cards
- explicit expected-result hints and operator guidance
- логи, графики, отчеты и terminal-like окно
- browser mode for normal phone use through Chrome
- fullscreen app-like mode with denser control layout
- fullscreen workspace
- app-like навигация без полного reload
- вкладочная структура по категориям и модульным срезам
- изолированная среда для bring-up и экспериментов, не заменяющая `Settings`

Важно:

- внутреннее stage-name может оставаться `Service/Test v1`;
- user-facing имя страницы фиксируется как `Laboratory`.
- это первая страница для поочередного тестирования отдельных модулей, но первый UX-уровень должен группировать их в понятные категории для телефона;
- slice `Ultrasonic` означает laboratory-only tweeter / emitter family, а не range-sensing;
- `HC-SR04`-class профиль остается experimental частью slice `Lidar`, а не переопределяет `Ultrasonic`;
- вкладка `Displays` выделяется отдельно от `Camera` и сейчас в `v1` держит owner-side `Raspberry Pi Touch Display` для `8-inch`, `1280x800`, `HDMI + USB touch` панели;
- вкладка `Servos` строится вокруг рабочего turret-baseline `MG996R + PCA9685`;
- шаговые моторы остаются laboratory-only и не подменяют turret motion layer;
- вкладка `Lidar` должна уметь тестировать и `TFmini Plus`, и `HC-SR04`-class профиль;
- вкладка `Motion Sensor` может быть зарезервирована заранее, даже если конкретный датчик еще не выбран;
- целевой сценарий для `Motion Sensor`: wake-testing turret-контура при обнаружении движения объекта в радиусе до примерно `20 m` днем или ночью;
- из `ESP32`-only shell display slice должен оставаться видимым, но locked до появления `Raspberry Pi` owner-side узла;
- `Laboratory` должна уметь принимать и внеплановые / неизвестные модули без слома общей структуры;
- параметры экспериментов из `Laboratory` не должны автоматически становиться глобальными настройками системы;
- при этом `Laboratory` должна быть спроектирована так, чтобы позже оператор мог явно повысить выбранный laboratory profile или preset до системной настройки в `Settings` с последующим применением в `Manual`, `FPV` и других релевантных user-facing режимах;
- slices, завязанные на adjustable bench supply, должны уметь честно различать manual power context:
  - `Bench PSU`
  - `LiFePO4 battery`
- при battery-context voltage-dependent calibration flow остается advisory-only или blocked до появления отдельного battery-safe profile.

### `Gallery`

Что это:

- глобальный раздел платформы для всего контента и сохраняемых артефактов.

Что входит в `v1`:

- `Plants`
- `Media`
- `Reports`
- explorer-представление поверх единого content tree
- режимы просмотра:
  - видео
  - фото
  - текст

`Gallery` — не secondary screen, а обязательная часть продукта.

Важно:

- весь сохраняемый пользовательский контент должен открываться через `Gallery`;
- `Gallery` считается глобальным виртуальным разделом без одного owner;
- если в системе доступен только один узел, `Gallery` должна открывать локальный slice и явно показывать отсутствие peer-content;
- storage-диагностика может жить отдельно как service/internal surface, но не должна подменять собой user-facing `Gallery`.

В `Reports` базовым представлением считаем:

- хронологический список карточек;
- mixed-type сущности;
- фильтрацию по типу данных;
- обязательные метки:
  - событие
  - время
  - длительность инцидента, если применимо
- источник действия:
  - `Laboratory`
  - `Manual FPV`
  - другие operator-facing режимы по мере появления
- краткую сводку параметров и результата.

Важно:

- `Gallery > Reports` считается главным user-facing просмотрщиком истории действий и отчетов;
- история действий из `Laboratory` и ручных режимов не должна оставаться только во внутреннем backend-логе;
- даже если у события нет медиа-вложений, оно должно уметь жить как текстовая report-card с параметрами действия.

## 4. Что не считать отдельными продуктами

В `v1` не считаем отдельными пользовательскими модулями:

- `sync`
- `logs`
- `settings`
- `diagnostics`
- `driver layers`
- `camera stack`
- `sensor packs`
- `water paths`

Они существуют как platform services и implementation layers.

## 5. Поведение интерфейса

### Если shell открыт на `ESP32`

- `Полив` активен;
- `Laboratory` открывается как локальный инженерный контур с peer-aware вкладками;
- `Турель` видна всегда;
- `Gallery` видна всегда;
- если `Raspberry Pi` недоступен, `Турель` остается серой, но видимой;
- если `Raspberry Pi` недоступен, `Gallery` все равно открывает локальный контент и помечает недоступность turret/media источников;
- при появлении `Raspberry Pi` shell предлагает owner-aware переход.

### Если shell открыт на `Raspberry Pi`

- `Турель` активна;
- `Полив` виден всегда;
- `Gallery` видна всегда;
- `Laboratory` открывается как инженерный контур с локальными и peer-owned вкладками;
- если `ESP32` нет в сети, `Полив` остается видимым в degraded/locked состоянии;
- если `ESP32` нет в сети, `Gallery` открывает локальный контент и помечает отсутствие irrigation-side источников;
- при появлении `ESP32` shell предлагает owner-aware переход к irrigation-owner.

## 6. Поведение при деградации

Пользователь должен видеть:

- какой узел недоступен;
- какой модуль заблокирован;
- почему он заблокирован;
- что можно делать локально даже при потере peer-узла.

Система не должна:

- скрывать проблему;
- хаотично перекидывать пользователя на другой host;
- притворяться владельцем чужого модуля.

Недоступные модули должны:

- оставаться видимыми;
- иметь серый кликабельный слой;
- по нажатию показывать причину и шаги для восстановления.

Для `Gallery` это означает:

- открытие локального content slice даже при потере peer-узла;
- явную маркировку недоступных peer-source групп;
- отказ от притворства, что отсутствующий owner по-прежнему может отдать свои файлы.

## 7. Что сохраняется из старого ТЗ

Сохраняем как обязательную основу:

- работа через браузер со смартфона;
- работа через браузер на компьютере;
- единый web-стиль на обоих узлах;
- модульность;
- автономность полива;
- turret-owner на `Raspberry Pi`;
- видимость недоступных модулей;
- `Manual FPV` режим турели;
- live video и operator-facing игровой режим;
- отдельный инженерный контур `Laboratory`;
- локальное хранение данных с последующей синхронизацией.

## 8. Что пока не считаем обязательным для software baseline

Пока не считаем полностью закрытым в текущем software-state:

- реальный live FPV transport;
- полный hardware-backed turret stack;
- production-ready machine vision;
- финальный media pipeline `Gallery`;
- полная реализация всех будущих hardware-вариантов.

Это относится к `product target`, но не означает, что уже все реализовано в коде.

## 9. Порядок продуктовой проработки

Дальше проект нужно вести по продуктовым блокам:

1. `System Shell v1`
2. `Irrigation v1`
3. `Turret v1`
4. `Gallery v1`
5. `Laboratory v1`

После этого уже углубляться в:

- сложный sync;
- расширенную hardware abstraction;
- pin/power документы;
- вторичные сценарии.

## 10. Критерий успеха этого документа

Если после чтения файла можно коротко ответить:

- что входит в `v1`;
- кто чем владеет;
- что пользователь реально увидит;
- где `product target`, а где `software baseline`;
- в каком порядке дальше работать;

значит верхний уровень продуктовой документации снова стал понятным.
