# System Core Contract

Этот документ фиксирует внутренний системный контракт платформы.

Важно:

- он описывает внутренние состояния, ownership и системные поля;
- он не заменяет продуктовую модель `v1`;
- для верхнего уровня сначала читать [26_v1_product_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/26_v1_product_spec.md).

Этот контракт нужен, чтобы все слои платформы одинаково называли:

- режимы;
- состояния модулей;
- причины блокировки;
- базовые поля состояния узла.

## Active Mode

Допустимые значения:

- `manual`
- `automatic`
- `service_test`
- `fault`
- `emergency`

## Module State

Допустимые значения:

- `online`
- `degraded`
- `locked`
- `fault`
- `service`
- `offline`

## Block Reason

Допустимые значения:

- `none`
- `owner_unavailable`
- `peer_sync_pending`
- `safety_interlock`
- `module_fault`
- `service_session_active`
- `service_mode_required`
- `emergency_state`
- `module_offline`
- `unknown`

## Node Type

Допустимые значения:

- `unknown`
- `esp32`
- `raspberry_pi`

## Local Node Health

Минимальный пример:

```json
{
  "node_id": "esp32-main",
  "shell_base_url": "http://192.168.4.1",
  "node_type": "esp32",
  "is_local": true,
  "reachable": true,
  "shell_ready": true,
  "wifi_ready": false,
  "sync_ready": true,
  "reported_mode": "manual",
  "uptime_ms": 1234
}
```

## Peer Node Health

Минимальный пример:

```json
{
  "node_id": "rpi-turret",
  "shell_base_url": "http://raspberrypi.local:8080",
  "node_type": "raspberry_pi",
  "is_local": false,
  "reachable": false,
  "shell_ready": false,
  "wifi_ready": false,
  "sync_ready": false,
  "reported_mode": "manual",
  "last_seen_ms": 0
}
```

## Federated Module Routing Fields

Каждый module snapshot в `v1` должен уметь описывать owner-aware shell routing.

Минимальный пример:

```json
{
  "id": "strobe",
  "owner": "rpi",
  "owner_node_id": "rpi-turret",
  "owner_available": true,
  "canonical_path": "/turret#strobe",
  "canonical_url": "http://raspberrypi.local:8080/turret#strobe",
  "federated_access": "peer_owner_available"
}
```

Допустимые значения `federated_access` в текущем bootstrap:

- `local_owner`
- `shared_local`
- `peer_owner_available`
- `peer_owner_missing`

## Правило совместимости

Если UI или синхронизация встречают неизвестное значение:

- нельзя молча считать его `online`;
- нужно переводить объект в безопасное поведение;
- в лог должен попадать `unknown` или совместимая причина.
