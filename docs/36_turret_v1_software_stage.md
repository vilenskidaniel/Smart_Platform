# Turret V1 Software Stage

Этот документ фиксирует завершение третьего пункта модульной очереди:

- `Turret v1`

Статус документа:

- stage-doc и implementation snapshot, а не primary product truth;
- читать после `docs/README.md`, `26_v1_product_spec.md`, `05_ui_shell_and_navigation.md`, `37_turret_product_context_map.md` и `39_design_decisions_and_screen_map.md`;
- если описание расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Важно:

- здесь фиксируется именно software-level контур `Turret v1` на turret compute node today-baseline `Raspberry Pi`;
- реальная камера, FPV, дальномер и hardware-backed actuator bindings остаются следующим этапом;
- это не отменяет старые bootstrap-документы, а поднимает turret-owner
  до первого законченного продуктового состояния.

Дополнительно:

- продуктовая роль `Turret`, operator UX, owner-aware shell semantics и границы `Laboratory` уже закреплены в канонических документах;
- этот stage-doc фиксирует только implementation-delta, который впервые материализовал эту модель в текущем software baseline.

## Какой Implementation-Delta Фиксируем На Этом Этапе

На этом этапе в software baseline зафиксированы такие практические сдвиги:

- route `/turret`, shell snapshot и owner-page title уже материализуют утвержденную product-role `Turret`;
- turret runtime отдает product-facing summaries вместо набора только внутренних runtime-флагов;
- owner-side turret engineering slice встроен в общий `Laboratory`, а не живет как отдельная product IA;
- readiness по `camera`, `range`, `vision` и action families уже участвует в честной owner-side модели;
- turret события начинают формировать platform-level и turret-specific activity layer, пригодный для shell и дальнейшего UX.

## Что Реализовано

### 1. Implementation Surface `/turret`

Страница `/turret` теперь показывает:

- общий turret state;
- manual console summary;
- automatic defense summary;
- engineering lane state;
- `camera / range / vision` availability;
- action channels и их readiness;
- dry-run automation signals;
- последние turret events.

На implementation-уровне это переводит turret-owner page из runtime-centric поверхности в product-facing summary surface.

### 2. Laboratory Contour

Появился owner-side turret engineering contour внутри общего `Laboratory` workspace.

Current software-stage compatibility surface может все еще использовать отдельный route:

- `/service/turret`

Она дает:

- engineering-сценарии;
- sensor availability toggles;
- automation flags;
- actuator probes;
- driver binding visibility;
- raw JSON и event log.

Это позволяет держать продуктовую страницу модульной и понятной,
не превращая ее в инженерную консоль.

Важно:

- целевая продуктовая модель — turret-oriented owner-side срез внутри `Laboratory`, а не отдельная user-facing service-page;
- compatibility route допустим как переходный implementation-layer, но не как главный способ мыслить структуру продукта.

### 3. Turret Product Snapshot

`TurretRuntime` теперь отдает не только список подсистем, но и `product_view`:

- `overview`
- `manual_console`
- `automatic_defense`
- `service_lane`
- `engagement`
- `sensing`
- `actions`

Это важный сдвиг:

- turret-owner уже мыслит пользовательскими состояниями;
- shell и owner page получают одну понятную точку правды;
- мы больше не завязаны только на внутренние флаги вида `automation_ready`.

### 4. Camera And Range Availability

В software-level модели появились:

- `camera`
- `range`
- `vision`

Пока это simulated availability channels, но они уже участвуют в:

- `automatic` gate logic;
- `target_locked` validation;
- product-level UI;
- turret module degradation rules.

### 5. Shell And Registry Integration

Сторона turret compute node today-baseline `Raspberry Pi` теперь показывает user-facing title:

- `Turret`

При этом модульный `id` остается:

- `turret_bridge`

Это синхронизирует:

- shell snapshot;
- owner page;
- `I/O`-side turret card;
- product wording в документации.

## Что Проверено

Проверки этого этапа:

1. `py -3 -m unittest discover -s tests` в `Smart_Platform/raspberry_pi`
   - результат: `14 tests`, `OK`
2. `pio run` в `Smart_Platform/firmware_esp32`
   - результат: `SUCCESS`
3. `pio run -t buildfs` в `Smart_Platform/firmware_esp32`
   - результат: `SUCCESS`

Память после сборки `ESP32`:

- RAM: `73456 / 327680` (`22.4%`)
- Flash: `936541 / 1310720` (`71.5%`)

## Что Еще Не Закрыто

Это остается следующими этапами, а не долгом текущего software-stage:

- real camera and FPV pipeline;
- real range sensor integration;
- real `motion / strobe / water / audio` driver bindings;
- hardware qualification turret IO path;
- richer owner-side engineering exposure внутри общего `Laboratory`;
- живая двухузловая обкатка `ESP32 + Raspberry Pi` на реальном железе.

## Практический Итог

Этот документ можно считать implementation snapshot того момента, когда `Turret v1` впервые получил связный owner-aware software baseline с product-facing summaries, engineering slice внутри `Laboratory` и platform-level activity layer.
