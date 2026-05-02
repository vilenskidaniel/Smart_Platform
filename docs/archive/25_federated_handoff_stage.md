# Federated Handoff Stage

Статус документа:

- archived historical snapshot;
- больше не входит в активный reading order;
- использовать только как след первого handoff UX, а не как active architecture truth.

Исходный активный путь раньше был `docs/25_federated_handoff_stage.md`.

## Historical Snapshot

Статус документа:

- stage-doc и migration snapshot, а не primary architecture truth;
- читать после `docs/README.md`, `04_sync_and_ownership.md`, `05_ui_shell_and_navigation.md`, `27_platform_shell_v1_spec.md` и `40_platform_shell_navigation_alignment.md`;
- если описание federated handoff flow расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ сохраняем как короткий historical snapshot первого user-facing handoff flow поверх уже существующего owner-aware routing contract.

## Какой historical delta здесь остается

- на `ESP32` и `Raspberry Pi` появился единый handoff route:
  - `/federated/handoff?module_id=...`
- появился route-info endpoint:
  - `/api/v1/federation/route?module_id=...`
- peer-owned module перестал открываться сырой owner-link и получил отдельный промежуточный handoff flow.

## Что этот этап реально доказал

1. Federated UX можно строить не только вокруг raw URLs, а вокруг честного промежуточного состояния.
2. Handoff page умеет объяснить route-info, owner readiness и blocked state до фактического перехода.
3. После этого шага стало возможно проектировать peer-owned engineering pages и owner-aware `Laboratory` flows уже поверх готового handoff pattern.

## Что уже не нужно брать отсюда как канон

- общую семантику owner-aware navigation;
- полное описание federated routing model;
- handoff как единственный конечный UX-паттерн для всех будущих peer-owned surfaces.

## Зачем файл сохраняем

Как след первого реального federated handoff UX, который заменил голую owner-link модель промежуточной страницей с route-info и честным состоянием владельца.
