# Спецификация постоянной системной страницы `Settings v1`

Этот документ фиксирует подробную спецификацию для `Settings`.

Его задача:

- отделить постоянный системный слой от `Laboratory` и shell-сводок;
- зафиксировать локальное меню, границы разделов и семантику применения;
- собрать в одном месте различия между `Modules`, `Components`, `System Services`, `Policies`, `Constructor` и `Diagnostics`;
- сделать `Settings` достаточно подробным документом для rebuild-from-docs без угадывания, куда что относится.

## 1. Роль `Settings`

`Settings` — это одна глобальная постоянная страница платформы.

Она нужна для:

- общие предпочтения;
- постоянные выборы среды выполнения и shell;
- настройки синхронизации;
- настройки и действия, связанные с хранилищем;
- постоянные решения по каталогу модулей и компонентов;
- policy layer;
- системный контур конструктора.

`Settings` не является:

- engineering workspace `Laboratory`;
- постраничным повтором shell bar;
- dump viewer для runtime state;
- местом, где определяют локальный состав карточек `Laboratory`.

## 2. Локальное меню и порядок разделов

У `Settings` должно быть собственное локальное левое меню.

Рекомендуемый порядок `v1`:

1. `Appearance`
2. `Среда выполнения`
3. `Синхронизация`
4. `Хранилище`
5. `Модули`
6. `Компоненты`
7. `Системные службы`
8. `Политики`
9. `Constructor`
10. `Диагностика`

Это меню для постоянных системных задач.

Оно не должно повторять порядок `Gallery` или `Laboratory`.

## 3. Заголовок и тон страницы

`Settings` должны ощущаться как спокойная persistent page.

Это означает:

- короткий заголовок страницы;
- отсутствие повторяющихся status-pills, которые уже есть в shell bar;
- диагностика раскрывается только тогда, когда дает реальный расширенный контекст;
- интерфейс не должен ощущаться как инженерная консоль.

## 4. `Appearance`

В `Appearance` живут:

- язык;
- theme;
- density;
- предпочтение полноэкранного режима;
- другие параметры представления shell-уровня.

Требования:

- глобальный переключатель `EN / RU` обязателен;
- дополнительные локали допустимы как видимые TODO-заглушки;
- выбранный язык применяется ко всем пользовательским подписям;
- предпочтение полноэкранного режима не должно молча теряться при выходе со стороны браузера.

## 5. `Среда выполнения`

`Runtime` не должен повторять одну и ту же мысль несколькими строками.

Здесь живут:

- shell/runtime profile;
- сводка контекста запуска;
- постоянные переключатели, связанные с просмотром, если они действительно есть;
- global keyboard control enable/disable.

Нельзя превращать раздел среды выполнения в подробный живой отладочный дамп.

## 6. `Синхронизация`

`Sync` описывает persistent sync behavior и domains.

Базовая модель:

- `Авто`
- `Ручная проверка`

Любое ручное изменение domain selection переводит режим в `Manual review`.

Подтвержденные sync domains:

- service link;
- module state;
- shared preferences;
- reports/logs;
- plant library;
- media content;
- component registry;
- software versions.

## 7. `Хранилище`

`Storage` — это persistent и operational слой, но не user-facing replacement для `Gallery`.

Здесь допустимы:

- storage roots and readiness details;
- `Копировать путь`;
- `Открыть папку`;
- `Открыть в приложении`;
- cleanup preview;
- подтвержденное удаление с backend root-boundary check.

`Storage` не должен превращаться в top-level content explorer.

## 8. `Modules`, `Components`, `System Services`

Это три разные сущности.

### `Modules`

Здесь живут функциональные системы уровня:

- `Turret`
- `Irrigation`
- `Power`

### `Components`

Здесь живут конкретные hardware elements:

- camera;
- strobe;
- piezo;
- servos;
- valves;
- pumps;
- sensors;
- converters;
- display devices.

### `System Services`

Здесь живут software/system entities:

- `Shell`
- `Sync Core`
- `Storage Service`
- другие software-only services.

Нельзя смешивать эти три группы в одном registry-list.

## 9. `Policies`

В `Policies` живут:

- rule switches;
- safety limitations;
- scenario restrictions;
- future target classification rules;
- fallback behavior choices.

Неподдерживаемые или недоступные rules:

- остаются видимыми;
- disabled;
- не скрываются.

## 10. `Constructor`

`Constructor` в `Settings` — это persistent system-level constructor.

Он нужен для:

- создания и редактирования module records;
- создания и редактирования component records;
- создания system profiles;
- явного review/apply уже подтвержденных вариантов.

Он не должен подменять:

- контур инженерных черновиков `Laboratory`;
- процесс экспериментального поиска в `Laboratory`.

## 11. `Диагностика`

`Diagnostics` в `Settings` — это не отдельный продуктовый модуль и не top-level page.

Он нужен только для расширенного контекста:

- sync details;
- storage details;
- runtime/readiness explanations;
- troubleshooting facts, которые действительно помогают понять persistent system state.

По умолчанию этот раздел должен быть свернут.

## 12. Граница `Settings` И `Laboratory`

Главное правило:

- `Laboratory` создает временное инженерное знание;
- `Settings` хранит примененную постоянную истину.

Это означает:

- `Settings` не должен управлять набором laboratory cards или tabs;
- `Settings` не должен дублировать laboratory controls;
- `Laboratory` не должен молча менять persistent system state.

## 13. `Сохранить выбор` Из `Laboratory`

Когда оператор нажимает `Сохранить выбор` в `Laboratory`, `Settings` становится местом финальной материализации результата.

В `Settings` после этого должны быть видимы:

- новый или обновленный persistent profile;
- applied status;
- связь с module/component record;
- возможность review/edit дальнейшего системного поведения.

Это важно, чтобы оператор понимал разницу между:

- temporary laboratory result;
- persistent active system choice.

## 14. Модель применения

Интерактивные настройки `Settings` применяются по оптимистичной модели, но это не должно маскировать истину.

Нужно сохранить:

- немедленный отклик интерфейса;
- debounce и фоновое сохранение;
- отсутствие блокировки всего интерфейса;
- честное отключенное состояние или состояние ошибки, если запись не удалась.

## 15. Клавиатура, полноэкранный режим и язык

Для `v1` обязательны как минимум:

- глобальный переключатель клавиатурного управления;
- редактируемые силовые модификаторы для действий с клавиатуры;
- language switching;
- предпочтение полноэкранного режима;
- theme and density.

Правила клавиатуры:

- keyboard action keys работают только на соответствующих control pages;
- если keyboard controls выключены, их field-set остается видимым, но disabled.

## 16. Что Нельзя Потерять При Дальнейшей Переписи

- Нельзя упрощать `Settings` до:

- обзорной страницы без постоянной семантики;
- дубликата shell bar;
- hidden policy layer;
- неявного получателя laboratory-черновиков без явного контура confirm/apply.

Если будущий документ или будущий UI делает что-то из этого, он конфликтует с canonical model `Settings`.
