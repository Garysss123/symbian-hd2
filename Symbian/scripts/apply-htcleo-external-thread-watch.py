#!/usr/bin/env python3
"""Add a read-only, low-rate Home context witness to its existing supervisor."""
import argparse
from pathlib import Path

MARKER = "HTCLEO_EXTERNAL_THREAD_WATCH_HOOK_V1"
INCLUDE = '#include "htcleothreadwatch.inl"\n'
OLD = '''        // Make sure process is started even if monitor startup
'''
NEW = '''        // HTCLEO_EXTERNAL_THREAD_WATCH_HOOK_V1
        // Capture the sole initial thread before the fresh child can spawn
        // helpers. Diagnostic failure must not affect its normal Resume.
        HtcleoWatchHomeProcess(process.Id());
        // Make sure process is started even if monitor startup
'''


def patch(text):
    if MARKER in text:
        if text.count(NEW) != 1 or text.count(INCLUDE) != 1:
            raise ValueError("partial external watcher hook")
        return text
    if text.count(OLD) != 1 or text.count('#include "htcleohomelog.h"\n') != 1:
        raise ValueError("supervisor source anchor changed")
    return text.replace('#include "htcleohomelog.h"\n',
                        '#include "htcleohomelog.h"\n' + INCLUDE, 1).replace(OLD, NEW, 1)


def restore(text):
    if MARKER not in text:
        return text
    if text.count(NEW) != 1 or text.count(INCLUDE) != 1:
        raise ValueError("external watcher cannot restore exact predecessor")
    return text.replace(NEW, OLD, 1).replace(INCLUDE, "", 1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--restore", action="store_true")
    a = p.parse_args()
    path = a.root / "sf/mw/homescreensrv/idlefw/hslaunch/src/hslaunch.cpp"
    original = path.read_text(encoding="latin-1")
    updated = restore(original) if a.restore else patch(original)
    if not a.restore:
        if patch(updated) != updated or restore(updated) != restore(original):
            raise ValueError("external watch source is not exactly reversible")
        asset = Path(__file__).parents[1] / "hd2/qsd8250-native-bsp/diagnostics/htcleokernelwatch.inl"
        body = asset.read_text()
        for forbidden in ("target.Suspend", "target.Resume", "aThread.Suspend", "aThread.Resume", "SetContext(",
                          "SetWindowGroup", "SendEventToWindowGroup", "file.Replace",
                          "file.Delete", "SetOrdinal", "timer.After("):
            if forbidden in body:
                raise ValueError("watcher contains target mutation or ordinary timer")
        if "functions[] = {0, 3, 4, 11, 12, 13}" not in body:
            raise ValueError("HAL must remain read-only")
        if "EPriorityAbsoluteHigh" not in body or "timer.HighRes(wait, 5000000)" not in body:
            raise ValueError("watcher priority/rate changed")
        if "file.Flush()" not in body or "User::WaitForRequest(wait)" not in body:
            raise ValueError("766 sampler/synchronous sink must be preserved")
        if "0x101f4cd2u" not in body or "thread.Name()" in body or "gHtcleoWatchMatches" not in body:
            raise ValueError("Matrix target identity must be explicit")
        if '21, reinterpret_cast<TAny*>(target.Handle()), &packet)' not in body:
            raise ValueError("native snapshot must use an owned thread handle")
        (path.parent / "htcleothreadwatch.inl").write_text(body)
        pulse = asset.parent / "htcleologlesspulse.inl"
        (path.parent / pulse.name).write_text(pulse.read_text())
    if updated != original:
        path.write_text(updated, encoding="latin-1")
    print("HTCLEO_EXTERNAL_THREAD_WATCH=" + ("restored" if a.restore else
          "ailaunch-matrix-kernel21-v2-readyqueue-endpoint-sync766-1m"))


if __name__ == "__main__":
    main()
