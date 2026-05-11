# 16. Hardware Component Profiles

## Роль Файла

Этот файл должен описывать hardware layer так, чтобы он был понятен человеку и не навязывал ложную вечную привязку модулей к конкретным платам.

## Статус

- текущий статус: `active draft`
- этот файл задает активный канон для языка hardware components, заменяемости и текущих временных профилей плат; историческое состояние переноса держим в `knowledge_base/17_open_questions_and_migration.md`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `knowledge_base/resources/smart_platform_workshop_inventory.xlsx` остается companion source для hardware truth.

## Установленные Истины

- controller nodes рассматриваются как hardware/component profiles текущей системы
- sensor, actuator, controller board и auxiliary device описываются на одном общем языке компонентов

## Canon

### 1. Hardware Families

`Hardware layer` в активном каноне должен описываться через families и component profiles, а не через лозунг `этот модуль навсегда равен этой плате`.

Минимальные hardware families `v1`:

1. `Controller boards`
2. `Sensors`
3. `Actuators`
4. `Displays`
5. `Power hardware`
6. `Storage and interface hardware`
7. `Auxiliary and laboratory-only devices`

Каждый hardware profile должен читаться через такие поля смысла:

- family;
- product or service role;
- current owner path or consumer path;
- interface class;
- power class;
- current certainty;
- replaceability notes.

Такой язык нужен, чтобы:

- один и тот же component family можно было переназначать между controller profiles без переписывания product truth;
- `Laboratory` могла квалифицировать alternative hardware without rewriting module canon;
- procurement and inventory discussion не ломали user-facing architecture.

### 2. Controller Boards Как Component Profiles

`ESP32` и `Raspberry Pi` в активном каноне рассматриваются как текущие временные профили плат и controller-side component profiles, а не как вечная архитектурная судьба модулей.

`ESP32` current profile:

- owner-side controller for `Irrigation`;
- local sensor acquisition;
- local `SD`-oriented storage slice;
- local shell presence and diagnostics fallback;
- `strobe_bench` service-only bench path.

`Raspberry Pi` current profile:

- owner-side controller for `Turret` family;
- camera/range/action readiness host;
- turret policy and media/report path;
- local shell/runtime for compute-side surfaces.

Canonical rule:

- boards may be current owners;
- modules are not reducible to those boards;
- board profiles may evolve without rewriting the module definitions themselves.

### 3. Sensors, Actuators, Displays, Power And Auxiliary Devices

Текущие baseline-families `Sensors`:

- soil moisture zone sensing;
- environment sensing pack;
- owner-side turret range sensing with `TFmini Plus` baseline;
- motion wake input family;
- laboratory-only experimental range profiles such as `HC-SR04` class.

Текущие baseline-families `Actuators`:

- peristaltic irrigation pump;
- irrigation valve cascade;
- turret water path with `SEAFLO 12V`;
- turret `strobe` family;
- turret `audio` family;
- turret motion baseline with `MG996R + PCA9685`;
- service-only outputs such as `strobe_bench`.

`Displays`:

- display hardware is its own family, not just a shell afterthought;
- current confirmed laboratory display baseline includes `8-inch Raspberry Pi 5 4 Monitor LCD`;
- display qualification belongs to hardware language even when the shell page is elsewhere.

`Power hardware`:

- logic rail;
- actuator rails;
- servo rail;
- dedicated water/strobe/audio rails where needed;
- bench PSU and related service power equipment;
- interlock-visible power groups.

`Storage and interface hardware`:

- `SD` module on `ESP32`;
- `CSI` camera path;
- `UART` or equivalent range link;
- `I2C` sensor and driver buses;
- `HDMI` and `USB` display/touch paths;
- serial/USB diagnostics paths.

`Auxiliary and laboratory-only devices`:

- experimental range sensors;
- stepper-drive experiments;
- bench-only strobe path;
- qualification-only devices that do not become product baselines automatically.

### 4. Текущие Временные Профили Плат

Current confirmed hardware baseline from donor docs and repo hardware memory:

- `IMX219 130°` is the primary camera baseline;
- `TFmini Plus` is the turret-owner range baseline;
- `MG996R + PCA9685` is the working turret motion baseline;
- `SEAFLO 12V` belongs to turret water path on `Raspberry Pi` side;
- irrigation uses peristaltic pump plus valve cascade on `ESP32` side;
- `ESP32 SD` is part of local-first shared content/storage baseline;
- `strobe_bench` exists as service-only bench hardware, not product turret ownership.

Current power and wake baseline:

- bench bring-up power baseline: `NICE-POWER dual 30V 10A`;
- autonomous field power baseline: `LiFePO4 12V 100Ah with BMS`;
- `ESP32` remains the current always-on sentinel, low-cost scheduler and wake dispatcher for expensive peer-side work;
- `Raspberry Pi` remains the turret-owner compute baseline with `warm standby` expectation rather than permanent full-power duty;
- turret-sensitive power groups must stay readable as hardware truth in shell and `Laboratory`, not inferred only from UI intent.

Current board-family map for `ESP32` profile:

| Family | Owner path | Interface class | Power class | Current certainty |
| --- | --- | --- | --- | --- |
| Soil moisture zones | `Irrigation` | filtered analog inputs | `3.3V` sensor rail | confirmed `5`-zone baseline, exact pins still open |
| Environment sensor pack | `Irrigation` | `I2C` or digital sensor bus | `3.3V` logic/sensor rail | family confirmed |
| Peristaltic pump | `Irrigation` | protected actuator switch | isolated irrigation power rail | confirmed baseline |
| Valve cascade | `Irrigation` | protected low-side actuator outputs | irrigation actuator rail | confirmed baseline |
| `SD` module | `Gallery`, history, sync reception | `SPI` | `3.3V` logic rail | confirmed baseline |
| `strobe_bench` output | `Laboratory / Strobe` | protected bench switch path | external bench power path | confirmed baseline |
| Local diagnostics and status path | shell and service bring-up | serial / `USB` diagnostics plus light GPIO indication | logic rail | required for bring-up |

Current board-family map for `Raspberry Pi` profile:

| Family | Owner path | Interface class | Power class | Current certainty |
| --- | --- | --- | --- | --- |
| `IMX219 130°` | `Turret`, `Manual FPV`, `Automatic` | `CSI` camera path | local logic + camera rail | confirmed baseline |
| `TFmini Plus` | `Turret`, `Laboratory / Lidar` | `UART` or equivalent range link | logic rail | confirmed baseline, exact wiring still open |
| `MG996R + PCA9685` | `Turret`, `Laboratory / Servos` | `I2C` driver + servo PWM outputs | separate servo rail | confirmed baseline |
| `8-inch Raspberry Pi 5 4 Monitor LCD` | `Laboratory / Displays` | `HDMI` video + `USB` touch path | display power path | confirmed laboratory display baseline |
| `SEAFLO 12V` | `Turret`, `Laboratory / Sprayer` | protected switch / driver boundary | `12V` turret water rail | confirmed baseline |
| Turret `strobe` | `Turret`, `Laboratory / Strobe` | protected switch / driver boundary | dedicated strobe rail | family confirmed, exact channel wiring still open |
| Turret `audio` | `Turret`, `Laboratory / Audio` | dual-channel driver path plus Bluetooth audio for `voice_fx` | separate audio path | family confirmed, exact board wiring still open |
| Motion wake input | shell, `Laboratory / Motion Sensor` | sensor trigger path | low-power wake path | role confirmed, exact sensor still open |

Current turret-audio hardware baseline:

- `ultrasonic_pair`:
  - `2 x 5140 Ultrasonic Speaker Horn`
  - current mounting baseline: turret head
- `horn_pair`:
  - `2 x 4 inch 110x110 mm square horn tweeter / piezo stage speaker`
  - current mounting baseline: turret head
  - current note: passive horn/waveguide path without its own smart controller
- `voice_fx`:
  - `1 x Soundcore Motion 300`
  - current mounting baseline: inside turret body
  - current interface expectation: Bluetooth audio path plus `Type-C` power path
- current experimental/high-power baseline for `horn_pair / ultrasonic_pair` is `TPA3116D2 XH-M543` dual-channel amplifier board;
- exact electrical closure for turret audio still remains open around voltage, power budget, final wiring and Bluetooth stability.

Current board-profile summary:

- `ESP32` owns irrigation-side sensing, pump/valve actuation, local `SD`, diagnostics path and service bench slices;
- `Raspberry Pi` owns camera, range, motion, turret water/strobe/audio families and owner-side compute/runtime path;
- peer loss changes availability, but not the truthful identity of those current profiles.

Retained board-closure rules for current hardware profiles:

- `ESP32` keeps sensor families, irrigation actuator families, service bench outputs and local storage contour as different closure groups rather than one undifferentiated GPIO map;
- `Raspberry Pi` keeps `camera`, `range`, `motion`, `water`, `strobe` and `audio` as separate readiness families instead of collapsing them into one generic turret-ready flag;
- logic ownership does not imply direct high-load GPIO driving: water, `strobe`, audio and other sensitive loads stay behind protected switch or driver boundaries;
- current power closure must distinguish `ESP32` logic / valves / peristaltic path / `strobe_bench` and turret-side logic / camera / servos / audio / `strobe` / water rails even before exact board wiring is fully closed;
- physical emergency interlock readback belongs to active hardware truth even while exact final wiring is still being verified.

Важная граница активного канона:

- `HC-SR04`-class sensors and stepper drives remain laboratory-only or experimental profiles unless explicitly promoted;
- they do not silently replace `TFmini Plus` or `MG996R + PCA9685` as product baselines.

### 5. Inventory, Procurement And Replaceability

Primary hardware source of truth for stocked and workshop-level detail:

- `knowledge_base/resources/smart_platform_workshop_inventory.xlsx`

Markdown-канон должен держать только читаемую и устойчивую profile truth:

- what the family is;
- what role it serves;
- what current baseline is confirmed;
- what may be replaced without changing product semantics.

Spreadsheet and registry should keep the denser operational truth:

- exact procurement entries;
- quantity and stock state;
- vendor or SKU detail;
- exact pin maps when they are not yet stable enough for active canon.

Replaceability rules:

- replacing one sensor or actuator inside the same family should not force a rewrite of module canon;
- replacing a current board owner is allowed in principle if the family contracts remain truthful;
- donor-era board maps are implementation support, not architecture destiny.

### 6. Links To Spreadsheet And External Hardware Truth

Active references for hardware truth:

- workshop inventory spreadsheet: `knowledge_base/resources/smart_platform_workshop_inventory.xlsx`
- module-facing hardware baselines in `knowledge_base/10_irrigation_module.md` and `knowledge_base/11_turret_module.md`
- service/runtime boundaries in `knowledge_base/15_platform_services_and_shared_content.md`

Board-centric donor docs remain useful for:

- current wiring closure questions;
- exact interface uncertainty;
- power-boundary details;
- bring-up hints for current controller profiles.

But those docs should no longer act as the primary human-facing hardware canon.

### 6.1 Реальные Кодовые Опоры Текущего Слоя

Чтобы hardware canon был привязан к живым board profiles и runtime baselines, ниже фиксируем текущие implementation anchors:

- `host_runtime/bridge_config.py` - runtime bridge/hardware configuration для owner-side paths и content roots;
- `io_firmware/platformio.ini` - current `ESP32` board profile, filesystem baseline и build-time hardware selection;
- `io_firmware/src/core/SystemCore.cpp` - hardware/bootstrap initialization для текущего `ESP32` profile;
- `io_firmware/src/storage/StorageManager.cpp` - storage bootstrap для `LittleFS` / `SD` baseline;
- `io_firmware/src/net/WiFiBootstrap.cpp` - network/bootstrap layer, который держит `ESP32` как current always-on sentinel path;
- `host_runtime/content/.system/platform_registry.v1.json` - runtime registry с current board и component records.

Отдельного long-lived hardware test layer в репозитории пока нет, поэтому текущий hardware baseline удобнее читать через эти board/runtime surfaces вместе со spreadsheet и модульными canon files.

### 7. Нормативные Таблицы И Примеры

Нормативная таблица component profile fields:

| Field | Meaning |
| --- | --- |
| `family` | component family such as sensor, actuator, board, display, power or auxiliary |
| `role` | product or service role |
| `owner_path` | current owner-side path or consumer path |
| `interface_class` | electrical/data interface class |
| `power_class` | power rail or protection class |
| `certainty` | confirmed baseline, family confirmed, or open |
| `replaceability` | what may change without changing product truth |

Пример controller board profile:

```json
{
  "family": "controller_board",
  "profile_id": "esp32-main.v1",
  "role": "irrigation owner-side controller",
  "owner_path": ["Irrigation", "Laboratory"],
  "interface_class": ["GPIO", "I2C", "SPI", "Wi-Fi"],
  "power_class": "logic_3v3_with_separate_actuator_rails",
  "certainty": "confirmed current profile",
  "replaceability": "board profile may change without redefining irrigation module semantics"
}
```

Пример hardware family entry:

```json
{
  "family": "range_sensor",
  "baseline": "TFmini Plus",
  "role": "turret owner-side range readiness",
  "owner_path": ["Turret", "Laboratory / Lidar"],
  "interface_class": "UART_or_equivalent",
  "power_class": "logic_rail",
  "certainty": "confirmed baseline",
  "replaceability": "laboratory alternatives allowed, product replacement requires explicit promotion"
}
```

Пример laboratory-only profile:

```json
{
  "family": "range_sensor",
  "profile_id": "hc-sr04.experimental",
  "role": "laboratory-only range qualification",
  "owner_path": ["Laboratory / Lidar"],
  "certainty": "experimental",
  "replaceability": "does not silently replace owner-side product baseline"
}
```

## Open Questions

- какой минимум component taxonomy нужен в markdown, а какой должен жить только в spreadsheet/registry
- какая точная pin-to-zone карта и какой reserved expansion set нужны для `5` irrigation zones в первом `ESP32` profile
- какой power-module split фиксируем для `ESP32` logic, valves, peristaltic path и `strobe_bench`
- как именно публикуется physical emergency interlock readback и power-group readiness в shell snapshot и `Laboratory`
- какая точная board-level topology нужна для turret `audio`, motion wake line и protected switch boundaries у `SEAFLO` и turret `strobe`
- насколько глубоко power-rail taxonomy должна входить в активный канон, а не только в historical electrical residue

## TODO

- после стабилизации active draft переаудировать board-level migration residue в ledger и оставить только wiring/electrical reminders без роли active authority source
- позже сверить markdown taxonomy с registry/spreadsheet naming

## TBD

- итоговая taxonomy для future component classes
