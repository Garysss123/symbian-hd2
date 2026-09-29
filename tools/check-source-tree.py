#!/usr/bin/env python3
"""Check the frozen public source snapshot; no build, network or device access."""
import ast
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.jar', '.jad', '.sis', '.sisx', '.exe', '.dll', '.o', '.a', '.so',
             '.elf', '.sym', '.map', '.class', '.png', '.jpg', '.jpeg', '.mbm',
             '.mif', '.bin', '.img', '.rom', '.gz', '.zip', '.log', '.dmp', '.pyc'}
EXCLUDED_DIRS = {'.git', '__pycache__'}

def main():
    manifest = ROOT / 'SOURCE-MANIFEST.sha256'
    expected = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        if not re.fullmatch(r'[a-f0-9]{64}', digest) or name in expected:
            raise SystemExit('Malformed/duplicate manifest entry')
        path = Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise SystemExit('Unsafe manifest path')
        expected[name] = digest
    actual = set()
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise SystemExit(f'Symlink not allowed: {relative}')
        if not path.is_file() or path == manifest:
            continue
        if path.suffix.lower() in FORBIDDEN or path.name == '.env':
            raise SystemExit(f'Non-source artifact: {relative}')
        name = relative.as_posix()
        data = path.read_bytes()
        if b'\0' in data:
            raise SystemExit(f'Binary content: {relative}')
        if hashlib.sha256(data).hexdigest() != expected.get(name):
            raise SystemExit(f'Hash mismatch: {relative}')
        if path.suffix == '.py':
            # Syntax only; historical scripts are never imported or executed here.
            ast.parse(data.decode('utf-8-sig'), filename=name)
        actual.add(name)
    if actual != set(expected):
        raise SystemExit('Missing or unexpected source files')
    print(f'PUBLIC_SOURCE_CHECK_OK {len(actual)} files; no device/build actions')

if __name__ == '__main__':
    main()
