"""Add dense, attributable Window Server plugin-manager events to WSLOG.TXT.

Iteration 411 proved that NGA Window Server reaches InitStatics stage 0x11 but
does not return from CWsPluginManager::NewL(). Screen-probe-era checkpoint
limits no longer apply: these durable events reuse the sole fail-open WSLOG
writer and bracket every meaningful leaving boundary in NewL, ConstructL, and
LoadPluginL without adding waits, retries, or alternate control flow.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_PLUGIN_PROGRESS_V2"
OLD_MARKER = "HTCLEO_WSERV_PLUGIN_PROGRESS_V1"
MACRO = "__HTCLEO_WSERV_DURABLE_LOG__"
STAGE_VALUES = tuple(range(0x40, 0x65)) + (0x6A,)
STAGES = tuple(f"0x{value:08X}u" for value in STAGE_VALUES)

OLD_LOGGER_BLOCK = f'''#ifdef {MACRO}
// {OLD_MARKER}
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoWsLog(TUint32, TInt, TUint32) {{}}
#endif
'''

LOGGER_BLOCK = f'''#ifdef {MACRO}
// {MARKER}
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoWsLog(TUint32, TInt, TUint32) {{}}
#endif
'''

REGION_START = "CWsPluginManager* CWsPluginManager::NewL()\n"
REGION_END = "void CWsPluginManager::InitializePluginsL"

DENSE_REGION = '''CWsPluginManager* CWsPluginManager::NewL()
	{
	HtcleoWsLog(0x00000040u, KErrNone, 0u);
	CWsPluginManager* self = new (ELeave) CWsPluginManager();
	HtcleoWsLog(0x00000041u, KErrNone, 0u);
	CleanupStack::PushL(self);
	HtcleoWsLog(0x00000042u, KErrNone, (TUint32)(self != NULL));
	self->ConstructL();
	HtcleoWsLog(0x0000004Fu, KErrNone, 0u);
	CleanupStack::Pop(self);
	HtcleoWsLog(0x0000006Au, KErrNone, (TUint32)(self != NULL));
	return self;
	}

CWsPluginManager::CWsPluginManager() :
    iSession(REComSession::OpenL())
	{
	}
	
CWsPluginManager::~CWsPluginManager()
	{
	iPlugins.ResetAndDestroy();
	iSession.Close();
	REComSession::FinalClose();
	}

void CWsPluginManager::ConstructL()
	{
	HtcleoWsLog(0x00000043u, KErrNone, 0u);
	_LIT(KPlugins,"PLUGINS");
	
	TPtrC pluginString;
	TBool havePlugins=WsIniFile->FindVar(KPlugins,pluginString);
	HtcleoWsLog(0x00000044u, (TInt)havePlugins,
		(TUint32)pluginString.Length());
	const TDesC * plugins;
	_LIT(KDefaultPlugins, "FLICKERBUFFER DISPLAY");	
	if (havePlugins)
		plugins = &pluginString;
	else
		plugins = &KDefaultPlugins;
	HtcleoWsLog(0x00000045u, (TInt)havePlugins,
		(TUint32)plugins->Length());
	TUint32 pluginIndex = 0u;
	TLex lex(*plugins);
	HtcleoWsLog(0x00000046u, KErrNone, (TUint32)plugins->Length());
	while(true)
		{
		TPtrC ptr = lex.NextToken();
		TUint32 tokenTag =
			((TUint32)(ptr.Length() > 0 ? ptr[0] : 0) << 16) |
			((TUint32)ptr.Length() & 0xFFFFu);
		HtcleoWsLog(0x00000047u, (TInt)pluginIndex, tokenTag);
		if (ptr.Length() > 0)
			{
			CWsPlugin * plugin = 0;
			HtcleoWsLog(0x00000048u, (TInt)pluginIndex, tokenTag);
			TRAPD(err, plugin = LoadPluginL(ptr));
			HtcleoWsLog(0x00000049u, err,
				(pluginIndex << 16) | (TUint32)(plugin != NULL));

			HtcleoWsLog(0x0000004Au, (TInt)(wsDebugLog != NULL), pluginIndex);
			if (wsDebugLog)
				{
				TBuf<80> buf;
				if (err == KErrNone)
					{
					_LIT(KLoadedPlugin,"Loaded plugin: ");
					_LIT(KPluginName, " calling itself: ");
					buf.Append(KLoadedPlugin);
					buf.Append(ptr);
					buf.Append(KPluginName);
					buf.Append(plugin->PluginName());
					wsDebugLog->MiscMessage(CDebugLogBase::ELogImportant,buf);
					}
				else
					{
					_LIT(KMissingPlugin,"Failed to load plugin (%d): ");
					buf.Append(KMissingPlugin);
					buf.Append(ptr);
					wsDebugLog->MiscMessage(CDebugLogBase::ELogImportant,buf,err);
					}
				}
			HtcleoWsLog(0x0000004Bu, err, pluginIndex);

			if (err<KErrNone)
				{	//Additionally log to RDebug if error
				_LIT(KMissingPlugin,"WServ: Failed to load plugin %S (error %d)");
				RDebug::Print(KMissingPlugin,&ptr,err);
				}
			HtcleoWsLog(0x0000004Cu, err, pluginIndex);
			++pluginIndex;
			}
		else
			{
			HtcleoWsLog(0x0000004Du, KErrNone, pluginIndex);
			break;
			}
		}
	HtcleoWsLog(0x0000004Eu, KErrNone, pluginIndex);
	}

CWsPlugin * CWsPluginManager::LoadPluginL(const TDesC& aSection)
	{
	TUint32 sectionTag =
		((TUint32)(aSection.Length() > 0 ? aSection[0] : 0) << 16) |
		((TUint32)aSection.Length() & 0xFFFFu);
	HtcleoWsLog(0x00000050u, KErrNone, sectionTag);
	_LIT(KId, "ID");
	_LIT(KData, "DATA");
	_LIT(KType, "TYPE");
	TInt id;
	TPtrC data;
	TPtrC type;
	TAny * dataPtr;
	CWsPlugin * plugin = 0;
	TBool hasId=WsIniFile->FindVar(aSection,KId,id);
	HtcleoWsLog(0x00000051u, (TInt)hasId,
		hasId ? (TUint32)id : 0u);
	TBool hasType=WsIniFile->FindVar(aSection,KType,type);
	TUint32 typeTag =
		((TUint32)(type.Length() > 0 ? type[0] : 0) << 16) |
		((TUint32)type.Length() & 0xFFFFu);
	HtcleoWsLog(0x00000052u, (TInt)hasType, typeTag);
	TInt fallbackRoute = 0;
	if ((!hasId) && (!hasType))
		{
		_LIT(KCscStage, "TCSC");
		_LIT(KFlickerBufferStage, "FLICKERBUFFER");
		_LIT(KDisplayStage, "DISPLAY");
		if (!aSection.CompareF(KFlickerBufferStage))
			{
			hasId = ETrue;
			id = 0x1028637B;
			fallbackRoute = 1;
			}
		else if (!aSection.CompareF(KDisplayStage))
			{
			hasId = ETrue;
			id = 0x1028637A;
			fallbackRoute = 2;
			}
		else if (!aSection.CompareF(KCscStage))
			{
			hasId = ETrue;
			id = 0x10286507;
			fallbackRoute = 3;
			}	
		else
			{
			hasType = ETrue;
			type.Set(aSection);
			typeTag = sectionTag;
			fallbackRoute = 4;
			}
		}
	TUint32 selectedId = hasId ? (TUint32)id : (TUint32)KPluginInterfaceId;
	HtcleoWsLog(0x00000053u, fallbackRoute,
		hasId ? selectedId : typeTag);
	TBool hasData = WsIniFile->FindVar(aSection,KData,data);
	TUint32 dataTag =
		((TUint32)(data.Length() > 0 ? data[0] : 0) << 16) |
		((TUint32)data.Length() & 0xFFFFu);
	HtcleoWsLog(0x00000054u, (TInt)hasData, dataTag);
	
	if (hasData)
		dataPtr = &data;
	else
		dataPtr = NULL;
	HtcleoWsLog(0x00000055u, (TInt)(dataPtr != NULL), selectedId);

	CPluginInfo* info = new (ELeave) CPluginInfo;
	HtcleoWsLog(0x00000056u, KErrNone, (TUint32)(info != NULL));
	CleanupStack::PushL(info);
	HtcleoWsLog(0x00000057u, KErrNone, (TUint32)(info != NULL));

	if (hasId)
		{
		TUid uid = TUid::Uid(id);
		HtcleoWsLog(0x00000058u, KErrNone, (TUint32)id);
		plugin = reinterpret_cast<CWsPlugin*>(iSession.CreateImplementationL(uid, CWsPlugin::DtorIDKeyOffset(), dataPtr));
		}
	else
		{
		HtcleoWsLog(0x00000059u, KErrNone, typeTag);
		TEComResolverParams params;
		RBuf8 buf8;
		buf8.CreateL(type.Length());
		HtcleoWsLog(0x0000005Au, KErrNone, (TUint32)buf8.MaxLength());
		CleanupClosePushL(buf8);
		buf8.Copy(type);
		params.SetDataType(buf8);
		HtcleoWsLog(0x0000005Bu, KErrNone, typeTag);
		HtcleoWsLog(0x0000005Cu, KErrNone, (TUint32)KPluginInterfaceId);
		plugin = reinterpret_cast<CWsPlugin*>(iSession.CreateImplementationL(TUid::Uid(KPluginInterfaceId),CWsPlugin::DtorIDKeyOffset(),dataPtr,params));
		HtcleoWsLog(0x0000005Du, KErrNone, (TUint32)(plugin != NULL));
		CleanupStack::PopAndDestroy(&buf8);
		HtcleoWsLog(0x0000005Eu, KErrNone, 0u);
		}
	HtcleoWsLog(0x0000005Fu, KErrNone, (TUint32)(plugin != NULL));
	
	User::LeaveIfNull(plugin);
	HtcleoWsLog(0x00000060u, KErrNone, 1u);
	info->iPlugin = plugin;
	HtcleoWsLog(0x00000061u, KErrNone, (TUint32)(info->iPlugin != NULL));
	HtcleoWsLog(0x00000062u, KErrNone, (TUint32)iPlugins.Count());
	TInt appendResult = iPlugins.Append(info);
	HtcleoWsLog(0x00000063u, appendResult, (TUint32)iPlugins.Count());
	User::LeaveIfError(appendResult);
	CleanupStack::Pop(info);
	HtcleoWsLog(0x00000064u, KErrNone, (TUint32)iPlugins.Count());
	return plugin;
	}

'''


def verify(source: str, top: str) -> None:
	checks = {
		"marker": source.count(MARKER) == 1 and OLD_MARKER not in source,
		"external logger": source.count("extern void HtcleoWsLog(") == 1,
		"single writer exported": top.count("\nvoid HtcleoWsLog(") == 2
		and top.count("static void HtcleoWsLog(") == 0,
		"dense checkpoints": all(source.count(stage) == 1 for stage in STAGES),
		"checkpoint count": sum(source.count(stage) for stage in STAGES) == len(STAGES),
		"no wait": "User::After" not in source,
		"one ECom open": source.count("REComSession::OpenL()") == 1,
		"one implementation call per branch": source.count("CreateImplementationL(") == 2,
	}
	failed = [name for name, ok in checks.items() if not ok]
	if failed:
		raise SystemExit("Window Server plugin progress verification failed: " + ", ".join(failed))


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
	args = parser.parse_args()

	base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc"
	source_path = base / "wspluginmanager.cpp"
	top_path = base / "WSTOP.CPP"
	for path in (source_path, top_path):
		if not path.is_file():
			raise SystemExit(f"missing Window Server source: {path}")

	source = source_path.read_text(encoding="utf-8")
	top = top_path.read_text(encoding="utf-8")
	if MARKER in source:
		verify(source, top)
		print(f"HTCLEO_WSERV_PLUGIN_PROGRESS=installed events={len(STAGES)} stages=40-64,6A")
		return

	if source.count(REGION_START) != 1 or source.count(REGION_END) != 1:
		raise SystemExit("Window Server plugin progress function region is ambiguous")
	if OLD_MARKER in source:
		if source.count(OLD_LOGGER_BLOCK) != 1:
			raise SystemExit("old Window Server plugin logger block is ambiguous")
		source = source.replace(OLD_LOGGER_BLOCK, LOGGER_BLOCK, 1)
	elif LOGGER_BLOCK not in source:
		anchor = '#include "inifile.h"\n'
		if source.count(anchor) != 1:
			raise SystemExit("Window Server plugin logger include anchor is ambiguous")
		source = source.replace(anchor, anchor + "\n" + LOGGER_BLOCK, 1)
	else:
		raise SystemExit("unexpected Window Server plugin logger state")

	# Re-resolve after header migration and replace the complete three-function
	# region. This upgrades V1 instrumentation while retaining manager semantics
	# in one canonical, reviewable body.
	start = source.index(REGION_START)
	end = source.index(REGION_END, start)
	source = source[:start] + DENSE_REGION + source[end:]
	source_path.write_text(source, encoding="utf-8")
	verify(source, top)
	print(f"HTCLEO_WSERV_PLUGIN_PROGRESS=installed events={len(STAGES)} stages=40-64,6A")


if __name__ == "__main__":
	main()
