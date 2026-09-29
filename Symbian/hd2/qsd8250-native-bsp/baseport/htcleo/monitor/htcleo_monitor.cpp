/* HTC Leo crash-monitor transport over the mapped QSD8250 UART3. */

#include <monitor.h>
#include "htcleo.h"

namespace
    {
    const TUint KUartMr1 = 0x00u;
    const TUint KUartMr2 = 0x04u;
    const TUint KUartCsrSr = 0x08u;
    const TUint KUartTfRf = 0x0cu;
    const TUint KUartCr = 0x10u;
    const TUint KUartImr = 0x14u;
    const TUint KUartSrTxReady = 1u << 2;
    const TUint KUartSrRxReady = 1u << 0;
    const TInt KUartPollLimit = 3000000;
    }

void CrashDebugger::InitUart()
    {
    WriteReg(KHwBaseUart3, KUartImr, 0u);
    WriteReg(KHwBaseUart3, KUartCr, 1u << 4); /* reset RX */
    WriteReg(KHwBaseUart3, KUartCr, 2u << 4); /* reset TX */
    WriteReg(KHwBaseUart3, KUartCr, 3u << 4); /* reset errors */
    WriteReg(KHwBaseUart3, KUartMr1, 0u);
    WriteReg(KHwBaseUart3, KUartMr2, (3u << 4) | (1u << 2));
    WriteReg(KHwBaseUart3, KUartCsrSr, 0xffu); /* 115200 */
    WriteReg(KHwBaseUart3, KUartCr, (1u << 2) | 1u); /* TX + RX */
    QsdDrainWriteBuffer();
    }

void CrashDebugger::UartOut(TUint aChar)
    {
    for (TInt i = 0; i < KUartPollLimit; ++i)
        if (ReadReg(KHwBaseUart3, KUartCsrSr) & KUartSrTxReady)
            {
            WriteReg(KHwBaseUart3, KUartTfRf, aChar & 0xffu);
            QsdDrainWriteBuffer();
            return;
            }
    }

TUint8 CrashDebugger::UartIn()
    {
    for (TInt i = 0; i < KUartPollLimit; ++i)
        if (ReadReg(KHwBaseUart3, KUartCsrSr) & KUartSrRxReady)
            return static_cast<TUint8>(ReadReg(KHwBaseUart3, KUartTfRf));
    return 0;
    }

TBool CrashDebugger::CheckPower()
    {
    return EFalse;
    }
