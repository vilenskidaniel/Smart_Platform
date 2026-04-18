# ESP32 Hardware And IO Map

Этот документ фиксирует software-relevant карту `ESP32`-узла.

Он не дублирует workbook как список железа, а объясняет:

- какие hardware families реально принадлежат `ESP32`;
- где проходят `I/O`, power и storage boundaries;
- какие service/laboratory slices должны быть доступны даже без `Raspberry Pi`.

## 1. Роль `ESP32` в платформе

`ESP32` остается owner-side узлом для:

- `Irrigation`;
- локальных environmental и soil-sensing пакетов;
- локального `SD` storage slice;
- `strobe_bench` и части `Laboratory` bring-up;
- fallback shell presence и части diagnostics.

## 2. Что должно быть раскрыто здесь

### 2.1 Owner Modules

- `irrigation`;
- `soil_moisture` / valve / peristaltic chain;
- local environment pack;
- `strobe_bench` service profile;
- local `Laboratory` slices.

### 2.2 Storage And Persistence

- `SD` как storage extension и backup intake;
- какие данные считаются local-first;
- что синхронизируется с peer, а что остается local-authoritative.

### 2.3 IO Families

- sensor inputs;
- irrigation outputs;
- laboratory outputs;
- serial / network / storage interfaces;
- reserved lines and expansion policy.

### 2.4 Power Boundaries

- logic rail expectations;
- actuator isolation points;
- irrigation power path;
- service-test power cautions.

### 2.5 Degradation And Safety Hooks

- поведение при отсутствии peer;
- поведение при отсутствии датчика;
- service-only families, которые не должны притворяться product modules.

## 3. Что не должно смешиваться в этом документе

- turret-owner hardware map для `Raspberry Pi`;
- product UX flows;
- acceptance matrix.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из legacy `ТЗ`, workbook и donor firmware-практики:

- software-relevant `ESP32` hardware ownership;
- `I/O` границы по irrigation и service-contour;
- power и bring-up observations, влияющие на код, shell и diagnostics.

## 5. Каноническая роль `ESP32`

`ESP32` в новой платформе не является "облегчённым вторым мозгом" для всего проекта.

Он нужен как owner-side узел для:

- `Irrigation`;
- локальной sensor acquisition;
- локального `SD` slice и backup-oriented storage tasks;
- части diagnostics;
- service-only `strobe_bench` профиля;
- локального shell presence при отсутствии `Raspberry Pi`.

Отсюда следуют два правила:

- `ESP32` не подменяет owner-side turret runtime;
- `ESP32` не владеет turret water path и боевым `strobe`.

## 6. Owner Hardware Families

### 6.1 Irrigation Chain

Для `ESP32` каноническими считаем такие hardware families:

- soil moisture sensing по plant-zones;
- environment sensing pack;
- peristaltic irrigation pump;
- valve cascade по plant zones;
- local status / diagnostics outputs;
- local `SD` storage module.

### 6.2 Service And Laboratory Families

На `ESP32` также допускаются:

- `strobe_bench` как service-only profile;
- отдельные sensor and actuator qualification slices внутри `Laboratory`;
- serial/USB diagnostics path;
- локальный fallback diagnostics UI.

## 7. Storage And Persistence

`ESP32`-сторона должна мыслиться так:

- `SD` используется для local-first artifacts, которые неудобно держать только во flash;
- irrigation-related history и часть shared content могут сначала появляться локально на `ESP32`;
- синхронизация не отменяет local authority для `ESP32`-owned slices;
- потеря peer-узла не должна ломать локальный storage contract `ESP32`.

Лучшее текущее решение относительно legacy `ТЗ`:

- не фиксировать `SQLite` и `EEPROM` как обязательную продуктовую догму;
- считать format choice implementation-level решением, подчиненным общему storage contract;
- критичные настройки хранить через устойчивый local config path, но не раздувать это до старой hardcoded схемы.

## 8. IO Families And Boundaries

### 8.1 Sensor Inputs

На `ESP32` логично держать:

- analog / filtered inputs для soil moisture zones;
- digital or bus-based environment sensors;
- возможные дополнительные service sensors;
- local status inputs для irrigation and service qualification.

### 8.2 Actuator Outputs

Для `ESP32` допустимы:

- low-side switched valve outputs;
- управление peristaltic pump через отдельный силовой switch-path;
- service-only bench outputs;
- локальные status LEDs или подобные lightweight indicators.

Каноническое правило:

- любой индуктивный irrigation actuator требует защитной схемы;
- logic-level control и силовая часть не должны смешиваться без явной развязки;
- irrigation outputs не должны выглядеть как owner of turret actuators.

### 8.3 Network And Storage Interfaces

`ESP32`-узлу нужны:

- network path для shell и peer sync;
- `SD` interface;
- local diagnostics path;
- возможность staged setup / reconfiguration без полной поломки основного shell contract.

## 9. Power Boundaries

`ESP32` documentation должна исходить из следующего:

- логическая часть живет на своей чистой rail;
- irrigation actuators и laboratory actuators используют отдельные силовые ветки;
- общий `GND` возможен только там, где это не ломает readings и control stability;
- pump/valve family требует flyback protection и аккуратного switch design;
- `strobe_bench` не должен питаться или трассироваться как обычный GPIO toy-load.

## 10. Proven Hints From Legacy And Donor Layer

Из старых материалов стоит сохранить именно такие engineering hints:

- capacitive soil sensors требуют фильтрации и sanity-check, а не голого `analogRead -> percent`;
- valve/pump family должен идти через отдельные switches и protection components;
- `SD` действительно нужен как часть local-first data strategy;
- service outputs лучше держать отдельно от product-owner outputs.

Для `strobe_bench` уже есть подтвержденный bench pattern на donor-side:

- low-side switch;
- внешний силовой путь;
- gate resistor;
- pull-down;
- software only controls timing, not current regulation.

Это полезно как service hardware knowledge и совместимо с новой owner-aware моделью.

## 11. Что Не Считаем Каноническим

Из legacy `ТЗ` не переносим как истину:

- полный старый GPIO map;
- старые конфликтующие pin assignments;
- `Seaflo` как irrigation-owned pump;
- аудио/RGB feature sprawl как обязательный baseline полива;
- идею, что `ESP32` должен отрисовывать turret behavior так, будто он локальный владелец.

Причина простая:

- старый pin map внутренне конфликтует;
- часть железа уже переопределена workbook и новыми решениями;
- owner model проекта стала строже.

## 12. Degradation And Safety Rules

Если `Raspberry Pi` недоступен:

- `ESP32` продолжает владеть irrigation и local service slices;
- `Turret` и turret-owner families видимы, но locked/degraded;
- `Gallery` открывает локальный slice;
- `Laboratory` показывает только реально тестируемые `ESP32`-ветки и peer-waiting состояния.

Если часть irrigation hardware family отсутствует:

- zone или sensor не исчезает silently;
- shell и `Laboratory` должны уметь показать missing / fault / service-required состояние;
- service qualification не должна автоматически менять product defaults.