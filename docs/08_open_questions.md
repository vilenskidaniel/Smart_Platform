# Open Questions

## Уже закрыто 2026-04-04

- модель “самый мощный мозг забирает всю систему” не используется;
- принята модель owner-per-module с federated shell;
- `ESP32` не считается локальным владельцем turret-железа;
- user-facing инженерный контур называется `Laboratory`;
- `Gallery` фиксируется как отдельный глобальный раздел;
- `Gallery` — глобальный виртуальный content explorer без одного owner;
- весь пользовательский сохраняемый контент должен открываться через `Gallery`;
- `Gallery` имеет вкладки:
  - `Plants`
  - `Media`
  - `Reports`
- `Laboratory` строится как tab-based страница по модулям;
- `Laboratory` является каноническим именем инженерного контура, который включает diagnostics и test-bench slices;
- недоступные модули остаются видимыми, но серыми и кликабельными;
- turret использует `warm standby`;
- для turret-sensitive групп принят physical emergency power interlock вне зависимости от корректности ПО;
- `Manual FPV` и `Automatic` должны выглядеть как app-like режимы без page reload;
- интерфейс двуязычный:
  - `EN / RU`
  - глобальное переключение в `Settings`
  - default `EN`
- `Soundcore Motion 300` фиксируется как voice/audio Bluetooth path;
- audio-группы:
  - `ultrasonic_pair`
  - `horn_pair`
  - `voice_fx`
- для `turret_audio` рабочая модель профиля сейчас:
  - один общий рабочий профиль
- для `Gallery > Reports` базовый UX фиксируется как хронологический mixed-type список карточек с фильтрацией по типу;
- `Gallery > Reports` считается каноническим user-facing просмотрщиком истории действий из `Laboratory` и ручных режимов;
- для `Laboratory` базовый верхний формат реакции считаем:
  - structured status cards
- `Settings` — отдельная persistent page для system/sync/interface/function/style choices;
- `Settings` не должны подменять `Laboratory` и не должны определять его тестовые вкладки.
- отдельная user-facing страница `Logs` не считается обязательной:
  deep history смотрим через `Gallery > Reports`, shell хранит только краткие activity summaries;
- baseline emergency power chain первого hardware profile включает:
  - servo motion
  - `strobe`
  - ultrasonic / piezo
  - `sprayer`

## Уже закрыто 2026-04-18

- единственная камера в наличии и `v1 primary camera`: `IMX219 130°`;
- `OV5647` убираем из активных hardware-планов;
- range-модель первого шага используем двойную:
  - `TFmini Plus` как owner-side профиль турели
  - `HC-SR04` / improved analog как дополнительный laboratory-профиль после закупки;
- `SD card module` физически относится к `ESP32`;
- роль `SD card module`:
  - расширение хранения для тяжелых файлов
  - резервный прием turret-файлов при синхронизации;
- `SEAFLO 12V` фиксируется как turret water path на `Raspberry Pi`;
- turret water scenario:
  - отпугивание птиц распылением ближе примерно `2 m`
  - опрыскивание растений через ту же форсунку;
- irrigation water path фиксируется отдельно:
  - малый peristaltic pump на `ESP32`
  - клапаны растений;
- рабочий turret motion baseline:
  - `MG996R`
  - `PCA9685`;
- шаговые моторы остаются только в `Laboratory` и не участвуют в turret motion;
- `Soundcore Motion 300` физически в наличии;
- `ultrasonic_pair` и `horn_pair` фиксируются как пары по `2` штуки каждая;
- bench-источник для bring-up:
  - `NICE-POWER dual 30V 10A`;
- автономный силовой baseline:
  - `LiFePO4 12V 100Ah with BMS`;
- боевой `strobe` - часть turret defense-line `v1`, а не отдельный поздний профиль;
- flyback-диоды закуплены, но их номиналы и placement еще нужно верифицировать по реальным нагрузкам.

## Сеть и доступ

- Как будут называться `SSID` и hostname для `ESP32` и `Raspberry Pi`?
- Нужен ли единый процесс сопряжения узлов или сначала достаточно ручного ввода адресов?
- Должен ли один узел уметь подсказывать браузеру адрес второго узла?

## Синхронизация

- Какой интервал heartbeat будет достаточным для first release?
- Какой формат времени использовать для событий: локальный uptime, `epoch` или оба варианта?
- Как бороться с рассинхроном часов между узлами?

## UI и UX

- Нужен ли на первом этапе live-update через `WebSocket`, или достаточно polling?
- Какой общий platform-wide contract нужен для profile/preset persistence модулей?
- Какие поля должны сохраняться как обязательный рабочий профиль для `strobe`?
- Какие поля потом должны стать обязательными для других модулей `Laboratory`?
- Какой формат у service-отчетов считаем основным:
  - только текстовый поток
  - текст + structured cards
  - текст + structured cards + graphs

## Стробоскоп

- Войдет ли `bench-only` профиль в первую версию или останется задачей следующего этапа?
- Нужен ли отдельный профиль “строб как независимый модуль без турели” уже в новом проекте?
- Какие сервисные пресеты стробоскопа обязательны в первой web-версии?

## Логи и отчеты

- Нужен ли экспорт в `JSONL`, `CSV` или оба формата?
- Нужно ли хранить полные журналы на обоих узлах или только сокращенную копию на одном из них?
- Какой минимальный единый набор полей должен стать обязательным для action/history карточек в `Gallery > Reports`?

## Hardware Inventory

- Какой именно тип датчика влажности почвы используется в первом прототипе?
- Какой `HC-SR04`-class модуль берем для закупки: классический `HC-SR04` или улучшенный аналог?

## Electrical And Power

- Какие силовые ветки считаем базовыми: `5V`, `12V`, `3.7V`, отдельные линии для LED/audio?
- Какой power-module становится основным в `v1`: `MP1584`, `LM2596`, `MT3608` или комбинация с четкими ролями?
- Нужен ли отдельный power interlock для турели и для полива?
- Как именно электрически читается и публикуется состояние physical emergency power interlock в UI и логах?
- Хватает ли закупленных flyback-диодов по току, `VRRM` и тепловому запасу для:
  - `SEAFLO`
  - peristaltic pump
  - solenoid valve?

## Turret Hardware

- Какой motion sensor становится `v1` wake-profile для турели?
- Какой усилитель используется для `horn_pair`?
- Нужен ли отдельный усилитель для `voice_fx`, или Bluetooth speaker path полностью закрывает этот контур?
- Какие реальные ограничения по latency/stability у Bluetooth audio + microphone path на `Raspberry Pi`?
- Какое рабочее напряжение и допустимая мощность у:
  - `horn_pair`
  - `ultrasonic_pair`
- Должен ли боевой `strobe` физически сидеть на отдельном драйверном канале относительно `strobe_bench`?

## Irrigation Hardware

- Какой water-path относится именно к поливу и не должен пересекаться с turret-path?
- Нужен ли `DS18B20` в поливе как обязательный датчик уже в `v1` или это позже?
- Должны ли environment sensors быть общими для всей платформы или часть из них относится только к поливу?
- Какой набор water-level sensors считаем обязательным:
  - irrigation reserve sensor
  - turret spray reserve sensor
  - дополнительные локальные датчики уровня/наличия воды на каждом узле
