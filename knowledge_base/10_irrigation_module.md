# 10. Irrigation Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Irrigation` как модуля, а не как набора stage-реализаций под конкретную плату.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный активный канон для `Irrigation`; историческое состояние переноса держим в `knowledge_base/17_open_questions_and_migration.md`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/irrigation_prompt.md` остается prompt-layer companion source для рабочего режима чата.

## Установленные Истины

- `Irrigation` описывается как продуктовый модуль полива
- текущий controller profile не равен вечной архитектурной истине модуля
- service и laboratory surfaces не должны подменять product surface

## Canon

### 1. Роль И Итог Для Пользователя

`Irrigation` - это продуктовый модуль, через который пользователь видит состояние зон полива, состояние среды и почвы, запускает ручной полив и включает базовый автоматический режим.

Для пользователя модуль должен давать такой итог:

- понятный список зон и их текущий статус;
- видимость environment summary и sensor health;
- ручной запуск и остановку без перехода в инженерные страницы;
- честное объяснение, почему auto или конкретная зона недоступны;
- работу без постоянной зависимости от `Raspberry Pi`.

`Irrigation` не должен мыслиться как страница пинов, драйверов или bench-controls. Эти детали живут в owner-side engineering surfaces и implementation layer.

### 2. Состав Модуля

В состав `Irrigation` как модуля входят:

- зоны полива;
- soil sensors и environment-related measurements;
- малый peristaltic pump и plant valve cascade;
- базовый automatic flow;
- product page `/irrigation`;
- owner-side laboratory/service slice для инженерной проверки;
- activity/log data и overlay data для других product surfaces;
- storage-extension role через `ESP32 SD module` для локальных irrigation-related данных и резервных synced-файлов.

`Irrigation` не владеет turret water path `SEAFLO`. Этот водяной контур относится к turret-family и owner-side turret runtime.

### 3. Controller Profiles И Текущая Временная Реализация

`Irrigation` не равен конкретной плате по смыслу модуля. Однако текущий working controller profile для `v1` таков:

- owner-side always-on `I/O` node today-baseline `ESP32`;
- локальная автономность без обязательного присутствия `Raspberry Pi`;
- direct owner-side page и API на `ESP32`;
- shell-visible owner-aware access с peer-side blocked/degraded semantics.

Текущий implementation baseline при этом временно фиксирует:

- реальные outputs оставлены выключенными по умолчанию;
- в коде используется safe default вроде `kEnableRealOutputsByDefault = false`;
- одна активная зона одновременно считается нормой текущего software baseline;
- реальные soil sensors, valve drivers и safe activation levels еще требуют отдельного hardware confirmation.

Это временный current profile, а не вечная архитектурная привязка модуля.

### 4. Product Surface

Каноническая product page для модуля:

- `/irrigation`

На product surface пользователь должен видеть:

- статус модуля;
- environment summary;
- список зон;
- sensor fault visibility;
- active run source;
- состояние базового auto-mode;
- локальный irrigation log или краткую activity summary.

Product page не должна превращаться в инженерный backend. На ней допустимы product-level manual actions и truthful status, но не raw service tooling.

Если owner-side недоступен на peer-view:

- модуль остается видимым в shell;
- peer-side UI не притворяется owner-side контроллером;
- пользователь получает blocked/degraded explanation вместо скрытия маршрута.

### 5. Service And Laboratory Surfaces

Owner-side engineering contour для `Irrigation` живет внутри общего `Laboratory` workspace.

Current compatibility surface может еще использовать route:

- `/service/irrigation`

Этот compatibility route допустим как implementation layer и может давать:

- service pulse по зоне;
- sensor profile simulation;
- engineering-oriented controls для проверки owner-side logic.

Поддерживаемые service-oriented sensor profiles на текущем baseline:

- `dry`
- `wet`
- `fault`
- `restore`

Нормативное правило:

- `Laboratory` и service slice не подменяют product IA модуля;
- промежуточные проверки, console output и trial actions не становятся автоматически product truth;
- подтвержденные параметры переходят в persistent layer только через явный `save/apply` path, а не из service-route напрямую.

### 6. Zone Model, Sensor Model And Water Path

Внутри owner-side controller модуль должен мыслить минимум следующими сущностями:

- zone;
- soil sensor state per zone;
- environment snapshot;
- auto eligibility per zone;
- active run source;
- water path state для small irrigation path.

Текущая normative model:

- зоны являются first-class сущностями, а не побочным массивом output pins;
- sensor logic живет в controller, а не в UI;
- модуль умеет честно показывать sensor fault flags и отсутствие live sensors;
- auto baseline выбирает самую сухую eligible zone;
- текущий software baseline допускает только одну активную зону одновременно.

Water-path boundary:

- `Irrigation` владеет small peristaltic pump + plant valve cascade;
- turret sprayer path не входит в модуль;
- owner-visible water reserve model для drip irrigation и turret spraying должны оставаться разделенными даже при общих shell summaries.

Overlay effect boundary:

- при доступном owner-side `ESP32` модуль может отдавать summary для turret manual HUD overlay;
- overlay может включать valve visibility, air temperature, air humidity и irrigation water reserve summary;
- overlay не превращает irrigation controls в часть turret ownership.

### 7. States, Faults And Blocked Behavior

Для cross-module shell и module page `Irrigation` использует общий shared UI vocabulary, а не свой отдельный язык состояний.

Практически это означает:

- `ready` или `online`: owner-side модуль доступен и может выполнять product actions;
- `active`: идет manual run или automatic run;
- `attention` или `degraded`: sensor data частично отсутствуют, используется simulation, либо часть условий для auto не выполнена;
- `blocked` или `locked`: route видим, но текущая точка входа не может исполнять действие, либо engineering/service context блокирует product-level auto start;
- `fault`: подтвержденная sensor/output/runtime problem, которая должна быть явно названа, а не замаскирована под neutral state.

Нормативные примеры blocked behavior:

- peer-side viewer без owner connection видит модуль, но не исполняет owner-only action;
- laboratory-held test flow не должен тихо запускать automatic scenario;
- dry-run baseline не должен притворяться live-water hardware execution без явного объяснения.

### 8. Data, Profiles, Reports And Overlay Effects

Текущие implementation-facing endpoints, которые уже материализуют модульный контракт:

- `/api/v1/irrigation/status`
- `/api/v1/irrigation/zones`
- `/api/v1/irrigation/start`
- `/api/v1/irrigation/stop`

На уровне данных модуль уже должен уметь держать:

- module status;
- zones snapshot;
- soil sensor state;
- environment snapshot;
- sensor fault flags;
- active run source;
- auto eligibility.

Логический storage/reporting boundary:

- irrigation actions и ошибки логируются в owner-side activity layer;
- product-significant outcomes могут подниматься в platform activity и дальше в `Gallery > Reports`;
- engineering/service traces остаются в `Laboratory` session layer и не должны напрямую засорять `Reports`.

### 8.1 Реальные Кодовые Опоры Текущего Слоя

Чтобы `Irrigation` не оставался только словарем продукта, ниже фиксируем реальные текущие implementation surfaces:

- `io_firmware/src/modules/irrigation/IrrigationController.cpp` - owner-side controller для зон, sensor state, auto baseline и safe output behavior на `ESP32`;
- `io_firmware/data/irrigation/index.html` - текущая пользовательская page `/irrigation` на стороне `ESP32`;
- `io_firmware/data/service/irrigation.html` - owner-side service-экран для инженерной проверки зон, sensor profiles и fault simulation;
- `host_runtime/server.py` - shell-side HTTP-вход, который уже держит irrigation endpoints вроде `/api/v1/irrigation/status`, `/api/v1/irrigation/zones`, `/api/v1/irrigation/start` и `/api/v1/irrigation/automatic`.

Отдельного выделенного irrigation test-slice в репозитории пока нет, поэтому текущий acceptance baseline для модуля нужно читать через controller behavior, page route и эти owner-side endpoints.

### 9. Safety And Acceptance Hooks

Для `Irrigation` в текущем active canon важны такие safety hooks:

- реальные outputs не включаются по умолчанию до hardware confirmation;
- safe activation level насоса и valve cascade должен быть подтвержден отдельно;
- отсутствие live sensors должно вести к truthful degraded behavior, а не к тихому auto optimism;
- shell, API и product page должны оставаться тестируемыми даже в safe dry-run baseline.

Минимальные acceptance hooks текущего этапа:

1. shell видит и открывает `/irrigation` как product module;
2. manual start и stop работают predictably в owner-side baseline;
3. sensor fault visibility и auto eligibility читаются явно;
4. automatic baseline выбирает самую сухую eligible zone;
5. peer-side shell сохраняет visibility модуля без ложного owner impersonation.

### 10. Нормативные Примеры И Форматы

Пример status payload:

```json
{
  "module": "irrigation",
  "state": "ready",
  "auto_mode": true,
  "active_run_source": "automatic",
  "environment": {
    "air_temperature_c": 23.4,
    "air_humidity_pct": 51.0
  },
  "faults": [],
  "owner_profile": "always_on_io_node"
}
```

Пример zone entry:

```json
{
  "zone_id": "zone_01",
  "label": "North Bed",
  "state": "attention",
  "soil_sensor": {
    "state": "dry",
    "fault": false
  },
  "auto_eligible": true,
  "last_run_source": "manual"
}
```

Нормативные route examples:

- product page: `/irrigation`
- owner-side engineering compatibility route: `/service/irrigation`
- status API: `/api/v1/irrigation/status`
- zones API: `/api/v1/irrigation/zones`
- action APIs: `/api/v1/irrigation/start`, `/api/v1/irrigation/stop`

## Open Questions

- какая часть auto-поведения уже считается устойчивым продуктовым контрактом, а какая еще временной реализацией
- где exactly проходит граница между owner-visible irrigation overlay для turret HUD и отдельным turret-side control surface

## TODO

- подключить реальные датчики и калибровку вместо полной sensor simulation;
- подтвердить безопасные уровни активации для реального peristaltic pump и valve cascade;
- добавить расписания и более богатые automatic scenarios поверх текущего baseline;
- описать и затем реализовать синхронизацию irrigation scenarios и связанных state-последствий между `ESP32` и `Raspberry Pi`;
- зафиксировать owner-visible water reserve model с раздельными summary для drip irrigation и turret spraying и минимум двумя sensor entry points на `ESP32` и `Raspberry Pi`;
- подготовить данные для turret manual HUD overlay: valve visibility, air temperature, air humidity и irrigation water reserve summary;
- после следующего module pass проверить, можно ли дальше схлопнуть implementation residue без потери current working baseline

## TBD

- будущая multi-controller схема для полива
- owner-visible water reserve split между drip irrigation и turret spraying summary
