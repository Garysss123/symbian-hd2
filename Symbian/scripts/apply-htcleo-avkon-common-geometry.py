#!/usr/bin/env python3
"""851: common EikCoCtl portrait layout boundary, no application whitelist."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/EikStd/coctlsrc')
HELPER='htcleoavkongeometry851.inl'
INC='#include "'+HELPER+'"\n'
BASE={
    'EIKCOLIB.CPP':'c9a209ad03f2e6d6782d0f56f032c90938771abf51d93edadc43a3925baed2ac',
    'eikspane.cpp':'45aa1e8df4e04cae09136150617a41d8f176369af448f3f1cc950b0538d21ba5',
    'eikcba.cpp':'d028331d9c3e1086420d7efab2a5547968d6285887f65c1e5277a293a8fa62a0',
}
CLIENT_OLD='''    const TUint32 htcleoGeometrySid = RProcess().SecureId().iId;
    if ( ( htcleoGeometrySid == 0x101F4CD2u ||
           htcleoGeometrySid == 0x102750F0u ) &&
         rect.iTl.iX >= 0 && rect.iTl.iY >= 0 &&
         rect.iBr.iX <= 360 && rect.iBr.iY <= 640 &&
         !rect.IsEmpty() )'''
CLIENT_NEW='''    // Fresh logical result after stock furniture/toolbar reductions.
    TRect htcleoPhysicalClient(rect);
    if ( HtcleoMapNominalRectToPanel(htcleoPhysicalClient,
            !Layout_Meta_Data::IsLandscapeOrientation()) )'''
CLIENT_SCALE='''        rect.iTl.iX = ( rect.iTl.iX * 480 + 180 ) / 360;
        rect.iBr.iX = ( rect.iBr.iX * 480 + 180 ) / 360;
        rect.iTl.iY = ( rect.iTl.iY * 800 + 320 ) / 640;
        rect.iBr.iY = ( rect.iBr.iY * 800 + 320 ) / 640;'''
PANE_OLD='''            const TUint32 htcleoPaneSid = RProcess().SecureId().iId;
            if ( ( htcleoPaneSid == 0x101F4CD2u ||
                   htcleoPaneSid == 0x102750F0u ) &&
                 htcleoPaneRect.iTl.iX >= 0 && htcleoPaneRect.iTl.iY >= 0 &&
                 htcleoPaneRect.iBr.iX <= 360 &&
                 htcleoPaneRect.iBr.iY <= 640 &&
                 !htcleoPaneRect.IsEmpty() )'''
PANE_NEW='''            TRect htcleoPhysicalPane(htcleoPaneRect);
            if ( HtcleoMapNominalRectToPanel(htcleoPhysicalPane,
                    !Layout_Meta_Data::IsLandscapeOrientation()) )'''
PANE_SCALE='''                htcleoPaneRect.iTl.iX =
                    ( htcleoPaneRect.iTl.iX * 480 + 180 ) / 360;
                htcleoPaneRect.iBr.iX =
                    ( htcleoPaneRect.iBr.iX * 480 + 180 ) / 360;
                htcleoPaneRect.iTl.iY =
                    ( htcleoPaneRect.iTl.iY * 800 + 320 ) / 640;
                htcleoPaneRect.iBr.iY =
                    ( htcleoPaneRect.iBr.iY * 800 + 320 ) / 640;'''
CBA_BOUND='''        const TUint32 htcleoCbaBoundingSid =
            RProcess().SecureId().iId;
        if ( ( htcleoCbaBoundingSid == 0x101F4CD2u ||
               htcleoCbaBoundingSid == 0x102750F0u ) &&
             htcleoCbaScreenRect.iTl.iX >= 0 &&
             htcleoCbaScreenRect.iTl.iY >= 0 &&
             htcleoCbaScreenRect.iBr.iX <= 360 &&
             htcleoCbaScreenRect.iBr.iY <= 640 &&
             !htcleoCbaScreenRect.IsEmpty() )
            {
            htcleoCbaScreenRect.iTl.iX =
                ( htcleoCbaScreenRect.iTl.iX * 480 + 180 ) / 360;
            htcleoCbaScreenRect.iBr.iX =
                ( htcleoCbaScreenRect.iBr.iX * 480 + 180 ) / 360;
            htcleoCbaScreenRect.iTl.iY =
                ( htcleoCbaScreenRect.iTl.iY * 800 + 320 ) / 640;
            htcleoCbaScreenRect.iBr.iY =
                ( htcleoCbaScreenRect.iBr.iY * 800 + 320 ) / 640;
            }'''
CBA_SIZE='''    const TUint32 htcleoCbaSizeSid = RProcess().SecureId().iId;
    if ( ( htcleoCbaSizeSid == 0x101F4CD2u ||
           htcleoCbaSizeSid == 0x102750F0u ) &&
         htcleoCbaScreenRect.iTl.iX >= 0 &&
         htcleoCbaScreenRect.iTl.iY >= 0 &&
         htcleoCbaScreenRect.iBr.iX <= 360 &&
         htcleoCbaScreenRect.iBr.iY <= 640 &&
         !htcleoCbaScreenRect.IsEmpty() )
        {
        htcleoCbaScreenRect.iTl.iX =
            ( htcleoCbaScreenRect.iTl.iX * 480 + 180 ) / 360;
        htcleoCbaScreenRect.iBr.iX =
            ( htcleoCbaScreenRect.iBr.iX * 480 + 180 ) / 360;
        htcleoCbaScreenRect.iTl.iY =
            ( htcleoCbaScreenRect.iTl.iY * 800 + 320 ) / 640;
        htcleoCbaScreenRect.iBr.iY =
            ( htcleoCbaScreenRect.iBr.iY * 800 + 320 ) / 640;
        }'''
REDUCE_OLD='''        // Cba in control pane.
        if ( aBoundingRect.Intersects( TRect( iPosition, iSize ) ) )
            {
            aBoundingRect.iBr.iY = Position().iY;
            }'''
REDUCE_NEW='''        // Cba in control pane: compare rectangles in the same domain.
        const TRect htcleoCbaForClient = HtcleoCbaInClientDomain(
            TRect(iPosition, iSize), aBoundingRect);
        if ( aBoundingRect.Intersects(htcleoCbaForClient) )
            {
            aBoundingRect.iBr.iY = htcleoCbaForClient.iTl.iY;
            }'''
EDITS={
 'EIKCOLIB.CPP':[(CLIENT_OLD,CLIENT_NEW),(CLIENT_SCALE,'        rect = htcleoPhysicalClient;')],
 'eikspane.cpp':[(PANE_OLD,PANE_NEW),(PANE_SCALE,'                htcleoPaneRect = htcleoPhysicalPane;')],
 'eikcba.cpp':[(CBA_BOUND,'        HtcleoMapNominalRectToPanel(htcleoCbaScreenRect,\n            !Layout_Meta_Data::IsLandscapeOrientation());'),
               (CBA_SIZE,'    HtcleoMapNominalRectToPanel(htcleoCbaScreenRect,\n        !Layout_Meta_Data::IsLandscapeOrientation());'),(REDUCE_OLD,REDUCE_NEW)],
}

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('851 geometry anchor drift '+repr(old[:85]))
    return text.replace(old,new,1)

def transform(text,name,restore=False):
    if INC in text:
        text=once(text,INC,'')
        for old,new in reversed(EDITS[name]):text=once(text,new,old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('851 requires exact850 '+name)
    if not restore:
        for old,new in EDITS[name]:text=once(text,old,new)
        text=INC+text
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    changes=[]
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('851 inverse failed '+name)
        changes.append((path,old,new))
    if not a.restore:
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    for path,old,new in changes:
        if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_AVKON_COMMON_GEOMETRY='+('restored' if a.restore else
          'portrait-client-status-cba-shared-360x640-to-480x800-logical-cba-reservation-no-app-whitelist'))

if __name__=='__main__':main()
