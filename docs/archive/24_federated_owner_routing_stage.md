# Federated Owner Routing Stage

Статус документа:

- archived historical snapshot;
- больше не входит в активный reading order;
- использовать только как след перехода от общей идеи ownership к routing-contract, а не как active architecture truth.

Исходный активный путь раньше был `docs/24_federated_owner_routing_stage.md`.

## Historical Snapshot

Статус документа:

- stage-doc и migration snapshot, а не primary architecture truth;
- читать после `docs/README.md`, `04_sync_and_ownership.md`, `05_ui_shell_and_navigation.md`, `27_platform_shell_v1_spec.md` и `40_platform_shell_navigation_alignment.md`;
- если описание owner-aware routing или handoff vocabulary расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ сохраняем как короткий historical snapshot того шага, где owner-aware routing впервые стал не только идеей, но и shell/sync contract.

## Какой historical delta здесь остается

- следующий практический шаг был переориентирован с pinout-first детализации на federated routing bootstrap;
- в sync heartbeat и snapshot появились routing-поля `shell_base_url`, `owner_node_id`, `owner_available`, `canonical_path`, `canonical_url`, `federated_access`, без которых shell не может честно вести пользователя к владельцу;
- оба shell начали показывать owner-aware links вместо слепого локального управления peer-owned modules.

## Что этот этап реально доказал

1. Federated shell можно было начать строить раньше, чем полный proxy или hardware maps.
2. Для честной owner-aware навигации достаточно сначала научить snapshot и heartbeat переносить routing truth.
3. Soft handoff оказался отдельным инженерным шагом, а не побочным эффектом sync.

## Что уже не нужно брать отсюда как канон

- общую ownership-модель;
- product vocabulary owner-aware shell;
- подробное описание дальнейшего handoff UX.

## Зачем файл сохраняем

Как след первого routing-bootstrap, после которого shell начал знать владельца модуля, его canonical path и owner availability на уровне контракта.
