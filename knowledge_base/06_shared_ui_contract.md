# 06. Shared UI Contract

## Роль Файла

Этот файл должен фиксировать сквозные UI-решения: состояния, подсказки, радиусы, кнопки, fullscreen, bar, input helpers и другие общие контракты.

## Статус

- текущий статус: `active draft`

## Donor Источники Для Первого Переноса

- donor mapping для этого файла зафиксирован в `knowledge_base/17_open_questions_and_migration.md`;
- `chat_prompts/foundation_prompt.md` остается active companion source для shared wording and guardrails sync.

## Settled Truths

- общие решения фиксируются один раз и не переопределяются локально без причины
- сквозные радиусы, tooltip behavior, state semantics и control roles должны быть едиными

## 1. Общий Словарь Состояний

Единое ядро shared UI-state для всех user-facing surfaces:

- `online / ready`: узел, функция или путь доступны и готовы к нормальной работе;
- `active`: текущий выбранный режим, текущая активная операция или текущий фокус;
- `attention`: требуется внимание из-за деградации, pending-перехода или advisory-condition;
- `fault`: ошибка, unsafe failure или реальная неисправность;
- `neutral`: нет truthful data, нет подключения, нет настройки, simulated или idle без ошибки;
- `blocked`: элемент видим, но сейчас недоступен из-за внешнего контекста;
- `locked`: элемент намеренно ограничен policy, access или safety-цепью.

Жесткие правила:

- `active` не подменяет `online / ready`;
- `pending` обычно выражается через `attention` с явной причиной, а не отдельным state-государством;
- для общей shell-правды нельзя создавать параллельную цветовую семантику вроде `service-only` или `engineering-only`;
- truth о shared state идет backend-first и должна одинаково читаться на `Home`, в bar, в `Turret`, `Laboratory`, `Gallery` и `Settings`.

## 2. Blocked vs Locked

Для `blocked` и `locked` действуют общие правила:

- элемент остается видимым;
- причина не маскируется под безмолвный disabled-state;
- пользователь получает короткую причину и следующий шаг прямо на экране;
- tooltip, detail-layer или modal только углубляют объяснение.

Разница:

- `blocked` означает внешнее ограничение текущего контекста;
- `locked` означает явный запрет policy/access/safety.

Это правило распространяется на:

- launcher cards;
- buttons и segmented controls;
- chips и badges;
- inputs и field groups;
- local menus, tabs и section surfaces.

Desktop cursor language:

- `pointer` для обычного интерактивного действия;
- `help` для объясняемого `blocked`/`locked` состояния;
- `not-allowed` только для полностью недоступного элемента без объясняемого действия.

## 3. Tooltip Contract

Tooltip и layered feedback используют единый контракт:

- hover-tooltip появляется примерно через `500 ms`;
- сдвиг курсора больше чем на `3 px` до появления или во время hover закрывает или отменяет tooltip;
- без движения курсора tooltip может оставаться видимым примерно до `6 s`;
- browser-native tooltip и custom tooltip не должны жить одновременно на одном элементе;
- touch-surface не должна зависеть только от hover-механики;
- повторяющийся helper text не должен одновременно жить под control и в tooltip.

Layering rule:

- короткая причина и следующий шаг видны рядом с элементом или внутри карточки;
- tooltip и status-sheet дают расширенное объяснение;
- `toast` нужен для короткого подтверждения без смены контекста;
- `modal` нужен для подтверждений, предупреждений и маршрутов, которые нельзя тихо проигнорировать;
- pairing, handoff и similar blocking transitions могут использовать overlay.

Feedback timing:

- pressed-state должен быть видимым, но коротким: целевой коридор `150-220 ms`;
- первый пользовательский клик нельзя тихо тратить на побочный fullscreen-эффект или скрытую tooltip-side effect логику.

## 4. Buttons, Chips, Cards And Inputs

Базовые control roles:

- primary action;
- secondary action;
- warning action;
- dangerous action;
- quiet/subtle action.

Form selection roles:

- segmented control для `2-4` сразу видимых вариантов;
- dropdown/select для длинных или редких списков;
- toggle только для независимого `true/false`;
- mode-switch является вариантом segmented control, а не отдельной смысловой семьей.

Surface roles:

- launcher card;
- interactive card;
- status card;
- wizard/modal surface;
- summary/list card.

Нормативные различия:

- кнопка должна выглядеть как кнопка;
- launcher card должна выглядеть как launcher card;
- status label не должен имитировать button surface;
- toggle, checkbox, dropdown и tooltip не должны сливаться в один capsule pattern;
- legacy слово `tile` допустимо только как implementation alias и не считается канонической UI-сущностью.

## 5. Radii, Spacing, Density And Control Scale

Scale corridor для shared shell-language:

- внешний page padding: примерно `12-28 px`;
- внутренний card padding: примерно `14-20 px`;
- стандартный gap: примерно `10-16 px`;
- минимальная высота control-а: около `40 px` на desktop и `44 px` на touch;
- compact state chips: примерно `32-36 px` по высоте;
- иконки действий и состояний: примерно `16-20 px`.

Density contract:

- `Comfortable` — обычная продуктовая плотность;
- `Compact` — заметно более плотная рабочая раскладка для маленьких экранов и узких окон;
- compact mode сначала сокращает secondary values, chip density и вспомогательные тексты, а не главные статусы и действия;
- переход в `Compact` должен реально менять высоту controls, gaps и полезную площадь, а не делать косметическую разницу в `1-2 px`.

Radius baseline фиксируем как текущую рекомендованную норму, выведенную из существующего UI baseline:

- shell/input small radius: `14 px`;
- shared control radius: `18 px`;
- shell/card surface radius: `24 px`;
- stage/operator large radius: `30 px`;
- pill/chip radius: `999 px`;
- fully circular joysticks, knobs и round indicators: `50%`.

Operator HUD может локально использовать более крупный control radius, но не должен ломать shared state language.

## 6. Fullscreen, Home And Input Helpers

`Fullscreen`:

- это shared preference и shared runtime context;
- настройка живет в `Settings`;
- состояние отражается в bar-панели;
- fullscreen меняет плотность и рабочую раскладку, но не скрывает global bar;
- неожиданный browser-exit из fullscreen при навигации не должен молча переписывать preference в `false`;
- если браузер сбросил fullscreen, bar может показать `restore pending`, но восстановление запускается только явным действием пользователя.

`Home`:

- остается обязательным control в bar-панели;
- выполняет роль экстренного возврата на home surface;
- после возврата оболочка приходит к дефолтному состоянию, выбранному в `Settings`.

`Input helpers`:

- это shared preference между `Settings` и bar;
- оно относится только к FPV/operator actions в духе `ARM`-gate;
- оно не должно серить laboratory cards и не должно отключать `Laboratory`;
- поверхности, не использующие operator-input contract, не обязаны трактовать этот флаг как блокировку.

## 7. Shared Visual Tokens И Примеры

Global visual direction:

- интерфейс должен ощущаться как приложение, а не как россыпь HTML-страниц;
- page backgrounds могут быть атмосферными, но читаемость обеспечивается panel surfaces и overlays, а не blur на всем полотне;
- shell и `Gallery` могут быть более воздушными и product-like;
- `Laboratory` и operator/HUD surfaces могут быть плотнее и инженернее;
- темы могут менять атмосферу и фон, но не смысл цветовых состояний.

Theme contract:

- shell-level theme model использует именованные темы;
- переключение темы должно быть быстрым и не ломать navigation continuity;
- bar-панель может оставаться нейтральной shell-surface и не обязана полностью повторять page theme.

Operator HUD contract:

- `FPV/manual`, `Automatic FPV` и будущие operator panels используют `operator-hud` visual family;
- глобальная theme не должна случайно перекрашивать HUD controls в карточный UI;
- reusable CSS entry point для этого слоя: `raspberry_pi/web/static/operator_hud.css`;
- HUD может использовать local radius/panel tokens, но обязан сохранять truthful state и safety visibility.

## 8. Нормативные Примеры Кода И CSS Tokens

```css
:root {
  --sp-radius-input: 14px;
  --sp-radius-control: 18px;
  --sp-radius-card: 24px;
  --sp-radius-stage: 30px;
  --sp-radius-pill: 999px;

  --sp-page-padding-min: 12px;
  --sp-page-padding-max: 28px;
  --sp-card-padding-min: 14px;
  --sp-card-padding-max: 20px;
  --sp-gap-min: 10px;
  --sp-gap-max: 16px;

  --sp-control-min-height-desktop: 40px;
  --sp-control-min-height-touch: 44px;
  --sp-chip-height-compact: 34px;

  --sp-tooltip-delay-ms: 500;
  --sp-tooltip-cancel-move-px: 3;
  --sp-tooltip-timeout-ms: 6000;
  --sp-press-feedback-ms-min: 150;
  --sp-press-feedback-ms-max: 220;
}

.operator-hud {
  --sp-radius-control: 24px;
  --sp-radius-stage: 30px;
}
```

```css
.sp-control[aria-disabled="true"][data-state="blocked"],
.sp-card[aria-disabled="true"][data-state="blocked"] {
  cursor: help;
}

.sp-control[data-state="locked"],
.sp-card[data-state="locked"] {
  cursor: help;
}
```

```text
Blocked message pattern:
Короткая причина
Следующий шаг

Tooltip/detail:
Более подробное объяснение источника блокировки
```

## Cleanup Targets And Helper Convergence

Shared UI cleanup не должен создавать второй канон поверх этого файла.

Current cleanup targets:

- параллельные системы `data-state`, `data-tone` и class-only badges не должны выражать один и тот же смысл тремя разными способами;
- локальные tooltip engines с расходящимся timing/dismiss behavior должны сходиться к общему tooltip contract;
- разные fullscreen helpers, которые переизобретают один и тот же continuity path, должны сходиться к одному shared helper flow;
- `tile` может жить как implementation alias для компактной инженерной карточки, но не как отдельная каноническая UI-family.

Urgent attention signals:

- active blinking допустим только для реально идущего процесса или immediate safety attention, которое требует постоянного notice;
- operator HUD может использовать более сильный active emphasis, но обычная shell/page furniture не должна мигать ради декоративной заметности.

## Open Questions

- где проходит граница между нормативным token-contract и частным модульным стилем

## TODO

- собрать все сквозные UI-договоренности в одном месте
- довести shared helper для fullscreen и input-helper continuity
- провести cleanup-pass по общему словарю кнопок и карточек

## TBD

- финальный набор UI tokens для экспортируемого design standard
