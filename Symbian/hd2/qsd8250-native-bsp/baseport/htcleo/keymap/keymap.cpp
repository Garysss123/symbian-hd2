/*
* Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
* All rights reserved.
* This component and the accompanying materials are made available
* under the terms of the License "Eclipse Public License v1.0"
* which accompanies this distribution, and is available
* at the URL "http://www.eclipse.org/legal/epl-v10.html".
*
* Initial Contributors:
* Nokia Corporation - initial contribution.
*
* Contributors:
*
* Description: This is for a UK Keyboard
*
*/

#include <k32keys.h>

//#define US_KEYBOARD

// the "array" parameter must be a true array and not a pointer
#define ARRAY_LENGTH(array) (sizeof(array)/sizeof(array[0]))

#define TABLE_ENTRY_ANOTHER_CTRL_DIGIT					\
	{  													\
		{												\
		EModifierKeyUp|EModifierFunc,	                \
		0												\
		},												\
		{												\
		EKeyNull,										\
		EAnyDigitGivenRadix								\
		},												\
		{												\
		EStateCtrlDigits,								\
		EAddOnCtrlDigit,								\
		0												\
		}												\
	}

// This table is searched for a match if a match has not been
// found in the current state's table

LOCAL_D const SFuncTableEntry defaultTable[]=
	{
		{ // prevent key up events generating keycodes
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateUnchanged,
			EDoNothing,
			0
			}
		},
		{ // prevent any modifer key from changing state
			{
			0,
			0
			},
			{
			EKeyNull,
			EAnyModifierKey
			},
			{
			EStateUnchanged,
			EDoNothing,
			0
			}
		},
		{ // filter out any unprocessed codes???
			{
			0,
			0
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateNormal,
			EDoNothing,
			0
			}
		}
	};

// The table indicating which keys change which modifiers;
// the state field in this table is ignored
LOCAL_D const SFuncTableEntry modifierTable[]=
	{
        {
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyCapsLock,
			EMatchKey
			},
			{
			EStateUnchanged,
			EToggleModifier,
			EModifierCapsLock
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyNumLock,
			EMatchKey
			},
			{
			EStateUnchanged,
			EToggleModifier,
			EModifierNumLock
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyScrollLock,
			EMatchKey
			},
			{
			EStateUnchanged,
			EToggleModifier,
			EModifierScrollLock
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyLeftAlt,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierAlt|EModifierLeftAlt
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyLeftAlt,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierLeftAlt
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyLeftFunc,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierFunc|EModifierLeftFunc
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyLeftFunc,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierLeftFunc
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyLeftShift,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierShift|EModifierLeftShift
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyLeftShift,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierLeftShift
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyLeftCtrl,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierCtrl|EModifierLeftCtrl
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyLeftCtrl,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierLeftCtrl
			}
        },
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyRightAlt,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierAlt|EModifierRightAlt
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyRightAlt,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierRightAlt
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyRightFunc,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierFunc|EModifierRightFunc
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyRightFunc,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierRightFunc
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyRightShift,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierShift|EModifierRightShift
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyRightShift,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierRightShift
			}
		},
		{
			{
			EModifierKeyUp,
			0
			},
			{
			EKeyRightCtrl,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOnModifier,
			EModifierCtrl|EModifierRightCtrl
			}
		},
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyRightCtrl,
			EMatchKey
			},
			{
			EStateUnchanged,
			ETurnOffModifier,
			EModifierRightCtrl
			}
		}
	};

// table0 to table12 are the tables corresponding to states
// 0 to 12 respectively

//LOCAL_D const SFuncTableEntry table0[]=
//	{
//	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
//	};

LOCAL_D const SFuncTableEntry table1[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'e',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAe
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'c',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcCcedilla
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			's',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1EsTset
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOslash
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'd',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcThorn
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			't',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcSoftTh
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'l',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LeftChevron
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'r',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1RightChevron
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'x',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1InvExclam
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'q',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1InvQuest
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAo
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'p',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1Pound
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTableEntry table2[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'e',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcEumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'i',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcIumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'u',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcUumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'y',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcYumlaut
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			' ',
			EMatchKey
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1SpaceUmlaut
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTableEntry table3[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAgrave
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'e',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcEgrave
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'i',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcIgrave
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOgrave
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'u',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcUgrave
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			' ',
			EMatchKey
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1SpaceGrave
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTableEntry table4[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'e',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcEacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'i',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcIacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'u',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcUacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'y',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcYacute
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			' ',
			EMatchKey
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcSpaceAcute
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTableEntry table5[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAtilde
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'n',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcNtilde
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOtilde
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			' ',
			EMatchKey
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcSpaceTilde
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTableEntry table6[]=
	{
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'a',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcAcirc
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'e',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcEcirc
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'i',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcIcirc
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'o',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcOcirc
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			'u',
			EMatchKeyCaseInsens
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcUcirc
			}
		},
		{
			{
			EModifierFunc|EModifierKeyUp,
			0
			},
			{
			' ',
			EMatchKey
			},
			{
			EStateNormal,
			EPassSpecialKeyThru,
			ELatin1LcSpaceCirc
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

//LOCAL_D const SFuncTableEntry table7[]=
//	{
//	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
//	};

//LOCAL_D const SFuncTableEntry table8[]=
//	{
//	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
//	};

//LOCAL_D const SFuncTableEntry table9[]=
//	{
//	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
//	};

LOCAL_D const SFuncTableEntry table10[]=
	{
		{ // filter out up key strokes
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateUnchanged,
			EDoNothing,
			0
			}
		},
		{ // check for ctrl-number presses
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierCtrl
			},
			{
			EKeyNull,
			EAnyDecimalDigit
			},
			{
			EStateDerivedFromDigitEntered,
			EAddOnCtrlDigit,
			0
			}
		},
		{ // pass thru any keys which can't be state control keys
			{
			EModifierFunc,
			0,
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateUnchanged,
			EPassKeyThru,
			0
			}
		},
		{ // pass thru any keys which can't be state control keys
			{
			EModifierCtrl,
			EModifierCtrl,
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateUnchanged,
			EPassKeyThru,
			0
			}
		},
		{ // check for FN-q
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'q',
			EMatchKeyCaseInsens
			},
			{
			1,
			EDoNothing,
			0
			}
		},
		{ // check for FN-z
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'z',
			EMatchKeyCaseInsens
			},
			{
			2,
			EDoNothing,
			0
			}
		},
		{ // check for FN-x
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'x',
			EMatchKeyCaseInsens
			},
			{
			3,
			EDoNothing,
			0
			}
		},
		{ // check for FN-c
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'c',
			EMatchKeyCaseInsens
			},
			{
			4,
			EDoNothing,
			0
			}
		},
		{ // check for FN-v
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'v',
			EMatchKeyCaseInsens
			},
			{
			5,
			EDoNothing,
			0
			}
		},
		{ // check for FN-b
			{
			EModifierCtrl|EModifierFunc|EModifierKeyUp,
			EModifierFunc
			},
			{
			'b',
			EMatchKeyCaseInsens
			},
			{
			6,
			EDoNothing,
			0
			}
		},
		{ // pass thru any non-processed keys
			{
			0,
			0
			},
			{
			EKeyNull,
			EAnyKey
			},
			{
			EStateUnchanged,
			EPassKeyThru,
			0
			}
		}
	};

//LOCAL_D const SFuncTableEntry table11[]=
//	{
//	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
//	};

LOCAL_D const SFuncTableEntry table12[]=
	{  
		{
			{
			EModifierKeyUp,
			EModifierKeyUp
			},
			{
			EKeyLeftCtrl,
			EMatchLeftOrRight
			},
			{
			EStateNormal,
			EPassCtrlDigitsThru,
			0
			}
		},
	TABLE_ENTRY_ANOTHER_CTRL_DIGIT
	};

LOCAL_D const SFuncTable genFuncTables[]=
	{
		{
		0,
		NULL
		},
		{
		ARRAY_LENGTH(table1),
		&table1[0]
		},
		{
		ARRAY_LENGTH(table2),
		&table2[0]
		},
		{
		ARRAY_LENGTH(table3),
		&table3[0]
		},
		{
		ARRAY_LENGTH(table4),
		&table4[0]
		},
		{
		ARRAY_LENGTH(table5),
		&table5[0]
		},
		{
		ARRAY_LENGTH(table6),
		&table6[0]
		},
		{
		0,
		NULL
		},
		{
		0,
		NULL
		},
		{
		0,
		NULL
		},
		{
		ARRAY_LENGTH(table10),
		&table10[0]
		},
		{
		0,
		NULL
		},
		{
		ARRAY_LENGTH(table12),
		&table12[0]
		}
	};

LOCAL_D const SFuncTables FuncTables=
	{
		{
		ARRAY_LENGTH(defaultTable),
		&defaultTable[0]
		},
		{
		ARRAY_LENGTH(modifierTable),
		&modifierTable[0]
		},
	ARRAY_LENGTH(genFuncTables),
	&genFuncTables[0]
	};

LOCAL_D const SScanCodeBlock scanCodeBlock_unmodifiable[]=
	{
	{EStdKeyLeftShift, EStdKeyScrollLock}
	};

LOCAL_D const TUint16 convKeyCodes_unmodifiable[]=
	{
	EKeyLeftShift,
	EKeyRightShift,
	EKeyLeftAlt,
	EKeyRightAlt,
	EKeyLeftCtrl,
	EKeyRightCtrl,
	EKeyLeftFunc,
	EKeyRightFunc,
	EKeyCapsLock,
	EKeyNumLock,
	EKeyScrollLock
	};

// base: this table traps all of the keyboard's scanCodes except those in convKeyCodes_unmodifiable
LOCAL_D const SScanCodeBlock scanCodeBlock_base[]=
	{
	{EStdKeyNull, EStdKeyDownArrow},
	{'0', '9'},
	{'A', 'Z'},
	{EStdKeyF1, EStdKeyDictaphoneRecord},

	{EStdKeyDevice0,EStdKeyDeviceF},
	{EStdKeyApplication0, EStdKeyApplicationF},
	{EStdKeyYes, EStdKeyDecBrightness},

	};

LOCAL_D const TUint16 convKeyCodes_base[]=
	{
	EKeyNull,
	EKeyBackspace,
	EKeyTab,
	EKeyEnter,
	EKeyEscape,
	' ',
	EKeyPrintScreen,
	EKeyPause,
	EKeyHome,
	EKeyEnd,
	EKeyPageUp,
	EKeyPageDown,
	EKeyInsert,
	EKeyDelete,
	EKeyLeftArrow,
	EKeyRightArrow,
	EKeyUpArrow,
	EKeyDownArrow,
	'0',
	'1',
	'2',
	'3',
	'4',
	'5',
	'6',
	'7',
	'8',
	'9',
	'a',
	'b',
	'c',
	'd',
	'e',
	'f',
	'g',
	'h',
	'i',
	'j',
	'k',
	'l',
	'm',
	'n',
	'o',
	'p',
	'q',
	'r',
	's',
	't',
	'u',
	'v',
	'w',
	'x',
	'y',
	'z',
	EKeyF1,
	EKeyF2,
	EKeyF3,
	EKeyF4,
	EKeyF5,
	EKeyF6,
	EKeyF7,
	EKeyF8,
	EKeyF9,
	EKeyF10,
	EKeyF11,
	EKeyF12,
	EKeyF13,
	EKeyF14,
	EKeyF15,
	EKeyF16,
	EKeyF17,
	EKeyF18,
	EKeyF19,
	EKeyF20,
	EKeyF21,
	EKeyF22,
	EKeyF23,
	EKeyF24,
	'`',
	',',
	'.',
	'/',
	'\\',
	';',
	'\'',
#ifndef US_KEYBOARD
	'#',
#else
	'\\',
#endif
	'[',
	']',
	'-',
	'=',
	'/',
	'*',
	'-',
	'+',
	EKeyEnter,
	EKeyEnd,
	EKeyDownArrow,
	EKeyPageDown,
	EKeyLeftArrow,
	EKeyNull, // numeric keypad '5'
	EKeyRightArrow,
	EKeyHome,
	EKeyUpArrow,
	EKeyPageUp,
	EKeyInsert,
	EKeyDelete,
    EKeyMenu,
    EKeyBacklightOn,
    EKeyBacklightOff,
    EKeyBacklightToggle,
    EKeyIncContrast,
    EKeyDecContrast,
    EKeySliderDown,
    EKeySliderUp,
    EKeyDictaphonePlay,
    EKeyDictaphoneStop,
    EKeyDictaphoneRecord,


	EKeyDevice0,
	EKeyDevice1,
	EKeyDevice2,
	EKeyDevice3,
	EKeyDevice4,
	EKeyDevice5,
	EKeyDevice6,
	EKeyDevice7,
	EKeyDevice8,
	EKeyDevice9,
	EKeyDeviceA,
	EKeyDeviceB,
	EKeyDeviceC,
	EKeyDeviceE,
	EKeyDeviceE,
	EKeyDeviceF,
	EKeyApplication0,
	EKeyApplication1,
	EKeyApplication2,
	EKeyApplication3,
	EKeyApplication4,
	EKeyApplication5,
	EKeyApplication6,
	EKeyApplication7,
	EKeyApplication8,
	EKeyApplication9,
	EKeyApplicationA,
	EKeyApplicationB,
	EKeyApplicationC,
	EKeyApplicationD,
	EKeyApplicationE,
	EKeyApplicationF,
	EKeyYes,
	EKeyNo,
	EKeyIncBrightness,
	EKeyDecBrightness

	};

// caps-lock: this table traps those scanCodes which are affected by caps-lock
LOCAL_D const SScanCodeBlock scanCodeBlock_capsLock[]=
	{
	{'A', 'Z'}
	};

LOCAL_D const TUint16 convKeyCodes_capsLock[]=
	{
	'A',
	'B',
	'C',
	'D',
	'E',
	'F',
	'G',
	'H',
	'I',
	'J',
	'K',
	'L',
	'M',
	'N',
	'O',
	'P',
	'Q',
	'R',
	'S',
	'T',
	'U',
	'V',
	'W',
	'X',
	'Y',
	'Z'
	};

// shift: this table traps those scanCodes which are affected
// by shift EXCEPT for those scanCodes affected by caps-lock
LOCAL_D const SScanCodeBlock scanCodeBlock_shift[]=
	{
	{'0', '9'},
	{EStdKeyXXX, EStdKeyEquals},
	};

LOCAL_D const TUint16 convKeyCodes_shift[]=
	{
	')',
	'!',
	'"',
	ELatin1Pound,
	'$',
	'%',
	'^',
	'&',
	'*',
	'(',
	ELatin1LogicNot,
	'<',
	'>',
	'?',
	'|',
	':',
	'@',
	'~',
	'{',
	'}',
	'_',
	'+'
	};

// numlock: this table traps those scanCodes which are affected by numlock
LOCAL_D const SScanCodeBlock scanCodeBlock_numLock[]=
	{
	{EStdKeyNkpForwardSlash, EStdKeyNkpFullStop}
	};

LOCAL_D const TUint16 convKeyCodes_numLock[]=
	{
	'/',
	'*',
	'-',
	'+',
	EKeyEnter,
	'1',
	'2',
	'3',
	'4',
	'5',
	'6',
	'7',
	'8',
	'9',
	'0',
	'.'
	};

// func: this table traps those scanCodes which are affected
// by func but not shift
LOCAL_D const SScanCodeBlock scanCodeBlock_func[]=
	{
	{'0', '9'},
	{'K', 'L'},
	{'U', 'U'},
	{'I', 'I'},
	{'O', 'P'},
	{EStdKeySingleQuote, EStdKeySingleQuote},
	{EStdKeyLeftArrow, EStdKeyDownArrow},
	{EStdKeyTab, EStdKeyTab},
	{EStdKeyEscape, EStdKeyEscape},
	{'M', 'M'},
	{EStdKeyComma, EStdKeyFullStop},
	{EStdKeySpace, EStdKeySpace},
	{EStdKeyMenu, EStdKeyMenu},
	};

LOCAL_D const TUint16 convKeyCodes_func[]=
	{
	'}',
	'_',
	'#',
	'\\',
	'@',
	'<',
	'>',
	'[',
	']',
	'{',
	'~',
	';',
	'/',
	'*',
	'-',
	'+',
	':',
	EKeyHome,
	EKeyEnd,
	EKeyPageUp,
	EKeyPageDown,
	EKeyCapsLock,
	EKeyOff,
	EKeyDecContrast,
	EKeyHelp,
	EKeyIncContrast,
	EKeyBacklightToggle,
	EKeyDial,
	};

// func: this table traps those scanCodes which are affected
// by func and shift - lower case entries
LOCAL_D const SScanCodeBlock scanCodeBlock_funcUnshifted[]=
	{
	{'E', 'E'},
	};

LOCAL_D const TUint16 convKeyCodes_funcUnshifted[]=
	{
	ELatin1LcEacute,
	};

// func: this table traps those scanCodes which are affected
// by func and shift - upper case entries
LOCAL_D const SScanCodeBlock scanCodeBlock_funcShifted[]=
	{
	{'E', 'E'},
	};

LOCAL_D const TUint16 convKeyCodes_funcShifted[]=
	{
	ELatin1UcEacute,
	};

// ctrl: this table traps those scanCodes which are affected by ctrl
LOCAL_D const SScanCodeBlock scanCodeBlock_ctrl[]=
	{
// The space key gets handled else where, otherwise it gets
// thrown away as a NULL key
//	{EStdKeySpace, EStdKeySpace},

	{'A', 'Z'}
	};

LOCAL_D const TUint16 convKeyCodes_ctrl[]=
	{
//	0,
	1,
	2,
	3,
	4,
	5,
	6,
	7,
	8,
	9,
	10,
	11,
	12,
	13,
	14,
	15,
	16,
	17,
	18,
	19,
	20,
	21,
	22,
	23,
	24,
	25,
	26
	};

LOCAL_D const SConvSubTable
	convSubTable_unmodifiable=
		{
		&convKeyCodes_unmodifiable[0],
			{
			ARRAY_LENGTH(scanCodeBlock_unmodifiable),
			&scanCodeBlock_unmodifiable[0]
			}
		},
    convSubTable_base=
		{
		&convKeyCodes_base[0],
			{
			ARRAY_LENGTH(scanCodeBlock_base),
			&scanCodeBlock_base[0]
			}
		},
	convSubTable_capsLock=
		{
		&convKeyCodes_capsLock[0],
			{
			ARRAY_LENGTH(scanCodeBlock_capsLock),
			&scanCodeBlock_capsLock[0]
			}
		},
	convSubTable_shift=
		{
		&convKeyCodes_shift[0],
			{
			ARRAY_LENGTH(scanCodeBlock_shift),
			&scanCodeBlock_shift[0]
			}
		},
	convSubTable_numLock=
		{
		&convKeyCodes_numLock[0],
			{
			ARRAY_LENGTH(scanCodeBlock_numLock),
			&scanCodeBlock_numLock[0]
			}
        },
	convSubTable_func=
		{
		&convKeyCodes_func[0],
			{
			ARRAY_LENGTH(scanCodeBlock_func),
			&scanCodeBlock_func[0]
			}
		},
	convSubTable_funcUnshifted=
		{
		&convKeyCodes_funcUnshifted[0],
			{
			ARRAY_LENGTH(scanCodeBlock_funcUnshifted),
			&scanCodeBlock_funcUnshifted[0]
			}
		},
	convSubTable_funcShifted=
		{
		&convKeyCodes_funcShifted[0],
			{
			ARRAY_LENGTH(scanCodeBlock_funcShifted),
			&scanCodeBlock_funcShifted[0]
			}
		},
	convSubTable_ctrl=
		{
		&convKeyCodes_ctrl[0],
			{
			ARRAY_LENGTH(scanCodeBlock_ctrl),
			&scanCodeBlock_ctrl[0]
			}
		};

// Some modifiers, e.g. shift, may required more than one table (other than "base")
// to be searched; therefore arrays of tables are required
LOCAL_D const SConvSubTable
	* const convSubTableArray_unmodifiable[]={&convSubTable_unmodifiable},
	* const convSubTableArray_base[]={&convSubTable_base},
	* const convSubTableArray_capsLock[]={&convSubTable_capsLock},
	* const convSubTableArray_shift[]={&convSubTable_capsLock, &convSubTable_shift},
	* const convSubTableArray_capsLockShift[]={&convSubTable_shift},
	* const convSubTableArray_numLock[]={&convSubTable_numLock},
	* const convSubTableArray_func[]={&convSubTable_func,&convSubTable_funcUnshifted},
	* const convSubTableArray_funcShift[]={&convSubTable_func,&convSubTable_funcShifted},
	* const convSubTableArray_ctrl[]={&convSubTable_ctrl};

// The order of these nodes is VITAL, as the scanCode/modifiers are
// searched for a match in this order
LOCAL_D const SConvTableNode convTableNodes[]=
	{
		{
			{
			0,
			0
			},
		ARRAY_LENGTH(convSubTableArray_unmodifiable),
		&convSubTableArray_unmodifiable[0]
		},
		{
			{
			EModifierCtrl,
			EModifierCtrl
			},
		ARRAY_LENGTH(convSubTableArray_ctrl),
		&convSubTableArray_ctrl[0]
		},
		{
			{
			EModifierNumLock,
			EModifierNumLock
			},
		ARRAY_LENGTH(convSubTableArray_numLock),
		&convSubTableArray_numLock[0]
		},
		{
			{
			EModifierFunc|EModifierShift|EModifierCapsLock,
			EModifierFunc
			},
		ARRAY_LENGTH(convSubTableArray_func),
		&convSubTableArray_func[0]
		},
		{
			{
			EModifierFunc|EModifierShift|EModifierCapsLock,
			EModifierFunc|EModifierShift|EModifierCapsLock
			},
		ARRAY_LENGTH(convSubTableArray_func),
		&convSubTableArray_func[0]
		},
		{
			{
			EModifierFunc|EModifierShift|EModifierCapsLock,
			EModifierFunc|EModifierShift
			},
		ARRAY_LENGTH(convSubTableArray_funcShift),
		&convSubTableArray_funcShift[0]
		},
		{
			{
			EModifierFunc|EModifierShift|EModifierCapsLock,
			EModifierFunc|EModifierCapsLock
			},
		ARRAY_LENGTH(convSubTableArray_funcShift),
		&convSubTableArray_funcShift[0]
		},
		{
			{
			EModifierCapsLock|EModifierShift,
			EModifierCapsLock
			},
		ARRAY_LENGTH(convSubTableArray_capsLock),
		&convSubTableArray_capsLock[0]
		},
		{
			{
			EModifierShift|EModifierCapsLock,
			EModifierShift
			},
		ARRAY_LENGTH(convSubTableArray_shift),
		&convSubTableArray_shift[0]
		},
		{
			{
			EModifierCapsLock|EModifierShift,
			EModifierCapsLock|EModifierShift
			},
		ARRAY_LENGTH(convSubTableArray_capsLockShift),
		&convSubTableArray_capsLockShift[0]
		},
		{
			{
			0,
			0
			},
		ARRAY_LENGTH(convSubTableArray_base),
		&convSubTableArray_base[0]
		}
	};

// The top-level exported data structure of all the conversion tables
LOCAL_D const SConvTable ConvTable=
	{
	ARRAY_LENGTH(convTableNodes),
	&convTableNodes[0]
	};

// The list of scan-codes on the numeric keypad
LOCAL_D const SScanCodeBlock keypadScanCodeBlockArray[]=
	{
	{EStdKeyNumLock, EStdKeyNumLock},
	{EStdKeyNkpForwardSlash, EStdKeyNkpFullStop}
	};

LOCAL_D const SScanCodeBlockList ConvTableKeypadScanCodes=
	{
	ARRAY_LENGTH(keypadScanCodeBlockArray),
	&keypadScanCodeBlockArray[0]
	};

// The list of non-autorepeating key-codes
LOCAL_D const TUint16 nonAutorepKeyCodeArray[]=
	{
	EKeyEscape,
	EKeyPrintScreen,
	EKeyPause,
	EKeyInsert,
	EKeyLeftShift,
	EKeyRightShift,
	EKeyLeftAlt,
	EKeyRightAlt,
	EKeyLeftCtrl,
	EKeyRightCtrl,
	EKeyLeftFunc,
	EKeyRightFunc,
	EKeyCapsLock,
	EKeyNumLock,
	EKeyScrollLock,
    EKeyMenu,
    EKeyDictaphonePlay,
    EKeyDictaphoneStop,
    EKeyDictaphoneRecord
	};

LOCAL_D const SKeyCodeList ConvTableNonAutorepKeyCodes=
	{
	ARRAY_LENGTH(nonAutorepKeyCodeArray),
	&nonAutorepKeyCodeArray[0]
	};

EXPORT_C void KeyDataSettings(TRadix &aRadix,TCtrlDigitsTermination &aCtrlDigitsTermination,TInt &aDefaultCtrlDigitsMaxCount,
							  TInt &aMaximumCtrlDigitsMaxCount)
	{
	aRadix=EDecimal;
	aCtrlDigitsTermination=ETerminationByCtrlUp;
	aDefaultCtrlDigitsMaxCount=3;
	aMaximumCtrlDigitsMaxCount=10;
	}

EXPORT_C void KeyDataFuncTable(SFuncTables &aFuncTables)
	{
	aFuncTables=FuncTables;
	}

EXPORT_C void KeyDataConvTable(SConvTable &aConvTable, TUint &aConvTableFirstScanCode,TUint &aConvTableLastScanCode,
							 SScanCodeBlockList &aKeypadScanCode,SKeyCodeList &aNonAutorepKeyCodes)
	{
	aConvTable=ConvTable;
	aConvTableFirstScanCode=scanCodeBlock_base[0].firstScanCode;
	aConvTableLastScanCode=scanCodeBlock_base[ARRAY_LENGTH(scanCodeBlock_base)-1].lastScanCode;
	aKeypadScanCode=ConvTableKeypadScanCodes;
	aNonAutorepKeyCodes=ConvTableNonAutorepKeyCodes;
	}

