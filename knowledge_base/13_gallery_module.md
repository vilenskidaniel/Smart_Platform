# 13. Gallery Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Gallery` как общего обозревателя контента и product-level истории.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный активный канон для `Gallery`; историческое состояние переноса держим в `knowledge_base/17_open_questions_and_migration.md`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/gallery_prompt.md` остается prompt-layer companion source для рабочего режима чата.

## Установленные Истины

- `Gallery` — shared virtual section
- `Reports` — только автономно и системно зафиксированные product-level события
- laboratory session notes не поднимаются сюда автоматически

## Канон

### 1. Роль И Пользовательский Итог

`Gallery` - это общий пользовательский обозреватель сохраняемого контента и продуктовой истории платформы.

Для пользователя `Gallery` должен давать такой итог:

- один понятный вход ко всему пользовательскому контенту;
- честное объединение локального и peer-owned content без потери source truth;
- три ясных семейства: `Plants`, `Media`, `Reports`;
- быстрый просмотр продуктовой истории без смешения со следом `Laboratory`-сессии;
- работоспособность даже в одноузловом режиме.

`Gallery` не является:

- обозревателем сырых storage-путей;
- заменой diagnostics surface типа `Content Storage`;
- обозревателем полного дампа серверных журналов;
- рабочим пространством `Laboratory` session notes.

### 2. Вкладки: Plants, Media, Reports

Канонический route:

- `/gallery`

Канонические верхнеуровневые вкладки:

1. `Plants`
2. `Media`
3. `Reports`

Текущая реализация уже материализует эти вкладки на gallery-страницах и `Raspberry Pi`, и `ESP32`, поэтому они должны считаться активной модульной истиной, а не только следом старой donor-спецификации.

`Plants`:

- curated plant library;
- plant care profiles;
- descriptive notes;
- basis for irrigation-related recommendations and future garden scenarios.

`Media`:

- camera captures;
- operator-created photos and videos;
- plant photos;
- turret-related media;
- visual reference materials for `Laboratory` such as component photos and wiring diagrams.

Минимальные подгруппы `Media v1`:

- `Videos`
- `Pictures`

`Reports`:

- короткая хронологическая лента продуктовых действий и итогов;
- reason/trigger/result semantics;
- optional attached artifact if the event really produced media or text output.

`Reports` читаются как быстрый пользовательский обзор, а не как инженерная консоль.

### 3. Provenance, Mirroring And Source Visibility

`Gallery` является общим виртуальным разделом на уровне страницы, но каждый объект контента сохраняет правдивые метаданные источника и хранения.

Это означает:

- локальный срез и срез другого узла могут сосуществовать в одном обозревателе;
- интерфейс может показывать объединенный вид без притворства, что владелец локален;
- owner/source metadata обязательны для media entries и reports entries;
- peer-missing state не должен маскироваться под пустой локальный state.

Текущий baseline зеркального хранения:

- пользовательский content-path материализуется через общее дерево под корнем `/gallery`;
- зеркальный контент существует в текущем baseline и на `ESP32`, и на `Raspberry Pi`;
- тяжелый контент живет на `ESP32 SD` и в локальном хранилище `Raspberry Pi`, а не зависит только от `LittleFS`;
- both sides should understand the same logical content roots.

Storage-layer truth должна поддерживать viewer, но пользовательская `Gallery` не должна схлопываться в storage diagnostics.

### 4. Reports Model

`Reports` - это краткая пользовательская история автономно и системно зафиксированных product-level событий.

Минимальные report entry types `v1`:

- automatic or scheduled irrigation action result;
- turret defense, emergency, or policy-driven action result;
- safety/interlock or other system constraint result;
- autonomously triggered sensor-check result;
- system-recorded media capture when it is part of a product event.

Обязательные поля `Reports`:

- `action_type`
- `owner_node_id`
- `started_at`
- `trigger_reason`
- `result`
- `parameter_summary`, если применимо

Допустимые дополнительные поля:

- `entry_type`
- `source_surface`
- `source_mode`
- `related_action_id`
- attached artifact metadata
- short duration, если она действительно полезна пользователю

По умолчанию в `Reports` не должны попадать:

- `Laboratory` console lines;
- intermediate calibration notes;
- state-table comparisons;
- every engineering step from `Laboratory`;
- local operator notes and session notes;
- save/apply events from `Laboratory` into `Settings`.

Если событие не имеет product-level смысла для user history, его место остается в `Laboratory` session layer or internal logs.

Report browsing rules:

- default reading order остается `action -> time -> reason/trigger -> result`;
- filtering inside `Reports` допустим по event family/type, но не должен ломать понятность хронологии;
- search, sort and mixed local/peer browsing могут существовать как implementation layer, если source markers и owner truth остаются видимыми;
- mixed local and peer content must not collapse into a fake single-source feed.

### 5. Plants И Media Как Семейства Контента

`Plants` и `Media` должны ощущаться как разные семейства контента, а не как один плоский список файлов.

`Plants` должны читаться как curated knowledge library.

`Media` должны читаться как смешанный слой capture- и reference-материалов:

- photo and video artifacts from product surfaces;
- turret- and irrigation-related captures when they exist;
- laboratory reference media used by component cards;
- будущий media-browsing без потери видимости источника.

Important boundary:

- `Gallery > Media` может служить reference-media layer для `Laboratory`;
- это не делает `Gallery` engineering console;
- `Laboratory` uses these references, but retains its own session workflow.

### 6. Поведение При Degraded И Peer-Missing Состоянии

Если peer owner недоступен:

- `Gallery` не скрывается;
- local slice остается доступным;
- missing source groups are marked explicitly and calmly;
- interface does not pretend peer-owned content is available.

Правда degraded-состояния для `Gallery`:

- user still sees the same three tabs;
- source availability markers explain why some content groups are absent;
- no fake empty state that erases the distinction between `peer missing` and `no local content`.

### 7. Связи С Laboratory, Settings И Shell

Связь с `Laboratory`:

- `Gallery` provides reference photos, wiring diagrams, and optional media artifacts;
- `Laboratory` does not have a direct export path into `Reports`;
- useful media created during work may later appear in `Media`, but session notes remain in `Laboratory`.

Связь с `Settings`:

- `Settings` may expose storage roots, cleanup tools, and persistent content preferences;
- `Settings` must not replace `Gallery` as the user-facing content viewer.

Связь с shell:

- `Gallery` is a top-level shell section;
- it remains visible and reachable in single-node and dual-node topologies;
- source truth and owner metadata stay consistent with shell snapshot and mirrored storage state.

Граница с diagnostics:

- `GET /api/v1/content/status` and similar storage diagnostics remain service-level tools;
- they support readiness and path operations, but are not the primary user-facing `Gallery` surface.

Требования к адаптивности:

- `Gallery` должен одинаково честно работать на телефоне и на desktop-screen, меняя density rather than page meaning;
- `Plants` and `Media` keep a library-like browsing feel, while `Reports` stays a quick chronological review surface;
- peer-missing or source-missing states must read as calm degraded truth, not as a broken page.

### 7.1 Реальные Кодовые Опоры Текущего Слоя

Чтобы `Gallery` не читался как чистая IA-абстракция, ниже фиксируем текущие implementation anchors:

- `host_runtime/web/gallery.html` - owner-side gallery page на `Raspberry Pi`;
- `io_firmware/data/gallery/index.html` - mirror gallery page на стороне `ESP32`;
- `host_runtime/report_feed.py` - строит normalized `Reports` snapshot из platform events и stored entries;
- `host_runtime/turret_capture_store.py` - current media artifact metadata path для gallery-facing captures;
- `host_runtime/server.py` - HTTP-вход, который отдает report/gallery data, включая `/api/v1/reports`;
- `host_runtime/tests/test_report_feed.py` - tests normalization и filtering для `Reports` feed.

### 8. Проверочные Критерии

Минимальные проверочные критерии текущего этапа:

1. `/gallery` exists on both current shells and exposes `Plants`, `Media`, `Reports`;
2. gallery remains available when one peer owner is missing;
3. local and peer source visibility are distinguishable;
4. `Reports` feed reads as action -> time -> reason/trigger -> result;
5. `Laboratory` session notes do not auto-promote into `Reports`;
6. `Content Storage` diagnostics do not replace the user-facing gallery surface;
7. `Plants` and `Media` feel like content families, not raw storage dumps.

### 9. Нормативные Примеры И Форматы

Нормативные route examples:

- gallery page: `/gallery`
- diagnostics API (not primary viewer): `/api/v1/content/status`

Пример report entry:

```json
{
  "action_type": "turret_strobe",
  "owner_node_id": "rpi",
  "started_at": "2026-05-09T14:22:00Z",
  "trigger_reason": "target_detected",
  "result": "completed",
  "parameter_summary": "duration=1.2s intensity=high"
}
```

Пример media entry:

```json
{
  "entry_type": "photo",
  "owner_node_id": "rpi",
  "source_surface": "manual_fpv",
  "path": "/gallery/media/2026/05/manual_capture_001.jpg",
  "artifact_kind": "image",
  "created_at": "2026-05-09T14:24:10Z"
}
```

Пример gallery tabs contract:

```json
{
  "default_tab": "reports",
  "tabs": ["plants", "media", "reports"]
}
```

## Open Questions

- какая глубина gallery browsing нужна для неинженерного пользователя уже в активном слое
- какая часть будущей модели review и filtering должна оставаться в активном каноне, а какая может жить только в implementation detail

## TODO

- после стабилизации active draft переаудировать gallery migration-state в ledger и оставить там только исторически полезные implementation/detail reminders
- позже разнести остаток storage-specific detail между `knowledge_base/07` и `knowledge_base/15`

## TBD

- будущие curated content collections и advanced preview rules
