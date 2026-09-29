// HTC Leo backlight-only LDD. No panel reset, brightness rewrite or CPU suspend.
// Hardware contract: HTC Linux board-htcleo.c and board-htcleo-bl.c:
// MicroP I2C0x66, command0x26 plus boolean enable byte.
#include <kernel/kern_priv.h>
#include "htcleo_qsd8k.h"
#include "htcleobacklight1018.h"

class DHtcleoBacklightChannel1018:public DLogicalChannel {
public:
    DHtcleoBacklightChannel1018():iClient(&Kern::CurrentThread()){
        ((DObject*)iClient)->Open();
        iStatus.iCommandedOn=-1;iStatus.iLastError=KErrNotReady;
        iStatus.iDiagnostic=0;iStatus.iWrites=0;iStatus.iRestoreNeeded=EFalse;
    }
    ~DHtcleoBacklightChannel1018(){Kern::SafeClose((DObject*&)iClient,NULL);}
    TInt DoCreate(TInt unit,const TDesC8* info,const TVersion& version){
        if(!Kern::CurrentThreadHasCapability(ECapabilityWriteDeviceData,__PLATSEC_DIAGNOSTIC_STRING("HTC Leo backlight"))||
           !Kern::CurrentThreadHasCapability(ECapabilityPowerMgmt,__PLATSEC_DIAGNOSTIC_STRING("HTC Leo backlight")))return KErrPermissionDenied;
        if(unit!=KNullUnit||info)return KErrArgument;
        if(!Kern::QueryVersionSupported(iDevice->iVersion,version))return KErrNotSupported;
        // Touch driver uses this same queue: no concurrent I2C transaction.
        SetDfcQ(Kern::DfcQue0());iMsgQ.Receive();return KErrNone;
    }
    TInt RequestUserHandle(DThread* thread,TOwnerType type){
        return type==EOwnerThread&&thread==iClient?KErrNone:KErrAccessDenied;
    }
    void HandleMsg(TMessageBase* message){
        TThreadMessage& m=*(TThreadMessage*)message;
        if(m.iValue==(TInt)ECloseMsg){
            // On normal close/client death, try to restore light on the same
            // serialized queue. Do not claim success if the hardware fails.
            if(iStatus.iRestoreNeeded)(void)SetBacklight(ETrue);
            m.Complete(KErrNone,EFalse);return;
        }
        TInt result=KErrNotSupported;
        if(m.Client()!=iClient)result=KErrAccessDenied;
        else if(m.iValue==KHtcleoBacklightSet1018){
            const TUint state=reinterpret_cast<TUint>(m.Ptr0());
            result=state<=1?SetBacklight(state!=0):KErrArgument;
        } else if(m.iValue==KHtcleoBacklightStatus1018){
            result=Kern::ThreadRawWrite(iClient,m.Ptr0(),&iStatus,sizeof(iStatus));
        }
        m.Complete(result,ETrue);
    }
private:
    TInt SetBacklight(TBool on){
        // Mark uncertainty before OFF: even a late transfer error may have
        // delivered the byte. Preserve recovery responsibility until ON ACKs.
        if(!on)iStatus.iRestoreNeeded=ETrue;
        const TUint8 command[2]={0x26u,static_cast<TUint8>(on?1:0)};
        TUint32 diagnostic=0;
        const TInt result=HtcleoI2cWrite(0x66u,command,2,1,&diagnostic);
        iStatus.iLastError=result;iStatus.iDiagnostic=diagnostic;++iStatus.iWrites;
        if(result==KErrNone){
            iStatus.iCommandedOn=on?1:0;
            if(on)iStatus.iRestoreNeeded=EFalse;
        }
        return result;
    }
    DThread* iClient;THtcleoBacklightStatus1018 iStatus;
};

class DHtcleoBacklightDevice1018:public DLogicalDevice {
public:
    DHtcleoBacklightDevice1018(){iVersion=TVersion(1,0,0);}
    TInt Install(){return SetName(&KHtcleoBacklightName1018);}
    void GetCaps(TDes8& caps)const{TPckgBuf<TVersion> v;v()=iVersion;Kern::InfoCopy(caps,v);}
    TInt Create(DLogicalChannelBase*& channel){
        if(iOpenChannels!=0)return KErrInUse;
        channel=new DHtcleoBacklightChannel1018;
        return channel?KErrNone:KErrNoMemory;
    }
};
DECLARE_STANDARD_LDD(){return new DHtcleoBacklightDevice1018;}
