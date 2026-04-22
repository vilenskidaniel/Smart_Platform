# Shell Runtime And Chat Guardrails

Этот документ фиксирует практические выводы из живых shell/home/bar/laptop сессий, где работа уже шла не только по docs, но и по реальному коду, browser behavior, launcher flow и regression recovery.

Он нужен, чтобы следующие чаты не повторяли одни и те же ошибки:

- не смешивали `host launch` и `browser entry`;
- не ломали shared bar крупными хрупкими patch-блоками;
- не считали source-файл достаточной проверкой после UI edits;
- не теряли truthful runtime semantics между `ESP32`, `Raspberry Pi`, laptop smoke и viewer device;
- не строили fullscreen/tooltips так, чтобы первый клик пользователя расходовался на побочный эффект вместо целевого действия.

## 1. Runtime Truth

В shell и user-facing pages нужно отдельно различать как минимум четыре сущности:

1. host node, который поднял shell-server;
2. module owner, который реально владеет функцией;
3. current browser client, который сейчас смотрит страницу;
4. entry context, через который пользователь вошел в систему.

Практические правила:

- `browser entry` и `host launch` — это разные слои, даже если на `Windows` они часто идут подряд;
- desktop smoke path не делает laptop отдельным hardware owner;
- current browser client можно выделять как active viewing surface, но нельзя выдавать его за owner board;
- если есть `runtime_profile`, `viewers` или другой более сильный runtime source, он важнее голых loopback-эвристик;
- если truthful data нет, интерфейс держит slot и показывает нейтральное состояние, а не выдумывает наличие peer, battery, sync readiness или sensor value.

## 2. Entry Model

Для `Smart Platform` уже подтверждена такая модель:

- `ESP32` может поднимать свой shell;
- `Raspberry Pi` может поднимать свой shell;
- laptop может поднимать smoke-host shell;
- остальные устройства входят через браузер по URL опубликованного shell.

Из этого следуют обязательные ограничения:

- нельзя сводить всю систему к одному “магическому ярлыку”;
- `Windows launcher` — это convenience only для host-side entry;
- phone/tablet/desktop clients должны входить через browser URL, а не через локальные launch-файлы;
- docs и prompts должны явно отделять “как поднять shell” от “как открыть shell с другого устройства”.

## 3. Implementation Guardrails

При работе над shell/home/bar и другими shared UI слоями:

- начинать с owning file или runtime surface, а не с широкого repo tour;
- если есть живой problem file, сначала читать его локальный контур, а не соседние подсистемы;
- для длинных JS-файлов делать маленькие patch-hunks в порядке следования кода;
- не смешивать в одном patch ранние и поздние области длинного файла, если можно пройтись по ним последовательно;
- не копировать крупные блоки между `Raspberry Pi` и `ESP32` вслепую: эти реализации могут быть разными поколениями одного UI слоя;
- если на одном узле уже есть нужный helper или state-layer, лучше расширять его, чем создавать второй параллельный контур.

Особенно важно для shared bar:

- bar считается общей инфраструктурой и проверяется не только на home page;
- после правки нужно смотреть минимум `Home`, `Gallery`, `Laboratory`, `Settings`, `Turret` и соответствующий compact/shared top bar behavior;
- summary tokens не должны сваливаться в длинную plain-text простыню, если внутри уже есть grouped data;
- custom tooltip и native browser tooltip не должны жить одновременно на одном control/token.

## 4. Validation Ladder

После существенной UI/JS правки нельзя останавливаться на чтении кода или diff.

Минимальный порядок проверки такой:

1. `get_errors` по измененному файлу;
2. проверка, что live-server реально отдает новую версию измененного asset;
3. узкий behavior check на рабочем порту;
4. только потом соседние доработки.

Практические выводы:

- stale browser cache может полностью исказить вывод о том, “сработала правка или нет”;
- для shared JS полезно проверять не только source-file, но и live-served content;
- для browser-first shell удобны быстрые headless/DOM smoke checks на реальном URL;
- если после первой правки сразу появилась regression, сначала чинится этот же slice, а не открывается новая тема в соседнем файле.

## 5. Browser Behavior Guardrails

Fullscreen, navigation и tooltip logic должны уважать ограничения браузера, а не только намерение разработчика.

Подтвержденные правила:

- fullscreen continuity across navigation — это best-effort, а не магическая гарантия;
- механизм восстановления fullscreen не должен красть первый пользовательский клик у ссылки, кнопки или другого control;
- если restore-path требует interaction, он не должен заставлять пользователя делать обязательный второй клик ради изначального действия;
- hover/tap/click подсказки не должны давать одновременно browser-native и custom tooltip;
- grouped tooltip content должно быть структурировано строками/секциями, а не идти одной длинной фразой.

## 6. Collaboration Guardrails

Для этих чатов подтвердились такие рабочие правила коммуникации:

- когда проблема уже локализована, пользователь ожидает действие, а не длинный proposal-only ответ;
- на audit/planning шаге полезен доступный язык и несколько точных вопросов для развилки;
- когда пользователь явно ограничивает поверхность, например “работать только с PC версией”, scope нельзя снова размывать;
- если пользователь показывает screenshot или описывает конкретный runtime symptom, приоритет у этой реальности, а не у абстрактной теории;
- после recovery/regression важно явно зафиксировать, что уже исправлено, что еще pending и на каком live port это подтверждено.

## 7. Когда Обновлять Docs И Prompts

Эти guardrails нужно переносить в docs/prompt layer, если меняется хотя бы одно из условий:

- entry contract между `ESP32`, `Raspberry Pi`, laptop smoke и browser clients;
- top bar/shared shell semantics;
- truthful status model для owner/client/viewer/runtime profile;
- fullscreen, mobile orientation или device-specific interaction contract;
- startup/launcher flow для `Windows` host и phone entry;
- validation workflow для shared UI assets.

Практический минимум:

- product/runtime contract идет в `docs/`;
- cross-chat operating rules идут в [WORKFLOW_FOR_OTHER_CHATS.md](../WORKFLOW_FOR_OTHER_CHATS.md);
- reusable chat guardrails идут в `chat_prompts/`.