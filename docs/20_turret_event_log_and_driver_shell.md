# Stage 20 - Turret Event Log And Driver Shell

Этот этап усиливает `Raspberry Pi`-сторону `Smart Platform` без привязки к конкретному железу.

## Что сделано

- Добавлен `TurretEventLog` как локальный кольцевой журнал событий.
- Добавлен `TurretDriverLayer` как каркас будущих аппаратных binding'ов.
- `TurretRuntime` теперь:
  - пишет события о смене режима, interlock'ов, флагов и подсистем;
  - отправляет runtime snapshot в driver layer;
  - получает безопасное место для будущего hardware apply.
- `BridgeState` теперь отдает:
  - runtime;
  - event log;
  - driver bindings.
- Страница `/turret` показывает:
  - режимы;
  - interlock;
  - подсистемы;
  - публикуемые модули;
  - sync-статус;
  - driver bindings;
  - журнал событий.

## Какие файлы появились

- `raspberry_pi/turret_event_log.py`
- `raspberry_pi/turret_driver_layer.py`
- `docs/20_turret_event_log_and_driver_shell.md`

## Какие файлы изменились

- `raspberry_pi/turret_runtime.py`
- `raspberry_pi/bridge_state.py`
- `raspberry_pi/server.py`
- `raspberry_pi/web/turret.html`
- `raspberry_pi/README.md`
- `shared_contracts/api_contracts.md`

## Что это дает прямо сейчас

1. Все важные переходы turret runtime начинают оставлять след.
2. Тестировщики видят не только итоговый state, но и цепочку действий.
3. Появляется честное место подключения реальных драйверов:
   - без переписывания shell;
   - без переписывания runtime;
   - без переписывания sync.

## Что пока остается заглушкой

- `TurretDriverLayer` еще не знает GPIO, SPI, I2C или serial-схемы.
- Binding'и `motion / strobe / water / audio` пока работают как `stub`.
- `vision` пока считается логическим runtime-профилем, а не реальной камерой.

## Почему это хороший этап до аппаратной карты

Сейчас можно безопасно доделывать платформу и тестовый UX:

- журналирование;
- shell;
- API;
- ownership;
- sync;
- приоритеты режимов.

А когда появится список компонентов и схемы, мы просто заменим stub-binding'и
на реальные адаптеры, не ломая уже согласованную архитектуру.

## Следующий логичный шаг

- вынести turret event log в общий log-контур платформы;
- начать service/test сценарии для turret runtime;
- затем подключать реальные hardware adapter'ы по мере готовности компонентной карты.
