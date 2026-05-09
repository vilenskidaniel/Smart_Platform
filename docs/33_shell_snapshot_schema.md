# Shell Snapshot Schema

Статус документа:

- legacy compatibility stub only;
- active authority file теперь живет в `shared_contracts/shell_snapshot_contract.md`;
- shell/runtime vocabulary and routing context теперь живут в `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/05_shell_navigation_and_screen_map.md` и `knowledge_base/15_platform_services_and_shared_content.md`;
- этот donor-файл больше не несет уникального contract meaning и может быть удален вместе со всем legacy donor layer.

## Migration Note

Если shell snapshot structure или field semantics меняются:

1. сначала обновлять `shared_contracts/shell_snapshot_contract.md`;
2. затем выравнивать active canon в `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`, `knowledge_base/05_shell_navigation_and_screen_map.md` и `knowledge_base/15_platform_services_and_shared_content.md`;
3. этот файл не расширять обратно: он остается только кратким residue-note до полного удаления legacy donor layer.

## Related Active Files

- [../shared_contracts/shell_snapshot_contract.md](../shared_contracts/shell_snapshot_contract.md)
- [../knowledge_base/04_runtime_topology_controller_profiles_and_sync.md](../knowledge_base/04_runtime_topology_controller_profiles_and_sync.md)
- [../knowledge_base/05_shell_navigation_and_screen_map.md](../knowledge_base/05_shell_navigation_and_screen_map.md)
- [../knowledge_base/15_platform_services_and_shared_content.md](../knowledge_base/15_platform_services_and_shared_content.md)
