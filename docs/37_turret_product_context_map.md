# Turret Product Context Map

Этот документ фиксирует объединенное знание о `Turret` после:

- старого ТЗ и migration-контекста;
- текущей архитектуры `Smart Platform`;
- новых пользовательских уточнений по UX, сценариям, emergency power interlock и media-flow.

Важно:

- прямые donor-файлы вне текущего workspace сейчас недоступны;
- источником истины здесь считаем:
  - [26_v1_product_spec.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/26_v1_product_spec.md)
  - [05_ui_shell_and_navigation.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/05_ui_shell_and_navigation.md)
  - [39_design_decisions_and_screen_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/39_design_decisions_and_screen_map.md)
  - текущий turret runtime/UI в `Smart_Platform/raspberry_pi`
  - новые ответы пользователя из этого чата

## 1. Главная роль Turret

`Turret` имеет гибридную роль:

- `Manual FPV` операторский режим;
- `Automatic` сценарный режим;
- наблюдение и live FPV;
- deterrence / защитные действия;
- future-ready база под machine vision, классификацию целей и внешние модули.

Это не набор отдельных actuator channels, а owner-side модуль поведения.

## 2. Owner Model

Владелец турели:

- `Raspberry Pi`

Важно:

- `ESP32` не притворяется owner-side исполнителем turret actions;
- но shell должен выглядеть одинаково независимо от точки входа;
- недоступные turret-функции остаются видимыми, но серыми и объяснимыми.

## 3. Общая модель интерфейса

Пользователь должен иметь возможность:

- зайти в UI с телефона или компьютера;
- открыть интерфейс с любой точки входа:
  - `ESP32`
  - `Raspberry Pi`
- видеть один и тот же визуальный язык;
- видеть одинаковую структуру разделов;
- видеть готовность модулей и компонентов в реальном времени.

Если работает только `ESP32`, интерфейс все равно остается тем же продуктом:

- `Turret` виден;
- недоступные функции серые;
- доступность зависит от реально подключенных owner-компонентов.

Языковая модель:

- интерфейс двуязычный;
- язык переключается глобально через `Settings`;
- default language:
  - `EN`

## 4. Три уровня Turret UX

### 4.1 Product-Level Turret Screen

Экран:

- `/turret`

Он должен быть operator-facing и не перегруженным.

Его задача:

- показывать live FPV;
- показывать текущий режим;
- показывать readiness sensing и actions;
- давать быстрое управление в `Manual`;
- давать понятную картину поведения в `Automatic`.

### 4.2 FPV Operator Layer

В `Manual` и `Automatic` пользователь видит:

- live video;
- crosshair;
- green auto-detection box;
- статус readiness важных элементов.

Для `strobe` фиксируем правило доступа:

- product-level доступ к `strobe` существует из `Manual FPV` как к action channel;
- это не отменяет отдельный доступ к `strobe` через `Laboratory`;
- два входа обслуживают разные сценарии:
  - `Manual FPV` для операторского использования;
  - `Laboratory` для проверки, bring-up и диагностики.

### 4.3 Deep Engineering Layer

User-facing имя:

- `Laboratory`

Внутренний stage-name:

- `Service/Test v1`

Alias-имена той же сущности:

- `Diagnostics`
- `Test Bench`
- `Service/Test`

Именно здесь живут:

- покомпонентные вкладки;
- супердетальные инструменты;
- terminal access;
- логи;
- графики;
- отчеты;
- ручные probes;
- подбор рабочих параметров;
- сохранение рабочего профиля.

## 5. Режимы Turret

### 5.1 Automatic

`Automatic`:

- переводит turret в самостоятельное поведение;
- сценарий выбирается через `Settings`;
- actuation происходит без ручного подтверждения;
- действия зависят от анализа цели, правил и подключенных модулей.

Примеры policy-сценариев:

- `только уход за растениями`
- `отпугивать животных, но не трогать людей`
- `silent observation`

### 5.2 Manual

`Manual` — полноценный операторский режим.

Он включает:

- live FPV;
- game-like screen layout;
- keyboard control в браузере на ПК;
- virtual controls в браузере на мобильном;
- operator HUD;
- захват фото и видео.

### 5.3 Laboratory

`Laboratory` выше по приоритету, чем обычные turret modes, но должен выглядеть как законченный продуктовый инженерный контур, а не как сырая backend-страница.

## 6. Physical Emergency Power Interlock

Для turret-sensitive power branches источником истины считаем аппаратную emergency-chain с физической кнопкой аварийного отключения.

- в released / raised состоянии питание подается, а UI может показывать derived статус `armed / power enabled`;
- в pressed / open состоянии чувствительные ветви физически обесточены;
- baseline safety-chain должен покрывать:
  - servo motion
  - `strobe`
  - ultrasonic / piezo
  - `sprayer`
  - другие активные deterrence channels, если они заведены в тот же power profile
- software не должен уметь возвращать питание без ручного возврата interlock.

Следствия для UI:

- в `Manual` чувствительные группы серые;
- состояние emergency power interlock должно быть видно в shell, operator HUD и `Laboratory`;
- при попытке нажатия пользователь получает сообщение о причине;
- в лог идет отчет:
  - `Emergency power interlock active, <function> unpowered`
- если interlock срабатывает во время работы, software защелкивает `emergency_latched` до ручного возврата и явного `clear`.

Важно:

- старую модель “virtual arming внутри FPV” больше не считаем главной;
- `Automatic` не требует отдельного виртуального arm-подтверждения;
- ограничения определяются hardware power cut, emergency state и rules/policies;
- если турель начинает вести себя непредсказуемо, надежный путь остановки должен быть аппаратным, а не зависеть от корректности ПО.

## 7. Manual FPV Layout

В `Manual FPV` должны быть:

- live video;
- crosshair;
- auto-detection box;
- верхняя правая строка статусов:
  - `arm / emergency power`
  - `manual`
  - подключенные устройства
  - батарея
  - уровень воды распылителя
  - уровень воды irrigation
  - температура
  - влажность
  - время
- верхняя левая зона:
  - кнопка `Automatic`
- нижняя левая зона:
  - стик управления осями
- нижняя часть:
  - постоянная irrigation overlay-панель с рядом клапанов
- нижняя правая зона:
  - `sprayer`
  - `strobe`
  - `piezo`
- кнопки:
  - `Запись видео`
  - `Фото`

Если `ESP32` доступен, irrigation-overlay должен показывать:

- управление каждым клапаном;
- температуру воздуха;
- влажность воздуха;
- запас воды для drip irrigation;
- запас воды для spraying path.

## 8. Mode Switching

Главное правило:

- системные mode toggles и policy switches живут в `Settings`;
- внутри `Manual` и `Automatic` должен быть быстрый переход в opposite mode;
- переход выполняется сразу, без confirmation dialog;
- переключение должно ощущаться как flip между экранами приложения, а не как reload страницы.

## 9. Settings And Policy Rules

В `Settings` должен быть отдельный раздел правил использования.

Формат:

- android-like toggles

Примеры правил:

- `не стрелять в людей`
- `silent observation`
- `разрешить отпугивание животных`
- `разрешить auto-water action`
- `возврат в warm standby после потери цели`

Неподдерживаемые правила:

- видимы;
- disabled;
- не скрываются из интерфейса.

Важно:

- `Settings` не заменяет `Laboratory`;
- policy-тогглы и persistent choices живут в `Settings`;
- `Laboratory` остается отдельным контуром тестов и экспериментов.

## 10. Sensing Model

Под product-level sensing model понимаем не только наличие устройств, но и operator-facing смысл сенсорной части.

Минимум:

- `camera available`
- `range available`
- `vision available`
- `target detected`
- `target classified`
- `tracking active`
- `motion wake source`

Потом можно расширять:

- confidence;
- fps / latency;
- low-light state;
- range confidence;
- classification profile.

Для `motion wake source` фиксируем product target:

- точный датчик еще не выбран;
- wake-path должен поднимать turret contour из `warm standby` при обнаружении движения объекта в радиусе до примерно `20 m`;
- сценарий должен работать и днем, и ночью, с учетом будущего hardware profile.

## 11. Action Model

Полная action-family модель:

- `motion`
- `strobe`
- `water`
- `audio`

Приоритет первой живой аппаратной интеграции:

1. `strobe`
2. затем `audio`

Сейчас углубляем только `strobe`.

`Audio` идет отдельным hardware/product briefing-треком.

## 12. Gallery And Media

Из главного меню нужен доступ к:

- `Gallery`

FPV должен:

- идти live;
- иметь минимальные задержки;
- быть доступен на мобильном и на ПК;
- поддерживать обычный и fullscreen режим;
- быть связан с turret screens, но не растворяться в них полностью.

`Gallery` — глобальный раздел shell с mirrored storage.
Это shared virtual section без одного owner на уровне самой страницы.

Ее структура:

1. `Plants`
2. `Media`
3. `Reports`

### `Plants`

- каталог растений сада;
- описания;
- параметры ухода.

### `Media`

- видео с камеры;
- изображения с камеры;
- записи при активации турели;
- фотографии растений;
- пользовательские видео из `Manual`;
- пользовательские фото из `Manual`.
- каждый media-entry должен хранить metadata о своем source owner.

### `Reports`

- экспортированные логи;
- service-снимки;
- диагностические отчеты;
- другие сохраняемые laboratory-артефакты;
- каноническую историю действий из `Manual` и `Laboratory`.

Базовый UX `Reports`:

- mixed-type хронологический список карточек;
- карточка может быть видео, изображением или текстом;
- каждая карточка маркируется:
  - событием
  - временем
  - длительностью инцидента, если применимо
- источником действия и кратким parameter summary
- есть фильтрация по типу данных.
- при недоступности peer-owner `Gallery` должна открывать local slice и явно маркировать отсутствие чужих источников.

Для turret-driven action history это означает, что `Reports` должны уметь показывать как минимум:

- перемещение сервоприводов в координаты;
- запуск `strobe` с ключевыми параметрами;
- запуск `sprayer` с длительностью и рабочим режимом;
- сохранение фото и видео из `Manual FPV`;
- срабатывания emergency/power interlock и причины блокировок.

## 13. Alert And Recovery Behavior

При тревоге система должна:

1. поднимать контур слежения;
2. запускать протокол защиты по правилам;
3. применять доступные действия по сценарию;
4. при потере цели ждать разумное время;
5. затем возвращаться в энергоэффективный режим;
6. оставаться в модели `warm standby`, а не полного cold shutdown.
7. в случае некорректного поведения turret runtime оставлять оператору аппаратный hard-stop через emergency interlock.

## 14. Human Protection Rule

Фиксируется обязательное продуктовое правило:

- `не стрелять в людей`

Пока это не считается полностью реализованной технической функцией, но уже является обязательной частью:

- policy model;
- settings UX;
- future machine vision roadmap.

## 15. Manual As Second-Level Testing

`Manual` — не только user mode, но и второй уровень тестирования:

- оператор видит реальную картину поведения;
- может проверить controls и реакцию;
- может наблюдать target/FPV/policy interaction.

Первым уровнем тестирования остается глубокий инженерный контур:

- `Laboratory`

## 16. Product Target vs Software Baseline

Нужно различать:

- `product target`
- `software baseline`

`Product target` отвечает на вопрос:

- каким должен быть turret UX и функционал для пользователя.

`Software baseline` отвечает на вопрос:

- что уже реализовано в текущем репозитории на software-level.

Это различие особенно важно для:

- live FPV;
- media pipeline;
- hardware interlocks;
- machine vision;
- `Gallery`;
- `Laboratory`.

## 17. Практический вывод для следующего чата

Следующий чат должен стартовать не с абстрактного обсуждения турели, а уже с этого контекста:

1. единый shell на `ESP32` и `Raspberry Pi`
2. turret как hybrid product module
3. `Manual FPV` + `Automatic`
4. `Laboratory` как deep engineering contour
5. physical emergency power interlock
6. `warm standby` как обязательная энергетическая модель
7. `strobe` как первый live turret channel
8. `Gallery` как глобальный content/media/report раздел
