# Laboratory Testing Readiness

## Purpose

This note captures the minimum readiness layer we need before sequential hardware bring-up starts.

It is not a replacement for the broader testing strategy in `docs/07_testing_strategy.md`.
It is the coordination layer that keeps real board-by-board testing repeatable instead of turning
into ad-hoc operator memory.

## Current Position

### Product target

- `Laboratory` should guide bring-up, not only host separate module pages.
- each hardware test session should start from explicit preflight visibility;
- the operator should know which board/module to connect next;
- `Gallery > Reports` should collect the evidence of each pass, fail, and warning.

### Software baseline

- `Laboratory` already acts as an owner-aware workspace;
- `Gallery > Reports` already exists as a persistent baseline on Raspberry Pi;
- there was no explicit readiness/preflight layer before this step.

## What We Need Before Smooth Hardware Testing

1. A visible preflight state inside `Laboratory`.
2. A canonical bring-up order for `shared`, `ESP32`, and `Raspberry Pi` steps.
3. Honest visibility for blocked peer-owned slices.
4. Persistent session evidence in `Gallery > Reports`.
5. A way to grow into testcase pass/fail recording without rebuilding the shell again.

## Minimum Bring-Up Order

1. Shell and reports smoke.
2. Peer link and owner handoff.
3. `ESP32 / Strobe Bench`.
4. `ESP32 / Irrigation Service`.
5. `Raspberry Pi / Turret Service`.
6. `Gallery > Reports` review before the next testcase bundle.

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
- persistent operator/session trace continues to move into `Gallery > Reports`.

This order is intentionally board-aware:

- `ESP32` owned slices should not be tested through a pretending peer shell;
- `Raspberry Pi` turret work should not hide emergency/fault/interlock state;
- reports review should happen between bundles, not only at the end of the whole bench session.

## Readiness Baseline Added In This Step

- `GET /api/v1/laboratory/readiness`
- Raspberry Pi `Laboratory` overview now shows:
  - overall readiness;
  - preflight checklist;
  - bring-up sequence with current status;
  - next recommended action.

## Smartphone Smoke Checklist

Use this exact order for the first physical browser passes.

### Pass 1. `ESP32` only

- Open `ESP32` shell on the phone.
- Confirm `Home` shows `1 / 2 boards connected`.
- Confirm the top ribbon shows `ESP32` as current shell and `Raspberry Pi` as missing peer.
- Confirm the ribbon exposes `wifi / shell / sync` values instead of only a generic online badge.
- Enter `Laboratory`.
- Confirm `ESP32` local slices remain available.
- Confirm peer-owned slices stay visibly blocked instead of failing after tap.
- Record every unclear label, missing status, or mobile layout pain point into the session notes.

### Pass 2. `Raspberry Pi` only

- Open `Raspberry Pi` shell on the phone.
- Confirm `Home` shows `1 / 2 boards connected`.
- Confirm the top ribbon shows `Raspberry Pi` as current shell and `ESP32` as missing peer.
- Enter `Laboratory`.
- Confirm readiness explains what can be tested now and what still waits for the peer board.
- Confirm local turret-side pages stay reachable without pretending `ESP32` ownership.
- Record missing explanations, crowded controls, and any status that feels too engineering-heavy for the phone shell.

### Pass 3. both boards connected

- Open one shell first and confirm `2 / 2 boards connected`.
- Confirm both board chips show truthful `wifi / shell / sync` state.
- Confirm peer-owned routes now switch from blocked to owner-aware handoff.
- Enter `Laboratory` and confirm the same board visibility is preserved.
- Open at least one peer-owned slice through the shell contract and confirm the handoff feels intentional rather than browser-like.
- End the pass by opening `Gallery > Reports` and checking that the session evidence is visible for review.

### Evidence To Capture During Each Pass

- which board was connected;
- which shell URL was opened;
- what the top ribbon showed;
- whether `Home -> Laboratory` preserved board context;
- which controls felt missing, redundant, or too dense for the phone;
- which step felt confusing enough that we should later turn it into explicit UI guidance.

## Still Missing After This Step

- equivalent readiness summary on direct `ESP32` shell when Raspberry Pi is absent.
- richer review helpers on top of the current feed, for example saved filter presets or quick bundle summaries.

## Recommended Next Focus

The next most useful step after baseline testcase capture, operator notes, and first filters is the review layer directly above them:

- quick review of recent pass/fail/warn entries between hardware bundles;
- later, export-oriented report bundles without replacing the current feed model.
