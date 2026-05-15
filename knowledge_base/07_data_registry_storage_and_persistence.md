# 07. Data, Registry, Storage And Persistence

## Роль Файла

Этот файл должен объяснять, как в системе устроены идентификаторы, registry, storage, save/apply и различие между временным и постоянным состоянием.

## Статус

- текущий статус: `active draft`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `shared_contracts/shell_snapshot_contract.md` остается active companion contract для shell-visible storage/runtime truth.

## Установленные Истины

- временное состояние, session notes, persistent profiles и reports не смешиваются
- registry и storage должны иметь читаемые и устойчивые идентификаторы

## 1. Общая Модель Данных

В активном каноне различаем пять разных data layers:

- `runtime truth`: текущее truthful состояние узлов, модулей, availability и sync;
- `persistent truth`: примененные системные выборы, registries, profiles и shared preferences;
- `draft/session truth`: локальные черновики и `Записи сессии` внутри `Laboratory`;
- `report truth`: короткие product-level event records для `Gallery > Reports`;
- `content truth`: media, reference materials, gallery artifacts и storage provenance.

Главное правило:

- эти слои не должны смешиваться ни в UI, ни в storage model, ни в naming;
- `Shell Snapshot` дает обзорную truthful картину, но не подменяет full registries, diagnostics APIs или mixed report feeds.

## 2. Registry И Идентификаторы

`Registry` в активном каноне означает persistent system truth.

Там живут:

- module descriptors и component bindings;
- confirmed profiles;
- constructor scaffolds;
- shared preferences и settings-derived defaults;
- turret audio profile defaults для `attack_audio` и `voice_fx`.

Правила идентификаторов:

- stable id должен быть machine-readable и долговечным;
- display label и stable id не должны совпадать по обязанности;
- `owner_node_id`, `source_node` и `storage owner` должны храниться как provenance fields, а не как часть display name;
- draft id из `Laboratory` не должен автоматически становиться persistent registry id;
- новые constructor-scaffold записи по умолчанию считаются неподтвержденными или `simulated`, пока не прошли явный путь подтверждения и применения.

Рекомендуемые классы идентификаторов:

- `module_id`
- `component_type`
- `profile_id`
- `registry_entry_id`
- `session_id`
- `report_id`
- `content_id`

## 3. Storage Slices И Корневые Границы

Для mirrored content/storage baseline фиксируем общую logical tree:

- `/assets`
- `/audio`
- `/animations`
- `/libraries`
- `/gallery`

Назначение:

- `LittleFS` или другой легкий local store держит shell bootstrap и минимальные файлы для старта;
- тяжелый content, mirrored media и growing libraries проектируются под отдельный content root;
- на `ESP32` baseline today тяжелый слой ориентирован на `SD` как SPI storage extension;
- на `Raspberry Pi` baseline today он живет в локальной filesystem root.

Базовое правило:

- shell не должен зависеть от наличия тяжелого content для самого факта запуска;
- обе стороны должны понимать одну и ту же logical structure путей, даже если физический storage backend различается.
- `ESP32 SD` может использоваться как резервная точка приема mirrored peer-owned файлов, включая turret-side bundles, но не становится источником authority для них.

## 4. Save, Apply, Draft And Default Profile

`Draft`:

- локальный временный результат работы оператора;
- может жить в browser/session context;
- не является persistent truth.

`Save/apply`:

- это явный переход из временного слоя в persistent truth;
- путь `Laboratory -> Settings` является explicit confirmation flow;
- оператор должен видеть, какой persistent target обновляется и какие поля отличаются от текущего профиля.

Если оператор нажал `Сохранить выбор` в `Laboratory`, `Settings` становится местом финальной материализации результата.

После этого должны быть видимы:

- новый или обновленный постоянный профиль;
- статус применения;
- связь с модулем или компонентом;
- возможность дальнейшего редактирования системного поведения;
- новый default selection для следующего входа в соответствующую laboratory-card.

Для audio this means explicitly:

- channel `A/B` values и scenario id для `attack_audio` остаются laboratory draft truth, пока оператор не подтвердил перенос;
- talkback / microphone / effect preset для `voice_fx` также не становятся persistent baseline автоматически от самого факта лабораторного теста;
- persistent registry/profile id для audio должен различать `attack_audio` и `voice_fx`, а не хранить их как один общий `audio` blob.

Интерактивные настройки `Settings` применяются optimistic-first, но это не должно маскировать truth:

- интерфейс получает немедленный отклик;
- запись идет в debounce/background flow;
- при ошибке остается честное error или disabled state;
- временный draft и примененный persistent profile должны оставаться различимыми.

## 5. Session Notes vs Reports

`Записи сессии` в `Laboratory`:

- это локальный рабочий след текущей инженерной сессии;
- они могут восстанавливаться после перезагрузки страницы;
- по умолчанию не синхронизируются между узлами;
- не уходят в `Gallery > Reports`.

Минимальный набор session record types для `v1`:

- `pass`
- `warn`
- `fail`
- `blocked`
- `skipped`
- `note`

`Reports`:

- это краткая пользовательская история автономно и системно зафиксированных product-level действий;
- это не архив сессий `Laboratory`;
- это не console feed, не state-table dump и не full system log.

В `Reports` по умолчанию не попадают:

- console lines;
- промежуточные calibration notes;
- state-table comparisons;
- локальные operator notes и session notes из `Laboratory`;
- ручное сохранение профиля из `Laboratory` в `Settings`.

## 6. Content Provenance And Mirroring

`Gallery` остается shared/virtual page, но каждый content object и report record должен сохранять truthful provenance:

- фактический `owner_node_id`;
- `source_surface` или related origin;
- `storage owner` или root;
- mirrored/local availability status.

`Shell Snapshot` должен давать обзорный слой storage truth:

- `storage_kind`
- `content_root`
- `content_root_state`
- `storage.paths[*]`
- `summaries.content`

Но snapshot не должен превращаться в:

- полный mixed feed `Gallery > Reports`;
- dump всех registries;
- замену `/api/v1/content/status` и других deep diagnostics APIs.

Правило mirror model:

- `Gallery` как user-facing section открывает одну logical tree;
- physical storage может быть локальным, mirrored или временно unavailable;
- при потере peer-side storage пользователь видит локальный slice и честную маркировку недоступных peer-sources.

### 6.1 Практические Guardrails Для Storage И Sync

- нельзя молча терять журналы при local write, mirror или merge flow;
- удаленный узел не должен снимать local fault или переписывать owner-local storage truth без явного policy-contract;
- mirrored files и records обязаны сохранять `origin_node`, `source_owner` или эквивалентную provenance-метку;
- резервный прием файлов на `ESP32 SD` не должен стирать происхождение peer-side content и не должен маскировать, где лежит активный owner-root.

## 7. Нормативные Форматы И Примеры

```json
{
  "schema_version": "sp-registry.v1",
  "registry_entry_id": "profile.irrigation.soil_sensor.default.v1",
  "module_id": "irrigation",
  "component_type": "soil_sensor",
  "profile_id": "soil_sensor.default.v1",
  "status": "simulated",
  "source_surface": "settings.constructor",
  "owner_node_id": "esp32-main",
  "is_default": false,
  "display_name": "Default Soil Sensor"
}
```

```json
{
  "schema_version": "sp-session-record.v1",
  "session_id": "laboratory.session.browser-123",
  "record_type": "note",
  "source_surface": "laboratory",
  "module_id": "turret",
  "component_type": "range_sensor",
  "persisted": false,
  "sync_default": false,
  "text": "Range profile still needs stable power context confirmation."
}
```

```json
{
  "schema_version": "sp-report-entry.v1",
  "report_id": "report.auto_irrigation.2026-05-09T10-15-00Z",
  "action_type": "irrigation_auto_run",
  "owner_node_id": "esp32-main",
  "started_at": "2026-05-09T10:15:00Z",
  "trigger_reason": "soil_moisture_below_threshold",
  "result": "completed",
  "parameter_summary": "Zone 2 watered for 45 s"
}
```

## Open Questions

- какой минимум registry schema нужно фиксировать на уровне человекочитаемого канона
- какой точный `ESP32 SD` wiring/pinout и hardware-confirmation path нужен для storage extension на целевой плате

## TODO

- собрать общую модель данных без распада по stage-docs

## TBD

- итоговая глубина documented JSON examples
