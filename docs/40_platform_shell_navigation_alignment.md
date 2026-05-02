# Выравнивание навигации `Platform Shell`

Этот документ фиксирует один компактный переходный слой для `Platform Shell / navigation contract`.

Его задача:

- не переписывать заново product vision;
- не подменять primary docs;
- собрать в одном месте текущее расхождение между `product target`, `software baseline` и текущими решениями по маршрутам и историческим alias;
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

Этот файл нужен именно как карта выравнивания для текущего шага миграции.

## 1. Что считаем каноническим пользовательским shell

На уровне shell и глобальной навигации каноническими считаются:

1. `Home`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`
6. `Settings`

Быстрый action-entry из shell:

- `Gallery > Reports`

Не считаются отдельными пользовательскими страницами верхнего уровня:

- `Logs`
- `Diagnostics`
- `Content Storage`
- исторические service-alias вроде `Test Bench` и старых `service`-поверхностей

Важно:

- это не значит, что backend/routes/diagnostics исчезают;
- это значит, что они не должны конкурировать с продуктовым словарем shell.

## 2. Целевой продукт и текущая программная база

### Целевой продукт

Shell должен ощущаться как приложение с единым control language и давать прямой вход в:

- `Gallery`
- `Laboratory`
- `Settings`
- `Gallery > Reports`

Глубокая история действий должна жить в `Gallery > Reports`.
Локальные storage/service diagnostics не должны подменять собой `Gallery`.

### Текущая программная база

Текущая база все еще использует переходный словарь:

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

Эта база допустима как промежуточный слой, но больше не считается целевой shell-моделью.

## 3. Alias Policy

### `Laboratory`

Фиксируем:

- пользовательское имя: `Laboratory`
- внутренний route alias: `/service`
- допустимые исторические alias-названия в документации и комментариях к коду:
  - `Laboratory`
  - `Diagnostics`
  - `Test Bench`

Правило:

- в main shell, launcher, cards и navigation label использовать только `Laboratory`;
- `Laboratory` допустим как внутренний stage-term и route-alias, но не как основной label.

### `Gallery`

Фиксируем:

- пользовательское имя: `Gallery`
- owner scope: shared / virtual
- пользовательские вкладки:
  - `Plants`
  - `Media`
  - `Reports`

Правило:

- shell не должен выставлять отдельную страницу верхнего уровня `Content`;
- готовность хранилища и диагностика контента могут существовать отдельно, но как служебная внутренняя поверхность.

### `Settings`

Фиксируем:

- `Settings` остается отдельной постоянной страницей;
- `Settings` не дублирует laboratory controls;
- `Settings` не управляет составом laboratory tabs;
- `Settings` может показывать storage/sync/interface/function/style policies.

## 4. Что Делаем С `Content Storage`

Текущее состояние:

- route и diagnostics-страница полезны для проверки mirrored content readiness;
- но словарь `Content Storage` в верхнем уровне shell перегружает модель и конфликтует с `Gallery`.

Выбранное решение:

- `Gallery` остается единственным пользовательским разделом контента;
- сырая страница контента и хранилища сохраняется как внутренняя служебная поверхность;
- в пользовательском словаре использовать не `Content`, а максимум внутреннее `Storage Diagnostics`;
- shell может показывать только короткий summary:
  - local content ready / missing
  - peer content available / unavailable
  - quick entry в `Gallery`

Что это дает:

- не плодим отдельную пользовательскую сущность;
- не теряем полезную диагностическую поверхность;
- не смешиваем content tree с low-level storage inspection.

Если later-stage shell станет слишком перегруженным, `Storage Diagnostics` можно окончательно увести в:

- `Settings > Storage & Sync`
- или `Laboratory` diagnostics slice

Но не в основной навигации верхнего уровня.

## 5. Что Делаем С `Logs`, `Diagnostics` И `Reports`

Фиксируем:

- `Logs` не считаются отдельной продуктовой страницей;
- `Diagnostics` не считаются отдельной продуктовой страницей верхнего уровня;
- shell показывает только короткие сводки и указатели;
- канонический пользовательский просмотрщик истории действий и отчетов:
  - `Gallery > Reports`

Это означает:

- route `/#logs` может существовать временно;
- route `/#diagnostics` может существовать временно;
- но они должны считаться устаревающими поверхностями shell.

## 6. Заметка оператора

`Operator note` не выделяем в отдельный модуль, страницу или подсистему.

Фиксируем:

- `operator note` = тип note-payload, а не отдельная shell-сущность;
- note может создаваться внутри `Laboratory` как часть session/evidence слоя;
- позже note может создаваться и из product-facing flows вроде `Manual`;
- note попадает в `Gallery > Reports` только если оператор делает явный product-level export или если заметка относится к пользовательской истории действия, а не к внутреннему engineering trace.

Для report-level note-entry, который уже действительно экспортирован в `Gallery > Reports`, минимальная нагрузка такая:

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
- не смешиваем laboratory session notes с user-facing history автоматически.

## 7. Navigation Contract Decision

На уровне shell snapshot и shell UI целевыми считаем такие навигационные понятия:

- `home`
- `irrigation`
- `turret`
- `gallery`
- `laboratory`
- `settings`
- быстрый указатель на `gallery > reports`

Transition rule:

- текущая программная база временно может продолжать отдавать переходные ключи;
- но новые shell-изменения должны проектироваться уже вокруг `gallery` и `laboratory`, а не вокруг `content` и `service`.

## 7.1 Выравнивание `Home` и верхней панели

Помимо navigation keys платформа теперь должна держать единый `home / bar contract`.

Пользовательский смысл этого слоя:

- домашняя страница называется `Smart Platform`, а не `Platform Shell`;
- верхняя bar-панель становится главным носителем честных статусов;
- отдельный блок `Entry Context` на home screen убирается;
- большая часть технической детализации уходит в tooltip/status-sheet по hover, focus или tap.

Bar contract обязан одинаково трактоваться на обеих сторонах:

- слева: компактный домашний логомарк, переключатель настольного взаимодействия, переключатель полноэкранного режима, значок текущего клиента;
- в центре: постоянные ярлыки `Raspberry Pi` и `ESP32`, mode-chips только для реально доступных owner modules, moisture strip из 5 irrigation groups;
- справа: `Wi-Fi`, `Sync`, environmental and system indicators, language, time, date;
- safety interlocks, active failures и locked/degraded state должны быть видимы через shell-visible слой `snapshot.summaries.faults`, а не прятаться только в deep diagnostics;
- если данных нет, слот сохраняется, а индикатор уходит в честное серое состояние `no data`.

Важно:

- это не dashboard для сырых booleans и не место для `node_id`, `base_url` или `wifi: true / false`;
- определение клиентской стороны браузером остается эвристикой, а не аппаратным источником истины;
- `Laptop smoke` считается честным одноплатным testing path, а не третьим аппаратным владельцем.

## 7.2 Политика прямых логичных маршрутов

На карте выравнивания shell фиксируем еще одно правило:

- логичные маршруты, вводимые пользователем, не должны ломаться в сырой `404`, если shell знает соответствующий модуль;
- owner-local route открывается локально;
- peer-owned route переводит на federated handoff или blocked explanation;
- прямой ввод адреса должен быть совместим со словарем с учетом владельца, а не обходить его.

Практический вывод для миграции snapshot:

1. Добавить canonical navigation entries:
   - `gallery`
   - `laboratory`
   - `settings`
2. Сохранить старые keys только как временный слой совместимости.
3. Перевести tests на canonical model.
4. Только потом убирать устаревшие keys из code paths.

## 8. Карта миграции словаря

Текущая база -> целевой словарь shell:

- `Laboratory` -> `Laboratory`
- `Content` -> `Gallery`
- `Content Storage` -> internal `Storage Diagnostics`
- `Logs` -> `Gallery > Reports`
- `Diagnostics` -> shell summaries + `Laboratory`

Важно:

- это не map route-to-route;
- это карта пользовательской семантики.

Маршруты могут временно сохраняться такими:

- `/service`
- `/content`
- `/#logs`
- `/#diagnostics`

Но пользовательские подписи должны мигрировать раньше самих route aliases.

## 9. Безопасный Порядок Миграции

1. Зафиксировать docs и vocabulary.
2. Выровнять `shell_snapshot_contract` и snapshot tests.
3. Выровнять `raspberry_pi/shell_snapshot_facade.py` и `firmware_esp32/src/web/ShellSnapshotFacade.cpp`.
4. Выровнять shell HTML и подписи навигации верхнего уровня на обеих сторонах.
5. Только после этого углубляться в пользовательские `Gallery` и `Reports`.

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
