from __future__ import annotations

from collections import deque
from copy import deepcopy
from threading import RLock
from time import monotonic
from typing import Any, Callable


class TurretEventLog:
    """Кольцевой журнал событий turret runtime.

    Это локальный лог на стороне Raspberry Pi. Позже его можно будет:
    - синхронизировать с ESP32;
    - сохранять на диск;
    - экспортировать в общий журнал платформы.
    """

    def __init__(
        self,
        max_entries: int = 200,
        forward_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._lock = RLock()
        self._boot_time = monotonic()
        self._next_id = 1
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)
        self._forward_sink = forward_sink

    def _timestamp_ms(self) -> int:
        return int((monotonic() - self._boot_time) * 1000)

    def add(self, level: str, event_type: str, message: str, **details: Any) -> dict[str, Any]:
        with self._lock:
            entry = {
                "event_id": f"turret-{self._next_id:05d}",
                "timestamp_ms": self._timestamp_ms(),
                "level": level,
                "type": event_type,
                "message": message,
                "details": details,
            }
            self._next_id += 1
            self._entries.append(entry)
            mirrored_entry = deepcopy(entry)

        # Зеркалим наружу уже после выхода из локального lock, чтобы не рисковать
        # взаимной блокировкой между turret-логом и общим platform log.
        if self._forward_sink is not None:
            self._forward_sink(mirrored_entry)

        return mirrored_entry

    def snapshot(self, limit: int = 40) -> dict[str, Any]:
        with self._lock:
            clamped_limit = max(1, limit)
            entries = list(self._entries)[-clamped_limit:]
            return {
                "count": len(self._entries),
                "limit": clamped_limit,
                "entries": [deepcopy(item) for item in reversed(entries)],
            }
