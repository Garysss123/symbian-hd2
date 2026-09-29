#ifndef HTCLEO_REMCON_POLICY985_H
#define HTCLEO_REMCON_POLICY985_H
// Standalone, C++98-testable policy; -1 is KErrNotFound, 0 is KErrNone.
// Missing remote-media-key service is not missing audio playback support.
inline bool RemConServiceAbsent985(int aOpen, int aFs, int aRom, int aWritable)
    {
    return aOpen==-1 && aFs==0 && aRom==-1 && aWritable==-1;
    }
#endif
