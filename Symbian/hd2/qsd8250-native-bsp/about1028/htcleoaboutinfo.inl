// HTCLEO_ABOUT1028_READONLY_INFO: port identity is a declared target, not a SIM.
#include <hal.h>
#include <hal_data.h>
#include "portversion.h"
#include "aboutrecord.h"

static TInt AboutPackageBuild1028(RFs& fs, TDes& output)
    {
    RFile file;
    TInt result = file.Open(fs, _L("C:\\Symbian3\\VERSION.txt"), EFileRead | EFileShareAny);
    if (result != KErrNone) return result;
    TInt size = 0; result = file.Size(size);
    TBuf8<4096> bytes;
    if (result == KErrNone && (size < 1 || size > bytes.MaxLength())) result = KErrCorrupt;
    if (result == KErrNone) result = file.Read(bytes, size);
    file.Close();
    if (result != KErrNone) return result;
    if (bytes.Length() != size) return KErrCorrupt;
    char build[8];
    const TInt length = AboutBuild1028(bytes.Ptr(), bytes.Length(), build, sizeof(build));
    if (!length) return KErrCorrupt;
    output.Copy(TPtrC8((const TUint8*)build, length));
    return KErrNone;
    }

void CAboutContainer::AddPortInfoL()
    {
    // Strings are nonempty and bounded. -2 is outside original legal-item IDs.
    SetTextL(_L("Port target: HTC HD2 (Leo)"), -2);
    SetTextL(_L("Source SDK: Symbian^3 PDK 3.0.4 / 1144"), -2);
    TBuf<160> row; TBuf<16> build;
    RFs fs; TInt connected = fs.Connect();
    TInt result = connected == KErrNone ? AboutPackageBuild1028(fs, build) : connected;
    row.Copy(_L("Port build: "));
    if (result == KErrNone) row.Append(build);
    else { row.Append(_L("Unavailable (")); row.AppendNum(result); row.Append(')'); }
    SetTextL(row, -2); AboutRecord1028(0x102820, result, 0);
    TVersion kernel = User::Version();
    row.Format(_L("Kernel (runtime): %d.%d.%d"), kernel.iMajor, kernel.iMinor, kernel.iBuild);
    SetTextL(row, -2);
    TInt bytes = 0;
    result = HAL::Get(HALData::EMemoryRAM, bytes);
    row.Copy(_L("RAM reported by OS: "));
    if (result == KErrNone && bytes >= 0) { row.AppendNum(bytes / 1048576); row.Append(_L(" MiB")); }
    else row.Append(_L("Unavailable"));
    SetTextL(row, -2); AboutRecord1028(0x102821, result, (TUint32)bytes);
    bytes = 0; result = HAL::Get(HALData::EMemoryRAMFree, bytes);
    row.Copy(_L("Free RAM (at open): "));
    if (result == KErrNone && bytes >= 0) { row.AppendNum(bytes / 1048576); row.Append(_L(" MiB")); }
    else row.Append(_L("Unavailable"));
    SetTextL(row, -2); AboutRecord1028(0x102822, result, (TUint32)bytes);
    const TSize screen = iCoeEnv->ScreenDevice()->SizeInPixels();
    row.Format(_L("Screen reported by OS: %d x %d"), screen.iWidth, screen.iHeight);
    SetTextL(row, -2);
    TVolumeInfo volume;
    result = connected == KErrNone ? fs.Volume(volume, EDriveC) : connected;
    row.Copy(_L("Free storage C: "));
    if (result == KErrNone && volume.iFree >= 0) { row.AppendNum(volume.iFree / 1048576); row.Append(_L(" MiB")); }
    else row.Append(_L("Unavailable"));
    fs.Close(); SetTextL(row, -2); AboutRecord1028(0x102823, result, 0);
    SetTextL(_L("Original component notices follow."), -2);
    }
