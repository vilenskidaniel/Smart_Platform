# Docs Completeness Migration Plan

Этот документ отвечает на новый вопрос:

- как выжать полезные знания из legacy `ТЗ`;
- не превращать сам `.docx` в вечный второй источник истины;
- довести папку `docs/` до состояния, когда по ней можно собрать полное приложение и все функции проекта через один большой "мегапромпт".

## 1. Главный принцип

Legacy `ТЗ` больше не считаем документом, который нужно "актуализировать".

Правильная роль legacy `ТЗ` теперь такая:

- временный `knowledge donor`;
- источник сценариев, ограничений, инженерных идей и пропущенных пакетов знаний;
- материал для выборочной миграции в текущую owner-aware архитектуру.

Неправильная роль legacy `ТЗ`:

- не главный spec проекта;
- не текущий roadmap;
- не место, где продолжаем проектировать новую платформу.

## 2. Что значит "docs готовы для мегапромпта"

Считаем папку `docs/` достаточной для build-from-docs только если новый чат может собрать рабочую картину проекта без обращения к legacy `ТЗ` и donor-репозиториям.

Для этого в `docs/` должны быть зафиксированы:

- продуктовая модель `v1`;
- owner-aware архитектура и handoff;
- поведение `System Shell`, `Irrigation`, `Turret`, `Gallery`, `Laboratory`;
- hardware и `I/O` границы по каждому узлу;
- storage, sync, reports и content flow;
- installation, onboarding, field operation и service-процедуры;
- safety, risk, interlock и degradation rules;
- acceptance / verification matrix.

Итоговое правило:

- legacy `.docx` можно удалять только после того, как все еще полезные знания либо мигрированы в `docs/`, либо явно помечены как устаревшие и сознательно отброшенные.

## 3. Что из legacy `ТЗ` еще стоит выжать

По текущему состоянию проекта из legacy `ТЗ` полезнее всего вытаскивать не главы как таковые, а `knowledge packets`.

Это в первую очередь:

- пользовательские и операторские сценарии, которые еще не доведены до acceptance-уровня;
- field/onboarding flow: first run, вход в shell, подключение узлов, сервисный вход;
- hardware integration ограничения, которые важны для software ownership, UI, safety и диагностики;
- installation / operation / maintenance практики;
- risk и mitigation логика;
- тестовые и приемочные критерии, которые можно превратить в явную validation matrix.

## 4. Что сознательно не мигрируем

Из legacy `ТЗ` не нужно переносить как норму проекта:

- `Google Home` как фиксированную продуктовую цель;
- `Telegram` как обязательный встроенный канал;
- `EN/RU/HE` как уже зафиксированный localization scope;
- `Видеотека` как каноническое название раздела вместо `Gallery > Media / Reports`;
- `Raspberry Pi` как центральный мозг всей системы;
- жестко зашитые `SQLite`, `EEPROM` и другие implementation choices как догму уровня продукта;
- старые budget / timeline / commercialization формулировки;
- старые placeholder-интеграции, которые противоречат owner-aware модели;
- любые аппаратные утверждения, которые уже конфликтуют с workbook `docs/smart_platform_workshop_inventory.xlsx`.

## 5. Лучшая структура миграции знаний

Полезные остатки legacy `ТЗ` лучше раскладывать не по его старым разделам, а по нынешним пакетам знаний проекта.

Уже существующие целевые слои:

- product / UX truth:
  - `docs/26_v1_product_spec.md`
  - `docs/37_turret_product_context_map.md`
  - `docs/39_design_decisions_and_screen_map.md`
- platform truth:
  - `docs/02_system_architecture.md`
  - `docs/04_sync_and_ownership.md`
  - `docs/11_system_core_spec.md`
  - `docs/29_shared_content_and_sd_strategy.md`
- testing / laboratory truth:
  - `docs/07_testing_strategy.md`
  - `docs/41_laboratory_testing_readiness.md`

Но для полного `build-from-docs` набора сейчас разумнее добавить еще не новые продуктовые модули, а недостающие cross-cutting docs.

Рекомендуемый минимальный набор новых целевых документов:

1. `docs/43_field_onboarding_and_operations.md`
2. `docs/44_esp32_hardware_and_io_map.md`
3. `docs/45_rpi_turret_hardware_and_io_map.md`
4. `docs/46_safety_risk_and_failure_matrix.md`
5. `docs/47_acceptance_and_validation_matrix.md`

Почему именно так:

- не дробим проект на лишние "модули ради модулей";
- не плодим отдельный документ под каждую старую главу;
- закрываем именно те knowledge-gaps, без которых мегапромпт будет каждый раз домысливать важные вещи сам.

Важно:

- `maintenance` и `service procedure` лучше держать внутри `43_field_onboarding_and_operations.md`, а не разносить еще в один отдельный файл без необходимости;
- hardware truth не дублируем с workbook, а добавляем только интеграционные и software-relevant карты;
- safety и risk держим в одном документе с failure matrix, чтобы interlock, degradation и operator warnings не разъезжались по разным заметкам.

## 6. Карта миграции из legacy `ТЗ`

### Разделы 1-5 legacy `ТЗ`

Что делать:

- не переписывать в отдельный новый общий spec;
- добрать только недостающие user stories, operator flows и mode transitions.

Куда мигрировать:

- `docs/03_modes_and_priorities.md`
- `docs/05_ui_shell_and_navigation.md`
- `docs/26_v1_product_spec.md`
- `docs/37_turret_product_context_map.md`
- `docs/39_design_decisions_and_screen_map.md`

### Разделы 6-7 legacy `ТЗ`

Что делать:

- переносить только то, что влияет на wiring boundaries, ownership, power domains, interlocks, service bring-up и UI readiness.

Куда мигрировать:

- `docs/44_esp32_hardware_and_io_map.md`
- `docs/45_rpi_turret_hardware_and_io_map.md`
- `docs/46_safety_risk_and_failure_matrix.md`
- workbook `docs/smart_platform_workshop_inventory.xlsx` только как hardware source of truth

### Раздел 8 legacy `ТЗ`

Что делать:

- вытащить полезные software flows и operator-visible expectations;
- не переносить устаревшие technology commitments как обязательный design.

Куда мигрировать:

- `docs/27_system_shell_v1_spec.md`
- `docs/29_shared_content_and_sd_strategy.md`
- `docs/35_irrigation_v1_software_stage.md`
- `docs/36_turret_v1_software_stage.md`
- `docs/43_field_onboarding_and_operations.md`

### Раздел 9 legacy `ТЗ`

Что делать:

- превратить в traceable validation model, а не оставить в prose-форме.

Куда мигрировать:

- `docs/07_testing_strategy.md`
- `docs/41_laboratory_testing_readiness.md`
- `docs/47_acceptance_and_validation_matrix.md`

### Разделы 10-11 legacy `ТЗ`

Что делать:

- мигрировать как field/onboarding/service knowledge;
- не оставлять это скрытым внутри старого текста.

Куда мигрировать:

- `docs/43_field_onboarding_and_operations.md`
- `docs/46_safety_risk_and_failure_matrix.md`

### Разделы 12-13 legacy `ТЗ`

Что делать:

- в общем случае не переносить;
- брать только то, что реально влияет на procurement risk, hardware dependency или sequencing.

Куда мигрировать при необходимости:

- `docs/08_open_questions.md`
- workbook `docs/smart_platform_workshop_inventory.xlsx`
- `docs/09_master_design_plan.md` только если найдено действительно полезное stage-observation

### Разделы 14-15 legacy `ТЗ`

Что делать:

- риски и mitigation вытаскивать;
- conclusion / общие завершающие формулировки не переносить.

Куда мигрировать:

- `docs/46_safety_risk_and_failure_matrix.md`
- `docs/07_testing_strategy.md`

## 7. Практический порядок работы

### Step 1. Legacy `ТЗ` extraction pass

- проходим legacy `.docx` по секциям;
- каждое наблюдение сразу маркируем как:
  - `keep`
  - `adapt`
  - `ignore`
- не копируем текст блоками, а переводим в короткие engineering conclusions.

### Step 2. Close docs gaps first

- сначала создаем и заполняем missing target docs `43-47`;
- затем обновляем существующие product / platform docs только там, где реально появился новый смысл.

### Step 3. Build the megaprompt pack

После закрытия gaps должна появиться устойчивая стартовая подборка документов для следующего кодового чата:

- `docs/01_product_decisions.md`
- `docs/02_system_architecture.md`
- `docs/04_sync_and_ownership.md`
- `docs/05_ui_shell_and_navigation.md`
- `docs/07_testing_strategy.md`
- `docs/11_system_core_spec.md`
- `docs/26_v1_product_spec.md`
- `docs/29_shared_content_and_sd_strategy.md`
- `docs/37_turret_product_context_map.md`
- `docs/39_design_decisions_and_screen_map.md`
- `docs/41_laboratory_testing_readiness.md`
- `docs/42_docs_completeness_migration_plan.md`
- `docs/43_field_onboarding_and_operations.md`
- `docs/44_esp32_hardware_and_io_map.md`
- `docs/45_rpi_turret_hardware_and_io_map.md`
- `docs/46_safety_risk_and_failure_matrix.md`
- `docs/47_acceptance_and_validation_matrix.md`

Именно этот набор должен со временем заменять legacy `ТЗ` как стартовую точку для реализации.

### Step 4. Delete the legacy `.docx`

Legacy `ТЗ` удаляем только когда:

- полезные знания мигрированы;
- устаревшие знания явно отброшены;
- в `docs/` больше нет скрытых обязательных пробелов, которые объясняются только ссылкой на старый `.docx`.

## 8. Definition Of Done

Эта миграция считается завершенной, когда верны все пункты:

- новый чат может читать только `docs/`, workbook, briefs и skeletons и после этого реализовывать платформу без обращения к legacy `ТЗ`;
- для каждого продуктового блока понятны owner, routes, storage, degradation и reports behavior;
- для каждого критичного hardware family понятны node ownership, `I/O`, power boundary, service entry и emergency behavior;
- acceptance checks и laboratory evidence path оформлены явно;
- оставшиеся неясности лежат в `docs/08_open_questions.md`, а не спрятаны в старом документе.

## 9. Current Extraction Status

После первого extraction pass ситуация такая:

- `docs/43-47` уже получили базовые adapted knowledge packets из legacy `ТЗ`;
- visual и interaction detail layer для shell, `Gallery`, `Laboratory` и blocked-state UX перенесен в `docs/05_ui_shell_and_navigation.md`, `docs/27_system_shell_v1_spec.md` и `docs/39_design_decisions_and_screen_map.md`;
- sections `5-8` legacy файла больше не содержат уникальной архитектурной истины, которую нельзя было бы выразить в текущих owner-aware docs;
- sections `9-11` и `14` в legacy файле оказались в основном placeholder-level и не дают скрытого детализированного spec;
- sections `12-13` полезны только как редкие observations для sequencing или procurement risk, но не как обязательный core spec.

Практический вывод:

- глобальный docs-audit не обнаружил новых уникальных зависимостей на старый текст;
- legacy `.docx` уже удален из рабочего набора, потому что remaining value файла либо мигрирован, либо сознательно признан устаревшим.