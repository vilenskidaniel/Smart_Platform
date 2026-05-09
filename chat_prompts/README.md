# Chat Prompts

Этот каталог хранит канонические prompt-контракты для новых специализированных чатов по `Smart_Platform`.

Активный человеческий слой документации теперь должен начинаться с `knowledge_base/README.md`.

Старый donor-only слой считается только источником переноса смысла в новый канон и не должен использоваться как active reading path.

Использовать их нужно не как набор разрозненных подсказок, а как управляемую систему работы:

1. сначала общий фундамент;
2. затем эталонный структурный prompt;
3. затем prompt нужного модуля;
4. при пересечении нескольких модулей — отдельный cross-module prompt.

## Новая Архитектура Prompt-Системы

Канонический состав каталога:

- `foundation_prompt.md` — общая рабочая философия для всех новых чатов;
- `laboratory_prompt.md` — первый эталонный prompt, задающий структуру, глубину и метод работы;
- `platform_shell_prompt.md` — prompt для `Platform Shell` и bar/home/navigation слоя;
- `irrigation_prompt.md` — prompt для `Irrigation`;
- `turret_prompt.md` — prompt для `Turret`;
- `gallery_prompt.md` — prompt для `Gallery`;
- `settings_prompt.md` — prompt для `Settings`;
- `cross_module_prompt.md` — prompt для синтеза, связности идей, sync и межмодульных решений.

Практическое правило:

- каждый новый специализированный чат должен сначала принять `foundation_prompt.md`;
- `laboratory_prompt.md` служит структурным эталоном, а не образцом того, что все модули обязаны выглядеть как `Laboratory`;
- остальные prompt-файлы наследуют дисциплину этого эталона, но сохраняют свой продуктовый характер;
- для `Laboratory` пользовательский слой называется `Записи сессии`, а `Gallery > Reports` остается только для автономно и системно зафиксированных product-level событий;
- если задача реально задевает несколько продуктовых блоков, не пытаться решать все внутри одного модульного prompt-а: перейти в `cross_module_prompt.md`.

## Рекомендуемый Порядок Модульных Чатов

На текущем этапе безопаснее идти по одному крупному product block за чат:

1. `Platform Shell`
2. `Irrigation`
3. `Turret`
4. `Gallery`
5. `Laboratory`

После этого возвращаться в coordination/cross-module layer для:

- синтеза изменений между модулями;
- сверки ownership, handoff и sync semantics;
- подготовки live integration и финальной cleanup-волны.

Важно не путать:

- `Этап 2` master-plan может относиться к shell-stage;
- второй модульный чат после shell в этой очереди считается `Irrigation`.

## Общие Правила Для Всех Новых Prompt-Файлов

Каждый новый специализированный чат обязан удерживать следующие правила:

- сначала отделять `host launch`, `browser entry`, `module owner` и `current browser client`;
- не считать laptop smoke отдельным hardware owner;
- при отсутствии truthful data оставлять нейтральное состояние, а не выдумывать позитивный статус;
- начинать работу от большей структуры к меньшей детализации;
- сначала собирать skeleton или каркас, а непроработанные места помечать `TODO` или `TBD`, а не маскировать их под уже закрытые решения;
- использовать модель `keep / adapt / rewrite` для уже существующего кода, UI, docs и prompt-ов;
- если идея, правило или рабочее решение перенесены из старого слоя, старый конкурирующий источник нужно удалить, сократить или явно лишить статуса активной истины;
- не оставлять устаревшие исходники, prompt-ы, compatibility-описания или дублирующие слои как будто они равноправны новому канону;
- если из донора берется полезная идея, переносить ее через вырезку и замещение, а не через бесконечное копирование;
- проектная документация должна умнеть по ходу работы: новые договоренности нужно вносить в docs и prompt-слой, а не держать только в переписке;
- если задача трогает shared UI semantics, сначала открыть `knowledge_base/06_shared_ui_contract.md` и не придумывать локальный канон рядом с ним;
- новый чат должен активно задавать пользователю вопросы по функционалу, интерфейсу, логике, ограничениям и приоритетам, если это помогает нарастить каркас деталями;
- вопросы должны идти от общего к частному и помогать дорастить модуль, а не заставлять пользователя повторять уже установленную истину;
- после UI/JS edits проверять не только source, но и live-served asset на реальном порту;
- длинные JS-файлы править маленькими hunks в порядке следования кода;
- не переносить большие куски между `Raspberry Pi` и `ESP32` как будто это один и тот же implementation generation;
- инженерный режим открывает дополнительные функции, но не создает отдельную цветовую или смысловую систему состояний;
- не строить fullscreen/tooltips так, чтобы первый клик пользователя тратился на побочный effect и ломал основное действие;
- не оставлять browser-native tooltip параллельно custom tooltip;
- hover tooltip во всех shell-поверхностях появляется с задержкой около `500 ms`, располагается рядом с курсором или местом наведения, закрывается или отменяется сразу при сдвиге курсора больше `3 px` и не держится дольше `6 s`;
- короткая причина blocked/locked состояния и следующий шаг должны быть видимы прямо на экране, а tooltip нужен для подробностей;
- различие `blocked` и `locked` должно быть не только текстовым, но и визуальным;
- интерактивные настройки применяются optimistic-first: UI меняется сразу, сохранение уходит в debounce/background и не должно блокировать клики, ввод или переключение секций;
- выбранный язык должен применяться ко всему видимому тексту; дополнительные локали могут быть `TODO`-заглушками, если переводной модуль еще не заполнен;
- hardware modules, hardware components, software services и storage slices не смешиваются в одном списке;
- `Settings` не держит отдельную секцию `Platform Nodes`: физический quick status остается в bar-панели, а продуктовая связь с платами живет в `Modules`;
- `fullscreen` и `input helpers` считаются shared preferences: их truth живет в `Settings`, отражается в bar-панели и читается рабочими страницами;
- `Home` остается обязательным control bar-панели как экстренный возврат на главную страницу и переход к дефолтному состоянию оболочки, заданному в `Settings`;
- `Sync` в `Settings` управляется списком `selected_domains`: `Auto` включает все, ручное изменение переводит режим в `Manual review`;
- утвержденный sync-набор: service link, module state, shared preferences, reports/logs, plant library, media content (`photo/video/audio/gallery reports`), component registry, software versions (`RPi/ESP/Web UI`);
- `Plant Library` считается irrigation-linked storage slice и опирается на JSON-библиотеки в `content/libraries`;
- однотипные инженерные поля компонентов должны подсказывать ранее введенные значения;
- destructive storage actions идут только через preview/confirm flow и backend root-boundary checks;
- `offline` и `not connected` отображаются серым или neutral во всех shell-поверхностях; красный остается для настоящих `fault`, `error` и `blocked` состояний;
- keyboard action shortcuts работают только на странице ручного управления турелью, а не как глобальная навигация по буквам;
- если keyboard controls выключены, связанные настройки остаются видимыми disabled или серыми и объясняют причину в tooltip;
- если пользователь ограничил поверхность, например “только PC версия”, сначала решить именно этот slice;
- после regression сначала восстанавливать рабочее поведение на live page, а уже потом расширять scope.

## Как Выбирать Prompt

Используй такой порядок:

1. `foundation_prompt.md`
2. `laboratory_prompt.md`, если нужен эталон структуры и глубины
3. один модульный prompt по целевому блоку
4. `cross_module_prompt.md`, если решение затрагивает несколько модулей, синхронизацию, общие правила, prompt-слой или канонические docs

Если задача уже ушла в другой product-level блок, лучше открыть новый чат или перейти в cross-module режим, чем продолжать смешивать несколько больших поверхностей в одном модульном потоке.

## Что Читать Вместе С Prompt-Файлом

До старта нового чата полезно открыть:

- [knowledge_base/README.md](../knowledge_base/README.md)
- [README.md](../README.md)
- [WORKFLOW_FOR_OTHER_CHATS.md](../WORKFLOW_FOR_OTHER_CHATS.md)
- [knowledge_base/06_shared_ui_contract.md](../knowledge_base/06_shared_ui_contract.md)
- [knowledge_base/04_runtime_topology_controller_profiles_and_sync.md](../knowledge_base/04_runtime_topology_controller_profiles_and_sync.md)
- [knowledge_base/05_shell_navigation_and_screen_map.md](../knowledge_base/05_shell_navigation_and_screen_map.md)
- [shared_contracts/shell_snapshot_contract.md](../shared_contracts/shell_snapshot_contract.md)

Этого достаточно, чтобы новый чат не повторял уже пройденные ошибки по launch flow, bar regressions, fullscreen restore, stale browser assets и устаревшим prompt-слоям.
