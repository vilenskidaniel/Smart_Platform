from __future__ import annotations

import platform
from pathlib import Path
from time import monotonic
from typing import Any, Callable

from bridge_state import BridgeState
from storage_status import build_content_status, build_runtime_host_paths


class ShellSnapshotFacade:
    """Build a concise shell-level snapshot for shared shell surfaces."""

    def __init__(
        self,
        state: BridgeState,
        content_root: Path,
        *,
        project_root: Path | None = None,
        runtime_root: Path | None = None,
        runtime_profile: str = "owner_device",
        viewer_provider: Callable[[], list[dict[str, Any]]] | None = None,
    ) -> None:
        self._state = state
        self._content_root = content_root.resolve()
        self._runtime_root = runtime_root.resolve() if runtime_root is not None else self._content_root.parent.resolve()
        self._project_root = project_root.resolve() if project_root is not None else self._runtime_root.parent.resolve()
        self._created_at = monotonic()
        self._runtime_profile = runtime_profile
        self._viewer_provider = viewer_provider

    def build_snapshot(self) -> dict[str, Any]:
        system_snapshot = self._state.build_system_snapshot()
        sync_status = self._state.build_sync_status()
        platform_log = self._state.build_platform_log(limit=20)
        storage_status = build_content_status(self._content_root)
        local_node = system_snapshot["local_node"]
        peer_node = system_snapshot["peer_node"]
        modules = system_snapshot["modules"]
        viewers = self._viewer_provider() if self._viewer_provider is not None else []

        sync_state = str(sync_status.get("state", "pending"))
        runtime_host = self._runtime_host(local_node, viewers)

        return {
            "schema_version": "shell-snapshot.v1",
            "generated_by": local_node["node_id"],
            "generated_at_ms": int((monotonic() - self._created_at) * 1000),
            "current_shell": {
                "node_id": local_node["node_id"],
                "node_type": "raspberry_pi",
                "shell_base_url": local_node.get("shell_base_url", ""),
                "ui_shell_version": system_snapshot.get("ui_shell_version", "0.1.0"),
                "active_mode": system_snapshot.get("active_mode", "manual"),
                "service_mode": system_snapshot.get("active_mode") == "service_test",
                "runtime_profile": self._runtime_profile,
            },
            "runtime": {
                "profile": self._runtime_profile,
                "host": runtime_host,
                "viewer_count": len(viewers),
                "viewer_hint": "Resolve the current viewer by matching the local viewer_id against viewers[].",
            },
            "viewers": viewers,
            "nodes": {
                "current": self._current_node_view(local_node),
                "peer": self._peer_node_view(peer_node),
            },
            "sync": {
                "enabled": bool(sync_status.get("enabled")),
                "state": sync_state,
                "peer_reachable": bool(sync_status.get("peer_reachable")),
                "peer_sync_ready": bool(sync_status.get("peer_sync_ready")),
                "last_sync_ms": int(sync_status.get("last_sync_ms", 0) or 0),
                "last_error": str(sync_status.get("last_error", "") or ""),
                "summary": str(sync_status.get("summary", "") or self._sync_summary(sync_state)),
                "domains": list(sync_status.get("domains", [])),
            },
            "storage": storage_status,
            "module_cards": [self._module_card(module) for module in modules if module.get("visible", True)],
            "navigation": {
                "home": "/",
                "gallery": {
                    "path": "/gallery",
                    "route_mode": "virtual",
                    "owner_scope": "shared",
                    "tabs": ["plants", "media", "reports"],
                    "default_tab": "reports",
                },
                "laboratory": {
                    "available": True,
                    "route_mode": "local",
                    "path": "/service",
                    "user_facing_title": "Laboratory",
                    "internal_stage_name": "Service/Test v1",
                },
                "settings": "/settings",
                "service": "/service",
                "content": "/content",
                "diagnostics": "/settings#diagnostics",
                "logs": "/gallery?tab=reports",
                "service_test": {
                    "available": True,
                    "route_mode": "local",
                    "path": "/service",
                },
            },
            "summaries": {
                "faults": self._fault_summary(modules, system_snapshot.get("global_block_reason", "none")),
                "diagnostics": {
                    "sync_state": sync_state,
                    "ownership_summary": "ESP32 owns irrigation, Raspberry Pi owns turret",
                    "content_ready": bool(storage_status["content_root_exists"]),
                },
                "activity": self._activity_summary(platform_log),
                "logs": dict(self._activity_summary(platform_log)),
                "content": {
                    "storage_kind": storage_status.get("storage_kind", "filesystem"),
                    "ready": bool(storage_status["content_root_exists"]),
                    "storage_state": storage_status.get("content_root_state", "unknown"),
                    "libraries_ready": bool(storage_status["libraries_ready"]),
                    "assets_ready": bool(storage_status["assets_ready"]),
                    "audio_ready": bool(storage_status["audio_ready"]),
                    "animations_ready": bool(storage_status["animations_ready"]),
                },
            },
        }

    def _runtime_host(self, local_node: dict[str, Any], viewers: list[dict[str, Any]]) -> dict[str, Any]:
        system_name = platform.system().strip() or "Unknown"
        node_type = str(local_node.get("node_type", "unknown")).strip().lower()
        shell_url = str(local_node.get("shell_base_url", "") or "")
        paths = build_runtime_host_paths(self._project_root, self._runtime_root)

        if self._runtime_profile == "desktop_smoke":
            title = f"{system_name} desktop host"
            kind = "desktop_host"
            summary = "The Raspberry Pi shell is currently served from a desktop host."
            is_owner_device = False
        elif node_type == "raspberry_pi":
            title = "Raspberry Pi owner device"
            kind = "raspberry_pi_owner"
            summary = "The Raspberry Pi owner device is hosting the Smart Platform shell."
            is_owner_device = True
        elif node_type == "esp32":
            title = "ESP32 fallback shell"
            kind = "esp32_fallback"
            summary = "The Smart Platform shell is currently hosted by the ESP32 fallback surface."
            is_owner_device = True
        else:
            title = f"{system_name} host"
            kind = "unknown_host"
            summary = "The Smart Platform shell is currently running on an unknown host profile."
            is_owner_device = False

        return {
            "kind": kind,
            "title": title,
            "platform": system_name,
            "is_owner_device": is_owner_device,
            "server_status": "online",
            "server_url": shell_url,
            "summary": summary,
            "paths": paths,
            "viewer_count": len(viewers),
            "open_supported": any(bool(path["open_supported"]) for path in paths),
        }

    def _current_node_view(self, local_node: dict[str, Any]) -> dict[str, Any]:
        title = self._node_title(local_node)
        if self._runtime_profile == "desktop_smoke":
            return {
                "node_id": local_node["node_id"],
                "title": title,
                "reachable": False,
                "health": "offline",
                "wifi_ready": False,
                "shell_ready": False,
                "sync_ready": False,
                "last_seen_ms": int(local_node.get("last_seen_ms", 0) or 0),
                "uptime_ms": int(local_node.get("uptime_ms", 0) or 0),
                "summary": "Owner board is offline. The shell is running from a desktop host.",
            }

        return {
            "node_id": local_node["node_id"],
            "title": title,
            "reachable": True,
            "health": self._node_health(local_node, is_local=True),
            "wifi_ready": bool(local_node.get("wifi_ready", False)),
            "shell_ready": bool(local_node.get("shell_ready", False)),
            "sync_ready": bool(local_node.get("sync_ready", False)),
            "last_seen_ms": int(local_node.get("last_seen_ms", 0) or 0),
            "uptime_ms": int(local_node.get("uptime_ms", 0) or 0),
            "summary": "Owner device is hosting the current shell.",
        }

    def _peer_node_view(self, peer_node: dict[str, Any]) -> dict[str, Any]:
        return {
            "node_id": peer_node["node_id"],
            "title": self._node_title(peer_node),
            "reachable": bool(peer_node.get("reachable", False)),
            "health": self._node_health(peer_node, is_local=False),
            "wifi_ready": bool(peer_node.get("wifi_ready", False)),
            "shell_ready": bool(peer_node.get("shell_ready", False)),
            "sync_ready": bool(peer_node.get("sync_ready", False)),
            "last_seen_ms": int(peer_node.get("last_seen_ms", 0) or 0),
            "uptime_ms": int(peer_node.get("uptime_ms", 0) or 0),
            "reported_mode": peer_node.get("reported_mode", "manual"),
            "shell_base_url": peer_node.get("shell_base_url", ""),
            "summary": self._peer_summary(peer_node),
        }

    def _activity_summary(self, platform_log: dict[str, Any]) -> dict[str, Any]:
        recent_visible = platform_log.get("count", 0)
        warning_count = sum(1 for entry in platform_log.get("entries", []) if entry.get("level") == "warning")
        error_count = sum(1 for entry in platform_log.get("entries", []) if entry.get("level") == "error")
        return {
            "recent_visible": recent_visible,
            "total_visible": recent_visible,
            "warning_count": warning_count,
            "error_count": error_count,
            "primary_viewer": "gallery.reports",
        }

    def _node_title(self, node: dict[str, Any]) -> str:
        if node.get("node_type") == "esp32":
            return "ESP32"
        if node.get("node_type") == "raspberry_pi":
            return "Raspberry Pi"
        return "Node"

    def _node_health(self, node: dict[str, Any], *, is_local: bool) -> str:
        reachable = bool(node.get("reachable", is_local))
        if not reachable:
            return "offline"
        if not node.get("wifi_ready", False) or not node.get("shell_ready", False):
            return "degraded"
        if not is_local and not node.get("sync_ready", False):
            return "degraded"
        return "online"

    def _peer_summary(self, peer_node: dict[str, Any]) -> str:
        if not peer_node.get("reachable", False):
            return "Peer owner is offline"
        if not peer_node.get("sync_ready", False):
            return "Peer is visible but sync is pending"
        return "Peer owner is ready"

    def _owner_scope(self, module: dict[str, Any]) -> str:
        owner = str(module.get("owner", "shared")).strip().lower()
        if owner in {"esp32", "rpi", "shared"}:
            return owner
        return "shared"

    def _owner_title(self, owner_scope: str) -> str:
        if owner_scope == "esp32":
            return "ESP32"
        if owner_scope == "rpi":
            return "Raspberry Pi"
        return "Platform Service"

    def _owner_available(self, module: dict[str, Any], owner_scope: str) -> bool:
        if owner_scope == "shared":
            return True
        if owner_scope == "rpi" and self._runtime_profile == "desktop_smoke":
            return False
        return bool(module.get("owner_available", False))

    def _module_card(self, module: dict[str, Any]) -> dict[str, Any]:
        owner_scope = self._owner_scope(module)
        owner_available = self._owner_available(module, owner_scope)
        return {
            "id": module["id"],
            "title": module["title"],
            "product_block": self._product_block(module),
            "owner_scope": owner_scope,
            "owner_title": self._owner_title(owner_scope),
            "owner_node_id": module.get("owner_node_id", ""),
            "owner_available": owner_available,
            "state": module.get("state", "offline"),
            "block_reason": module.get("block_reason", "unknown"),
            "canonical_path": module.get("canonical_path", "/"),
            "canonical_url": module.get("canonical_url", ""),
            "route_mode": self._route_mode(module, owner_scope, owner_available),
            "summary": self._module_summary(module, owner_scope, owner_available),
        }

    def _product_block(self, module: dict[str, Any]) -> str:
        module_id = module.get("id", "")
        if module_id == "irrigation":
            return "irrigation"
        if module_id == "irrigation_service":
            return "service_test"
        if module_id in {"turret_bridge", "strobe"}:
            return "turret"
        if module_id in {"strobe_bench", "service_mode"}:
            return "service_test"
        return "system_shell"

    def _route_mode(self, module: dict[str, Any], owner_scope: str, owner_available: bool) -> str:
        if owner_scope == "esp32":
            return "handoff" if owner_available else "blocked"
        return "local"

    def _module_summary(self, module: dict[str, Any], owner_scope: str, owner_available: bool) -> str:
        state = module.get("state", "offline")
        block_reason = module.get("block_reason", "unknown")
        if state == "fault":
            return f"Module fault: {block_reason}"
        if state == "locked":
            return f"Module is locked: {block_reason}"
        if state == "degraded":
            return f"Module is degraded: {block_reason}"
        if owner_scope == "shared":
            return "Shared platform service is available on the current host."
        if owner_scope == "esp32":
            return "Peer-owned page is available" if owner_available else "Peer owner is not available"
        if self._runtime_profile == "desktop_smoke":
            return "Preview path from desktop host; owner device is offline"
        return "Owner-side module is ready"

    def _fault_summary(self, modules: list[dict[str, Any]], global_block_reason: str) -> dict[str, Any]:
        has_fault = global_block_reason != "none" or any(module.get("state") == "fault" for module in modules)
        has_degraded = any(module.get("state") in {"degraded", "locked"} for module in modules)
        if has_fault:
            message = "Some modules require attention"
        elif has_degraded:
            message = "Some modules are degraded or blocked"
        else:
            message = "System shell is healthy"
        return {
            "has_fault": has_fault,
            "has_degraded": has_degraded,
            "message": message,
        }

    def _sync_summary(self, state_value: str) -> str:
        if state_value == "local_only":
            return "Background sync is disabled. This host is currently operating in local-only mode."
        if state_value == "remote_unavailable":
            return "Base node connectivity is unavailable because the remote node is offline."
        if state_value == "never_synced":
            return "Sync is enabled, but the first successful exchange has not completed yet."
        if state_value == "ready":
            return "Background sync is ready and the remote node is reachable."
        if state_value == "error":
            return "Background sync reported an error during the last exchange."
        return "Background sync is enabled, but the remote node is still pending."
