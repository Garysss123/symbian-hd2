#!/usr/bin/env python3
"""Report ROM payload sizes and fail when an image overlaps the RAM window."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ENTRY = re.compile(r'^(?:file|data)=([^\s]+)\s+"([^"]+)"', re.I)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--window", type=lambda value: int(value, 0))
    parser.add_argument("--largest", type=int, default=0)
    args = parser.parse_args()
    rows: list[tuple[int, str, str]] = []
    for line in args.recipe.read_text(encoding="utf-8").splitlines():
        match = ENTRY.match(line)
        if not match:
            continue
        source = Path(match.group(1))
        if source.is_file():
            rows.append((source.stat().st_size, match.group(2), str(source)))
    rows.sort(reverse=True)
    for size, destination, source in rows[: args.largest]:
        print(f"{size:12d}\t{destination}\t{source}")
    if args.image is not None:
        if args.window is None:
            raise SystemExit("--window is required with --image")
        size = args.image.stat().st_size
        remaining = args.window - size
        print(f"IMAGE_SIZE={size}")
        print(f"ROM_WINDOW={args.window}")
        print(f"ROM_REMAINING={remaining}")
        if remaining < 0:
            raise SystemExit(f"ROM image exceeds window by {-remaining} bytes")


if __name__ == "__main__":
    main()
