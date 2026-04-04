from __future__ import annotations

from collections import deque
from copy import deepcopy
from threading import RLock
from time import monotonic
from typing import Any


class PlatformEventLog:
    """Общий журнал событий узла Raspberry Pi.

    Это верхний уровень логирования для shell:
    - sync-события;
    - turret runtime;
    - service/test сценарии;
    - будущие события других модулей;
    - зеркалированные записи peer-узла.
    """

    def __init__(self, local_node_id: str, max_entries: int = 400) -> None:
        self._lock = RLock()
        self._boot_time = monotonic()
        self._local_node_id = local_node_id
        self._max_entries = max_entries
        self._next_id = 1
        self._entries: deque[dict[str, Any]] = deque()
        self._seen_remote_keys: set[tuple[str, str]] = set()

    def _timestamp_ms(self) -> int:
        return int((monotonic() - self._boot_time) * 1000)

    def _append_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        if len(self._entries) >= self._max_entries:
            removed = self._entries.popleft()
            if removed.get("mirrored") and removed.get("origin_node") and removed.get("origin_event_id"):
                self._seen_remote_keys.discard((removed["origin_node"], removed["origin_event_id"]))

        self._entries.append(entry)
        return deepcopy(entry)

    def add(self, source: str, level: str, event_type: str, message: str, **details: Any) -> dict[str, Any]:
        with self._lock:
            event_id = f"platform-{self._next_id:05d}"
            self._next_id += 1
            return self._append_entry(
                {
                    "event_id": event_id,
                    "origin_node": self._local_node_id,
                    "origin_event_id": event_id,
                    "mirrored": False,
                    "timestamp_ms": self._timestamp_ms(),
                    "source": source,
                    "level": level,
                    "type": event_type,
                    "message": message,
                    "details": details,
                }
            )

    def add_remote(
        self,
        origin_node: str,
        origin_event_id: str,
        source: str,
        level: str,
        event_type: str,
        message: str,
        details: Any,
    ) -> dict[str, Any] | None:
        remote_key = (origin_node, origin_event_id)
        with self._lock:
            if not origin_node or not origin_event_id or remote_key in self._seen_remote_keys:
                return None

            event_id = f"platform-{self._next_id:05d}"
            self._next_id += 1
            self._seen_remote_keys.add(remote_key)
            return self._append_entry(
                {
                    "event_id": event_id,
                    "origin_node": origin_node,
                    "origin_event_id": origin_event_id,
                    "mirrored": True,
                    "timestamp_ms": self._timestamp_ms(),
                    "source": source,
                    "level": level,
                    "type": event_type,
                    "message": message,
                    "details": details,
                }
            )

    def snapshot(self, limit: int = 60) -> dict[str, Any]:
        with self._lock:
            clamped_limit = max(1, limit)
            entries = list(self._entries)[-clamped_limit:]
            return {
                "count": len(self._entries),
                "limit": clamped_limit,
                "entries": [deepcopy(item) for item in reversed(entries)],
            }

    def export_local_entries(self, limit: int = 12) -> dict[str, Any]:
        with self._lock:
            clamped_limit = max(1, limit)
            local_entries = [item for item in self._entries if item.get("origin_node") == self._local_node_id]
            selected = local_entries[-clamped_limit:]
            return {
                "count": len(local_entries),
                "limit": clamped_limit,
                "entries": [deepcopy(item) for item in reversed(selected)],
            }
