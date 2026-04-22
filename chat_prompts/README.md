# Chat Prompts

Этот каталог хранит bootstrap prompt-файлы для новых модульных чатов.

Использовать их нужно не как произвольные “идеи для разговора”, а как рабочие контракты для следующей сессии.

## Как Выбирать Prompt

- `laptop_ui_testing_chat_bootstrap_prompt.md` — laptop smoke, launch flow, local browser testing;
- `smart_platform_home_bar_chat_bootstrap_prompt.md` — home page, shared top bar, launcher cards, tooltip/fullscreen behavior;
- `gallery_settings_sync_chat_bootstrap_prompt.md` — cross-node continuity для `Gallery` и `Settings`;
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
- если пользователь ограничил поверхность, например “только PC версия”, сначала решить именно этот slice;
- после regression сначала восстанавливать рабочее поведение на live page, а уже потом расширять scope.

## Что Читать Вместе С Prompt-Файлом

До старта нового чата полезно открыть:

- [README.md](../README.md)
- [WORKFLOW_FOR_OTHER_CHATS.md](../WORKFLOW_FOR_OTHER_CHATS.md)
- [docs/48_browser_entry_and_host_launch.md](../docs/48_browser_entry_and_host_launch.md)
- [docs/49_shell_runtime_and_chat_guardrails.md](../docs/49_shell_runtime_and_chat_guardrails.md)

Этого достаточно, чтобы новый чат не повторял уже пройденные ошибки по launch flow, bar regressions, fullscreen restore и stale browser assets.