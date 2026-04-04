# Бриф Модуля: Strobe

## Назначение

Семейство `strobe` обеспечивает управление стробоскопическим каналом как частью turret-системы и как отдельным service/bench объектом.

## Два контура доступа

- `product / turret`
  - владелец: `Raspberry Pi`
  - вход через `FPV/manual` турели
  - это action-channel операторского и автоматического поведения
- `service / bench`
  - владелец: `ESP32`
  - вход через `Service/Test`
  - это лабораторная и диагностическая поверхность

Эти два контура не конкурируют между собой. Они обслуживают разные сценарии.

## Что модуль уже умеет в Service/Test

- `arm / disarm / abort`
- `pulse`
- `burst`
- safe `presets`
- live status snapshot
- command response window
- tab-based laboratory UI на `/service/strobe`
  - `Overview`
  - `Pulse`
  - `Burst`
  - `Presets`

## Что считается правильной моделью дальше

- product-level доступ к `strobe` остается в `FPV/manual`;
- инженерный доступ живет в `Service/Test`;
- подобранные сервисом параметры позже должны сохраняться как рабочий профиль;
- этот профиль потом должен применяться в:
  - `manual FPV`
  - `automatic`
  - повторных service/test сценариях

## Что модуль не должен делать

- подменять turret owner-side логику;
- обходить interlock-правила платформы;
- становиться просто россыпью прямых GPIO-команд без контекста статуса и блокировок;
- смешивать продуктовый HUD с deep service-диагностикой.

## Ближайшие задачи

1. Зафиксировать profile/preset persistence contract для `strobe`.
2. Довести laboratory slice до более полной инженерной панели с логами и отчетами.
3. Подготовить понятный мост между `strobe_bench` и будущим turret product-layer поведением.
