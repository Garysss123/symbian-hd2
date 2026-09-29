#!/usr/bin/env python3
"""Trace EikStart pre-factory startup for the HomeScreen process only."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKSTART_HOMESCREEN_TRACE_V1"
HOME_SID = "0x102750F0u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
// HTCLEO_EIKSTART_HOMESCREEN_TRACE_V1
// Append to the same one-MiB XML-controller trace.  The SID gate is checked
// before any file-server work, so every other EikStart caller remains silent.
static void HtcleoHomeEikStartLog(TUint32 aStage, TInt aResult,
                                  TUint32 aDetail)
                                  __attribute__((noinline));

static void HtcleoHomeEikStartLog(TUint32 aStage, TInt aResult,
                                  TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x102750F0u)
        return;
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSXML.TXT");
    (void)fs.MkDirAll(KDir);
    RFile file;
    r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= (1048576 - 128))
        {
        TBuf8<128> record;
        _LIT8(KPrefix, "HTCLEO_HST  ");
        record.Append(KPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
        record.Append('\n');
        (void)file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


FUNCTION = r'''EXPORT_C TInt EikStart::RunApplication(TApaApplicationFactory aApplicationFactory)
	{ // static
	const TBool htcleoHome =
		(RProcess().SecureId().iId == 0x102750F0u);
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590000u, KErrNone,
			1u);
	// Get the command line object with data as attached to the process by AppArc.
	CApaCommandLine* commandLine = NULL;
	TBool disableShutdownChecks = EFalse;
	TInt error = CApaCommandLine::GetCommandLineFromProcessEnvironment(commandLine);
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590001u, error,
			reinterpret_cast<TUint32>(commandLine));
	if(error)
		goto done;
		
#ifdef ALLOC_COUNTING
	TInt allocData[2];
	allocData[0]=0;
	allocData[1]=0;
	User::__DbgSetAllocFail(RHeap::EUser, STATIC_CAST(RHeap::TAllocFail, REINTERPRET_CAST(TUint, &allocData[0])), 0); // this line requires \base\e32\euser\US_HEAP.CPP to be temporarily modified to write to the allocData array passed in here
#endif // ALLOC_COUNTING

#ifdef _DEBUG
	TInt notUsed;
	HAL::Get(HALData::EDisplayColors, notUsed); // this is to pre-allocate the heap-cell that certain HAL functions leave lying around (without actually orphaning it) - if we don't do this then the User::__DbgMarkEnd near the end of the loop below will panic because of this heap-cell
#endif // _DEBUG

	// Mark the heap to detect memory leaks in debug builds.
	// The corresponding __DbgMarkEnd method is called conditionally below, dependent upon whether the app has disabled shutdown checks.
	// Here, the app has not yet run and so cannot yet have disabled shutdown checks. This call is therefore not conditional.
	User::__DbgMarkStart(RHeap::EUser);
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590002u, KErrNone, 0u);
	
	// Rename the thread. Do it in a {} block so that executableFileName does not stay 
	// on the stack while the application is running.
	{
	TFileName executableFileName = RProcess().FileName();
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590003u, KErrNone,
			(TUint32)executableFileName.Length());
	error = User::RenameThread(TParsePtrC(executableFileName).Name());
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590004u, error, 0u);
	if(error)
		goto done;
	}

	// Continue in a {} block, to avoid gccxml compiler complaining about gotos jumping over CEikEnv initialization
	{
	// Create the CEikonEnv, and construct the app from the command line if no problems
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590005u, KErrNone, 0u);
	CEikonEnv* env = new CEikonEnv;
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590006u,
			env ? KErrNone : KErrNoMemory,
			reinterpret_cast<TUint32>(env));
	if(!env)
		error = KErrNoMemory;
	else
		{
		const TInt constructorError = env->ConstructorError();
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x48590007u, constructorError, 0u);
		if(constructorError != KErrNone)
			error = constructorError;
		else
			{
			if (htcleoHome)
				HtcleoHomeEikStartLog(0x48590008u, KErrNone, 0u);
			TRAP(error, env->ConstructAppFromCommandLineL(aApplicationFactory, *commandLine));
			if (htcleoHome)
				HtcleoHomeEikStartLog(0x48590009u, error, 0u);
			}
		}
		
#ifdef ALLOC_COUNTING
	RDebug::Print(_L("Allocated %d and deallocated %d heap-cells %S start-up"), allocData[0], allocData[1], executable);
#endif // ALLOC_COUNTING
		
	delete commandLine;	// Must be deleted or CCoeEnv's heap checks will fail
	commandLine = NULL;
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x4859000Au, error, 0u);
	
	if (!error)	// Start the app if no errors
		{		
		// Run the application
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x4859000Bu, KErrNone, 0u);
		env->Execute();
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x4859000Cu, KErrNone, 0u);
		}
	else if(env)	// ... or handle errors (error != KErrNone)
		{
		const TInt originalError = error;
		if (error==KLeaveWithoutAlert || error==KLeaveExit)
			error = KErrNone;
		else
			TRAP_IGNORE(env->HandleError(error));	
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x4859000Du, originalError,
				(TUint32)error);
		} 
	if (env!=NULL)
		{
		disableShutdownChecks = env->DisableShutdownChecks();
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x4859000Eu, KErrNone,
				disableShutdownChecks ? 1u : 0u);
		env->DestroyEnvironment();
		if (htcleoHome)
			HtcleoHomeEikStartLog(0x4859000Fu, KErrNone, 0u);
		}
   				
	if (!error)
		{
		env = NULL;
		}
	}

done:
	delete commandLine;
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590010u, error,
			disableShutdownChecks ? 1u : 0u);
	if (!disableShutdownChecks)
		{
		User::__DbgMarkEnd(RHeap::EUser, 0); // Affects debug builds.
		}
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590011u, error,
			disableShutdownChecks ? 1u : 0u);
	
#ifdef ALLOC_COUNTING
	User::__DbgSetAllocFail(RHeap::EUser, RHeap::ENone, 0);
#endif // ALLOC_COUNTING
	
	if (htcleoHome)
		HtcleoHomeEikStartLog(0x48590012u, error, 0u);
	return error;
	}'''


def find_function(text: str) -> tuple[int, int]:
    start_text = "EXPORT_C TInt EikStart::RunApplication(TApaApplicationFactory aApplicationFactory)"
    start = text.find(start_text)
    if start < 0 or text.find(start_text, start + 1) >= 0:
        raise SystemExit("EikStart RunApplication anchor is absent or ambiguous")
    brace = text.find("{", start)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise SystemExit("EikStart RunApplication closing brace not found")


def verify(path: Path) -> None:
    text = path.read_text(encoding="latin-1")
    stages = [f"0x485900{stage:02X}u" for stage in range(0x13)]
    checks = {
        "marker": text.count(MARKER) == 1,
        "SID gate": text.count(HOME_SID) == 2,
        "all stages": all(text.count(stage) == 1 for stage in stages),
        "one path": text.count("C:\\\\Symbian3\\\\HSXML.TXT") == 1,
        "one MiB": text.count("1048576 - 128") == 1,
        "factory call preserved": text.count(
            "env->ConstructAppFromCommandLineL(aApplicationFactory, *commandLine)"
        ) == 1,
        "opaque factory not cast": "reinterpret_cast<TUint32>(aApplicationFactory)" not in text,
        "execute preserved": text.count("env->Execute();") == 1,
        "no normalization": "commandLine = CApaCommandLine::New" not in text,
        "no timer/display": "User::After" not in text and "HalFunction" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HomeScreen EikStart trace audit failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKSTART.CPP"
    if not path.is_file():
        raise SystemExit(f"missing EikStart source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER in text and "reinterpret_cast<TUint32>(aApplicationFactory)" in text:
        text = replace_once(
            text,
            "reinterpret_cast<TUint32>(aApplicationFactory)",
            "1u",
            "opaque application factory trace detail",
        )
        path.write_text(text, encoding="latin-1")
    elif MARKER not in text:
        text = replace_once(
            text,
            "#endif\n\n\n/** Called to run the application",
            "#endif\n" + LOGGER + "\n\n/** Called to run the application",
            "logger insertion",
        )
        start, end = find_function(text)
        text = text[:start] + FUNCTION + text[end:]
        path.write_text(text, encoding="latin-1")
    verify(path)
    print("HTCLEO_EIKSTART_HOMESCREEN_TRACE=installed stages=48590000-48590012 log=HSXML.TXT capacity=1048576")


if __name__ == "__main__":
    main()
