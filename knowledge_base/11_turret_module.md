# 11. Turret Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Turret` как поведенческого модуля, а не как вечной пары `Turret = Raspberry Pi`.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный активный канон для `Turret`; историческое состояние переноса держим в `knowledge_base/17_open_questions_and_migration.md`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/turret_prompt.md` остается prompt-layer companion source для рабочего режима чата.

## Установленные Истины

- `Turret` описывается через роли, действия, sensing и safety
- текущий controller profile — временный implementation baseline
- `Manual`, `Automatic`, `Laboratory` и related services описываются как части одной модульной системы

## Canon

### 1. Роль И Пользовательский Итог

`Turret` - это owner-aware поведенческий модуль, который объединяет наблюдение, operator-facing control, automatic policy behavior и safety-gated action channels.

Для пользователя модуль должен давать такой итог:

- понятную turret page, а не набор runtime flags;
- быстрый вход в `Manual FPV` и понятную картину `Automatic` behavior;
- truthful readiness по sensing и action families;
- видимые и объяснимые blocked/degraded states на peer-view;
- надежный safety path через physical interlock и policy rules.

`Turret` не должен мыслиться как вечная пара `Turret = Raspberry Pi`. Текущий owner-side controller profile - лишь working baseline этого этапа.

### 2. Состав Модуля И Действующие Families

В состав `Turret` как модуля входят:

- product page `/turret`;
- owner-side turret runtime и product-facing summaries;
- sensing families:
  - `camera`
  - `range`
  - `vision`
  - `motion wake source`
- action families:
  - `motion`
  - `strobe`
  - `water`
  - `attack_audio`
  - `voice_fx`
- operator-facing `Manual FPV` surface;
- `Automatic` policy-driven surface;
- owner-side `Laboratory` / service contour;
- media capture, turret events и platform-level activity effects.

Product-level action-family truth:

- `strobe` остается частью turret defense-line `v1`, а не отдельным поздним профилем;
- turret water path относится к turret family и не должен смешиваться с irrigation-owned drip path;
- `attack_audio` входит в action family модуля как направленный атакующий contour для target-directed high-frequency scenarios;
- `voice_fx` входит в turret module как отдельный полнофункциональный audio/talkback contour, а не как побочный режим `attack_audio`.

### 2.1 Два Контура Доступа К `strobe`

Для `strobe` текущий модульный канон различает два неконкурирующих контура:

- product / turret contour на стороне владельца `Raspberry Pi`, который живет внутри `Manual` и `Automatic` как action-family модуля;
- engineering / bench contour на стороне `ESP32`, который живет в `Laboratory` как `strobe_bench` owner-side profile.

Эти контуры не подменяют друг друга:

- продуктовый доступ остается turret-facing operator path;
- инженерный доступ остается laboratory-facing service path;
- параметры, подтвержденные в engineering contour, позже могут сохраняться как рабочий профиль для `Manual`, `Automatic` и повторных laboratory-сценариев.

### 3. Controller Profiles И Временная Реализация

Текущий working controller profile для `Turret v1` таков:

- owner-side turret compute node today-baseline `Raspberry Pi`;
- user-facing название модуля: `Turret`;
- implementation `id` может оставаться `turret_bridge`;
- peer-side shell сохраняет модуль видимым даже при отсутствии owner-side execution.

Текущий confirmed hardware baseline этого шага:

- primary camera baseline: `IMX219 130°`;
- range profiles:
  - `TFmini Plus` как owner-side turret profile;
  - `HC-SR04`-class как laboratory profile;
- motion baseline:
  - `MG996R`
  - `PCA9685`
- turret water baseline:
  - `SEAFLO 12V`
- stepper profiles:
  - только `Laboratory`, не product-ready turret motion;
- audio stock baseline:
  - `ultrasonic_pair = 2`
  - `horn_pair = 2`
  - `voice_fx = Soundcore Motion 300`

Current audio-family topology этого шага:

- turret audio этого этапа больше не описывается как один плоский `audio` actuator;
- `attack_audio` является отдельным dual-channel contour:
  - baseline driver: `TPA3116D2 XH-M543` dual-channel amplifier board;
  - каналы `A` и `B` должны оставаться отдельно управляемыми в software и `Laboratory`;
  - на каждом канале допускается parallel-load path с двумя парами разных излучателей семейства `ultrasonic_pair / horn_pair`, пока точная wiring closure не зафиксирована окончательно;
- `voice_fx` является отдельным полнофункциональным contour:
  - device baseline: `Soundcore Motion 300`;
  - transport baseline: постоянный Bluetooth audio path;
  - microphone path считается обязательной частью этого contour, а не необязательным бонусом;
- preferred reconnect path для `voice_fx` - `Raspberry Pi`, fallback requirement - `ESP32`;
- `Laboratory` по audio должен отдельно уметь:
  - управлять `attack_audio` channel `A` и `B`;
  - запускать attack-audio scenarios;
  - проверять `voice_fx` playback / microphone / talkback / effect path;
- `Settings` должен хранить default scenario и channel levels для `attack_audio`, а также talkback/effect baseline для `voice_fx`.

Current implementation limits:

- real camera/FPV pipeline еще не закрыт;
- real range integration еще не закрыта;
- hardware-backed actuator bindings для `motion / strobe / water / audio` остаются следующим этапом;
- точное рабочее напряжение и допустимая мощность для `horn_pair` и `ultrasonic_pair` еще не закрыты;
- точная board-level wiring map и окончательное разведение dual-channel audio path еще не закрыты;
- устойчивость Bluetooth audio + microphone path для live scenarios еще не закрыта;
- storage/source contract для turret audio assets еще требует финального закрытия;
- часть readiness channels пока simulated, но уже участвует в truthful gate logic.

### Current Owner-Side Runtime Baseline

Current owner-side runtime baseline для `Turret` должен мыслиться как единая runtime-point-of-truth, а не как случайный набор bridge-flags.

Минимальная runtime-структура этого этапа уже различает:

- subsystem groups `motion`, `strobe`, `water`, `attack_audio`, `voice_fx`, `vision`;
- runtime flags уровня `automation_ready`, `target_locked`, `vision_tracking`;
- interlock truth уровня `fault`, `emergency`, `clear`;
- derived module summaries для shell/snapshot/sync вместо ручного дублирования состояния в нескольких местах.

Практический вывод из этого baseline:

- product page `/turret`, shell summaries и sync payload должны читать одну runtime truth;
- `turret_bridge` и related action-family summaries должны вычисляться из runtime, а не жить отдельным несвязанным флаговым слоем;
- переходы `manual`, `automatic`, `laboratory` и action gating должны оцениваться через один runtime contract;
- блокировка чувствительных action families при unsafe runtime conditions считается частью общей runtime policy, а не локальной UI-эвристикой.

### Runtime Trace And Driver Boundary

Owner-side turret runtime может иметь собственный trace-layer и отдельную driver boundary раньше, чем появится полный набор hardware bindings.

Нормативный смысл этого этапа:

- runtime может держать локальный event log для смены режима, interlock и runtime-flags;
- future `driver layer` должен быть явной adapter boundary между runtime contract и конкретными GPIO / PWM / I2C / serial / media bindings;
- owner-side diagnostics может показывать runtime trace и driver-binding summary, не превращая product page `/turret` в raw engineering console;
- raw turret trace остается owner/service-level evidence и не должен автоматически становиться user-facing report stream.

Больше не считаем active truth старое bootstrap-допущение вида `automatic blocked because not armed`.

Новая устойчивая трактовка:

- physical arm/disarm interlock на корпусе является safety source-of-truth;
- UI обязан показывать этот interlock и уважать его;
- product-level semantics `Manual` и `Automatic` не должны заново определяться через bootstrap-stage wording.

### 4. Product Surfaces

Каноническая product page для модуля:

- `/turret`

На product surface пользователь должен видеть:

- общий turret state;
- manual console summary;
- automatic defense summary;
- engineering lane state;
- `camera / range / vision` availability;
- readiness action channels;
- последние turret events.

Product page должна быть product-facing summary surface, а не engineering console.

Peer-side contract:

- на shell, открытом не у owner-side, `Turret` остается видимым;
- peer-side UI не обходит владельца и не притворяется local executor;
- blocked/degraded explanation обязательна вместо скрытия маршрута.

### 5. Manual, Automatic, Laboratory And Service Surfaces

`Manual` и `Automatic` - это не отдельные модули, а два operator-facing режима одного turret module.

`Manual FPV` включает:

- live video как product target;
- operator HUD;
- crosshair;
- truthful readiness display по sensing и action channels;
- capture actions `Фото` и `Запись видео`;
- быстрый переход в `Automatic`.

Manual FPV layout baseline:

- shared FPV base держит live video, crosshair и readiness overlays в центре, а не разбрасывает operator surface по отдельным diagnostic panes;
- верхний status strip держит короткие owner/readiness/interlock summaries и может показывать truthful turret/irrigation water levels, когда эти данные доступны;
- тот же status strip может включать current mode, connected-device availability, battery/environment summaries и clock, если они не вытесняют owner/readiness/interlock truth;
- один mode switch `Manual / Automatic` остается видимым прямо на operator surface;
- manual control cluster может включать joystick/aim controls, capture actions и action-family controls для `attack_audio`, `voice_fx`, `strobe` и `sprayer`;
- irrigation overlay остается видимым в `Manual`, если соответствующий owner path доступен, а не прячется за отдельную страницу;
- если irrigation overlay materialized, он может показывать valve-level controls, air temperature/humidity и water-reserve summaries как shared context, а не как отдельный product page;
- если desktop controls или input helpers выключены, manual controls остаются видимыми, но переходят в честное blocked состояние с коротким next-step explanation.

`Automatic`:

- использует тот же turret module, но policy-driven mode switching и automatic action gating;
- зависит от `camera / range / vision` readiness, rules и available action families;
- не требует отдельного виртуального arm-path поверх physical safety chain;
- использует тот же FPV base, что и `Manual`, но может скрывать manual-only controls, не превращаясь в другую page family;
- должен сохранять быстрый возврат в `Manual`.

`Laboratory`:

- остается owner-side deep engineering contour;
- живет внутри общего `Laboratory` workspace, а не как отдельная product IA;
- держит component-level probes, raw JSON, event logs и engineering scenarios.

Current compatibility route может сохраняться как implementation layer:

- `/service/turret`

Но нормативно он не должен становиться главным способом описывать turret product structure.

Manual as testing rule:

- `Manual` является second-level testing surface;
- first-level deep engineering testing остается в `Laboratory`.
- operator-made captures из `Manual FPV` попадают в `Gallery > Media`, а product-significant capture events могут дополнительно появляться в `Gallery > Reports` по правилам gallery layer.

### 6. Readiness, Vision, Range And Action Gates

Минимальный product-facing sensing model должен уметь выражать:

- `camera available`
- `range available`
- `vision available`
- `target detected`
- `target classified`
- `tracking active`
- `motion wake source`

Current gating truth:

- readiness по `camera`, `range`, `vision` уже участвует в `automatic` gate logic;
- `target_locked` validation не должна притворяться активной, если vision/target stack simulated, inactive или unavailable;
- action channels должны публиковать не только наличие, но и причину недоступности;
- `motion wake source` product target должен уметь будить turret contour из `warm standby` при обнаружении движения объекта примерно до `20 m` днем или ночью.

Action-family priority note текущего этапа:

1. `strobe`
2. `water`
3. затем `audio`

Это порядок ближайшей hardware/software проработки, а не product-level иерархия важности канала.

### 7. Media, Reports And Reference Effects

Turret module должен участвовать в `Gallery` не как отдельный storage-world, а как один из source owners shared content model.

`Manual FPV` должен уметь:

- сохранять фото;
- сохранять видео;
- работать на mobile и desktop;
- поддерживать обычный и fullscreen use.

`Gallery > Media` может хранить turret-related:

- видео с камеры;
- изображения с камеры;
- записи из `Manual`;
- activation-related media entries.

Каждый media-entry должен хранить truthful source owner metadata.

`Gallery > Reports` для turret module должен получать product-significant short records, например:

- запуск `strobe` с ключевыми параметрами;
- запуск `sprayer` с длительностью и режимом;
- сохранение фото или видео из `Manual FPV`;
- срабатывания emergency/power interlock и причины блокировки.

При этом raw laboratory traces, service snapshots и engineering logs не должны автоматически засорять `Reports`; они остаются в `Laboratory` session layer.

### 8. Safety, Interlock And Recovery

Для turret-sensitive power branches источником истины считается physical emergency power interlock.

Нормативная семантика:

- `POWER ENABLED / ARMED` = emergency chain closed, питание подано;
- `POWER CUT / DISARMED` = emergency chain open, чувствительные ветви обесточены.

Baseline safety-chain должна покрывать:

- servo motion;
- `strobe`;
- ultrasonic / piezo;
- `sprayer`;
- другие active deterrence channels в этом power profile.

UI and runtime consequences:

- sensitive groups видимы, но серые при power cut;
- shell, operator HUD и `Laboratory` явно показывают interlock state;
- попытка действия возвращает понятную причину блокировки;
- в лог может идти сообщение формата `Emergency power interlock active, <function> unpowered`;
- при срабатывании во время работы runtime входит в latched emergency state до ручного возврата и явного `clear`.

Recovery behavior:

1. при тревоге система поднимает tracking/defense contour;
2. применяет доступные действия по rules/policies;
3. при потере цели ждет разумное время;
4. возвращается в `warm standby`, а не в полный cold shutdown;
5. при некорректном runtime behavior оператор всегда сохраняет аппаратный hard-stop path.

Human protection rule:

- `не стрелять в людей` является обязательным product rule уже сейчас;
- это обязательная часть policy model и settings UX, даже если техническая реализация detection/classification еще не закрыта полностью.

### 8.1 Реальные Кодовые Опоры Текущего Слоя

Чтобы `Turret` не висел отдельно от реального runtime, ниже фиксируем текущие owning files:

- `host_runtime/turret_runtime.py` - current runtime point of truth for modes, readiness, interlock и action gating;
- `host_runtime/turret_driver_layer.py` - явная driver boundary между runtime и hardware channels `motion`, `strobe`, `water`, `attack_audio` и `voice_fx`;
- `host_runtime/turret_event_log.py` - owner-side event journal для смены режима и turret actions;
- `host_runtime/turret_service_scenarios.py` - service- и laboratory-сценарии для owner-side проверок;
- `host_runtime/turret_capture_store.py` - metadata и artifact-handling для `Manual FPV` captures;
- `host_runtime/web/turret.html` - текущая owner-side product page `/turret`;
- `io_firmware/src/modules/strobe/StrobeBenchController.cpp` - инженерный contour `strobe_bench` на стороне `ESP32`;
- `host_runtime/tests/test_turret_runtime_and_scenarios.py` - tests runtime state transitions и scenario orchestration.

### 9. Acceptance Hooks

Минимальные acceptance hooks текущего этапа:

1. shell и owner page показывают модуль как `Turret`, сохраняя implementation `id` при необходимости;
2. `/turret` дает product-facing summary, а не только internal runtime flags;
3. peer-side shell сохраняет visibility модуля и truthful blocked/degraded behavior;
4. `Manual`, `Automatic` и `Laboratory` читаются как части одной модульной системы;
5. interlock state честно блокирует sensitive actions и сохраняет visible reason;
6. readiness channels `camera / range / vision / actions` не притворяются ready без truthful data;
7. product-significant turret outcomes могут появляться в shared activity/reporting layer без смешения с laboratory traces.

### 10. Нормативные Примеры И Форматы

Пример status payload:

```json
{
  "module_id": "turret_bridge",
  "display_name": "Turret",
  "state": "ready",
  "mode": "manual",
  "readiness": {
    "camera": "ready",
    "range": "attention",
    "vision": "blocked"
  },
  "interlock": {
    "state": "power_enabled",
    "latched": false
  },
  "actions": {
    "strobe": "ready",
    "water": "blocked",
    "audio": "attention"
  }
}
```

Пример product-view snapshot:

```json
{
  "product_view": {
    "overview": "ready",
    "manual_console": "available",
    "automatic_defense": "degraded",
    "service_lane": "available",
    "sensing": "attention",
    "actions": "mixed"
  },
  "target": {
    "detected": true,
    "classified": false,
    "tracking_active": true
  },
  "wake_source": "motion"
}
```

Нормативные route examples:

- product page: `/turret`
- owner-side engineering compatibility route: `/service/turret`

Нормативные settings/policy examples:

- `не стрелять в людей`
- `silent observation`
- `разрешить отпугивание животных`
- `разрешить auto-water action`
- `возврат в warm standby после потери цели`

## Open Questions

- как описать будущую модульную заменяемость turret controller без потери текущего working baseline
- где проходит окончательная граница между product-facing turret media events и deeper service/laboratory traces при следующем pass по `Gallery`

## TODO

- подключить реальные `IMX219` и `TFmini Plus` driver paths вместо полной software simulation там, где baseline уже зафиксирован;
- подтвердить real hardware bindings для `MG996R + PCA9685`, `strobe`, `SEAFLO`, `attack_audio` и `voice_fx` action families;
- довести `FPV` / media и heavy-content flow до реального owner-side сценария без разрыва между product и engineering слоями;
- синхронизировать turret service entry points с общим `Laboratory` workspace и не держать их как отдельный скрытый продуктовый слой;
- текущий software skeleton уже показывает active audio profile в `Turret` telemetry HUD и saved baseline vs local draft skeleton в `Laboratory`;
- к углублению `attack_audio / voice_fx` переходить отдельным этапом через `chat_prompts/turret_audio_prompt.md`, не смешивая этот pass с ближайшим `strobe` или общим turret cleanup;
- сохранять `HC-SR04`-class и stepper profiles только как `Laboratory`-пути, а не как product-ready turret controls;
- после следующего turret pass проверить, можно ли дальше схлопнуть retained context residue без потери useful product detail

## TBD

- будущая multi-node или detachable control схема для turret family
- будущая точная machine-vision/classification closure для policy rules и human-protection enforcement
