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
