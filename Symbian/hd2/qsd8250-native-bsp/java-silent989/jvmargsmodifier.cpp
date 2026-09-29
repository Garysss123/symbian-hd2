// Shared opt-in playback compatibility hook. The original default is a no-op.
#include "jvmargsmodifier.h"
#include "logger.h"
#include <f32file.h>

static TBool SilentEnabled989()
{
    RFs fs;
    TInt err = fs.Connect();
    if (err != KErrNone) { ELOG1(EJavaRuntime, "J9SIL989 config_fs=%d unchanged", err); return EFalse; }
    RFile file;
    _LIT(KMode, "c:\\resource\\java\\jvm\\lib\\silent.txt");
    _LIT8(KEnabled, "SILENT989\r\n");
    err = file.Open(fs, KMode, EFileRead | EFileShareReadersOnly);
    TBuf8<16> text;
    TInt size = -1;
    if (err == KErrNone) err = file.Size(size);
    if (err == KErrNone && size == KEnabled().Length()) err = file.Read(text);
    file.Close(); fs.Close();
    return err == KErrNone && size == KEnabled().Length() && text == KEnabled;
}

OS_EXPORT void java::runtime::modifyJvmArguments(
    const std::wstring& identifier, std::list<std::wstring>& jvmArgs,
    std::list<std::wstring>& applicationAndArgs)
{
    // The production MIDP and standalone MIDlet launchers use distinct IDs.
    // Do not alter Installer, TCK, CDC main or control panel launch parameters.
    if (identifier != L"Midp" && identifier != L"standalonemidlet") return;
    if (!SilentEnabled989()) return;
    const std::wstring prefix(L"-Xbootclasspath/p:");
    const std::wstring path(L"c:\\resource\\java\\jvm\\lib\\silent989.jar");
    std::list<std::wstring>::iterator existing = jvmArgs.end();
    for (std::list<std::wstring>::iterator i = jvmArgs.begin(); i != jvmArgs.end(); ++i)
    {
        if (i->compare(0, prefix.length(), prefix) == 0)
        {
            if (existing != jvmArgs.end())
            { ELOG(EJavaRuntime, "J9SIL989 duplicate_prepend unchanged"); return; }
            existing = i;
        }
    }
    if (existing == jvmArgs.end()) jvmArgs.push_front(prefix + path);
    else *existing = prefix + path + L";" + existing->substr(prefix.length());
    // Only a loader request. The Java class emits a separate backend marker.
    ELOG(EJavaRuntime, "J9SIL989 requested=silent prepend=1 no_audio_hardware");
    (void)applicationAndArgs;
}
