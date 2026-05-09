# 08. Safety, Acceptance And Field Operations

## Роль Файла

Этот файл должен объединить safety, acceptance и реальные полевые/стендовые правила в один практический слой.

## Статус

- текущий статус: `active draft`

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- specific legacy donor paths больше не считаются обязательным reading path для этого active file.

## Settled Truths

- blocked и safety truth должны быть честными и видимыми
- acceptance не должен теряться в чисто narrative тексте

## 1. Общие Safety-Principles

Активный safety canon для `v1` держится на следующих правилах:

1. owner-side runtime принимает решение об исполнении опасного действия;
2. peer-side shell может отображать, объяснять и направлять, но не обходить блокировку владельца;
3. физическая аварийная блокировка сильнее программного намерения;
4. `Laboratory` не должен автоматически повышать инженерные параметры до product defaults;
5. выбранный оператором power context должен оставаться явным для bench-sensitive slices;
6. blocked, fault и degraded truth должны быть честными, видимыми и сопровождаться следующим шагом;
7. product-level report нужен только когда событие действительно имеет пользовательский смысл, а не просто произошло внутри engineering workflow.

Retained command arbitration order for `v1`:

1. `Emergency / Abort`
2. `Safety Fault` и interlock-enforced block
3. явное service or `Laboratory` действие внутри допустимого safety envelope
4. `Manual`
5. `Automatic`
6. фоновая синхронизация и телеметрия

Owner-side execution invariant:

- UI отправляет команду в current owner path модуля;
- owner-side runtime проверяет режим, readiness, interlock и safety gates;
- owner либо исполняет команду, либо возвращает явную блокировку;
- результат фиксируется до того, как shell считает действие успешным.

## 2. Acceptance Gates Для `v1`

Для завершенного `v1` acceptance важно не количество тестов, а закрытие обязательных ворот:

### Shell And Owner Routing Gate

- одноплатные и двухплатные входы читаются честно;
- peer-owned routes остаются видимыми и объяснимыми;
- handoff не подменяется ложным локальным владением.

### Irrigation Gate

- видимость зон и sensor truth сохраняется даже в деградации;
- manual и basic automatic irrigation идут только через owner-side logic;
- faults водяного контура и sensor failures честно отражаются.

### Turret Gate

- manual/FPV вход и readiness families читаются правдиво;
- недоступные camera/range/action families не исчезают молча;
- turret safety rules и policy hooks соблюдаются до исполнения действий.

### Gallery And Reports Gate

- локальный и mixed content slice читаются честно;
- `Reports` остаются продуктовой историей, а не dump-layer всего engineering trace;
- source provenance и degraded availability видимы пользователю.

### Laboratory Gate

- readiness и preflight видимы до глубокого hardware work;
- experimental profiles остаются laboratory-only и не притворяются product-ready;
- confirmed results передаются в `Settings` явным путем `save/apply`.

### Safety And Recovery Gate

- emergency, fault, degraded и locked states отражаются одинаковым языком;
- оператор видит не только цвет, но и допустимый fallback-mode и следующий шаг;
- критические состояния оставляют понятный след результата.

## 3. Field And Bench Operations

Практический bring-up order для первых реальных проходов:

1. shell and readiness smoke;
2. peer link and owner handoff;
3. `ESP32 / Strobe Bench`;
4. `ESP32 / Irrigation`;
5. `Raspberry Pi / Turret`;
6. experimental profiles;
7. session review before the next testcase bundle.

Обязательные entry states для phone/browser path:

- `ESP32` only;
- `Raspberry Pi` only;
- both boards connected.

Для каждого реального прохода должны быть явно зафиксированы:

- кто оператор;
- какой objective у прохода;
- какой hardware profile используется;
- какой power context выбран;
- какая board topology сейчас активна;
- какой slice или page был реально открыт;
- где останется след результата.

Практический baseline для первых phone/browser passes:

- top shell bar должен быть читаем без zoom и сразу показывать current board, missing peer и truthful owner-aware state;
- переход `Home -> Laboratory` не должен терять board context, owner visibility или power context;
- blocked peer-owned slices должны объяснять себя до deep navigation, а не выглядеть как сломанная страница;
- browser mode и fullscreen mode должны менять density, но не терять shell status и owner truth.

Outcome heuristic for this pass:

- `pass`, если board context очевиден, shell readable и blocked slices честно объясняются;
- `warn`, если путь работает, но labels, chips, density или fullscreen behavior затрудняют операторское чтение;
- `fail`, если оператор теряет board context или не может понять ownership active slice.

Практический baseline для `8-inch` Raspberry Pi Touch Display pass:

- `Laboratory -> Displays -> Raspberry Pi Touch Display` открывается без потери shell и owner context;
- минимум один color-pattern pass, один geometry/grid pass и один touch-grid pass выполняются и в browser mode, и в fullscreen mode;
- проверка должна отдельно замечать clipping, dead zones, obvious distortion и degraded touch comfort.

### First Field Entry And Onboarding

Базовая field-model для `v1` должна оставаться browser-first:

- первый вход делается через shell доступного узла, а не через отдельное нативное приложение;
- phone-first entry допустим и желателен как реальный операторский путь;
- пользователь сразу должен видеть, на каком узле он находится, доступен ли peer и какие маршруты локальны, peer-owned или временно заблокированы;
- первый практический маршрут должен быть коротким: открыть shell, понять board context, увидеть peer status, затем перейти в `Home`, `Laboratory` или продуктовый раздел.

Связанный runtime contract:

- model `host launch` vs `browser entry` задается в `knowledge_base/04_runtime_topology_controller_profiles_and_sync.md`;
- shell-language и route behavior задаются в `knowledge_base/05_shell_navigation_and_screen_map.md`;
- этот файл фиксирует уже не сам launcher-flow, а полевое применение этих правил.

### One-Node And Two-Node Field Modes

`ESP32`-only mode:

- `Irrigation` должен оставаться полноценным локальным product module;
- `Gallery` должен показывать локальный content/report slice;
- `Laboratory` должен показывать локальные irrigation и bench-sensitive slices;
- `Turret` остается видимой, но честно заблокированной peer-owned веткой.

`Raspberry Pi`-only mode:

- `Turret` остается локальным owner module;
- `Gallery` должен показывать локальный media/report slice;
- `Laboratory` должен сохранять turret-owner context и честно показывать ожидание peer-side irrigation;
- `Irrigation` остается видимой, но честно деградированной веткой.

Dual-node mode:

- shell на любом узле показывает обе платы и их availability;
- peer-owned маршруты открываются через owner-aware handoff, а не через притворство локальным владельцем;
- shared shell truth и shared preferences остаются согласованными;
- `Gallery` работает как mixed-source surface;
- `Laboratory` показывает связанную readiness картину и рекомендуемый следующий инженерный шаг.

### Maintenance Windows And Service Sessions

Во время обслуживания система должна явно различать:

- штатную работу;
- инженерную или обслуживающую сессию;
- аварийную остановку или состояние блокировки.

Практические правила:

- безопасный вход в обслуживание идет через явный переход в `Laboratory`;
- до запуска чувствительных актуаторов обязателен readiness/preflight слой;
- инженерные результаты сначала фиксируются в session layer `Laboratory`;
- в `Gallery > Reports` попадают только результаты с product-level смыслом;
- обслуживание, калибровка и temporary overrides не должны молча менять глобальное продуктовое поведение без явного подтверждения.

### Installation Prerequisites

Перед продуктовым использованием должны быть подтверждены:

- отдельные power boundaries для логики и силовых актуаторов;
- физическая доступность emergency interlock для turret-sensitive групп;
- разделение irrigation water path и turret water path;
- наличие корректного локального хранилища для `Gallery` и связанной истории;
- сетевой путь хотя бы до одной browser entry точки shell;
- честная маркировка отсутствующих аппаратных семейств в `Laboratory`.

### Periodic Operations And Checks

Регулярная эксплуатация должна включать:

- проверку состояния peer-связи и owner handoff;
- проверку запаса хранилища и видимости отчетов;
- калибровку и перепроверку адекватности сенсоров по мере необходимости;
- осмотр water paths и interlock-state;
- разбор последних laboratory session results со статусами `pass / warn / fail`;
- просмотр `Gallery > Reports` только как product-level operational history, а не как полного engineering trace.

### Optional Bootstrap Helpers

Допустимые вспомогательные слои для первичного входа и настройки:

- `SoftAP` или setup-like bootstrap path для первичной сетевой конфигурации;
- QR как быстрый mobile entry helper;
- явная индикация pairing/bootstrap state как временный shell-layer во время первичного входа.

Что не считается обязательной нормой `v1`:

- один магический центральный URL для всех узлов;
- фиксированные device credentials как product-level onboarding model;
- обязательный первый вход через `Telegram` или другой внешний канал.

## 4. Emergency, Fault, Degraded And Recovery Paths

`Emergency`:

- самый высокий приоритет;
- чувствительные ветви должны уходить в безопасное состояние;
- hardware interlock может физически снять питание вне зависимости от software state;
- software фиксирует latched emergency state до ручного clear/return path.

`Fault`:

- указывает на реальную неисправность или unsafe failure;
- продолжение работы требует устранения причины;
- fault не должен маскироваться под advisory warning.

`Degraded`:

- модуль остается частично доступным;
- пользователю и оператору должен быть понятен допустимый fallback mode;
- degraded route не должен притворяться полноценным normal mode.

`Locked`:

- управление намеренно запрещено policy, ownership или safety-chain;
- shell обязан показать причину и следующий шаг.

Recovery rule:

- каждое critical state change должно отвечать на три вопроса:
  - что сейчас разрешено делать;
  - что нужно проверить;
  - где останется trace результата: в `Laboratory` session layer или в product-level `Reports`.

## 5. Human Checklist-Formats

Минимальный human-readable checklist item должен содержать:

- `case_id` или `failure_id`;
- цель проверки или описание риска;
- требуемый hardware profile;
- предусловия;
- шаги выполнения;
- ожидаемое поведение shell и active module;
- ожидаемую фиксацию результата;
- итог `pass / warn / fail / blocked / skipped`.

Практический шаблон:

```text
Case ID:
Objective:
Hardware profile:
Power context:
Preconditions:
Steps:
Expected shell truth:
Expected module truth:
Result location:
Outcome:
Notes:
```

Canonical validation case-family prefixes for the current stage:

- `ACC-SHELL` for shell entry, handoff, blocked-route and surface continuity checks;
- `ACC-IRR` for irrigation visibility, manual action and degraded sensor-path checks;
- `ACC-TUR` for turret manual entry, degraded readiness and owner-side action gating checks;
- `ACC-GAL` for gallery source visibility, mixed reports and report-card semantics;
- `ACC-LAB` for laboratory readiness, workspace continuity, power-context and display-pass checks;
- `ACC-SAFE` for interlock, collision and safety-blocking checks.

Precondition vocabulary for acceptance cases:

- `board_reachable`;
- `shell_ready`;
- `peer_visible`;
- `sync_ready`;
- `engineering_session_inactive`;
- `interlock_clear`;
- `required_family_online`;
- `storage_writable`.

Canonical safety risk families for the current stage:

- power and interlock failures;
- irrigation and turret water-path failures;
- motion, strobe and audio misuse or unavailable actuator families;
- sensor, camera, range and vision truth failures;
- peer-link, ownership and degraded-routing failures.

Minimum failure-record shape for a safety case:

- `failure_id`;
- affected area/family;
- trigger;
- owner node or owner-side execution boundary;
- expected shell state;
- block reason or fault reason;
- allowed fallback mode;
- required operator action;
- result location.

### Detailed Automated Checks And Qualification Buckets

Acceptance gates не заменяют собой detailed test inventory. Для текущего этапа полезно отдельно фиксировать первые automated checks и hardware qualification buckets.

First automated runtime checks worth keeping in code, not only as manual smoke:

- `strobe` остается заблокированным в `automatic`, если `target_locked` не подтвержден;
- `emergency` снимает активные актуаторы и оставляет latched safe state;
- service scenario вроде `service_safe_idle` проходит в допустимом safety envelope;
- turret event trace зеркалится в shared `platform log` с корректным provenance.

Hardware qualification buckets текущего этапа:

- `Power Qualification`: стартовые напряжения, просадка при actuator load, отсутствие нежелательной перезагрузки логики и предсказуемое degraded behavior при power issues;
- `Sensor Pack Qualification`: отдельная проверка каждого датчика, отсутствие/шум/недостоверность данных и корректное попадание `environment_pack` / `soil_sensing` truth в shell и logs;
- `Water Path Qualification`: отдельная проверка irrigation и turret water paths, запрет смешивания команд и корректные emergency stop/recovery transitions;
- `Turret IO Qualification`: motion, `strobe`, `audio`, manual/service modes и owner-unavailable blocking behavior;
- `Camera And Vision Qualification`: camera initialization, отсутствие камеры, safe behavior при vision-stack failure и truthful sync отражение camera-state на peer side.

## 6. Module-Specific Safety Hooks

`Irrigation`:

- dry-run, leak, pressure and sensor-truth issues должны вести к fault или degraded behavior по зоне;
- при недостоверном sensor state manual fallback должен оставаться возможным только в допустимых пределах.

`Turret`:

- emergency power interlock обязан перекрывать чувствительные action families;
- camera/range/motion/strobe/water readiness должны быть видимы как отдельные семьи риска;
- owner-side runtime не должен терять приоритет над peer shell.

Для `strobe` и других чувствительных action families retained override rule выглядит так:

- `Emergency` всегда останавливает текущий шаблон или активное действие;
- `Fault` запрещает новый запуск до устранения причины;
- активная `Laboratory` или service session блокирует автоматическое использование, пока сессия не завершена;
- `Manual` имеет приоритет над автоматическим сценарием;
- автоматический режим разрешен только на owner-side runtime соответствующего модуля.

`Laboratory`:

- experimental slices должны оставаться laboratory-only;
- power context для voltage-sensitive flows должен быть явным;
- engineering session не должна автоматически становиться product history.

`Gallery` и `Reports`:

- сохраняют только product-level history;
- blocked/fault/warning product events могут попасть в `Reports`, если событие имеет пользовательский смысл;
- laboratory session artifacts туда не попадают по умолчанию.

## Open Questions

- какие acceptance matrices стоит оставить табличными, а какие упростить до канонических списков

## TODO

- перенести operational truth без stage-дублирования

## TBD

- финальная форма полевого пакета для внешнего помощника
