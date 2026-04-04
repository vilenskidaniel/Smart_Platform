# Бриф Модуля: Irrigation

## Назначение

Модуль `irrigation` отвечает за полив, датчики и связанные пользовательские сценарии.

## Владелец

- основной владелец: `ESP32`

## Что модуль обязан уметь

- показывать статус зон;
- читать датчики;
- запускать ручной полив;
- выполнять автоматические сценарии;
- поддерживать сервисный тест зон и датчиков;
- логировать действия и ошибки.

## Текущий Статус

На текущем этапе software-level контур `Irrigation v1` уже собран:

- есть продуктовая страница `/irrigation`;
- есть отдельная service/test страница `/service/irrigation`;
- есть базовый auto-mode на `ESP32`;
- есть sensor simulation как отдельный data-layer;
- есть platform-log интеграция и shell-visible service entry point.

## Что модуль не должен делать

- брать на себя турельную логику;
- хранить в UI аппаратные детали;
- зависеть от постоянного наличия `Raspberry Pi`.

## Источник миграции

Основной донор:

- [IrrigationSystemESP32](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/IrrigationSystemESP32)

## Следующие Задачи

1. Подключить реальные датчики и калибровку вместо полной симуляции.
2. Подтвердить аппаратный water-path и безопасные уровни активации.
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
