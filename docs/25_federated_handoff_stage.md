# Federated Handoff Stage

Этот этап строится поверх owner-aware routing bootstrap и добавляет первый user-facing handoff flow.

## Что было до этого

Shell уже умел:

- видеть owner модуля;
- знать canonical owner URL;
- понимать, доступен ли peer-owner;
- показывать owner-aware ссылки в snapshot и module registry.

Но пользователь все еще видел только "сырой" owner link.

## Что добавлено теперь

- На `ESP32` и `Raspberry Pi` появился одинаковый маршрут:
  - `/federated/handoff?module_id=...`
- На обоих узлах появился route-info endpoint:
  - `/api/v1/federation/route?module_id=...`
- Shell для peer-owned модулей теперь ведет не сразу по голой ссылке, а через handoff flow.

## Что делает handoff flow

1. Узнает route-info для выбранного модуля.
2. Проверяет, найден ли модуль в registry.
3. Проверяет, доступен ли owner.
4. Если owner готов:
   - показывает canonical owner page;
   - дает ручную ссылку;
   - делает мягкий auto-redirect с задержкой.
5. Если owner не готов:
   - не пытается локально выполнить чужую команду;
   - честно показывает, что модуль пока locked или owner unavailable.

## Почему это важно

Это первый реальный federated UX слой.

Теперь:

- `ESP32` shell не притворяется хозяином turret-модулей;
- `Raspberry Pi` shell не притворяется хозяином irrigation;
- пользователь по-прежнему живет внутри одного platform-style интерфейса;
- система уже готова к следующему шагу — proxy-ready service/test flow.

## Что дальше

Следующий логичный этап:

- не полный reverse-proxy всех peer-owned страниц;
- а сначала federated service/test routing:
  - peer-owned service pages;
  - owner-aware settings entry points;
  - унифицированные подсказки "где сейчас выполняется команда".
