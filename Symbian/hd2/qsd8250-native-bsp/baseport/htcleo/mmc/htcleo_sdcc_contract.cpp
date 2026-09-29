/*
 * Compile-only HTC Leo SDCC2 contract.
 *
 * This unit deliberately performs no MMIO and is not included in the ROM.
 * It exists to validate the clean-room register and command contract with the
 * same legacy GCCE toolchain that will build the later MMC variant driver.
 */

#include "htcleo_sdcc_regs.h"

typedef char TSectorSizeMustBe512[
    HtcleoSdcc::KSectorBytes == 512u ? 1 : -1];
typedef char TFifoSizeMustBe64[
    HtcleoSdcc::KFifoBytes == 64u ? 1 : -1];
typedef char TFifoOffsetMustBeAligned[
    (HtcleoSdcc::EFifo & 3u) == 0u ? 1 : -1];

EXPORT_C TBool HtcleoSdccBringupCommandSupported(TUint32 aCommand)
    {
    return HtcleoSdcc::IsBringupCommand(aCommand);
    }

EXPORT_C TUint32 HtcleoSdcc2PhysicalBase()
    {
    return HtcleoSdcc::KSdcc2PhysicalBase;
    }
