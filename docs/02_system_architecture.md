# System Architecture

Этот документ описывает архитектуру платформы простым способом:

1. продуктовый уровень;
2. platform services;
3. внутренние технические слои.

Главное правило:

- не путать эти уровни между собой.
- аппаратную правду по наличию и закупкам держать в `docs/smart_platform_workshop_inventory.xlsx`.

## 1. Продуктовый уровень

Для пользователя и для верхнего roadmap платформа состоит из пяти блоков:

1. `Platform Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

Важно:

- `Laboratory` — user-facing имя;
- внутреннее stage-name `Laboratory` можно сохранять в roadmap и технических brief-файлах.
- `Diagnostics` и `Test Bench` считаем alias-именами того же инженерного контура;
- `Gallery` — shared virtual section shell, а не модуль одного owner.

## 2. Platform Services

Эти части не являются самостоятельными продуктами, но нужны всем блокам:

- `sync`
- `logs`
- `settings`
- `diagnostics`
- `auth groundwork`
- `storage/export`

Они должны поддерживать продуктовые блоки, а не разрастаться в отдельные мини-продукты.

## 3. Внутренние технические слои

Ниже живут слои реализации:

- runtime state machines;
- driver bindings;
- sensor profiles;
- water paths;
- hardware profiles;
- transport adapters;
- filesystems and data stores.

Это инженерные слои. Их не нужно поднимать на верхний уровень навигации и roadmap как равноправные пользовательские модули.

## 4. Владение модулями

### `ESP32`

Локальная зона `ESP32`:

- `Irrigation`
- локальные датчики среды и почвы;
- peristaltic irrigation path и клапанный каскад;
- SD storage как расширение памяти и приемник резервных turret-sync копий;
- часть service/power диагностики;
- fallback shell;
- `strobe_bench` как bench/service профиль;
- always-on sentinel;
- диспетчер пробуждения peer-узла.

### `Raspberry Pi`

Локальная зона `Raspberry Pi`:

- `Turret`
- primary camera `IMX219 130°`;
- range sensing с `TFmini Plus` как owner-side профилем и `HC-SR04`-class как laboratory-профилем;
- combat `strobe`;
- turret motion `MG996R` через `PCA9685` baseline;
- turret water `SEAFLO 12V`;
- audio;
- vision and targeting;
- live media ownership.

### Shared Virtual Sections

- `Gallery` не имеет одного owner на уровне shell-page;
- explorer-страница строится как shared section;
- каждый файл, отчет или media entry при этом хранит origin/storage owner и может деградировать по доступности источника.

## 5. Энергетический контур

Архитектура должна учитывать не только ownership, но и стоимость пробуждения по энергии.

Базовая модель:

1. `ESP32` слушает дешевые события и расписания.
2. `ESP32` локально решает все, что не требует turret-owner.
3. Если нужен точный анализ или turret-action, `ESP32` будит `Raspberry Pi`.
4. После этого `Raspberry Pi` берет на себя только turret-family задачи.

Для `Raspberry Pi` в turret-контуре базовой считаем модель:

- `warm standby`

Подтвержденный power baseline текущего шага:

- лабораторный bring-up ведем от `NICE-POWER dual 30V 10A`;
- автономную силовую шину строим вокруг `LiFePO4 12V 100Ah with BMS`.

## 6. Federated Shell

В первой версии используется не global master switch, а federated shell:

- каждый узел поднимает свой shell;
- shell на обоих узлах выглядит одинаково;
- shell показывает все известные продуктовые блоки;
- каждая команда уходит владельцу соответствующего модуля;
- если владелец недоступен, модуль не скрывается, а уходит в `locked` или `degraded`;
- недоступные модули остаются видимыми и кликабельными, с объяснением.
- `Gallery` может открываться даже при наличии только одного узла и показывать локальный slice без притворства, что peer-content доступен.

## 7. Состояния модулей

Для всех продуктовых блоков используем единый набор состояний:

- `online`
- `degraded`
- `locked`
- `fault`
- `service`
- `offline`

## 8. Правило исполнения команд

Запрещенный путь:

- UI напрямую дергает GPIO;
- UI сам решает, можно ли выполнять опасную команду;
- UI хранит critical business logic.

Правильный путь:

1. UI отправляет команду модулю.
2. Модуль-владелец проверяет права, режим, interlock и safety.
3. Модуль либо исполняет команду, либо возвращает блокировку.
4. Система логирует результат.

## 9. Потеря узла

### Если пропал `Raspberry Pi`

- `Turret` остается видимым;
- элементы управления турелью блокируются;
- `ESP32` продолжает локально вести полив и service-функции;
- `strobe_bench` может оставаться доступным как отдельный bench/service профиль.

### Если пропал `ESP32`

- `Turret` продолжает жить на `Raspberry Pi`;
- `Irrigation` уходит в `degraded` или `locked`;
- shell явно показывает, что irrigation-owner недоступен.

## 10. Почему это лучше старой модели

Эта архитектура лучше идеи “один узел забирает все”, потому что:

- не ломает автономность полива;
- не заставляет `ESP32` притворяться хозяином turret-железа;
- не делает `Raspberry Pi` обязательным для всего продукта;
- лучше соответствует старому ТЗ и новому product-shell подходу.

## 11. Product Target vs Software Baseline

На архитектурном уровне тоже нужно различать:

- `product target`
- `software baseline`

Это нужно, чтобы не путать:

- обязательную архитектурную модель;
- уже собранную и проверенную software-level реализацию.

## 12. Что дальше

Следующий уровень детализации должен идти не в глубину слоев, а в продуктовые блоки:

1. `Platform Shell v1`
2. `Irrigation v1`
3. `Turret v1`
4. `Gallery v1`
5. `Laboratory v1`
