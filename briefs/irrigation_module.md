# Бриф Модуля: Irrigation

## Назначение

Модуль `irrigation` отвечает за полив, датчики и связанные пользовательские сценарии.

## Владелец

- основной владелец: `ESP32`

## Что модуль обязан уметь

- показывать статус зон;
- читать датчики;
- вести малый peristaltic pump и клапанный каскад растений;
- запускать ручной полив;
- выполнять автоматические сценарии;
- поддерживать сервисный тест зон и датчиков;
- отдавать данные для turret HUD overlay, если `ESP32` доступен;
- использовать `ESP32 SD` как расширение хранения и локальную точку резервных synced-файлов;
- логировать действия и ошибки.

Важно:

- модуль `irrigation` не владеет `SEAFLO` turret water path;
- `SEAFLO` принадлежит `Raspberry Pi` и относится к turret defense/sprayer contour.

## Текущий Статус

На текущем этапе software-level контур `Irrigation v1` уже собран:

- есть продуктовая страница `/irrigation`;
- есть отдельная service/test страница `/service/irrigation`;
- есть базовый auto-mode на `ESP32`;
- есть sensor simulation как отдельный data-layer;
- есть platform-log интеграция и shell-visible service entry point.
- hardware baseline зафиксирован так:
   - малый peristaltic pump + plant valves;
   - soil / environment sensors;
   - `ESP32 SD module` как storage extension.

## Что модуль не должен делать

- брать на себя турельную логику;
- хранить в UI аппаратные детали;
- зависеть от постоянного наличия `Raspberry Pi`.

## Источник миграции

Основной донор:

- `IrrigationSystemESP32` как historical donor-repository для сценариев, UX и отдельных моделей.

Важно:

- donor-репозиторий не должен оставаться обязательной runtime-опорой текущего проекта;
- после подтвержденной выборочной миграции его можно убрать из активного workspace; текущий brief должен оставаться самодостаточным и без donor-папки.

## Следующие Задачи

1. Подключить реальные датчики и калибровку вместо полной симуляции.
2. Подключить реальный peristaltic + valve cascade и подтвердить безопасные уровни активации.
3. Добавить расписания и более богатые automatic scenarios.
4. Подготовить синхронизацию irrigation-сценариев между `ESP32` и `Raspberry Pi`.
5. Подготовить owner-visible water reserve model:
   - отдельный запас воды для drip irrigation;
   - отдельный запас воды для spraying path;
   - минимум два water-level sensor entry points:
     - один на стороне `ESP32`
     - один на стороне `Raspberry Pi`
6. Подготовить данные для manual HUD турели, если `ESP32` доступен:
   - управление каждым клапаном;
   - air temperature;
   - air humidity;
   - water reserve summary.
7. Не смешивать irrigation hardware plan с donor-слоем после подтверждения миграции знаний.
