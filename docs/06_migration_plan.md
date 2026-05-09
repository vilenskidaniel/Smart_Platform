# Migration Plan

Статус документа:

- legacy compatibility stub only;
- active migration control rules теперь живут в `knowledge_base/17_open_questions_and_migration.md`;
- donor-репозитории, legacy office specs и старые source maps считаются только selective knowledge donors, а не обязательными workspace dependencies;
- этот donor-файл больше не несет уникального planning authority и может быть удален вместе со всем legacy donor layer.

## Migration Note

- сохранять как knowledge только проверенные hardware/tests/product decisions;
- полезные UI/flow patterns адаптировать, а не копировать как готовую кодовую базу;
- weak auth, embedded secrets, monolith entrypoints и ownership-blind assumptions не переносить как есть.

## Related Active File

- [../knowledge_base/17_open_questions_and_migration.md](../knowledge_base/17_open_questions_and_migration.md)
