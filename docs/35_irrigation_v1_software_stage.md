# Irrigation V1 Software Stage

Этот документ фиксирует завершение второго пункта модульной очереди:

- `Irrigation v1`

Важно:

- здесь фиксируется именно software-level контур `Irrigation v1` на `ESP32`;
- реальный hardware path, калибровка датчиков и live water qualification остаются следующим этапом;
- это не отменяет старый bootstrap-документ, а поднимает модуль до первого законченного продуктового состояния.

## Что Теперь Считаем Закрытым

На этом этапе `Irrigation` уже не считается просто "первым dry-run модулем".

Теперь модуль уже умеет:

- показывать product-level страницу `/irrigation`;
- жить как irrigation-owner на `ESP32`;
- работать с зонами, датчиками и состояниями, а не только с насосом и клапанами;
- запускать ручной полив;
- выполнять базовый automatic baseline;
- иметь отдельную service/test страницу `/service/irrigation`;
- проводить сервисную проверку зон и датчиков;
- писать события в общий `platform log`;
- показываться в shell как локальный product-module и как отдельный service entry point.

## Что Реализовано

### 1. Product Irrigation Page

Страница `/irrigation` теперь показывает:

- статус модуля;
- environment summary;
- зоны;
- sensor fault visibility;
- active run source;
- переключение базового auto-mode;
- локальный irrigation log.

### 2. Laboratory Contour

Появилась отдельная страница:

- `/service/irrigation`

Она дает:

- вход и выход из `Laboratory`;
- service pulse по зоне;
- sensor profiles:
  - `dry`
  - `wet`
  - `fault`
  - `restore`

Это закрывает требование "сервисная проверка зон и датчиков" без превращения продуктовой страницы в инженерный backend.

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

Сторона `ESP32` теперь держит:

- `irrigation` как product module;
- `irrigation_service` как отдельный `Laboratory` module.

Это отражается:

- в module registry;
- в shell snapshot;
- в service section общего shell;
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

`Irrigation v1` как второй модульный software-stage можно считать завершенным.

Дальше правильнее идти не обратно в большой shell-refactor и не сразу в hardware detail,
а в следующий product block:

1. `Turret v1`
2. затем `Laboratory` как отдельный блок общего уровня
3. после этого возвращаться к cross-module integration и hardware qualification
