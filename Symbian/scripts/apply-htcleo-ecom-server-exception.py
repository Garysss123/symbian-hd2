#!/usr/bin/env python3
"""859: server entry exception witness and request RAM checkpoints only."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame')
BASE={'EComServerStart.cpp':'846c9692e348b5941d22f90d898a1cf51994fb2567975cc29eb90d9c84fe3178',
      'EComServerSession.cpp':'baae7aa23760b245b1e174beac09eeef6f3e5ec79cf507614026cf9e5780a4fb'}
INC='#include "HtcleoEcomServerLog.h"\n'
EDITS={
'EComServerStart.cpp':[
    (INC,INC+'#include "htcleoecserverexception.inl"\n'),
    ('\t\tTRAP(err,RunServerL());','\t\t(void)HtcleoEcInstallExceptionObserver();\n\t\tTRAP(err,RunServerL());')],
'EComServerSession.cpp':[
    (INC,INC+'#include "htcleoecservertrace.h"\n'),
    ('\tHtcleoEcomServerDisarm();','\tHtcleoEcTraceBegin(aMessage.Function());\n\tHtcleoEcomServerDisarm();'),
    ('\tconst TClientRequest msg(aMessage);','\tconst TClientRequest msg(aMessage);\n\tHtcleoEcTraceMark(2, 0);'),
    ('\tServiceL(msg);','\tServiceL(msg);\n\tHtcleoEcTraceMark(0xffu, 0);')]}
LIST_EDITS=[
    ('\taMessage.ReadL(KIPCParameterUids, uidsPkg);','\taMessage.ReadL(KIPCParameterUids, uidsPkg);\n\tHtcleoEcTraceIdentity((TUint32)uids[KInterfaceUidIndex].iUid, (TUint32)uids[KResolverUidIndex].iUid);'),
    ('\taMessage.ReadL(2,listParamPkg);','\taMessage.ReadL(2,listParamPkg);\n\tHtcleoEcTraceMark(4, 0);'),
    ('\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);','\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);\n\tHtcleoEcTraceMark(5, 0);'),
    ('\tswitch(iListContext)','\tHtcleoEcTraceMark(6, 0);\n\tswitch(iListContext)'),
    ('\t//Now cleanup the extended interface','\tHtcleoEcTraceMark(7, (TUint32)iList);\n\t//Now cleanup the extended interface'),
    ('\t\t\t\t(*iList)[i]->ExternalizeL(ETrue,writeStream);','\t\t\t\tHtcleoEcTraceMark(8, (TUint32)i);\n\t\t\t\t(*iList)[i]->ExternalizeL(ETrue,writeStream);\n\t\t\t\tHtcleoEcTraceMark(9, (TUint32)i);'),
    ('\t\t\tbufferSizeRequired=iMemoryStore->Size();','\t\t\tbufferSizeRequired=iMemoryStore->Size();\n\t\t\tHtcleoEcTraceMark(10, (TUint32)bufferSizeRequired);')]
POLICY='ECom-main-terminal-ECX1-init-plus-fault-1m-RAM-request10-no-normal-filelog-preserve-panic'

def once(t,a,b):
    if t.count(a)!=1:raise ValueError('859 anchor drift '+repr(a[:90]))
    return t.replace(a,b,1)

def list_transform(t,restore):
    start=t.index('void CEComServerSession::DoListImplementationsL(')
    end=t.index('void CEComServerSession::DoGetResolvedImplementationL(',start)
    block=t[start:end]
    for a,b in reversed(LIST_EDITS) if restore else LIST_EDITS:block=once(block,b,a) if restore else once(block,a,b)
    return t[:start]+block+t[end:]

def transform(name,text,restore=False):
    active='htcleoecserver' in text
    if active:
        if name=='EComServerSession.cpp':text=list_transform(text,True)
        for a,b in reversed(EDITS[name]):text=once(text,b,a)
    if hashlib.sha256(text.encode()).hexdigest()!=BASE[name]:raise ValueError('859 not exact858 server source '+name)
    if not restore:
        for a,b in EDITS[name]:text=once(text,a,b)
        if name=='EComServerSession.cpp':text=list_transform(text,False)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    for name in BASE:
        path=a.root/ROOT/name;old=path.read_text();new=transform(name,old,a.restore)
        if transform(name,new,True)!=transform(name,old,True):raise ValueError('859 inverse failed')
        if old!=new:path.write_text(new)
    if not a.restore:
        for name in ('htcleoecservertrace.h','htcleoecserverexception.inl'):
            (a.root/ROOT/name).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/name).read_bytes())
    print('HTCLEO_ECOM_SERVER_EXCEPTION='+('restored' if a.restore else POLICY))
if __name__=='__main__':main()
