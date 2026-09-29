#!/usr/bin/env python3
"""Pin the remaining two iteration742 UI binaries for the recovery branch.

The current sources are first rebuilt and must match immutable743 artifacts
apart from E32 creation time/header CRC. Only then are the verified742 binaries
copied into the release tree. This preserves a reproducible proof that the
functional delta is exactly the two binaries requested by the recovery plan.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

SPECS = {
    "aifw.dll": (
        "eb6e34b8fa929dcd424cf4d6973e5fbdc7fbc77cef904d44f7aa15c95cc25cc7",
        "8801b7d4e5d0a2b08b8650f95b30810b73c955252d7291bef2d71145b814a502",
    ),
    "xn3layoutengine.dll": (
        "61d35bbe570be2c09000ce795b943dec0e843625c482d9fc0a2fd2f356d9aea8",
        "b9fd5ebf7117d1b8c676d12a4f74ba55dd07b63a1f0bc9cc5fb2d6a7d4d53cb4",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_e32_equivalent(rebuilt: bytes, reference: bytes, name: str) -> int:
    if len(rebuilt) != len(reference) or rebuilt[0x10:0x14] != b"EPOC":
        raise SystemExit(f"{name}: E32 signature/length mismatch")
    allowed = set(range(0x14, 0x18)) | set(range(0x24, 0x2C))
    differences = [i for i, pair in enumerate(zip(rebuilt, reference)) if pair[0] != pair[1]]
    unexpected = [i for i in differences if i not in allowed]
    if unexpected:
        raise SystemExit(f"{name}: rebuilt source differs from immutable743 at {unexpected[:16]}")
    return len(differences)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("control742", type=Path)
    parser.add_argument("reference743", type=Path)
    args = parser.parse_args()
    expected_release = Path("/root/symbian3-full/epoc32/release/armv5/urel")
    if args.release.resolve() != expected_release.resolve():
        raise SystemExit("refuse non-release target")
    for name, (control_hash, reference_hash) in SPECS.items():
        target = args.release / name
        control_path = args.control742 / name
        reference_path = args.reference743 / name
        compiled = target.read_bytes()
        control = control_path.read_bytes()
        reference = reference_path.read_bytes()
        if sha(control) != control_hash or sha(reference) != reference_hash:
            raise SystemExit(f"{name}: immutable package identity mismatch")
        differences = verify_e32_equivalent(compiled, reference, name)
        target.write_bytes(control)
        if sha(target.read_bytes()) != control_hash:
            raise SystemExit(f"{name}: pin verification failed")
        print(
            f"HTCLEO_742_UI_CONTROL_PIN={name} exact={control_hash} "
            f"rebuilt743={sha(compiled)} timestamp-crc-bytes={differences}"
        )


if __name__ == "__main__":
    main()
