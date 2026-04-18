# Acceptance And Validation Matrix

Этот документ нужен, чтобы перевести сценарии и обещания проекта в проверяемую матрицу.

Он должен стать мостом между:

- `docs/07_testing_strategy.md`;
- `docs/41_laboratory_testing_readiness.md`;
- product-level `v1` expectations;
- будущими hardware bring-up сессиями.

## 1. Цель документа

Каждый важный продуктовый или safety сценарий должен иметь:

- понятный `acceptance target`;
- owner и preconditions;
- способ проверки;
- expected evidence;
- место, где результат будет виден пользователю или оператору.

## 2. Основные validation группы

### 2.1 Shell And Handoff

- truthful board visibility;
- honest blocked states;
- owner-aware routing;
- consistent mobile entry.

### 2.2 Irrigation

- zone control;
- environment and soil readings;
- manual irrigation;
- basic automatic behavior;
- local-first operation without peer.

### 2.3 Turret

- manual FPV entry;
- readiness of camera / range / action family;
- degraded behavior when owner dependencies are missing;
- safety and policy enforcement.

### 2.4 Gallery And Reports

- local and mixed content visibility;
- report card generation;
- evidence from `Laboratory` and manual actions;
- owner-aware content degradation.

### 2.5 Laboratory And Bring-Up

- preflight visibility;
- module-by-module qualification;
- experimental profile handling;
- pass / fail / warning evidence.

### 2.6 Safety And Failure Handling

- emergency path;
- interlock reflection;
- fault and locked states;
- safe fallback behavior.

## 3. Test Case Skeleton

Для каждого acceptance item здесь позже нужно фиксировать:

- `case_id`;
- target module or flow;
- required hardware profile;
- preconditions;
- execution steps;
- expected shell behavior;
- expected report/evidence output;
- pass / fail notes.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из legacy `ТЗ` и текущих readiness notes:

- приемочные критерии;
- сценарии проверки продукта глазами пользователя и оператора;
- hardware-assisted validation rules, которые сейчас еще не собраны в единую traceable matrix.

## 5. Базовая Acceptance Matrix Для `v1`

| Case ID | Target | Required Hardware | Preconditions | Expected Shell Behavior | Expected Evidence |
| --- | --- | --- | --- | --- | --- |
| `ACC-SHELL-01` | single-board `ESP32` entry | `ESP32` only | shell reachable | `ESP32` shown as current board, peer shown as absent, peer-owned routes visible but blocked | report or session note for shell smoke |
| `ACC-SHELL-02` | single-board `Raspberry Pi` entry | `Raspberry Pi` only | shell reachable | `Raspberry Pi` shown as current board, `Irrigation` visible but degraded/locked | shell smoke report |
| `ACC-SHELL-03` | dual-board handoff | both boards | peer sync active | peer-owned routes open through owner-aware handoff, not fake local ownership | handoff report |
| `ACC-IRR-01` | irrigation zone visibility | `ESP32` + at least one zone profile | irrigation module online | zones and sensor state visible with honest missing-data markers | irrigation status report |
| `ACC-IRR-02` | manual irrigation action | `ESP32` irrigation path | zone configured, service lock absent | manual action available only through owner, state changes visible in shell | action report |
| `ACC-IRR-03` | irrigation degraded sensing | `ESP32` with missing sensor | one sensor absent or invalid | affected zone remains visible and degraded, not silently removed | warning report |
| `ACC-TUR-01` | manual turret entry | `Raspberry Pi`, camera baseline | local turret shell reachable | manual/FPV entry available with truthful readiness state | manual session report |
| `ACC-TUR-02` | turret degraded readiness | `Raspberry Pi` without one critical family | camera/range/action family partially absent | turret remains visible, unavailable family shown as degraded/locked | readiness report |
| `ACC-GAL-01` | local gallery slice | one board only | local content exists | `Gallery` opens local slice and marks missing peer content | gallery report |
| `ACC-GAL-02` | mixed reports feed | both boards | reports/events exist on one or both nodes | `Gallery > Reports` shows mixed feed with source and result metadata | reports feed evidence |
| `ACC-LAB-01` | laboratory preflight | one or both boards | `Laboratory` reachable | preflight shows what can be tested now and what waits for peer | readiness report |
| `ACC-LAB-02` | experimental profile isolation | `Laboratory` with `HC-SR04` or stepper profile | experimental slice enabled | experimental slice visible as laboratory-only, not product-ready | lab report |
| `ACC-SAFE-01` | interlock reflection | turret-sensitive branch + interlock | interlock engaged | shell and owner module show locked state with explicit reason | safety report |
| `ACC-SAFE-02` | service collision handling | service session active | product command attempted | product command blocked with explicit reason | collision report |

## 6. Validation Execution Rules

Каждый acceptance case должен выполняться так, чтобы осталось понятное evidence trail:

- кто запускал кейс;
- на каком узле выполнялась проверка;
- какие hardware families были подключены;
- какой был итог: pass, fail или warn;
- где смотреть артефакт в `Gallery > Reports` или service-history.

## 7. Minimal Preconditions Vocabulary

Для удобства следующих implementation и testing чатов используем такие precondition-группы:

- `board_reachable`;
- `shell_ready`;
- `peer_visible`;
- `sync_ready`;
- `service_session_inactive`;
- `interlock_clear`;
- `required_family_online`;
- `storage_writable`.

## 8. Что Считается Достаточной Валидацией

Для `v1` validation не обязана сразу быть fully automated.

Но acceptance model считается рабочей только если:

- кейсы можно повторить пошагово;
- они используют одинаковые статусы и причины блокировки, что и shell;
- результат не остается только в устной памяти оператора;
- кейсы покрывают single-board, dual-board, degraded и service-safe состояния.

## 9. Что Реально Взято Из Legacy `ТЗ`

Сохранены как полезные знания:

- продукт нужно проверять именно сценариями, а не только слоем unit tests;
- installation, operation и failure handling должны иметь приемочные критерии;
- ручные и автоматические ветки должны проверяться отдельно.

Не перенесено как обязательный baseline:

- слишком общая prose-формулировка "модульные, интеграционные, системные тесты" без traceable cases;
- старый style acceptance без связи с owner-aware shell и reports model.