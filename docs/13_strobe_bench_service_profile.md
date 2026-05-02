# Strobe Bench Laboratory Profile

Статус документа:

- supporting stage-doc для engineering profile, а не самостоятельный product spec;
- читать после `docs/README.md`, `50_laboratory_v1_workspace_spec.md`, `39_design_decisions_and_screen_map.md` и `46_safety_risk_and_failure_matrix.md`;
- если описание `strobe_bench` расходится с канонической моделью `Laboratory`, приоритет у primary docs, а этот файл нужно дочищать или сокращать.

Этот документ фиксирует текущий software-stage для `strobe_bench` внутри `Smart_Platform`.

Имя файла остается историческим. Текущая каноническая трактовка этого контура — laboratory/engineering profile, а не отдельная user-facing страница старого типа.

## Какой historical delta здесь остается

- в системе окончательно разведены два разных профиля одного семейства `strobe`:
  - turret/product `strobe` на стороне `Raspberry Pi`;
  - laboratory/bench `strobe_bench` на стороне `ESP32`;
- для `strobe_bench` появился отдельный `ESP32` controller с engineering-gated командами `arm`, `disarm`, `stop`, `abort`, `pulse`, `burst`, `loop`, `continuous on`, `preset`;
- появились API surfaces `strobe_bench/status`, `presets`, `arm`, `disarm`, `stop`, `abort`, `pulse`, `burst`, `loop`, `continuous`, `preset`;
- compatibility route `/service/strobe` впервые стал глубоким laboratory-slice с вкладками `Overview`, `Pulse`, `Burst`, `Loop`, `Continuous`, `Presets`, живым статусом и safe preset запуском.

## Что этот этап реально доказал

1. `strobe_bench` можно держать как owner-side engineering profile внутри общего `Laboratory`, не подменяя turret product-path.
2. Bench-команды и live status можно собрать в один app-like slice вместо набора разрозненных POST-методов.
3. Ownership boundary между боевым `strobe` и bench-profile остается честной уже на этом этапе.

## Что уже не нужно брать отсюда как канон

- compatibility route `/service/strobe` как финальную IA-модель;
- текущий набор вкладок и команд как окончательную форму `Laboratory / Strobe`;
- open items как активный roadmap всего `Laboratory`.

## Зачем файл сохраняем

Как след первого глубокого owner-side `Laboratory` slice для `strobe_bench`, где bench-profile впервые стал частью общего workspace, а не отдельным donor-side bench-flow.
