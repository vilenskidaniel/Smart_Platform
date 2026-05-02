# Stage 19 - Raspberry Pi Turret Runtime

Этот этап описывает bootstrap-этап turret runtime на стороне `Raspberry Pi`.

Важно:

- это исторический runtime-bootstrap документ;
- он не является главным источником истины по текущему product UX;
- software-level фиксация `Turret v1` вынесена в [36_turret_v1_software_stage.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/36_turret_v1_software_stage.md);
- актуальная продуктовая картина turret UX вынесена в:
  - [37_turret_product_context_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/37_turret_product_context_map.md)
  - [39_design_decisions_and_screen_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/39_design_decisions_and_screen_map.md)

## Что было сделано на этом этапе

- добавлен слой `turret_runtime.py`;
- появились подсистемы:
  - `motion`
  - `strobe`
  - `water`
  - `audio`
  - `vision`
- появились runtime-флаги:
  - `automation_ready`
  - `target_locked`
  - `vision_tracking`
- появились interlock-команды:
  - `fault`
  - `emergency`
  - `clear`
- `BridgeState` перестал хранить turret-состояние как случайный набор флагов;
- состояния `turret_bridge` и `strobe` начали вычисляться из runtime;
- страница `/turret` была переведена на runtime API.

## Какие файлы менялись

- `raspberry_pi/turret_runtime.py`
- `raspberry_pi/bridge_state.py`
- `raspberry_pi/server.py`
- `raspberry_pi/web/turret.html`
- `raspberry_pi/README.md`
- `shared_contracts/api_contracts.md`

## Новый API

- `GET /api/v1/turret/status`
- `GET /api/v1/turret/runtime`
- `POST /api/v1/turret/runtime/mode?value=...`
- `POST /api/v1/turret/runtime/subsystem?id=...&enabled=...`
- `POST /api/v1/turret/runtime/flag?name=...&value=...`
- `POST /api/v1/turret/runtime/interlock?value=...`

## Что тогда можно было проверять

1. Переходы между `manual`, `automatic`, `laboratory`.
2. Латч `fault` и `emergency`.
3. Сброс interlock и возврат в безопасный `manual`.
4. Блокировку чувствительных действий при небезопасных runtime-условиях.
5. Блокировку `strobe / water / audio`, если цель не захвачена.
6. Публикацию вычисленных модульных состояний в `ESP32`.

## Важное обновление контекста

Старое bootstrap-предположение вида:

- `automatic` блокируется, если он “не armed”

больше не считаем источником истины.

Новая продуктовая модель такая:

- turret-sensitive группы контролируются физическим arm/disarm interlock на корпусе;
- UI только отображает это состояние и уважает аппаратную блокировку;
- `Manual` и `Automatic` дальше описываются product-level документами, а не этим bootstrap-stage файлом.

## Почему этот этап был лучше предыдущего bootstrap

Раньше turret-page просто дергала состояния модулей напрямую.

Это:

- не отражало ownership-модель;
- плохо расширялось;
- плохо подходило для будущих vision и actuator drivers.

После этого этапа появилась единая runtime-точка правды, из которой строятся:

- shell;
- sync payload;
- JSON snapshot;
- будущие turret-drivers.

## Что на этом этапе оставалось заглушкой

- реальной камеры еще не было;
- vision пока был только логическим флагом;
- реального движения турели не было;
- `strobe / water / audio` еще не были привязаны к живым драйверам;
- event log turret runtime еще не был вынесен отдельно.

`TODO(stage-rpi-real-turret-devices)`

## Как правильно читать этот документ теперь

Этот файл нужно читать как:

- исторический bootstrap-runtime этап;
- технический мост к более поздним turret-документам;
- не как финальное описание пользовательского `Turret v1`.
