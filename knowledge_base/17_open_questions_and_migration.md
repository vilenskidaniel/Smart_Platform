# 17. Open Questions And Migration Ledger

## Роль Файла

Этот файл должен быть рабочим журналом перехода от donor-слоя к новому активному канону.

## Статус

- текущий статус: `active draft`

## Правило Работы

Для каждого donor-файла фиксировать:

1. куда переносится его смысл;
2. что уже перенесено;
3. что остается уникальным;
4. когда старый файл можно истончить, сократить или вывести в historical-only слой.

## Migration Ledger Template

| Donor id | Active target | Status | Unique value left in donor | Next thinning step |
| --- | --- | --- | --- | --- |
| `26_v1_product_spec` | `knowledge_base/01_project_scope_and_goals.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | browser-first scenarios, `v1` boundaries, degradation language и distinction between product canon and temporary implementation profile уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `01_product_decisions` | `knowledge_base/01_project_scope_and_goals.md`, `knowledge_base/02_system_terms_and_design_rules.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md`, `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | energy baseline, command arbitration order, hybrid `strobe` role и access-transition reminders уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `02_system_architecture` | `knowledge_base/02_system_terms_and_design_rules.md`, `knowledge_base/03_platform_architecture_and_module_relationships.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md`, `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | board-centric inventory, wake model, command invariant и legacy state vocabulary note уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `03_modes_and_priorities` | `knowledge_base/02_system_terms_and_design_rules.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | compatibility mode wording, command arbitration order и strobe-sensitive override reminder уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `04_sync_and_ownership` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md` | `stub-ready-for-deletion` | sync domains, conflict defaults, transport baseline и role-alias compatibility note уже сведены в active sync canon | удалить stub вместе с остальным legacy donor layer |
| `30_top_down_architecture_map` | `knowledge_base/03_platform_architecture_and_module_relationships.md`, `knowledge_base/09_repository_layout_and_code_map.md` | `stub-ready-for-deletion` | current class surfaces, target skeleton names и skeleton entrypoints уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `05_ui_shell_and_navigation` | `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/06_shared_ui_contract.md`, `knowledge_base/11_turret_module.md`, `knowledge_base/12_laboratory_module.md`, `knowledge_base/13_gallery_module.md`, `knowledge_base/14_settings_module.md` | `stub-ready-for-deletion` | shell/home/bar/fullscreen/theme и module-facing screen detail уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `07_testing_strategy` | `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | turret runtime automated checks и hardware qualification buckets уже сведены в active acceptance canon | удалить stub вместе с остальным legacy donor layer |
| `09_master_design_plan` | `knowledge_base/03_platform_architecture_and_module_relationships.md`, `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | historical roadmap ordering, docs anti-bloat rules и modular-transition context уже сведены в active canon or historical active reference | удалить stub вместе с остальным legacy donor layer |
| `39_design_decisions_and_screen_map` | `knowledge_base/05_shell_navigation_and_screen_map.md`, `knowledge_base/08_safety_acceptance_and_field_operations.md`, `knowledge_base/11_turret_module.md`, `knowledge_base/12_laboratory_module.md`, `knowledge_base/13_gallery_module.md`, `knowledge_base/14_settings_module.md` | `stub-ready-for-deletion` | operator-HUD/interlock semantics и page-specific layout baseline уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `53_shared_ui_state_and_interaction_contract` | `knowledge_base/06_shared_ui_contract.md` | `stub-ready-for-deletion` | scale corridors, cleanup targets и helper-convergence reminders уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `29_shared_content_and_sd_strategy` | `knowledge_base/07_data_registry_storage_and_persistence.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `stub-ready-for-deletion` | `LittleFS/SD` split, diagnostics boundary и unresolved backend-gap notes уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `46_safety_risk_and_failure_matrix` | `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | risk-family catalog, owner-specific safety reminders и minimum failure-record shape уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `47_acceptance_and_validation_matrix` | `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | validation execution rules, case-family prefixes и precondition vocabulary уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `10_repository_layout` | `knowledge_base/09_repository_layout_and_code_map.md` | `stub-ready-for-deletion` | target-layout detail, code ownership rules и anti-duplication constraints уже сведены в active repository canon | удалить stub вместе с остальным legacy donor layer |
| `15_irrigation_module_stage` | `knowledge_base/10_irrigation_module.md`, `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | bootstrap dry-run baseline, safe-output default и hardware-confirmation constraints уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `35_irrigation_v1_software_stage` | `knowledge_base/10_irrigation_module.md`, `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | `/irrigation`, auto/dry-run baseline и laboratory compatibility semantics уже сведены в active canon; historical build/test snapshot сохранен в section `8.1` | удалить stub вместе с остальным legacy donor layer |
| `36_turret_v1_software_stage` | `knowledge_base/11_turret_module.md`, `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | `/turret`, runtime summaries и readiness/action gating semantics уже сведены в active canon; historical build/test snapshot сохранен в section `8.1` | удалить stub вместе с остальным legacy donor layer |
| `37_turret_product_context_map` | `knowledge_base/11_turret_module.md`, `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | manual FPV layout baseline, current hardware/action context и alert/recovery semantics уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `50_laboratory_v1_workspace_spec` | `knowledge_base/12_laboratory_module.md`, `knowledge_base/13_gallery_module.md`, `knowledge_base/14_settings_module.md` | `stub-ready-for-deletion` | card skeleton, session-note rules и `Save to Settings` promotion path уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `41_laboratory_testing_readiness` | `knowledge_base/08_safety_acceptance_and_field_operations.md`, `knowledge_base/12_laboratory_module.md` | `stub-ready-for-deletion` | bring-up order, phone/display practical passes и session-context semantics уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `51_gallery_v1_content_and_reports_spec` | `knowledge_base/13_gallery_module.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `stub-ready-for-deletion` | report fields, browsing/filter rules, diagnostics boundary и responsive expectations уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `52_settings_v1_persistent_system_spec` | `knowledge_base/06_shared_ui_contract.md`, `knowledge_base/14_settings_module.md` | `stub-ready-for-deletion` | page tone, host/viewer storage caveats, `Laboratory` promotion semantics и keyboard/apply rules уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `11_system_core_spec` | `knowledge_base/15_platform_services_and_shared_content.md`, `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/02_system_terms_and_design_rules.md` | `stub-ready-for-deletion` | `ESP32` startup baseline и historical bring-up boundary notes уже сведены в active canon or historical active reference | удалить stub вместе с остальным legacy donor layer |
| `44_esp32_hardware_and_io_map` | `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | `ESP32` board-family map, power boundaries, engineering closure rules и open electrical questions уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `45_rpi_turret_hardware_and_io_map` | `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | `Raspberry Pi` board-family map, power/interlock boundaries, readiness families и open electrical questions уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |

## Skeleton

### 1. Global Open Questions

- как глубоко переносить board-specific implementation details в активный человеческий слой, чтобы не засорить его кодоцентричным narrative
- какой минимальный documented registry/index standard нужен прямо в `knowledge_base/07_data_registry_storage_and_persistence.md`

### 2. Module-Level Open Questions

- `Irrigation`: как описать controller profile как временный, не размыв при этом текущий working baseline
- `Turret`: как зафиксировать controller profile и owner-sensitive behavior без возвращения к жесткой привязке модуля к одной плате

### 3. Migration Matrix: Legacy Donor Layer -> `knowledge_base/`

- ключевой cross-module конфликт уже зафиксирован: модуль не должен быть равен текущей плате-контроллеру
- все будущие переносы по `Irrigation`, `Turret`, `Topology`, `Hardware` и `Settings` должны сверяться с этой поправкой

### 4. Prompt Sync Checklist

- `foundation_prompt.md`: переключен на `knowledge_base/` как active canon
- `cross_module_prompt.md`: читает `knowledge_base/` раньше donor-слоя
- модульные prompt-файлы `Laboratory`, `Gallery`, `Settings`, `Irrigation`, `Turret`, `Platform Shell`: перепривязаны к новому active reading path
- controller-profile correction для `Irrigation` и `Turret`: уже зафиксирован в prompt-слое

### 5. Donor Files Ready For Thinning

- `29_shared_content_and_sd_strategy`

### 6. Donor Files Ready For Archive

- `archive/24_federated_owner_routing_stage` остается historical snapshot и не требует возврата в active layer
- `archive/25_federated_handoff_stage` остается historical snapshot и не требует возврата в active layer

### 7. Risks Of Semantic Drift

- active authority для shell snapshot уже закреплен в `shared_contracts/shell_snapshot_contract.md`, а `33_shell_snapshot_schema` сведен к compatibility stub
- shell-supporting donor cluster уже истончен; remaining deletion risk теперь смещен из shell snapshot authority в unresolved donor rows и final donor-map cleanup
- hardware closure truth теперь должна читаться из `knowledge_base/16_hardware_component_profiles.md` и workshop inventory spreadsheet, а не из donor files `01_product_decisions`, `02_system_architecture`, `44_esp32_hardware_and_io_map`, `45_rpi_turret_hardware_and_io_map`
- shell/shared-UI cluster, deep-spec module UI donors и recent bootstrap/runtime/storage/readiness/validation/safety/product donors `15/26/29/35/36/37/41/46/47` уже сведены к compatibility stubs; remaining deletion risk больше не сидит в одном крупном donor-файле и смещается в final re-audit remaining `thinned` rows main ledger

### 8.1 Historical Audit Residue

- early audit уже подтверждал, что архитектурная линия не расползалась хаотично: `ESP32` удерживал fallback/local role, `Raspberry Pi` шел в turret-owner role, а build-проверки на bootstrap-stage продолжали проходить;
- полезный historical debt snapshot этого этапа: docs lagged behind code, `Raspberry Pi` temporarily trailed `ESP32`, sync был только bootstrap, а общий reusable web layer еще не был собран;
- software-stage snapshots `35_irrigation_v1_software_stage` и `36_turret_v1_software_stage` зафиксировали успешные `raspberry_pi` unit-test passes (`12`, затем `14` tests) и успешные `ESP32` `pio run` / `buildfs` сборки при ориентировочно `22%` RAM и `71%` Flash usage;
- dry-run и simulated placeholders считаются честным допустимым состоянием только пока они явно маркированы, а не выданы за готовую product truth.
- donor-репозитории, legacy office specs и старые source maps считаются только selective knowledge donors и не должны оставаться обязательными workspace dependencies после selective migration;
- при аудите legacy material нужно держать три фильтра: verified knowledge сохранить, useful patterns адаптировать, ownership-blind/secret-bearing/monolithic implementation не переносить как есть;
- слабая auth-модель, embedded secrets, монолитные entrypoints и старые runtime assumptions, где одна плата притворяется вечным owner всего продукта, считаются явно non-transferable residue;
- historical closed questions полезны только как краткая closure history после того, как тот же смысл уже закреплен в active canon `knowledge_base/01-16`.

Historical documentation-governance reminders, которые все еще нужны для zero-loss cleanup:

- цель зрелости docs — не минимальное число файлов, а плотный active reading path без скрытой истины в donor-layer;
- новый документ допустим только если он закрывает уникальный knowledge gap, который нельзя аккуратно встроить в existing active canon;
- supporting/stage docs не должны пересказывать уже стабилизированную product truth как равноправный источник;
- при конфликте между active canon и supporting/stage residue исправляется residue, а не размножается параллельная формулировка;
- если roadmap снова начинает описываться через внутренние слои вместо user-facing blocks, это считается симптомом architectural overgrowth и поводом вернуться к product-level canon.

### 8.2 Deletion Readiness Gates

Считать удаление legacy donor layer безопасным можно только если одновременно выполнены такие условия:

- новый чат может стартовать из `knowledge_base/`, `chat_prompts/`, `WORKFLOW_FOR_OTHER_CHATS.md` и `shared_contracts/` без обязательного чтения конкретных donor files;
- для каждого крупного вопроса есть один active primary file, а donor detail остается только historical residue и не нужен как reading-path authority;
- `supporting-ref` donor либо сведен к краткой useful note в active layer, либо признан expendable without data loss;
- active repo files больше не требуют specific donor paths или legacy folder names как текущий reading order, authority contract или coordination entry.

### 8. Unique Residue Action Plan

1. Сначала закрыть dual-authority зоны и supporting-doc hierarchy для shell detail.
2. Затем дозаполнить ledger для unmapped donor docs и разделить их на `archive`, `supporting-ref` и `retained residue`.
3. После этого точечно переносить уникальные residue-кластеры: hardware closure -> `16`, testing and field operations -> `08`, module UI detail -> `10-14`.
4. Только после явного mapping и residue-plan принимать решение, какие legacy donor artifacts физически удаляются, а какие сводятся к archive-only residue.

### 9. Remaining Top-Level Donor Coverage For Full Legacy Donor Removal

Ниже зафиксированы top-level donor artifacts, которые еще не были явно отражены в основном migration ledger, но должны быть закрыты до полного удаления legacy donor layer.

| Donor id | Active target / residue location | Status | Unique value left in donor | Next thinning step |
| --- | --- | --- | --- | --- |
| `06_migration_plan` | `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | migration rules уже сведены в section `8.1`, donor сведен к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `08_open_questions` | `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | closure logic уже сведена в section `8.1`, donor сведен к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `12_esp32_shell_bootstrap` | `legacy archive stub: 12_esp32_shell_bootstrap` | `stub-ready-for-deletion` | уникального смысла уже нет, остался compatibility stub | после перепривязки ссылок удалить stub вместе с legacy archive residue |
| `13_strobe_bench_service_profile` | `knowledge_base/12_laboratory_module.md` | `stub-ready-for-deletion` | `strobe_bench` laboratory reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `14_shell_littlefs_stage` | `knowledge_base/09_repository_layout_and_code_map.md` | `stub-ready-for-deletion` | `LittleFS`-first shell serving reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `16_sync_bootstrap_stage` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md` | `stub-ready-for-deletion` | sync-bootstrap reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `17_project_audit` | `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | early audit baseline reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `18_rpi_turret_bridge_bootstrap` | `legacy archive stub: 18_rpi_turret_bridge_bootstrap` | `stub-ready-for-deletion` | уникального смысла уже нет, остался compatibility stub | после перепривязки ссылок удалить stub вместе с legacy archive residue |
| `19_rpi_turret_runtime_stage` | `knowledge_base/11_turret_module.md` | `stub-ready-for-deletion` | turret runtime-stage reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `20_turret_event_log_and_driver_shell` | `knowledge_base/11_turret_module.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `stub-ready-for-deletion` | turret event-log separation reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `21_platform_log_and_turret_scenarios` | `knowledge_base/12_laboratory_module.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `stub-ready-for-deletion` | laboratory scenario-pack and platform-log reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `22_shared_log_sync_stage` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/15_platform_services_and_shared_content.md` | `stub-ready-for-deletion` | shared-log sync reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `27_platform_shell_v1_spec` | `knowledge_base/05_shell_navigation_and_screen_map.md` | `stub-ready-for-deletion` | implementation-only shell-obligation wording уже сведено к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `28_legacy_migration_map` | `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | selective migration categories уже сведены в section `8.1`, donor сведен к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `31_platform_shell_class_map` | `knowledge_base/15_platform_services_and_shared_content.md`, `knowledge_base/09_repository_layout_and_code_map.md` | `stub-ready-for-deletion` | shell service-role names и adapter-thinning reminders уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |
| `32_current_shell_role_mapping` | `knowledge_base/09_repository_layout_and_code_map.md` | `stub-ready-for-deletion` | safe refactor order и monolith-pressure reminder уже сведены в active code-map canon | удалить stub вместе с остальным legacy donor layer |
| `33_shell_snapshot_schema` | `shared_contracts/shell_snapshot_contract.md` | `stub-ready-for-deletion` | active authority уже закреплен в `shared_contracts/`, donor сведен к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `34_modular_chat_transition_plan` | `knowledge_base/09_repository_layout_and_code_map.md`, `chat_prompts/README.md`, `WORKFLOW_FOR_OTHER_CHATS.md` | `stub-ready-for-deletion` | modular chat transition reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `38_turret_audio_briefing` | `knowledge_base/11_turret_module.md`, `knowledge_base/16_hardware_component_profiles.md` | `stub-ready-for-deletion` | turret audio closure reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `40_platform_shell_navigation_alignment` | `knowledge_base/05_shell_navigation_and_screen_map.md` | `stub-ready-for-deletion` | canonical shell language и `Home / bar` alignment уже сведены в active shell canon | удалить stub вместе с остальным legacy donor layer |
| `42_docs_completeness_migration_plan` | `knowledge_base/17_open_questions_and_migration.md` | `stub-ready-for-deletion` | docs-completeness reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `43_field_onboarding_and_operations` | `knowledge_base/08_safety_acceptance_and_field_operations.md` | `stub-ready-for-deletion` | field-onboarding helper reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `48_browser_entry_and_host_launch` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/05_shell_navigation_and_screen_map.md` | `stub-ready-for-deletion` | browser-entry helper reminder уже сведён к compatibility stub | удалить stub вместе с остальным legacy donor layer |
| `49_shell_runtime_and_chat_guardrails` | `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/05_shell_navigation_and_screen_map.md`, `WORKFLOW_FOR_OTHER_CHATS.md`, `chat_prompts/foundation_prompt.md` | `stub-ready-for-deletion` | runtime-truth distinctions и workflow/browser guardrails уже сведены в active canon | удалить stub вместе с остальным legacy donor layer |

### 10. Current Blockers Before Full Legacy Donor Deletion

- direct legacy path blockers, governance residue и historical-only donor subcluster уже закрыты; основной migration ledger больше не содержит `thinned` rows с явным residue left in donor
- финальный reference audit не нашел active `docs/` path dependencies вне самого donor-layer: ссылки на `docs/` остались только внутри `docs/` и не участвуют в active reading path
- shell/shared-UI donor cluster, deep-spec product/module donors, runtime/bootstrap residue, detailed testing residue, priority/safety residue, governance residue и historical-only reminder cluster уже сведены к compatibility stubs; с точки зрения active knowledge перенос смысла завершен
- оставшееся решение теперь не semantic, а operational: удалять ли `docs/` сразу целиком или сначала сохранить внешний historical snapshot donor-layer для археологии

## TODO

- удерживать migration ledger в donor-id форме и не возвращать path-based legacy references в active files
- помечать каждый завершенный перенос отдельной записью
- при решении на физическое удаление legacy donor layer удалить `docs/` одним cleanup-pass и при необходимости отдельно сохранить внешний historical snapshot

## TBD

- нужен ли отдельный внешний archival snapshot donor-layer после того, как semantic deletion readiness уже достигнута
