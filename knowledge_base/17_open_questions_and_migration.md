# 17. Open Questions And Migration Ledger

## Роль Файла

Этот файл должен быть историческим appendix для перехода от donor-слоя к активному канону, а не второй рабочей точкой истины.

## Статус

- текущий статус: `historical appendix`
- физический donor-layer `docs/` уже удален из репозитория; этот ledger теперь хранит историческую карту переноса и правила против возврата legacy path dependencies
- бывший summary-layer с отдельными брифами уже упразднен: уникальный смысл должен жить в `knowledge_base/` и `chat_prompts/`, а не в отдельной второй точке входа

## Как Использовать Этот Файл

- этот файл нужен только для historical migration status, donor-id coverage и anti-regression rules;
- active product/system truth живет в `knowledge_base/01-16`, `chat_prompts/`, `shared_contracts/` и workflow-файлах;
- если historical appendix расходится с active canon, сильнее всегда становится active canon.

## Historical Coverage Snapshot

Ниже сохранена компактная карта того, куда ушел смысл удаленного donor-layer. Это historical coverage snapshot, а не текущий operational backlog.

| Historical donor ids | Where the meaning lives now | Historical note | Status |
| --- | --- | --- | --- |
| `26_v1_product_spec`, `01_product_decisions`, `02_system_architecture`, `03_modes_and_priorities`, `04_sync_and_ownership`, `07_testing_strategy`, `46_safety_risk_and_failure_matrix`, `47_acceptance_and_validation_matrix` | `knowledge_base/01_project_scope_and_goals.md`, `knowledge_base/02_system_terms_and_design_rules.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md`, `knowledge_base/16_hardware_component_profiles.md` | Product boundaries, state vocabulary, arbitration, sync defaults, risk и acceptance language уже сведены в active canon. | `historical-only` |
| `30_top_down_architecture_map`, `10_repository_layout`, `27_platform_shell_v1_spec`, `31_platform_shell_class_map`, `32_current_shell_role_mapping`, `40_platform_shell_navigation_alignment`, `48_browser_entry_and_host_launch`, `49_shell_runtime_and_chat_guardrails` | `knowledge_base/03_platform_architecture_and_module_relationships.md`, `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/09_repository_layout_and_code_map.md`, `knowledge_base/15_platform_services_and_shared_content.md`, `WORKFLOW_FOR_OTHER_CHATS.md`, `chat_prompts/foundation_prompt.md` | Shell role mapping, routing, repository map и browser/runtime guardrails уже переписаны в active files. | `historical-only` |
| `05_ui_shell_and_navigation`, `39_design_decisions_and_screen_map`, `53_shared_ui_state_and_interaction_contract` | `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/06_shared_ui_contract.md`, `knowledge_base/11_turret_module.md`, `knowledge_base/12_laboratory_module.md`, `knowledge_base/13_gallery_module.md`, `knowledge_base/14_settings_module.md` | Shared UI language, fullscreen/bar behavior и page-facing layout semantics уже живут в active canon. | `historical-only` |
| `29_shared_content_and_sd_strategy`, `11_system_core_spec`, `21_platform_log_and_turret_scenarios`, `22_shared_log_sync_stage`, `33_shell_snapshot_schema` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/07_data_registry_storage_and_persistence.md`, `knowledge_base/15_platform_services_and_shared_content.md`, `shared_contracts/shell_snapshot_contract.md` | Shared content, shell snapshot, platform log и sync continuity сохранены в active contracts и service canon. | `historical-only` |
| `15_irrigation_module_stage`, `35_irrigation_v1_software_stage` | `knowledge_base/10_irrigation_module.md`, `knowledge_base/16_hardware_component_profiles.md` | Dry-run baseline, safe-output default и owner-side irrigation contract теперь держатся модульным и hardware canon; build/test residue осталось историческим. | `historical-only` |
| `18_rpi_turret_bridge_bootstrap`, `19_rpi_turret_runtime_stage`, `20_turret_event_log_and_driver_shell`, `36_turret_v1_software_stage`, `37_turret_product_context_map`, `38_turret_audio_briefing` | `knowledge_base/11_turret_module.md`, `knowledge_base/15_platform_services_and_shared_content.md`, `knowledge_base/16_hardware_component_profiles.md` | Turret runtime, event-log boundary, FPV/product semantics и audio closure reminders уже captured in active turret and hardware canon. | `historical-only` |
| `50_laboratory_v1_workspace_spec`, `41_laboratory_testing_readiness`, `13_strobe_bench_service_profile` | `knowledge_base/12_laboratory_module.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md` | Laboratory workspace structure, readiness order и `strobe_bench` engineering contour уже живут в active canon. | `historical-only` |
| `51_gallery_v1_content_and_reports_spec`, `52_settings_v1_persistent_system_spec` | `knowledge_base/13_gallery_module.md`, `knowledge_base/14_settings_module.md`, `knowledge_base/06_shared_ui_contract.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `Reports`, storage/viewer caveats, settings persistence и promotion semantics уже переписаны в active module docs. | `historical-only` |
| `44_esp32_hardware_and_io_map`, `45_rpi_turret_hardware_and_io_map`, `12_esp32_shell_bootstrap`, `14_shell_littlefs_stage`, `16_sync_bootstrap_stage` | `knowledge_base/16_hardware_component_profiles.md`, `knowledge_base/09_repository_layout_and_code_map.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/15_platform_services_and_shared_content.md` | Board-family maps, bootstrap baselines, `LittleFS/SD` reminders и sync bring-up notes сохранены только как historical hardware/bootstrap context. | `historical-only` |
| `06_migration_plan`, `08_open_questions`, `09_master_design_plan`, `17_project_audit`, `28_legacy_migration_map`, `34_modular_chat_transition_plan`, `42_docs_completeness_migration_plan`, `43_field_onboarding_and_operations` | `knowledge_base/17_open_questions_and_migration.md`, `knowledge_base/09_repository_layout_and_code_map.md`, `chat_prompts/README.md`, `WORKFLOW_FOR_OTHER_CHATS.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md` | Migration governance, audit residue и onboarding reminders сведены к этому appendix и active workflow files. | `historical-only` |

## Preserved Historical Notes

### 1. Historical Audit Residue

- early audit уже подтверждал базовую траекторию: `ESP32` удерживал local/fallback and always-on role, а `Raspberry Pi` шел в turret-owner compute path;
- software-stage snapshots для irrigation и turret зафиксировали успешные `raspberry_pi` unit-test passes (`12`, затем `14` tests) и успешные `ESP32` `pio run` / `buildfs` сборки при ориентировочно `22%` RAM и `71%` Flash usage;
- dry-run и simulated placeholders считаются допустимыми только пока они явно маркированы, а не выданы за готовую product truth;
- слабая auth-модель, embedded secrets, ownership-blind monoliths и старые runtime assumptions вида `one board owns everything forever` считаются non-transferable residue.

### 2. Post-Deletion Safety Checks

Считать удаление legacy donor layer безопасно завершенным можно потому, что:

- новый чат может стартовать из `knowledge_base/`, `chat_prompts/`, `WORKFLOW_FOR_OTHER_CHATS.md` и `shared_contracts/` без обязательного чтения donor-files;
- active repo files больше не требуют `docs/`, `docs/archive/` или `briefs/` как reading-order dependency или authority contract;
- повторный reference audit не находит живых `docs/` path dependencies вне исторических заметок этого appendix;
- активный companion source для hardware truth живет по пути `knowledge_base/resources/smart_platform_workshop_inventory.xlsx`.

## Preventive Rules

1. Не возвращать `docs/`, `docs/archive/` и `briefs/` path references в active files.
2. При конфликте между prompt-layer и `knowledge_base/` чинить active canon, а не оживлять historical donor sources.
3. Новый документ допустим только если он закрывает уникальный knowledge gap, который нельзя встроить в existing active canon.
4. Если понадобится archival snapshot удаленного donor-layer, хранить его вне active repo.
5. После каждого крупного documentation cleanup-pass делать узкий reference audit на возврат donor-vocabulary и старых path dependencies.

## Current Status After Legacy Donor Removal

- physical donor layer удален из репозитория, включая `docs/archive/` и старый путь `docs/smart_platform_workshop_inventory.xlsx`;
- `briefs/` как отдельный summary-layer тоже удален из active repo;
- active reading path теперь стартует из `knowledge_base/`, `chat_prompts/`, `WORKFLOW_FOR_OTHER_CHATS.md` и `shared_contracts/`;
- этот файл больше не должен разрастаться в operational backlog и должен оставаться historical appendix.

## TODO

- удерживать migration ledger в donor-id форме и не возвращать path-based legacy references в active files
- при правках active docs перепроверять, что ссылки ведут только в текущий layout репозитория и на актуальные companion sources
- после крупных documentation cleanup-pass делать узкий reference audit на возврат `docs/`-путей

## TBD

- нужен ли отдельный внешний archival snapshot удаленного donor-layer после того, как semantic deletion readiness уже достигнута
