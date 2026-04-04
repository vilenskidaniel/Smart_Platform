from __future__ import annotations

from pathlib import Path
from time import monotonic
from typing import Any

from bridge_state import BridgeState


class ShellSnapshotFacade:
    """Собирает shell-level snapshot для Raspberry Pi shell.

    Это не замена runtime endpoint и не proxy-механизм. Facade нужен только
    для того, чтобы shell получал одну короткую сводку системы, а не собирал
    картину по кускам из нескольких API.
    """

    def __init__(self, state: BridgeState, content_root: Path) -> None:
        self._state = state
        self._content_root = content_root
        self._created_at = monotonic()

    def build_snapshot(self) -> dict[str, Any]:
        system_snapshot = self._state.build_system_snapshot()
        platform_log = self._state.build_platform_log(limit=20)
        content_status = self._build_content_status()
        local_node = system_snapshot["local_node"]
        peer_node = system_snapshot["peer_node"]
        modules = system_snapshot["modules"]

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
            },
            "nodes": {
                "current": {
                    "node_id": local_node["node_id"],
                    "title": self._node_title(local_node),
                    "reachable": True,
                    "health": self._node_health(local_node, is_local=True),
                    "summary": "Local shell is active",
                },
                "peer": {
                    "node_id": peer_node["node_id"],
                    "title": self._node_title(peer_node),
                    "reachable": peer_node.get("reachable", False),
                    "health": self._node_health(peer_node, is_local=False),
                    "sync_ready": peer_node.get("sync_ready", False),
                    "reported_mode": peer_node.get("reported_mode", "manual"),
                    "shell_base_url": peer_node.get("shell_base_url", ""),
                    "summary": self._peer_summary(peer_node),
                },
            },
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
                    "sync_state": self._sync_summary_state(peer_node),
                    "ownership_summary": "ESP32 owns irrigation, Raspberry Pi owns turret",
                    "content_ready": bool(content_status["content_root_exists"]),
                },
                "activity": self._activity_summary(platform_log),
                "logs": dict(self._activity_summary(platform_log)),
                "content": {
                    "storage_kind": "filesystem",
                    "ready": bool(content_status["content_root_exists"]),
                    "libraries_ready": bool(content_status["libraries_ready"]),
                    "assets_ready": bool(content_status["assets_ready"]),
                    "audio_ready": bool(content_status["audio_ready"]),
                    "animations_ready": bool(content_status["animations_ready"]),
                },
            },
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

    def _build_content_status(self) -> dict[str, object]:
        root = self._content_root
        return {
            "storage": "filesystem",
            "content_root": str(root),
            "content_root_exists": root.exists(),
            "assets_ready": (root / "assets").is_dir(),
            "audio_ready": (root / "audio").is_dir(),
            "animations_ready": (root / "animations").is_dir(),
            "libraries_ready": (root / "libraries").is_dir(),
        }

    def _node_title(self, node: dict[str, Any]) -> str:
        if node.get("node_type") == "esp32":
            return "ESP32"
        if node.get("node_type") == "raspberry_pi":
            return "Raspberry Pi"
        return "Node"

    def _node_health(self, node: dict[str, Any], *, is_local: bool) -> str:
        if not is_local and not node.get("reachable", False):
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

    def _module_card(self, module: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": module["id"],
            "title": module["title"],
            "product_block": self._product_block(module),
            "owner_node_id": module.get("owner_node_id", ""),
            "owner_available": module.get("owner_available", False),
            "state": module.get("state", "offline"),
            "block_reason": module.get("block_reason", "unknown"),
            "canonical_path": module.get("canonical_path", "/"),
            "canonical_url": module.get("canonical_url", ""),
            "route_mode": self._route_mode(module),
            "summary": self._module_summary(module),
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

    def _route_mode(self, module: dict[str, Any]) -> str:
        owner = module.get("owner", "")
        if owner == "esp32":
            return "handoff" if module.get("owner_available", False) else "blocked"
        return "local"

    def _module_summary(self, module: dict[str, Any]) -> str:
        state = module.get("state", "offline")
        block_reason = module.get("block_reason", "unknown")
        owner = module.get("owner", "")
        if state == "fault":
            return f"Module fault: {block_reason}"
        if state == "locked":
            return f"Module is locked: {block_reason}"
        if state == "degraded":
            return f"Module is degraded: {block_reason}"
        if owner == "esp32":
            return "Peer-owned page is available" if module.get("owner_available", False) else "Peer owner is not available"
        return "Local module is ready"

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

    def _sync_summary_state(self, peer_node: dict[str, Any]) -> str:
        if not peer_node.get("reachable", False):
            return "peer_offline"
        if not peer_node.get("sync_ready", False):
            return "pending"
        return "ready"
