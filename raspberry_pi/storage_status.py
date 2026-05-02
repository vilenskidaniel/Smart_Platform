from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _count_tree(path: Path) -> tuple[int, int, int]:
    if not path.is_dir():
        return 0, 0, 0

    file_count = 0
    dir_count = 0
    total_bytes = 0
    for _current, dirs, files in os.walk(path, followlinks=False):
        current_path = Path(_current)
        dir_count += len(dirs)
        file_count += len(files)
        for file_name in files:
            try:
                item = current_path / file_name
                if not item.is_symlink():
                    total_bytes += item.stat().st_size
            except OSError:
                continue
    return file_count, dir_count, total_bytes


def _path_state(path: Path) -> str:
    if not path:
        return "not_configured"
    if not path.exists():
        return "missing"
    if not path.is_dir():
        return "unavailable"
    return "ready"


def _plant_profile_count(library_root: Path) -> int:
    profile_path = library_root / "plant_profiles.v1.json"
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    entries = payload.get("entries", [])
    return len(entries) if isinstance(entries, list) else 0


def _open_supported() -> bool:
    system_name = platform.system().strip().lower()
    if system_name == "windows":
        return True
    if system_name == "darwin":
        return True
    if system_name == "linux":
        return shutil.which("xdg-open") is not None
    return False


def _open_windows_folder_in_front(path: Path) -> None:
    subprocess.Popen(["explorer.exe", str(path)])
    focus_script = (
        "Start-Sleep -Milliseconds 350; "
        "$shell = New-Object -ComObject WScript.Shell; "
        "$null = $shell.AppActivate('File Explorer'); "
        "$null = $shell.AppActivate('Проводник')"
    )
    try:
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", focus_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return


def _path_entry(
    entry_id: str,
    title: str,
    path: Path,
    *,
    open_target: str | None = None,
    app_url: str = "",
    description: str = "",
    cleanup_supported: bool = False,
    cleanup_reason: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = path.resolve()
    state = _path_state(resolved)
    file_count, dir_count, total_bytes = _count_tree(resolved) if state == "ready" else (0, 0, 0)
    open_supported = bool(open_target) and _open_supported() and state == "ready"
    return {
        "id": entry_id,
        "title": title,
        "path": str(resolved),
        "state": state,
        "exists": state == "ready",
        "file_count": file_count,
        "dir_count": dir_count,
        "total_bytes": total_bytes,
        "copy_supported": True,
        "open_supported": open_supported,
        "open_target": open_target or "",
        "app_url": app_url,
        "app_supported": bool(app_url),
        "cleanup_supported": cleanup_supported and state in {"ready", "missing"},
        "cleanup_reason": cleanup_reason,
        "description": description,
        "metadata": metadata or {},
    }


def build_runtime_host_paths(project_root: Path, runtime_root: Path) -> list[dict[str, Any]]:
    return [
        _path_entry(
            "project_root",
            "Project Root",
            project_root,
            open_target="project_root",
            description="Smart Platform workspace root.",
        ),
        _path_entry(
            "runtime_root",
            "Runtime Folder",
            runtime_root,
            open_target="runtime_root",
            description="Active Raspberry Pi shell runtime folder.",
        ),
    ]


def build_content_status(content_root: Path, *, project_root: Path | None = None) -> dict[str, Any]:
    root = content_root.resolve()
    project = (project_root or root.parent).resolve()
    paths = [
        _path_entry(
            "project_root",
            "Project Root",
            project,
            open_target="project_root",
            app_url="/",
            description="Smart Platform workspace root.",
            cleanup_reason="Project root is protected from cleanup in Settings.",
        ),
        _path_entry(
            "libraries",
            "Plant Library",
            root / "libraries",
            open_target="libraries",
            app_url="/irrigation?library=plants",
            description="Structured plant profiles, state rules, and care scenarios used by the irrigation page.",
            cleanup_reason="Reference libraries are protected from cleanup in Settings.",
            metadata={"plant_profile_count": _plant_profile_count(root / "libraries")},
        ),
        _path_entry(
            "video",
            "Video",
            root / "video",
            open_target="video",
            app_url="/gallery?tab=media&kind=video",
            description="Camera captures and video recordings.",
            cleanup_supported=True,
        ),
        _path_entry(
            "audio",
            "Audio",
            root / "audio",
            open_target="audio",
            app_url="/gallery?tab=media&kind=audio",
            description="Audio files used by platform modules.",
            cleanup_supported=True,
        ),
        _path_entry(
            "gallery_reports",
            "Reports Archive",
            root / "gallery" / "reports",
            open_target="gallery_reports",
            app_url="/gallery?tab=reports",
            description="Persistent report and evidence archive behind Gallery > Reports.",
            cleanup_supported=True,
        ),
        _path_entry(
            "gallery",
            "Gallery Content",
            root / "gallery",
            open_target="gallery",
            app_url="/gallery",
            description="User-facing gallery content root.",
            cleanup_reason="Gallery root is protected; clean a specific slice instead.",
        ),
        _path_entry(
            "assets",
            "Assets",
            root / "assets",
            open_target="assets",
            app_url="/content?target=assets",
            description="Shared image and UI asset storage.",
            cleanup_supported=True,
        ),
        _path_entry(
            "animations",
            "Animations",
            root / "animations",
            open_target="animations",
            app_url="/content?target=animations",
            description="Animation bundles and motion assets.",
            cleanup_supported=True,
        ),
        _path_entry(
            "content_root",
            "Content Root",
            root,
            open_target="content_root",
            app_url="/content",
            description="Local content root used by Gallery, reports, and shared libraries.",
            cleanup_reason="Content root is protected; clean a specific slice instead.",
        ),
    ]

    by_id = {entry["id"]: entry for entry in paths}
    total_bytes = sum(int(entry.get("total_bytes", 0) or 0) for entry in paths if entry["id"] != "content_root")
    return {
        "storage": "filesystem",
        "storage_kind": "filesystem",
        "content_root": str(root),
        "content_root_exists": by_id["content_root"]["exists"],
        "content_root_state": by_id["content_root"]["state"],
        "assets_ready": by_id["assets"]["exists"],
        "audio_ready": by_id["audio"]["exists"],
        "animations_ready": by_id["animations"]["exists"],
        "libraries_ready": by_id["libraries"]["exists"],
        "video_ready": by_id["video"]["exists"],
        "total_bytes": total_bytes,
        "paths": paths,
        "summary": "Local filesystem storage is used for content, reports, and shared libraries.",
    }


def resolve_host_path_target(
    target: str,
    *,
    project_root: Path,
    runtime_root: Path,
    content_root: Path,
) -> tuple[str, Path] | None:
    project_root = project_root.resolve()
    runtime_root = runtime_root.resolve()
    content_root = content_root.resolve()

    mapping = {
        "project_root": ("Project Root", project_root),
        "runtime_root": ("Runtime Folder", runtime_root),
        "content_root": ("Content Root", content_root),
        "gallery": ("Gallery Content", content_root / "gallery"),
        "gallery_reports": ("Reports Archive", content_root / "gallery" / "reports"),
        "assets": ("Assets", content_root / "assets"),
        "audio": ("Audio", content_root / "audio"),
        "video": ("Video", content_root / "video"),
        "animations": ("Animations", content_root / "animations"),
        "libraries": ("Libraries", content_root / "libraries"),
    }

    resolved = mapping.get(str(target or "").strip().lower())
    if resolved is None:
        return None

    title, path = resolved
    full_path = path.resolve()
    if not (_is_within(full_path, project_root) or full_path == project_root):
        return None
    return title, full_path


def open_host_path_target(
    target: str,
    *,
    project_root: Path,
    runtime_root: Path,
    content_root: Path,
) -> tuple[bool, str, str]:
    resolved = resolve_host_path_target(
        target,
        project_root=project_root,
        runtime_root=runtime_root,
        content_root=content_root,
    )
    if resolved is None:
        return False, "target is not allowed", ""

    title, path = resolved
    if not path.exists() or not path.is_dir():
        return False, f"{title} is not currently available on the host", str(path)

    system_name = platform.system().strip().lower()
    try:
        if system_name == "windows":
            _open_windows_folder_in_front(path)
        elif system_name == "darwin":
            subprocess.Popen(["open", str(path)])
        elif system_name == "linux":
            opener = shutil.which("xdg-open")
            if opener is None:
                return False, "xdg-open is not available on this host", str(path)
            subprocess.Popen([opener, str(path)])
        else:
            return False, "open folder is not supported on this host", str(path)
    except OSError as error:
        return False, str(error), str(path)

    return True, f"{title} opened on host device", str(path)


def cleanup_host_path_target(
    target: str,
    *,
    project_root: Path,
    runtime_root: Path,
    content_root: Path,
    confirm: bool = False,
) -> dict[str, Any]:
    target_id = str(target or "").strip().lower()
    cleanup_allowed = {"gallery_reports", "audio", "video", "assets", "animations"}
    if target_id not in cleanup_allowed:
        return {
            "command": "content_cleanup",
            "accepted": False,
            "preview": not confirm,
            "target": target_id,
            "message": "target is protected or not cleanup-enabled",
        }

    resolved = resolve_host_path_target(
        target_id,
        project_root=project_root,
        runtime_root=runtime_root,
        content_root=content_root,
    )
    if resolved is None:
        return {
            "command": "content_cleanup",
            "accepted": False,
            "preview": not confirm,
            "target": target_id,
            "message": "target is not allowed",
        }

    title, path = resolved
    content_root_resolved = content_root.resolve()
    path_resolved = path.resolve()
    if path_resolved == content_root_resolved or not _is_within(path_resolved, content_root_resolved):
        return {
            "command": "content_cleanup",
            "accepted": False,
            "preview": not confirm,
            "target": target_id,
            "path": str(path_resolved),
            "message": "cleanup target must stay inside content root",
        }

    if not path_resolved.exists():
        return {
            "command": "content_cleanup",
            "accepted": True,
            "preview": not confirm,
            "target": target_id,
            "path": str(path_resolved),
            "message": f"{title} is already empty or missing",
            "file_count": 0,
            "dir_count": 0,
            "total_bytes": 0,
        }

    if not path_resolved.is_dir():
        return {
            "command": "content_cleanup",
            "accepted": False,
            "preview": not confirm,
            "target": target_id,
            "path": str(path_resolved),
            "message": "cleanup target is not a directory",
        }

    file_count, dir_count, total_bytes = _count_tree(path_resolved)
    payload = {
        "command": "content_cleanup",
        "accepted": True,
        "preview": not confirm,
        "target": target_id,
        "path": str(path_resolved),
        "message": f"{title} cleanup preview" if not confirm else f"{title} cleaned",
        "file_count": file_count,
        "dir_count": dir_count,
        "total_bytes": total_bytes,
    }
    if not confirm:
        return payload

    for child in path_resolved.iterdir():
        child_resolved = child.resolve()
        if not _is_within(child_resolved, path_resolved):
            return {
                **payload,
                "accepted": False,
                "message": f"refusing to remove path outside cleanup target: {child_resolved}",
            }
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)

    return payload
