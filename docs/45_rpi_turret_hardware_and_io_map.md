# Raspberry Pi Turret Hardware And IO Map

Этот документ фиксирует software-relevant карту `Raspberry Pi` turret-owner узла.

Он нужен, чтобы turret runtime, shell, `Laboratory` и safety rules опирались не на разрозненные заметки,
а на одну понятную owner-aware hardware map.

## 1. Роль `Raspberry Pi` в платформе

`Raspberry Pi` остается owner-side узлом для:

- `Turret` product module;
- camera / FPV / media capture path;
- owner-side range profile;
- motion, sound, strobe и water action family;
- turret-specific policy execution и warm-standby behavior.

## 2. Что должно быть раскрыто здесь

### 2.1 Owner Modules And Hardware Families

- `IMX219 130°` primary camera;
- `TFmini Plus` owner-side range profile;
- `MG996R + PCA9685` motion baseline;
- owner-side display qualification for `8-inch Raspberry Pi 5 4 Monitor LCD`, `1280x800`, `16:10`, `HDMI + USB touch`;
- turret `audio` family;
- turret `strobe` action channel;
- `SEAFLO 12V` turret water path;
- motion wake path и будущий motion-sensor integration boundary.

### 2.2 Runtime-Relevant IO And Interfaces

- camera interface;
- servo / driver control path;
- display output and touch input path;
- range interface;
- audio output path;
- strobe control boundary;
- water actuation boundary;
- peer sync and shell handoff dependencies.

### 2.3 Power And Readiness Boundaries

- `warm standby` expectations;
- turret-sensitive power groups;
- emergency interlock visibility;
- readiness degradation по camera / range / actuator availability.

### 2.4 Laboratory Relationship

- что считается product-owner hardware;
- что допускается как laboratory-only profile;
- как `HC-SR04`-class и другие experimental sensors сосуществуют с turret-owner baseline.

## 3. Что не должно смешиваться в этом документе

- `ESP32` irrigation-owner wiring;
- общий onboarding flow;
- acceptance matrix.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из legacy `ТЗ`, turret docs и donor observations:

- turret-owner hardware boundaries;
- power / interlock / readiness implications для runtime и shell;
- operator-visible degradation rules, завязанные на реальное turret hardware family.

## 5. Каноническая роль `Raspberry Pi`

`Raspberry Pi` остается owner-side узлом turret family.

Это означает:

- turret decisions принимаются здесь;
- camera/range/action readiness canonical именно здесь;
- peer shell может открыть turret routes только через owner-aware handoff;
- потеря `ESP32` не лишает `Raspberry Pi` локальной turret identity, но влияет на shared views и части cross-node scenarios.

## 6. Owner Hardware Families

### 6.1 Primary Product Baseline

Текущий turret-owner baseline включает:

- `IMX219 130°` как primary camera;
- `TFmini Plus` как owner-side range profile;
- `MG996R + PCA9685` как рабочий motion baseline;
- turret `strobe` как product action channel;
- turret `audio` family;
- `SEAFLO 12V` как turret-owned water path.

### 6.2 Motion And Wake Path

Даже если конкретный motion sensor еще не выбран окончательно, документ должен учитывать:

- motion wake path для выхода turret-контура из `warm standby`;
- связь между wake detection, shell readiness и turret policy state;
- видимость этого readiness слоя в `Laboratory` и shell.

### 6.3 Confirmed `Raspberry Pi` turret map for `v1`

| Family | Product or service role | Owner path | Interface class | Power class | Current certainty |
| --- | --- | --- | --- | --- | --- |
| `IMX219 130°` | primary camera | `Turret` / `Manual FPV` / `Automatic` | `CSI` camera path | local logic + camera rail | confirmed baseline |
| `TFmini Plus` | owner-side range | `Turret` and `Laboratory / Lidar` | `UART` or equivalent range link | logic rail | confirmed baseline, exact wiring still open |
| `MG996R + PCA9685` | motion baseline | `Turret` and `Laboratory / Servos` | `I2C` driver + servo PWM outputs | separate servo rail | confirmed baseline |
| `8-inch Raspberry Pi 5 4 Monitor LCD` | owner-side display qualification | `Laboratory / Displays` | `HDMI` video + `USB` touch path | Raspberry Pi display power path | confirmed laboratory display baseline |
| `SEAFLO 12V` | turret water path | `Turret` and `Laboratory / Sprayer` | protected switch / driver boundary | `12V` turret water rail | confirmed baseline |
| Turret `strobe` | deterrence action | `Turret` and `Laboratory / Strobe` | protected switch / driver boundary | dedicated strobe power path | confirmed family, exact channel wiring open |
| Turret `audio` | deterrence / voice / signal family | `Turret` and `Laboratory / Audio` | one dual-channel driver for `ultrasonic_pair` + `horn_pair`, plus Bluetooth path for `voice_fx` | separate audio path | family confirmed, stereo driver topology fixed, exact board wiring still open |
| Motion wake input | wake and readiness path | shell / `Laboratory / Motion Sensor` | sensor input / trigger path | low-power wake-capable path | role confirmed, exact sensor still open |

## 7. Runtime-Relevant Interfaces

### 7.1 Camera

- camera path должен считаться обязательным owner dependency;
- отсутствие camera не должно приводить к притворству полной готовностью турели;
- manual entry и automatic readiness могут иметь разные уровни деградации.

### 7.2 Motion Control

Лучшая текущая архитектурная ставка:

- `Raspberry Pi` не должен строить turret motion вокруг прямого грязного PWM с собственных GPIO как основного design path;
- `PCA9685` остается лучшей baseline-идеей для сервоприводов turret motion;
- shell и runtime должны мыслить readiness на уровне motion family, а не только на уровне "GPIO поднялся".

### 7.3 Range And Action Families

Для turret-owner слоя важно отдельно отражать readiness таких families:

- range;
- strobe;
- audio;
- water;
- camera.

Это лучше старой логики, где всё могло считаться "турелью вообще" без честной разбивки по зависимостям.

## 8. Water And Actuator Boundaries

В новой архитектуре:

- `SEAFLO 12V` принадлежит turret water path;
- irrigation path не имеет права подменять эту ветку;
- turret `strobe` и water actions относятся к отдельным чувствительным actuator families;
- `Raspberry Pi` владеет policy и readiness, но силовые цепи должны идти через защищенные switch / driver boundaries.

Из этого следует лучший design choice:

- не проектировать turret actuators как прямую нагрузку на `Raspberry Pi` GPIO;
- держать logic ownership отдельно от силового исполнения;
- interlock и hard-stop должны быть выше удобства реализации.

## 9. Power And Readiness Boundaries

Для turret-owner side обязательны:

- `warm standby` как baseline mode;
- видимость power state в shell и `Laboratory`;
- отдельная маркировка turret-sensitive power groups;
- emergency interlock как истина для разрешения чувствительных действий;
- degradation при отсутствии camera, range или actuator family.

### 9.1 Interlock visibility contract

На turret-owner side должны различаться два слоя:

- physical interlock truth;
- software-derived runtime reaction.

В UI и API нужно уметь отдельно выражать:

- питание turret-sensitive ветвей подано или снято;
- latched ли `emergency` / `fault` состояние;
- какие action families сейчас обесточены и потому blocked даже при живом shell.

Это важнее старых рассуждений о зарядках, powerbank и общих потребительских сценариях питания.

## 10. Laboratory Relationship

`Laboratory` должна различать:

- product-owner turret baseline;
- service qualification для turret families;
- experimental profiles, которые не являются продуктовой нормой.

Отсюда правило:

- `HC-SR04`-class range sensors допустимы как experimental/laboratory profile;
- они не подменяют `TFmini Plus` как owner-side turret baseline;
- stepper drives не подменяют `MG996R + PCA9685` как рабочую motion baseline.

## 11. Что Реально Стоит Сохранить Из Legacy `ТЗ`

Полезные bits:

- camera, range, audio, strobe и water нужно описывать как разные readiness families;
- turret сценарии реально завязаны на distance bands и multi-stage response;
- media capture и operator-visible reports являются частью turret experience, а не только внутренним логом.

## 12. Что Сознательно Не Переносим Как Истину

Не переносим как канон:

- старый direct-GPIO style для силового управления актуаторами;
- старую идею про `Raspberry Pi` как центральный мозг всего проекта;
- placeholder stack choices вроде обязательных `Flask + SQLite + Telegram` как финальный design;
- старые power assumptions, противоречащие текущему hardware baseline;
- старую vocabulary, где `Видеотека` и отдельные turret page names диктуют IA всей платформы.

## 13. Degradation Rules

При отсутствии `ESP32`:

- `Turret` остается локально доступной;
- `Irrigation` и `ESP32`-owned routes видимы, но degraded/locked;
- `Gallery` остается usable как локальный turret/media/report slice;
- shared reports и peer-derived data маркируются как partial.

При отсутствии turret critical family:

- camera absence должна блокировать или деградировать automatic path;
- range absence должна честно менять readiness соответствующих сценариев;
- interlock active должен блокировать чувствительные action families вне зависимости от peer state.

## 14. Open electrical questions for `Raspberry Pi`

Ниже уже не продуктовые, а hardware-closure вопросы:

- как именно публикуем readback physical emergency interlock в runtime и shell snapshot;
- какая конкретная линия используется для motion wake-profile в `v1`;
- какая конкретная board-level wiring map у dual-channel audio driver, где одна пара спикеров сидит на левом канале, а другая на правом;
- какая topology у protected switch / driver boundaries для `strobe` и `SEAFLO`;
- какие power rails считаем отдельными для logic, camera, servos, audio, strobe и water path.