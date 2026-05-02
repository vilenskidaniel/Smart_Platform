# Laboratory Testing Readiness

Статус документа:

- supporting readiness-doc, а не primary product truth;
- читать после `docs/50_laboratory_v1_workspace_spec.md`, `docs/51_gallery_v1_content_and_reports_spec.md`, `docs/52_settings_v1_persistent_system_spec.md`, `docs/46_safety_risk_and_failure_matrix.md` и `docs/47_acceptance_and_validation_matrix.md`;
- если readiness-layer расходится с каноническими границами `Laboratory`, `Gallery > Reports` или `Settings`, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

## Назначение

Этот документ фиксирует минимальный coordination-layer для readiness, preflight и bring-up внутри `Laboratory`.

Он не заменяет:

- общую testing-strategy из `docs/07_testing_strategy.md`;
- deep-spec границ между `Laboratory`, `Gallery > Reports` и `Settings` из документов `50-52`;
- safety и acceptance truth из `docs/46_safety_risk_and_failure_matrix.md` и `docs/47_acceptance_and_validation_matrix.md`.

Здесь фиксируем только тот coordination-gap, без которого реальные board-by-board проходы быстро превращаются в ad-hoc operator memory:

- явную предварительную проверку внутри `Laboratory`;
- канонический порядок bring-up;
- owner-aware blocked visibility;
- session/evidence continuity внутри `Laboratory`;
- handoff подтвержденных результатов в `Settings` без смешивания с user-facing history.

## What We Need Before Smooth Hardware Testing

1. A visible preflight state inside `Laboratory`.
2. A canonical bring-up order for `shared`, `ESP32`, and `Raspberry Pi` steps.
3. Honest visibility for blocked peer-owned slices.
4. Persistent session evidence inside `Laboratory` itself.
5. A way to grow into testcase pass/fail recording without rebuilding the shell again.
6. A stable path for experimental modules such as `HC-SR04`-class range sensors and stepper drives.
7. A visible manual power context for bench-sensitive slices such as strobe qualification.
8. Usable behavior both in normal phone-browser mode and in fullscreen app-like mode.
9. A clear handoff from confirmed laboratory results into `Settings`.

## Minimum Bring-Up Order

1. Shell and readiness smoke.
2. Peer link and owner handoff.
3. `ESP32 / Strobe Bench`.
4. `ESP32 / Irrigation Service`.
5. `Raspberry Pi / Turret Service`.
6. `Laboratory / Experimental Profiles` (`HC-SR04`-class range, stepper drives).
7. `Laboratory` session review before the next testcase bundle.

## Smartphone Entry Flow

Before deeper hardware testing begins, the phone browser path should already be usable in three states:

1. `ESP32` only.
2. `Raspberry Pi` only.
3. both boards connected.

### Home page expectations

- the upper shell bar should immediately show board presence, not only generic shell text;
- the operator should be able to tell whether the current view is single-board or dual-board;
- the peer board must stay visible even when absent;
- blocked peer-owned routes must stay honest instead of looking clickable and failing later.

### Laboratory expectations

- entering `Laboratory` should preserve board visibility from the shell header;
- the operator should still know which board currently owns the active slice;
- the screen should show what can be tested now and what is still waiting for the second board;
- category-first navigation should keep the phone IA readable even when the second-level slices stay technical;
- experimental slices such as `HC-SR04`-class ranging and stepper drives should stay visible as `Laboratory`-only, not pretend to be product-ready turret controls;
- Raspberry Pi display testing should live in its own `Displays` slice and stay visibly blocked from `ESP32`-only sessions until the owner board is present;
- the operator should be able to declare whether the current session uses `Bench PSU` or `LiFePO4 battery` before voltage-sensitive bring-up;
- browser mode and fullscreen mode should both preserve owner/status visibility while changing layout density;
- this is where interface pain points and desired control density can be collected during real bring-up.

## Device Entry Baseline Today

Right now a board enters the system through the transport and shell path below:

1. the board brings up its own shell URL;
2. the local shell marks its own `wifi_ready`, `shell_ready`, and `sync_ready` state;
3. if the peer board exists, sync starts sending heartbeat and module state;
4. the current shell applies the peer snapshot and updates owner-aware routes;
5. `Home` and `Laboratory` show board presence in the top ribbon instead of hiding the missing peer.

For the current baseline, we should treat a board as "entered the system" only when all of these are true:

- its shell page opens in the phone browser;
- the upper device ribbon shows the board identity;
- the ribbon shows truthful `wifi / shell / sync` state;
- the shell does not pretend peer-owned routes are local;
- `Laboratory` keeps the same board visibility after navigation from `Home`.

## Registration And Onboarding Gap

This part must stay explicit before real bench testing starts:

- we already have transport-level node identity and sync registration;
- we do not yet have a full user-facing onboarding wizard;
- we do not yet have the old donor `login -> Wi-Fi setup -> normal mode` flow reworked for the new shell;
- we intentionally did not migrate the legacy cookie/auth flow as-is.

So for the first physical passes, "device registration" means:

- the shell is reachable;
- the node is visible in the top ribbon;
- peer presence is reflected through heartbeat/snapshot state.

It does not yet mean:

- guided first-run onboarding;
- captive setup wizard;
- persistent user-facing device registry page.

## Donor Strengths We Keep

Legacy desktop files were stronger than the current baseline in four practical areas:

1. explicit connection status instead of vague readiness language;
2. session lifecycle visibility;
3. recommended next action after connection;
4. persistent operator trace.

We adapt those strengths into the web shell like this:

- connection visibility becomes top-bar board chips on `Home` and `Laboratory`;
- recommended next action becomes `Laboratory` readiness;
- persistent operator/session trace continues to move into the `Laboratory` session bundle.

This order is intentionally board-aware:

- `ESP32` owned slices should not be tested through a pretending peer shell;
- `Raspberry Pi` turret work should not hide emergency/fault/interlock state;
- session review should happen between bundles, not only at the end of the whole bench session.

## Readiness Baseline Added In This Step

- `GET /api/v1/laboratory/readiness`
- Raspberry Pi `Laboratory` overview now shows:
  - overall readiness;
  - preflight checklist;
  - bring-up sequence with current status;
  - next recommended action.
- the bring-up sequence now includes a direct `Raspberry Pi / Displays` step with deep link to `Laboratory / Displays`.

## Session And Evidence Baseline Added In This Step

- Raspberry Pi now exposes a small laboratory session contract:
  - `GET /api/v1/laboratory/session`
  - `POST /api/v1/laboratory/session/context`
  - `POST /api/v1/laboratory/session/start`
  - `POST /api/v1/laboratory/session/update`
  - `POST /api/v1/laboratory/session/finish`
  - `POST /api/v1/laboratory/event`
- `POST /api/v1/laboratory/event` по умолчанию создает запись только внутри laboratory session/evidence слоя и не должен сам по себе превращаться в `Gallery > Reports` entry без явного product-level export;
- shared `Laboratory` hub now includes a visible `Session Backbone` block above the category rail flow;
- the operator can record `pass`, `warn`, `fail`, and note entries from the active slice without leaving the hub;
- the display page now records explicit display-lab evidence instead of keeping everything only in a local page log;
- session entries carry laboratory context fields such as session id, operator, objective, hardware profile, external module, power context, view mode, and active slice;
- mirrored shells can keep a local draft session if Raspberry Pi backend session API is not available, while preserving the same laboratory metadata model;
- `Gallery > Reports` is not the default sink for these engineering records; it remains reserved for short user-facing history of real system actions.

## Smartphone Smoke Checklist

Use this exact order for the first physical browser passes.

### Pass 1. `ESP32` only

- Open `ESP32` shell on the phone.
- Confirm `Home` shows `1 / 2 boards connected`.
- Confirm the top ribbon shows `ESP32` as current shell and `Raspberry Pi` as missing peer.
- Confirm the ribbon exposes `wifi / shell / sync` values instead of only a generic online badge.
- Enter `Laboratory`.
- Set the visible power context before opening a bench-sensitive slice.
- Confirm `ESP32` local slices remain available.
- Confirm peer-owned slices stay visibly blocked instead of failing after tap.
- Confirm the `Displays` slice stays blocked because `Raspberry Pi` is absent.
- Switch between browser mode and fullscreen mode and confirm the category/module navigation still stays readable.
- Record every unclear label, missing status, or mobile layout pain point into the session notes.

### Pass 2. `Raspberry Pi` only

- Open `Raspberry Pi` shell on the phone.
- Confirm `Home` shows `1 / 2 boards connected`.
- Confirm the top ribbon shows `Raspberry Pi` as current shell and `ESP32` as missing peer.
- Enter `Laboratory`.
- Confirm readiness explains what can be tested now and what still waits for the peer board.
- Confirm local turret-side pages stay reachable without pretending `ESP32` ownership.
- Open `Displays` and run at least one color pattern plus touch-grid pass on the Raspberry Pi screen.
- Switch between browser mode and fullscreen mode and confirm shell status, category rail, and active slice remain visible.
- Record missing explanations, crowded controls, and any status that feels too engineering-heavy for the phone shell.

### Pass 3. both boards connected

- Open one shell first and confirm `2 / 2 boards connected`.
- Confirm both board chips show truthful `wifi / shell / sync` state.
- Confirm peer-owned routes now switch from blocked to owner-aware handoff.
- Enter `Laboratory` and confirm the same board visibility is preserved.
- Open at least one peer-owned slice through the shell contract and confirm the handoff feels intentional rather than browser-like.
- Confirm browser mode and fullscreen mode both preserve the same owner and power context semantics.
- End the pass by reviewing the `Laboratory` session bundle and checking that the recorded evidence is visible without leaving the workspace.

### Evidence To Capture During Each Pass

- which board was connected;
- which shell URL was opened;
- who the operator was for this pass;
- what the current objective and hardware profile were;
- whether an external or third-party module participated in the pass;
- what the top ribbon showed;
- whether `Home -> Laboratory` preserved board context;
- which power context was selected for the session;
- whether browser and fullscreen modes changed density without losing context;
- which slice or deep page produced the evidence;
- which case id or session action was used for the explicit laboratory entry;
- which controls felt missing, redundant, or too dense for the phone;
- which step felt confusing enough that we should later turn it into explicit UI guidance.

## Practical Hardware Checklist For The First Real Pass

This section is intentionally more concrete than the higher-level smoke list above.

Use it when a real phone and a real `8-inch` Raspberry Pi panel are already on the bench.

### Card A. Phone Browser Pass

Before starting:

- note the phone model;
- note the browser and version if it matters;
- note portrait or landscape orientation;
- note whether the pass begins from `ESP32`, `Raspberry Pi`, or dual-board state.

Run this order:

1. open the current shell URL on the phone;
2. confirm the top ribbon is readable without zooming;
3. confirm the current board and missing peer are understandable at a glance;
4. open `Home -> Laboratory` and confirm board context is preserved;
5. switch one time between normal browser mode and fullscreen mode;
6. open one available slice and one blocked slice;
7. record whether the blocked slice explains itself clearly enough for a non-author operator.

Mark the pass as:

- `pass` if the shell stays readable, owner context is obvious, and blocked slices explain themselves;
- `warn` if the path works but labels, chips, density, or fullscreen behavior feel confusing;
- `fail` if the operator loses board context, cannot tell who owns the active slice, or blocked pages look broken instead of intentionally blocked.

### Card B. `8-inch` Raspberry Pi Display Pass

Preconditions:

- `Raspberry Pi` is the current owner shell;
- the panel is connected through `HDMI` and `USB touch`;
- the operator can open `Laboratory / Displays`.

Run this order:

1. open `Laboratory -> Displays -> Raspberry Pi Touch Display`;
2. verify the page opens without losing shell or owner context;
3. run `white`, `black`, `red`, `green`, `blue`, and `grayscale` patterns;
4. run `checker` and `grid` patterns for geometry and scaling;
5. check the four edges and four corners for clipping, dead zones, or obvious distortion;
6. complete the `12-zone` touch grid;
7. repeat at least one visual pattern and one touch check in fullscreen mode;
8. return to browser mode and note whether density, readability, or touch comfort changed.

Mark the pass as:

- `pass` if patterns look correct, touch reaches all zones, and fullscreen does not break the workflow;
- `warn` if the page works but there is drift, edge discomfort, dense layout, or visible scaling compromise;
- `fail` if touch misses zones, geometry is clearly wrong, or the operator loses practical control in one of the two view modes.

### Card C. Evidence Bundle To Save In The Laboratory Session Right After The Pass

Capture at least these facts:

- date and operator;
- which board state was active: `ESP32 only`, `Raspberry Pi only`, or dual-board;
- phone model and browser;
- whether the pass used browser mode only or both browser and fullscreen;
- active laboratory session id if one was started;
- objective, hardware profile, and external module label if they mattered for the bench setup;
- selected power context;
- result for phone pass: `pass`, `warn`, or `fail`;
- result for display pass: `pass`, `warn`, or `fail`;
- short list of concrete issues, not only general impressions.

If the pass also created useful media artifacts, they may later be attached through `Gallery > Media`, but the engineering result itself should stay anchored to the `Laboratory` session record.

Recommended short wording for operator notes:

- `context:` which board and which screen was used;
- `worked:` what stayed clear and usable;
- `friction:` what felt slow, unclear, too dense, or misleading;
- `result:` `pass`, `warn`, or `fail`;
- `next change:` one concrete UI or readiness improvement.

## Near-Term Improvement Plan For `laboratory_readiness.py`

The current readiness layer already gives honest system state.

The most useful recent improvements are already in place:

- readiness copy is now shorter and easier to scan on a phone;
- readiness now has an explicit `Raspberry Pi / Displays` step.

The next useful improvements should focus on operator clarity beyond that, not on adding more abstract status prose.

### Current `/service` Implementation Note

The old `/service` hub template has been replaced by a single `Laboratory`
workspace. The page now treats `Laboratory` as the primary engineering surface,
not as a launcher for several unrelated service pages.

Current behavior to preserve:

- top-level category rail and second-level slice rail switch in-page without a
  full reload;
- `Session Backbone`, readiness, and evidence controls remain visible around
  the active slice;
- `Turret Service Lane` is available as `/service?tool=turret_service` and
  carries the useful runtime mode, interlock, subsystem, flag, scenario, and
  JSON/log inspection controls that previously lived in the old turret service
  template;
- `Raspberry Pi Touch Display` is available as
  `/service?tool=rpi_touch_display` and carries the useful pattern bench,
  fullscreen pattern, touch-grid, and evidence controls from the display
  service template;
- peer-owned slices stay visible and blocked until the owner/peer state allows
  handoff; the local shell must not fake ownership;
- experimental slices such as `HC-SR04`, `Stepper Motor / Drives`, motion wake,
  custom module intake, and audio/voice profiles are visible as skeletons but
  remain explicitly laboratory-local until a review/apply path promotes them.

Legacy routes `/service/turret` and `/service/displays` can stay temporarily for
compatibility, but new work should target the unified `/service` workspace first.

### Step 1. Reflect phone/browser context in readiness output

- add a lightweight notion of `browser` versus `fullscreen` pass state;
- surface whether the operator already reviewed both modes;
- keep this as session guidance, not as fake hardware truth.

### Step 2. Add evidence-oriented next actions

- let `next_action` point not only to the next route, but also to the expected evidence bundle;
- make it easier to move from a completed pass into `Laboratory` session review and, only when relevant, into explicit media attachment or settings promotion;
- keep the action phrasing short enough for in-UI chips or compact cards.

### Step 3. Split local-only and dual-board operator guidance more cleanly

- keep the current owner-aware logic;
- make single-board advice explicitly different from dual-board advice;
- avoid one generic text block trying to cover all three states at once.

## Still Missing After This Step

- equivalent backend session contract on direct `ESP32` shell instead of local-draft fallback only;
- UI-level regression tests for shared `Laboratory` hub and dedicated display page behavior;
- richer review helpers on top of the current feed, for example saved filter presets or quick bundle summaries.

## Recommended Next Focus

The next most useful step after baseline testcase capture, operator notes, and first filters is the review layer directly above them:

- quick review of recent pass/fail/warn entries between hardware bundles;
- later, export-oriented report bundles without replacing the current feed model.
