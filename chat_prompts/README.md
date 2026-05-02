# Chat Prompts

Этот каталог хранит bootstrap prompt-файлы для новых модульных чатов.

Использовать их нужно не как произвольные “идеи для разговора”, а как рабочие контракты для следующей сессии.

## Как Выбирать Prompt

- `laptop_ui_testing_chat_bootstrap_prompt.md` — laptop smoke, launch flow, local browser testing;
- `smart_platform_home_bar_chat_bootstrap_prompt.md` — home page, shared top bar, launcher cards, tooltip/fullscreen behavior;
- `gallery_settings_sync_chat_bootstrap_prompt.md` — cross-node continuity для `Gallery` и `Settings`;
- `settings_architecture_refactor_chat_bootstrap_prompt.md` — Settings page architecture refactor: runtime/viewer/node model, shared Smart Bar status/tooltip behavior, sync/storage/preferences separation, module/component configuration;
- остальные prompt-файлы — по своему модульному блоку.

Если задача уже ушла в другой product-level блок, лучше открыть новый чат, чем продолжать смешивать несколько больших поверхностей в одном.

## Общие Guardrails Для Всех Prompt-Файлов

Каждый новый модульный чат должен удерживать следующие правила:

- сначала отделять `host launch`, `browser entry`, `module owner` и `current browser client`;
- не считать laptop smoke отдельным hardware owner;
- при отсутствии truthful data оставлять нейтральное состояние, а не выдумывать позитивный статус;
- после UI/JS edits проверять не только source, но и live-served asset на реальном порту;
- длинные JS-файлы править маленькими hunks в порядке следования кода;
- не переносить большие куски между `Raspberry Pi` и `ESP32` как будто это один и тот же implementation generation;
- не строить fullscreen/tooltips так, чтобы первый клик пользователя тратился на побочный effect и ломал основное действие;
- не оставлять browser-native tooltip параллельно custom tooltip;
- hover tooltip во всех shell-поверхностях появляется с задержкой около `500 ms`, располагается рядом с курсором/местом наведения, закрывается/отменяется сразу при сдвиге курсора больше `3 px` и не держится дольше `6 s`;
- интерактивные настройки применяются optimistic-first: UI меняется сразу, сохранение уходит в debounce/background и не должно блокировать клики, ввод или переключение секций;
- выбранный язык должен применяться ко всему видимому тексту; дополнительные локали могут быть TODO-заглушками, если переводной модуль еще не заполнен;
- hardware modules, hardware components, software services и storage slices не смешиваются в одном списке;
- `Settings` не держит отдельную секцию `Platform Nodes`: физический quick status остаётся в bar-панели, а продуктовая связь с платами живёт в `Modules`;
- `Sync` в `Settings` управляется списком `selected_domains`: `Auto` включает всё, ручное изменение переводит режим в `Manual review`;
- утверждённый sync-набор: service link, module state, shared preferences, reports/logs, plant library, media content (`photo/video/audio/gallery reports`), component registry, software versions (`RPi/ESP/Web UI`);
- `Plant Library` считается irrigation-linked storage slice и опирается на JSON-библиотеки в `content/libraries`;
- однотипные инженерные поля компонентов должны подсказывать ранее введённые значения;
- destructive storage actions идут только через preview/confirm flow и backend root-boundary checks;
- `offline`/`not connected` отображается серым/neutral во всех shell-поверхностях; красный остаётся для настоящих `fault/error/blocked` состояний;
- keyboard action shortcuts работают только на странице ручного управления турелью, а не как глобальная навигация по буквам;
- если keyboard controls выключены, связанные настройки остаются видимыми disabled/серыми и объясняют причину в tooltip;
- если пользователь ограничил поверхность, например “только PC версия”, сначала решить именно этот slice;
- после regression сначала восстанавливать рабочее поведение на live page, а уже потом расширять scope.

## Что Читать Вместе С Prompt-Файлом

До старта нового чата полезно открыть:

- [README.md](../README.md)
- [WORKFLOW_FOR_OTHER_CHATS.md](../WORKFLOW_FOR_OTHER_CHATS.md)
- [docs/48_browser_entry_and_host_launch.md](../docs/48_browser_entry_and_host_launch.md)
- [docs/49_shell_runtime_and_chat_guardrails.md](../docs/49_shell_runtime_and_chat_guardrails.md)

Этого достаточно, чтобы новый чат не повторял уже пройденные ошибки по launch flow, bar regressions, fullscreen restore и stale browser assets.
