#!/usr/bin/env python3
"""DirWatch – Tiny directory change monitor.

Proactive error detection, clear naming, and idempotent operation are baked in:
- Validates the target path exists and is a directory.
- Handles KeyboardInterrupt gracefully.
- Uses deterministic snapshot comparison for reliable change detection.
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Dict, Tuple

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Watch a directory for file creation, modification, and deletion."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path of the directory to monitor.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0).",
    )
    return parser.parse_args()

def validate_directory(path: str) -> str:
    """Ensure *path* exists and is a directory. Exit with a clear error otherwise."""
    if not os.path.exists(path):
        sys.stderr.write(f"Error: Path does not exist → {path}\n")
        sys.exit(1)
    if not os.path.isdir(path):
        sys.stderr.write(f"Error: Path is not a directory → {path}\n")
        sys.exit(1)
    return os.path.abspath(path)

def snapshot(dir_path: str) -> Dict[str, Tuple[float, int]]:
    """Return a mapping of relative file paths to a tuple of (mtime, size).

    Using both modification time and size reduces false‑positives from
    timestamp‑only changes.
    """
    result: Dict[str, Tuple[float, int]] = {}
    for root, _, files in os.walk(dir_path):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                stat = os.stat(full_path)
                rel_path = os.path.relpath(full_path, dir_path)
                result[rel_path] = (stat.st_mtime, stat.st_size)
            except FileNotFoundError:
                # File might have disappeared between os.walk and os.stat.
                continue
    return result

def format_event(event: str, rel_path: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {event}: {rel_path}"

def monitor(dir_path: str, interval: float) -> None:
    previous = snapshot(dir_path)
    print(f"Started watching: {dir_path} (interval={interval}s)")
    try:
        while True:
            time.sleep(interval)
            current = snapshot(dir_path)
            # Detect creations
            for path in current.keys() - previous.keys():
                print(format_event("CREATED", path))
            # Detect deletions
            for path in previous.keys() - current.keys():
                print(format_event("DELETED", path))
            # Detect modifications
            for path in current.keys() & previous.keys():
                if current[path] != previous[path]:
                    print(format_event("MODIFIED", path))
            previous = current
    except KeyboardInterrupt:
        print("\nDirWatch stopped by user.")

def main() -> None:
    args = parse_args()
    watch_path = validate_directory(args.path)
    if args.interval <= 0:
        sys.stderr.write("Error: Interval must be positive.\n")
        sys.exit(1)
    monitor(watch_path, args.interval)

if __name__ == "__main__":
    main()
