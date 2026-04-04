from __future__ import annotations

import json
from collections import deque
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any

from report_feed import build_reports_snapshot_from_entries, normalize_report_entry


class ReportArchive:
    """Persistent report-entry archive for Gallery > Reports.

    This is a transitionary baseline archive:
    - stores normalized report entries as JSONL;
    - keeps one simple append-only file in content storage;
    - trims to a bounded number of entries to avoid silent growth.
    """

    def __init__(
        self,
        reports_root: Path,
        *,
        file_name: str = "report_feed.jsonl",
        max_entries: int = 2000,
    ) -> None:
        self._lock = RLock()
        self._reports_root = Path(reports_root)
        self._reports_root.mkdir(parents=True, exist_ok=True)
        self._archive_path = self._reports_root / file_name
        self._max_entries = max(1, max_entries)
        self._entries: deque[dict[str, Any]] = deque(maxlen=self._max_entries)
        self._load_from_disk()

    @property
    def archive_path(self) -> Path:
        return self._archive_path

    def append_platform_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_report_entry(entry)
        with self._lock:
            was_full = len(self._entries) >= self._max_entries
            self._entries.append(deepcopy(normalized))
            if was_full:
                self._rewrite_file_locked()
            else:
                with self._archive_path.open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(json.dumps(normalized, ensure_ascii=False))
                    handle.write("\n")
        return deepcopy(normalized)

    def snapshot(self, limit: int = 60, *, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            newest_first = [deepcopy(item) for item in reversed(self._entries)]
        return build_reports_snapshot_from_entries(
            newest_first,
            count=len(newest_first),
            limit=limit,
            source_kind="report_archive_v1",
            filters=filters,
        )

    def _load_from_disk(self) -> None:
        if not self._archive_path.exists():
            return

        rewrite_required = False
        with self._archive_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    rewrite_required = True
                    continue

                if not isinstance(payload, dict):
                    rewrite_required = True
                    continue

                if len(self._entries) >= self._max_entries:
                    rewrite_required = True
                self._entries.append(payload)

        if rewrite_required:
            self._rewrite_file_locked()

    def _rewrite_file_locked(self) -> None:
        with self._archive_path.open("w", encoding="utf-8", newline="\n") as handle:
            for entry in self._entries:
                handle.write(json.dumps(entry, ensure_ascii=False))
                handle.write("\n")
