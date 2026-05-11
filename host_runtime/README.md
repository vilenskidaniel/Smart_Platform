# host_runtime

Здесь живет логика `Raspberry Pi` для `Smart Platform`.

На текущем этапе это уже не только shell и turret runtime bootstrap,
а software-level `Turret v1` с отдельными product/service страницами и двумя новыми слоями:

- `TurretEventLog` для локального журнала событий;
- `TurretDriverLayer` для будущих аппаратных binding'ов.

## Что уже есть

- локальный shell `/`;
- turret-страница `/turret`;
- отдельная service/test страница `/service/turret`;
- runtime-подсистемы:
  - `motion`
  - `strobe`
  - `water`
  - `audio`
  - `camera`
  - `range`
  - `vision`
- product-level snapshot с:
  - `manual console`
  - `automatic defense`
  - `service lane`
  - `camera/range availability`
  - `action readiness`
- фоновые heartbeat и push состояния в `ESP32`;
- флаги:
  - `automation_ready`
  - `target_locked`
  - `vision_tracking`
- interlock-команды:
  - `fault`
  - `emergency`
  - `clear`
- локальный журнал событий turret-runtime;
- заглушечный слой будущих драйверов.

## Чего пока нет

- реальной камеры;
- реального дальномерного канала;
- машинного зрения;
- баллистики и наведения;
- реальных драйверов исполнительных устройств турели;
- полного merge логов и настроек между узлами.

## Как запустить

Поддерживаемые entry paths:

1. owner-side запуск из каталога `host_runtime`:

```bash
python3 app.py
```

1. local laptop smoke из корня репозитория с честно отключенным sync:

```powershell
$env:SMART_PLATFORM_RPI_HOST = "127.0.0.1"
$env:SMART_PLATFORM_RPI_PORT = "8091"
$env:SMART_PLATFORM_RPI_PUBLIC_BASE_URL = "http://127.0.0.1:8091"
$env:SMART_PLATFORM_SYNC_ENABLED = "0"
python host_runtime/app.py
```

Во втором случае shell остается `Raspberry Pi`-веткой по ownership, но browser entry context должен маркироваться как `Laptop smoke`, а не как real-device equivalent.

По умолчанию сервер поднимается на:

- `http://0.0.0.0:8080/`

Основные страницы:

- `/`
- `/service`
- `/gallery`
- `/settings`
- `/turret`
- `/service/turret`
- `/service/displays`

Логичные direct routes для peer-owned slices должны уходить не в raw `404`, а в owner-aware handoff / blocked explanation:

- `/irrigation`
- `/service/irrigation`
- `/service/strobe`

Полезные API:

- `/api/v1/turret/status`
- `/api/v1/turret/runtime`
- `/api/v1/turret/events`
- `/api/v1/turret/drivers`
- `/api/v1/turret/scenarios`
- `/api/v1/content/status`

## Развертывание На Raspberry Pi С NVMe SSD

Ниже practical baseline для owner-side запуска на `Raspberry Pi`, когда `NVMe SSD` используется как основной runtime/data disk.

### 1. Что лучше делать на NVMe

Рекомендуемая схема этого этапа:

- держать сам checkout проекта на `NVMe`, а не на `microSD`;
- держать Python `venv` на `NVMe`;
- держать `content_root` на `NVMe`, чтобы `Gallery`, `Reports` и тяжелые библиотеки не писались на карту памяти.

Если `Raspberry Pi` уже загружается прямо с `NVMe`, это самый простой вариант: проект и контент можно просто разместить на этом диске и не переопределять пути.

Если система загружается с `microSD`, а `NVMe` только подключен как data disk, используйте один выделенный путь вроде:

```bash
/mnt/nvme/smart-platform
```

### 2. Что поставить на Raspberry Pi

Минимальный bootstrap:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip rsync
```

`requirements.txt` сейчас легкий, но `python3-venv` и `pip` все равно нужны.

### 3. Что копировать на NVMe

Самый безопасный вариант для текущего этапа: копировать весь репозиторий на `NVMe`.

Например:

```bash
sudo mkdir -p /mnt/nvme/smart-platform
sudo chown -R "$USER":"$USER" /mnt/nvme/smart-platform
cd /mnt/nvme/smart-platform
git clone <YOUR_REPO_URL> Smart_Platform
```

Или, если копируете с laptop вручную:

- скопируйте весь каталог проекта `Smart_Platform/` на `NVMe`;
- убедитесь, что внутри есть `host_runtime/` и `requirements.txt`.

Если нужен именно минимальный runtime payload, а не весь репозиторий, для текущего owner-side shell достаточно как минимум:

- `host_runtime/`
- `requirements.txt`

Но это менее устойчиво к будущим изменениям структуры, поэтому полный checkout надежнее.

### 4. Что обязательно должно быть в content root

Если вы переносите проект на новый `Raspberry Pi`, не забудьте каталог контента:

- `host_runtime/content/assets/`
- `host_runtime/content/audio/`
- `host_runtime/content/animations/`
- `host_runtime/content/libraries/`
- `host_runtime/content/gallery/`

Если у вас уже есть живая история `Gallery > Reports` или другие артефакты, их нужно перенести вместе с `host_runtime/content/`, а не только код.

### 5. Как подготовить venv на NVMe

Из корня проекта на `Raspberry Pi`:

```bash
cd /mnt/nvme/smart-platform/Smart_Platform
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Как запускать вручную

Если весь проект лежит на `NVMe`, можно использовать простой owner-side запуск:

```bash
cd /mnt/nvme/smart-platform/Smart_Platform/host_runtime
../.venv/bin/python app.py
```

По умолчанию сервер слушает `0.0.0.0:8080`, а `content_root` берется из:

```bash
host_runtime/content
```

относительно самого файла `app.py`.

### 7. Как запускать с явными переменными окружения

Если хотите сразу зафиксировать публичный URL, `ESP32` peer и отдельный content path на `NVMe`, используйте так:

```bash
cd /mnt/nvme/smart-platform/Smart_Platform
export SMART_PLATFORM_RPI_HOST="0.0.0.0"
export SMART_PLATFORM_RPI_PORT="8080"
export SMART_PLATFORM_RPI_PUBLIC_BASE_URL="http://raspberrypi.local:8080"
export SMART_PLATFORM_RPI_CONTENT_ROOT="/mnt/nvme/smart-platform/Smart_Platform/host_runtime/content"
export SMART_PLATFORM_ESP32_BASE_URL="http://192.168.4.1"
export SMART_PLATFORM_SYNC_ENABLED="1"
./.venv/bin/python host_runtime/app.py
```

Если пока нужен только локальный owner-side прогон без реального peer sync, можно временно поставить:

```bash
export SMART_PLATFORM_SYNC_ENABLED="0"
```

### 8. Если код на NVMe, а content_root хотите хранить отдельно

Допустима и такая схема:

- код: `/mnt/nvme/smart-platform/Smart_Platform`
- тяжелый контент: `/mnt/nvme/smart-platform/content_root`

Тогда перед запуском задайте:

```bash
export SMART_PLATFORM_RPI_CONTENT_ROOT="/mnt/nvme/smart-platform/content_root"
```

и заранее скопируйте туда содержимое `host_runtime/content/`.

### 9. Как сделать автозапуск через systemd

Создайте unit:

```bash
sudo nano /etc/systemd/system/smart-platform-rpi.service
```

Содержимое:

```ini
[Unit]
Description=Smart Platform Raspberry Pi Shell
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/mnt/nvme/smart-platform/Smart_Platform
Environment=SMART_PLATFORM_RPI_HOST=0.0.0.0
Environment=SMART_PLATFORM_RPI_PORT=8080
Environment=SMART_PLATFORM_RPI_PUBLIC_BASE_URL=http://raspberrypi.local:8080
Environment=SMART_PLATFORM_RPI_CONTENT_ROOT=/mnt/nvme/smart-platform/Smart_Platform/host_runtime/content
Environment=SMART_PLATFORM_ESP32_BASE_URL=http://192.168.4.1
Environment=SMART_PLATFORM_SYNC_ENABLED=1
ExecStart=/mnt/nvme/smart-platform/Smart_Platform/.venv/bin/python /mnt/nvme/smart-platform/Smart_Platform/host_runtime/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-platform-rpi.service
sudo systemctl start smart-platform-rpi.service
sudo systemctl status smart-platform-rpi.service
```

### 10. Что проверить после запуска

С `Raspberry Pi` или с другого viewer-устройства откройте:

- `http://raspberrypi.local:8080/`
- `http://raspberrypi.local:8080/service`
- `http://raspberrypi.local:8080/service/displays`
- `http://raspberrypi.local:8080/settings`

Минимальная smoke-проверка:

- shell открывается;
- `Laboratory` открывается;
- `Display Laboratory` открывается;
- `Settings` показывает runtime host и storage paths;
- если `ESP32` еще не поднята, peer должен честно отображаться как `offline`, а не притворяться локально доступной.

## Переменные окружения

- `SMART_PLATFORM_RPI_HOST`
- `SMART_PLATFORM_RPI_PORT`
- `SMART_PLATFORM_RPI_PUBLIC_BASE_URL`
- `SMART_PLATFORM_RPI_CONTENT_ROOT`
- `SMART_PLATFORM_RPI_NODE_ID`
- `SMART_PLATFORM_ESP32_BASE_URL`
- `SMART_PLATFORM_SYNC_INTERVAL_SEC`
- `SMART_PLATFORM_SYNC_ENABLED`

## Что важно помнить

- `Raspberry Pi` — владелец турели.
- `ESP32` не должен напрямую перетирать runtime турели.
- shell на `Raspberry Pi` и `ESP32` должен оставаться визуально согласованным.
- верхняя shell bar должна объяснять не только ownership, но и entry context: host runtime, launch client, topology, input profile и layout helper;
- текущий driver layer еще не управляет железом, а только держит каркас binding'ов.
- peer-owned модули теперь открываются через federated handoff flow, а не через слепое локальное управление чужой страницей.
- тяжелый контент и крупные библиотеки данных на этой стороне должны жить в `content_root`, зеркально к `ESP32 SD`.

`TODO(stage-rpi-real-devices-and-vision)`

## Latest Stage

Теперь в каталоге `host_runtime` уже есть software-level `Turret v1`
поверх первого общего log/sync-контура с `ESP32`.

Что это значит practically:

- `Turret` больше не выглядит как набор внутренних runtime-флагов;
- `/turret` показывает продуктовый модульный обзор, а `/service/turret` держит service/test инструменты;
- `camera` и `range` уже присутствуют в owner-модели как software-level availability channels;
- action channels и automatic gates публикуются как понятные product-level состояния;
- локальные события `Raspberry Pi` отправляются в `ESP32`;
- `Raspberry Pi` умеет забирать `/api/v1/logs` у `ESP32`;
- общий shell показывает смешанный platform log с локальными и зеркалированными записями;
- повторные remote log entry дедуплицируются по `origin_node + origin_event_id`.

Это еще не real-device turret integration, но уже рабочее software-level продуктовое состояние
для следующего модульного шага: `Service/Test v1`.
