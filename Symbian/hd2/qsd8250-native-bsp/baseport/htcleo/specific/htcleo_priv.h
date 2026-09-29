/*
* Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
* All rights reserved.
* This component and the accompanying materials are made available
* under the terms of the License "Eclipse Public License v1.0"
* which accompanies this distribution, and is available
* at the URL "http://www.eclipse.org/legal/epl-v10.html".
*
* Initial Contributors:
* Nokia Corporation - initial contribution.
*
* Contributors:
*
* Description:
*
*/

#ifndef __HTCLEO_PRIV_H__
#define __HTCLEO_PRIV_H__

#include <e32const.h>
#include <arm.h>
#include <assp.h>
#include <htcleo.h>

#define	_LOCK		TInt irq=NKern::DisableAllInterrupts();
#define	_UNLOCK		NKern::RestoreInterrupts(irq);

const TUint32 K1000HzTickMatchLoad = KQsdGptMatch;
const TInt KNumHtcleoInts = 64;

class HtcleoInterrupt : public Interrupt
{
public:
	static void IrqDispatch();
	static void FiqDispatch();
	static void DisableAndClearAll();
	static void Init1();
	static void Init3();
	static void Spurious(TAny* anId);
    static void MsTimerTick(TAny* aPtr);

	static SInterruptHandler Handlers[KNumHtcleoInts];
};

class Htcleo : public Asic
{
public:
	IMPORT_C Htcleo();

public:
	// Initialisation
	IMPORT_C virtual TMachineStartupType StartupReason();
	IMPORT_C virtual void Init1();
	IMPORT_C virtual void Init3();

	// Power management
	IMPORT_C virtual void Idle();

	IMPORT_C void DebugInit();
	IMPORT_C virtual void DebugOutput(TUint aChar);

	// Timing
	IMPORT_C virtual TInt MsTickPeriod();
	IMPORT_C virtual TInt SystemTimeInSecondsFrom2000(TInt& aTime);
	IMPORT_C virtual TInt SetSystemTimeInSecondsFrom2000(TInt aTime);
	IMPORT_C virtual TUint32 NanoWaitCalibration();

	// HAL
	virtual TInt VariantHal(TInt aFunction, TAny* a1, TAny* a2);

	// Machine configuration
	virtual TPtr8 MachineConfiguration();

	TUint32 iDebugPortBase;

	static Htcleo* Variant;
	NTimerQ* iTimerQ;
};

GLREF_D Htcleo TheVariant;

#endif  // __HTCLEO_PRIV_H__

