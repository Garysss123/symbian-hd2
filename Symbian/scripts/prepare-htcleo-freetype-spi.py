#!/usr/bin/env python3
"""864: retire only the absent iType rasterizer registration that shadows FreeType."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

SPI_SHA='4b61811287c80ddd4ea4a66b5c41adcb635e10274680b365245f2782c9787df7'
ITYPE_SHA='5121d4e729d610ee04530b941ec6dd343f70b37372b8ce22329f7f8b3b2efec1'
FREETYPE_SHA='edcd3a08e65255a7fc12dba56257b793b0660f7bf0ed57c6ec7ea18da35302b6'
POLICY='remove-only-absent-ityperast-duplicate100012a7-101f7f5d-101f7f5e-keep-real-freetype-140-spi-entries'
OLD_SOURCE='/root/symbian3-full-work/htcleo-native/ecom-spi/ecom-0-0.spi'
NEW_SOURCE='/root/symbian3-full-work/htcleo-native/ecom-spi/no-itype-864/ecom-0-0.spi'
sha=lambda data:hashlib.sha256(data).hexdigest()


def parse(raw):
    if len(raw)<32 or struct.unpack_from('<III',raw)!=(0x10205c2b,0x10205c2c,0) or any(raw[16:32]):
        raise ValueError('invalid ECom SPI header')
    pos=32;entries=[];names=set()
    while pos<len(raw):
        if pos+8>len(raw):raise ValueError('short SPI record')
        n,size=struct.unpack_from('<II',raw,pos)
        end=pos+8+n+size;aligned=end+(-(n+size)%4)
        if not 0<n<=255 or aligned>len(raw):raise ValueError('invalid SPI record bounds')
        name=raw[pos+8:pos+8+n].decode('ascii').lower()
        if any(c in name for c in '\x00\\/') or name in names:raise ValueError('invalid/duplicate SPI name')
        if any(raw[end:aligned]):raise ValueError('nonzero SPI padding')
        entries.append(dict(name=name,start=pos,end=aligned,data=raw[pos+8+n:end],record=raw[pos:aligned]))
        names.add(name);pos=aligned
    return entries


def known_registration(entry,expected_sha):
    data=entry['data']
    if sha(data)!=expected_sha:raise ValueError('rasterizer registration drift '+entry['name'])
    # These two pinned, native version1 resource payloads have the same header.
    # Do not pretend this offset check is a general RSC decompressor.
    fields=tuple(struct.unpack_from('<I',data,p)[0] for p in (22,28,34))+(data[38],)
    if fields!=(0x100012a7,0x101f7f5d,0x101f7f5e,1):raise ValueError('rasterizer identity/version drift')
    return fields


def transform(raw):
    if sha(raw)!=SPI_SHA:raise ValueError('864 requires exact863 SPI; no broad registry cleanup')
    entries=parse(raw)
    if len(entries)!=141:raise ValueError('unexpected863 SPI entry count')
    by_name={x['name']:x for x in entries}
    stale=by_name['ityperast'];real=by_name['freetype']
    known_registration(stale,ITYPE_SHA);known_registration(real,FREETYPE_SHA)
    if (stale['start'],stale['end']-stale['start'])!=(11728,308):raise ValueError('stale entry moved')
    new=raw[:stale['start']]+raw[stale['end']:]
    expected=[x for x in entries if x['name']!='ityperast'];actual=parse(new)
    if len(actual)!=140 or [(x['name'],x['record']) for x in actual]!=[(x['name'],x['record']) for x in expected]:
        raise ValueError('864 changed more than the single stale entry')
    uid=struct.pack('<I',0x101f7f5e)
    if [x['name'] for x in actual if uid in x['data']]!=['freetype']:
        raise ValueError('font implementation still has a duplicate SPI registration')
    return new,dict(status='HTCLEO_FREETYPE_SPI_FILTER_OK',policy=POLICY,
        source_sha256=SPI_SHA,source_bytes=len(raw),source_entries=141,
        result_sha256=sha(new),result_bytes=len(new),result_entries=140,
        removed_name='ityperast',removed_record_bytes=308,removed_resource_sha256=ITYPE_SHA,
        retained_freetype_resource_sha256=FREETYPE_SHA,remaining_entry_bytes_identical=True,
        dll_uid='100012a7',interface_uid='101f7f5d',implementation_uid='101f7f5e',version=1)


def audit_text(info):
    return '\n'.join([
        'STATUS=HTCLEO_HOMESCREEN_ECOM_SPI_OK', 'BASE_ENTRIES=108', 'APPENDED_ENTRIES=33',
        'RETIRED_ENTRIES=1', 'RETIRED_NAME=ityperast', 'EXTENDED_ENTRIES=140',
        'STOCK_ENTRIES_BYTE_IDENTICAL=0', 'RETAINED_ENTRY_BYTES_IDENTICAL=1',
        'APPENDED_PAYLOADS_BYTE_IDENTICAL=1', 'FREETYPE_IMPLEMENTATION_UNIQUE=1',
        'PREFILTER_SHA256='+info['source_sha256'], 'EXTENDED_SHA256='+info['result_sha256'],
    ])+'\n'


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--audit',type=Path,required=True);a=p.parse_args()
    if a.input.resolve()==a.output.resolve():raise ValueError('do not overwrite the original SPI')
    data,info=transform(a.input.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(data)
    a.report.write_text(json.dumps(info,indent=2)+'\n');a.audit.write_text(audit_text(info))
    print(json.dumps(info,sort_keys=True))
