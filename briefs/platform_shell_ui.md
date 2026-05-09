# Бриф продуктового блока: Platform Shell

## Назначение

`Platform Shell` — это общая browser-first оболочка платформы.

Он должен:

- одинаково выглядеть на `ESP32` и `Raspberry Pi`;
- быть главной точкой входа в систему;
- показывать доступность узлов и модулей;
- обеспечивать owner-aware handoff;
- давать доступ к `Gallery`, `Laboratory` и `Settings`;
- давать быстрый вход в `Gallery > Reports` как в главный user-facing viewer истории.

## Что входит в ответственность shell

- главная страница;
- верхняя статусная полоса;
- навигация;
- статус узлов;
- статусы продуктовых модулей;
- federated handoff к peer-owned страницам;
- activity summary и быстрый вход в `Gallery > Reports`;
- единый язык визуальных состояний `online/degraded/locked/fault/service`.

## Что shell не должен делать

- хранить бизнес-логику `Irrigation` или `Turret`;
- напрямую дергать GPIO;
- сам решать аппаратные safety-правила;
- превращаться в витрину внутренних runtime-слоев.

## Ключевая UX-задача

Пользователь должен чувствовать, что работает с одной системой.

При этом интерфейс обязан честно показывать:

- какой узел сейчас активен;
- какой модуль доступен локально;
- какой модуль принадлежит соседнему узлу;
- почему модуль заблокирован;
- куда пользователь будет переведен при handoff.

## Минимальный scope `Platform Shell`

1. `Главная`
2. `Полив`
3. `Турель`
4. `Gallery`
5. `Laboratory`
6. `Настройки`

Не считать top-level user-facing страницами:

- `Логи`
- `Диагностика`
- `Laboratory`

Важно:

- `Laboratory` остается user-facing именем инженерного контура;
- legacy alias `service_test` сохраняем только как внутренний compatibility-term.

## Первый practical follow-up

Если работа идет в отдельном чате, следующий документ для этого блока:

- [05_shell_navigation_and_screen_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/knowledge_base/05_shell_navigation_and_screen_map.md)
