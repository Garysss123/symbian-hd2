#include <e32base.h>
#include "aboutrecord.h"
#include "observer_core.h"

class TAboutObserver1030
    {
public:
    TAboutObserver1030():iPid(0),iTid(0),iArmed(EFalse),iTimerArmed(EFalse){}
    TInt Bind()
        {
        const TInt n=User::CommandLineLength();
        if(n<=0 || n>40)return KErrArgument;
        TBuf<40> args;User::CommandLine(args);TLex lex(args);
        TInt r=lex.Val(iPid,EHex);if(r)return r;
        lex.SkipSpace();r=lex.Val(iTid,EHex);if(r)return r;
        lex.SkipSpace();if(!lex.Eos() || !iPid || !iTid)return KErrArgument;
        r=iThread.Open(TThreadId(iTid),EOwnerThread);if(r)return r;
        r=iThread.Process(iProcess);if(r)return r;
        if(iProcess.Id().Id()!=iPid || iThread.Id().Id()!=iTid ||
           iProcess.SecureId().iId!=0x10005a22u)return KErrPermissionDenied;
        if(iThread.ExitType()!=EExitPending)return KErrDied;
        return iTimer.CreateLocal();
        }
    TInt Arm()
        {
        iThread.Logon(iDeath);iArmed=ETrue;
        if(iDeath!=KRequestPending && iThread.ExitType()==EExitPending)
            return iDeath.Int()!=KErrNone?iDeath.Int():KErrGeneral;
        iTimer.After(iDeadline,30000000);iTimerArmed=ETrue;
        if(iDeadline!=KRequestPending && iDeadline.Int()!=KErrNone)
            return iDeadline.Int();
        return KErrNone;
        }
    void Ready(TInt r){RProcess::Rendezvous(r);}
    void Wait(){User::WaitForRequest(iDeath,iDeadline);}
    TBool Exited()const{return iThread.ExitType()!=EExitPending;}
    void RecordExit()
        {
        // Only after the About UI thread stopped: never race its log appends.
        AboutRecord1028(0x103100,0,iPid);
        AboutRecord1028(0x103101,0,iTid);
        AboutRecord1028(0x103102,iThread.ExitType(),iThread.ExitReason());
        const TExitCategoryName c=iThread.ExitCategory();
        AboutRecord1028(0x103103,c.Length(),iProcess.ExitType());
        for(TInt i=0;i<8;++i)
            {
            TUint32 v=0;const TInt p=2*i;
            if(p<c.Length())v=TUint32(c[p])<<16;
            if(p+1<c.Length())v|=TUint32(c[p+1]);
            AboutRecord1028(0x103110+i,i,v);
            }
        AboutRecord1028(0x1031ff,0,0x10005a22u);
        }
    void Close()
        {
        if(iTimerArmed && iDeadline==KRequestPending)
            {iTimer.Cancel();User::WaitForRequest(iDeadline);}
        if(iArmed && iDeath==KRequestPending)
            {iThread.LogonCancel(iDeath);User::WaitForRequest(iDeath);}
        iTimer.Close();iProcess.Close();iThread.Close();
        }
private:
    TUint32 iPid,iTid;
    RThread iThread;RProcess iProcess;RTimer iTimer;
    TRequestStatus iDeath,iDeadline;TBool iArmed,iTimerArmed;
    };

GLDEF_C TInt E32Main()
    {TAboutObserver1030 api;return AboutObserve1030(api);}
