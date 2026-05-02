# Platform Shell Navigation Alignment

Этот документ фиксирует один компактный переходный слой для `Platform Shell / navigation contract`.

Его задача:

- не переписывать заново product vision;
- не подменять primary docs;
- собрать в одном месте текущий drift между `product target`, `software baseline` и текущими route/alias решениями;
- дать безопасный порядок миграции для shell, snapshot и UI vocabulary.

Primary truth по-прежнему живет в:

1. [../README.md](../README.md)
2. [05_ui_shell_and_navigation.md](05_ui_shell_and_navigation.md)
3. [26_v1_product_spec.md](26_v1_product_spec.md)
4. [27_platform_shell_v1_spec.md](27_platform_shell_v1_spec.md)
5. [29_shared_content_and_sd_strategy.md](29_shared_content_and_sd_strategy.md)
6. [33_shell_snapshot_schema.md](33_shell_snapshot_schema.md)
7. [39_design_decisions_and_screen_map.md](39_design_decisions_and_screen_map.md)
8. [../shared_contracts/shell_snapshot_contract.md](../shared_contracts/shell_snapshot_contract.md)

Этот файл нужен именно как alignment-map для текущего шага миграции.

## 1. Что Считаем Каноническим User-Facing Shell

На уровне shell и глобальной навигации каноническими считаются:

1. `Home`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`
6. `Settings`

Быстрый action-entry из shell:

- `Gallery > Reports`

Не считаются отдельными top-level user-facing pages:

- `Logs`
- `Diagnostics`
- `Content Storage`
- `Laboratory`

Важно:

- это не значит, что backend/routes/diagnostics исчезают;
- это значит, что они не должны конкурировать с product-level vocabulary в shell.

## 2. Product Target vs Software Baseline

### Product target

Shell должен ощущаться как приложение с единым control language и давать прямой вход в:

- `Gallery`
- `Laboratory`
- `Settings`
- `Gallery > Reports`

Глубокая история действий должна жить в `Gallery > Reports`.
Локальные storage/service diagnostics не должны подменять собой `Gallery`.

### Software baseline

Текущий baseline все еще использует transitional vocabulary:

- `Laboratory`
- `Content`
- `Logs`
- `Diagnostics`

и transitional snapshot/navigation keys:

- `service`
- `content`
- `logs`
- `diagnostics`
- `laboratory`

Этот baseline допустим как промежуточный слой, но больше не считается целевой shell-моделью.

## 3. Alias Policy

### `Laboratory`

Фиксируем:

- user-facing имя: `Laboratory`
- внутренний route alias: `/service`
- допустимые исторические alias-названия в docs и code comments:
  - `Laboratory`
  - `Diagnostics`
  - `Test Bench`

Правило:

- в main shell, launcher, cards и navigation label использовать только `Laboratory`;
- `Laboratory` допустим как внутренний stage-term и route-alias, но не как основной label.

### `Gallery`

Фиксируем:

- user-facing имя: `Gallery`
- owner scope: shared / virtual
- user-facing tabs:
  - `Plants`
  - `Media`
  - `Reports`

Правило:

- shell не должен выставлять отдельную top-level страницу `Content`;
- storage readiness и content diagnostics могут существовать отдельно, но как service/internal surface.

### `Settings`

Фиксируем:

- `Settings` остается отдельной persistent page;
- `Settings` не дублирует laboratory controls;
- `Settings` не управляет составом laboratory tabs;
- `Settings` может показывать storage/sync/interface/function/style policies.

## 4. Что Делаем С `Content Storage`

Текущее состояние:

- route и diagnostics-страница полезны для проверки mirrored content readiness;
- но vocabulary `Content Storage` в top-level shell перегружает модель и конфликтует с `Gallery`.

Выбранное решение:

- `Gallery` остается единственным user-facing content section;
- raw content/storage page сохраняется как internal/service surface;
- в user-facing vocabulary использовать не `Content`, а максимум внутреннее `Storage Diagnostics`;
- shell может показывать только короткий summary:
  - local content ready / missing
  - peer content available / unavailable
  - quick entry в `Gallery`

Что это дает:

- не плодим отдельную пользовательскую сущность;
- не теряем полезную diagnostics surface;
- не смешиваем content tree с low-level storage inspection.

Если later-stage shell станет слишком перегруженным, `Storage Diagnostics` можно окончательно увести в:

- `Settings > Storage & Sync`
- или `Laboratory` diagnostics slice

Но не в top-level main navigation.

## 5. Что Делаем С `Logs`, `Diagnostics` И `Reports`

Фиксируем:

- `Logs` не считаются отдельной product page;
- `Diagnostics` не считаются отдельной top-level product page;
- shell показывает только короткие summaries и pointers;
- канонический user-facing viewer истории действий и отчетов:
  - `Gallery > Reports`

Это означает:

- route `/#logs` может существовать временно;
- route `/#diagnostics` может существовать временно;
- но они должны считаться deprecated shell surfaces.

## 6. Operator Note

`Operator note` не выделяем в отдельный модуль, страницу или subsystem.

Фиксируем:

- `operator note` = один из типов `report entry`
- note может создаваться из `Laboratory`
- позже note может создаваться из `Manual`
- note должен отображаться в `Gallery > Reports` как часть mixed chronological feed

Минимальный payload note-entry:

- `entry_type = operator_note`
- `text`
- `created_at`
- `owner_node_id`
- `source_surface`
- `source_mode`
- `module_id`
- `related_action_id` optional

Почему так:

- не плодим отдельную сущность;
- не теряем человеческий контекст;
- не оставляем note только во внутреннем backend-log.

## 7. Navigation Contract Decision

На уровне shell snapshot и shell UI целевыми считаем такие navigation concepts:

- `home`
- `irrigation`
- `turret`
- `gallery`
- `laboratory`
- `settings`
- quick pointer to `gallery > reports`

Transition rule:

- current software baseline временно может продолжать отдавать transitional keys;
- но новые shell-изменения должны проектироваться уже вокруг `gallery` и `laboratory`, а не вокруг `content` и `service`.

## 7.1 Home And Bar Alignment

Помимо navigation keys платформа теперь должна держать единый `home / bar contract`.

User-facing смысл этого слоя:

- домашняя страница называется `Smart Platform`, а не `Platform Shell`;
- верхняя bar-панель становится главным носителем честных статусов;
- отдельный блок `Entry Context` на home screen убирается;
- большая часть технической детализации уходит в tooltip/status-sheet по hover, focus или tap.

Bar contract обязан одинаково трактоваться на обеих сторонах:

- слева: compact home logomark, desktop interaction toggle, fullscreen toggle, current client icon;
- в центре: постоянные ярлыки `Raspberry Pi` и `ESP32`, mode-chips только для реально доступных owner modules, moisture strip из 5 irrigation groups;
- справа: `Wi-Fi`, `Sync`, environmental and system indicators, language, time, date;
- если данных нет, slot сохраняется, а индикатор уходит в честное серое `no data` состояние.

Важно:

- это не dashboard для сырых booleans и не место для `node_id`, `base_url` или `wifi: true / false`;
- browser-side client detection остается эвристикой, а не hardware source of truth;
- `Laptop smoke` считается честным single-node testing path, а не третьим hardware owner.

## 7.2 Logical Direct Route Policy

На shell-level alignment-map фиксируем еще одно правило:

- логичные user-typed routes не должны ломаться в сырой `404`, если shell знает соответствующий module;
- owner-local route открывается локально;
- peer-owned route переводит на federated handoff или blocked explanation;
- прямой ввод адреса должен быть совместим с owner-aware vocabulary, а не обходить ее.

Практический вывод для snapshot migration:

1. Добавить canonical navigation entries:
   - `gallery`
   - `laboratory`
   - `settings`
2. Сохранить старые keys только как temporary compatibility layer.
3. Перевести tests на canonical model.
4. Только потом убирать deprecated keys из code paths.

## 8. Vocabulary Migration Map

Текущий baseline -> целевая shell vocabulary:

- `Laboratory` -> `Laboratory`
- `Content` -> `Gallery`
- `Content Storage` -> internal `Storage Diagnostics`
- `Logs` -> `Gallery > Reports`
- `Diagnostics` -> shell summaries + `Laboratory`

Важно:

- это не map route-to-route;
- это map user-facing semantics.

Маршруты могут временно сохраняться такими:

- `/service`
- `/content`
- `/#logs`
- `/#diagnostics`

Но user-facing labels должны мигрировать раньше самих route aliases.

## 9. Безопасный Порядок Миграции

1. Зафиксировать docs и vocabulary.
2. Выровнять `shell_snapshot_contract` и snapshot tests.
3. Выровнять `raspberry_pi/shell_snapshot_facade.py` и `firmware_esp32/src/web/ShellSnapshotFacade.cpp`.
4. Выровнять shell HTML и top-level navigation labels на обеих сторонах.
5. Только после этого углубляться в user-facing `Gallery` и `Reports`.

Почему так:

- сначала фиксируем смысл navigation contract;
- потом приводим к нему data contract;
- и только потом переписываем UI surface.

## 10. Что Здесь Сознательно Не Решается

Этот alignment-doc не закрывает:

- полный UI layout `Gallery`
- полный data model `Reports`
- полный `Settings` schema
- окончательный FPV/HUD design для `Turret`
- storage sync internals

Он закрывает только:

- shell vocabulary
- alias policy
- page boundaries
- место `Content Storage`
- место `operator note`
- безопасный migration order
