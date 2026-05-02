# Turret Audio Briefing

Статус документа:

- supporting module briefing, а не primary product spec или полная hardware truth;
- читать после `docs/README.md`, `37_turret_product_context_map.md`, `45_rpi_turret_hardware_and_io_map.md` и `46_safety_risk_and_failure_matrix.md`;
- если audio-model, priorities или hardware assumptions расходятся с каноническим слоем, приоритет у primary docs и hardware maps, а этот файл нужно дочищать или сокращать.

Этот документ фиксирует текущий briefing-track по `turret_audio`.

Важно:

- подробная turret-role, owner semantics и общая hardware truth уже зафиксированы в `37_turret_product_context_map.md` и `45_rpi_turret_hardware_and_io_map.md`;
- этот файл сохраняем как краткий audio-specific briefing snapshot с тем, что пока не должно потеряться при общей турельной проработке.

## 1. Какой audio delta сейчас зафиксирован

Для `turret_audio` на текущем шаге считаем подтвержденными три channel groups:

1. `ultrasonic_pair`
2. `horn_pair`
3. `voice_fx`

На уровне `Laboratory` это остается одной audio-вкладкой, но внутри с тремя независимыми группами тестирования и одним общим рабочим профилем, который позже должен применяться в `automatic`, `manual FPV` и engineering-сценариях.

## 2. Подтвержденный hardware baseline

### `ultrasonic_pair`

- количество:
  - `2`
- текущий кандидат:
  - `5140 Ultrasonic Speaker Horn`
- монтаж:
  - на голове турели
- статус по наличию:
  - в наличии `2` штуки

### `horn_pair`

- количество:
  - `2`
- текущий кандидат:
  - `4 inch 110x110mm Square Horn Tweeter Stage Speaker Piezoelectric`
- монтаж:
  - на голове турели
- hardware note:
  - это пассивные рупоры / волноводы без собственного драйвера
- статус по наличию:
  - в наличии `2` штуки

### `voice_fx`

- количество:
  - `1`
- текущий кандидат:
  - `Soundcore Motion 300 Wireless Hi-Res Portable Speaker Bluetooth`
- монтаж:
  - внутри корпуса
- статус по наличию:
  - физически в наличии

## 3. Усиление, Bluetooth и микрофон

- ультразвуковая пара сейчас рассматривается через:
  - `TPA3116D2 XH-M543 DC 12V/24V 120W*2 Dual Channel Digital Power Audio Amplifier Board`
- этот усилитель сейчас рассматриваем как основной мощный тракт для `horn_pair` / `ultrasonic_pair` экспериментов;
- текущая wiring-логика фиксируется так:
  - одна пара спикеров подключается к левому каналу драйвера
  - вторая пара спикеров подключается к правому каналу драйвера
- это означает, что `horn_pair` и `ultrasonic_pair` сейчас считаются двумя нагрузочными группами одного dual-channel audio path, а не двумя независимыми усилителями;
- микрофонный путь сейчас задается встроенным микрофоном `Soundcore Motion 300`;
- `voice_fx` путь сейчас задается именно Bluetooth-колонкой, а не отдельным пассивным динамиком;
- внутри корпуса для этой колонки нужен `Type-C` power path.

## 3. Новое обязательное behavioral-требование

При включении `Soundcore Motion 300` система должна стремиться автоматически подцеплять колонку к активному узлу платформы:

- preferred path:
  - `Raspberry Pi`
- fallback product requirement:
  - `ESP32`

Ожидаемое поведение:

- колонка автоматически переподключается после включения;
- воспроизводит звуки выбранного узла;
- источником аудио считаются звуки/файлы, доступные на стороне этого узла.

Это пока product requirement, а не закрытая hardware/software реализация.

## 4. Что здесь уже можно считать устойчивым правилом

- в UI это может оставаться одним модулем `turret_audio`;
- внутри hardware/contracts это три разные channel groups;
- `Laboratory` по `audio` должен уметь подбирать частоты, уровни и сценарии, а затем сохранять рабочие параметры;
- `audio` нельзя честно закрывать как модуль до появления понятной схемы усиления, питания, Bluetooth contract и mounting constraints.

## 5. Что пока еще не зафиксировано до конца

- рабочее напряжение и допустимая мощность для `horn_pair`;
- рабочее напряжение и допустимая мощность для `ultrasonic_pair`;
- какая точная board-level распайка и разведение будут у левого/правого канала этого dual-channel driver path;
- насколько стабилен Bluetooth audio + microphone path для live-сценариев;
- какая точная power-карта будет у `turret_audio` в целом;
- как будет организован storage/source contract для звуков на `Raspberry Pi` и возможном `ESP32` fallback.

## 6. Зачем файл сохраняем

Как короткий audio-briefing snapshot, где собраны подтвержденные channel groups, текущий amplifier/Bluetooth baseline и еще не закрытые audio-specific вопросы, которые не стоит размазывать по общим turret-docs.
