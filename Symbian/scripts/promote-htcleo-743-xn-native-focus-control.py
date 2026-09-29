#!/usr/bin/env python3
"""Promote only the immutable743 Xn native-focus binary over the 742 control."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


AIFW_742 = "eb6e34b8fa929dcd424cf4d6973e5fbdc7fbc77cef904d44f7aa15c95cc25cc7"
XN_742 = "61d35bbe570be2c09000ce795b943dec0e843625c482d9fc0a2fd2f356d9aea8"
XN_743 = "b9fd5ebf7117d1b8c676d12a4f74ba55dd07b63a1f0bc9cc5fb2d6a7d4d53cb4"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_e32_equivalent(rebuilt: bytes, reference: bytes) -> int:
    if len(rebuilt) != len(reference) or rebuilt[0x10:0x14] != b"EPOC":
        raise SystemExit("xn3layoutengine: E32 signature/length mismatch")
    allowed = set(range(0x14, 0x18)) | set(range(0x24, 0x2C))
    differences = [
        i for i, pair in enumerate(zip(rebuilt, reference)) if pair[0] != pair[1]
    ]
    unexpected = [i for i in differences if i not in allowed]
    if unexpected:
        raise SystemExit(
            "xn3layoutengine: rebuilt source differs from immutable743 at "
            + repr(unexpected[:16])
        )
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

    aifw = args.release / "aifw.dll"
    xn = args.release / "xn3layoutengine.dll"
    aifw_control = args.control742 / "aifw.dll"
    xn_control = args.control742 / "xn3layoutengine.dll"
    xn_reference = args.reference743 / "xn3layoutengine.dll"

    for path in (aifw, xn, aifw_control, xn_control, xn_reference):
        if not path.is_file():
            raise SystemExit(f"missing focus-control artifact: {path}")

    if sha(aifw_control.read_bytes()) != AIFW_742:
        raise SystemExit("immutable742 aifw identity mismatch")
    if sha(xn_control.read_bytes()) != XN_742:
        raise SystemExit("immutable742 xn identity mismatch")
    reference = xn_reference.read_bytes()
    if sha(reference) != XN_743:
        raise SystemExit("immutable743 xn identity mismatch")
    if sha(aifw.read_bytes()) != AIFW_742:
        raise SystemExit("current aifw is not the exact742 control")

    rebuilt = xn.read_bytes()
    differences = verify_e32_equivalent(rebuilt, reference)
    xn.write_bytes(reference)
    if sha(xn.read_bytes()) != XN_743:
        raise SystemExit("immutable743 xn promotion verification failed")

    print(
        "HTCLEO_743_XN_NATIVE_FOCUS_PROMOTION="
        f"exact={XN_743} rebuilt-source-equivalent timestamp-crc-bytes={differences} "
        f"aifw742={AIFW_742}"
    )


if __name__ == "__main__":
    main()
