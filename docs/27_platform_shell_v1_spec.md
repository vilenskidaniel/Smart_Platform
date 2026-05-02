# Platform Shell V1 Spec

Этот документ открывает помодульную проработку `v1`.

Он описывает только продуктовый блок `Platform Shell`.

## 1. Назначение

`Platform Shell v1` — это общая оболочка, через которую пользователь входит в платформу и понимает:

- какие узлы доступны;
- какие модули доступны;
- кто владеет модулем;
- куда пойдет команда;
- почему что-то заблокировано.

## 2. Что должен дать `Platform Shell v1`

После его завершения пользователь должен уметь:

1. Открыть shell на `ESP32` или `Raspberry Pi`.
2. Узнать состояние обоих узлов.
3. Увидеть одни и те же продуктовые разделы.
4. Понять, какой раздел локальный, а какой peer-owned.
5. Без путаницы перейти к владельцу нужного раздела.
6. Открыть `Настройки`, `Gallery` и `Laboratory`.
7. Из shell быстро попасть в `Gallery > Reports` как в главный viewer истории действий.
8. Понять причину `locked/degraded/fault`.
9. Узнать, готово ли content-хранилище на текущем узле и какие content-источники доступны.

## 3. Обязательные shell surfaces

### `Главная`

Показывает:

- карточку `ESP32`;
- карточку `Raspberry Pi`;
- доступность `Полив`;
- доступность `Турель`;
- быстрый переход в `Laboratory`;
- быстрый переход в `Gallery`;
- активные предупреждения;
- handoff-подсказки.

### `Настройки`

В `v1` достаточно:

- язык;
- глобальный переключатель `EN / RU`;
- тема;
- базовые сетевые параметры;
- базовые owner/shell адреса;
- задел под будущую авторизацию.

Важно:

- `Settings` — отдельная persistent page;
- `Settings` не должны дублировать лабораторные тестовые controls;
- лабораторные эксперименты не должны неявно подчиняться пользовательским product-settings, кроме обязательных safety/hardware interlocks.

Default language:

- `EN`

### Activity Summary

Показывает:

- короткую shell-level summary недавней активности;
- важные аварии;
- ручные действия высокого уровня;
- быстрый вход в `Gallery > Reports`.

Важно:

- отдельная продуктовая страница `Diagnostics` больше не считается обязательной shell-сущностью;
- отдельная верхнеуровневая страница `Logs` тоже больше не считается обязательной user-facing shell-сущностью;
- shell-level diagnostics должны жить в summary-cards на `Главной`, в коротких activity summaries и в `Laboratory`;
- глубокая история действий и отчетов должна открываться через `Gallery > Reports`.

## 4. Поведение `Главная -> Полив`

- если `ESP32` доступен, раздел активен;
- если пользователь уже на `ESP32`, переход локальный;
- если пользователь на `Raspberry Pi`, shell предлагает owner-aware handoff к irrigation-owner;
- если `ESP32` недоступен, раздел виден, но заблокирован или деградирован.

## 5. Поведение `Главная -> Турель`

- если `Raspberry Pi` доступен, раздел активен;
- если пользователь уже на `Raspberry Pi`, переход локальный;
- если пользователь на `ESP32`, shell предлагает handoff к turret-owner;
- если `Raspberry Pi` недоступен, раздел виден, но заблокирован.

## 6. Поведение `Gallery`

`Gallery` в shell открывается как shared virtual explorer без одного owner.

Это означает:

- shell открывает одну user-facing страницу `Gallery`;
- локальный узел всегда может показать свой local content slice;
- peer-content подключается как дополнительный источник, а не как owner всей страницы;
- если peer-owner недоступен, `Gallery` не скрывается и не ломается, а помечает недоступные source-groups;
- `Gallery > Reports` считается каноническим user-facing просмотрщиком истории действий из `Laboratory` и ручных режимов;
- storage/service route вроде `Content Storage` можно держать отдельно как internal diagnostics surface, но не как замену `Gallery`.

## 7. Поведение `Laboratory`

`Platform Shell v1` не должен исполнять тестовые команды сам.

Он должен:

- показывать доступные test/service страницы;
- разделять локальные и peer-owned сервисные страницы;
- честно отправлять пользователя к владельцу модуля.

Важно:

- `Laboratory` является каноническим именем инженерного контура, который включает diagnostics и test-bench slices;
- user-facing имя этого контура: `Laboratory`;
- внутренний route/stage-term может оставаться `/service` и legacy alias `service_test`;
- `Laboratory` должна ощущаться tab-based app-like страницей, а не набором backend-route экранов.

## 8. Что считается ошибкой дизайна

Признаки плохого `Platform Shell v1`:

- пользователь не понимает, на каком узле он сейчас находится;
- пользователь не понимает, почему раздел серый;
- shell скрывает peer-owned разделы полностью;
- shell открывает peer-owned команды так, будто он их хозяин;
- shell заставляет пользователя читать внутренние runtime-термины для простой навигации;
- shell показывает `Content Storage` как главный пользовательский контент-раздел вместо `Gallery`;
- shell разводит `Diagnostics` и `Laboratory` как две разные верхнеуровневые страницы, хотя для пользователя это одна сущность.

## 9. Минимальные данные, которые нужны shell

От платформы shell ожидает:

- `node status`
- `module registry`
- `owner_node_id`
- `owner_available`
- `canonical_url`
- `federated_access`
- `active mode`
- `fault summary`
- `gallery source availability`
- `recent activity summary`
- `emergency power interlock state`

Этого достаточно для `v1`.

## 9.1. Canonical Surface Map

Чтобы следующий implementation-чат не домысливал навигацию заново, фиксируем базовую карту surface-level маршрутов.

| User-facing surface | Backing module or layer | Owner scope | Canonical path | Route mode | Primary evidence path |
| --- | --- | --- | --- | --- | --- |
| `Home / Platform Shell` | `platform_shell` | `shared` | `/` | local shell | activity summary + `Gallery > Reports` |
| `Irrigation` | `irrigation` | `io_node` | `/irrigation` | local or handoff | irrigation reports / gallery reports |
| `Turret` | `turret_bridge` | `compute_node` | `/turret` | local or handoff | turret reports / gallery reports |
| `Gallery` | shared virtual section | `shared` | `/gallery` | virtual shared explorer | `Plants`, `Media`, `Reports` |
| `Reports` quick entry | `logs` summary path | `shared` | `/gallery?tab=reports` | shared viewer shortcut | canonical history viewer |
| `Laboratory` | `laboratory` + owner-specific service slices | `shared entry + owner execution` | `/service` | local workspace + owner-aware tools | readiness + `Gallery > Reports` |
| `Settings` | `settings` | `shared` | `/settings` | local persistent page | settings audit trail later |

Важно:

- не каждая user-facing surface обязана иметь отдельный runtime module id один-к-одному;
- но каждая поверхность обязана иметь canonical path, owner semantics и понятный evidence path.

## 10. Что пока не обязательно

Для `Platform Shell v1` пока не обязательно:

- полный reverse-proxy peer-owned страниц;
- идеальный real-time push;
- сложная авторизация;
- сложная персонализация интерфейса;
- тяжелая анимация и декоративные эффекты.

## 11. Критерий завершения

`Platform Shell v1` можно считать достаточно зрелым, когда:

- обе стороны показывают одинаковый shell;
- handoff понятен и предсказуем;
- `Полив`, `Турель`, `Gallery`, `Laboratory` и `Settings` видны из любой точки входа;
- быстрый вход в `Gallery > Reports` доступен из shell без поиска по внутренним service-route;
- блокировки и деградация читаются без расшифровки внутренних терминов;
- пользователь понимает систему как единый продукт.
