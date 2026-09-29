#!/usr/bin/env python3
"""783: trace real CAknGrid pointer dispatch only; no new hit testing or bypass."""
import argparse
from pathlib import Path

INC = '#include "htcleomatrixpointertrace.inl"\n'
START = 'EXPORT_C void CAknGrid::HandlePointerEventL('
END = 'EXPORT_C void* CAknGrid::ExtensionInterface('
MARKER = 'HTCLEO_MATRIX_POINTER_FRONTIER_V1'
PATCHES = (
    ('    _AKNTRACE_FUNC_ENTER;\n    if ( AknLayoutUtils::PenEnabled() )',
     '    _AKNTRACE_FUNC_ENTER;\n'
     '    // HTCLEO_MATRIX_POINTER_FRONTIER_V1\n'
     '    const TBool htcleoTrace = HtcleoMatrixPointerTraceEnabled(aPointerEvent);\n'
     '    HtcleoMatrixPointerLog(htcleoTrace, 0x1900u, aPointerEvent, 0u);\n'
     '    const TBool htcleoPen = AknLayoutUtils::PenEnabled();\n'
     '    HtcleoMatrixPointerLog(htcleoTrace, 0x1901u, aPointerEvent, htcleoPen);\n'
     '    if ( htcleoPen )'),
    ('        // Scroll bar\n',
     '        HtcleoMatrixPointerLog(htcleoTrace, 0x1910u, aPointerEvent, iSBFrame ? 1u : 0u);\n'
     '        // Scroll bar\n'),
    ('            if ( !ScrollingDisabled()\n',
     '            HtcleoMatrixPointerLog(htcleoTrace, 0x1911u, aPointerEvent, 1u);\n'
     '            if ( !ScrollingDisabled()\n'),
    ('                CEikListBox::HandlePointerEventL( aPointerEvent );',
     '                HtcleoMatrixPointerLog(htcleoTrace, 0x1920u, aPointerEvent, 1u);\n'
     '                CEikListBox::HandlePointerEventL( aPointerEvent );\n'
     '                HtcleoMatrixPointerLog(htcleoTrace, 0x1921u, aPointerEvent, 1u);'),
    ('                CCoeControl::HandlePointerEventL( aPointerEvent );',
     '                HtcleoMatrixPointerLog(htcleoTrace, 0x1922u, aPointerEvent, 1u);\n'
     '                CCoeControl::HandlePointerEventL( aPointerEvent );\n'
     '                HtcleoMatrixPointerLog(htcleoTrace, 0x1923u, aPointerEvent, 1u);'),
    ('            CAknGridView* gridView = GridView();',
     '            HtcleoMatrixPointerLog(htcleoTrace, 0x1912u, aPointerEvent, 0u);\n'
     '            CAknGridView* gridView = GridView();'),
    ('                gridView->ItemSize(itemIndex).iHeight * iNumOfRowsInView));',
     '                gridView->ItemSize(itemIndex).iHeight * iNumOfRowsInView));\n'
     '            HtcleoMatrixPointerLog(htcleoTrace, 0x1913u, aPointerEvent,\n'
     '                ((TUint)(visibleItemsRect.Width() & 0xffff) << 16) |\n'
     '                (TUint)(visibleItemsRect.Height() & 0xffff));'),
    ('            CEikListBox::HandlePointerEventL( aPointerEvent ); // eventually will call CAknGrid::HandleDragEventL if dragged',
     '            HtcleoMatrixPointerLog(htcleoTrace, 0x1920u, aPointerEvent, 0u);\n'
     '            CEikListBox::HandlePointerEventL( aPointerEvent ); // eventually will call CAknGrid::HandleDragEventL if dragged\n'
     '            HtcleoMatrixPointerLog(htcleoTrace, 0x1921u, aPointerEvent, 0u);'),
    ('    _AKNTRACE_FUNC_EXIT;\n    }',
     '    HtcleoMatrixPointerLog(htcleoTrace, 0x193fu, aPointerEvent, 0u);\n'
     '    _AKNTRACE_FUNC_EXIT;\n    }'),
)


def method_span(source):
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('grid method bounds changed')
    start, end = source.index(START), source.index(END)
    if end <= start:
        raise ValueError('grid method order changed')
    return start, end


def transform(source, restore=False):
    start, end = method_span(source)
    body = source[start:end]
    if MARKER in body:
        if body.count(MARKER) != 1 or source.count(INC) != 1:
            raise ValueError('partial pointer frontier')
        for old, new in reversed(PATCHES):
            if body.count(new) != 1:
                raise ValueError('pointer frontier cannot restore: ' + old[:60])
            body = body.replace(new, old, 1)
        source = (source[:start] + body + source[end:]).replace(INC, '', 1)
    elif INC in source or MARKER in source:
        raise ValueError('partial pointer frontier')
    if not restore:
        start, end = method_span(source)
        body = source[start:end]
        for old, new in PATCHES:
            if body.count(old) != 1:
                raise ValueError('grid anchor changed: ' + old[:60])
            body = body.replace(old, new, 1)
        source = source[:start] + body + source[end:]
        anchor = '#include "akntrace.h"\n'
        if source.count(anchor) != 1:
            raise ValueError('include anchor changed')
        source = source.replace(anchor, anchor + INC, 1)
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / 'sf/mw/classicui/uifw/AvKon/src/akngrid.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, a.restore)
    if not a.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('frontier is not exactly reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomatrixpointertrace.inl').read_text()
        for forbidden in ('Flush(', 'Replace(', 'SetPriority', 'SetOrdinal', 'RTimer', 'SendEvent', 'static TInt', 'Dll::SetTls'):
            if forbidden in body:
                raise ValueError('out-of-scope observer: ' + forbidden)
        (path.parent / 'htcleomatrixpointertrace.inl').write_text(body)
    if new != old:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_MATRIX_POINTER_FRONTIER=' + ('restored' if a.restore else 'matrix-down-up-first32-no-flush-original-dispatch'))


if __name__ == '__main__':
    main()
