/* HTC Leo 3x3 matrix keypad and power key. */

#include <kernel/kern_priv.h>
#include <e32event.h>
#include <e32keys.h>
#include <e32hal.h>
#include "htcleo_qsd8k.h"
#include "htcleokeymatrix1015.inl"

namespace
    {
    const TUint32 KColumns[] = { 33u, 32u, 31u };
    const TUint32 KRows[] = { 42u, 41u, 40u };
    const TUint KPollTicks = 20u;

    const TUint8 KKeyCodes[9] =
        {
        EStdKeyIncVolume, EStdKeyDecVolume, EStdKeyNull,
        EStdKeyApplication0, EStdKeyDial, EStdKeyDevice2,
        EStdKeyF22, EStdKeyDevice0, EStdKeyNull
        };

    class DHtcleoKeys
        {
    public:
        DHtcleoKeys();
        TInt Create();
        static void Poll(TAny* aPtr);
        static TInt Hal(TAny* aPtr, TInt aFunction, TAny* a1, TAny* a2);
        TInt HalFunction(TInt aFunction, TAny* a1, TAny* a2);
    private:
        TUint32 Scan();
        void Update(TUint32 aSample);
        void Send(TInt aIndex, TRawEvent::TType aType);
    private:
        NTimer iTimer;
        TUint32 iRaw;
        TUint32 iStable;
        TBool iKeyboardOn;
        };

    DHtcleoKeys::DHtcleoKeys()
        : iTimer(Poll, this), iRaw(0), iStable(0), iKeyboardOn(ETrue)
        {
        }

    TInt DHtcleoKeys::Create()
        {
        for (TUint i = 0; i < 3; ++i)
            {
            TInt r = HtcleoTlmmConfigure(KColumns[i], 0u, ETrue,
                                         EHtcleoNoPull, 0u);
            if (!HtcleoKeyMuxResult1015(r))
                return r;
            r = HtcleoGpioDirection(KColumns[i], ETrue, ETrue);
            if (r != KErrNone)
                return r;
            r = HtcleoTlmmConfigure(KRows[i], 0u, EFalse,
                                    EHtcleoPullUp, 0u);
            if (!HtcleoKeyMuxResult1015(r))
                return r;
            r = HtcleoGpioDirection(KRows[i], EFalse, EFalse);
            if (r != KErrNone)
                return r;
            }
        TInt r = HtcleoTlmmConfigure(94u, 0u, EFalse,
                                     EHtcleoPullUp, 0u);
        if (!HtcleoKeyMuxResult1015(r))
            return r;
        r = HtcleoGpioDirection(94u, EFalse, EFalse);
        if (r != KErrNone)
            return r;
        (void)Kern::AddHalEntry(EHalGroupKeyboard, Hal, this);
        iTimer.OneShot(KPollTicks, ETrue);
        return KErrNone;
        }

    TUint32 DHtcleoKeys::Scan()
        {
        TUint32 result = 0;
        for (TUint column = 0; column < 3; ++column)
            {
            for (TUint i = 0; i < 3; ++i)
                (void)HtcleoGpioWrite(KColumns[i], ETrue);
            (void)HtcleoGpioWrite(KColumns[column], EFalse);
            Kern::NanoWait(40000u);
            for (TUint row = 0; row < 3; ++row)
                {
                TBool high = ETrue;
                if (HtcleoGpioRead(KRows[row], high) == KErrNone && !high)
                    result |= 1u << (column * 3u + row);
                }
            }
        for (TUint i = 0; i < 3; ++i)
            (void)HtcleoGpioWrite(KColumns[i], ETrue);

        TBool powerHigh = ETrue;
        if (HtcleoGpioRead(94u, powerHigh) == KErrNone && !powerHigh)
            result = HtcleoMergePower1015(result, ETrue);
        return result;
        }

    void DHtcleoKeys::Send(TInt aIndex, TRawEvent::TType aType)
        {
        const TUint key = KKeyCodes[aIndex];
        if (key == EStdKeyNull)
            return;
        TRawEvent event;
        event.Set(aType, key, 0);
        Kern::AddEvent(event);
        }

    void DHtcleoKeys::Update(TUint32 aSample)
        {
        /* A 20 ms repeated sample exceeds the board's 5 ms debounce rule. */
        if (aSample != iRaw)
            {
            iRaw = aSample;
            return;
            }
        const TUint32 changed = iStable ^ aSample;
        if (!changed)
            return;
        for (TInt i = 0; i < 9; ++i)
            if (changed & (1u << i))
                Send(i, (aSample & (1u << i)) ?
                     TRawEvent::EKeyDown : TRawEvent::EKeyUp);
        iStable = aSample;
        }

    void DHtcleoKeys::Poll(TAny* aPtr)
        {
        DHtcleoKeys* self = static_cast<DHtcleoKeys*>(aPtr);
        if (self->iKeyboardOn)
            self->Update(self->Scan());
        self->iTimer.Again(KPollTicks);
        }

    TInt DHtcleoKeys::Hal(TAny* aPtr, TInt aFunction, TAny* a1, TAny* a2)
        {
        return static_cast<DHtcleoKeys*>(aPtr)->HalFunction(aFunction, a1, a2);
        }

    TInt DHtcleoKeys::HalFunction(TInt aFunction, TAny* a1, TAny*)
        {
        switch (aFunction)
            {
            case EKeyboardHalKeyboardInfo:
                {
                TPckgBuf<TKeyboardInfoV01> info;
                info().iKeyboardType = EKeyboard_Keypad;
                info().iDeviceKeys = 2;
                info().iAppsKeys = 1;
                Kern::InfoCopy(*static_cast<TDes8*>(a1), info);
                return KErrNone;
                }
            case EKeyboardHalSetKeyboardState:
                iKeyboardOn = static_cast<TBool>(reinterpret_cast<TUint>(a1));
                return KErrNone;
            case EKeyboardHalKeyboardState:
                kumemput32(a1, &iKeyboardOn, sizeof(iKeyboardOn));
                return KErrNone;
            default:
                return KErrNotSupported;
            }
        }
    }

DECLARE_STANDARD_EXTENSION()
    {
    DHtcleoKeys* keys = new DHtcleoKeys;
    if (keys)
        {
        const TInt r = keys->Create();
        if (r == KErrNone)
            return KErrNone;
        delete keys;
        }
    /* Input is not an ESTART dependency.  Fail open so a missing modem TLMM
     * service can never regress the proven boot path. */
    return KErrNone;
    }
