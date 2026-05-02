# Stage 21 - Platform Log And Turret Engineering Scenarios

Статус документа:

- stage-doc и implementation snapshot, а не primary product truth;
- читать после `docs/README.md`, `07_testing_strategy.md`, `37_turret_product_context_map.md`, `41_laboratory_testing_readiness.md` и `47_acceptance_and_validation_matrix.md`;
- если описание engineering scenarios, logs или product-level flows расходится с каноническим слоем, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ сохраняем как короткий implementation snapshot того этапа, где у `Raspberry Pi` появились node-level platform log и повторяемые dry-run engineering scenarios.

## Какой historical delta здесь остается

- добавлен `PlatformEventLog` как общий журнал узла, в который начали зеркалиться turret events;
- добавлен compatibility-named scenario pack `turret_service_scenarios` и его runner;
- shell `/` начал показывать последние записи platform log;
- страница `/turret` получила запуск dry-run сценариев;
- появились первые `unittest` для runtime и сценариев;
- появились API surfaces:
  - `GET /api/v1/logs`
  - `GET /api/v1/turret/scenarios`
  - `POST /api/v1/turret/scenarios/run?id=...`

## Что этот этап реально доказал

1. Узловую картину можно собирать не только из модульных статусов, но и из общего platform log.
2. Engineering scenarios можно запускать как повторяемый browser-driven слой еще до реальных hardware bindings.
3. Runtime, log и scenario pack можно связать первыми unit-тестами до живой двухузловой обкатки.

## Что уже не нужно брать отсюда как канон

- compatibility-name `turret_service_scenarios` как обязательный будущий vocabulary;
- список дальнейших улучшений логов и сценариев как актуальный roadmap;
- локальный dry-run stage как замену canonical `Laboratory` flows.

## Зачем файл сохраняем

Как след первого этапа, где у платформы появился node-level log layer и повторяемые dry-run engineering scenarios для turret-owner стороны.
