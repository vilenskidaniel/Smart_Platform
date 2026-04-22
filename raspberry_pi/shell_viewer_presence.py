from __future__ import annotations

from threading import Lock
from time import monotonic
from typing import Any


class ShellViewerPresence:
    def __init__(self, ttl_sec: float = 15.0) -> None:
        self._ttl_sec = ttl_sec
        self._entries: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def heartbeat(
        self,
        viewer_id: str,
        *,
        viewer_kind: str,
        title: str,
        value: str,
        page: str,
        address: str,
        user_agent: str,
    ) -> list[dict[str, Any]]:
        now = monotonic()
        kind = self._normalize_kind(viewer_kind)
        with self._lock:
            self._entries[viewer_id] = {
                "viewer_id": viewer_id,
                "viewer_kind": kind,
                "title": title.strip() or self._default_title(kind),
                "value": value.strip().upper() or self._default_value(kind),
                "page": page.strip() or "/",
                "address": address.strip(),
                "user_agent": user_agent,
                "last_seen": now,
            }
            self._purge_locked(now)
            return self._snapshot_locked()

    def active_viewers(self) -> list[dict[str, Any]]:
        now = monotonic()
        with self._lock:
            self._purge_locked(now)
            return self._snapshot_locked()

    def _purge_locked(self, now: float) -> None:
        stale_ids = [viewer_id for viewer_id, entry in self._entries.items() if now - float(entry["last_seen"]) > self._ttl_sec]
        for viewer_id in stale_ids:
            self._entries.pop(viewer_id, None)

    def _snapshot_locked(self) -> list[dict[str, Any]]:
        def sort_key(entry: dict[str, Any]) -> tuple[int, str, str]:
            return (self._kind_order(entry["viewer_kind"]), entry["value"], entry["viewer_id"])

        return [
            {
                "viewer_id": entry["viewer_id"],
                "viewer_kind": entry["viewer_kind"],
                "title": entry["title"],
                "value": entry["value"],
                "page": entry["page"],
                "address": entry["address"],
            }
            for entry in sorted(self._entries.values(), key=sort_key)
        ]

    def _normalize_kind(self, viewer_kind: str) -> str:
        normalized = viewer_kind.strip().lower()
        if normalized in {"phone", "tablet", "display", "desktop"}:
            return normalized
        return "desktop"

    def _kind_order(self, viewer_kind: str) -> int:
        order = {
            "phone": 0,
            "desktop": 1,
            "tablet": 2,
            "display": 3,
        }
        return order.get(viewer_kind, 9)

    def _default_title(self, viewer_kind: str) -> str:
        defaults = {
            "phone": "Phone",
            "tablet": "Tablet",
            "display": "Pi Display",
            "desktop": "Desktop",
        }
        return defaults.get(viewer_kind, "Viewer")

    def _default_value(self, viewer_kind: str) -> str:
        defaults = {
            "phone": "PH",
            "tablet": "TB",
            "display": "Pi",
            "desktop": "PC",
        }
        return defaults.get(viewer_kind, "VW")