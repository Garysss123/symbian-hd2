#ifndef HTCLEO_BACKLIGHT_1018_H
#define HTCLEO_BACKLIGHT_1018_H
#include <e32cmn.h>
_LIT(KHtcleoBacklightName1018,"HtcleoBacklight1018");
const TInt KHtcleoBacklightSet1018=0;
const TInt KHtcleoBacklightStatus1018=1;
struct THtcleoBacklightStatus1018 {
    TInt iCommandedOn; // -1 until a write succeeds; not a measured panel state
    TInt iLastError;
    TUint32 iDiagnostic;
    TUint32 iWrites;
    TBool iRestoreNeeded;
};
#ifndef __KERNEL_MODE__
#include <e32std.h>
class RHtcleoBacklight1018:public RBusLogicalChannel {
public:
    TInt Open(){
        if(Handle())return KErrNone;
        TInt r=User::LoadLogicalDevice(_L("Z:\\sys\\bin\\htcleobl18.ldd"));
        if(r!=KErrNone&&r!=KErrAlreadyExists)return r;
        return DoCreate(KHtcleoBacklightName1018,TVersion(1,0,0),KNullUnit,NULL,NULL,EOwnerThread);
    }
    TInt Set(TBool on){return DoControl(KHtcleoBacklightSet1018,reinterpret_cast<TAny*>(on?1:0));}
    TInt Status(THtcleoBacklightStatus1018& status){return DoControl(KHtcleoBacklightStatus1018,&status);}
};
#endif
#endif
