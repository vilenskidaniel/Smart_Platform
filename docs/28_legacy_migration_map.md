# Legacy Migration Map From IrrigationSystemESP32

Статус документа:

- legacy compatibility stub only;
- selective migration rules теперь сведены в `knowledge_base/17_open_questions_and_migration.md`;
- donor-репозиторий `IrrigationSystemESP32` не считается обязательной частью workspace;
- этот donor-файл больше не несет уникального migration authority и может быть удален вместе со всем legacy donor layer.

## Migration Note

- verified hardware/tests/product decisions сохранять как knowledge;
- useful UI/flow ideas адаптировать, а не копировать как monolithic implementation;
- ownership-blind auth/secrets/monolith patterns не переносить как есть.

## Related Active File

- [../knowledge_base/17_open_questions_and_migration.md](../knowledge_base/17_open_questions_and_migration.md)
