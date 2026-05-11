# io_firmware

Здесь живет новая прошивка `ESP32` для `Smart Platform`.

На текущем этапе это уже не пустой skeleton, а рабочий platform foundation
для локального shell, `Irrigation`, `Service/Test` и sync bootstrap.

## Что Уже Есть

- `SystemCore` и `ModuleRegistry`;
- `WebShellServer`;
- `ShellSnapshotFacade`;
- `WiFiBootstrap` с локальным shell по `SoftAP`;
- `StorageManager` и content status;
- entry-context layer в верхней bar-строке для `ESP32 shell`, launch client, topology, input profile и layout helper;
- `IrrigationController` как software-level `Irrigation v1` модуль;
- product page `/irrigation` и service page `/service/irrigation`;
- базовый irrigation auto-mode и sensor simulation;
- `StrobeBenchController` как локальный `Service/Test` модуль;
- logical direct route `/turret` теперь должен идти через owner-aware handoff вместо сырого `404`;
- базовые sync endpoints для связи с `Raspberry Pi`.

## Что Пока Еще Не Завершено

- полностью завершенный продуктовый `System Shell v1`;
- реальные irrigation outputs, live sensors и hardware qualification water-path;
- полная двухузловая живая интеграция;
- финальная production-очистка shell-ролей и presenters.

## Как Собирать

Работать и собирать эту прошивку нужно из этого каталога:

- `Smart_Platform/io_firmware/`

Основные команды:

```powershell
pio run
pio run -t buildfs
```

Важно:

- для новой платформенной разработки использовать именно этот `platformio.ini`;
- верхний `platformio.ini` в корне репозитория относится к старому bench-слою
  и не должен быть основной точкой входа для `Smart Platform`.

## Что Важно Помнить

- `ESP32` не должна брать на себя активное turret-owner управление;
- турельные разделы на `ESP32` должны оставаться видимыми, но честно блокироваться при отсутствии `Raspberry Pi`;
- код здесь должен оставаться модульным, а не возвращаться в один большой `main.cpp`.

`TODO(stage-firmware-bootstrap)`
