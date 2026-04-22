# Field Onboarding And Operations

Этот документ собирает user-facing и operator-facing практику, которая не должна оставаться спрятанной в legacy `ТЗ`.

Он закрывает четыре больших области:

- first-run и onboarding;
- field entry и board discovery;
- service / maintenance routines;
- installation и normal operation expectations.

## 1. Цель документа

Нужен единый practical guide для того, как система входит в жизнь пользователя и оператора:

- как впервые открыть shell;
- как выглядит board presence;
- как проходит owner-aware handoff;
- как зайти в `Laboratory` и безопасно выполнить service-step;
- как отделять normal operation от maintenance.

## 2. Что должно быть описано здесь

### 2.1 First Run Flow

- первый доступ к узлу;
- сеть и browser entry;
- минимальная регистрация / узнавание board identity;
- переход от одиночного узла к dual-board конфигурации.

### 2.2 Shell Entry Expectations

- что пользователь видит на `Home`;
- как отображаются текущий узел и peer;
- как работают заблокированные peer-owned разделы;
- как объясняется owner-aware handoff.

### 2.3 Field Operation

- normal daily use;
- manual entry в `Irrigation`, `Turret`, `Gallery`, `Laboratory`;
- поведение при потере peer-узла;
- правила работы в single-board и dual-board режимах.

### 2.4 Service And Maintenance

- безопасный вход в `Laboratory`;
- preflight;
- hardware bring-up order;
- maintenance window;
- post-service review через `Gallery > Reports`.

### 2.5 Installation Expectations

- что нужно подтвердить перед установкой;
- какие hardware family требуют отдельной квалификации;
- какие power / network / mounting assumptions должны быть проверены до product-use.

## 3. Что не должно жить только здесь

- hardware source of truth остается в workbook `docs/smart_platform_workshop_inventory.xlsx`;
- safety и failure matrix живут в `docs/46_safety_risk_and_failure_matrix.md`;
- acceptance criteria живут в `docs/47_acceptance_and_validation_matrix.md`.

## 4. Ближайшая задача заполнения

Сюда нужно мигрировать из legacy `ТЗ` и donor-опыта:

- first-run / browser-entry сценарии;
- installation и эксплуатационные ожидания;
- service-процедуры, которые сейчас размазаны между `ТЗ`, readiness notes и donor UX.

## 5. Рабочая модель для `v1`

Из legacy `ТЗ` здесь полезны не конкретные старые экраны, а логика входа и эксплуатации.

Для `Smart Platform v1` фиксируем такую адаптированную модель:

- система остается browser-first;
- первый вход возможен с телефона прямо в shell соответствующего узла;
- единый UX достигается не одним "магическим" URL, а одинаковым shell-language и owner-aware handoff;
- отсутствие peer-узла должно быть видно сразу;
- `Laboratory` считается штатной частью жизненного цикла, а не только разработческой лазейкой.

## 6. First Run И Первый Вход

### 6.1 Базовый путь, который нужен уже сейчас

Для первых реальных проходов и hardware bring-up достаточно такого пути:

1. открыть shell доступного узла в браузере телефона;
2. убедиться, что верхний слой shell показывает identity текущей платы;
3. увидеть статус peer-узла как присутствующий или отсутствующий;
4. перейти в `Home`, затем в `Laboratory` или продуктовый раздел;
5. получить честную owner-aware картину доступных и заблокированных модулей.

Это уже лучше старой идеи с "единым центральным адресом", потому что не ломает federated ownership.

### 6.2 Что стоит забрать из legacy `ТЗ`

Полезные идеи из старого документа:

- `SoftAP / setup` путь для первичной настройки сети;
- QR как быстрый способ открыть локальный URL или onboarding entry point;
- явная индикация режима сопряжения или bootstrap-состояния;
- mobile-first вход без требования нативного приложения.

Для текущего `v1` это уже можно трактовать практично:

- desktop host поднимает shell и может сразу показать QR entry popup;
- phone открывает тот же shell URL через камеру без отдельного launcher-файла;
- viewer presence и shell ribbon затем сами показывают, что в систему вошел еще один клиент.

### 6.3 Что не фиксируем как обязательную норму

Не переносим как обязательный baseline:

- один производственный логин/пароль на устройство;
- автоматическую авторизацию через QR как security-модель;
- единственный общий URL для всех узлов;
- `Telegram` как обязательный канал для первого запуска.

Лучший вариант для `v1`:

- QR и `SoftAP` оставить как onboarding convenience layer;
- transport identity, shell ribbon и owner-aware routing считать обязательным baseline;
- full user-facing onboarding wizard считать отдельным поздним product slice.

## 7. Shell Entry Expectations

### 7.1 Что пользователь должен видеть сразу

При открытии shell на любом узле пользователь должен сразу понимать:

- на какой плате он находится сейчас;
- доступен ли peer;
- какие модули локальны;
- какие модули peer-owned;
- почему часть маршрутов заблокирована.

### 7.2 Что должно оставаться видимым при деградации

- `Turret` остается видимой на `ESP32`, даже если владелец недоступен;
- `Irrigation` остается видимым на `Raspberry Pi`, даже если `ESP32` пропал;
- `Gallery` должна открывать локальный slice даже при потере peer;
- `Laboratory` должна сохранять board context и показывать, что реально можно тестировать в текущем состоянии.

### 7.3 Лучшая адаптация старых UX-идей

Из old UX worth keeping:

- blocked routes должны быть не скрыты, а честно объяснены;
- pairing / connecting overlay может использоваться как transient status layer;
- mobile-first и app-like поведение важнее page-reload website feeling.

Из old UX лучше не переносить как догму:

- отдельную `Видеотеку` как верхнеуровневый канон;
- жёсткую привязку к старому набору страниц `catalog.html`, `video.html` и т.д. как к финальной IA;
- избыточную привязку к конкретным анимациям, media filenames и Telegram-полям в `Settings`.

## 8. Field Operation

### 8.1 Single-Board `ESP32`

В этом режиме пользователь и оператор должны получать:

- `Irrigation` как полноценный локальный продуктовый модуль;
- локальный `Gallery` slice для irrigation/history/report artifacts;
- `Laboratory` с локальными irrigation и `strobe_bench` slices;
- видимую, но заблокированную `Turret` ветку с причиной блокировки.

### 8.2 Single-Board `Raspberry Pi`

В этом режиме нужны:

- `Turret` как локальный owner module;
- `Gallery` с локальным media/report slice;
- `Laboratory` с turret-owned и peer-waiting slices;
- честно деградированный `Irrigation` entry.

### 8.3 Dual-Board Operation

Когда обе платы доступны:

- shell на любом узле показывает обе платы;
- peer-owned маршруты открываются через handoff, а не через притворство локальным owner;
- глобальные UI settings и snapshot-состояния синхронизируются;
- `Gallery` становится mixed-source пространством;
- `Laboratory` показывает связанный preflight и рекомендуемый следующий bring-up шаг.

## 9. Service And Maintenance

### 9.1 Безопасный вход в `Laboratory`

Service-path должен включать:

- явный вход в `Laboratory`;
- preflight / readiness перед запуском актуаторов;
- разделение product-owner и service-only slices;
- post-action evidence через `Gallery > Reports`.

### 9.2 Канонический порядок bring-up

Для реальных hardware sessions используем такой порядок:

1. shell and reports smoke;
2. peer visibility and handoff;
3. `ESP32 / Strobe Bench`;
4. `ESP32 / Irrigation Service`;
5. `Raspberry Pi / Turret Service`;
6. experimental `Laboratory` profiles;
7. review in `Gallery > Reports`.

### 9.3 Maintenance Windows

Во время обслуживания система должна различать:

- normal operation;
- service session;
- emergency stop / interlock state.

Важное правило:

- maintenance и calibration не должны молча менять глобальное product behavior без явного подтверждения.

## 10. Installation Expectations

Перед product-use должны быть подтверждены:

- отдельные power boundaries для логики и силовых актуаторов;
- физическая доступность emergency interlock для turret-sensitive групп;
- разделение irrigation water path и turret water path;
- наличие корректного local storage, если на него опираются `Gallery` и history;
- сетевой reachable path хотя бы до одного shell entry point;
- честная маркировка отсутствующих hardware families в `Laboratory`.

## 11. Periodic Operations And Checks

Регулярная эксплуатация должна включать:

- проверку состояния peer-link и owner handoff;
- проверку storage headroom и report visibility;
- калибровку и sensor sanity-check по мере необходимости;
- осмотр water paths и interlock-состояний;
- review последних pass/fail/warn записей в `Gallery > Reports`.

## 12. Итог Extraction Pass Для Этого Документа

Из legacy `ТЗ` реально сохранены как полезные знания:

- browser-first entry;
- mobile-first shell;
- `SoftAP` / QR bootstrap как хорошие идеи;
- pairing / connecting status как явный UX слой;
- сценарии single-device и dual-device работы.

Из legacy `ТЗ` сознательно не перенесены как норма:

- общая central-address модель;
- fixed credentials;
- обязательный `Telegram` onboarding;
- старая page-map vocabulary.