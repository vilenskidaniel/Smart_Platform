# 14. Settings Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Settings` как постоянного системного слоя.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный активный канон для `Settings`; историческое состояние переноса держим в `knowledge_base/17_open_questions_and_migration.md`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/settings_prompt.md` остается prompt-layer companion source для рабочего режима чата.

## Установленные Истины

- `Settings` хранит persistent truth и shared preferences
- constructor, registry, profiles и save/apply описываются отдельно от runtime state
- current controller profile не должен маскироваться под вечный module ownership

## Канон

### 1. Роль И Пользовательский Итог

`Settings` - это одна глобальная постоянная страница платформы.

Для пользователя `Settings` должен давать такой итог:

- одно спокойное место для durable operator intent;
- shared preferences, которые не теряются между входами;
- persistent настройки sync, storage, policies и module-facing baselines;
- явное различие между saved, staged, applied и fallback-persisted state;
- понятную границу между `Laboratory` experiment flow и product-level system truth.

`Settings` не является:

- инженерным рабочим пространством `Laboratory`;
- повтором shell bar или обзорной runtime page;
- full live dump of runtime state;
- местом, где модуль временно приравнивается к текущей плате-контроллеру.

Канонический route:

- `/settings`

### 2. IA: Appearance, Runtime, Sync, Storage, Modules, Components, Services, Policies, Constructor, Diagnostics

Канонический rail order `v1`:

1. `Appearance`
2. `Runtime`
3. `Sync`
4. `Storage`
5. `Modules`
6. `Components`
7. `Services`
8. `Policies`
9. `Constructor`
10. `Diagnostics`

Этот порядок уже материализован в текущих shell-реализациях и поэтому считается активной модульной истиной.

Назначение разделов:

- `Appearance`: language, theme, density, fullscreen и другие shell-facing preferences;
- `Runtime`: launch context, host/viewer distinction, runtime profile и honest summary without turning into debug dump;
- `Sync`: continuity preferences, selected domains и persistent sync mode;
- `Storage`: roots, readiness, path actions и guarded cleanup operations;
- `Modules`: module registry, module ownership baselines и expected routes;
- `Components`: hardware component registry, fields and bindings;
- `Services`: software/system services tracked separately from hardware modules;
- `Policies`: persistent safety and behavior preferences;
- `Constructor`: guided creation/editing of module/component scaffolds and system profiles;
- `Diagnostics`: expanded engineering context only when really needed.

`Diagnostics` по умолчанию должен быть secondary surface и не должен перехватывать тон страницы.

### 3. Shared Preferences And Shell Coupling

`Settings` хранит shared preferences, которые должны оставаться одной и той же истиной на всех shell-поверхностях.

Минимальный обязательный набор `v1`:

- language;
- theme;
- density;
- fullscreen preference;
- desktop controls / keyboard enablement;
- advanced diagnostics visibility.

Правила coupling:

- fullscreen preference shared between `Settings` and shell controls;
- global keyboard enablement is shared preference, but its effect applies only on relevant operator surfaces;
- language choice applies to user-facing copy across the shell;
- bar-panel and page-level controls must reflect the same stored truth rather than separate local toggles.

Theme and operator-input semantics for the current baseline:

- `theme` является именованной shell-wide preference, а не только бинарным `light/dark` switch;
- theme choice распространяется на shell pages, но global bar может сохранять нейтральный shell chrome, а operator HUD - более строгий локальный token set;
- keyboard action keys работают только на релевантных operator surfaces вроде `Turret Manual`; вне них клавиши остаются обычным text-input behavior;
- disabled `Keyboard controls` не скрывает связанные bindings и power-profile fields: они остаются видимыми, заблокированными и объясняют следующий шаг;
- `Shift` считается конфигурируемым power modifier baseline для operator controls: по умолчанию `50%`, с modifier `100%`, пока пользователь явно не переназначит эти значения.

`Settings` хранит это предпочтение. Shell-поверхности могут поддерживать его поэтапно, но не должны придумывать конфликтующий параллельный слой настроек.

### 4. Profiles, Registry And Constructor

`Settings` является постоянным домом для профилей, registry-записей и constructor-scaffold сущностей.

Здесь живут разные persistent entities:

- module records;
- component records;
- service records;
- system profiles and module-facing baselines.

Эти сущности не должны смешиваться в один undifferentiated registry list.

`Constructor` в `Settings` нужен для:

- creating new module records;
- creating new component records;
- editing registry-backed metadata;
- reviewing scaffold entries before real apply.

Constructor-scaffold entries по умолчанию считаются staged, draft or simulated until explicit confirmation/apply path completes.

Перенос из `Laboratory`:

- `Laboratory` may emit reviewed candidates or profile updates into `Settings`;
- they do not silently become durable product settings just because they were observed in a session;
- `Settings` must show origin, related module/component and current apply state;
- once a profile is confirmed as the active baseline, the corresponding module/component can use it as the default on the next entry.

### 5. Save, Apply, Defaults And Origin Tracking

`Settings` следует optimistic-first, но честной модели сохранения.

Нужно сохранить:

- immediate UI response;
- debounced background save;
- no full-page blocking for ordinary edits;
- explicit disabled or error state when persistence fails.

Active canon distinguishes at least these states:

- draft;
- saved;
- applied;
- failed;
- browser-fallback persisted.

Origin tracking must remain visible enough to prevent false confidence:

- saved on host/server;
- saved only in this browser as fallback;
- staged but not yet applied;
- inherited default versus user-chosen override.

Browser fallback persistence is acceptable on limited shells when server-backed endpoint is unavailable, but the UI must say so plainly.

### 6. Storage And Sync

`Storage` inside `Settings` is an operational persistent surface, not the user-facing replacement for `Gallery`.

Allowed storage responsibilities:

- content roots and report/archive paths;
- readiness detail;
- `Copy path`;
- `Open folder` and `Open in app` when safely supported on the host;
- cleanup preview;
- confirmed cleanup with protected-root boundaries.

Host/viewer caveat must stay visible:

- storage paths belong to the host filesystem, not necessarily to the current viewer device;
- `Open folder` and similar host-actions execute on the host side and must not pretend they can open a peer or browser-local filesystem;
- when viewer and host differ, `Settings` may keep the same storage truth but should explain where the action will actually run.

`Storage` must not turn into a top-level content browser.

`Sync` stores persistent synchronization behavior.

Минимальная model truth:

- `Auto`
- `Manual review`

Any explicit domain override moves the mode into `Manual review`.

Confirmed sync domains for `v1`:

- `service_link`
- `module_state`
- `shared_preferences`
- `reports_history`
- `plant_library`
- `media_content`
- `component_registry`
- `software_versions`

`Sync` may also store continuity preference and polling baseline, but it must still read as persistent system behavior rather than a raw transport console.

### 7. Controller Profiles, Components And Platform Configuration

`Settings` can show current owner expectations, routes and availability, but it must not collapse `module` into `board`.

Canonical distinctions:

- `Modules` are functional systems such as `Turret`, `Irrigation`, `Power`;
- `Components` are concrete hardware elements such as cameras, servos, valves, pumps, sensors and displays;
- `Services` are software/system entities such as shell, sync core and storage service.

Current controller profiles are deployment-time truth, not eternal architecture truth.

So `Settings` must be able to express:

- expected owner node;
- current availability;
- local / handoff / blocked / virtual routing semantics;
- stored owner-side baseline even when that owner is currently unavailable.

Example: an irrigation baseline stored on an `ESP32` owner remains a truthful owner-side baseline, not a fake local irrigation controller on another host.

`Policies` also live here as durable behavior baselines:

- turret safety preferences;
- irrigation automatic-behavior preferences;
- scenario constraints and fallback rules.

Representative persistent policy families at the current stage:

- turret action constraints вроде `do not fire on humans` или `silent observation only`;
- capture policy вроде `allow_auto_capture` и `max_recording_seconds`;
- operator input/power baselines, которые влияют на `Manual`, не превращая `Settings` в live control page.

Unavailable policies stay visible with a short reason and the next step, rather than being hidden.

### 7.1 Реальные Кодовые Опоры Текущего Слоя

Чтобы `Settings` оставался связанным с реальным persistent layer, ниже фиксируем текущие implementation anchors:

- `host_runtime/settings_store.py` - persistent JSON-backed `SettingsStore` для owner-side system settings;
- `host_runtime/web/settings.html` - current `/settings` page на стороне `Raspberry Pi`;
- `io_firmware/data/settings/index.html` - mirror `/settings` page на стороне `ESP32`;
- `host_runtime/server.py` - HTTP-entry для `GET/POST /api/v1/settings`;
- `host_runtime/tests/test_settings_store.py` - tests persistence и validation для settings layer;
- `host_runtime/content/.system/settings_state.json` - фактический persisted state, который использует текущий store.

### 8. Проверочные Критерии

Минимальные проверочные критерии текущего этапа:

1. `/settings` exists on current shells as a persistent settings surface;
2. canonical rail order remains `Appearance -> Runtime -> Sync -> Storage -> Modules -> Components -> Services -> Policies -> Constructor -> Diagnostics`;
3. shared preferences remain one truth between `Settings` and shell-level controls;
4. `Storage` allows safe path actions and guarded cleanup without replacing `Gallery`;
5. `Sync` stores mode and domains without turning into a transport log page;
6. `Modules`, `Components` and `Services` stay separate registry families;
7. promotion from `Laboratory` into `Settings` remains explicit and origin-tracked;
8. browser fallback persistence, when used, is visible as fallback rather than pretending server-backed save succeeded;
9. diagnostics stay secondary and do not redefine the whole page tone.

### 9. Нормативные Примеры И Форматы

Нормативные route examples:

- settings page: `/settings`
- storage diagnostics entry point: `/api/v1/content/status`

Пример settings payload:

```json
{
  "schema_version": "settings.v1",
  "interface": {
    "language": "en",
    "desktop_controls_enabled": true,
    "fullscreen_enabled": false,
    "show_advanced_diagnostics": false
  },
  "style": {
    "theme": "meadow",
    "density": "comfortable"
  },
  "synchronization": {
    "preferred_mode": "auto",
    "prefer_peer_continuity": true
  }
}
```

Пример module ownership baseline:

```json
{
  "module_id": "irrigation",
  "expected_owner": "esp32",
  "route_mode": "handoff",
  "availability": "remote_unavailable",
  "baseline_profile": "greenhouse_v1"
}
```

Пример promoted candidate from `Laboratory`:

```json
{
  "source_surface": "laboratory",
  "target_family": "component_profile",
  "target_component": "camera.main",
  "candidate_id": "camera_daylight_v2",
  "save_state": "staged",
  "apply_state": "pending_review"
}
```

## Open Questions

- где лучше провести границу между persistent topology config и runtime-visible platform composition
- какая часть constructor/profile schema должна стать human-editable contract, а какая может оставаться implementation-facing

## TODO

- после стабилизации active draft переаудировать settings migration-state в ledger и оставить там только исторически полезные detail reminders
- позже разнести service/storage-specific residue между `knowledge_base/07` и `knowledge_base/15`

## TBD

- итоговая форма long-lived registry schemas и human-editable profile documents
