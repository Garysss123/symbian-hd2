#ifndef ABOUT1030_OBSERVER_CORE_H
#define ABOUT1030_OBSERVER_CORE_H

// Symbian and host fixture share this exact ownership/timeout state machine.
template<class TApi> int AboutObserve1030(TApi& api)
    {
    int r=api.Bind();
    if(r){api.Ready(r);api.Close();return r;}
    r=api.Arm();
    api.Ready(r);
    if(!r)
        {
        api.Wait();
        // Query the held thread, not a later lookup of a possibly reused ID.
        if(api.Exited())api.RecordExit();
        }
    api.Close();
    return r;
    }
#endif
