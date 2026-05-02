# Бриф Модуля: Turret Bridge

## Назначение

`Turret Bridge` — это модуль-владелец для турели на стороне `Raspberry Pi`.

В реализации модульный `id` остается `turret_bridge`, но user-facing продуктовый блок
в shell и на владельце должен называться просто `Turret`.

Он связывает:

- камеру;
- машинное зрение;
- наведение;
- актуаторы;
- реакции турели;
- исполнительные устройства вроде стробоскопа, воды и звука.

## Владелец

- основной владелец: `Raspberry Pi`

## Что модуль обязан уметь

- сообщать свою доступность;
- открывать и закрывать турельные функции в UI;
- вызывать исполнительные модули через контракт;
- публиковать статус турели;
- передавать причины блокировки;
- работать в ручном, автоматическом и сервисном режимах.

## Текущий Статус

На текущем этапе software-level контур `Turret v1` уже собран:

- есть продуктовая страница `/turret`;
- есть отдельная service/test страница `/service/turret`;
- есть product-level snapshot для `manual`, `automatic` и `service`;
- есть simulated `camera` / `range` availability как часть runtime-модели;
- есть action channels `motion`, `strobe`, `water`, `audio` с safety-gates;
- есть `platform log`, `TurretEventLog` и `TurretDriverLayer`.

Подтвержденный hardware baseline этого шага:

- primary camera:
  - `IMX219 130°`
- range:
  - `TFmini Plus` как owner-side профиль
  - `HC-SR04`-class как laboratory-профиль после закупки
- motion:
  - `MG996R`
  - `PCA9685`
- turret water:
  - `SEAFLO 12V`
- stepper-моторы:
  - только `Laboratory`, не turret motion
- audio stock baseline:
  - `ultrasonic_pair = 2`
  - `horn_pair = 2`
  - `Soundcore Motion 300` в наличии
- `strobe` остается частью turret defense-line `v1`, а не отдельным поздним профилем.

## Уточненный Product Context

Для следующего этапа turret нужно мыслить уже не только как runtime-owner,
а как hybrid product module:

- `manual FPV`
- `automatic policy mode`
- `service/test laboratory`
- `warm standby`
- future-ready machine vision and classification

Главная сводка нового контекста вынесена отдельно:

- [37_turret_product_context_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/37_turret_product_context_map.md)

Дополнительная фиксация по action layers:

- `strobe` должен быть доступен в двух разных контурах:
  - как turret action в `manual FPV`
  - как отдельный laboratory slice в `Laboratory`
- `audio` сейчас не углубляется вместе со `strobe`;
- для `audio` сначала нужен отдельный briefing по hardware, mounting и power:
  - [38_turret_audio_briefing.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/38_turret_audio_briefing.md)

## Что модуль не должен делать

- отдавать прямой контроль турели `ESP32`;
- позволять обходить владельца через чужой UI;
- смешивать логику машинного зрения с браузерными страницами.

## Источник миграции

Основной донор:

- ТЗ и будущая логика `Raspberry Pi`

Частичный референс:

- `TurretManager.cpp` из `IrrigationSystemESP32` только как historical UX/reference stub.

Важно:

- этот donor-file не должен оставаться обязательной опорой для нового turret-owner контракта;
- после переноса нужных UX-наблюдений donor-layer можно убрать из активного workspace; сам brief не должен зависеть от наличия donor-папки.

## Следующие Задачи

1. Подключить реальные `IMX219` / `TFmini Plus` driver'ы вместо полной software simulation.
2. Подтвердить real hardware bindings для `MG996R + PCA9685`, `strobe`, `SEAFLO` и `audio`.
3. Довести FPV/media и heavy content flow до реального owner-side сценария.
4. Углубить `strobe` как ближайший service/test и FPV-facing action slice.
5. После этого синхронизировать turret service entry points с общим `Laboratory` workspace.
6. К `audio` переходить отдельным этапом после hardware/power briefing.
7. Вести `HC-SR04`-class и stepper profiles только как laboratory-пути, не как product-ready turret controls.
