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
* Description: Htcleo interrupt control and dispatch
*
*/

#include <htcleo_priv.h>

SInterruptHandler HtcleoInterrupt::Handlers[KNumHtcleoInts];

void HtcleoInterrupt::DisableAndClearAll()
{
	WriteReg(KHwBaseVic, EVicIntSelect0, 0u);
	WriteReg(KHwBaseVic, EVicIntSelect1, 0u);
	WriteReg(KHwBaseVic, EVicIntEnClear0, 0xffffffffu);
	WriteReg(KHwBaseVic, EVicIntEnClear1, 0xffffffffu);
	WriteReg(KHwBaseVic, EVicIntClear0, 0xffffffffu);
	WriteReg(KHwBaseVic, EVicIntClear1, 0xffffffffu);
	WriteReg(KHwBaseVic, EVicMasterEnable, 0u);
	QsdDrainWriteBuffer();
}

void HtcleoInterrupt::Init1()
{
	__KTRACE_OPT(KBOOT,Kern::Printf("HtcleoInterrupt::Init1()"));

	for(TUint i = 0; i < KNumHtcleoInts; i++)
	{
		Handlers[i].iPtr = (TAny*)i;
		Handlers[i].iIsr = Spurious;
	}

	DisableAndClearAll();
	/* GPT is a rising-edge IRQ; all other sources remain at boot defaults. */
	WriteReg(KHwBaseVic, EVicIntType0, 1u << EIntGpt);
	WriteReg(KHwBaseVic, EVicIntType1, 0u);
	WriteReg(KHwBaseVic, EVicIntPolarity0, 0u);
	WriteReg(KHwBaseVic, EVicIntPolarity1, 0u);
	WriteReg(KHwBaseVic, EVicConfig, 0u);
	QsdDrainWriteBuffer();
	
	Arm::SetIrqHandler((TLinAddr)HtcleoInterrupt::IrqDispatch);
	Arm::SetFiqHandler((TLinAddr)HtcleoInterrupt::FiqDispatch);
}

void HtcleoInterrupt::Init3()
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("HtcleoInterrupt::Init3()"));
}

void HtcleoInterrupt::Spurious(TAny* anId)
{
	// Handle an unexpected interrupt
	Kern::Fault("SpuriousInt", (TInt)anId);
}

EXPORT_C TInt Interrupt::Bind(TInt anId, TIsr anIsr, TAny* aPtr)
{
  __KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::Bind(anId=%d anIsr=0x%X aPtr=0x%X)",anId,anIsr,aPtr));
	if((anId >= 0) && ((TUint)anId < KNumHtcleoInts))
	{
		SInterruptHandler& h = HtcleoInterrupt::Handlers[anId];
		TInt irq = NKern::DisableAllInterrupts();
        TInt r;
		if(h.iIsr != HtcleoInterrupt::Spurious)
		{
            r = KErrInUse;
	    }
		else
		{
    	    h.iPtr = aPtr;
	    	h.iIsr = anIsr;
            r = KErrNone;
		}
		NKern::RestoreInterrupts(irq);
		return r;
	}
	return KErrArgument;
}

EXPORT_C TInt Interrupt::Unbind(TInt anId)
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::Unbind(%d)",anId));
	if((anId >= 0) && ((TUint)anId < KNumHtcleoInts))
	{
		SInterruptHandler& h = HtcleoInterrupt::Handlers[anId];
		TInt irq = NKern::DisableAllInterrupts();
    	TInt r;
		if(h.iIsr == HtcleoInterrupt::Spurious)
		{
			r = KErrGeneral;
		}
		else
		{
            // Reset pointer to handler back to default
			h.iPtr = (TAny*)anId;
			h.iIsr = HtcleoInterrupt::Spurious;	
			// Disable the interrupt
			THtcleo::DisableInt(anId);
			r = KErrNone;
        }
		NKern::RestoreInterrupts(irq);
    	return r;
	}
	return KErrArgument;
}

EXPORT_C TInt Interrupt::Enable(TInt anId)
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::Enable(%d)",anId));
	if((anId >= 0) && ((TUint)anId < KNumHtcleoInts))
	{
		if(HtcleoInterrupt::Handlers[anId].iIsr == HtcleoInterrupt::Spurious)
		{
	        return KErrNotReady;
		}
		else
		{
		  THtcleo::EnableInt(anId);
		  return KErrNone;
		}
	}
	return KErrArgument;
}

EXPORT_C TInt Interrupt::Disable(TInt anId)
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::Disable(%d)",anId));
	if((anId >= 0) && ((TUint)anId < KNumHtcleoInts))
	{
	  THtcleo::DisableInt(anId);
	  return KErrNone;
	}
	return KErrArgument;
}

EXPORT_C TInt Interrupt::Clear(TInt anId)
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::Clear(%d)",anId));
	if((anId >= 0) && ((TUint)anId < KNumHtcleoInts))
	{
		const TUint bankOffset = ((TUint)anId >> 5) << 2;
		WriteReg(KHwBaseVic, EVicIntClear0 + bankOffset,
		         1u << ((TUint)anId & 31));
		QsdDrainWriteBuffer();
	        return KErrNone;
	}
	return KErrArgument;
}

EXPORT_C TInt Interrupt::SetPriority(TInt anId, TInt aPriority)
{
	__KTRACE_OPT(KHARDWARE,Kern::Printf("Interrupt::SetPriority(anId=%d aPriority=0x%X)",anId,aPriority));
	return KErrNotSupported;
}

