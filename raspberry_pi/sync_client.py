from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from bridge_config import BridgeConfig
from bridge_state import BridgeState


class SyncClient:
    def __init__(self, config: BridgeConfig, state: BridgeState) -> None:
        self._config = config
        self._state = state
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return

        self._state.set_sync_enabled(self._config.sync_enabled)
        self._thread = threading.Thread(target=self._run, name="smart-platform-sync", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def sync_once(self) -> None:
        if not self._config.sync_enabled:
            return

        payload = self._state.build_sync_payload()
        log_payload = self._state.build_log_sync_payload(limit=12)

        try:
            self._post_form("/api/v1/sync/heartbeat", payload["heartbeat"])
            for module in payload["modules"]:
                self._post_form("/api/v1/sync/modules/push", module)

            for entry in log_payload["entries"]:
                self._post_form(
                    "/api/v1/sync/logs/push",
                    {
                        "origin_node": entry.get("origin_node", ""),
                        "origin_event_id": entry.get("origin_event_id", entry.get("event_id", "")),
                        "source": entry.get("source", "rpi"),
                        "level": entry.get("level", "info"),
                        "type": entry.get("type", "platform_event"),
                        "message": entry.get("message", ""),
                        "details": json.dumps(entry.get("details", {}), ensure_ascii=False),
                    },
                )

            snapshot = self._get_json("/api/v1/system")
            self._state.apply_esp32_snapshot(snapshot)
            esp32_logs = self._get_json("/api/v1/logs?limit=24")
            self._state.apply_esp32_logs(esp32_logs)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            self._state.mark_peer_unreachable(str(exc))

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self.sync_once()
            self._stop_event.wait(self._config.sync_interval_sec)

    def _post_form(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{self._config.esp32_base_url}{path}?{query}",
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=1.8) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def _get_json(self, path: str) -> dict[str, Any]:
        with urllib.request.urlopen(f"{self._config.esp32_base_url}{path}", timeout=1.8) as response:
            return json.loads(response.read().decode("utf-8"))
