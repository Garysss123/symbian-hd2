// Private methods in the existing1018 channel; unchanged public ABI/lifecycle.
TInt WriteBacklightCommand1033(const TUint8* command,TInt bytes,TUint32 step){
    // HTC MicroP reference i2c_write_block sleeps at least1ms BEFORE each
    // transaction. A bounded NanoWait keeps this sequence on the existing
    // Dfc0 queue, serialized with touch, without a new timer/worker or retry.
    // It is a minimum device-command gap, not Linux scheduler equivalence.
    Kern::NanoWait(1000000u);
    TUint32 diagnostic=0;
    const TInt result=HtcleoI2cWrite(0x66u,command,bytes,1,&diagnostic);
    iStatus.iLastError=result;
    // Actual BSP diagnostics use phase1..5 in bits24..27 and zero bits28..31.
    // Preserve all those bits; mark the failed subcommand in the spare nibble.
    // 1=enable/disable,2=manual-mode,3=level. Success retains raw diagnostic.
    iStatus.iDiagnostic=result==KErrNone?diagnostic:(diagnostic|(step<<28));
    ++iStatus.iWrites;
    return result;
}
TInt SetBacklight(TBool on){
    // Even a late transfer error may have reached hardware. Clear recovery
    // responsibility only after the complete ON sequence acknowledges.
    iStatus.iRestoreNeeded=ETrue;
    const TUint8 enable[2]={0x26u,static_cast<TUint8>(on?1:0)};
    TInt result=WriteBacklightCommand1033(enable,2,1u);
    if(result!=KErrNone)return result;
    if(on){
        const TUint8 manual[3]={0x23u,1u,0u};
        result=WriteBacklightCommand1033(manual,3,2u);
        if(result!=KErrNone)return result;
        // Reference default255 -> (255-30)/23 ==9. Explicitly user-selected;
        // not a readback/claim about inherited boot-firmware brightness.
        const TUint8 brightness[2]={0x22u,0x90u};
        result=WriteBacklightCommand1033(brightness,2,3u);
        if(result!=KErrNone)return result;
    }
    iStatus.iCommandedOn=on?1:0;
    if(on)iStatus.iRestoreNeeded=EFalse;
    return KErrNone;
}
