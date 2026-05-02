# Stage 18 - Raspberry Pi Turret Bridge Bootstrap

Статус документа:

- archived historical snapshot;
- больше не входит в активный reading order;
- использовать только как след раннего turret-owner bootstrap-stage, а не как active product truth.

Исходный активный путь раньше был `docs/18_rpi_turret_bridge_bootstrap.md`.

## Historical Snapshot

Статус документа:

- stage-doc и bootstrap snapshot, а не primary product truth;
- читать после `docs/README.md`, `26_v1_product_spec.md`, `05_ui_shell_and_navigation.md`, `27_platform_shell_v1_spec.md` и `37_turret_product_context_map.md`;
- если описание turret-side shell или vocabulary расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ сохраняем как короткий historical snapshot первого живого owner-side shell на `Raspberry Pi`.

## Какой historical delta здесь остается

- на `Raspberry Pi` впервые поднят локальный browser-shell на `Python stdlib` с маршрутами `/` и `/turret`;
- появились первые owner-side runtime surfaces для `turret_bridge` и `strobe`;
- появился фоновый sync-клиент, который:
  - отправлял heartbeat в `ESP32`;
  - публиковал состояние `turret_bridge` и `strobe`;
  - читал peer snapshot и начинал зеркалить peer modules;
- в этом же этапе сложился первый набор ключевых файлов стороны `Raspberry Pi`:
  - `app.py`
  - `bridge_config.py`
  - `bridge_state.py`
  - `server.py`
  - `sync_client.py`
  - `web/index.html`
  - `web/turret.html`

## Что этот этап реально доказал

1. `Raspberry Pi` может жить в той же shell-модели, что и `ESP32`, не ломая ownership.
2. Двусторонний sync-контракт можно было проверять до появления реальной камеры, vision и драйверов.
3. `Python stdlib` оказался достаточным для первого owner-side bootstrap, даже если не является конечным архитектурным выбором.

## Что уже не нужно брать отсюда как канон

- выбор `Python stdlib` как продуктовую норму;
- ручную имитацию turret runtime как целевую модель owner-side страницы;
- локальный список маршрутов и bootstrap-ограничений как актуальный product spec.

## Зачем файл сохраняем

Как след первого момента, когда `Raspberry Pi` стал живым turret-owner узлом с локальным shell, `/turret` и двусторонним sync bridge.
