#!/usr/bin/env python3
"""784: bounded release witnesses in the original ListBox paths, no bypasses."""
import argparse
from pathlib import Path

INC = '#include "htcleomatrixreleasetrace.inl"\n'
MARKER = 'HTCLEO_MATRIX_LIST_RELEASE_V1'
MAIN_START = 'EXPORT_C void CEikListBox::HandlePointerEventL('
MAIN_END = 'EXPORT_C void CEikListBox::SimulateArrowKeyEventL('
UP_START = '        case TPointerEvent::EButton1Up:\n'
UP_END = '        case TPointerEvent::EDrag:\n'


def log(stage, value='0u', detail='0u', indent='    '):
    return f'{indent}HtcleoMatrixReleaseLog(htcleoReleaseTrace, 0x{stage:04x}u, {value}, {detail});\n'


MAIN_EDITS = (
    ('    _AKNTRACE_FUNC_ENTER;\n',
     '    _AKNTRACE_FUNC_ENTER;\n    // HTCLEO_MATRIX_LIST_RELEASE_V1\n'
     '    const TBool htcleoReleaseTrace = HtcleoMatrixReleaseEnabled(aPointerEvent);\n' +
     log(0x2000, '(TUint)aPointerEvent.iPosition.iX', '(TUint)aPointerEvent.iPosition.iY')),
    ("    CheckCreateBufferL(); // don't need to create the full matching buffer here - only the iPressedIndex\n",
     "    CheckCreateBufferL(); // don't need to create the full matching buffer here - only the iPressedIndex\n" + log(0x2001)),
    ('    TBool pointerIsOverAnItem = iView->XYPosToItemIndex(pointerPos, itemIndex);\n',
     '    TBool pointerIsOverAnItem = iView->XYPosToItemIndex(pointerPos, itemIndex);\n' + log(0x2002, '(TUint)itemIndex', 'pointerIsOverAnItem')),
    ('    TBool listEmpty = !ItemExists( iView->TopItemIndex() );\n',
     '    TBool listEmpty = !ItemExists( iView->TopItemIndex() );\n' + log(0x2003, 'listEmpty', '(TUint)iListBoxFlags')),
    ('    TBool wasFlicking = EFalse;\n',
     '    TBool wasFlicking = EFalse;\n' + log(0x2010, 'hasPhysics', 'iListBoxExt->iSingleClickEnabled ? 1u : 0u')),
    ('        if ( HandlePhysicsPointerEventL( aPointerEvent ) )\n',
     log(0x2020, indent='        ') +
     '        const TBool htcleoPhysicsConsumed = HandlePhysicsPointerEventL( aPointerEvent );\n' +
     log(0x2021, 'htcleoPhysicsConsumed', indent='        ') +
     '        if ( htcleoPhysicsConsumed )\n'),
)
UP_EDITS = (
    ('            _AKNTRACE("TPointerEvent::EButton1Up");\n',
     '            _AKNTRACE("TPointerEvent::EButton1Up");\n' + log(0x2100, '(TUint)itemIndex', '(TUint)iListBoxFlags', '            ')),
    ('            if ((! (Rect().Contains(aPointerEvent.iPosition))) && (iListBoxFlags & EPopout))',
     log(0x2101, indent='            ') +
     '            if ((! (Rect().Contains(aPointerEvent.iPosition))) && (iListBoxFlags & EPopout))'),
    ('                    ReportEventL(MCoeControlObserver::EEventStateChanged);\n                    UpdateMarkUnmarkMSKL();',
     log(0x2110, indent='                    ') +
     '                    ReportEventL(MCoeControlObserver::EEventStateChanged);\n' +
     log(0x2111, indent='                    ') +
     '                    UpdateMarkUnmarkMSKL();\n' + log(0x2112, indent='                    ').rstrip('\n')),
    ('                    iListBoxExt->LongTapPointerEventL( aPointerEvent );',
     log(0x2120, indent='                    ') +
     '                    iListBoxExt->LongTapPointerEventL( aPointerEvent );\n' + log(0x2121, indent='                    ').rstrip('\n')),
    ('                        iListBoxExt->EnableHighlight( EFalse );\n                        UpdateHighlightL( itemIndex );\n                        ReportListBoxEventL( \n                            MEikListBoxObserver::EEventItemSingleClicked );\n                        _AKNTRACE_FUNC_EXIT;',
     log(0x2130, '(TUint)itemIndex', indent='                        ') +
     '                        iListBoxExt->EnableHighlight( EFalse );\n' + log(0x2131, '(TUint)itemIndex', indent='                        ') +
     '                        UpdateHighlightL( itemIndex );\n' + log(0x2132, '(TUint)itemIndex', indent='                        ') +
     '                        ReportListBoxEventL( \n                            MEikListBoxObserver::EEventItemSingleClicked );\n' +
     log(0x2133, '(TUint)itemIndex', indent='                        ') + '                        _AKNTRACE_FUNC_EXIT;'),
)
PHYS_EDITS = (
    ('    _AKNTRACE_FUNC_ENTER;\n',
     '    _AKNTRACE_FUNC_ENTER;\n    const TBool htcleoReleaseTrace = HtcleoMatrixReleaseEnabled(aPointerEvent);\n' + log(0x2200)),
    ('            if ( iListBoxExt->HighlightTimerActive() )\n',
     log(0x2201, indent='            ') + '            if ( iListBoxExt->HighlightTimerActive() )\n'),
    ('                iListBoxExt->iHighlightTimer->Cancel();\n                CListBoxExt::HighlightTimerCallback( iListBoxExt );',
     log(0x2202, indent='                ') + '                iListBoxExt->iHighlightTimer->Cancel();\n' +
     log(0x2203, indent='                ') + '                CListBoxExt::HighlightTimerCallback( iListBoxExt );\n' + log(0x2204, indent='                ').rstrip('\n')),
    ('            iListBoxExt->LongTapPointerEventL( aPointerEvent );',
     log(0x2210, indent='            ') + '            iListBoxExt->LongTapPointerEventL( aPointerEvent );\n' + log(0x2211, indent='            ').rstrip('\n')),
    ('            if (  allowDragEvent &&\n',
     log(0x2220, 'allowDragEvent', indent='            ') + '            if (  allowDragEvent &&\n'),
    ('                iListBoxExt->CancelLongTapL();\n\n                if ( !iListBoxExt->iScrolling )',
     log(0x2221, '1u', indent='                ') + '                iListBoxExt->CancelLongTapL();\n\n                if ( !iListBoxExt->iScrolling )'),
    ('            else\n                {\n                iListBoxExt->iScrolling = EFalse;\n                }\n\n            if ( iListBoxExt->iSingleClickEnabled',
     '            else\n                {\n' + log(0x2221, '0u', indent='                ') +
     '                iListBoxExt->iScrolling = EFalse;\n                }\n\n            if ( iListBoxExt->iSingleClickEnabled'),
    ('    return blockEvent;\n', log(0x222f, 'blockEvent') + '    return blockEvent;\n'),
)
FEEDBACK_EDITS = (
    ('    _AKNTRACE_FUNC_ENTER;\n',
     '    _AKNTRACE_FUNC_ENTER;\n    const TBool htcleoReleaseTrace = HtcleoMatrixReleaseEnabled(aPointerEvent);\n' + log(0x2300, 'iFeedback ? 1u : 0u', '(TUint)aFeedbackType')),
    ('        iFeedback->InstantFeedback( &iListBox, aFeedback, aFeedbackType, aPointerEvent );',
     log(0x2301, indent='        ') + '        iFeedback->InstantFeedback( &iListBox, aFeedback, aFeedbackType, aPointerEvent );\n' + log(0x2302, indent='        ').rstrip('\n')),
)
LONG_EDITS = (
    ('    if ( iSingleClickEnabled && iLongTapDetector && iItemActionMenu  )',
     '    const TBool htcleoReleaseTrace = HtcleoMatrixReleaseEnabled(aPointerEvent);\n' +
     log(0x2400, 'iSingleClickEnabled', '(iLongTapDetector ? 1u : 0u) | (iItemActionMenu ? 2u : 0u)') +
     '    if ( iSingleClickEnabled && iLongTapDetector && iItemActionMenu  )'),
    ('            iLongTapDetector->PointerEventL ( aPointerEvent );',
     log(0x2401, indent='            ') + '            iLongTapDetector->PointerEventL ( aPointerEvent );\n' + log(0x2402, indent='            ').rstrip('\n')),
)
SCOPES = (
    ('void CListBoxExt::LongTapPointerEventL(', 'void CListBoxExt::CancelLongTapL()', LONG_EDITS),
    ('void CListBoxExt::ImmediateFeedback(', 'TBool CListBoxExt::FeedbackEnabledOnUpEvent()', FEEDBACK_EDITS),
    (MAIN_START, MAIN_END, MAIN_EDITS),
    ('TBool CEikListBox::HandlePhysicsPointerEventL(', 'void CEikListBox::UpdateHighlightL(', PHYS_EDITS),
)


def edit(text, pairs, restore):
    for old, new in reversed(pairs) if restore else pairs:
        source, target = (new, old) if restore else (old, new)
        if text.count(source) != 1:
            raise ValueError('release anchor count changed: ' + source[:80])
        text = text.replace(source, target, 1)
    return text


def bounds(text, start, end):
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('release method boundaries changed')
    a, b = text.index(start), text.index(end)
    if b <= a:
        raise ValueError('release method order changed')
    return a, b


def patch_scopes(source, restore):
    for start, end, pairs in SCOPES:
        a, b = bounds(source, start, end)
        body = source[a:b]
        if start == MAIN_START and restore:
            c, d = bounds(body, UP_START, UP_END)
            body = body[:c] + edit(body[c:d], UP_EDITS, True) + body[d:]
        body = edit(body, pairs, restore)
        if start == MAIN_START and not restore:
            c, d = bounds(body, UP_START, UP_END)
            body = body[:c] + edit(body[c:d], UP_EDITS, False) + body[d:]
        source = source[:a] + body + source[b:]
    return source


def transform(source, restore=False):
    if MARKER in source:
        if source.count(MARKER) != 1 or source.count(INC) != 1:
            raise ValueError('partial release witness')
        source = patch_scopes(source, True).replace(INC, '', 1)
    elif INC in source:
        raise ValueError('partial release witness')
    if not restore:
        source = patch_scopes(source, False)
        anchor = '#include "akntrace.h"\n'
        if source.count(anchor) != 1:
            raise ValueError('release include changed')
        source = source.replace(anchor, anchor + INC, 1)
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / 'sf/mw/classicui/uifw/EikStd/coctlsrc/EIKLBX.CPP'
    old = path.read_text(encoding='latin-1')
    new = transform(old, a.restore)
    if not a.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('release trace is not reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomatrixreleasetrace.inl').read_text()
        for forbidden in ('Flush(', 'Replace(', 'SetPriority', 'RTimer', 'SetOrdinal', 'static TInt', 'Dll::SetTls'):
            if forbidden in body:
                raise ValueError('out-of-scope release observer: ' + forbidden)
        (path.parent / 'htcleomatrixreleasetrace.inl').write_text(body)
    if new != old:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_MATRIX_LIST_RELEASE=' + ('restored' if a.restore else 'matrix-up-only-first64-no-flush-original-behavior'))


if __name__ == '__main__':
    main()
