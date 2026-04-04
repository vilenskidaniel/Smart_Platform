# Preliminary Hardware Inventory

## Уточнение от 2026-04-03: этот inventory не равен ESP32 pinout

- Список ниже больше не трактуется как список кандидатов на прямое подключение к `ESP32`.
- Для `v1` он служит общей inventory-картой всей платформы.
- Перед реальным pinout нужно сначала разделить:
  - что физически относится к локальной зоне `ESP32`;
  - что физически относится к turret-owner на `Raspberry Pi`;
  - что является только электрическим строительным блоком и не должно превращаться в software-модуль.
- До этого момента pin/power документы нельзя считать следующим автоматическим шагом.

Этот файл фиксирует первый рабочий разбор предположительного железа для `Smart Platform`.

Важно: это не финальная спецификация закупки и не утвержденная схема.
Это отправная точка для архитектуры, этапов и будущего pin/power matrix.

## 1. Что входит в список

### Вычислительные узлы

- `ESP32 Dev Board Type-C 30 pin`
- `Raspberry Pi 5 8 GB`

### Камеры и компьютерное зрение

- `OV5647 camera module`
- `IMX219 camera module 130° MF`

### Датчики присутствия, расстояния и среды

- `PIR HC-SR501`
- `HC-SR04`
- `TFmini Plus`
- `DHT22 / AM2302`
- `BH1750`
- `DS18B20`
- `Soil moisture sensor`
- `Water level / reserve sensor`
- `Additional node-local water sensor`

### Накопители и локальная запись

- `SD card module`

### Исполнительные устройства турели и сервиса

- `MG996R servo`
- `IRLZ44N TO-220`
- `LED strobe light 50W red`
- `50W constant-current LED driver`
- `Metal push button 8mm latching IP67`
- `Ultrasonic transducer / speaker x2`
- `Horn speaker x2`
- `Voice / SFX speaker x1`
- `Raspberry Pi microphone`
- `TPA3116D2 XH-M543 dual-channel amplifier board`
- `Soundcore Motion 300 Bluetooth speaker`

### Исполнительные устройства воды

- `Seaflo pump`
- `Peristaltic pump 6–12V`
- `Solenoid valve NC 3.7V`
- `Nozzle`

### Питание и преобразование

- `MP1584 step-down`
- `LM2596 step-down`
- `MT3608 step-up`
- `USB power module`

## 2. Главный архитектурный вывод

Не каждый пункт из списка должен превращаться в отдельный software-модуль.

Правильнее делить железо на четыре уровня:

1. Вычислительные узлы.
2. Пользовательские модули платформы.
3. Аппаратные подсистемы ввода-вывода.
4. Электрические строительные блоки.

### 2.1 Вычислительные узлы

- `ESP32`
- `Raspberry Pi`

### 2.2 Пользовательские software-модули

- `irrigation`
- `turret_bridge`
- `strobe`
- `strobe_bench`
- `diagnostics`
- `settings`
- `logs`

### 2.3 Аппаратные подсистемы ввода-вывода

- `camera_stack`
- `range_sensors`
- `environment_sensors`
- `soil_sensing`
- `turret_motion`
- `turret_audio`
- `turret_water`
- `strobe_power_stage`
- `storage`
- `power_monitoring`
- `physical_controls`

### 2.4 Электрические строительные блоки

Это не самостоятельные software-модули:

- `IRLZ44N`
- `MP1584`
- `LM2596`
- `MT3608`
- `USB power module`
- `constant-current LED driver`
- `nozzle`

Их нужно учитывать в схемах, safety-ограничениях и документации, но не рисовать как самостоятельные страницы UI.

## 3. Как это раскладывается по владельцам

### ESP32

На стороне `ESP32` логично держать:

- полив;
- локальные датчики среды;
- локальные датчики почвы;
- сервисный `strobe_bench`;
- fallback shell;
- часть физических кнопок и safety interlock;
- локальную SD-запись, если она нужна без `Raspberry Pi`.

### Raspberry Pi

На стороне `Raspberry Pi` логично держать:

- камеру;
- машинное зрение;
- автоматические turret-сценарии;
- turret runtime;
- логику наведения;
- роль владельца `strobe`, `turret_water`, `turret_audio`, `turret_motion`.

### Важная оговорка по turret hardware

Логический владелец турели должен остаться `Raspberry Pi`, как мы и зафиксировали раньше.
Но физическое формирование некоторых сигналов в прототипах не обязательно должно жить прямо на GPIO `Raspberry Pi`.

Реалистичный путь для первой версии:

- `Raspberry Pi` владеет turret runtime и решает, что делать;
- низкоуровневый real-time вывод можно временно отдавать:
  - либо напрямую `Raspberry Pi`, если это надежно;
  - либо отдельному IO-слою на `ESP32`;
  - либо позже нашей собственной плате.

Это не ломает правило ownership, если исполнительный low-level слой остается под командой владельца турели.

## 4. Рекомендуемая первая аппаратная конфигурация v1

Чтобы не утонуть в вариантах, для первого рабочего релиза лучше выбрать не все модули сразу, а один базовый стек.

### Обязательное ядро v1

- `ESP32 Dev Board Type-C 30 pin`
- `Raspberry Pi 5 8 GB`
- одна камера, а не две сразу
- `PIR HC-SR501`
- один дальномерный канал, предпочтительно `TFmini Plus` как основной кандидат для серьезного развития
- `DHT22 / AM2302`
- `BH1750`
- `DS18B20`
- один тип датчика влажности почвы
- `SD card module`
- один прототипный привод движения турели
- `IRLZ44N`
- `LED strobe light 50W red`
- `50W constant-current LED driver`
- один путь воды для турели
- один путь воды для полива
- `Metal push button 8mm`

### Что лучше не тащить в первую связку как обязательное

- обе камеры одновременно;
- `HC-SR04` и `TFmini Plus` сразу как равноправные дальномеры;
- сразу оба типа помп без четкого разделения ролей;
- весь `turret_audio` стек без отдельного сценарного и power-разбора:
  - `ultrasonic_pair`
  - `horn_pair`
  - `voice_fx`
- все power-модули в качестве взаимозаменяемых без утвержденной карты питания.

## 5. Предварительное назначение модулей

### Camera Stack

Кандидаты:

- `OV5647`
- `IMX219 130°`

Рекомендация:

- выбрать одну камеру как `v1 primary camera`;
- вторую оставить как альтернативный профиль, а не как обязательную часть первой интеграции.

### Range Sensors

Кандидаты:

- `HC-SR04`
- `TFmini Plus`

Рекомендация:

- для раннего bench и дешевых тестов можно поддерживать `HC-SR04`;
- для серьезного turret runtime правильнее закладывать отдельный профиль под `TFmini Plus`;
- в архитектуре это должны быть два backend-профиля одного sensor-класса, а не два разных пользовательских модуля.

### Environment Sensors

- `DHT22 / AM2302`
- `BH1750`
- `DS18B20`

Рекомендация:

- объединить их в `environment_pack`;
- в UI показывать как один логический раздел с несколькими каналами.

### Irrigation IO

- `Soil moisture sensor`
- `Seaflo pump`
- `Peristaltic pump 6–12V`
- `Solenoid valve NC 3.7V`
- `Nozzle`
- `Water reserve sensing for drip / spraying storage`

Рекомендация:

- не пытаться сделать один абстрактный "water" модуль для всего;
- разделить:
  - `irrigation_water_path`
  - `turret_water_path`

### Turret Motion

- `MG996R servo`

Рекомендация:

- считать его прототипным actuator-классом, а не финальным решением турели;
- в software завести общий класс `turret_motion`, чтобы потом заменить servo на другой привод без переписывания UI.

### Strobe Path

- `IRLZ44N`
- `LED strobe light 50W red`
- `50W constant-current LED driver`

Рекомендация:

- текущая логика `strobe_bench` хорошо ложится на этот стек;
- боевой `strobe` и bench `strobe_bench` должны и дальше оставаться разными профилями одного семейства.

### Audio Path

- `Ultrasonic transducer / speaker x2`
- `Horn speaker x2`
- `Voice / SFX speaker x1`
- `Raspberry Pi microphone`
- `TPA3116D2 XH-M543 dual-channel amplifier board`
- `Soundcore Motion 300 Bluetooth speaker`

Рекомендация:

- мыслить не одним абстрактным speaker, а как минимум тремя audio-family направлениями:
  - `ultrasonic_pair`
  - `horn_pair`
  - `voice_fx`
- при этом в software/UI это может остаться одним модулем `turret_audio`
  с разными hardware capabilities и channel groups.

Текущее уточнение от пользователя:

- ультразвуковая пара подключается через:
  - `TPA3116D2 XH-M543 DC 12V/24V 120W*2 dual-channel amplifier`
- `horn_pair` текущий кандидат:
  - `4 inch 110x110mm Square Horn Tweeter Stage Speaker Piezoelectric`
- `ultrasonic_pair` текущий кандидат:
  - `40x5mm 490 8 Ohm 2W`
- динамик для голоса/звуковых эффектов и микрофон реализуются через:
  - `Soundcore Motion 300 Wireless Hi-Res Portable Speaker Bluetooth`
- voice/audio path сейчас фиксируем как preferred Bluetooth-path на стороне `Raspberry Pi`,
  но с product-level требованием уметь автоматически подцеплять колонку и к `ESP32`
  как fallback-сценарию;
- внутри корпуса для колонки нужен `Type-C` power path;
- для audio-path обязательно нужна отдельная карта питания, а не “подключим потом по месту”.
- `ultrasonic_pair` и `horn_pair` физически находятся на голове турели;
- `Soundcore Motion 300` встраивается в корпус.
- будущая `audio` service/test surface должна показывать одну общую audio-вкладку,
  внутри которой:
  - `ultrasonic_pair`
  - `horn_pair`
  - `voice_fx`
  тестируются как независимые группы;
- текущая рабочая модель параметров:
  - один общий рабочий профиль.

Что пока еще не зафиксировано окончательно:

- рабочее напряжение и допустимая мощность для `horn_pair`;
- рабочее напряжение и допустимая мощность для `ultrasonic_pair`;
- каким усилением и на каком напряжении питается `horn_pair`;
- как именно подключается `voice / SFX speaker`;
- насколько стабилен и пригоден Bluetooth audio/microphone path для live-режимов;
- какая итоговая power-ветка обслуживает весь `turret_audio`.

Отдельный briefing для этого направления:

- [38_turret_audio_briefing.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/38_turret_audio_briefing.md)

## 6. Тонкие места и риски

### Электрические

- `HC-SR04` требует особого внимания по уровням сигналов, если его цеплять к `ESP32`.
- `MG996R` шумный и прожорливый servo-класс, его нельзя считать "безопасной мелочью" для питания логики.
- `3.7V solenoid valve` выбивается из более типичных 5/12V веток и потребует отдельной проверки driver-схемы и питания.
- `50W LED driver` и `50W strobe` нельзя считать простым GPIO-устройством: software управляет только разрешением/импульсом, но силовая часть живет отдельно.
- `MT3608`, `LM2596`, `MP1584` нельзя выбирать по месту без power map, иначе тесты будут неповторяемыми.

### Архитектурные

- две камеры в первом релизе почти наверняка замедлят проект без заметной пользы;
- два параллельных типа дальномеров в первом релизе тоже размоют effort;
- turret water и irrigation water нельзя смешивать в один software-канал;
- `ultrasonic_pair`, `horn_pair` и `voice_fx` требуют разных классов ограничений,
  монтажа, усиления и сценариев.

### Эксплуатационные

- защелкивающаяся кнопка больше не считается открытым вопросом уровня product intent:
  - для turret-sensitive групп фиксируется physical arm/disarm interlock;
  - его состояние должно отображаться в UI;
  - при `disarmed` блокируются servo motion, `strobe` и ultrasonic/piezo path;
  - детали электрического исполнения и чтения сигнала остаются предметом отдельного pin/power этапа;
- SD-карта полезна, но должна иметь четкий приоритет по ролям: что пишется всегда, а что только при включенной диагностике;
- датчик влажности почвы без конкретизации типа пока нельзя считать стабильной частью v1.

## 7. Что нужно добавить в roadmap

На основе этого списка в план платформы нужно добавить отдельные стадии:

1. `hardware inventory and classification`
2. `pin and power matrix`
3. `driver abstraction layer`
4. `sensor packs on ESP32`
5. `irrigation hardware path`
6. `turret IO prototype layer`
7. `camera qualification`
8. `storage and export layer`
9. `hardware qualification and service checklists`

## 8. Что я рекомендую как альтернативу слишком прямому подходу

Вместо идеи "подключить все перечисленные модули и потом разбираться" лучше идти так:

### Вариант A, рекомендованный

- одна камера;
- один дальномер;
- один turret motion prototype;
- один строб;
- один water path для турели;
- один water path для полива;
- environment pack;
- storage;
- сервисная кнопка.

### Вариант B, более быстрый прототип

- вообще не тащить пока turret water и полный `turret_audio` стек;
- сделать сначала vision + strobe + motion + irrigation;
- остальное добавить после появления стабильной power map.

### Вариант C, самый безопасный инженерно

- сначала утвердить power architecture;
- потом запускать actuator-классы;
- уже после этого делать полную автоматику турели.

## 9. Следующий обязательный документ

После этого файла следующим шагом нужен не прямой pinout, а уточняющий federated-слой:

- owner-aware shell routing;
- canonical owner URL propagation;
- proxy-ready service/test flow для peer-owned модулей.

И только после этого можно переходить к pin/power документам уже для реально локальной зоны `ESP32`.


## 11. Уже подтвержденные пользователем выборы для v1 draft

- `IMX219` как основная камера
- `TFmini Plus` как основной дальномер
- `Capacitive Soil Moisture Sensor` как базовый soil-sensor profile
- `SD card module` на стороне `ESP32`
- turret IO напрямую на `Raspberry Pi`
- irrigation path: `1` peristaltic pump + `5` `NC` valves + `5` sensors
- turret water path: `Seaflo 12V`
- turret использует отдельный physical arm/disarm interlock для чувствительных групп;
- в системе должны быть учтены раздельные water-level / reserve сигналы:
  - irrigation reserve
  - turret spray reserve
  - дополнительные node-local water sensors по мере уточнения аппаратной схемы
- legacy `GPIO23` больше не закреплен автоматически
