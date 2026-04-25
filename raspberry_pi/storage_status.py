from __future__ import annotations

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


def _count_tree(path: Path) -> tuple[int, int]:
    if not path.is_dir():
        return 0, 0

    file_count = 0
    dir_count = 0
    for _current, dirs, files in os.walk(path, followlinks=False):
        dir_count += len(dirs)
        file_count += len(files)
    return file_count, dir_count


def _path_state(path: Path) -> str:
    if not path:
        return "not_configured"
    if not path.exists():
        return "missing"
    if not path.is_dir():
        return "unavailable"
    return "ready"


def _open_supported() -> bool:
    system_name = platform.system().strip().lower()
    if system_name == "windows":
        return hasattr(os, "startfile")
    if system_name == "darwin":
        return True
    if system_name == "linux":
        return shutil.which("xdg-open") is not None
    return False


def _path_entry(
    entry_id: str,
    title: str,
    path: Path,
    *,
    open_target: str | None = None,
    description: str = "",
) -> dict[str, Any]:
    resolved = path.resolve()
    state = _path_state(resolved)
    file_count, dir_count = _count_tree(resolved) if state == "ready" else (0, 0)
    open_supported = bool(open_target) and _open_supported() and state == "ready"
    return {
        "id": entry_id,
        "title": title,
        "path": str(resolved),
        "state": state,
        "exists": state == "ready",
        "file_count": file_count,
        "dir_count": dir_count,
        "copy_supported": True,
        "open_supported": open_supported,
        "open_target": open_target or "",
        "description": description,
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


def build_content_status(content_root: Path) -> dict[str, Any]:
    root = content_root.resolve()
    paths = [
        _path_entry(
            "content_root",
            "Content Root",
            root,
            open_target="content_root",
            description="Local content root used by Gallery, reports, and shared libraries.",
        ),
        _path_entry(
            "gallery_reports",
            "Reports Archive",
            root / "gallery" / "reports",
            open_target="gallery_reports",
            description="Persistent report and evidence archive behind Gallery > Reports.",
        ),
        _path_entry(
            "assets",
            "Assets",
            root / "assets",
            open_target="assets",
            description="Shared image and UI asset storage.",
        ),
        _path_entry(
            "audio",
            "Audio",
            root / "audio",
            open_target="audio",
            description="Audio files used by platform modules.",
        ),
        _path_entry(
            "animations",
            "Animations",
            root / "animations",
            open_target="animations",
            description="Animation bundles and motion assets.",
        ),
        _path_entry(
            "libraries",
            "Libraries",
            root / "libraries",
            open_target="libraries",
            description="Shared structured libraries for Gallery and product logic.",
        ),
    ]

    by_id = {entry["id"]: entry for entry in paths}
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
        "gallery_reports": ("Reports Archive", content_root / "gallery" / "reports"),
        "assets": ("Assets", content_root / "assets"),
        "audio": ("Audio", content_root / "audio"),
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
            os.startfile(str(path))  # type: ignore[attr-defined]
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
