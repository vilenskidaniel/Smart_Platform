# Module Registry Contract

Этот файл относится к пункту 1 master-plan.

Он фиксирует минимальную модель реестра модулей, без которой дальше нельзя строить ни shell, ни синхронизацию, ни разблокировку страниц.

## Зачем нужен реестр модулей

Shell на `compute node` и `I/O node` должен понимать:

- какие модули существуют;
- кто владелец каждого модуля;
- в каком состоянии модуль находится;
- какие действия для него разрешены;
- должен ли модуль отображаться, если его владелец недоступен.

## Обязательные поля модуля

Каждый модуль обязан описываться одинаково.

Минимальный состав для `platform_registry.v1`:

```json
{
  "id": "turret",
  "title": {
    "en": "Turret",
    "ru": "Турель"
  },
  "summary": {
    "en": "Camera-guided module.",
    "ru": "Модуль наведения и наблюдения."
  },
  "owner_role": "compute_node",
  "runtime_module_id": "turret_bridge",
  "state": "disconnected",
  "component_ids": ["camera", "servo_pan_tilt"]
}
```

Legacy-поля `profile`, `visible`, `service_page`, `manual_page`,
`capabilities`, `locked_reason` и `ui_group` могут появляться в старых
документах или payload, но не являются обязательными полями нового registry.

## Актуальный JSON-реестр Settings/Constructor

Рабочий файл host-side реестра:

`host_runtime/content/.system/platform_registry.v1.json`

Backend обслуживает его через:

- `GET /api/v1/platform/registry`;
- `POST /api/v1/platform/registry/constructor`.

`Constructor` в `Settings` больше не является декоративной заглушкой: после
подтверждения wizard создаёт записи в JSON/config через приложение. Железо при
этом не обязано быть подключено: новые записи могут иметь состояние `simulated`
или `not_detected`, пока не появится runtime-проверка.

Структура реестра:

```json
{
  "schema_version": "platform_registry.v1",
  "updated_at_ms": 0,
  "modules": [],
  "components": [],
  "assignments": [],
  "templates": {
    "modules": [],
    "components": []
  }
}
```

Смысл слоёв:

- `modules` — функциональные системы: `turret`, `irrigation`, `power`, будущие
  пользовательские модули вроде `cat_feeder`;
- `components` — конкретные элементы: камера, клапан, сервопривод, датчик
  движения, насос, конвертер;
- `assignments` — связь component → module, чтобы компонент можно было
  переназначать без переписывания всей модели;
- `templates` — стартовые заготовки wizard, не источник runtime-состояния.

## Канонические id модулей первой версии

- `irrigation`
- `turret`
- `power`
- `cat_feeder` как первый пример custom module

Software-сущности вроде `Platform Shell`, `Sync Core`, `Storage Service`,
`Settings`, `Diagnostics` и `Laboratory` не смешиваются с hardware modules.
Они живут в отдельном слое `System Services`.

## Legacy ui_group

- `system`
- `irrigation`
- `turret`
- `service`
- `settings`
- `logs`

`ui_group` остаётся compatibility-полем для старых shell payload. Новый
Settings registry группирует hardware через `modules/components/assignments`,
а software surfaces через `System Services`.

## Правило видимости

- Если модуль важен для общей карты системы, он должен быть видим даже в `locked` или `offline`.
- Полностью скрывать допускается только внутренние служебные сущности, которые не являются пользовательскими разделами.

## Правило владельца

- Только владелец модуля может исполнять управляющие команды.
- Невладелец может только показывать статус, кнопку и причину блокировки.
- Для новых документов и UI-моделей использовать канонические значения:
  - `compute_node`
  - `io_node`
  - `shared`
- Legacy alias `rpi` и `esp32` допускаются только как compatibility-layer для
  уже существующих payload и логов.

## Пример Cat Feeder

`Cat Feeder` не должен использовать `Light Sensor` как смысловой компонент:
кот не является источником света и не обязан менять освещённость перед
устройством.

Утверждённый базовый сценарий:

- `Motion Sensor` будит камеру;
- камера запускает видеоидентификацию;
- дополнительный сигнал запроса, например мяуканье или событие присутствия,
  может уведомить владельца;
- после политики/подтверждения запускается `Servo dispenser`.

Минимальный набор компонентов примера:

- `cat_feeder_motion_sensor`;
- `cat_feeder_camera`;
- `cat_feeder_servo`.

## Связь с shell UI

Shell обязан строить меню и карточки модулей не по захардкоженному списку в нескольких местах, а по единому registry.

`TODO(stage-shell-registry)`

На следующем этапе этот контракт нужно использовать как основу для:

- генерации меню;
- построения карточек на главной;
- состояния `locked/degraded/fault`.
