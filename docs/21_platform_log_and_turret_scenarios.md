# Stage 21 - Platform Log And Turret Scenarios

Этот этап поднимает более общую картину на стороне `Raspberry Pi`.

## Что сделано

- Добавлен `PlatformEventLog` как общий журнал узла.
- Turret events теперь зеркалятся в platform log.
- Добавлен каталог и runner для `turret service scenarios`.
- Общий shell `/` теперь показывает последние записи platform log.
- Страница `/turret` теперь умеет запускать dry-run сценарии.
- Добавлены первые `unittest` для runtime и сценариев.

## Какие файлы появились

- `raspberry_pi/platform_event_log.py`
- `raspberry_pi/turret_service_scenarios.py`
- `raspberry_pi/tests/test_turret_runtime_and_scenarios.py`
- `docs/21_platform_log_and_turret_scenarios.md`

## Какие файлы изменились

- `raspberry_pi/turret_event_log.py`
- `raspberry_pi/bridge_state.py`
- `raspberry_pi/server.py`
- `raspberry_pi/web/index.html`
- `raspberry_pi/web/turret.html`
- `shared_contracts/api_contracts.md`
- `docs/07_testing_strategy.md`

## Новый API

- `GET /api/v1/logs`
- `GET /api/v1/turret/scenarios`
- `POST /api/v1/turret/scenarios/run?id=...`

## Что теперь можно проверять в браузере

1. Как turret runtime пишет события в локальный журнал.
2. Как эти события попадают в общий platform log.
3. Как service/test сценарий меняет runtime без ручной цепочки кликов.
4. Как shell показывает свежую картину узла целиком, а не только модульные статусы.

## Первые сценарии

- `service_safe_idle`
- `auto_target_gate_probe`
- `emergency_recovery_probe`

Все они сейчас dry-run и не трогают реальное железо.

## Почему это важный шаг

До этого у нас уже были:

- runtime;
- event log турели;
- driver shell.

Но не было хорошей “сборки картины” на уровне всего узла. Теперь shell начинает работать ближе к реальной платформе:

- есть общий журнал;
- есть сценарии для тестировщиков;
- есть unit-тесты;
- есть место для будущего объединения логов `ESP32` и `Raspberry Pi`.

## Что дальше

- вынести platform log в двусторонний sync между узлами;
- добавить экспорт логов;
- расширить service/test сценарии и привязать их к будущим реальным binding'ам.
