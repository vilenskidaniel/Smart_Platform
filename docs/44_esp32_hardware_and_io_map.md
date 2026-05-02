# ESP32 Hardware And IO Map

Статус документа:

- supporting hardware map, а не замена workbook и не верхнеуровневый product spec;
- читать после `docs/README.md`, `26_v1_product_spec.md`, `04_sync_and_ownership.md`, `05_ui_shell_and_navigation.md` и `43_field_onboarding_and_operations.md`;
- если hardware-role, ownership или laboratory boundaries расходятся с каноническим слоем, приоритет у primary docs и workbook, а этот файл нужно дочищать или сокращать.

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
- `strobe_bench` laboratory profile;
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
- предупреждения по питанию для инженерных тестов.

### 2.5 Degradation And Safety Hooks

- поведение при отсутствии peer;
- поведение при отсутствии датчика;
- семейства только для обслуживания, которые не должны притворяться продуктовыми модулями.

## 3. Что не должно смешиваться в этом документе

- turret-owner hardware map для `Raspberry Pi`;
- product UX flows;
- acceptance matrix.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из старого `ТЗ`, workbook и донорских практик прошивки:

- аппаратное владение `ESP32`, значимое для программной логики;
- границы `I/O` для irrigation и обслуживающего контура;
- наблюдения по питанию и выводу оборудования, влияющие на код, shell и диагностику.

## 5. Каноническая роль `ESP32`

`ESP32` в новой платформе не является "облегчённым вторым мозгом" для всего проекта.

Он нужен как owner-side узел для:

- `Irrigation`;
- локального съема данных с сенсоров;
- локального `SD`-среза и задач резервно-ориентированного хранения;
- части diagnostics;
- профиля `strobe_bench`, используемого только для обслуживания;
- локального присутствия shell при отсутствии `Raspberry Pi`.

Отсюда следуют два правила:

- `ESP32` не подменяет runtime турели на стороне владельца;
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

### 6.2 Семейства обслуживания и `Laboratory`

На `ESP32` также допускаются:

- `strobe_bench` как профиль только для обслуживания;
- отдельные срезы квалификации сенсоров и актуаторов внутри `Laboratory`;
- путь диагностики через `serial/USB`;
- локальный резервный диагностический интерфейс.

### 6.3 Подтвержденная аппаратная карта `ESP32` для `v1`

| Семейство | Продуктовая или служебная роль | Путь владельца | Класс интерфейса | Класс питания | Текущая подтвержденность |
| --- | --- | --- | --- | --- | --- |
| Зоны влажности почвы | продуктовые сенсоры | `Irrigation` | фильтрованные аналоговые входы | шина сенсоров `3.3V` | подтвержденная база: `5` зон растений, точная карта пинов еще открыта |
| Пакет сенсоров среды | продуктовые сенсоры | `Irrigation` | шина `I2C` или цифровых сенсоров | логическая шина `3.3V` | семейство подтверждено, точный набор еще уточняется |
| Перистальтический насос | продуктовый актуатор полива | `Irrigation` | коммутируемый выход актуатора | изолированная силовая линия полива | подтвержденная база |
| Каскад клапанов | продуктовый актуатор полива | `Irrigation` | коммутируемые выходы низкой стороны | силовая линия актуаторов полива | подтвержденная база |
| Модуль `SD` | продуктовое хранилище | `Gallery`, история, прием синхронизации | `SPI` | логическая шина `3.3V` | подтвержденная база |
| Выход `strobe_bench` | актуатор только для обслуживания | `Laboratory / Strobe` | изолированный коммутируемый путь стенда | внешний стендовый путь питания | подтвержденная база |
| Локальные статусные индикаторы | диагностика и легкая обратная связь | shell и обслуживание | простые GPIO или слаботочные выходы | логическая шина | необязательно |

## 8.4 Current IO planning status

Для `ESP32` уже можно считать зафиксированным:

- sensor families должны быть логически отделены от actuator switch families;
- irrigation actuator outputs и bench outputs не должны смешиваться в одной owner-semantics группе;
- `SPI SD` относится к local storage contour, а не к optional cosmetic accessory;
- serial / USB diagnostics path обязателен хотя бы для bring-up и fault tracing.

Пока еще не зафиксировано на уровне exact electrical map:

- конкретные GPIO по каждой зоне;
- окончательный power-module set для logic/actuator rails;
- единый rule для резервных / expansion pins.

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

- коммутируемые выходы низкой стороны для клапанов;
- управление peristaltic pump через отдельный силовой коммутируемый путь;
- стендовые выходы только для обслуживания;
- локальные status LED или подобные легкие индикаторы.

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

## 13. Open electrical questions for `ESP32`

Эти вопросы уже не про продуктовую архитектуру, а про окончательное hardware closure:

- точная pin-to-zone карта для `5` plant zones в первом реальном `ESP32` профиле;
- какие силовые ветки выделяем отдельно для logic, valves, peristaltic path и `strobe_bench`;
- как именно публикуется состояние irrigation-side power readiness в shell и `Laboratory`;
- какие пины считаем reserved заранее под expansion или future sensor packs.
