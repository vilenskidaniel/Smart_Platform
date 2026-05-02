# Irrigation V1 Software Stage

Этот документ фиксирует завершение второго пункта модульной очереди:

Статус документа:

- stage-doc и implementation snapshot, а не primary product truth;
- читать после `docs/README.md`, `26_v1_product_spec.md`, `05_ui_shell_and_navigation.md` и актуальных irrigation-related supporting docs;
- если описание расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

- `Irrigation v1`

Важно:

- здесь фиксируется именно software-level контур `Irrigation v1` на owner-side `I/O` node today-baseline `ESP32`;
- реальный hardware path, калибровка датчиков и live water qualification остаются следующим этапом;
- это не отменяет старый bootstrap-документ, а поднимает модуль до первого законченного продуктового состояния.

Дополнительно:

- продуктовая роль `Irrigation`, shell semantics, границы `Laboratory` и общая owner-aware модель уже закреплены в канонических документах;
- этот stage-doc фиксирует только implementation-delta, который материализовал эту модель в текущем software baseline.

## Какой Implementation-Delta Фиксируем На Этом Этапе

На этом этапе в software baseline зафиксированы такие практические сдвиги:

- route `/irrigation`, module registry и shell snapshot уже материализуют утвержденную product-role `Irrigation`;
- owner-side controller мыслит зонами, датчиками и состояниями, а не только насосом и клапанами;
- owner-side irrigation engineering slice встроен в общий `Laboratory` и больше не требует отдельной product IA;
- базовый automatic flow и manual/service actions уже работают в одной truthful owner-model;
- события irrigation-path начинают попадать в общий platform-level activity слой.

## Что Реализовано

### 1. Implementation Surface `/irrigation`

Страница `/irrigation` теперь показывает:

- статус модуля;
- environment summary;
- зоны;
- sensor fault visibility;
- active run source;
- переключение базового auto-mode;
- локальный irrigation log.

### 2. Laboratory Contour

Появился owner-side irrigation engineering contour внутри общего `Laboratory` workspace.

Current software-stage compatibility surface может все еще использовать отдельный route:

- `/service/irrigation`

Она дает:

- вход в irrigation-oriented engineering controls через `Laboratory`;
- service pulse по зоне;
- sensor profiles:
  - `dry`
  - `wet`
  - `fault`
  - `restore`

На implementation-уровне это отделяет owner-side инженерные controls от продуктовой страницы, не превращая `/irrigation` в инженерный backend.

Важно:

- целевая модель для следующих документов и следующих чатов — не отдельная user-facing service-page, а irrigation-oriented карточка или срез внутри общего `Laboratory`;
- compatibility route допустим как переходный implementation-layer, но не как главная продуктовая структура.

### 3. Sensor And Environment Layer

Внутри `IrrigationController` теперь есть отдельные данные для:

- состояния soil sensor по каждой зоне;
- simulated environment snapshot;
- sensor fault flags;
- auto eligibility по зонам.

Это важный сдвиг:

- UI больше не держит sensor logic внутри себя;
- controller уже мыслит зонами и датчиками как отдельными сущностями.

### 4. Automatic Baseline

Добавлен первый безопасный automatic baseline:

- `ESP32` может перевести irrigation в `automatic`;
- auto-mode выбирает самую сухую eligible zone;
- `Laboratory` блокирует запуск automatic сценария;
- manual и service actions остаются видимыми и предсказуемыми.

Это не финальный scheduler, но уже честный `Automatic Mode` для `Irrigation v1`.

### 5. Shell And Registry Integration

Сторона owner-side `I/O` node today-baseline `ESP32` теперь держит:

- `irrigation` как product module;
- irrigation-oriented engineering surface как owner-side `Laboratory` slice.

Это отражается:

- в module registry;
- в shell snapshot;
- в owner-aware semantics общего `Laboratory`;
- в owner-aware federated shell на `Raspberry Pi`.

## Что Проверено

Проверки этого этапа:

1. `py -3 -m unittest discover -s tests` в `Smart_Platform/raspberry_pi`
   - результат: `12 tests`, `OK`
2. `pio run` в `Smart_Platform/firmware_esp32`
   - результат: `SUCCESS`
3. `pio run -t buildfs` в `Smart_Platform/firmware_esp32`
   - результат: `SUCCESS`

Память после сборки `ESP32`:

- RAM: `73456 / 327680` (`22.4%`)
- Flash: `936421 / 1310720` (`71.4%`)

## Что Еще Не Закрыто

Это остается следующими этапами, а не долгом текущего software-stage:

- реальные irrigation outputs;
- подтвержденные драйверы насоса и клапанов;
- live soil sensors и калибровка;
- hardware qualification `irrigation_water_path`;
- расписания и более сложные automatic scenarios;
- sync user scenarios между `ESP32` и `Raspberry Pi`.

## Практический Итог

Этот документ можно считать implementation snapshot того момента, когда `Irrigation v1` впервые получил связный software baseline поверх owner-aware shell, `Laboratory` и platform activity layer.
