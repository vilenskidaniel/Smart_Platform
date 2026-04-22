# Smart Platform Home / Bar Chat Bootstrap Prompt

Этот файл нужен для отдельного модульного чата, который занимается только домашней страницей `Smart Platform`, верхней bar-панелью, launcher-card логикой, home navigation и связанными status rules.

## Что Это За Чат

Этот чат отвечает за:

- home screen `Smart Platform` как app-like launcher;
- persistent top bar, которая живет на всех страницах;
- visual contract между logomark, buttons, status-labels, cards, dropdowns и tooltips;
- truthful status behavior для `Raspberry Pi`, `ESP32`, current client, `Wi-Fi`, `Sync`, environment, battery, language, time и date;
- irrigation moisture strip на 5 групп в центральной части bar-панели;
- one-line compact grouping order: controls -> devices -> irrigation -> sensors -> system;
- desktop edge-to-edge bar behavior с равным внешним отступом и адаптивным распределением места между группами;
- home-card hierarchy для `Irrigation`, `Turret`, `Gallery`, `Laboratory`, `Settings`;
- unified desktop + touch interaction model для bar hints, hover, tap и fullscreen helpers;
- i18n-ready home/navigation layer.

Этот чат не должен по умолчанию уезжать в глубокую проработку самих продуктовых модулей, если home/bar слой можно исправить отдельно.

## Что Считать Источником Правды

Перед работой в этом чате сначала читать:

1. `docs/05_ui_shell_and_navigation.md`
2. `docs/40_system_shell_navigation_alignment.md`
3. `docs/39_design_decisions_and_screen_map.md`
4. `briefs/web_shell_ui.md`
5. актуальные home and page templates в `raspberry_pi/web/` и `firmware_esp32/data/`

## Главные Правила Для Этого Чата

1. Домашняя страница называется `Smart Platform`, а не `System Shell`.
2. Верхняя bar-панель несет правдивые статусы и быстрые controls.
3. Отдельный блок `Entry Context` на home screen не возвращается.
4. Подробные статусы не должны жить россыпью больших карточек на главной странице.
5. Home surface показывает только главные пользовательские действия:
   - `Irrigation`
   - `Turret`
   - `Gallery`
   - `Laboratory`
   - `Settings`
6. `Turret` на home screen держит две внутренние action-кнопки: `Manual Control` и `Automatic Control`.
7. `Reports` не живут на home screen и открываются через `Gallery`.
8. UI не должен смешивать в одном visual role button, status-pill, launcher-card и diagnostic dump.
9. Если данных нет, bar сохраняет slot и показывает честное серое состояние вместо выдуманных значений.
10. Текущий browser client можно показывать, но нельзя выдумывать несуществующие remote client sessions.
11. Compact bar остается однострочной на desktop и не возвращает нижнюю detail-strip с дублирующим текстом.
12. В видимом слое bar предпочтительны icon + short value; полные названия и объяснения уходят в tooltip / compact hint.
13. В laptop smoke controlling boards остаются серыми, а active desktop client может подсвечиваться синим как реальная viewing surface.
14. `Raspberry Pi` и `ESP32` используют разные board-icons.
15. Soil-zone names и будущие plant descriptions живут в tooltip, а не раздувают саму bar.
16. При снижении ширины bar сначала уплотняется, а затем может переходить в stacked / multi-row режим вместо постоянного horizontal scroll.
17. `Settings` и `Laboratory` не должны деградировать в shallow pages только потому, что home/bar слой стал компактнее.

## Что Нельзя Делать

- возвращать на лицо интерфейса `System Shell` как название домашней страницы;
- выводить на home screen `node_id`, `base_url`, raw booleans и другие служебные поля;
- путать состояния модулей, current client и controlling boards;
- делать все элементы одинаковыми pill-кнопками;
- держать на главной странице логи, reports summary или oversized diagnostic cards;
- имитировать, будто laptop smoke является отдельным hardware owner;
- смешивать английский и русский на одном экране без реального language-switch context.

## Если Задача Уходит В Соседний Блок

Явно фиксируй границу и выноси работу в отдельный модульный чат.

Примеры таких границ:

- deep irrigation product logic -> отдельный Irrigation chat;
- turret runtime, FPV and action behavior -> отдельный Turret chat;
- gallery reports and media structure -> отдельный Gallery chat;
- laboratory workflows and checklists -> отдельный Laboratory chat;
- sync semantics and mirrored content policy -> отдельный sync-focused chat.

## Хорошие Первые Задачи Для Такого Чата

1. Audit home page against the current UX contract.
2. Redesign the top bar with truthful board, client and system indicators.
3. Remove technical copy and diagnostic cards from the home screen.
4. Rebuild main launcher cards and central action hierarchy.
5. Propagate the same bar and visual control logic to `Gallery`, `Laboratory`, `Turret` and `Settings`.