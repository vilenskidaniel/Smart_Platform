# Safety Risk And Failure Matrix

Этот документ собирает то, что нельзя оставлять разорванным между product-docs, testing notes и legacy `ТЗ`.

Здесь должен жить единый safety-layer для:

- interlock logic;
- risk buckets;
- failure modes;
- operator-visible warnings;
- degradation and shutdown expectations.

## 1. Цель документа

Платформа должна явно отвечать на вопросы:

- что может пойти не так;
- какой узел это обнаруживает;
- кто имеет право блокировать действие;
- как это отражается в shell, `Laboratory` и `Gallery > Reports`;
- какой safe fallback обязателен.

## 2. Основные safety buckets

### 2.1 Power And Interlock

- emergency power interlock;
- turret-sensitive power groups;
- safe startup / safe shutdown;
- actuator isolation.

### 2.2 Water Risks

- irrigation water path faults;
- turret water path faults;
- запрет смешивания owner-логики двух водяных каналов;
- leak / dry-run / pressure-related warnings.

### 2.3 Motion, Light And Audio Risks

- motion overtravel or unavailable actuator;
- strobe misuse or unsafe activation;
- audio misuse or wrong mode activation;
- service vs product command collisions.

### 2.4 Sensor And Vision Risks

- missing or noisy sensor;
- camera absence;
- range-sensor mismatch;
- invalid readings affecting automatic behavior.

### 2.5 Network And Ownership Risks

- peer loss;
- stale snapshot;
- wrong owner execution path;
- operator confusion during degraded state.

## 3. Failure Matrix Skeleton

Для каждого failure-case здесь позже нужно фиксировать:

- `failure_id`;
- affected module / family;
- owner node;
- trigger;
- detection source;
- shell-visible state;
- `block_reason`;
- allowed fallback;
- required operator action;
- report/evidence expectation.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из legacy `ТЗ`, workbook и текущих product docs:

- risk и mitigation fragments;
- safety observations вокруг turret power, strobe, water и service modes;
- operator-visible failure semantics, которые сейчас частично размазаны по нескольким документам.

## 5. Канонические Safety Principles

1. Owner node принимает решение об исполнении опасного действия.
2. Peer shell может отображать и объяснять состояние, но не обходить owner-side блокировки.
3. Emergency interlock сильнее software intent.
4. `Laboratory` не должен автоматически превращать service-tuned параметры в product defaults.
5. Любой опасный или неясный случай должен попадать в report/evidence path.
6. Manual power context for bench-sensitive laboratory slices must stay explicit; software must not pretend it knows adjustable supply capabilities when the operator declared battery-only power.

## 6. Базовая Failure Matrix Для `v1`

| Failure ID | Scope | Trigger | Owner | Shell State | Block Reason | Allowed Fallback | Required Operator Action | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SAF-PWR-01` | turret power | emergency interlock active | `Raspberry Pi` | `locked` | `safety_interlock` | observation-only shell | проверить interlock и силовую группу | report-card + event |
| `SAF-PWR-02` | storage/power | storage unavailable or unstable power causes unsafe writes | local owner | `degraded` | `module_fault` | local read-only or reduced logging | проверить питание и storage path | warning report |
| `SAF-PWR-03` | laboratory bench power | operator selected battery context or adjustable PSU is unavailable for a voltage-sensitive slice | active laboratory owner | `degraded` or `locked` | `power_profile_guard` | keep hint/status view or low-risk non-calibration checks only | выбрать правильный power context или вернуться к bench PSU | laboratory power warning report |
| `SAF-WTR-01` | irrigation water path | pump runs but moisture does not rise | `ESP32` | `fault` for zone | `module_fault` | stop irrigation for affected zone | проверить dry-run, leak, sensor validity | irrigation failure report |
| `SAF-WTR-02` | turret water path | turret water actuator unavailable or unsafe | `Raspberry Pi` | `degraded` or `locked` | `module_fault` | sound/light only defense set | проверить `SEAFLO`, pressure path, interlock | turret action report |
| `SAF-STB-01` | strobe | product strobe requested in forbidden mode or without readiness | `Raspberry Pi` | `locked` | `service_mode_required` or `module_fault` | no strobe action | проверить mode, owner readiness, interlock | blocked-action report |
| `SAF-STB-02` | strobe_bench | service pulse/burst requested outside safe bench state | `ESP32` | `locked` | `service_session_active` or `service_mode_required` | status-only bench view | arm/disarm explicitly and confirm bench state | bench report |
| `SAF-MOT-01` | motion | servo/driver unavailable or overtravel risk | `Raspberry Pi` | `fault` or `degraded` | `module_fault` | freeze movement, allow observation | проверить motion family and calibration | turret motion report |
| `SAF-SNS-01` | irrigation sensing | sensor absent, noisy or invalid | `ESP32` | `degraded` | `module_offline` or `module_fault` | manual-only zone handling | проверить sensor pack and calibration | sensor warning report |
| `SAF-CAM-01` | camera | camera missing or stream unavailable | `Raspberry Pi` | `degraded` or `locked` | `module_offline` | disable automatic targeting, allow limited local diagnostics | проверить camera path | readiness report |
| `SAF-RNG-01` | range | owner-side range unavailable or mismatched profile | `Raspberry Pi` | `degraded` | `module_offline` | camera/manual-only fallback | подтвердить `TFmini Plus` or selected profile | range report |
| `SAF-NET-01` | peer sync | peer heartbeat lost during cross-node flow | local shell | `degraded` | `owner_unavailable` or `peer_sync_pending` | stay local, keep blocked peer routes visible | дождаться peer or continue local-only | sync warning report |
| `SAF-SVC-01` | service vs product | service session active while product command arrives | owner node | `locked` | `service_session_active` | keep current service context | завершить service session or abort it explicitly | service collision report |

## 7. Owner-Wise Safety Notes

### 7.1 `ESP32`

- владеет irrigation safety decisions;
- владеет `strobe_bench` service safety;
- не имеет права локально исполнять turret product actions как owner;
- должен сохранять честную деградацию при потере `Raspberry Pi`.

### 7.2 `Raspberry Pi`

- владеет turret action-family safety;
- учитывает camera, range, motion, water and strobe readiness;
- обязан уважать physical interlock поверх любого software state.

## 8. Operator-Facing Warning Model

При проблеме пользователь или оператор должны видеть не только красный статус, но и:

- какой family затронут;
- какой owner это обнаружил;
- что сейчас разрешено делать;
- какой следующий шаг нужен для восстановления;
- попадет ли событие в `Gallery > Reports`.

Это лучше legacy-подхода, где многие риски только назывались, но не переводились в shell-visible semantics.

## 9. Что Реально Мигрировано Из Legacy `ТЗ`

Сохранены как полезные знания:

- раздельные риски для water, light, sound, movement и sensing;
- связь между критическими ситуациями и operator notification;
- необходимость installation / maintenance awareness.

Не перенесено как норма:

- абстрактные финансовые и организационные риски без влияния на инженерную реализацию;
- слабая security-модель как допустимый baseline;
- старое смешение product, service and safety semantics.