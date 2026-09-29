#!/usr/bin/env python3
"""Plan and apply778's stock English font/Settings entry closure over777."""
from __future__ import annotations
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/htcleo-gate17-entry.json'
IMPORT = runpy.run_path(str(ROOT / 'scripts/audit-htcleo-homescreen-import-closure.py'))['IMPORT']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(text):
    result = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().upper().startswith('REM'):
            continue
        match = re.match(r'^(?:file|data|primary\[[^]]+\]|extension\[[^]]+\]|device\[[^]]+\]|variant\[[^]]+\]|secondary)\s*=\s*(\S+)\s+"([^"]+)"', line, re.I)
        if match:
            target = match[2].replace('/', '\\').lower()
            if target in result:
                raise ValueError('duplicate ROM destination: ' + target)
            result[target] = (Path(match[1]), line)
    return result


def create_plan(sdk, parent, cfg):
    if sha(parent / 'initrd.gz') != cfg['parent_sha256']:
        raise ValueError('Gate17 parent is not the verified777 payload')
    original = (parent / 'build/htcleo_symbian3_full_native.oby').read_text()
    mapping = entries(original)
    present = {PureWindowsPath(n).name for n in mapping if n.startswith('sys\\bin\\')}
    release = sdk / 'epoc32/release/armv5/urel'
    available = {p.name.lower(): p for p in release.iterdir() if p.is_file()}
    for logical, actual in cfg.get('binary_overrides', {}).items():
        if logical in available or actual not in available:
            raise ValueError('unexpected adapter state: ' + logical)
        available[logical] = available[actual]
    seeds = [n.lower() for n in cfg['binary_seeds']]
    queue = deque(seeds)
    visited, additions = set(), {}
    while queue:
        name = queue.popleft()
        if name in visited:
            continue
        visited.add(name)
        if name not in available:
            raise ValueError('missing Gate17 binary/import: ' + name)
        source = available[name]
        if name not in present:
            additions[name] = dict(name=name, source=str(source), destination='sys\\bin\\'+name,
                                   sha256=sha(source), bytes=source.stat().st_size)
        dump = subprocess.run([str(sdk/'epoc32/tools/elf2e32'), '--dump=i',
                               '--e32input='+str(source)], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
        for item in IMPORT.findall(dump):
            imported = item.lower()+'.dll'
            if imported not in present and imported not in visited:
                queue.append(imported)
    assets = []
    for name in cfg['data_resources'] + ['resource/plugins/'+n for n in cfg['ecom_resources']]:
        target = name.replace('/', '\\').lower()
        source = sdk / 'epoc32/data/z' / name
        if not source.is_file() or source.stat().st_size == 0:
            raise ValueError('missing Gate17 data: ' + str(source))
        if target not in mapping:
            assets.append(dict(source=str(source), destination=target,
                               sha256=sha(source), bytes=source.stat().st_size))
    aliases = []
    for item in cfg['font_aliases']:
        source_name = item['source'].replace('/', '\\').lower()
        alias_name = item['alias'].replace('/', '\\').lower()
        first, second = mapping[source_name][0], mapping[alias_name][0]
        if not first.is_file() or not second.is_file() or sha(first) != sha(second):
            raise ValueError('font alias would change bytes: ' + alias_name)
        aliases.append(dict(source=source_name, alias=alias_name, sha256=sha(first),
                            bytes=second.stat().st_size, replaced_line=mapping[alias_name][1]))
    return dict(parent_package=cfg['parent_package'], parent_sha256=cfg['parent_sha256'],
                config_sha256=sha(CONFIG), binaries=list(additions.values()),
                assets=assets, font_aliases=aliases, ecom_resources=cfg['ecom_resources'],
                transitive_missing_imports=0, visited=len(visited),
                optional_adapter='power-save-display-stock-noop-no-hardware-not-functional-pass',
                existing_binary_policy='all54-777-binaries-unchanged', hardware_result='pending')


def render_recipe(text, plan):
    if 'REM HTCLEO GATE17 STOCK ENTRY BEGIN' in text:
        raise ValueError('Gate17 overlay already present; do not double-apply')
    for item in plan['font_aliases']:
        old = item['replaced_line']
        if text.splitlines().count(old) != 1:
            raise ValueError('font alias input changed: ' + item['alias'])
        text = text.replace(old, 'alias \\'+item['source']+' \\'+item['alias'], 1)
    present = entries(text)
    lines = ['REM HTCLEO GATE17 STOCK ENTRY BEGIN']
    for kind, items in (('file', plan['binaries']), ('data', plan['assets'])):
        for item in items:
            if item['destination'] in present or sha(Path(item['source'])) != item['sha256']:
                raise ValueError('Gate17 added resource changed/duplicates: '+item['destination'])
            lines.append(kind+'='+item['source']+' \t"'+item['destination']+'"')
    lines.append('REM HTCLEO GATE17 STOCK ENTRY END')
    return text.rstrip('\n')+'\n'+'\n'.join(lines)+'\n'


def apply_plan(recipe, plan):
    recipe.write_text(render_recipe(recipe.read_text(), plan))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--apply-recipe', type=Path)
    p.add_argument('--extend-release-manifest', type=Path)
    a = p.parse_args()
    cfg = json.loads(CONFIG.read_text())
    plan = create_plan(a.sdk, a.parent, cfg)
    if a.apply_recipe or a.extend_release_manifest:
        if json.loads(a.plan.read_text()) != plan:
            raise ValueError('Gate17 pinned plan changed')
        if a.apply_recipe:
            apply_plan(a.apply_recipe, plan)
        if a.extend_release_manifest:
            manifest = a.extend_release_manifest
            if not str(manifest.resolve()).startswith('/root/symbian3-full-work/htcleo-native/'):
                raise ValueError('refusing to change an immutable/out-of-work manifest')
            lines = manifest.read_text().splitlines()
            known = {line.split(None, 1)[1] for line in lines}
            if len(lines) != 54 or len(known) != 54:
                raise ValueError('expected exactly54 parent release inputs')
            for line in lines:
                expected, source = line.split(None, 1)
                if sha(Path(source)) != expected:
                    raise ValueError('baseline binary changed before migration: ' + source)
            for item in plan['binaries']:
                if item['source'] in known:
                    raise ValueError('new input was already in the baseline')
                lines.append(item['sha256']+'  '+item['source'])
            manifest.write_text('\n'.join(sorted(lines))+'\n')
    else:
        a.plan.write_text(json.dumps(plan, indent=2)+'\n')
    print('HTCLEO_GATE17_ENTRY_PLAN_PASS binaries=%d assets=%d aliases=%d unresolved=0' %
          (len(plan['binaries']),len(plan['assets']),len(plan['font_aliases'])))
    for item in plan['binaries']:
        print('ADD_BINARY\t'+item['destination']+'\t'+item['sha256'])


if __name__ == '__main__':
    main()
