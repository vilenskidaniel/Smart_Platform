# 13. Gallery Module

## Роль Файла

Этот файл должен стать новым каноническим описанием `Gallery` как общего обозревателя контента и product-level истории.

## Статус

- текущий статус: `active draft`
- этот файл задает новый модульный active canon для `Gallery`; donor docs ниже остаются detail and storage residue

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/gallery_prompt.md` остается active companion source для module wording and scope discipline.

## Settled Truths

- `Gallery` — shared virtual section
- `Reports` — только автономно и системно зафиксированные product-level события
- laboratory session notes не поднимаются сюда автоматически

## Canon

### 1. Роль И Пользовательский Итог

`Gallery` - это общий пользовательский обозреватель сохраняемого контента и product-level истории платформы.

Для пользователя `Gallery` должен давать такой итог:

- один понятный вход ко всему user-facing content;
- честное объединение локального и peer-owned content без потери source truth;
- три ясных семейства: `Plants`, `Media`, `Reports`;
- быстрый просмотр product-level истории без смешения с `Laboratory` session trail;
- работоспособность даже в одноузловом режиме.

`Gallery` не является:

- raw storage browser;
- заменой diagnostics surface типа `Content Storage`;
- viewer для полного дампа server logs;
- рабочим пространством `Laboratory` session notes.

### 2. Tabs: Plants, Media, Reports

Канонический route:

- `/gallery`

Канонические верхнеуровневые вкладки:

1. `Plants`
2. `Media`
3. `Reports`

Current implementation already materializes these tabs on both `Raspberry Pi` and `ESP32` gallery pages, so они должны считаться active module truth, а не только donor-spec aspiration.

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

- short chronological feed of product-level actions and outcomes;
- reason/trigger/result semantics;
- optional attached artifact if the event really produced media or text output.

### 3. Provenance, Mirroring And Source Visibility

`Gallery` является shared virtual section на уровне страницы, но каждый content object сохраняет truthful source and storage metadata.

Это означает:

- local slice и peer slice могут сосуществовать в одном viewer;
- interface может показывать combined view without pretending the owner is local;
- owner/source metadata обязательны для media entries и reports entries;
- peer-missing state не должен маскироваться под пустой local state.

Current mirrored-storage baseline:

- user-facing content path materializes through shared tree rooted under `/gallery`;
- mirrored content exists on both `ESP32` and `Raspberry Pi` baselines;
- heavy content lives on `ESP32 SD` and `Raspberry Pi` local storage rather than depending on `LittleFS` alone;
- both sides should understand the same logical content roots.

Storage-layer truth must support the viewer, but user-facing `Gallery` must not collapse into storage diagnostics.

### 4. Reports Model

`Reports` - это краткая user-facing history автономно и системно зафиксированных product-level событий.

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

### 5. Plants And Media As Shared Content Families

`Plants` и `Media` должны ощущаться как разные content families, а не как один flat file list.

`Plants` должны читаться как curated knowledge library.

`Media` должны читаться как mixed capture/reference layer:

- photo and video artifacts from product surfaces;
- turret- and irrigation-related captures when they exist;
- laboratory reference media used by component cards;
- future media browsing without losing source visibility.

Important boundary:

- `Gallery > Media` может служить reference-media layer для `Laboratory`;
- это не делает `Gallery` engineering console;
- `Laboratory` uses these references, but retains its own session workflow.

### 6. Degraded And Peer-Missing Behavior

Если peer owner недоступен:

- `Gallery` не скрывается;
- local slice остается доступным;
- missing source groups are marked explicitly and calmly;
- interface does not pretend peer-owned content is available.

Degraded truth for `Gallery`:

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

Boundary with diagnostics:

- `GET /api/v1/content/status` and similar storage diagnostics remain service-level tools;
- they support readiness and path operations, but are not the primary user-facing `Gallery` surface.

Responsive expectations:

- `Gallery` должен одинаково честно работать на телефоне и на desktop-screen, меняя density rather than page meaning;
- `Plants` and `Media` keep a library-like browsing feel, while `Reports` stays a quick chronological review surface;
- peer-missing or source-missing states must read as calm degraded truth, not as a broken page.

### 8. Acceptance Hooks

Минимальные acceptance hooks текущего этапа:

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
- какая часть future review and filtering model должна оставаться в active canon, а какая может жить только в implementation detail

## TODO

- после стабилизации active draft переаудировать gallery donor residue в migration ledger и оставить только implementation/detail reminders without active authority role
- позже разнести остаток storage-specific detail между `knowledge_base/07` и `knowledge_base/15`

## TBD

- будущие curated content collections и advanced preview rules
