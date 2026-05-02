# ESP32 Shell Bootstrap

Статус документа:

- archived historical snapshot;
- больше не входит в активный reading order;
- использовать только как след раннего bootstrap-stage, а не как active product truth.

Исходный активный путь раньше был `docs/12_esp32_shell_bootstrap.md`.

## Historical Snapshot

Статус документа:

- stage-doc и bootstrap snapshot, а не primary product truth;
- читать после `docs/README.md`, `26_v1_product_spec.md`, `05_ui_shell_and_navigation.md` и `27_platform_shell_v1_spec.md`;
- если описание shell vocabulary расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ сохраняем как короткий historical snapshot первого живого shell-bootstrap на стороне `ESP32`.

## Какой historical delta здесь остается

- на `ESP32` впервые поднят browser-shell, доступный по `Wi-Fi` без внешнего роутера и без USB-сценария;
- shell уже читал данные из `System Core` и отдавал базовые поверхности:
  - `/`
  - `/api/v1/system`
  - `/api/v1/modules`
  - `/api/v1/diagnostics`
- на этой стадии впервые материализована честная blocked-модель для peer-owned turret-family:
  - `turret_bridge` и `strobe` оставались видимыми;
  - причина блокировки фиксировалась как `owner_unavailable`.

## Что этот этап реально доказал

1. `ESP32` способен быть первой browser-first точкой входа платформы.
2. Модель видимых, но заблокированных peer-owned модулей работает еще до зрелого federated handoff.
3. Shell bootstrap можно было развивать раньше, чем завершились sync, `LittleFS` layout и unified `Laboratory` workspace.

## Что уже не нужно брать отсюда как канон

- историческую верхнеуровневую страницу `Diagnostics`;
- shell, встроенный в прошивку, как окончательную архитектурную форму;
- старый список следующих шагов как актуальный roadmap.

## Зачем файл сохраняем

Как след первого момента, когда `ESP32` стал реальной shell-entry surface и начал честно показывать locked peer-owned turret modules.
