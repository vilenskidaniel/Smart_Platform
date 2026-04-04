# Turret V1 Software Stage

Этот документ фиксирует завершение третьего пункта модульной очереди:

- `Turret v1`

Важно:

- здесь фиксируется именно software-level контур `Turret v1` на `Raspberry Pi`;
- реальная камера, FPV, дальномер и hardware-backed actuator bindings остаются следующим этапом;
- это не отменяет старые bootstrap-документы, а поднимает turret-owner
  до первого законченного продуктового состояния.

## Что Теперь Считаем Закрытым

На этом этапе `Turret` уже не считается просто bootstrap-страницей runtime.

Теперь модуль уже умеет:

- показывать product-level страницу `/turret`;
- жить как turret-owner на `Raspberry Pi`;
- отдельно держать service/test страницу `/service/turret`;
- публиковать manual/automatic/service summary, а не только внутренние флаги;
- показывать `camera` и `range` availability как часть owner-side модели;
- держать action channels `motion`, `strobe`, `water`, `audio` с safety-gates;
- писать события в `platform log` и `TurretEventLog`;
- показываться в shell как локальный product-module с owner-aware handoff на `ESP32`.

## Что Реализовано

### 1. Product Turret Page

Страница `/turret` теперь показывает:

- общий turret state;
- manual console summary;
- automatic defense summary;
- service lane state;
- `camera / range / vision` availability;
- action channels и их readiness;
- dry-run automation signals;
- последние turret events.

Это закрывает требование из UI-документа:

- думать `manual / automatic / service`, camera/range availability и actions,
  а не только набором runtime-подсистем.

### 2. Service/Test Contour

Появилась отдельная страница:

- `/service/turret`

Она дает:

- service/test сценарии;
- sensor availability toggles;
- automation flags;
- actuator probes;
- driver binding visibility;
- raw JSON и event log.

Это позволяет держать продуктовую страницу модульной и понятной,
не превращая ее в инженерную консоль.

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

Сторона `Raspberry Pi` теперь показывает user-facing title:

- `Turret`

При этом модульный `id` остается:

- `turret_bridge`

Это синхронизирует:

- shell snapshot;
- owner page;
- ESP32-side turret card;
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
- richer owner-side service exposure внутри общего `Service/Test v1`;
- живая двухузловая обкатка `ESP32 + Raspberry Pi` на реальном железе.

## Практический Итог

`Turret v1` как третий модульный software-stage можно считать завершенным.

Дальше правильнее идти не обратно в общий shell-refactor и не сразу в глубину turret hardware,
а в следующий product block:

1. `Service/Test v1`
2. затем возвращаться к cross-module integration
3. после этого переходить к live hardware qualification
