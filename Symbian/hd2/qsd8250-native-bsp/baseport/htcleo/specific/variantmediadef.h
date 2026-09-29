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
* Description:
*
*/

#ifndef __VARIANTMEDIADEF_H__
#define __VARIANTMEDIADEF_H__

// Variant parameters for IRAM Media Driver (MEDINT.PDD)
#define IRAM_DRIVECOUNT 1
#define IRAM_DRIVELIST  0       // D:
#define IRAM_NUMMEDIA   1	
#define IRAM_DRIVENAME "IRam"

/*
 * Do not instantiate the Syborg fake NVMEM device.  HTC Leo uses the boot
 * microSD for both writable drives: partition 1 remains E: so the existing
 * MAGLDR payload and files are untouched, while partition 2 is exposed as C:.
 * DRIVELIST entries are local-drive indices ordered by MBR partition number.
 */
#define MMC0_DRIVECOUNT 2
#define MMC0_DRIVELIST  2,1
#define MMC0_NUMMEDIA   1
#define MMC0_DRIVENAME  "HTCLeoSD"

#endif  // __VARIANTMEDIADEF_H__
