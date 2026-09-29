#!/usr/bin/env python3
"""841: pinned stock About entry chain on840; never rebuild or mutate existing code."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path, PureWindowsPath
import runpy
import re
import struct
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SDK=Path('/root/symbian3-full')
CONFIG=ROOT/'config/htcleo-gate17-about-entry.json'
ENTRY=runpy.run_path(str(HERE/'prepare-htcleo-gate17-entry.py'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create_plan(parent,config=None):
    config=CONFIG if config is None else config
    cfg=json.loads(config.read_text())
    if parent.name!='Symbian3' or parent.parent.name!=cfg['parent_package'] or sha(parent/'initrd.gz')!=cfg['parent_sha256']:
        raise ValueError('About entry requires exact840 checkpoint')
    mapping=ENTRY['entries']((parent/'build/htcleo_symbian3_full_native.oby').read_text())
    release=SDK/'epoc32/release/armv5/urel'
    present={PureWindowsPath(n).name for n in mapping if n.startswith('sys\\bin\\')}
    queue=deque(cfg['binary_seeds']); seen=set(); binaries=[]
    while queue:
        name=queue.popleft()
        if name in seen: continue
        seen.add(name)
        source=release/name
        if not source.is_file(): raise ValueError('missing About dependency '+name)
        if name not in present:
            dump=subprocess.check_output([str(SDK/'epoc32/tools/elf2e32'),'--dump=hi','--e32input='+str(source)],text=True)
            binaries.append(dict(source=str(source),destination='sys\\bin\\'+name,bytes=source.stat().st_size,
                                 sha256=sha(source)))
            for module in ENTRY['IMPORT'].findall(dump):
                dep=module.lower()+'.dll'
                if dep not in present and dep not in seen: queue.append(dep)
    # An unexpected dependency is a decision boundary, not implicit authority
    # to revive network/SIS services or install a broad package closure.
    if {PureWindowsPath(x['destination']).name for x in binaries}!=set(cfg['binary_seeds']):
        raise ValueError('About minimal3 closure changed; review new dependency explicitly '+repr(binaries))
    rom_api=runpy.run_path(str(HERE/'verify-htcleo-gate17-entry.py'))
    parent_bytes=(parent/'initrd.gz').read_bytes()
    parent_files=rom_api['rom_files'](parent_bytes,(parent/'build/ROMBUILD.LOG').read_text(errors='replace'))
    assets=[]; retained_assets=[]
    for name in cfg['data_resources']+['resource/plugins/'+n for n in cfg['ecom_resources']]:
        dest=name.replace('/','\\').lower(); source=SDK/'epoc32/data/z'/name
        if not source.is_file() or source.stat().st_size==0: raise ValueError('missing About asset '+name)
        item=dict(source=str(source),destination=dest,bytes=source.stat().st_size,sha256=sha(source))
        if dest in mapping:
            if rom_api['file_data'](parent_bytes,parent_files,dest)!=source.read_bytes():
                raise ValueError('existing About resource differs; do not overwrite '+dest)
            retained_assets.append(item)
        else: assets.append(item)
    if len(assets)!=16 or len(retained_assets)!=4: raise ValueError('unexpected About resource membership')
    registrations={name:sha(source) for name,(source,_) in mapping.items()
                   if re.fullmatch(r'private\\10003a3f\\(?:import\\)?apps\\[^\\]+\.rsc',name)}
    for item in assets:
        if re.fullmatch(r'private\\10003a3f\\(?:import\\)?apps\\[^\\]+\.rsc',item['destination']):
            registrations[item['destination']]=item['sha256']
    if 'private\\10003a3f\\apps\\about_reg.rsc' not in registrations: raise ValueError('About registration not fingerprinted')
    fingerprint=hashlib.sha256(json.dumps(sorted(registrations.items())).encode()).hexdigest()
    version='V HTCLEO REG-'+fingerprint[:12]+r'\nPDK3.0.4\nS60-52'
    if len(version)>64: raise ValueError('SysUtil version exceeds reviewed budget')
    payload=b'\xff\xfe'+version.encode('utf-16le')
    rescan=cfg.get('catalog_rescan',True)
    if not isinstance(rescan,bool): raise ValueError('catalog_rescan must be boolean')
    catalog_policy='native-SysUtil-cache-invalidation-no-host-cache-delete'
    if not rescan:
        #842 recovery: retain the actual840 software-version bytes. Merely
        #packaging About must not invalidate the global startup app cache.
        payload=rom_api['file_data'](parent_bytes,parent_files,'resource\\versions\\sw.txt')
        catalog_policy='exact840-version-no-global-rescan-About-registration-deferred'
    catalog=dict(source='/root/symbian3-full-work/htcleo-native/htcleo-about-catalog-sw.txt',
                 destination='resource\\versions\\sw.txt',hex=payload.hex(),sha256=hashlib.sha256(payload).hexdigest(),
                 fingerprint=fingerprint,registrations=len(registrations),policy=catalog_policy)
    if 'catalog_rescan' in cfg: catalog['rescan']=rescan
    reserves=[]
    for original,stem in (('private\\10009d8f\\ecom-0-0.spi','spi'),('resource\\versions\\sw.txt','sw')):
        data=rom_api['file_data'](parent_bytes,parent_files,original)
        reserves.append(dict(original_destination=original,
            destination='resource\\htcleo\\840-'+stem+'-layout.bin',
            source='/root/symbian3-full-work/htcleo-native/htcleo840-'+stem+'-layout.bin',
            bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    return dict(parent_package=cfg['parent_package'],parent_sha256=cfg['parent_sha256'],config_sha256=sha(config),
        binaries=binaries,assets=assets,retained_assets=retained_assets,ecom_resources=cfg['ecom_resources'],existing_binary_count=65,
        catalog_version=catalog,
        layout_reserves=reserves,layout_reserve_bytes=sum(x['bytes'] for x in reserves),
        raw_asset_bytes=sum(a['bytes'] for a in assets),hardware_result='pending',
        policy='stock-General-DeviceManagement-About-minimal-chain-no-existing-code-font-product-info-change')

def render_recipe(text,plan):
    marker='REM HTCLEO ABOUT ENTRY 841 BEGIN'
    if marker in text: raise ValueError('About overlay already applied')
    mapping=ENTRY['entries'](text); lines=[marker]
    for kind,items in (('file',plan['binaries']),('data',plan['assets'])):
        for item in items:
            if item['destination'] in mapping or sha(Path(item['source']))!=item['sha256']:
                raise ValueError('About input drift/duplicate '+item['destination'])
            lines.append(kind+'='+item['source']+' \t"'+item['destination']+'"')
    # Keep both old-sized data slots in their original recipe positions. The
    # replacement SPI/version go at the tail, so existing ROM code never moves.
    for reserve in plan['layout_reserves']:
        old=mapping[reserve['original_destination']][1]
        if text.splitlines().count(old)!=1: raise ValueError('ambiguous layout reserve source')
        if reserve['destination'] in mapping: raise ValueError('layout reserve already exists')
        replacement='data='+reserve['source']+' \t"'+reserve['destination']+'"'
        text=text.replace(old,replacement,1)
    catalog=plan['catalog_version']
    lines.append('data='+catalog['source']+' \t"'+catalog['destination']+'"')
    spi='private\\10009d8f\\ecom-0-0.spi'
    lines.append('data='+str(mapping[spi][0])+' \t"'+spi+'"')
    return text.rstrip('\n')+'\n'+'\n'.join(lines)+'\nREM HTCLEO ABOUT ENTRY 841 END\n'

def extend_manifest(path,plan):
    if not str(path.resolve()).startswith('/root/symbian3-full-work/htcleo-native/'):
        raise ValueError('refuse immutable/out-of-work manifest')
    lines=path.read_text().splitlines()
    if len(lines)!=65 or len({line.split(None,1)[1] for line in lines})!=65:
        raise ValueError('expected65 original inputs before About cache addition')
    for line in lines:
        digest,name=line.split(None,1)
        if sha(Path(name))!=digest: raise ValueError('840 binary changed '+name)
    known={line.split(None,1)[1] for line in lines}
    for item in plan['binaries']:
        if item['source'] in known or sha(Path(item['source']))!=item['sha256']:
            raise ValueError('new About cache input drift')
        lines.append(item['sha256']+'  '+item['source'])
    path.write_text('\n'.join(sorted(lines))+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--apply-recipe',type=Path)
    p.add_argument('--extend-release-manifest',type=Path);p.add_argument('--config',type=Path)
    a=p.parse_args();plan=create_plan(a.parent,a.config)
    if a.apply_recipe or a.extend_release_manifest:
        if json.loads(a.plan.read_text())!=plan: raise ValueError('pinned About plan changed')
        if a.apply_recipe:
            if not str(a.apply_recipe.resolve()).startswith('/root/symbian3-full-work/htcleo-native/'):
                raise ValueError('refuse immutable/out-of-work recipe')
            version=Path(plan['catalog_version']['source'])
            if version.resolve()!=Path('/root/symbian3-full-work/htcleo-native/htcleo-about-catalog-sw.txt'):
                raise ValueError('refuse non-work software-version output')
            version.write_bytes(bytes.fromhex(plan['catalog_version']['hex']))
            rom_api=runpy.run_path(str(HERE/'verify-htcleo-gate17-entry.py'))
            parent_bytes=(a.parent/'initrd.gz').read_bytes()
            files=rom_api['rom_files'](parent_bytes,(a.parent/'build/ROMBUILD.LOG').read_text(errors='replace'))
            for reserve in plan['layout_reserves']:
                target=Path(reserve['source'])
                if target.resolve().parent!=Path('/root/symbian3-full-work/htcleo-native'):
                    raise ValueError('refuse non-work layout reserve output')
                data=rom_api['file_data'](parent_bytes,files,reserve['original_destination'])
                if len(data)!=reserve['bytes'] or hashlib.sha256(data).hexdigest()!=reserve['sha256']:
                    raise ValueError('layout reserve source drift')
                target.write_bytes(data)
            a.apply_recipe.write_text(render_recipe(a.apply_recipe.read_text(),plan))
        if a.extend_release_manifest: extend_manifest(a.extend_release_manifest,plan)
    else: a.plan.write_text(json.dumps(plan,indent=2)+'\n')
    print('HTCLEO_ABOUT_ENTRY_PLAN_OK '+json.dumps(plan,sort_keys=True))

if __name__=='__main__':main()
