# Smart Platform Donor Docs Map

Этот файл больше не является канонической точкой входа в активный слой документации.

Новый активный слой теперь живет в `knowledge_base/README.md`.

Папка `docs/` считается donor-only слоем:

- ее нужно читать как старый архив смысла и переходных решений;
- перенос из нее идет по модели `вырезать из донора -> вставить в новый канон`;
- старые файлы больше не считаются primary truth для нового чата;
- если в donor-файле есть уникальная инженерная истина, она должна быть перенесена в `knowledge_base/`, а donor-файл после этого истончен или помечен как historical.

Важно:

- эта папка пока физически не удаляется, потому что остается рабочим донором для миграции;
- старые reading orders и stage-maps ниже полезны только как подсказки для переноса;
- новый чат не должен начинать работу отсюда как с живого канона.

## 1. Как устроена документация

Папка `docs/` должна читаться слоями.

### Layer A. Canonical Core

Это верхний слой истины, который задает:

- цель продукта;
- словарь терминов;
- структуру приложения;
- роли разделов;
- общую архитектуру;
- модель данных и сохранения;
- safety и acceptance.

Этот слой должен быть достаточным, чтобы новый чат быстро понял систему целиком и не начал придумывать собственную архитектуру с нуля.

### Layer B. Deep Product And Module Specs

Это не "дополнительные заметки", а подробные документы по крупным блокам системы:

- `Laboratory`;
- `Settings`;
- `Gallery`;
- `Irrigation`;
- `Turret`;
- `Power` и другим системным ролям.

Здесь должна жить глубокая детализация сценариев, экранов, карточек, статусов, таблиц, полей, ограничений и связей между разделами.

### Layer C. Platform Maps And Supporting Truth

Это слой, который не должен подменять собой product docs, но остается обязательным для корректной реализации:

- repository layout;
- ownership и sync;
- storage/content maps;
- shell schemas;
- hardware/I-O maps;
- field/onboarding/operations;
- safety/failure matrix;
- acceptance matrix.

### Layer D. Stage And Migration Docs

Это переходный слой.

Его можно сокращать или архивировать только после того, как:

- полезная истина явно перенесена в Layer A-C;
- из нового reading order не выпадает ни один важный сценарий;
- новый чат больше не нуждается в этих stage-документах для восстановления логики проекта.

Если уникальная польза stage-doc уже сведена к historical snapshot, такой файл переносим в `docs/archive/`,
а на старом пути при необходимости оставляем короткий compatibility-stub.

## 1.1. Карта первичных источников

Чтобы папка `docs/` не разрасталась в набор равноправных дублей, для каждого крупного вопроса фиксируем основной источник истины.

### Product Scope And Vocabulary

- primary: `26_v1_product_spec.md`
- supporting: `01_product_decisions.md`, `39_design_decisions_and_screen_map.md`

### Shared UI State And Interaction

- primary: `53_shared_ui_state_and_interaction_contract.md`
- supporting: `39_design_decisions_and_screen_map.md`, `40_platform_shell_navigation_alignment.md`, `50_laboratory_v1_workspace_spec.md`, `52_settings_v1_persistent_system_spec.md`

### Shell And Navigation

- primary: `05_ui_shell_and_navigation.md`
- supporting: `40_platform_shell_navigation_alignment.md`, `27_platform_shell_v1_spec.md`

### Laboratory Workspace

- primary: `50_laboratory_v1_workspace_spec.md`
- supporting: `41_laboratory_testing_readiness.md`, `46_safety_risk_and_failure_matrix.md`, `47_acceptance_and_validation_matrix.md`

### Gallery And Reports

- primary: `51_gallery_v1_content_and_reports_spec.md`
- supporting: `29_shared_content_and_sd_strategy.md`, `39_design_decisions_and_screen_map.md`

### Settings And Save Flows

- primary: `52_settings_v1_persistent_system_spec.md`
- supporting: `29_shared_content_and_sd_strategy.md`, `40_platform_shell_navigation_alignment.md`

### Safety, Validation, Field And Hardware Truth

- primary: `46_safety_risk_and_failure_matrix.md`, `47_acceptance_and_validation_matrix.md`
- supporting: `43_field_onboarding_and_operations.md`, `44_esp32_hardware_and_io_map.md`, `45_rpi_turret_hardware_and_io_map.md`

Из этого следуют жесткие правила:

- если вопрос уже закрыт primary doc, supporting и stage-docs не должны переписывать эту истину как второй канон;
- если supporting-doc начинает определять продуктовый словарь вместо primary doc, это сигнал на cleanup-pass;
- stage-doc может хранить переходную или implementation-specific детализацию, но не должен становиться скрытым обязательным входом в продуктовую модель.

## 2. Главный принцип переделки

Мы не "схлопываем docs до маленького набора".

Мы строим:

1. канонический вход в документацию;
2. ясный порядок чтения;
3. глубокие модульные документы без скрытых пробелов;
4. явные supporting maps;
5. controlled migration старых stage-docs.

Если при переписывании оказывается, что новый короткий документ теряет важную детализацию, значит:

- либо детализацию нужно оставить в отдельном deep-doc;
- либо новый документ еще не готов быть каноническим.

## 3. Рекомендуемый Reading Order Для Полного Нового Чата

Если чат должен понять систему целиком и работать не только по одному модулю, читать так:

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [01_product_decisions.md](./01_product_decisions.md)
3. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
4. [02_system_architecture.md](./02_system_architecture.md)
5. [04_sync_and_ownership.md](./04_sync_and_ownership.md)
6. [10_repository_layout.md](./10_repository_layout.md)
7. [29_shared_content_and_sd_strategy.md](./29_shared_content_and_sd_strategy.md)
8. [39_design_decisions_and_screen_map.md](./39_design_decisions_and_screen_map.md)
9. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
10. [50_laboratory_v1_workspace_spec.md](./50_laboratory_v1_workspace_spec.md)
11. [51_gallery_v1_content_and_reports_spec.md](./51_gallery_v1_content_and_reports_spec.md)
12. [52_settings_v1_persistent_system_spec.md](./52_settings_v1_persistent_system_spec.md)
13. [43_field_onboarding_and_operations.md](./43_field_onboarding_and_operations.md)
14. [44_esp32_hardware_and_io_map.md](./44_esp32_hardware_and_io_map.md)
15. [45_rpi_turret_hardware_and_io_map.md](./45_rpi_turret_hardware_and_io_map.md)
16. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
17. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

После этого уже читать конкретные deep-docs по нужному модулю.

## 4. Рекомендуемый Reading Order По Задаче

### Если чат работает с `Laboratory`

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [39_design_decisions_and_screen_map.md](./39_design_decisions_and_screen_map.md)
4. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
5. [50_laboratory_v1_workspace_spec.md](./50_laboratory_v1_workspace_spec.md)
6. [41_laboratory_testing_readiness.md](./41_laboratory_testing_readiness.md)
7. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
8. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

### Если чат работает с `Turret`

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [37_turret_product_context_map.md](./37_turret_product_context_map.md)
4. [39_design_decisions_and_screen_map.md](./39_design_decisions_and_screen_map.md)
5. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
6. [45_rpi_turret_hardware_and_io_map.md](./45_rpi_turret_hardware_and_io_map.md)
7. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
8. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

### Если чат работает с `Irrigation`

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
4. [04_sync_and_ownership.md](./04_sync_and_ownership.md)
5. [44_esp32_hardware_and_io_map.md](./44_esp32_hardware_and_io_map.md)
6. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
7. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

### Если чат работает с `Gallery`

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [29_shared_content_and_sd_strategy.md](./29_shared_content_and_sd_strategy.md)
4. [39_design_decisions_and_screen_map.md](./39_design_decisions_and_screen_map.md)
5. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
6. [51_gallery_v1_content_and_reports_spec.md](./51_gallery_v1_content_and_reports_spec.md)
7. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
8. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

### Если чат работает с `Settings`

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [40_platform_shell_navigation_alignment.md](./40_platform_shell_navigation_alignment.md)
4. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
5. [52_settings_v1_persistent_system_spec.md](./52_settings_v1_persistent_system_spec.md)
6. [29_shared_content_and_sd_strategy.md](./29_shared_content_and_sd_strategy.md)
7. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)
8. [47_acceptance_and_validation_matrix.md](./47_acceptance_and_validation_matrix.md)

### Если чат работает с data model или save flows

1. [26_v1_product_spec.md](./26_v1_product_spec.md)
2. [05_ui_shell_and_navigation.md](./05_ui_shell_and_navigation.md)
3. [29_shared_content_and_sd_strategy.md](./29_shared_content_and_sd_strategy.md)
4. [53_shared_ui_state_and_interaction_contract.md](./53_shared_ui_state_and_interaction_contract.md)
5. [50_laboratory_v1_workspace_spec.md](./50_laboratory_v1_workspace_spec.md)
6. [51_gallery_v1_content_and_reports_spec.md](./51_gallery_v1_content_and_reports_spec.md)
7. [52_settings_v1_persistent_system_spec.md](./52_settings_v1_persistent_system_spec.md)
8. [46_safety_risk_and_failure_matrix.md](./46_safety_risk_and_failure_matrix.md)

## 5. Правила Для Дальнейшей Переписи Docs

1. Сначала переносим смысл, потом упрощаем структуру.
2. Короткий канонический документ обязан ссылаться на deep-doc, если без него теряется важная детализация.
3. Нельзя удалять stage-doc только потому, что он старый по номеру или неудобен по форме.
4. Если истина уже стабильна, она должна жить не в stage-doc, а в canonical core или deep product spec.
5. Если deep-doc остается единственным местом, где описан важный сценарий, это нормальная временная стадия, а не дефект.
6. Конечная цель не минимальное число файлов, а самодостаточная и понятная структура.

## 5.1. Cleanup Gate После Появления Канонического Набора

После появления `docs/README.md` и deep-docs `50-52` базовым режимом работы считаем cleanup, а не расширение структуры.

Это означает:

1. Новый документ добавляем только если без него появляется реальный knowledge-gap.
2. Если смысл уже устойчиво описан в primary doc, в supporting/stage-doc оставляем ссылку, а не повторный пересказ.
3. Если stage-doc по-прежнему нужен, он должен быть нужен из-за уникальной переходной пользы, а не потому что канонический слой еще не договорил важную вещь.
4. Если stage-doc больше не нужен новому чату для восстановления логики, он становится кандидатом на архивирование или сильное сокращение.

Архивный слой для уже выведенных из активного reading order snapshot-файлов живет в `docs/archive/README.md`.

## 6. Definition Of Done Для Папки `docs/`

Считаем документацию достаточно зрелой только когда верно все:

- новый чат начинает с этого файла и дальше имеет понятный reading order;
- нет скрытой обязательной зависимости от старых переписок, donor-repos или удаленного legacy `.docx`;
- верхний канонический слой не противоречит deep-docs;
- deep-docs не зависят от догадок и не оставляют критичные пробелы;
- stage-docs либо уже мигрированы, либо явно помечены как временные источники переходного знания.
