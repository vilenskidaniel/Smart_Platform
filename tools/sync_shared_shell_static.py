from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "host_runtime" / "web" / "static"
TARGET_DIRS = [
    ROOT / "io_firmware" / "data" / "static",
]
FILES = ("entry_context.js", "smart_bar.js")


def sync_shared_shell_static(*, check: bool) -> int:
    out_of_sync: list[tuple[Path, Path]] = []

    for file_name in FILES:
        source = SOURCE_DIR / file_name
        source_bytes = source.read_bytes()

        for target_dir in TARGET_DIRS:
            target = target_dir / file_name
            target_bytes = target.read_bytes() if target.exists() else b""
            if target_bytes == source_bytes:
                continue

            out_of_sync.append((source, target))
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source_bytes)

    if check:
        if out_of_sync:
            for source, target in out_of_sync:
                print(
                    f"OUT_OF_SYNC {target.relative_to(ROOT)} <- {source.relative_to(ROOT)}",
                    file=sys.stderr,
                )
            return 1

        print("Shared shell static files are in sync.")
        return 0

    if out_of_sync:
        for source, target in out_of_sync:
            print(f"UPDATED {target.relative_to(ROOT)} <- {source.relative_to(ROOT)}")
    else:
        print("Shared shell static files already matched the canonical host source.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize shared shell static helpers. "
            "host_runtime/web/static is the canonical source; firmware copies are generated mirrors."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return a non-zero exit code if any generated copy differs from the canonical source.",
    )
    args = parser.parse_args()
    return sync_shared_shell_static(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())