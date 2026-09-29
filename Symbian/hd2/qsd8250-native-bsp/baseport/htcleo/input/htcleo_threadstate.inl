// HTCLEO_THREAD_STATE_READONLY_V2. Called only by explicit diagnostic HAL21.
// No GPIO/I2C, timer, scheduling, wake, suspend or completion operations.
// Native UP EKA2 structures are read under the system lock; the caller's
// already-open RThread handle pins the target object for this syscall.
// Read the native circular ready lists without changing their order. NThread
// objects are the queue nodes; no cast to an unknown DThread is needed.
// A brief IRQ mask protects this bounded read, inside the existing system lock.
static void HtcleoReadReadyQueues(TUint32* aWords, DThread& aCaller,
    DThread& aTarget, DThread* aEndpoint)
    {
    TScheduler* scheduler = TScheduler::Ptr();
    __ASSERT_COMPILE(_FOFF(TScheduler, iRescheduleNeededFlag) >=
        _FOFF(TPriListBase, iQueue) + 64 * sizeof(SDblQueLink*));
    aWords[24] = scheduler->iTimeSliceExpireCounter;
    aWords[25] = 0xffffffffu;
    TUint32 flags = 0;
    TInt seen = 0;
    TBool complete = ETrue;
    const TInt irq = NKern::DisableAllInterrupts();
    for (TInt priority = 63; priority >= 0 && complete; --priority)
        {
        if (!(scheduler->iPresent[priority >> 5] & (1u << (priority & 31))))
            continue;
        SDblQueLink* first = NULL;
        // TPriListBase declares a one-entry trailing array; TScheduler owns
        // the remaining63 entries. Match the kernel's offset-based access.
        memcpy(&first, reinterpret_cast<const TUint8*>(scheduler) +
            _FOFF(TPriListBase, iQueue) + priority * sizeof(first), sizeof(first));
        if (!first) { complete = EFalse; break; }
        SDblQueLink* link = first;
        do
            {
            if (!link || ((TLinAddr)link & 3u) || ++seen > 256) { complete = EFalse; break; }
            TPriListLink* item = static_cast<TPriListLink*>(link);
            if (item->iPriority != priority) { complete = EFalse; break; }
            NThreadBase* thread = static_cast<NThreadBase*>(item);
            if (thread == &aTarget.iNThread) flags |= 1u;
            if (aEndpoint && thread == &aEndpoint->iNThread) flags |= 2u;
            if (thread == &aCaller.iNThread) flags |= 4u;
            else if (aWords[25] == 0xffffffffu)
                {
                aWords[25] = (TUint32)priority;
                if (aEndpoint && thread == &aEndpoint->iNThread) flags |= 32u;
                if (thread == &aTarget.iNThread) flags |= 64u;
                }
            link = link->iNext;
            }
        while (link != first);
        }
    if (complete) flags |= 8u;
    else flags |= 16u;
    aWords[26] = flags;
    if (scheduler->iRescheduleNeededFlag) aWords[1] |= 4096u;
    if (scheduler->iDfcPendingFlag) aWords[1] |= 8192u;
    NKern::RestoreInterrupts(irq);
    }

static TInt __attribute__((noinline)) HtcleoReadThreadState(TAny* aHandle, TAny* aOutput)
    {
#ifdef __SMP__
    return KErrNotSupported;
#else
    if (!aOutput) return KErrArgument;
    DThread& caller = Kern::CurrentThread();
    if (caller.iOwningProcess->iS.iSecureId != 0x200286e3u)
        return KErrPermissionDenied;
    TUint32 words[37];
    memclr(words, sizeof(words));
    words[0] = 2u;
    words[12] = 0xffffffffu;
    words[13] = 0xffffffffu;
    for (TInt unknown = 27; unknown <= 34; ++unknown) words[unknown] = 0xffffffffu;
    TInt result = KErrBadHandle;
    NKern::ThreadEnterCS();
    NKern::LockSystem();
    DThread* target = static_cast<DThread*>(Kern::ObjectFromHandle(
        &caller, (TInt)aHandle, EThread));
    if (target && target != &caller && target->iOwningProcess)
        {
        const TUint32 sid = target->iOwningProcess->iS.iSecureId;
        if (sid == 0x101f4cd2u || sid == 0x102750f0u)
            {
            result = KErrNone;
            words[1] = 1u; // validated shell thread handle
            words[2] = target->iId;
            words[3] = target->iOwningProcess->iId;
            words[4] = target->iExitType;
            // Native sthread.cpp/arm/ckernel.cpp define iMState/iExiting on
            // iWaitLink, while nk_priv.h puts iNState on NThreadBase itself.
            words[5] = target->iWaitLink.iSpare1; // DThread::iMState
            words[6] = target->iNThread.iSpare1; // NThreadBase::iNState
            words[7] = (TUint32)target->iNThread.iSuspendCount;
            words[8] = (TUint32)target->iDefaultPriority;
            words[9] = (TUint32)target->iNThread.iPriority;
            words[10] = (TUint32)target->iNThread.iRequestSemaphore.iCount;
            words[11] = target->iIpcCount;
            words[22] = (TUint32)target->iNThread.iTimeslice;
            words[23] = (TUint32)target->iNThread.iTime;
            DThread* endpoint = NULL;
            if (target->iNThread.iHeldFastMutex) words[1] |= 64u;
            if (target->iNThread.iWaitFastMutex) words[1] |= 128u;
            words[36] = (TUint32)target->iExitReason;
            const TBool alive = target->iExitType == EExitPending &&
                !target->iWaitLink.iSpare2; // DThread::iExiting
            RMessageK* msg = alive ? target->iSyncMsgPtr : NULL;
            if (msg)
                {
                words[12] = msg->IsFree() ? 0u :
                    msg->IsInitialising() ? 1u : msg->IsDelivered() ? 2u :
                    msg->IsAccepted() ? 3u : msg->IsCompleting() ? 4u : 5u;
                if (!msg->IsFree() && msg->iClient == target)
                    {
                    words[1] |= 4u;
                    words[13] = (TUint32)msg->iFunction;
                    if (msg->iSession && msg->iSession->iServer)
                        {
                        words[1] |= 8u;
                        endpoint = msg->iSession->iServer->iOwningThread;
                        if (endpoint && endpoint->iOwningProcess)
                            {
                            // Session endpoint, not necessarily a server's
                            // eventual worker thread for this request.
                            words[1] |= 16u;
                            if (endpoint->iExitType == EExitPending) words[1] |= 32u;
                            words[14] = endpoint->iOwningProcess->iId;
                            words[15] = endpoint->iId;
                            words[16] = endpoint->iOwningProcess->iS.iSecureId;
                            words[27] = (TUint32)endpoint->iDefaultPriority;
                            words[28] = (TUint32)endpoint->iNThread.iPriority;
                            words[29] = endpoint->iNThread.iSpare1;
                            words[30] = endpoint->iWaitLink.iSpare1;
                            if (endpoint->iNThread.iWaitFastMutex) words[1] |= 512u;
                            if (endpoint->iNThread.iHeldFastMutex) words[1] |= 1024u;
                            if (endpoint != &caller && endpoint->iThreadType == EThreadUser &&
                                endpoint->iExitType == EExitPending && !endpoint->iWaitLink.iSpare2)
                                {
                                TUint32 regs[18];
                                memclr(regs, sizeof(regs));
                                words[1] |= 256u;
                                NKern::ThreadGetUserContext(&endpoint->iNThread, regs, words[35]);
                                words[31] = regs[13]; words[32] = regs[14];
                                words[33] = regs[15]; words[34] = regs[16];
                                }
                            }
                        }
                    }
                }
            if (target->iThreadType == EThreadUser && alive)
                {
                TUint32 regs[18];
                memclr(regs, sizeof(regs));
                words[1] |= 2u;
                NKern::ThreadGetUserContext(&target->iNThread, regs, words[17]);
                words[18] = regs[13]; words[19] = regs[14];
                words[20] = regs[15]; words[21] = regs[16];
                }
            HtcleoReadReadyQueues(words, caller, *target, endpoint);
            }
        else
            result = KErrPermissionDenied;
        }
    NKern::UnlockSystem();
    // No target/kernel pointers escape. All user memory copying is outside
    // the system lock, using the kernel's checked descriptor copy routine.
    if (result == KErrNone)
        Kern::InfoCopy(*static_cast<TDes8*>(aOutput),
            reinterpret_cast<const TUint8*>(words), sizeof(words));
    NKern::ThreadLeaveCS();
    return result;
#endif
    }
