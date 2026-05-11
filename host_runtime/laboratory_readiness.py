from __future__ import annotations

from typing import Any


_READY = "ready"
_ATTENTION = "attention"
_BLOCKED = "blocked"
_ACTIVE_ACTUATORS = {"motion", "strobe", "water", "audio"}


def build_laboratory_readiness(
    *,
    current_node: dict[str, Any],
    peer_node: dict[str, Any],
    active_mode: str,
    runtime: dict[str, Any],
    reports_source_kind: str,
) -> dict[str, Any]:
    interlocks = runtime.get("interlocks", {})
    summary = runtime.get("summary", {})
    local_shell_ready = bool(current_node.get("shell_ready", True))
    emergency_latched = bool(interlocks.get("emergency_latched", False))
    fault_latched = bool(interlocks.get("fault_latched", False))
    peer_ready = _peer_ready(peer_node)
    active_actuators = [
        subsystem_id for subsystem_id in summary.get("active_subsystems", []) if subsystem_id in _ACTIVE_ACTUATORS
    ]
    reports_persistent = reports_source_kind == "report_archive_v1"

    preflight = [
        _item(
            "local_shell_ready",
            "Локальный shell открыт",
            _READY if local_shell_ready else _BLOCKED,
            "Текущий shell открыт и готов к следующей проверке."
            if local_shell_ready
            else "Откройте текущий shell перед началом следующей проверки.",
            "Оставайтесь в локальном shell и подтвердите, что страница доступна, прежде чем трогать следующее оборудование.",
        ),
        _item(
            "reports_archive",
            "Краткая история `Reports` сохраняется",
            _READY if reports_persistent else _ATTENTION,
            "Краткая история в `Gallery > Reports` уже сохраняется в постоянное хранилище."
            if reports_persistent
            else "Краткая история в `Gallery > Reports` пока ведется во временном локальном журнале этого узла.",
            "Продолжать можно и без этого, но продуктовую историю лучше держать в постоянном хранилище. Инженерные свидетельства сессии при этом остаются внутри `Laboratory`.",
        ),
        _item(
            "safe_start_mode",
            "Система стартует безопасно",
            _status_for_mode(active_mode, emergency_latched, fault_latched),
            _mode_summary(active_mode, emergency_latched, fault_latched),
            _mode_action(active_mode, emergency_latched, fault_latched),
        ),
        _item(
            "actuators_idle",
            "Чувствительные выходы простаивают",
            _BLOCKED if emergency_latched or fault_latched else (_ATTENTION if active_actuators else _READY),
            "Движение, строб, вода и аудио находятся в покое."
            if not active_actuators and not emergency_latched and not fault_latched
            else "Некоторые чувствительные каналы все еще активны: " + ", ".join(active_actuators)
            if active_actuators
            else "Аварийное состояние или fault все еще защелкнуты, поэтому сессия не находится в чистом стартовом состоянии.",
            "Вернитесь в безопасный простой и убедитесь, что движение, строб, вода и аудио полностью неактивны.",
        ),
        _item(
            "peer_owner_link",
            "Связь с ESP32 готова",
            _READY if peer_ready else _ATTENTION,
            "ESP32 доступна, поэтому laboratory-срезы на стороне владельца могут открываться через передачу управления."
            if peer_ready
            else "ESP32 пока не готова, поэтому сейчас оставайтесь на локальных срезах Raspberry Pi.",
            "Пока можно продолжать только с локальными срезами Raspberry Pi. Поднимите ESP32 перед проверками стендового строба или полива.",
        ),
    ]

    bringup_sequence = [
        _step(
            "shell_smoke",
            "Открыть shell и `Laboratory`",
            "shared",
            "/",
            preflight[0]["status"],
            "Проверьте, что shell открывается, `Laboratory` доступен и каркас laboratory-сессии отвечает.",
            "Начинайте каждую физическую сессию с входа в shell и `Laboratory`, прежде чем переходить к более глубоким аппаратным проверкам.",
        ),
        _step(
            "rpi_display_checks",
            "Raspberry Pi / Displays",
            "rpi",
            "/service?tool=rpi_touch_display",
            _READY if local_shell_ready else _BLOCKED,
            "Выполните проверку экранов на стороне владельца: цветовые шаблоны, полноэкранный режим и сенсорную сетку.",
            "Используйте этот шаг для локальной проверки дисплея до или между более глубокими модульными проверками.",
        ),
        _step(
            "peer_link_smoke",
            "Проверить связь с peer-узлом",
            "shared",
            "/service",
            _READY if peer_ready else _ATTENTION,
            "Проверьте heartbeat, синхронизацию и передачу управления с учетом владельца, прежде чем открывать ESP32-срезы.",
            "Используйте этот шаг, чтобы подтвердить, что из текущего shell ESP32 действительно видна как владелец.",
        ),
        _step(
            "esp32_strobe_bench",
            "ESP32 / Стендовый строб",
            "esp32",
            "/service?tool=strobe_bench",
            _READY if peer_ready else _BLOCKED,
            "Выполните короткие импульсы и базовые пресеты перед интегрированными тестами турели.",
            "Начинайте с импульса минимальной энергии и держите аварийную цепь доступной.",
        ),
        _step(
            "esp32_irrigation_service",
            "ESP32 / Инженерный срез полива",
            "esp32",
            "/service?tool=irrigation_service",
            _READY if peer_ready else _BLOCKED,
            "Проверьте команды зон, имитацию сенсоров и передачу управления владельцу без ложного локального владения поливом.",
            "Сначала прогоняйте сухие и короткие сценарии, а затем переходите к проверке водяного контура, когда инженерное управление выглядит стабильным.",
        ),
        _step(
            "turret_service_lane",
            "Raspberry Pi / Инженерный срез турели",
            "rpi",
            "/service?tool=turret_service",
            _status_for_turret_lane(active_mode, emergency_latched, fault_latched),
            "Проверьте локальное состояние турели, видимость interlock и инженерные сценарии из shell владельца на Raspberry Pi.",
            "Подтвердите видимость аварийного состояния, безопасный простой и блокировку действий на стороне владельца перед интегрированными тестами turret IO.",
        ),
        _step(
            "session_review",
            "Разобрать laboratory-сессию",
            "shared",
            "/service",
            _READY if local_shell_ready else _BLOCKED,
            "Проверьте контекст сессии, заметки и результаты `pass / warn / fail` внутри `Laboratory` перед следующим пакетом проверок.",
            "Опирайтесь на сессию `Laboratory` как на основной инженерный след. `Gallery > Reports` используйте только для краткой продуктовой истории.",
        ),
    ]

    overall_status = _combine_statuses([item["status"] for item in preflight])
    next_action = _next_action(preflight, bringup_sequence)
    return {
        "schema_version": "laboratory-readiness.v1",
        "overall_status": overall_status,
        "summary": _overall_summary(overall_status, preflight),
        "active_mode": active_mode,
        "reports_source_kind": reports_source_kind,
        "next_action": next_action,
        "preflight": preflight,
        "bringup_sequence": bringup_sequence,
    }


def _peer_ready(peer_node: dict[str, Any]) -> bool:
    return bool(
        peer_node.get("reachable")
        and peer_node.get("shell_ready")
        and peer_node.get("sync_ready")
        and peer_node.get("shell_base_url")
    )


def _status_for_mode(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return _BLOCKED
    if fault_latched or active_mode == "fault":
        return _BLOCKED
    if active_mode == "automatic":
        return _ATTENTION
    return _READY


def _mode_summary(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return "Аварийное состояние защелкнуто. Остановите физический вывод оборудования, пока оно не будет снято."
    if fault_latched or active_mode == "fault":
        return "Fault защелкнут. Снимите его перед следующей аппаратной проверкой."
    if active_mode == "automatic":
        return "Активен автоматический режим. Сначала вернитесь в ручной или инженерно-безопасный режим."
    if active_mode == "service_test":
        return "Активен `service_test`, и он подходит для изолированных модульных проверок."
    return "Активен ручной режим, и это хорошая база для пошагового тестирования."


def _mode_action(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return "Снимите аварийное состояние перед повторным подключением любой чувствительной ветки."
    if fault_latched or active_mode == "fault":
        return "Устраните fault, снимите защелку и вернитесь в ручной режим."
    if active_mode == "automatic":
        return "Переключитесь обратно в ручной режим, прежде чем продолжать изолированные тесты."
    if active_mode == "service_test":
        return "Оставайтесь в `service_test`, пока выполняете изолированные laboratory-срезы."
    return "Оставайтесь в ручном режиме, пока проходите порядок вывода оборудования."


def _status_for_turret_lane(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return _BLOCKED
    if fault_latched or active_mode == "fault":
        return _BLOCKED
    if active_mode == "automatic":
        return _ATTENTION
    return _READY


def _combine_statuses(statuses: list[str]) -> str:
    if any(status == _BLOCKED for status in statuses):
        return _BLOCKED
    if any(status == _ATTENTION for status in statuses):
        return _ATTENTION
    return _READY


def _overall_summary(overall_status: str, preflight: list[dict[str, Any]]) -> str:
    if overall_status == _READY:
        return "Готовность выглядит хорошо. Следуйте порядку вывода оборудования ниже."
    if overall_status == _BLOCKED:
        blockers = [item["title"] for item in preflight if item["status"] == _BLOCKED]
        return "Тестирование заблокировано. Сначала разберите эти пункты: " + ", ".join(blockers)
    warnings = [item["title"] for item in preflight if item["status"] == _ATTENTION]
    return "Продолжать можно, но держите под контролем эти пункты: " + ", ".join(warnings)


def _next_action(preflight: list[dict[str, Any]], bringup_sequence: list[dict[str, Any]]) -> dict[str, Any]:
    for item in preflight:
        if item["status"] != _READY:
            return {
                "kind": "preflight",
                "id": item["id"],
                "title": item["title"],
                "status": item["status"],
                "action": item["action"],
            }
    for step in bringup_sequence:
        if step["status"] != _READY:
            return {
                "kind": "bringup",
                "id": step["id"],
                "title": step["title"],
                "status": step["status"],
                "action": step["action"],
                "route": step["route"],
            }
    first_step = bringup_sequence[0]
    return {
        "kind": "bringup",
        "id": first_step["id"],
        "title": first_step["title"],
        "status": first_step["status"],
        "action": first_step["action"],
        "route": first_step["route"],
    }


def _item(item_id: str, title: str, status: str, summary: str, action: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "status": status,
        "summary": summary,
        "action": action,
    }


def _step(
    step_id: str,
    title: str,
    owner_scope: str,
    route: str,
    status: str,
    summary: str,
    action: str,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "title": title,
        "owner_scope": owner_scope,
        "route": route,
        "status": status,
        "summary": summary,
        "action": action,
    }
