# 04. Runtime Topology, Controller Profiles And Sync

## Роль Файла

Этот файл должен объяснять, как система живет во времени: кто запущен, кто смотрит интерфейс, какие controller profiles сейчас используются и как это влияет на sync и ownership.

## Статус

- текущий статус: `active draft`

## Донорские Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `shared_contracts/shell_snapshot_contract.md` остается active companion contract для snapshot/routing truth.

## Установленные Истины

- host, viewer и controller profile — разные сущности
- `ESP32` и `Raspberry Pi` не считаются вечными owner-ярлыками модулей
- текущий controller profile может быть временным

## 1. Host, Viewer И Runtime Context

В активном topology language нужно отдельно различать как минимум четыре сущности:

- `host node`, который поднял shell-server или текущую страницу;
- `viewer`, то есть конкретную браузерную сессию и устройство пользователя;
- `owner-side runtime`, который реально исполняет команду и держит truthful module state;
- `peer node`, который может быть доступен, недоступен или работать как удаленный owner-side runtime.

Базовое правило:

- `host launch` и `browser entry` — это разные слои;
- viewer может входить через URL host-side shell и при этом работать с peer-owned модулем;
- host не должен притворяться owner-side runtime только потому, что именно он отдал HTML пользователю.

### Shell Surface, Runtime Host И Physical Device Truth

Для этого проекта опасно схлопывать несколько разных ответов на вопрос “что это за устройство?”.

- `current_shell` описывает family опубликованной shell-surface, а не устройство, которое пользователь сейчас держит в руках;
- `runtime.host` описывает машину, где сейчас реально работает backend/server;
- `viewers` описывают конкретные браузеры и устройства просмотра;
- `nodes.current` и `nodes.peer` описывают physical platform nodes, а не viewer-сессии.

Практические примеры, которые нужно считать нормой, а не исключением:

- `Windows laptop` может одновременно быть `runtime.host`, текущим `desktop` viewer и временным smoke-host для shell family `raspberry_pi`, пока `ESP32` остается отдельным physical peer node;
- на втором этапе тестирования голый `Raspberry Pi` с экраном и камерой должен оставаться отдельным physical node и одновременно давать отдельный `display` viewer, не стирая различие между этим экраном и Windows laptop viewer;
- bar, `Settings`, `Laboratory` и другие shared shell surfaces не должны показывать `current_shell.node_type` как будто это “текущее устройство пользователя”.

### Host launch, browser entry и viewer detection

- `host launch` означает только то, что один runtime-host или smoke-host поднял shell-server и опубликовал shell URL;
- `browser entry` означает, что любой viewer-клиент после этого просто открывает опубликованный URL без локального launcher requirement;
- `Windows` shortcut, `VBS`, `CMD` или `PowerShell` launcher допустимы только как host convenience layer, а не как универсальная entry point для всех устройств;
- `ESP32`, `Raspberry Pi`, `Windows laptop`, `Linux laptop`, `phone`, `tablet` и встроенный display должны укладываться в одну browser-first модель, где viewer-клиенту нужен URL, а не локальный startup script;
- shell должен различать viewer presence отдельно от host launch: `viewer_id`, viewer-kind, page, address и `last_seen` принадлежат viewer layer, а не owner-role layer.

Практический вывод:

- desktop/laptop host может временно поднимать shell как smoke-host или convenience host;
- этот host не становится от этого owner-side runtime модуля;
- phone или другой browser client не должен запускать локальные host scripts и должен входить по уже опубликованному URL;
- loopback entry и LAN entry — это разные deployment modes одного host layer, а не разные архитектурные owner semantics.

### Current Windows Host Convenience Layer

Текущий convenience layer для `Windows` может использовать launcher scripts из `tools/`, но они не меняют сам runtime contract:

- `Launch-SmartPlatformShell.vbs`, `Launch-SmartPlatformShell.cmd` и `Launch-SmartPlatformShell.ps1` остаются host-side wrappers, а не частью cross-device entry model;
- default convenient mode для host-side entry может быть `LAN`, чтобы shell сразу был доступен локальному desktop-host и другим browser clients в сети;
- `Loopback`-style smoke entry остается допустимым только как локальный desktop path;
- launcher может автоматически открыть browser window, но viewer entry semantics после этого остаются browser-first и URL-based.

### Mobile Entry Helper Layer

Допустимый helper layer поверх browser-first model:

- shell может показывать QR/mobile-entry helper для уже опубликованного `LAN` URL;
- такой helper не заменяет host launch, а только упрощает phone/tablet entry в уже поднятый shell;
- если shell доступен только через loopback URL, mobile-entry helper не должен притворяться валидной phone entry path.

## 2. Platform Topologies

В `v1` нужно честно описывать несколько topology-сценариев:

### Single-node local topology

- доступен только один runtime-host;
- shell и локальные user-facing pages открываются напрямую;
- peer-owned surfaces остаются видимыми, но честно деградируют.

### Dual-node owner-aware topology

- одновременно доступны `always-on I/O role` и `turret compute role`;
- shell знает availability обоих узлов;
- команды маршрутизируются owner-side runtime соответствующего модуля.

### Smoke-host topology

- shell может быть поднят на временном desktop/laptop host для smoke или development entry;
- такой host не становится автоматическим owner модуля;
- если есть более сильный runtime source, например `runtime_profile`, `viewers` или routing truth в snapshot, они важнее простых loopback-эвристик.
- если published shell family относится к `Raspberry Pi`, это не означает, что текущий viewer или runtime host тоже являются `Raspberry Pi`.

## 3. Controller Profiles Для Модулей

`Controller profile` в активном каноне описывает не модуль, а текущий способ его исполнения:

- на каком runtime-host он сейчас исполняется;
- какие компоненты и safety checks участвуют;
- это product profile, laboratory profile, bench profile или temporary bring-up path.

Один и тот же модуль может иметь несколько controller profiles на разных этапах жизни:

- product profile;
- laboratory profile;
- smoke/simulation profile;
- temporary migration profile.

Вывод:

- controller profile может меняться;
- модульная роль и user-facing meaning от этого не должны переименовываться.

## 4. Current Temporary Profiles Для `Irrigation` И `Turret`

Текущий baseline на сегодня:

- `Irrigation` использует controller profile на `ESP32`, который одновременно реализует `always-on I/O role`, локальный полив, часть wake/sentinel logic и fallback shell behavior;
- `Turret` использует controller profile на `Raspberry Pi`, который реализует `turret compute role`, heavy turret-family runtime, vision/analysis и media-heavy workflows;
- `Windows` или другой desktop/laptop host может временно поднимать smoke-host shell для `Raspberry Pi`, но это convenience layer, а не новая архитектурная owner-role.

Текущий handoff baseline допускает:

- route-info endpoint для owner-aware routing;
- промежуточный federated handoff flow;
- preview и degraded UX даже при недоступном owner-side device.

## 5. Sync Domains И Visibility Rules

В topology language различаем несколько доменов синхронизации:

- `routing truth`: `shell_base_url`, `owner_node_id`, `owner_available`, `canonical_path`, `canonical_url` и related owner-routing fields;
- `runtime truth`: module states, active mode, fault/lock reasons, heartbeat, availability;
- `persistent truth`: settings, registries, shared preferences, confirmed profiles;
- `event/content truth`: logs, reports, media and content provenance.

Visibility rules:

- snapshot должен отделять `runtime host`, `current viewer`, `platform nodes`, `sync` и `storage`;
- owner availability и canonical route должны приходить как часть shell truth, а не вычисляться только на клиенте;
- viewer видит локальный или mixed slice в зависимости от фактической доступности источников.

### Sync Bootstrap And Intermediate States

Для `v1` важен не только факт reachability peer-side node, но и промежуточная стадия между простым heartbeat и уже подтвержденным module/runtime sync.

Минимальный staged sync bootstrap этого этапа:

1. peer объявляет себя reachable;
2. heartbeat дает `sync_ready` и `reported_mode`;
3. owner-side runtime или peer-side bridge публикует module/runtime state;
4. только после этого shell получает право считать peer-side module truth fully synced.

Отсюда следуют обязательные intermediate states:

- `degraded / owner_unavailable`, если peer-side owner недоступен;
- `degraded / peer_sync_pending`, если heartbeat уже есть, но module/runtime sync еще не завершен;
- `online / none`, если peer на связи и sync truth уже подтвержден.

Практическое sync правило этого bootstrap layer:

- одного флага `reachable` недостаточно для честного shell behavior;
- shell должен различать `peer already visible` и `peer already synchronized`;
- peer-side push не должен переписывать локальные owner modules текущего узла;
- staged bootstrap может использовать отдельные surfaces для `sync state`, `heartbeat` и `module push`, даже если полный двусторонний sync engine еще не завершен.

### Shared Log Sync Continuity

`Event/content truth` может включать mirrored platform-log continuity между узлами.

Для такого sync contour обязательны:

- origin metadata у mirrored entry;
- marker, что запись пришла с peer-side node;
- deduplication repeated remote delivery;
- честное разделение между shared diagnostic log continuity и более тяжелыми merge-задачами вроде persistent settings или long-term history.

### Sync Compatibility Baseline

Active topology language не должен возвращаться к brand-first owner model, но compatibility-layer может по-прежнему встречать старые role aliases в payloads, логах и transitional runtime surfaces.

Допустимые legacy aliases:

- `io_node`;
- `compute_node`;
- `shared`.

Если в старом runtime или compatibility payloads еще встречаются `esp32` и `rpi`, их можно сохранять только как legacy alias layer, а не как active user-facing ownership vocabulary.

Conflict defaults для `v1` baseline:

- safety-critical truth не перетирается удаленно молча;
- команду исполняет только owner-side runtime соответствующего модуля;
- для `persistent truth` базовый conflict rule остается `last_write_wins` + timestamp + `source_node`;
- shared logs и mirrored entries должны оставаться append-only и не переписывать уже принятые записи без явного provenance.

Transport baseline этого этапа:

- стартовая transport-модель опирается на `HTTP JSON` API surfaces;
- heartbeat и short sync steps могут идти короткими запросами по расписанию;
- browser читает текущий host-side shell и его routing truth напрямую;
- `WebSocket` допустим как later-stage расширение, но не считается обязательной базой `v1`.

## 6. Degraded, Offline And Peer-Missing Behavior

- потеря peer-side node не должна прятать peer-owned module из shell;
- peer-owned surface остается видимой, но уходит в `blocked`, `locked` или `degraded` в зависимости от причины;
- `Gallery` должна открывать локальный slice и явно маркировать отсутствие peer-sources;
- handoff flow должен честно показать owner readiness и route-info до фактического перехода;
- host-side shell не должен имитировать выполнение peer-owned опасной команды локально.

## 7. Что Считается Каноном, А Что Текущей Реализацией

Каноном считаем:

- различение `host`, `viewer`, `owner-side runtime` и `peer`;
- owner-aware routing truth в snapshot и shell behavior;
- controlled degradation при потере связи;
- правило, что controller profile не равен вечному owner-ярлыку модуля.

Текущей реализацией считаем:

- связку `ESP32` + `Raspberry Pi` как физический baseline today;
- текущие launcher flows для `Windows` smoke-host entry;
- конкретные route endpoints и handoff pages, которые могут развиваться без смены общей topology language.

## Open Questions

- когда controller profile должен повышаться из temporary в stable

## TODO

- собрать topology language без старых brand-based owner shortcuts

## TBD

- будущая multi-controller модель для модулей с распределенным управлением
