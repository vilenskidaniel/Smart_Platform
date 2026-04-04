# Raspberry Pi Content Root

Здесь хранится зеркальная копия тяжелого контента платформы.

Обязательные каталоги:

- `assets/`
- `audio/`
- `animations/`
- `libraries/`
- `gallery/`

Это не shell-код и не легкие fallback-страницы.
Этот каталог предназначен для:

- изображений;
- аудио;
- анимаций;
- крупных библиотек состояний растений;
- сценариев полива и опрыскивания;
- gallery-артефактов, которые потом открываются через user-facing `Gallery`;
- report-entry артефактов для `Gallery > Reports`, включая историю действий из `Laboratory` и ручных режимов;
- других растущих наборов данных.

На `ESP32` этому каталогу соответствует структура на `SD` карте.

Reference libraries, которые уже добавлены на этом этапе:

- `libraries/plant_profiles.v1.json`
- `libraries/plant_state_rules.v1.json`
- `libraries/care_scenarios.v1.json`

Current `Gallery > Reports` baseline archive on `Raspberry Pi`:

- `gallery/reports/report_feed.jsonl`

This is the current persistent archive of normalized report entries.
It keeps the user-facing `Reports` feed alive across restarts before richer
report bundles and export packages are introduced.

The same archive now also receives minimal typed testcase results recorded
through `POST /api/v1/reports/testcase`, so first hardware smoke passes can
immediately leave pass/fail/warn evidence in `Gallery > Reports`.

Typed operator notes recorded through `POST /api/v1/reports/note` now land in
the same archive as `entry_type = operator_note`, so short human observations
stay next to testcase results instead of drifting into separate scratch notes.
