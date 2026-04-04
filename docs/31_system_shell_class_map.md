# System Shell V1 Class Map

Этот документ нужен, чтобы `System Shell v1` не продолжал жить как один
разросшийся `WebShellServer` на `ESP32` и один большой `server.py` на
`Raspberry Pi`.

Он не заставляет нас немедленно переписывать runtime. Его задача проще:

- зафиксировать 5-8 крупных сущностей shell;
- разделить продуктовые роли и transport-склейку;
- дать понятную карту дальнейшего рефакторинга без ухода в мелкие методы.

## 1. Главный принцип

`System Shell v1` для обеих сторон должен мыслиться одинаково:

- один и тот же продуктовый shell;
- одинаковые страницы;
- одинаковые смыслы `locked/degraded/fault`;
- одинаковый federated handoff;
- разные runtime-источники данных на `ESP32` и `Raspberry Pi`.

Значит, мы не проектируем две разные shell-системы. Мы проектируем один набор
крупных ролей, который потом реализуется двумя адаптерами.

Важно:

- названия `ShellLogPresenter` и `ShellContentPresenter` в этом документе описывают
  текущий software baseline, а не конечный product vocabulary;
- глубокая история действий должна уходить в `Gallery > Reports`,
  а `Content Storage` остается service/storage diagnostics surface.

## 2. Целевые крупные классы

### 1. `ShellSnapshotFacade`

Назначение:
- превращает runtime-данные узла в понятный shell snapshot;
- собирает `node status`, `module registry`, `owner summary`,
  `content status`, краткую диагностику и краткие логи.

Граница ответственности:
- не рисует HTML;
- не знает про конкретные кнопки интерфейса;
- не запускает пользовательские команды модулей.

### 2. `ShellNavigationCoordinator`

Назначение:
- решает, что открывать локально, а что вести через handoff;
- знает `canonical_url`, `owner_available`, `federated_access`;
- определяет поведение пунктов `Полив`, `Турель`, `Gallery`, `Laboratory`.

Граница ответственности:
- не хранит runtime-состояние модуля;
- не рендерит страницы;
- не подменяет собой владельца peer-owned модуля.

### 3. `ShellHomePresenter`

Назначение:
- формирует главную страницу shell;
- показывает карточки узлов, быстрые входы в разделы, предупреждения,
  handoff-подсказки и общий статус системы.

Граница ответственности:
- не должен знать детали transport-слоя;
- не должен самостоятельно лезть в модули;
- получает только уже подготовленные shell-данные.

### 4. `ShellSettingsPresenter`

Назначение:
- отвечает за страницу `Настройки`;
- показывает язык, тему, базовые сетевые параметры, shell base URL,
  задел под будущую авторизацию.

Граница ответственности:
- не владеет peer sync;
- не хранит тяжелую бизнес-логику модулей;
- работает только с shell-level настройками.

### 5. `ShellDiagnosticsPresenter`

Назначение:
- отвечает за shell-level diagnostics summary;
- показывает heartbeat, sync state, ownership summary, capability flags,
  fault/degraded причины и storage readiness.

Граница ответственности:
- не запускает ремонтные действия;
- не подменяет service/test раздел;
- показывает только диагностическую картину.

### 6. `ShellLogPresenter`

Назначение:
- отвечает за короткий shell activity summary и transitional log surfaces;
- показывает локальные события, синхронизированные события и ручные действия высокого уровня;
- умеет отбирать краткий набор активности, нужный пользователю shell,
  и подготавливать быстрый вход в `Gallery > Reports`.

Граница ответственности:
- не является самим логгером платформы;
- не решает вопросы хранения и репликации логов;
- только представляет их в shell.

### 7. `ShellContentPresenter`

Назначение:
- отвечает за service/storage страницу `Content Storage`;
- показывает состояние `LittleFS`, `SD`, mirrored content root и `/libraries`;
- помогает понять, доступен ли тяжелый контент на текущем узле.

Граница ответственности:
- не управляет синхронизацией контента;
- не хранит библиотеки сам;
- не подменяет user-facing `Gallery`;
- только представляет и объясняет состояние content-слоя.

### 8. `ShellHttpAdapter`

Назначение:
- это тонкий transport-слой shell;
- регистрирует маршруты, принимает HTTP-запросы, отдает страницы и JSON;
- связывает runtime-адаптеры с presenter-слоем.

Граница ответственности:
- не должен быть местом, где живет вся shell-логика;
- не должен разрастаться в монолит business/UI/runtime слоя;
- должен делегировать работу перечисленным выше сущностям.

## 3. Как это ложится на текущий код

Сейчас в проекте:

- на `ESP32` почти вся shell-логика физически сидит в `WebShellServer`;
- на `Raspberry Pi` почти вся shell-логика физически сидит в `server.py`.

Это допустимо для bootstrap-этапа, но уже неудобно для контроля глубины.

Поэтому наша цель не "срочно переписать все", а постепенно привести текущий код
к этой карте:

- `WebShellServer` и `server.py` должны остаться transport entrypoint;
- сборка данных должна постепенно уходить в `ShellSnapshotFacade`;
- handoff и owner-aware правила должны жить в `ShellNavigationCoordinator`;
- страницы shell должны мыслиться как отдельные presenters.

## 4. Что пока не нужно дробить

Чтобы снова не уйти в хаос, сейчас не нужно:

- выдумывать отдельный класс на каждый JSON-ответ;
- делать отдельный presenter на каждую мелкую карточку;
- дробить `Settings` на десять внутренних сервисов;
- строить сложный client-side framework ради shell v1.

Для `System Shell v1` достаточно этих восьми крупных ролей.

## 5. Порядок внедрения

1. Сначала держим эту карту как целевой reference.
2. Затем отмечаем, где текущий runtime уже покрывает нужную роль.
3. После этого выносим в отдельные классы только то, что уже начинает мешать.
4. И только потом углубляем конкретные shell-страницы.

## 6. Связанные артефакты

- [27_system_shell_v1_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/27_system_shell_v1_spec.md)
- [30_top_down_architecture_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/30_top_down_architecture_map.md)
- [32_current_shell_role_mapping.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/32_current_shell_role_mapping.md)
- [33_shell_snapshot_schema.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/docs/33_shell_snapshot_schema.md)
- [shell_snapshot_contract.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/shared_contracts/shell_snapshot_contract.md)
- [system_shell_esp32_blueprint.h](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/system_shell_esp32_blueprint.h)
- [system_shell_raspberry_pi_blueprint.py](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/skeletons/system_shell_raspberry_pi_blueprint.py)
