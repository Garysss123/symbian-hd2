#!/usr/bin/env python3
"""Pinned, single-binary Matrix pointer diagnostic profiles; same resources."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import re
import subprocess
import struct
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROM = runpy.run_path(str(HERE / 'verify-htcleo-gate17-entry.py'))
PARENT_SHA = '499f7308241888f9be83df88cff5dedd0755858308c7e96953c52bb3a6a85718'
CHANGED = '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll'
PROFILES = {
    'grid': (PARENT_SHA, CHANGED, 'HTCLEO_MATRIX_POINTER_FRONTIER_OK'),
    'list-release': (
        'bf861f5e9267f62ebe08a9090eb25144a16f1836bd180c829a5c42a634ac3c1f',
        '/root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll',
        'HTCLEO_MATRIX_LIST_RELEASE_OK'),
    'matrix-fade': (
        '6153b886333aa37d04f94319e7bd3af785d806f3cd39968585b0bdff1b21e113',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_MATRIX_SYSTEM_FADE_OK'),
    'menu-action': (
        'b750ad3873068bf3321ea4f5d5e59073466ccac25654984e0a4b89e354132c84',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll',
        'HTCLEO_MCS_ACTION_FRONTIER_OK'),
    'menu-launch': (
        'e146778e92e8c4f0ad19b5a50d879bb1b618a2a37907bdf1995d7b183a7191ad',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll',
        'HTCLEO_MENU_LAUNCH_FRONTIER_OK'),
    'menu-attribute': (
        '4e09bc4257b352104470ac3d4bb80a47b13ddaaf2e5bfe0fbf95fb37832131c8',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll',
        'HTCLEO_MENU_ATTRIBUTE_FRONTIER_OK'),
    'menu-request': (
        'b54fc702f863cd56b08aac27bf3a89862bdec808d2a23c6f30e58e6fb8742e11',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll',
        'HTCLEO_MENU_REQUEST_FRONTIER_OK'),
    'menu-server-exit': (
        '734ca1e3407d6135b89b87b0b97759b5a6338ed33e4586161b6d67c2a21b6077',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll',
        'HTCLEO_MENU_SERVER_EXIT_WATCH_OK'),
    'menu-software-exception': (
        'bb63f21abc4d3f9a49092445042bc399e3603186140dd2a1d53ec66a2c25b1c5',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll',
        'HTCLEO_MENU_SOFTWARE_EXCEPTION_OK'),
    'menu-exception-stack': (
        '9f62489182294029a1d6e5fb0ea646062a7bd423e68aef8ba8ad91017b42cd6c',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll',
        'HTCLEO_MENU_EXCEPTION_STACK_OK'),
    'menu-notifier-stop': (
        '3a9311c573089ae783a06eed05a547974897eef5507054945765d9481fdb7c4b',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll',
        'HTCLEO_MENU_NOTIFIER_STOP_OK'),
    'menu-task-lookup-control': (
        'c4b1aceb20602e276ad12074bf2e786782a7a5913f952baa6da9b6fd42d6b4ce',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll',
        'HTCLEO_MENU_TASK_LOOKUP_CONTROL_OK'),
    'menu-operation-completion': (
        '7006606d64bf0860e709ab48fb3277dc1c219c3d2fa805cfc4c171cf4f78255b',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll',
        'HTCLEO_MENU_OPERATION_COMPLETION_OK'),
    'gsapp-statuspane': (
        '007e593c707c433afe3cbb1f2a9f4d15eb129c822ee1ada292354e1fbeebcd65',
        '/root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll',
        'HTCLEO_GSAPP_STATUSPANE_FRONTIER_OK'),
    'gsapp-appinfo': (
        'd48af8ceaf595ec3a56c03c4ae78d6a43841bde853985af6d20641ee2a13f56e',
        '/root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll',
        'HTCLEO_GSAPP_APPINFO_FRONTIER_OK'),
    'gsapp-eikbase': (
        '57cd7ce4c4cc6b5e877d3eda26865ddef68f20e9ecb3ee342f65d0f6b095cf7f',
        '/root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll',
        'HTCLEO_GSAPP_EIKBASE_FRONTIER_OK'),
    'gsapp-view': (
        '944cb503eb298fdf64989d030bd542681c2a41d20621999d1d2ae88ea586de40',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_VIEW_OK'),
    'home-priority-ab': (
        '2c435f9eb3780b481a08f5f14bae1b9ef5859737d0ff58ecf21b28ff42f8c409',
        '/root/symbian3-full/epoc32/release/armv5/urel/xn3layoutengine.dll',
        'HTCLEO_HOME_PRIORITY_AB_OK'),
    'home-kernel-watch': (
        '3628f0e9dacb2e46855ce0d96ad9c6241aac7a26d0c8179543679de48c8a971c',
        '/root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe',
        'HTCLEO_HOME_KERNEL_WATCH_OK'),
    'vws-session-deactivation': (
        '4a363e8201a995ca32f6ea91276c68e4bc89250bd694947d61d4e71a23f3e94a',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll',
        'HTCLEO_VWS_SESSION_DEACTIVATION_OK'),
    'vws-server-event': (
        '49d7479f8b9f049ef29aca0a6a98ee9905fe45939e17f307c3842e3efb7559d9',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll',
        'HTCLEO_VWS_SERVER_EVENT_OK'),
    'viewsrv-control': (
        '422dbcdc11bbdc6c06dab75819e9957f7c0584a5420ddf0831b84b91fb793557',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll',
        'HTCLEO_VIEWSRV_SOURCE_CONTROL_OK'),
    'vws-client-state': (
        'f1f21b5baea8ba56145db1959f19403660a2dbb0f80be103aeb572d1b6534416',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll',
        'HTCLEO_VWS_CLIENT_STATE_OK'),
    'vws-client-queue': (
        '1fbd7d9330744c4f9a89c0459e238b968e5e61f9706b34cc4365cce6fb7ba4c4',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll',
        'HTCLEO_VWS_CLIENT_QUEUE_OK'),
    'viewcli-control': (
        '7dc370a3e2303585d2e1a8851c19d8123bc237ad07d09913a3510dafc1a0d6fa',
        '/root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll',
        'HTCLEO_VIEWCLI_SOURCE_CONTROL_OK'),
    'home-view-event': (
        '8dd7aeb93c292c14955f0c5c5cc36d4b8c014c357107dfad18158008ff9093d2',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll',
        'HTCLEO_HOME_VIEW_EVENT_OK'),
    'gsapp-cone-event': (
        '21d8c46c2548f537423d44f2dbcafd9eb00bb468676a12e74ec80678fc728768',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll',
        'HTCLEO_GSAPP_CONE_EVENT_OK'),
    'gsapp-transition': (
        '8b55c070e1ce8fea824ebd8a6d66056c8e6d14ac420a24bc61061e03c351f2b0',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_TRANSITION_OK'),
    'gsapp-async': (
        '300acd04c11038ede3857c8893564ebb5d247b27d47a60de9f44d15956a6df71',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_ASYNC_OK'),
    'gsapp-list': (
        'f8284ad6bdc4c3b9cd598c19c030c8d960f4c683793e126263aa0589db11d140',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_LIST_OK'),
    'gsapp-child': (
        'eada54bcf7791f5f483518c8544c634b76510733a93854e53179991aa6f9f4e9',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll',
        'HTCLEO_GSAPP_CHILD_OK'),
    'gsapp-create': (
        '1c6855e011c2c4a818ce917dc1d51dc1a675aee386c7d3dadfd07938f1b36c8e',
        '/root/symbian3-full/epoc32/release/armv5/urel/ecom.dll',
        'HTCLEO_GSAPP_CREATE_RETRY_OK'),
    'gsapp-notify': (
        '67d5dc3a32c64697baae79cbc4da71b77256f9cdcf9e737da41511e237b70f57',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll',
        'HTCLEO_GSAPP_NOTIFY_OK'),
    'gsapp-exception': (
        '71b51748f5fddbb17cdbdced25b487f3f8df2f817d07e0bb8d5557cbdef6ffd8',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_EXCEPTION_OK'),
    'gsapp-lifetime': (
        '49879f086242cbbf6aa187fbd33263cf3dc2fc213c8e7994a6a563a676c5c4f2',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_LIFETIME_OK'),
    'gsapp-redraw': (
        '14d4cb6f40d1a3e71281afa762f62a69927bf7c2ef372d637b45c172eaf8bb15',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll',
        'HTCLEO_GSAPP_REDRAW_OK'),
    'gsapp-plugin': (
        'c0586f069435ef7c40438dd4e0593e7189050debac8c2a0979c010153345b2cb',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll',
        'HTCLEO_GSAPP_PLUGIN_OK'),
    'gsapp-activation': (
        'bd8333eb069cc40a57f237a630eaac5f3fa59567c6ad69fb8d33d29a1f8af441',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_ACTIVATION_OK'),
    'gsapp-keyblock': (
        '80226a6295de224afe5c58500b836ff56dd1945be545c0da86d829bb77abf91f',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_KEYBLOCK_OK'),
    'gsapp-sgc-fade': (
        '45db81dc957dd9e520d7352d824ee4eb8172a61030833ac536731f91d47c7baf',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_SGC_FADE_OK'),
    'gsapp-sgc-params': (
        'c3aa8440f59ce7260c4842e4513773b7cb91611d0bf5cb9b5ded731ee960dd6b',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_SGC_PARAMS_OK'),
    'gsapp-focus': (
        'cd0d851c09035ff12be336b9a1cfc449af7faf83ddc5cb58b6daa132b7b908f6',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_FOCUS_FRONTIER_OK'),
    'gsapp-appui': (
        'a123123f4fa9e27fb2bc08a738aa6a7b41796eb7e10e00ad4f02ec46a4bc0619',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_APPUI_FRONTIER_OK'),
    'gsapp-sgc-local': (
        'dd5ce3a840b819b2f23a81b50930df47515eb7ca20ae3e114b36f07bc97d1852',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_SGC_LOCAL_OK'),
    'gsapp-aknenv': (
        'abc34ed06af0b4dc0a22698564ff208125d755236e834dbdf7f6f9ebe4d4db21',
        '/root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll',
        'HTCLEO_GSAPP_AKNENV_FRONTIER_OK'),
    'gsapp-env': (
        '69988ee1ceb6a177050db1e6664f3b9c6e115e7a37b4ce9521c2451879e4b777',
        '/root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll',
        'HTCLEO_GSAPP_ENV_FRONTIER_OK'),
    'gsapp-eikstart': (
        '508a51ac6e2cf71e025277cb04276ff1f55436ab3f47c47cc30dc6e39aff0da4',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_EIKSTART_FRONTIER_OK'),
    'gsapp-startup': (
        'a9ba6cad1bde6727f65d8d3aefa20d204a41dc13af0d574c599af67c780f65c0',
        '/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe',
        'HTCLEO_GSAPP_STARTUP_OBSERVER_OK'),
    'menu-task-enumeration-804': (
        'cdcdebe1aac15952b430a742fff57d8732e576abd9396c8eb6efb758d8946d3d',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll',
        'HTCLEO_MENU_TASK_ENUMERATION_804_OK'),
    'hsps-header-cache': (
        '78a5f3c8cd8557a61e14ef0075f32903ad07c85e2aaf183ef80e769e39e7981c',
        '/root/symbian3-full/epoc32/release/armv5/urel/hspsthemeserver.exe',
        'HTCLEO_HSPS_HEADER_CACHE_OK'),
    'menu-task-enumeration': (
        '78a5f3c8cd8557a61e14ef0075f32903ad07c85e2aaf183ef80e769e39e7981c',
        '/root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll',
        'HTCLEO_MENU_TASK_ENUMERATION_OK'),
    'wserv-find-notfound': (
        '78a5f3c8cd8557a61e14ef0075f32903ad07c85e2aaf183ef80e769e39e7981c',
        '/root/symbian3-full/epoc32/release/armv5/urel/wserv_nga.exe',
        'HTCLEO_WSERV_FIND_NOTFOUND_OK'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_import_contract(before, after):
    # Linkers may reorder imports. Preserve module, ordinal, offset AND count;
    # do not compare a positional array or discard duplicates with a set.
    return ({module: sorted(entries) for module, entries in before.items()} ==
            {module: sorted(entries) for module, entries in after.items()})


def selected_imports(dump, names=('apgrfx', 'apparc', 'ws32')):
    result, current, remaining = {}, None, 0
    for line in dump.splitlines():
        module = re.fullmatch(r'(\d+) imports? from (\S+)', line)
        if module:
            if current and remaining:
                raise ValueError('incomplete selected import dump')
            name = module[2].split('{')[0]
            current = name if name in names else None
            remaining = int(module[1]) if current else 0
            if current:
                if current in result:
                    raise ValueError('duplicate selected module')
                result[current] = []
        elif current and remaining:
            entry = re.fullmatch(r'\s*(\d+)(?: offset by (\d+))?\s*', line)
            if entry:
                result[current].append((int(entry[1]), int(entry[2] or 0)))
                remaining -= 1
    if (current and remaining) or set(result) != set(names):
        raise ValueError('selected native imports missing')
    return result


def verify_enumeration_imports(before_dump, after_dump):
    before, after = selected_imports(before_dump), selected_imports(after_dump)
    expected = {name: list(values) for name, values in before.items()}
    if expected['apgrfx'].count((48, 0)) != 1 or (64, 0) in expected['ws32']:
        raise ValueError('unexpected801 window-query import contract')
    expected['apgrfx'].remove((48, 0))  # FindByAppUid
    expected['ws32'].append((64, 0))   # GetWindowGroupNameFromIdentifier
    if not same_import_contract(expected, after):
        raise ValueError('enumeration must replace ONLY apgrfx48 with ws32_64')
    return dict(removed_module='apgrfx', removed_ordinal=48,
                added_module='ws32', added_ordinal=64, offsets=0)


def rom_code_span(raw, files, name):
    # TRomImageHeader, e32rom.h: header120, code addr+14/code size+1c,
    # data addr+18/data size+24, exports count+3c/address+40.
    start, declared = files[name]
    if start < 0 or start + 120 > len(raw):
        raise ValueError('truncated ROM executable header')
    code, data, size = struct.unpack_from('<III', raw, start + 0x14)
    data_size = struct.unpack_from('<I', raw, start + 0x24)[0]
    if code != ROM['ROM_BASE'] + start + 120 or data or data_size or not size or size & 3:
        raise ValueError('unsupported ROM code/data layout for import verification')
    end = code - ROM['ROM_BASE'] + size
    if end > len(raw):
        raise ValueError('ROM code extends outside image')
    return start, end, code, size


def rom_export_table(raw, files, name):
    start, end, code, size = rom_code_span(raw, files, name)
    count, address = struct.unpack_from('<II', raw, start + 0x3c)
    pos = address - ROM['ROM_BASE']
    if not 0 < count < 10000 or pos < code - ROM['ROM_BASE'] or pos + count * 4 > end:
        raise ValueError('invalid ROM export table')
    return struct.unpack_from('<' + str(count) + 'I', raw, pos), code, size


def verify_shared_import_relocations(old, new, files0, files1, name):
    """802 exception to raw equality: ONLY ARM import literals to same ws32 ordinal.

    No instruction/header/data masking and no blanket delta allowance. The whole
    code span (including bytes beyond the directory's code-size field) is checked.
    """
    start0, end0, _, _ = rom_code_span(old, files0, name)
    start1, end1, _, _ = rom_code_span(new, files1, name)
    before, after = old[start0:end0], new[start1:end1]
    if len(before) != len(after):
        raise ValueError('shared executable length changed')
    differences = sorted({i & ~3 for i, (a, b) in enumerate(zip(before, after)) if a != b})
    if not differences:
        return dict(module=name, changed_import_literals=0)
    provider = 'sys\\bin\\ws32.dll'
    exports0, code0, size0 = rom_export_table(old, files0, provider)
    exports1, code1, size1 = rom_export_table(new, files1, provider)
    if len(exports0) != len(exports1) or size0 != size1:
        raise ValueError('ws32 export count/code length changed')
    rows = []
    for offset in differences:
        if (offset < 124 or offset + 4 > len(before) or
                before[offset-4:offset] != b'\x04\xf0\x1f\xe5' or
                after[offset-4:offset] != before[offset-4:offset]):
            raise ValueError('non-import-instruction/literal difference in ' + name)
        a, = struct.unpack_from('<I', before, offset)
        b, = struct.unpack_from('<I', after, offset)
        ordinals = [i+1 for i, value in enumerate(exports0) if value == a and exports1[i] == b]
        if (not ordinals or not code0 <= (a & ~1) < code0 + size0 or
                not code1 <= (b & ~1) < code1 + size1 or a-code0 != b-code1):
            raise ValueError('changed import target/ordinal/function offset in ' + name)
        rows.append(dict(offset=offset, before=a, after=b, matching_ordinals=ordinals))
    return dict(module=name, provider=provider, provider_delta=code1-code0,
                changed_import_literals=len(rows), imports=rows)



def parse_e32_import_sites(raw):
    """E32ImageHeader/E32ImportSection ELF import offsets, not guessed pointers."""
    if len(raw)<124 or raw[16:20]!=b'EPOC':
        raise ValueError('invalid E32 consumer header')
    word=lambda n: struct.unpack_from('<I',raw,n)[0]
    if word(28)!=0 or word(44)&0xf0000000 != 0x10000000:
        raise ValueError('requires uncompressed ELF-style E32 imports')
    code_size,code_offset,import_offset=word(48),word(100),word(108)
    refs=word(84)
    if not (124<=code_offset<=len(raw) and code_offset+code_size<=len(raw) and
            0<refs<256 and import_offset+4<=len(raw)):
        raise ValueError('E32 code/import bounds')
    section_end=import_offset+word(import_offset)
    if section_end>len(raw) or section_end<=import_offset+4:
        raise ValueError('truncated E32 import section')
    pos=import_offset+4
    sites,table={},{}
    for _ in range(refs):
        if pos+8>section_end: raise ValueError('truncated E32 import block')
        name_offset,count=word(pos),word(pos+4)
        end=pos+8+4*count
        name_start=import_offset+name_offset
        if count>10000 or end>section_end or not import_offset<=name_start<section_end:
            raise ValueError('invalid E32 import block')
        name_end=raw.find(b'\0',name_start,section_end)
        if name_end<0: raise ValueError('unterminated E32 provider')
        module=raw[name_start:name_end].decode('ascii').split('{')[0].lower()
        if module in table: raise ValueError('duplicate E32 provider')
        table[module]=[]
        for at in range(pos+8,end,4):
            offset=word(at)
            if offset&3 or offset+4>code_size: raise ValueError('bad E32 import patch offset')
            value=word(code_offset+offset)
            ordinal,addend=value&0xffff,value>>16
            if not ordinal or offset+120 in sites: raise ValueError('invalid/duplicate E32 import site')
            sites[offset+120]=(module,ordinal,addend)
            table[module].append((ordinal,addend))
        pos=end
    return sites,table,code_size


def load_e32_import_sites(source, declared):
    # PETRAN operates only on a temporary diagnostic copy, never an SDK input.
    with tempfile.TemporaryDirectory(prefix='htcleo-import-sites-') as folder:
        path=Path(folder)/'consumer.e32'
        shutil.copyfile(source,path)
        data=path.read_bytes()
        if struct.unpack_from('<I',data,28)[0]:
            subprocess.run(['/root/symbian3-full/epoc32/tools/petran','-nocompress',str(path)],
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
            data=path.read_bytes()
        sites,table,size=parse_e32_import_sites(data)
    if {n:sorted(v) for n,v in table.items()}!={n:sorted(v) for n,v in declared.items()}:
        raise ValueError('raw import sites disagree with native ELF2E32 import dump')
    return sites,size


def verify_declared_import_relocations(old, new, files0, files1, name, imports, sites, source_code_size):
    """822: accept only exact E32-declared import sites, ordinal and addend.

    Import slots include vtable pointers as well as ARM thunks. No arbitrary
    words, executable instructions, header fields or data are masked.
    """
    start0,end0,_,_=rom_code_span(old,files0,name)
    start1,end1,_,_=rom_code_span(new,files1,name)
    before,after=old[start0:end0],new[start1:end1]
    if len(before)!=len(after) or len(before)!=120+source_code_size:
        raise ValueError('shared consumer size changed: '+name)
    differences=sorted({i & ~3 for i,(a,b) in enumerate(zip(before,after)) if a!=b})
    if not differences: return dict(module=name,changed_import_literals=0)
    tables={}
    rows=[]
    for offset in differences:
        if offset not in sites:
            raise ValueError('difference outside declared E32 import sites: '+name+' offset='+hex(offset))
        module,ordinal,addend=sites[offset]
        if (ordinal,addend) not in imports.get(module,[]):
            raise ValueError('site not in declared import contract')
        provider='sys\\bin\\'+module+'.dll'
        if provider not in tables:
            exports0,code0,size0=rom_export_table(old,files0,provider)
            exports1,code1,size1=rom_export_table(new,files1,provider)
            if len(exports0)!=len(exports1) or size0!=size1:
                raise ValueError('shared provider ABI/size changed: '+provider)
            tables[provider]=(exports0,exports1,code0,code1,size0)
        exports0,exports1,code0,code1,size=tables[provider]
        a,=struct.unpack_from('<I',before,offset)
        b,=struct.unpack_from('<I',after,offset)
        if (not 1<=ordinal<=len(exports0) or exports0[ordinal-1]+addend!=a or
                exports1[ordinal-1]+addend!=b or a-code0!=b-code1 or
                not code0<=(a & ~1)<code0+size or not code1<=(b & ~1)<code1+size):
            raise ValueError('declared import target/ordinal/addend changed: '+name+' offset='+hex(offset))
        rows.append(dict(offset=offset,before=a,after=b,provider=provider,ordinal=ordinal,addend=addend))
    return dict(module=name,changed_import_literals=len(rows),imports=rows,
                policy='exact-E32-import-sites-same-ordinal-addend-function-offset-no-code-mask')


def verify_stack_wrapper():
    objects = list(Path('/root/symbian3-full/epoc32/build/mcsmenu-build').glob(
        '*/mcsmenu_dll/armv5/urel/menusrv.o'))
    if len(objects) != 1:
        raise ValueError('ambiguous current server object for entry-wrapper verification')
    disassembly = subprocess.check_output([
        '/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump', '-drC', str(objects[0])], text=True)
    match = re.search(r'<HtcleoMcsSoftwareException\(TExcType\)>:\n(.*?)(?:\n\n|\Z)', disassembly, re.S)
    if not match:
        raise ValueError('missing naked handler in compiled object')
    block = match.group(1)
    instructions = re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{4})\s+', block, re.M)
    if (instructions[:2] != ['4669', '4672'] or len(instructions) < 3 or
            int(instructions[2], 16) & 0xf800 != 0xe000 or
            'R_ARM_THM_JUMP11' not in block or 'HtcleoMcsExceptionStackBody' not in block):
        raise ValueError('handler entry must capture SP/LR then tail branch without a C prologue')
    return dict(object=str(objects[0]), object_sha256=sha(objects[0]), entry_disassembly=block.strip())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--profile', choices=tuple(PROFILES), default='grid')
    for name in ('parent', 'recipe', 'image', 'rom-log', 'report'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    parent_sha, changed_binary, status = PROFILES[a.profile]
    if sha(a.parent / 'initrd.gz') != parent_sha:
        raise ValueError('not the immutable profile parent')
    wserv_patch = None
    wserv_evidence = None
    if a.profile == 'wserv-find-notfound':
        wserv_patch = runpy.run_path(str(HERE / 'apply-htcleo-wserv-find-notfound.py'))
        sdkroot = Path('/root/symbian3-full')
        source = (sdkroot / wserv_patch['REL'] / wserv_patch['NAME']).read_text(encoding='latin-1')
        if wserv_patch['transform'](wserv_patch['transform'](source, True)) != source:
            raise ValueError('WServ final-query source drift')
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        wserv_evidence = json.loads((native / 'WSERV-FIND-NOTFOUND-OBJECTS.json').read_text())
        if (wserv_evidence['status'] != 'HTCLEO_WSERV_FIND_NOTFOUND_OBJECTS_OK' or
                wserv_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                wserv_evidence['base_binary_sha256'] != wserv_patch['CONTROL_SHA'] or
                wserv_evidence['source_sha256'] != wserv_patch['digest'](source) or
                wserv_evidence['base_certificate_sha256'] != sha(native / 'wserv-find-notfound-base-802.json') or
                len(wserv_evidence['changed_objects']) != 1 or
                Path(wserv_evidence['changed_objects'][0]).name != 'CLIENT.o'):
            raise ValueError('WServ derivation evidence mismatch')
        helper = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleowservfindnotfound.inl'
        if (wserv_evidence['helper_sha256'] != sha(helper) or
                sha(sdkroot / wserv_patch['REL'] / helper.name) != sha(helper) or
                wserv_patch['header_contract'](Path(changed_binary)) != wserv_evidence['header_contract']):
            raise ValueError('WServ helper/ABI contract mismatch')
    enumeration_patch = None
    enumeration_imports = None
    if a.profile in ('menu-task-enumeration','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        enumeration_patch = runpy.run_path(str(HERE / 'apply-htcleo-menu-task-enumeration.py'))
        root = Path('/root/symbian3-full')
        source = (root / enumeration_patch['REL'] / enumeration_patch['NAME']).read_text(encoding='latin-1')
        if enumeration_patch['transform'](enumeration_patch['transform'](source, True)) != source:
            raise ValueError('enumeration source drift')
        helper = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomenutaskenumeration.inl'
        if sha(root / enumeration_patch['REL'] / 'handlersrc' / helper.name) != sha(helper):
            raise ValueError('enumeration compiled helper drift')
        restored = runpy.run_path(str(HERE / 'apply-htcleo-wserv-find-notfound.py'))
        wsource = (root / restored['REL'] / restored['NAME']).read_text(encoding='latin-1')
        if restored['digest'](wsource) != restored['BASE_SHA']:
            raise ValueError('802 WServ source still active')
        if sha(root / 'epoc32/release/armv5/urel/wserv_nga.exe') != restored['CONTROL_SHA']:
            raise ValueError('WServ is not exact742/801 recovery binary')
    hsps_patch = None
    if a.profile in ('hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        hsps_patch = runpy.run_path(str(HERE / 'apply-htcleo-hsps-header-cache-recovery.py'))
        root = Path('/root/symbian3-full')
        source = (root / hsps_patch['REL'] / hsps_patch['NAME']).read_text(encoding='latin-1')
        if hsps_patch['transform'](hsps_patch['transform'](source, True)) != source:
            raise ValueError('HSPS header-cache source drift')
        helper = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleohspsheadercache.inl'
        if sha(root / hsps_patch['REL'] / helper.name) != sha(helper):
            raise ValueError('HSPS compiled helper drift')
        restored = runpy.run_path(str(HERE / 'apply-htcleo-wserv-find-notfound.py'))
        wsource = (root / restored['REL'] / restored['NAME']).read_text(encoding='latin-1')
        if restored['digest'](wsource) != restored['BASE_SHA'] or sha(root / 'epoc32/release/armv5/urel/wserv_nga.exe') != restored['CONTROL_SHA']:
            raise ValueError('HSPS recovery requires exact742/801 WServ')
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        before_dump = (a.parent / 'build/hspsthemeserver-e32-dump.txt').read_text()
        after_dump = (native / 'hspsthemeserver-e32-dump.txt').read_text()
        names = tuple(re.findall(r'^\d+ imports? from ([^{\s]+)', before_dump, re.M))
        after_names = tuple(re.findall(r'^\d+ imports? from ([^{\s]+)', after_dump, re.M))
        if set(names) != set(after_names) or not same_import_contract(selected_imports(before_dump, names), selected_imports(after_dump, names)):
            raise ValueError('HSPS recovery changed native import contract')
        for key in ('Secure ID','Vendor ID','Capabilities','Module Version','Flags',
                    'Min Heap Size','Max Heap Size','Stack Size','Code link addr','Data link addr'):
            values = [re.search(r'^'+re.escape(key)+r':\s*(.+)$', text, re.M) for text in (before_dump, after_dump)]
            if not all(values) or values[0][1].split() != values[1][1].split():
                raise ValueError('HSPS ABI/security contract drift: '+key)
    completion_patch = None
    if a.profile in ('menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        completion_patch = runpy.run_path(str(HERE / 'apply-htcleo-mcs-operation-completion.py'))
        completion_dir = Path('/root/symbian3-full') / completion_patch['REL']
        source = (completion_dir / completion_patch['NAME']).read_text(encoding='latin-1')
        if completion_patch['transform'](completion_patch['transform'](source, True)) != source:
            raise ValueError('operation completion source drift')
        for name in ('htcleomenulaunchtrace.inl','htcleomcsopcompletion.inl'):
            if ((completion_dir / name).read_bytes() !=
                    (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name).read_bytes()):
                raise ValueError('compiled completion helper mismatch')
    lookup_patch = None
    if a.profile in ('menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        lookup_patch = runpy.run_path(str(HERE / 'apply-htcleo-menu-task-lookup-control.py'))
        lookup_dir = Path('/root/symbian3-full') / lookup_patch['REL']
        for name in lookup_patch['BASE']:
            source = (lookup_dir / name).read_text(encoding='latin-1')
            if enumeration_patch and name == enumeration_patch['NAME']:
                source = enumeration_patch['transform'](source, True)
            if lookup_patch['transform'](lookup_patch['transform'](source, name, True), name) != source:
                raise ValueError('task lookup control source drift')
        for name in ('htcleomenulaunchtrace.inl', 'htcleomenutasklookup.inl'):
            if ((lookup_dir / 'handlersrc' / name).read_bytes() !=
                    (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name).read_bytes()):
                raise ValueError('compiled lookup helper mismatch')
    notifier_patch = None
    if a.profile in ('menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        notifier_patch = runpy.run_path(str(HERE / 'apply-htcleo-mcs-applist-notifier.py'))
        notifier_dir = Path('/root/symbian3-full') / notifier_patch['REL']
        for name in notifier_patch['BASE']:
            source = (notifier_dir / name).read_text(encoding='latin-1')
            if notifier_patch['transform'](notifier_patch['transform'](source, name, True), name) != source:
                raise ValueError('notifier source drift')
        for name in ('htcleomcsapplistnotifier.inl', 'htcleomcsactiontrace.inl'):
            if ((notifier_dir / 'srvsrc' / name).read_bytes() !=
                    (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name).read_bytes()):
                raise ValueError('compiled notifier helper mismatch')
    stack_observer = None
    stack_entry = None
    if a.profile in ('menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        stack_observer = runpy.run_path(str(HERE / 'apply-htcleo-mcs-exception-stack.py'))
        stack_dir = Path('/root/symbian3-full') / stack_observer['REL']
        stack_source = (stack_dir / stack_observer['NAME']).read_text(encoding='latin-1')
        if stack_observer['transform'](stack_observer['transform'](stack_source, True)) != stack_source:
            raise ValueError('exception stack source drift')
        stack_asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsexceptionstack.inl'
        if (stack_dir / 'srvsrc' / stack_asset.name).read_bytes() != stack_asset.read_bytes():
            raise ValueError('compiled stack helper mismatch')
        stack_entry = verify_stack_wrapper()
    software_observer = None
    if a.profile in ('menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        software_observer = runpy.run_path(str(HERE / 'apply-htcleo-mcs-software-exception-observer.py'))
        observer_dir = Path('/root/symbian3-full') / software_observer['REL']
        for name in software_observer['BASE']:
            observer_source = (observer_dir / name).read_text(encoding='latin-1')
            if stack_observer and name == stack_observer['NAME']:
                observer_source = stack_observer['transform'](observer_source, True)
            if software_observer['transform'](software_observer['transform'](observer_source, name, True), name) != observer_source:
                raise ValueError('software-exception source drift')
        observer_asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcssoftwareexception.inl'
        if (observer_dir / 'srvsrc' / observer_asset.name).read_bytes() != observer_asset.read_bytes():
            raise ValueError('compiled software-exception helper mismatch')
    server_watch = None
    if a.profile in ('menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        server_watch = runpy.run_path(str(HERE / 'apply-htcleo-mcs-server-exit-watch.py'))
        watch_dir = Path('/root/symbian3-full') / server_watch['REL']
        watch_source = (watch_dir / server_watch['NAME']).read_text(encoding='latin-1')
        if server_watch['transform'](server_watch['transform'](watch_source, True)) != watch_source:
            raise ValueError('server-watch source drift')
        watch_asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsserverwatch.inl'
        if (watch_dir / watch_asset.name).read_bytes() != watch_asset.read_bytes():
            raise ValueError('compiled server-watch helper mismatch')
    if a.profile in ('menu-action', 'menu-launch', 'menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        patch = runpy.run_path(str(HERE / 'apply-htcleo-mcs-action-frontier.py'))
        sdk = Path('/root/symbian3-full') / patch['REL']
        for name in patch['BASE']:
            source = (sdk / name).read_text(encoding='latin-1')
            if server_watch and name == server_watch['NAME']:
                source = server_watch['transform'](source, True)
            base = patch['transform'](source, name, True)
            if patch['transform'](base, name) != source:
                raise ValueError('menu-action source not exact reversible observation')
        asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsactiontrace.inl'
        if (sdk / asset.name).read_text() != asset.read_text():
            raise ValueError('compiled action logger source mismatch')
    if a.profile in ('menu-launch', 'menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        patch = runpy.run_path(str(HERE / 'apply-htcleo-menu-launch-frontier.py'))
        sdk = Path('/root/symbian3-full') / patch['REL']
        source = (sdk / patch['NAME']).read_text(encoding='latin-1')
        if lookup_patch:
            source = lookup_patch['transform'](source, 'handlersrc/menuapphandler.cpp', True)
        if patch['transform'](patch['transform'](source, True)) != source:
            raise ValueError('menu launch source drift')
        if (sdk / asset.name).read_bytes() != asset.read_bytes():
            raise ValueError('handler logger differs from existing action logger')
        pin = dict(line.split('=', 1) for line in (HERE.parent / 'hd2/qsd8250-native-bsp/incremental-migrations/793-menuhandler-parent.txt').read_text().splitlines())
        stock = HERE.parent / 'output/qsd8250-native-full-rom/mcsmenuhandler-stock-792.dll'
        if sha(stock) != pin['PARENT_BINARY_SHA256'] or stock.stat().st_size != int(pin['PARENT_BINARY_SIZE']):
            raise ValueError('unpinned plugin baseline')
        if a.profile == 'menu-launch' and sha(Path(changed_binary)) == pin['PARENT_BINARY_SHA256']:
            raise ValueError('plugin did not change')
        if sha(a.recipe) != pin['PARENT_RECIPE_SHA256']:
            raise ValueError('plugin recipe drift')
        import_parser = runpy.run_path(str(HERE / 'verify-htcleo-g17-settings.py'))['apparc_imports']
        before_dump = stock.with_name('mcsmenuhandler-stock-792-e32-dump.txt').read_text()
        after_dump = stock.with_name('mcsmenuhandler-e32-dump.txt').read_text()
        if enumeration_patch:
            parent_dump = (a.parent / 'build/mcsmenuhandler-e32-dump.txt').read_text()
            if a.profile not in ('gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') and not same_import_contract(import_parser(before_dump), import_parser(parent_dump)):
                raise ValueError('801 stock AppArc contract drift')
            if a.profile in ('gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
                if not same_import_contract(selected_imports(parent_dump), selected_imports(after_dump)):
                    raise ValueError('805 task enumeration imports were changed')
                enumeration_imports = dict(policy='exact805-retained')
            else:
                enumeration_imports = verify_enumeration_imports(parent_dump, after_dump)
        elif not same_import_contract(import_parser(before_dump), import_parser(after_dump)):
            raise ValueError('native AppArc/apparc import ordinals changed')
        for contract in ('Secure ID: 200113de', 'Vendor ID: 101fb657',
                         'Capabilities: 00000000 000ffffe', 'Module Version: 10.0',
                         'Number of exports = 1'):
            if (contract.lower() not in [line.strip().lower() for line in before_dump.splitlines()] or
                    contract.lower() not in [line.strip().lower() for line in after_dump.splitlines()]):
                raise ValueError('plugin ABI/security contract changed: ' + contract)
    request_patch = None
    if a.profile in ('menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        request_patch = runpy.run_path(str(HERE / 'apply-htcleo-menu-request-frontier.py'))
        sdk = Path('/root/symbian3-full') / request_patch['REL']
        request_asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomenurequesttrace.inl'
        for name in request_patch['BASE']:
            source = (sdk / name).read_text(encoding='latin-1')
            if stack_observer and name == stack_observer['NAME']:
                source = stack_observer['transform'](source, True)
            if software_observer and name in software_observer['BASE']:
                source = software_observer['transform'](source, name, True)
            base = request_patch['transform'](source, name, True)
            if request_patch['transform'](base, name) != source:
                raise ValueError('request source drift: ' + name)
            if (sdk / name).with_name(request_asset.name).read_bytes() != request_asset.read_bytes():
                raise ValueError('compiled request logger mismatch')
    if a.profile in ('menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
        patch = runpy.run_path(str(HERE / 'apply-htcleo-menu-attribute-frontier.py'))
        sdk = Path('/root/symbian3-full') / patch['REL']
        for name in patch['BASE']:
            source = (sdk / name).read_text(encoding='latin-1')
            if stack_observer and name == stack_observer['NAME']:
                source = stack_observer['transform'](source, True)
            if software_observer and name in software_observer['BASE']:
                source = software_observer['transform'](source, name, True)
            if request_patch and name in request_patch['BASE']:
                source = request_patch['transform'](source, name, True)
            if patch['transform'](patch['transform'](source, name, True), name) != source:
                raise ValueError('attribute source drift: ' + name)
            if (sdk / name).with_name(asset.name).read_bytes() != asset.read_bytes():
                raise ValueError('compiled attribute logger differs from shared action logger')
    if a.recipe.read_text() != (a.parent / 'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('recipe drift from profile parent')
    cache = a.parent / 'build/incremental-release-cache'
    lines = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    parent_count = 65 if a.profile in ('vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 64 if a.profile in ('vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 63 if a.profile in ('gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 62 if a.profile in ('menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 61
    if len(lines) != parent_count:
        raise ValueError('unexpected parent binary count')
    changed = []
    for line in lines:
        digest, source, name = line.split('\t')
        if sha(cache / name) != digest:
            raise ValueError('immutable cache corrupted: ' + name)
        if sha(Path(source)) != digest:
            changed.append(source)
    viewcli_audit = None
    if a.profile == 'viewcli-control':
        viewcli_audit=runpy.run_path(str(HERE/'verify-htcleo-viewcli-source-control.py'))
        viewcli_audit['verify_parent_member']()
        if any(line.split('\t')[1]==changed_binary for line in lines):
            raise ValueError('832 cache expansion already present unexpectedly')
        if sha(Path(changed_binary)) == viewcli_audit['STOCK_SHA']:
            raise ValueError('ViewCLI source control was not built')
        changed.append(changed_binary)
    viewsrv_audit = None
    if a.profile == 'viewsrv-control':
        viewsrv_audit=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
        viewsrv_audit['verify_parent_member']()
        if any(line.split('\t')[1]==changed_binary for line in lines):
            raise ValueError('835 cache expansion already present unexpectedly')
        if sha(Path(changed_binary))==viewsrv_audit['STOCK_SHA']:raise ValueError('ViewServer source control not built')
        changed.append(changed_binary)
    expected_changed = [] if a.profile in ('menu-launch','gsapp-plugin') else [changed_binary]
    if changed != expected_changed:
        raise ValueError('unexpected binary deltas: ' + repr(changed))
    old, new = (a.parent / 'initrd.gz').read_bytes(), a.image.read_bytes()
    files0 = ROM['rom_files'](old, (a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    files1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    keyblock_evidence = None
    if a.profile == 'gsapp-keyblock':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-keyblock-local.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        keyblock_evidence = json.loads((native / 'GSAPP-KEYBLOCK-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/819-gsapp-keyblock-local/BASE-OBJECTS.json'
        if (keyblock_evidence['status'] != 'HTCLEO_GSAPP_KEYBLOCK_OBJECTS_OK' or
                keyblock_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                keyblock_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                keyblock_evidence['objects'] != akn_audit['objects']() or
                keyblock_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        keyblock_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-keyblock-819-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('SGC keyblock source drift')
        if akn_audit['PATCH']['transform'](source,True) != (a.parent / 'build/aknsgcc-812.cpp').read_text(encoding='latin-1'):
            raise ValueError('818 SGC source not retained beneath keyblock guard')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSKB',):
            if witness in before or witness not in after:
                raise ValueError('GSApp SGC params observer missing in actual ROM')
    fade_evidence = None
    if a.profile == 'gsapp-sgc-fade':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-sgc-fade-local.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        fade_evidence = json.loads((native / 'GSAPP-SGC-FADE-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/816-gsapp-sgc-fade-local/BASE-OBJECTS.json'
        if (fade_evidence['status'] != 'HTCLEO_GSAPP_SGC_FADE_OBJECTS_OK' or
                fade_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                fade_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                fade_evidence['objects'] != akn_audit['objects']() or
                fade_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        fade_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-sgc-fade-816-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('SGC fade source drift')
        if akn_audit['PATCH']['transform'](source,True) != (a.parent / 'build/aknsgcc-812.cpp').read_text(encoding='latin-1'):
            raise ValueError('815 SGC functional source not retained beneath fade patch')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSF',):
            if witness in before or witness not in after:
                raise ValueError('GSApp SGC params observer missing in actual ROM')
    params_evidence = None
    if a.profile == 'gsapp-sgc-params':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-sgc-params-local.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        params_evidence = json.loads((native / 'GSAPP-SGC-PARAMS-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/812-gsapp-sgc-params-local/BASE-OBJECTS.json'
        if (params_evidence['status'] != 'HTCLEO_GSAPP_SGC_PARAMS_OBJECTS_OK' or
                params_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                params_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                params_evidence['objects'] != akn_audit['objects']() or
                params_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        params_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-sgc-params-812-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('SGC params source drift')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSC',):
            if witness in before or witness not in after:
                raise ValueError('GSApp SGC params observer missing in actual ROM')
    focus_evidence = None
    if a.profile == 'gsapp-focus':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-focus-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        focus_evidence = json.loads((native / 'GSAPP-FOCUS-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/818-gsapp-focus-frontier/BASE-OBJECTS.json'
        if (focus_evidence['status'] != 'HTCLEO_GSAPP_FOCUS_OBJECTS_OK' or
                focus_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                focus_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                focus_evidence['objects'] != akn_audit['objects']() or
                focus_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        focus_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-focus-818-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('Focus frontier source drift')
        if akn_audit['PATCH']['transform'](source,True) != (a.parent / 'build/AknAppUi-811.cpp').read_text(encoding='latin-1'):
            raise ValueError('817 AppUi policy source changed beneath observation')
        if sha(cache / 'gsapp.exe') != 'c2b4216e919af1d53333df8a3dd5507b9abb1dd96338e3644a7c4160c97c9b22':
            raise ValueError('817 GSApp parent observer changed')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSW',):
            if witness in before or witness not in after:
                raise ValueError('GSApp Focus observer missing in actual ROM')
    home_priority_ab_evidence = None
    if a.profile == 'home-priority-ab':
        ab=runpy.run_path(str(HERE/'apply-htcleo-home-background-priority-ab.py'))
        home_priority_ab_evidence=ab['verify_rom'](old,new,files0,files1)
        if sha(cache/'ailaunch.exe')!='c04fdce1229c2279c5425513a657b0af18c6a17d20c43a7b5101d74fae982901':
            raise ValueError('839 Home sampler not retained')
    home_watch_evidence = None
    if a.profile == 'home-kernel-watch':
        ha=runpy.run_path(str(HERE/'verify-htcleo-home-kernel-watch.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        baseline=HERE.parent/'output/iteration-evidence/839-home-kernel-watch/BASE-OBJECTS.json'
        home_watch_evidence=json.loads((native/'HOME-KERNEL-WATCH-OBJECTS.json').read_text())
        ha['check_sources']()
        if (home_watch_evidence['status']!='HTCLEO_HOME_KERNEL_WATCH_OBJECTS_OK' or
                home_watch_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                home_watch_evidence['base_binary_sha256']!=sha(cache/'ailaunch.exe') or
                home_watch_evidence['objects']!=ha['objects']() or
                home_watch_evidence['baseline_sha256']!=sha(baseline)):
            raise ValueError('Home sampler provenance drift')
        table=ha['GS']['imports']((native/ha['DUMP']).read_text())
        home_watch_evidence['rom_providers']=ha['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('viewsrv.dll','a2c3a9c353cf69e4f3eff62d276432f0f7377a363a3bdf8d8db07d24cc69dec2'),
                ('viewcli.dll','1330252e5e0919bdc025703e1cfaa619713ee4c70775bc71cf2336116c1516ce'),
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('838 recovery/observation not retained '+filename)
    vws_session_evidence = None
    if a.profile == 'vws-session-deactivation':
        va=runpy.run_path(str(HERE/'verify-htcleo-vws-session-deactivation.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        baseline=HERE.parent/'output/iteration-evidence/838-vws-session-deactivation/BASE-OBJECTS.json'
        vws_session_evidence=json.loads((native/'VWS-SESSION-DEACTIVATION-OBJECTS.json').read_text())
        va['check_sources']()
        if (vws_session_evidence['status']!='HTCLEO_VWS_SESSION_DEACTIVATION_OBJECTS_OK' or
                vws_session_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                vws_session_evidence['base_binary_sha256']!=sha(cache/'viewsrv.dll') or
                vws_session_evidence['objects']!=va['objects']() or
                vws_session_evidence['baseline_sha256']!=sha(baseline)):
            raise ValueError('session-deactivation provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        vws_session_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        vws_session_evidence['client_rom_binding']=va['CONTROL']['verify_viewcli_rom_binding'](old,new,files0,files1)
        for filename,expected in (
                ('viewcli.dll','1330252e5e0919bdc025703e1cfaa619713ee4c70775bc71cf2336116c1516ce'),
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('837 recovery/observation not retained '+filename)
    vws_event_evidence = None
    if a.profile == 'vws-server-event':
        va=runpy.run_path(str(HERE/'verify-htcleo-vws-server-event.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        baseline=HERE.parent/'output/iteration-evidence/837-vws-server-event/BASE-OBJECTS.json'
        vws_event_evidence=json.loads((native/'VWS-SERVER-EVENT-OBJECTS.json').read_text())
        va['check_sources']()
        if (vws_event_evidence['status']!='HTCLEO_VWS_SERVER_EVENT_OBJECTS_OK' or
                vws_event_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                vws_event_evidence['base_binary_sha256']!=sha(cache/'viewsrv.dll') or
                vws_event_evidence['objects']!=va['objects']() or
                vws_event_evidence['baseline_sha256']!=sha(baseline)):
            raise ValueError('server-event provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        vws_event_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        vws_event_evidence['client_rom_binding']=va['CONTROL']['verify_viewcli_rom_binding'](old,new,files0,files1)
        for filename,expected in (
                ('viewcli.dll','1330252e5e0919bdc025703e1cfaa619713ee4c70775bc71cf2336116c1516ce'),
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('836 recovery/observation not retained '+filename)
    viewsrv_evidence = None
    if a.profile == 'viewsrv-control':
        va=viewsrv_audit
        native=HERE.parent/'output/qsd8250-native-full-rom'
        receipt=va['EVID']/'CONTROL-OBJECTS.json'
        viewsrv_evidence=json.loads((native/'VIEWSRV-SOURCE-CONTROL-OBJECTS.json').read_text())
        va['check_sources']()
        if (viewsrv_evidence['status']!='HTCLEO_VIEWSRV_SOURCE_CONTROL_OBJECTS_OK' or
                viewsrv_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                viewsrv_evidence['stock_sha256']!=va['STOCK_SHA'] or
                viewsrv_evidence['control_receipt_sha256']!=sha(receipt) or
                viewsrv_evidence['objects']!=va['objects']() or viewsrv_evidence['sources']!=va['sources']()):
            raise ValueError('ViewServer source-control provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        viewsrv_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        viewsrv_evidence['client_rom_binding']=va['verify_viewcli_rom_binding'](old,new,files0,files1)
        for filename,expected in (
                ('viewcli.dll','1330252e5e0919bdc025703e1cfaa619713ee4c70775bc71cf2336116c1516ce'),
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('835 recovery/observation not retained '+filename)
        current_cache=(native/'Symbian3/build/incremental-release-cache/RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
        additions=[row for row in current_cache if row.split('\t')[1]==changed_binary]
        if len(current_cache)!=65 or len(additions)!=1 or additions[0].split('\t')[0]!=sha(Path(changed_binary)):
            raise ValueError('ViewServer65-input cache expansion drift')
    vws_state_evidence = None
    if a.profile == 'vws-client-state':
        va=runpy.run_path(str(HERE/'verify-htcleo-vws-client-state.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        baseline=HERE.parent/'output/iteration-evidence/835-vws-client-state/BASE-OBJECTS.json'
        vws_state_evidence=json.loads((native/'VWS-CLIENT-STATE-OBJECTS.json').read_text())
        va['check_sources']()
        if (vws_state_evidence['status']!='HTCLEO_VWS_CLIENT_STATE_OBJECTS_OK' or
                vws_state_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                vws_state_evidence['base_binary_sha256']!=sha(cache/'viewcli.dll') or
                vws_state_evidence['objects']!=va['objects']() or
                vws_state_evidence['baseline_sha256']!=sha(baseline)):
            raise ValueError('VWS client state provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        vws_state_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('834 recovery/observation not retained '+filename)
    vws_queue_evidence = None
    if a.profile == 'vws-client-queue':
        va=runpy.run_path(str(HERE/'verify-htcleo-vws-client-queue.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        baseline=HERE.parent/'output/iteration-evidence/834-vws-client-queue/BASE-OBJECTS.json'
        vws_queue_evidence=json.loads((native/'VWS-CLIENT-QUEUE-OBJECTS.json').read_text())
        va['check_sources']()
        if (vws_queue_evidence['status']!='HTCLEO_VWS_CLIENT_QUEUE_OBJECTS_OK' or
                vws_queue_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                vws_queue_evidence['base_binary_sha256']!=sha(cache/'viewcli.dll') or
                vws_queue_evidence['objects']!=va['objects']() or
                vws_queue_evidence['baseline_sha256']!=sha(baseline)):
            raise ValueError('VWS client queue provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        vws_queue_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('833 recovery/observation not retained '+filename)
    viewcli_evidence = None
    if a.profile == 'viewcli-control':
        va=viewcli_audit
        native=HERE.parent/'output/qsd8250-native-full-rom'
        receipt=va['EVID']/'CONTROL-OBJECTS.json'
        viewcli_evidence=json.loads((native/'VIEWCLI-SOURCE-CONTROL-OBJECTS.json').read_text())
        va['check_sources']()
        if (viewcli_evidence['status']!='HTCLEO_VIEWCLI_SOURCE_CONTROL_OBJECTS_OK' or
                viewcli_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                viewcli_evidence['stock_sha256']!=va['STOCK_SHA'] or
                viewcli_evidence['control_receipt_sha256']!=sha(receipt) or
                viewcli_evidence['objects']!=va['objects']() or
                viewcli_evidence['sources']!=va['sources']()):
            raise ValueError('ViewCLI source-control provenance drift')
        table=va['GS']['imports']((native/va['DUMP']).read_text())
        viewcli_evidence['rom_providers']=va['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('stem_cone.dll','3e91ae0c96ea220f3a6c6111376679814c309233a549a9f1ba8a70d6d2f6164a'),
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c')):
            if sha(cache/filename)!=expected:raise ValueError('832 observation/recovery not retained '+filename)
        actual_cache=(native/'Symbian3/build/incremental-release-cache/RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
        additions=[row for row in actual_cache if row.split('\t')[1]==changed_binary]
        if len(actual_cache)!=64 or len(additions)!=1 or additions[0].split('\t')[0]!=sha(Path(changed_binary)):
            raise ValueError('ViewCLI 64-input cache expansion drift')
    home_event_evidence = None
    if a.profile == 'home-view-event':
        ta=runpy.run_path(str(HERE/'verify-htcleo-home-view-event.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/832-home-view-event/BASE-OBJECTS.json'
        home_event_evidence=json.loads((native/'HOME-VIEW-EVENT-OBJECTS.json').read_text())
        if (home_event_evidence['status']!='HTCLEO_HOME_VIEW_EVENT_OBJECTS_OK' or
                home_event_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                home_event_evidence['base_binary_sha256']!=sha(cache/'stem_cone.dll') or
                home_event_evidence['objects']!=ta['objects']() or
                home_event_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('Home CONE event provenance drift')
        source=(ta['SDK']/ta['P']['REL']/ta['P']['NAME']).read_text(encoding='latin-1')
        if ta['P']['transform'](source)!=source:raise ValueError('Home CONE event source drift')
        table=ta['GS']['imports']((native/ta['DUMP']).read_text())
        home_event_evidence['rom_providers']=ta['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c'),
                ('gsframework.dll','15100468cc7f24df32075d61cf9830dfd66acc9b8dd21c2ab1518118d281ac6d'),
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5')):
            if sha(cache/filename)!=expected:raise ValueError('831 recovery/observation not retained '+filename)
    cone_event_evidence = None
    if a.profile == 'gsapp-cone-event':
        ta=runpy.run_path(str(HERE/'verify-htcleo-gsapp-cone-view-event.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/831-gsapp-cone-view-event/BASE-OBJECTS.json'
        cone_event_evidence=json.loads((native/'GSAPP-CONE-EVENT-OBJECTS.json').read_text())
        if (cone_event_evidence['status']!='HTCLEO_GSAPP_CONE_EVENT_OBJECTS_OK' or
                cone_event_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                cone_event_evidence['base_binary_sha256']!=sha(cache/'stem_cone.dll') or
                cone_event_evidence['objects']!=ta['objects']() or
                cone_event_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS CONE event provenance drift')
        source=(ta['SDK']/ta['P']['REL']/ta['P']['NAME']).read_text(encoding='latin-1')
        if ta['P']['transform'](source)!=source:raise ValueError('GS CONE event source drift')
        table=ta['GS']['imports']((native/ta['DUMP']).read_text())
        cone_event_evidence['rom_providers']=ta['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('stem_avkon.dll','efe7aac0667681faa61d0e91c5dfd6f8b2a3a54a62834b10a7b7944918488c64'),
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c'),
                ('gsframework.dll','15100468cc7f24df32075d61cf9830dfd66acc9b8dd21c2ab1518118d281ac6d'),
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5')):
            if sha(cache/filename)!=expected:raise ValueError('830 recovery/observation not retained '+filename)
    transition_evidence = None
    if a.profile == 'gsapp-transition':
        ta=runpy.run_path(str(HERE/'verify-htcleo-gsapp-view-transition.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/830-gsapp-view-transition/BASE-OBJECTS.json'
        transition_evidence=json.loads((native/'GSAPP-TRANSITION-OBJECTS.json').read_text())
        if (transition_evidence['status']!='HTCLEO_GSAPP_TRANSITION_OBJECTS_OK' or
                transition_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                transition_evidence['base_binary_sha256']!=sha(cache/'stem_avkon.dll') or
                transition_evidence['objects']!=ta['objects']() or
                transition_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS transition provenance drift')
        source=(ta['SDK']/ta['P']['REL']/ta['P']['NAME']).read_text(encoding='latin-1')
        if ta['P']['transform'](source)!=source:raise ValueError('GS transition source drift')
        table=ta['GS']['imports']((native/ta['DUMP']).read_text())
        transition_evidence['rom_providers']=ta['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('gsapp.exe','4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c'),
                ('gsframework.dll','15100468cc7f24df32075d61cf9830dfd66acc9b8dd21c2ab1518118d281ac6d'),
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5')):
            if sha(cache/filename)!=expected:raise ValueError('829 recovery not retained '+filename)
    async_evidence = None
    if a.profile == 'gsapp-async':
        la=runpy.run_path(str(HERE/'verify-htcleo-gsapp-async-view-event.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/829-gsapp-async-view-event/BASE-OBJECTS.json'
        async_evidence=json.loads((native/'GSAPP-ASYNC-OBJECTS.json').read_text())
        if (async_evidence['status']!='HTCLEO_GSAPP_ASYNC_OBJECTS_OK' or
                async_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                async_evidence['base_binary_sha256']!=sha(cache/'gsapp.exe') or
                async_evidence['objects']!=la['objects']() or
                async_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS async view witness provenance drift')
        source=(la['SDK']/la['P']['REL']/la['P']['NAME']).read_text(encoding='latin-1')
        if la['P']['transform'](source)!=source:raise ValueError('GS async view source drift')
        table=la['GS']['imports']((native/la['DUMP']).read_text())
        async_evidence['rom_providers']=la['GS']['verify_providers'](new,files1,table)
        async_evidence['exception_wrapper']=la['EX']['verify_wrapper']()
        for filename,expected in (
                ('gsframework.dll','15100468cc7f24df32075d61cf9830dfd66acc9b8dd21c2ab1518118d281ac6d'),
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5'),
                ('stem_avkon.dll','0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776')):
            if sha(cache/filename)!=expected:raise ValueError('827 retention drift '+filename)
    list_evidence = None
    if a.profile == 'gsapp-list':
        la=runpy.run_path(str(HERE/'verify-htcleo-gsapp-input-activation.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/828-gsapp-list-activation/BASE-OBJECTS.json'
        list_evidence=json.loads((native/'GSAPP-LIST-OBJECTS.json').read_text())
        if (list_evidence['status']!='HTCLEO_GSAPP_LIST_OBJECTS_OK' or
                list_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                list_evidence['base_binary_sha256']!=sha(cache/'gsapp.exe') or
                list_evidence['objects']!=la['objects']() or
                list_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS list witness provenance drift')
        source=(la['SDK']/la['P']['REL']/la['P']['NAME']).read_text(encoding='latin-1')
        if la['P']['transform'](source)!=source:raise ValueError('GS list source drift')
        table=la['GS']['imports']((native/la['DUMP']).read_text())
        list_evidence['rom_providers']=la['GS']['verify_providers'](new,files1,table)
        list_evidence['exception_wrapper']=la['EX']['verify_wrapper']()
        for filename,expected in (
                ('gsframework.dll','15100468cc7f24df32075d61cf9830dfd66acc9b8dd21c2ab1518118d281ac6d'),
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5'),
                ('stem_avkon.dll','0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776')):
            if sha(cache/filename)!=expected:raise ValueError('827 retention drift '+filename)
    child_evidence = None
    if a.profile == 'gsapp-child':
        ch=runpy.run_path(str(HERE/'verify-htcleo-gsapp-child-frontier.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/827-gsapp-child-frontier/BASE-OBJECTS.json'
        child_evidence=json.loads((native/'GSAPP-CHILD-OBJECTS.json').read_text())
        if (child_evidence['status']!='HTCLEO_GSAPP_CHILD_OBJECTS_OK' or
                child_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                child_evidence['base_binary_sha256']!=sha(cache/'gsframework.dll') or
                child_evidence['objects']!=ch['objects']() or
                child_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS child witness provenance drift')
        source=(ch['SDK']/ch['P']['REL']/ch['P']['NAME']).read_text(encoding='latin-1')
        if ch['P']['transform'](source)!=source:raise ValueError('GS child source drift')
        table=ch['GS']['imports']((native/ch['DUMP']).read_text())
        child_evidence['rom_providers']=ch['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('ecom.dll','b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5'),
                ('gsapp.exe','357f146ed426b06f5a6ab273c5bea146ebf7be4de622c9615b0004a6bd32b6eb'),
                ('stem_avkon.dll','0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776')):
            if sha(cache/filename)!=expected:raise ValueError('826 retention drift '+filename)
        for raw,entries in ((old,files0),(new,files1)):
            module=ROM['file_data'](raw,entries,'sys\\bin\\gsframework.dll')
            if struct.unpack_from('<I',module,0x3c)[0]!=127:
                raise ValueError('GSFramework127 ROM exports drift')
    create_evidence = None
    if a.profile == 'gsapp-create':
        ca=runpy.run_path(str(HERE/'verify-htcleo-gsapp-ecom-create-retry.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        evidence=HERE.parent/'output/iteration-evidence/826-gsapp-ecom-create-retry'
        base=evidence/'CONTROL-OBJECTS.json'
        control=evidence/'ecom-native-source-control-825.dll'
        create_evidence=json.loads((native/'GSAPP-CREATE-RETRY-OBJECTS.json').read_text())
        if (create_evidence['status']!='HTCLEO_GSAPP_CREATE_RETRY_OBJECTS_OK' or
                create_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                create_evidence['base_binary_sha256']!=sha(cache/'ecom.dll') or
                create_evidence['objects']!=ca['objects']() or
                create_evidence['baseline_sha256']!=sha(base) or
                create_evidence['control_sha256']!=sha(control)):
            raise ValueError('GS ECom create provenance drift')
        cc=ca['CONTROL']
        create_evidence['verified_source_control']=cc['compare'](
            cc['decode'](cache/'ecom.dll'),cc['decode'](control))
        source=(ca['SDK']/ca['P']['REL']/ca['P']['NAME']).read_text()
        if ca['P']['transform'](source)!=source:raise ValueError('GS ECom source drift')
        table=ca['GS']['imports']((native/ca['DUMP']).read_text())
        create_evidence['rom_providers']=ca['GS']['verify_providers'](new,files1,table)
        for filename,expected in (
                ('gsframework.dll','1c9e75f7b6cd5a6cb00de8fba2fc4830e73d701ddacbf4f86bf685100ea357b5'),
                ('gsapp.exe','357f146ed426b06f5a6ab273c5bea146ebf7be4de622c9615b0004a6bd32b6eb'),
                ('stem_avkon.dll','0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776')):
            if sha(cache/filename)!=expected:raise ValueError('825 shell/observer retention drift '+filename)
        for raw,entries in ((old,files0),(new,files1)):
            data=ROM['file_data'](raw,entries,'sys\\bin\\ecom.dll')
            if struct.unpack_from('<I',data,0x3c)[0]!=39:raise ValueError('ECom39 ROM exports drift')
    notify_evidence = None
    if a.profile == 'gsapp-notify':
        na=runpy.run_path(str(HERE/'verify-htcleo-gsapp-ecom-notify-guard.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/825-gsapp-ecom-notify-guard/BASE-OBJECTS.json'
        notify_evidence=json.loads((native/'GSAPP-NOTIFY-OBJECTS.json').read_text())
        if (notify_evidence['status']!='HTCLEO_GSAPP_NOTIFY_OBJECTS_OK' or
                notify_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                notify_evidence['base_binary_sha256']!=sha(cache/'gsframework.dll') or
                notify_evidence['objects']!=na['objects']() or
                notify_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS notifier object provenance drift')
        source=(na['SDK']/na['P']['REL']/na['P']['NAME']).read_text(encoding='latin-1')
        if na['P']['transform'](source)!=source:raise ValueError('GS notifier source drift')
        parser=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
        table=parser['imports']((native/na['DUMP']).read_text())
        notify_evidence['rom_providers']=parser['verify_providers'](new,files1,table)
        for filename,expected in (
                ('gsapp.exe','357f146ed426b06f5a6ab273c5bea146ebf7be4de622c9615b0004a6bd32b6eb'),
                ('stem_avkon.dll','0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776'),
                ('stem_cone.dll','a267a5862d864872c067881667703d1c717e70c2e9a1018cddd9162b6dbb845b')):
            if sha(cache/filename)!=expected:raise ValueError('Inherited824 observer drift '+filename)
        for rom_data,entries in ((old,files0),(new,files1)):
            module=ROM['file_data'](rom_data,entries,'sys\\bin\\gsframework.dll')
            if struct.unpack_from('<I',module,0x3c)[0]!=127:
                raise ValueError('GSFramework127 exports not preserved in actualROM')
    exception_evidence = None
    if a.profile == 'gsapp-exception':
        ea=runpy.run_path(str(HERE/'verify-htcleo-gsapp-exception-witness.py'))
        native=HERE.parent/'output/qsd8250-native-full-rom'
        base=HERE.parent/'output/iteration-evidence/824-gsapp-exception-witness/BASE-OBJECTS.json'
        exception_evidence=json.loads((native/'GSAPP-EXCEPTION-OBJECTS.json').read_text())
        if (exception_evidence['status']!='HTCLEO_GSAPP_EXCEPTION_OBJECTS_OK' or
                exception_evidence['binary_sha256']!=sha(Path(changed_binary)) or
                exception_evidence['base_binary_sha256']!=sha(cache/'gsapp.exe') or
                exception_evidence['objects']!=ea['objects']() or
                exception_evidence['baseline_sha256']!=sha(base)):
            raise ValueError('GS exception object provenance drift')
        exception_evidence['entry_wrapper']=ea['verify_wrapper']()
        source=(ea['SDK']/ea['PATCH']['REL']/ea['PATCH']['NAME']).read_text(encoding='latin-1')
        if ea['PATCH']['transform'](source)!=source:raise ValueError('GS exception source drift')
        parser=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
        table=parser['imports']((native/'gsapp-exception-824-full-dump.txt').read_text())
        exception_evidence['rom_providers']=parser['verify_providers'](new,files1,table)
        if sha(cache/'stem_avkon.dll')!='0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776':
            raise ValueError('823 lifetime observer not retained')
        before=ROM['file_data'](old,files0,'sys\\bin\\gsapp.exe')
        after=ROM['file_data'](new,files1,'sys\\bin\\gsapp.exe')
        witness='C:\\Symbian3\\GSEXCLOG.TXT'.encode('utf-16le')
        if witness in before or witness not in after:raise ValueError('GS exception sink missing in actual ROM')
    lifetime_evidence = None
    if a.profile == 'gsapp-lifetime':
        la = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-lifetime-observer.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        base = HERE.parent / 'output/iteration-evidence/823-gsapp-lifetime-observer/BASE-OBJECTS.json'
        lifetime_evidence = json.loads((native / 'GSAPP-LIFETIME-OBJECTS.json').read_text())
        if (lifetime_evidence['status'] != 'HTCLEO_GSAPP_LIFETIME_OBJECTS_OK' or
                lifetime_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                lifetime_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                lifetime_evidence['objects'] != la['objects']() or
                lifetime_evidence['baseline_sha256'] != sha(base)):
            raise ValueError('lifetime observer object provenance drift')
        source=(la['SDK']/la['PATCH']['REL']/la['PATCH']['NAME']).read_text(encoding='ascii')
        if la['PATCH']['transform'](source)!=source:
            raise ValueError('clock lifetime helper drift')
        if sha(la['SDK']/la['PATCH']['REL']/'AknAppUi.cpp')!=la['PATCH']['APPUI_SHA']:
            raise ValueError('AppUi outside clock helper changed')
        gs_audit=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
        lifetime_evidence['rom_providers']=gs_audit['verify_providers'](
            new,files1,gs_audit['imports']((native/'avkon-lifetime-823-full-dump.txt').read_text()))
        before=ROM['file_data'](old,files0,'sys\\bin\\avkon.dll')
        after=ROM['file_data'](new,files1,'sys\\bin\\avkon.dll')
        if b' GSL1' in before or b' GSL1' not in after:
            raise ValueError('lifetime fields absent from actual Avkon ROM bytes')
        if sha(cache/'stem_cone.dll')!='a267a5862d864872c067881667703d1c717e70c2e9a1018cddd9162b6dbb845b':
            raise ValueError('822 CONE not retained')
    redraw_evidence = None
    if a.profile == 'gsapp-redraw':
        ca = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-redraw-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        baseline = HERE.parent / 'output/iteration-evidence/822-gsapp-redraw-frontier/BASE-OBJECTS.json'
        redraw_evidence = json.loads((native / 'GSAPP-REDRAW-OBJECTS.json').read_text())
        if (redraw_evidence['status'] != 'HTCLEO_GSAPP_REDRAW_OBJECTS_OK' or
                redraw_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                redraw_evidence['base_binary_sha256'] != sha(cache / 'stem_cone.dll') or
                redraw_evidence['objects'] != ca['objects']() or
                redraw_evidence['baseline_sha256'] != sha(baseline)):
            raise ValueError('CONE redraw object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        redraw_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'cone-redraw-822-full-dump.txt').read_text()))
        source = (ca['SDK'] / ca['PATCH']['REL'] / ca['PATCH']['NAME']).read_text(encoding='latin-1')
        if ca['PATCH']['transform'](source) != source:
            raise ValueError('CONE redraw source drift')
        if sha(cache / 'gsframework.dll') != '4521bcec67615afffecb902868f4d3a356e87352d9feb20291c019ab8aac7b52':
            raise ValueError('821 GSFramework not retained')
        before = ROM['file_data'](old, files0, 'sys\\bin\\cone.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\cone.dll')
        if b'HTCLEO_GSRD' in before or b'HTCLEO_GSRD' not in after:
            raise ValueError('Redraw observation missing in actual ROM')
    plugin_evidence = None
    if a.profile == 'gsapp-plugin':
        pl = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-plugin-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        proof = HERE.parent / 'output/iteration-evidence/821-gsapp-plugin-frontier'
        plugin_evidence = json.loads((native / 'GSAPP-PLUGIN-OBJECTS.json').read_text())
        if (plugin_evidence['status'] != 'HTCLEO_GSAPP_PLUGIN_OBJECTS_OK' or
                plugin_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                plugin_evidence['base_binary_sha256'] != pl['PATCH']['BASE_BINARY'] or
                plugin_evidence['calibration_sha256'] != pl['CALIBRATION_SHA'] or
                plugin_evidence['objects'] != pl['objects']() or
                plugin_evidence['baseline_sha256'] != sha(proof / 'BASE-OBJECTS.json')):
            raise ValueError('GSFramework compiler/source provenance drift')
        if sha(proof / 'gsframework-stock-820.dll') != pl['PATCH']['BASE_BINARY']:
            raise ValueError('Stock820 GSFramework drift')
        source = (pl['SDK'] / pl['PATCH']['REL'] / 'src/GSPluginLoader.cpp').read_text(encoding='latin-1')
        if pl['PATCH']['transform'](source) != source:
            raise ValueError('Plugin trace source drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        table = gs_audit['imports']((native / 'gsframework-plugin-821-full-dump.txt').read_text())
        plugin_evidence['rom_providers'] = gs_audit['verify_providers'](new, files1, table)
        before = ROM['file_data'](old, files0, 'sys\\bin\\gsframework.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\gsframework.dll')
        if struct.unpack_from('<I',before,0x3c)[0] != 123 or struct.unpack_from('<I',before,0x1c)[0] != 0x52e4:
            raise ValueError('Parent ROM GSFramework shape differs from pinned stock')
        if struct.unpack_from('<I',after,0x3c)[0] != 127:
            raise ValueError('ROM loses original123+4compiler constructors')
        if b'HTCLEO_GSPL' in before or b'HTCLEO_GSPL' not in after:
            raise ValueError('Plugin observer missing in actual ROM')
        if sha(cache / 'stem_avkon.dll') != 'b13d8516e804f2bd89538dc8af0f857a14634627a25211b3388bdb33141e7ea5':
            raise ValueError('820 Avkon not retained')
        if sha(cache / 'gsapp.exe') != 'c2b4216e919af1d53333df8a3dd5507b9abb1dd96338e3644a7c4160c97c9b22':
            raise ValueError('817 GSApp not retained')
        current_cache = native / 'Symbian3/build/incremental-release-cache/RELEASE-CACHE-MANIFEST.tsv'
        current = current_cache.read_text().splitlines()
        if len(current) != 63 or sum(line.split('\t')[1] == changed_binary for line in current) != 1:
            raise ValueError('GSFramework cache expansion differs from62to63')
    activation_evidence = None
    if a.profile == 'gsapp-activation':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-activation-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        activation_evidence = json.loads((native / 'GSAPP-ACTIVATION-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/820-gsapp-activation-frontier/BASE-OBJECTS.json'
        if (activation_evidence['status'] != 'HTCLEO_GSAPP_ACTIVATION_OBJECTS_OK' or
                activation_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                activation_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                activation_evidence['objects'] != akn_audit['objects']() or
                activation_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        activation_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-activation-820-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('Activation frontier source drift')
        if sha(cache / 'gsapp.exe') != 'c2b4216e919af1d53333df8a3dd5507b9abb1dd96338e3644a7c4160c97c9b22':
            raise ValueError('817 GSApp observer not retained')
        if (akn_audit['SDK'] / 'sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp').read_bytes() != (a.parent / 'build/aknsgcc-819.cpp').read_bytes():
            raise ValueError('819 keyblock/fade source not retained')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSAV',):
            if witness in before or witness not in after:
                raise ValueError('GSApp activation observer missing in actual ROM')
    appui_evidence = None
    if a.profile == 'gsapp-appui':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-appui-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        appui_evidence = json.loads((native / 'GSAPP-APPUI-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/811-gsapp-appui-frontier/BASE-OBJECTS.json'
        if (appui_evidence['status'] != 'HTCLEO_GSAPP_APPUI_OBJECTS_OK' or
                appui_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                appui_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                appui_evidence['objects'] != akn_audit['objects']() or
                appui_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        appui_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-appui-811-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('AppUi frontier source drift')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSB',):
            if witness in before or witness not in after:
                raise ValueError('GSApp AppUi observer missing in actual ROM')
    sgc_evidence = None
    if a.profile == 'gsapp-sgc-local':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-sgc-local-layout.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        sgc_evidence = json.loads((native / 'GSAPP-SGC-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/810-gsapp-sgc-local-layout/BASE-OBJECTS.json'
        if (sgc_evidence['status'] != 'HTCLEO_GSAPP_SGC_OBJECTS_OK' or
                sgc_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                sgc_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                sgc_evidence['objects'] != akn_audit['objects']() or
                sgc_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        sgc_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-sgc-810-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('SGC compatibility source drift')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSS',):
            if witness in before or witness not in after:
                raise ValueError('GSApp SGC observer missing in actual ROM')
    aknenv_evidence = None
    if a.profile == 'gsapp-aknenv':
        akn_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-aknenv-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        aknenv_evidence = json.loads((native / 'GSAPP-AKNENV-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/809-gsapp-aknenv-frontier/BASE-OBJECTS.json'
        if (aknenv_evidence['status'] != 'HTCLEO_GSAPP_AKNENV_OBJECTS_OK' or
                aknenv_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                aknenv_evidence['base_binary_sha256'] != sha(cache / 'stem_avkon.dll') or
                aknenv_evidence['objects'] != akn_audit['objects']() or
                aknenv_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('Avkon object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        aknenv_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'avkon-aknenv-809-full-dump.txt').read_text()))
        source = (akn_audit['SDK'] / akn_audit['PATCH']['REL'] / akn_audit['PATCH']['NAME']).read_text(encoding='latin-1')
        if akn_audit['PATCH']['transform'](akn_audit['PATCH']['transform'](source,True)) != source:
            raise ValueError('AknEnv source routing drift')
        before = ROM['file_data'](old, files0, 'sys\\bin\\avkon.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\avkon.dll')
        for witness in (b'HTCLEO_GSA', 'C:\\Symbian3\\GSBOOT.TXT'.encode('utf-16le')):
            if witness in before or witness not in after:
                raise ValueError('GSApp AknEnv observer missing in actual ROM')
    statuspane_evidence = None
    if a.profile == 'gsapp-statuspane':
        env_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-statuspane-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        statuspane_evidence = json.loads((native / 'GSAPP-STATUSPANE-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/815-gsapp-statuspane-frontier/BASE-OBJECTS.json'
        if (statuspane_evidence['status'] != 'HTCLEO_GSAPP_STATUSPANE_OBJECTS_OK' or
                statuspane_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                statuspane_evidence['base_binary_sha256'] != sha(cache / 'eikcoctl.dll') or
                statuspane_evidence['objects'] != env_audit['objects']() or
                statuspane_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('EikCoCtl object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        statuspane_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'eikcoctl-statuspane-815-full-dump.txt').read_text()))
        if sha(Path('/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe')) != 'fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137':
            raise ValueError('807 GSApp binary not retained')
        gsroot = Path('/root/symbian3-full/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
        for name in ('GSApp.cpp','GSDocument.cpp','GSUi.cpp','htcleogseikstart.inl'):
            if (gsroot / 'Src' / name).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('retained GSApp source changed: ' + name)
        sp = runpy.run_path(str(HERE / 'apply-htcleo-gsapp-statuspane-frontier.py'))
        spanetext = (Path('/root/symbian3-full') / sp['REL'] / sp['NAME']).read_text(encoding='latin-1')
        if sp['transform'](spanetext) != spanetext:
            raise ValueError('StatusPane source observer not applied')
        for name in ('EIKCOLIB-814.CPP', 'htcleogsappinfo.inl'):
            actual = 'EIKCOLIB.CPP' if name.endswith('.CPP') else name
            if (Path('/root/symbian3-full') / sp['REL'] / actual).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('814 AppInfo source not retained: ' + name)
        before = ROM['file_data'](old, files0, 'sys\\bin\\eikcoctl.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\eikcoctl.dll')
        for witness in (b'HTCLEO_GSP',):
            if witness in before or witness not in after:
                raise ValueError('GSApp StatusPane observer missing in actual ROM')
    appinfo_evidence = None
    if a.profile == 'gsapp-appinfo':
        env_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-appinfo-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        appinfo_evidence = json.loads((native / 'GSAPP-APPINFO-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/814-gsapp-appinfo-frontier/BASE-OBJECTS.json'
        if (appinfo_evidence['status'] != 'HTCLEO_GSAPP_APPINFO_OBJECTS_OK' or
                appinfo_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                appinfo_evidence['base_binary_sha256'] != sha(cache / 'eikcoctl.dll') or
                appinfo_evidence['objects'] != env_audit['objects']() or
                appinfo_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('EikCoCtl object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        appinfo_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'eikcoctl-appinfo-814-full-dump.txt').read_text()))
        if sha(Path('/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe')) != 'fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137':
            raise ValueError('807 GSApp binary not retained')
        gsroot = Path('/root/symbian3-full/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
        for name in ('GSApp.cpp','GSDocument.cpp','GSUi.cpp','htcleogseikstart.inl'):
            if (gsroot / 'Src' / name).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('retained GSApp source changed: ' + name)
        before = ROM['file_data'](old, files0, 'sys\\bin\\eikcoctl.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\eikcoctl.dll')
        for witness in (b'HTCLEO_GSI',):
            if witness in before or witness not in after:
                raise ValueError('GSApp AppInfo observer missing in actual ROM')
    eikbase_evidence = None
    if a.profile == 'gsapp-eikbase':
        env_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-eikbase-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        eikbase_evidence = json.loads((native / 'GSAPP-EIKBASE-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/813-gsapp-eikbase-frontier/BASE-OBJECTS.json'
        if (eikbase_evidence['status'] != 'HTCLEO_GSAPP_EIKBASE_OBJECTS_OK' or
                eikbase_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                eikbase_evidence['base_binary_sha256'] != sha(cache / 'eikcore.dll') or
                eikbase_evidence['objects'] != env_audit['objects']() or
                eikbase_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('EikCore object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        eikbase_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'eikcore-eikbase-813-full-dump.txt').read_text()))
        if sha(Path('/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe')) != 'fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137':
            raise ValueError('807 GSApp binary not retained')
        gsroot = Path('/root/symbian3-full/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
        for name in ('GSApp.cpp','GSDocument.cpp','GSUi.cpp','htcleogseikstart.inl'):
            if (gsroot / 'Src' / name).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('retained GSApp source changed: ' + name)
        before = ROM['file_data'](old, files0, 'sys\\bin\\eikcore.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\eikcore.dll')
        for witness in (b'HTCLEO_GSK',):
            if witness in before or witness not in after:
                raise ValueError('GSApp Eikon base observer missing in actual ROM')
    env_evidence = None
    if a.profile == 'gsapp-env':
        env_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-env-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        env_evidence = json.loads((native / 'GSAPP-ENV-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/808-gsapp-env-frontier/BASE-OBJECTS.json'
        if (env_evidence['status'] != 'HTCLEO_GSAPP_ENV_OBJECTS_OK' or
                env_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                env_evidence['base_binary_sha256'] != sha(cache / 'eikcore.dll') or
                env_evidence['objects'] != env_audit['objects']() or
                env_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('EikCore object provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        env_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'eikcore-env-808-full-dump.txt').read_text()))
        if sha(Path('/root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe')) != 'fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137':
            raise ValueError('807 GSApp binary not retained')
        gsroot = Path('/root/symbian3-full/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
        for name in ('GSApp.cpp','GSDocument.cpp','GSUi.cpp','htcleogseikstart.inl'):
            if (gsroot / 'Src' / name).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('retained GSApp source changed: ' + name)
        before = ROM['file_data'](old, files0, 'sys\\bin\\eikcore.dll')
        after = ROM['file_data'](new, files1, 'sys\\bin\\eikcore.dll')
        for witness in (b'HTCLEO_GSE', 'C:\\Symbian3\\GSBOOT.TXT'.encode('utf-16le')):
            if witness in before or witness not in after:
                raise ValueError('GSApp environment observer missing in actual ROM')
    view_evidence = None
    if a.profile == 'gsapp-view':
        audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-view-frontier.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        view_evidence = json.loads((native / 'GSAPP-VIEW-OBJECTS.json').read_text())
        base_objects = HERE.parent / 'output/iteration-evidence/817-gsapp-view-frontier/BASE-OBJECTS.json'
        if (view_evidence['status'] != 'HTCLEO_GSAPP_VIEW_OBJECTS_OK' or
                view_evidence['binary_sha256'] != sha(Path(changed_binary)) or
                view_evidence['base_binary_sha256'] != sha(cache / 'gsapp.exe') or
                view_evidence['objects'] != audit['objects']() or
                view_evidence['baseline_sha256'] != sha(base_objects)):
            raise ValueError('GSApp view provenance drift')
        gs_audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        view_evidence['rom_providers'] = gs_audit['verify_providers'](
            new, files1, gs_audit['imports']((native / 'gsapp-view-817-full-dump.txt').read_text()))
        gsroot = audit['SDK'] / audit['P']['REL']
        for name in audit['P']['BASE']:
            source = (gsroot / name).read_text(encoding='latin-1')
            if audit['P']['transform'](source,name) != source:
                raise ValueError('GSApp view source not applied')
            audit['P']['transform'](source,name,True)
        for name in ('GSApp.cpp','GSDocument.cpp','htcleogseikstart.inl'):
            if (gsroot / 'Src' / name).read_bytes() != (a.parent / 'build' / name).read_bytes():
                raise ValueError('native GSApp EikStart/document changed: ' + name)
        rawapp = ROM['file_data'](new, files1, 'sys\\bin\\gsapp.exe')
        if b'HTCLEO_GS' not in rawapp:
            raise ValueError('GSApp own writer missing from actual ROM')
        if sha(cache / 'stem_avkon.dll') != '4050b7cbd5d6879aca2e8aa1a1a89747f7af8e7f5e62b0e9f10d888948a9215d':
            raise ValueError('816 Avkon compatibility parent changed')
    gsapp_evidence = None
    if a.profile in ('gsapp-startup','gsapp-eikstart'):
        audit = runpy.run_path(str(HERE / 'verify-htcleo-gsapp-observer.py'))
        native = HERE.parent / 'output/qsd8250-native-full-rom'
        gsapp_evidence = audit['verify'](new, files1, native, Path(changed_binary), cache / 'gsapp.exe', a.parent if a.profile == 'gsapp-eikstart' else None)
        old_app = ROM['file_data'](old, files0, 'sys\\bin\\gsapp.exe')
        new_app = ROM['file_data'](new, files1, 'sys\\bin\\gsapp.exe')
        for witness in (b'HTCLEO_GS', 'C:\\Symbian3\\GSBOOT.TXT'.encode('utf-16le')):
            if (a.profile == 'gsapp-startup' and witness in old_app) or witness not in new_app:
                raise ValueError('GSApp diagnostic absent from actual ROM target')
    if completion_patch:
        old_service = ROM['file_data'](old, files0, 'sys\\bin\\mcsservice.dll')
        new_service = ROM['file_data'](new, files1, 'sys\\bin\\mcsservice.dll')
        witness = 'C:\\Symbian3\\MLAUNCH.TXT'.encode('utf-16le')
        if (a.profile == 'menu-operation-completion' and witness in old_service) or witness not in new_service:
            raise ValueError('completion observer absent from actual service ROM bytes')
    if lookup_patch:
        old_plugin = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenuhandler.dll')
        new_plugin = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenuhandler.dll')
        witness = 'C:\\Symbian3\\MLAUNCH.TXT'.encode('utf-16le')
        if (not completion_patch and witness in old_plugin) or witness not in new_plugin:
            raise ValueError('isolated launch observer absent from actual plugin ROM bytes')
    if notifier_patch:
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenu.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenu.dll')
        if (not lookup_patch and b'MN15' in old_module) or b'MN15' not in new_module:
            raise ValueError('new notifier error branch absent from actual ROM')
        shared_relocations = []
        for shared in ('apgrfx.dll', 'euser.dll', 'drtaeabi.dll'):
            name = 'sys\\bin\\' + shared
            if wserv_patch or a.profile in ('gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
                if a.profile in ('gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab'):
                    matches=re.findall(r'^file=(\S+)\s+"'+re.escape(name)+r'"\s*$',a.recipe.read_text(),re.M|re.I)
                    if len(matches)!=1: raise ValueError('ambiguous shared recipe source: '+name)
                    source=Path(matches[0])
                    dump=subprocess.check_output(['/root/symbian3-full/epoc32/tools/elf2e32','--dump=hi','--e32input='+str(source)],text=True)
                    parser=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))['imports']
                    table=parser(dump)
                    sites,size=load_e32_import_sites(source,table)
                    receipt=verify_declared_import_relocations(old,new,files0,files1,name,table,sites,size)
                    receipt['unchanged_consumer_source_sha256']=sha(source)
                    shared_relocations.append(receipt)
                else:
                    shared_relocations.append(verify_shared_import_relocations(old, new, files0, files1, name))
            elif ROM['file_data'](old, files0, name) != ROM['file_data'](new, files1, name):
                raise ValueError('shared notifier/runtime changed: ' + shared)
    if a.profile == 'menu-exception-stack':
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenu.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenu.dll')
        if b'MEX2' in old_module or b'MEX2' not in new_module:
            raise ValueError('MEX2 stack recorder missing from actual ROM module')
        if 'C:\\Symbian3\\MEXCLOG.TXT'.encode('utf-16le') not in new_module:
            raise ValueError('stack recorder sink changed')
    if a.profile == 'menu-software-exception':
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenu.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenu.dll')
        witness = 'C:\\Symbian3\\MEXCLOG.TXT'.encode('utf-16le')
        if witness in old_module or witness not in new_module:
            raise ValueError('software-exception recorder absent from actual ROM')
    if a.profile == 'menu-server-exit':
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsservice.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsservice.dll')
        watch_literal = '*!MCSSRV'.encode('utf-16le')
        if watch_literal in old_module or watch_literal not in new_module:
            raise ValueError('server-watch selection absent from actual ROM module')
    if a.profile == 'menu-request':
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenu.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenu.dll')
        if b'HTCLEO_MREQ' in old_module or b'HTCLEO_MREQ' not in new_module:
            raise ValueError('new request observer absent from actual ROM module')
    if a.profile == 'menu-attribute':
        old_module = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenu.dll')
        new_module = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenu.dll')
        for witness in (b'HTCLEO_MACT', 'C:\\Symbian3\\MACTLOG.TXT'.encode('utf-16le')):
            if witness in old_module or witness not in new_module:
                raise ValueError('attribute observer absent from actual ROM module')
    if a.profile == 'menu-launch':
        if 'sys\\bin\\mcsmenuhandler.dll' not in files0:
            raise ValueError('plugin was not in parent ROM')
        old_plugin = ROM['file_data'](old, files0, 'sys\\bin\\mcsmenuhandler.dll')
        new_plugin = ROM['file_data'](new, files1, 'sys\\bin\\mcsmenuhandler.dll')
        # Attribute the new observer to the actual ROM module, not just SDK files.
        for witness in (b'HTCLEO_MACT', 'C:\\Symbian3\\MACTLOG.TXT'.encode('utf-16le')):
            if witness in old_plugin or witness not in new_plugin:
                raise ValueError('new observer absent from actual plugin ROM bytes')
        # Stock plugin registrations live inside SPI, not loose ROM .rsc files.
        spi_raw, spi_entries = ROM['SPI']['parse_spi'](a.parent / 'build/ecom-0-0-homescreen-extended.spi')
        if spi_raw != ROM['file_data'](old, files0, 'private\\10009d8f\\ecom-0-0.spi'):
            raise ValueError('parent SPI artifact does not match actual ROM')
        registrations = [entry for entry in spi_entries if entry.name == 'mcsmenuhandler']
        if len(registrations) != 1 or hashlib.sha256(registrations[0].data).hexdigest() != pin['RESOURCE_SHA256']:
            raise ValueError('parent ROM packed plugin resource does not match pin')
    if set(files0) != set(files1):
        raise ValueError('ROM membership changed')
    count = 0
    for name in files0:
        if name.startswith('sys\\bin\\'):
            continue
        if ROM['file_data'](old, files0, name) != ROM['file_data'](new, files1, name):
            raise ValueError('resource bytes changed: ' + name)
        count += 1
    window = (len(new) + 1048575) // 1048576 * 1048576
    if window != 0x03a00000:
        raise ValueError('ROM/RAM boundary changed')
    result = dict(status=status, profile=a.profile, parent_sha256=parent_sha,
                  changed_binary=changed_binary, changed_sha256=sha(Path(changed_binary)),
                  unchanged_binaries=(64 if a.profile in ('viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 63 if a.profile in ('viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 62 if a.profile in ('gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 61 if a.profile in ('menu-launch', 'menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab') else 60), preserved_resources=count,
                  rom_window=window, ram_start=0x12200000 + window,
                  payload_sha256=sha(a.image), font_changes=False,
                  settings_worker=('unchanged791-native-registration-and-root-icon-confirmed' if a.profile in ('menu-action', 'menu-launch', 'menu-attribute', 'menu-request', 'menu-server-exit', 'menu-software-exception', 'menu-exception-stack', 'menu-notifier-stop', 'menu-task-lookup-control','menu-operation-completion','wserv-find-notfound','menu-task-enumeration','hsps-header-cache','menu-task-enumeration-804','gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab')
                                   else 'unchanged782-unproven-execution'),
                  home_priority_ab_evidence=home_priority_ab_evidence,
                  policy=('Home-priority-retention-one-byte-AB-on839-not-permanent-fix' if a.profile == 'home-priority-ab'
                          else 'existing-kernel-sampler-known-newborn-Home-main-on838-no-target-mutation' if a.profile == 'home-kernel-watch'
                          else 'UI-native-session-deactivation-delivery-ack-observation-on837' if a.profile == 'vws-session-deactivation'
                          else 'UI-native-ViewServer-activation-ack-timeout-event-observation-on836' if a.profile == 'vws-server-event'
                          else 'unmodified-native-ViewServer-source-control-on835-no-new-log-or-timeout-change' if a.profile == 'viewsrv-control'
                          else 'Home-GS-sync-result-and-create-handler-state-on834' if a.profile == 'vws-client-state'
                          else 'Home-GS-native-VWS-request-RunL-rearm-cancel-on833' if a.profile == 'vws-client-queue'
                          else 'unmodified-native-ViewCLI-source-GCCE-control-on832-no-new-log' if a.profile == 'viewcli-control'
                          else 'Home-plus-GS-native-view-events-and-deactivation-on831' if a.profile == 'home-view-event'
                          else 'GS-only-CONE-registration-inbound-event-native-dispatch-on830' if a.profile == 'gsapp-cone-event'
                          else 'GS-enqueue-and-existing-native-view-transition-observation-on829' if a.profile == 'gsapp-transition'
                          else 'GS-root-native-async-view-event-on828-no-sync-activation-completion-wait' if a.profile == 'gsapp-async'
                          else 'GS-first8-list-events-native-view-activation-on827-no-policy-change' if a.profile == 'gsapp-list'
                          else 'GS-General-child-first2-observation-no-loading-policy-change-on826' if a.profile == 'gsapp-child'
                          else 'GS-create-minus15-one-native-reconnect-no-empty-fallback-on825' if a.profile == 'gsapp-create'
                          else 'GS-negative-ECom-notify-retired-no-requery-rearm-on824' if a.profile == 'gsapp-notify'
                          else 'GS-terminal-exception-stack-witness-on823-native-panic-retained' if a.profile == 'gsapp-exception'
                          else 'GS-native-lifetime-in-existing-Home-clock-padding-on822' if a.profile == 'gsapp-lifetime'
                          else 'GS-first-redraw-and-native-panic-witness-on821' if a.profile == 'gsapp-redraw'
                          else 'GS-root-native-plugin-first2-rounds-on820-no-policy-change' if a.profile == 'gsapp-plugin'
                          else 'GSApp-no-active-view-activation-transaction-on819' if a.profile == 'gsapp-activation'
                          else 'GSApp-zero-session-keyblock-IPC-skip-on818' if a.profile == 'gsapp-keyblock'
                          else 'GSApp-first-FocusGained-logonly-on817-no-Home-policy-change' if a.profile == 'gsapp-focus'
                          else 'gsapp-own-first8-events-and-first-view-activation-on816' if a.profile == 'gsapp-view'
                          else 'gsapp-zero-handle-real-local-fade-first-getter-on815' if a.profile == 'gsapp-sgc-fade'
                          else 'gsapp-native-statuspane-constructor-frontier-on814' if a.profile == 'gsapp-statuspane'
                          else 'gsapp-native-appinfo-resource-furniture-frontier-on813' if a.profile == 'gsapp-appinfo'
                          else 'gsapp-existing-eikon-base-constructor-frontier-on812' if a.profile == 'gsapp-eikbase'
                          else 'gsapp-nullhandle-local-params-firstchange64-on811' if a.profile == 'gsapp-sgc-params'
                          else 'gsapp-only-appui-constructor-frontier-on810-sgc-retained' if a.profile == 'gsapp-appui'
                          else 'gsapp-only-nullhandle-missing-server-native-local-layout-on809' if a.profile == 'gsapp-sgc-local'
                          else 'gsapp-SID-only-existing-aknenv-frontier-on808-no-recovery-change' if a.profile == 'gsapp-aknenv'
                          else 'gsapp-SID-only-existing-environment-frontier-on807' if a.profile == 'gsapp-env'
                          else 'gsapp-local-native-eikstart-on806-no-error-bypass' if a.profile == 'gsapp-eikstart'
                          else 'gsapp-native-startup-observer-on805-no-UI-policy-change' if a.profile in ('gsapp-startup','gsapp-eikstart','gsapp-env','gsapp-aknenv','gsapp-sgc-local','gsapp-appui','gsapp-sgc-params','gsapp-eikbase','gsapp-appinfo','gsapp-statuspane','gsapp-sgc-fade','gsapp-view','gsapp-focus','gsapp-keyblock','gsapp-activation','gsapp-plugin','gsapp-redraw','gsapp-lifetime','gsapp-exception','gsapp-notify','gsapp-create','gsapp-child','gsapp-list','gsapp-async','gsapp-transition','gsapp-cone-event','home-view-event','viewcli-control','vws-client-queue','vws-client-state','viewsrv-control','vws-server-event','vws-session-deactivation','home-kernel-watch','home-priority-ab')
                          else 'native-root-window-enumeration-on-recovered804-hsps-guard-retained' if a.profile == 'menu-task-enumeration-804'
                          else 'hsps-native-header-load-leave-safe-pending-on801-first12' if hsps_patch
                          else 'finite-root-window-name-enumeration-on801-exact-wserv-recovery' if enumeration_patch
                          else 'matrix-final-name-query-native-notfound-no-new-log' if wserv_patch
                          else 'watcher-real-error-callback-nonresource-cleanup-recovery-control' if completion_patch
                          else 'single-plugin-bounded-lookup-error-completion-control-on-frozen799' if lookup_patch
                          else 'mcs-owned-notifier-minus15-stop-no-requeue' if notifier_patch
                          else 'mcs-terminal-bounded-stack-restores-reraises' if stack_observer
                          else 'mcs-terminal-exception-observer-restores-reraises' if a.profile == 'menu-software-exception'
                          else 'matrix-zero-session-local-fade-get-set' if a.profile == 'matrix-fade'
                          else a.profile + '-original-dispatch'), hardware_result='pending')
    if keyblock_evidence:
        result['gsapp_keyblock'] = keyblock_evidence
    if fade_evidence:
        result['gsapp_sgc_fade'] = fade_evidence
    if params_evidence:
        result['gsapp_sgc_params'] = params_evidence
        result['shared_import_relocations'] = shared_relocations
    if focus_evidence:
        result['gsapp_focus'] = focus_evidence
    if home_watch_evidence:
        result['home_kernel_watch'] = home_watch_evidence
        result['shared_import_relocations'] = shared_relocations
    if vws_session_evidence:
        result['vws_session_deactivation'] = vws_session_evidence
        result['shared_import_relocations'] = shared_relocations
    if vws_event_evidence:
        result['vws_server_event'] = vws_event_evidence
        result['shared_import_relocations'] = shared_relocations
    if viewsrv_evidence:
        result['viewsrv_source_control'] = viewsrv_evidence
        result['shared_import_relocations'] = shared_relocations
    if vws_state_evidence:
        result['vws_client_state'] = vws_state_evidence
        result['shared_import_relocations'] = shared_relocations
    if vws_queue_evidence:
        result['vws_client_queue'] = vws_queue_evidence
        result['shared_import_relocations'] = shared_relocations
    if viewcli_evidence:
        result['viewcli_source_control'] = viewcli_evidence
        result['shared_import_relocations'] = shared_relocations
    if home_event_evidence:
        result['home_view_event'] = home_event_evidence
        result['shared_import_relocations'] = shared_relocations
    if cone_event_evidence:
        result['gsapp_cone_event'] = cone_event_evidence
        result['shared_import_relocations'] = shared_relocations
    if transition_evidence:
        result['gsapp_transition'] = transition_evidence
        result['shared_import_relocations'] = shared_relocations
    if async_evidence:
        result['gsapp_async'] = async_evidence
        result['shared_import_relocations'] = shared_relocations
    if list_evidence:
        result['gsapp_list'] = list_evidence
        result['shared_import_relocations'] = shared_relocations
    if child_evidence:
        result['gsapp_child'] = child_evidence
        result['shared_import_relocations'] = shared_relocations
    if create_evidence:
        result['gsapp_create_retry'] = create_evidence
        result['shared_import_relocations'] = shared_relocations
    if notify_evidence:
        result['gsapp_notify'] = notify_evidence
        result['shared_import_relocations'] = shared_relocations
    if exception_evidence:
        result['gsapp_exception'] = exception_evidence
        result['shared_import_relocations'] = shared_relocations
    if lifetime_evidence:
        result['gsapp_lifetime'] = lifetime_evidence
        result['shared_import_relocations'] = shared_relocations
    if redraw_evidence:
        result['gsapp_redraw'] = redraw_evidence
        result['shared_import_relocations'] = shared_relocations
    if plugin_evidence:
        result['gsapp_plugin'] = plugin_evidence
    if activation_evidence:
        result['gsapp_activation'] = activation_evidence
    if appui_evidence:
        result['gsapp_appui'] = appui_evidence
        result['shared_import_relocations'] = shared_relocations
    if sgc_evidence:
        result['gsapp_sgc'] = sgc_evidence
        result['shared_import_relocations'] = shared_relocations
    if aknenv_evidence:
        result['gsapp_aknenv'] = aknenv_evidence
        result['shared_import_relocations'] = shared_relocations
    if statuspane_evidence:
        result['gsapp_statuspane'] = statuspane_evidence
    if appinfo_evidence:
        result['gsapp_appinfo'] = appinfo_evidence
        result['shared_import_relocations'] = shared_relocations
    if eikbase_evidence:
        result['gsapp_eikbase'] = eikbase_evidence
        result['shared_import_relocations'] = shared_relocations
    if env_evidence:
        result['gsapp_env'] = env_evidence
        result['shared_import_relocations'] = shared_relocations
    if view_evidence:
        result['gsapp_view'] = view_evidence
    if gsapp_evidence:
        result['gsapp_observer'] = gsapp_evidence
    if stack_entry:
        result['stack_entry_verification'] = stack_entry
    if enumeration_imports:
        result['enumeration_import_contract'] = enumeration_imports
        result['restored_wserv_sha256'] = restored['CONTROL_SHA']
    if hsps_patch:
        result['restored_wserv_sha256'] = restored['CONTROL_SHA']
        result['hsps_header_cache_trace'] = 'first12-48581320-22-no-cleanup-io'
    if wserv_evidence:
        result['wserv_derivation'] = wserv_evidence
        result['shared_import_relocations'] = shared_relocations
    a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
