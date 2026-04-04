# Federated Owner Routing Stage

Этот этап фиксирует новый практический курс после уточнения ownership-модели.

## Почему меняем направление

Раньше было слишком раннее предположение, что большой перечень prototype-компонентов нужно сразу раскладывать в `ESP32` pinout.

После уточнений пользователя правильная картина такая:

- `ESP32` владеет только своим локальным контуром:
  - полив;
  - локальные датчики;
  - локальная SD-запись;
  - локальный сервис и fallback shell;
  - отдельный `strobe_bench`, если он не является частью turret runtime.
- `Raspberry Pi` владеет turret-family модулями:
  - камера;
  - лидар;
  - боевой стробоскоп;
  - пьезо и аудио;
  - сервоприводы и motion;
  - water-path турели;
  - vision и расчет наведения.

## Что это меняет в следующем этапе

Теперь следующий технический шаг — не pinout, а federated shell bootstrap:

1. Узлы должны обмениваться canonical shell base URL.
2. Модуль в snapshot должен уметь сообщать:
   - кто его owner;
   - доступен ли owner;
   - какой canonical path у owner page;
   - какой canonical URL нужно открыть.
3. Shell должен рендерить owner-aware действия:
   - локальная страница;
   - peer owner page;
   - locked состояние, если owner недоступен.

## Что делаем сейчас

- фиксируем owner-aware routing contract в docs и API;
- передаем `shell_base_url` в sync heartbeat;
- добавляем canonical URLs в system snapshot;
- обновляем shell `ESP32` и `Raspberry Pi`, чтобы он умел показывать owner page links.

## Что уже сделано в bootstrap-реализации

- `ESP32` snapshot теперь отдает:
  - `shell_base_url` у local/peer node;
  - `owner_node_id`;
  - `owner_available`;
  - `canonical_path`;
  - `canonical_url`;
  - `federated_access`.
- `Raspberry Pi` heartbeat передает свой `shell_base_url`.
- Оба shell уже показывают owner-aware links вместо слепого локального управления чужим модулем.
- На этом этапе это soft handoff, а не полный reverse-proxy.

## Что делаем позже

Полный federated proxy откладываем на следующий шаг.

Сначала нам нужен soft handoff:

- shell знает владельца;
- shell знает, куда вести пользователя;
- shell не скрывает модуль;
- shell не пытается исполнять чужую команду локально.

После этого уже можно расширять платформу:

- proxy для peer-owned service pages;
- merge shared settings;
- owner-aware settings/service workflows;
- только потом pin/power документы для локального `ESP32` контура.
