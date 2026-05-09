# Бриф Продуктового Блока: Laboratory

## Назначение

`Laboratory` - это user-facing инженерный контур платформы для модульной проверки, диагностики, bring-up и подбора рабочих параметров.

Внутренний stage/route-контекст для совместимости пока может сохранять:

- legacy alias:
  - `service_test`
- рабочий route:
  - `/service`

Но пользовательское имя для интерфейса теперь фиксируем как:

- `Laboratory`

Новые документы и prompt-файлы должны использовать именно `Laboratory` как
каноническое имя блока. Старый alias нужен только для compatibility-слоя.

## Что это значит для UX

`Laboratory` не должен выглядеть как россыпь отдельных service-страниц.

Это одна отдельная страница с вкладками:

- первый уровень строится по понятным категориям для телефона;
- второй уровень внутри категории строится по module slices;
- category bar и module rail располагаются в верхней части экрана;
- под ними меняется рабочая область;
- в рабочей области всегда должны быть:
  - состояние
  - элементы взаимодействия
  - окно текстовых отчетов и реакции системы
  - expected-result hints

Визуальное направление для `v1`:

- android-like UI language;
- app-like навигация без полного reload всего экрана;
- fullscreen-ready поведение;
- разные layout-режимы для browser и fullscreen использования на телефоне;
- полная видимость даже неподдерживаемых модулей и правил.

## Обязательная логика доступности

- если модуль или подсистема недоступны, они не скрываются;
- они становятся серыми;
- поверх них должен быть серый кликабельный слой;
- при нажатии пользователь получает понятное объяснение:
  - почему модуль недоступен
  - что нужно сделать для разблокировки

## Что уже зафиксировано как baseline

- единая точка входа:
  - `/service`
- `Laboratory` доступна и на `ESP32`, и на `Raspberry Pi`;
- внутри уже есть owner-aware workspace;
- первый углубленный slice уже существует для `strobe`;
- будущие срезы должны повторять ту же модель, а не разъезжаться по разным стилям.
- аппаратный источник истины по наличию и ownership держим в `knowledge_base/resources/smart_platform_workshop_inventory.xlsx`.

## Первая обязательная структура вкладок

Первый уровень строится по крупным категориям, а не по owner:

- `Light`
- `Drives`
- `Water`
- `Audio`
- `Sensors`
- `Camera`
- `Displays`
- `Experimental`

Второй уровень внутри категории строится по hardware/function groups:

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

- `Ultrasonic` здесь означает tweeter / emitter laboratory slice;
- `HC-SR04`-class profile остается experimental частью `Lidar`, а не подменяет `Ultrasonic`;
- `Servos` фиксируются вокруг рабочего turret-baseline `MG996R + PCA9685`;
- `Stepper Motor / Drives` - strictly laboratory-only ветка и не часть turret motion UX;
- `Lidar` должен уметь тестировать owner-side `TFmini Plus` и `HC-SR04`-class laboratory-профили;
- `Displays` держит owner-side `Raspberry Pi Touch Display` отдельно от `Camera` и остается visibly blocked в `ESP32`-only shell, пока `Raspberry Pi` не доступен;
- `Laboratory` должна уметь принимать и внеплановые / неизвестные модули без слома общей структуры.

Верхний статус-бар Laboratory должен показывать:

- какие платы сейчас участвуют в системе;
- какие owner-side узлы доступны;
- какие модули активны, degraded или locked.

## Role Of Laboratory

`Laboratory` нужен не только для разовых тестовых нажатий.

Это место, где пользователь должен:

- проверять отдельные подсистемы;
- подбирать тайминги, частоты, уровни и сценарии;
- начинать и завершать явную engineering-session с оператором, целью, hardware profile и optional external module;
- явно видеть power context для bench-sensitive модулей;
- видеть реакцию системы в расширенном текстовом окне;
- фиксировать `pass`, `warn`, `fail` и operator notes прямо из активного slice в `Gallery > Reports`;
- затем сохранять рабочие параметры.

Дополнительное правило для mixed-shell режима:

- `Raspberry Pi` shell хранит canonical laboratory session backend и синхронизирует его через `/api/v1/laboratory/session*`;
- mirrored shells, например `ESP32`, могут держать draft session локально, но explicit report actions все равно должны нести тот же laboratory context в payload;
- это нужно, чтобы внутренний инженерный контур оставался единым даже при временном участии сторонних модулей или owner-side handoff.

Следующая обязательная стадия:

- перейти от разовых значений к единому profile/preset contract платформы;
- не применять эти значения глобально автоматически;
- дать оператору явный review/apply flow для повышения laboratory profile до системной настройки;
- применять сохраненные параметры в:
  - `automatic`
  - `manual FPV`
  - повторных laboratory-сценариях

## Power Context Baseline

Для slices, завязанных на adjustable bench supply, фиксируем явный ручной контекст:

- `Bench PSU`
- `LiFePO4 battery`

Это нужно, чтобы:

- не притворяться, что shell знает smart-features зарядки, когда питание идет от батареи;
- честно блокировать или снижать scope voltage-sensitive calibration flow в battery-context;
- оставлять operator-visible причину и путь возврата к полноценному bench режиму.

## Audio Baseline

Для будущего `audio` slice фиксируем:

- все три audio-group тестируются независимо;
- UI при этом остается одной общей audio-вкладкой;
- текущая рабочая модель хранения:
  - один общий рабочий профиль
- Bluetooth-колонка должна стремиться автоматически переподключаться к активному узлу:
  - `Raspberry Pi` preferred
  - `ESP32` fallback requirement

## Следующие практические приоритеты

1. Довести `strobe` до profile-ready laboratory slice.
2. Формализовать hardware/function tab model для всего `Laboratory`.
3. Добавить experimental profiles для `HC-SR04`-class range и stepper drives.
4. Развести product UX и deep diagnostic UX окончательно.
5. После этого брать `audio` как следующий отдельный module-tab.
