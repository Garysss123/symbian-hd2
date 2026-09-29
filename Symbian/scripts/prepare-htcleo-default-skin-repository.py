#!/usr/bin/env python3
"""Select the complete stock Haze theme for the HTC Leo UI milestone.

The PDK CenRep default points to the intentionally sparse Symbian theme
(200259E6).  Hardware 595 proves that theme loads correctly and changes icons
and CBA chrome, but its main background remains white/outline-only.  Haze
(2000B12D) is already a complete stock ROM skin, so change only read-only
personalisation key 0x14 in a generated UTF-16 repository file.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


SOURCE_UID = "200259E6"
TARGET_UID = "2000B12D"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.source.is_file():
        raise SystemExit(f"missing personalisation repository: {args.source}")

    raw = args.source.read_bytes()
    if not raw.startswith(b"\xff\xfe"):
        raise SystemExit("personalisation repository is not UTF-16LE with BOM")
    text = raw[2:].decode("utf-16le")
    pattern = re.compile(
        r'(?mi)^(0x14\s+string\s+")' + SOURCE_UID + r'("\s+.*)$'
    )
    text, count = pattern.subn(r"\g<1>" + TARGET_UID + r"\g<2>", text)
    if count != 1:
        raise SystemExit(
            f"default skin key: expected one {SOURCE_UID} entry, found {count}"
        )
    checks = {
        "owner": "0x10207114" in text,
        "target key": len(re.findall(
            rf'(?mi)^0x14\s+string\s+"{TARGET_UID}"', text
        )) == 1,
        "old default absent": not re.search(
            rf'(?mi)^0x14\s+string\s+"{SOURCE_UID}"', text
        ),
        "active skin key retained": len(re.findall(
            r"(?mi)^0x2\s+string", text
        )) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HTC Leo default-skin repository verification failed: "
            + ", ".join(failed)
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))
    if args.output.stat().st_size != args.source.stat().st_size:
        raise SystemExit("default-skin repository size changed unexpectedly")
    print(
        "HTCLEO_DEFAULT_SKIN_SELECTION="
        "haze-2000b12d-cenrep-key14-data-only"
    )


if __name__ == "__main__":
    main()
