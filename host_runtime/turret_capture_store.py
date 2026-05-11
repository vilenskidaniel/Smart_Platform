from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


_VALID_KINDS = {"photo", "video"}
_VALID_PHASES = {"photo", "video_start", "video_stop"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(now: datetime) -> str:
    return now.strftime("%Y%m%d_%H%M%S_%f")[:-3]


def _iso(now: datetime) -> str:
    return now.isoformat().replace("+00:00", "Z")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _safe_capture_id(raw: str) -> str:
    cleaned = "".join(ch for ch in str(raw or "") if ch.isalnum() or ch in {"_", "-"})
    return cleaned[:96]


def _artifact_url(path: Path, content_root: Path) -> str:
    relative = path.resolve().relative_to(content_root.resolve())
    return "/" + "/".join(relative.parts)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_capture_artifact(
    content_root: Path,
    *,
    kind: str,
    phase: str,
    capture_id: str = "",
    duration_ms: int = 0,
    power_percent: int = 0,
) -> dict[str, Any]:
    root = Path(content_root).resolve()
    normalized_kind = str(kind or "").strip().lower()
    normalized_phase = str(phase or "").strip().lower()
    if normalized_kind not in _VALID_KINDS:
        raise ValueError("kind must be photo or video")
    if normalized_phase not in _VALID_PHASES:
        raise ValueError("phase must be photo, video_start, or video_stop")
    if normalized_kind == "photo" and normalized_phase != "photo":
        raise ValueError("photo captures only support phase=photo")
    if normalized_kind == "video" and normalized_phase == "photo":
        raise ValueError("video captures require video_start or video_stop")

    now = _utc_now()
    if normalized_phase == "photo":
        artifact_id = f"turret_photo_{_stamp(now)}_{uuid4().hex[:8]}"
        path = root / "gallery" / "captures" / "photos" / f"{artifact_id}.json"
        payload = {
            "schema_version": "turret-capture-artifact.v1",
            "capture_id": artifact_id,
            "kind": "photo",
            "phase": "photo",
            "status": "captured",
            "created_at_utc": _iso(now),
            "source_surface": "turret_manual_fpv",
            "module_id": "turret_bridge",
            "camera_binding": "placeholder_until_physical_camera",
            "power_percent": max(0, int(power_percent or 0)),
            "artifact_note": "Metadata placeholder created before real camera frame transport is wired.",
        }
        _write_json(path, payload)
        return _decorate_payload(payload, path, root)

    if normalized_phase == "video_start":
        artifact_id = f"turret_video_{_stamp(now)}_{uuid4().hex[:8]}"
        path = root / "video" / "captures" / f"{artifact_id}.json"
        payload = {
            "schema_version": "turret-capture-artifact.v1",
            "capture_id": artifact_id,
            "kind": "video",
            "phase": "video_start",
            "status": "recording",
            "created_at_utc": _iso(now),
            "started_at_utc": _iso(now),
            "stopped_at_utc": "",
            "duration_ms": 0,
            "source_surface": "turret_manual_fpv",
            "module_id": "turret_bridge",
            "camera_binding": "placeholder_until_physical_camera",
            "power_percent": max(0, int(power_percent or 0)),
            "artifact_note": "Metadata placeholder created before real video stream recording is wired.",
        }
        _write_json(path, payload)
        return _decorate_payload(payload, path, root)

    artifact_id = _safe_capture_id(capture_id)
    if not artifact_id:
        raise ValueError("capture_id is required for video_stop")

    path = root / "video" / "captures" / f"{artifact_id}.json"
    if not _is_within(path, root / "video" / "captures"):
        raise ValueError("capture_id resolves outside the video capture root")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError("video capture_id was not found") from None
    except json.JSONDecodeError as error:
        raise ValueError("video capture artifact is not valid JSON") from error

    if not isinstance(payload, dict) or payload.get("kind") != "video":
        raise ValueError("video capture artifact is invalid")

    payload["phase"] = "video_stop"
    payload["status"] = "captured"
    payload["stopped_at_utc"] = _iso(now)
    payload["duration_ms"] = max(0, int(duration_ms or 0))
    _write_json(path, payload)
    return _decorate_payload(payload, path, root)


def list_capture_artifacts(content_root: Path, *, limit: int = 20) -> dict[str, Any]:
    root = Path(content_root).resolve()
    candidates: list[Path] = []
    for folder in (
        root / "gallery" / "captures" / "photos",
        root / "video" / "captures",
    ):
        if folder.is_dir():
            candidates.extend(item for item in folder.glob("*.json") if item.is_file())

    artifacts: list[dict[str, Any]] = []
    for path in sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[: max(1, int(limit))]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            artifacts.append(_decorate_payload(payload, path, root))

    return {
        "schema_version": "turret-captures.v1",
        "count": len(artifacts),
        "limit": max(1, int(limit)),
        "artifacts": artifacts,
    }


def _decorate_payload(payload: dict[str, Any], path: Path, content_root: Path) -> dict[str, Any]:
    result = dict(payload)
    result["artifact_path"] = str(path.resolve())
    result["artifact_url"] = _artifact_url(path, content_root)
    result["gallery_url"] = "/gallery?tab=media&kind=" + str(result.get("kind", "media"))
    result["settings_target"] = "video" if result.get("kind") == "video" else "gallery"
    return result
