#ifndef ABOUT1030_STARTWATCH_H
#define ABOUT1030_STARTWATCH_H
#include <e32base.h>
inline TInt AboutStartWatch1030()
    {
    if(RProcess().SecureId().iId!=0x10005a22u)return KErrPermissionDenied;
    // A diagnostic helper failure must not prevent the original UI startup.
    RTimer timer;TInt r=timer.CreateLocal();if(r)return r;
    TBuf<40> args;args.AppendNumFixedWidth(RProcess().Id().Id(),EHex,8);
    args.Append(' ');args.AppendNumFixedWidth(RThread().Id().Id(),EHex,8);
    RProcess child;r=child.Create(_L("C:\\sys\\bin\\abtwatch1030.exe"),args);
    if(r){timer.Close();return r;}
    TRequestStatus ready,deadline;child.Rendezvous(ready);
    if(ready!=KRequestPending)
        {
        r=ready.Int();
        // Do not strand our newly created helper suspended if logon allocation
        // failed. Its own observation is bounded; the target is never killed.
        if(child.ExitType()==EExitPending)child.Resume();
        child.Close();timer.Close();return r;
        }
    timer.After(deadline,1000000);child.Resume();
    User::WaitForRequest(ready,deadline);
    r=ready==KRequestPending?KErrTimedOut:ready.Int();
    if(deadline==KRequestPending){timer.Cancel();User::WaitForRequest(deadline);}
    if(ready==KRequestPending){child.RendezvousCancel(ready);User::WaitForRequest(ready);}
    child.Close();timer.Close();return r;
    }
#endif
