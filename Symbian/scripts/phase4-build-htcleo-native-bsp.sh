#!/bin/sh
# Build the source-native HTC Leo/QSD8250 EKA2 kernel, variant and bootstrap.
# This stage deliberately does not create or deploy a Mini ROM.
set -eu

mode=${1:-udeb}
case "$mode" in
    udeb|urel) ;;
    *) echo "usage: $0 [udeb|urel]" >&2; exit 2 ;;
esac

export EPOCROOT=/root/symbian/
export SBS_HOME=/root/symbian/linux_build/sbsv2/raptor
export SBS_GCCE441BIN=/root/gcce-native-4.4.1/bin
export PERL5LIB=/root/symbian/linux_build/cross-plat-dev-utils
export PERL_USE_UNSAFE_INC=1

project=/path/to/hd2-legacy-lab/Symbian
bsp_source="$project/hd2/qsd8250-native-bsp"
bsp_stage="$EPOCROOT/sf/adapt/htcleo"
kernel_source=/root/symbian-oss/kernelhwsrv-gccsurge
kernel_patch="$bsp_source/patches/kernelhwsrv-qsd8250-l1ip.patch"
low_rom_pd_patch="$bsp_source/patches/kernelhwsrv-qsd8250-low-rom-user-pd.patch"
mmc_retry_gap_patch="$bsp_source/patches/kernelhwsrv-qsd8250-mmc-retrygap-sync.patch"
mmc_retry_gap_migrate_patch="$bsp_source/patches/kernelhwsrv-qsd8250-mmc-retrygap-migrate.patch"
mmc_session_timers_patch="$bsp_source/patches/kernelhwsrv-qsd8250-mmc-session-timers-sync.patch"
gate2_probe_patch="$bsp_source/patches/kernelhwsrv-qsd8250-gate2-probe.patch"
first_user_probe_patch="$bsp_source/patches/kernelhwsrv-qsd8250-second-thread-post-tls-result-all-arm-udf-probe.patch"
retire_kernel_exception_screen_transform="$project/scripts/retire-htcleo-kernel-exception-screen-probe.py"
retire_estart_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-retire-estart-screen-probe.patch"
fat_log_writer_patch="$bsp_source/patches/kernelhwsrv-htcleo-fat-log-writer.patch"
fat_log_symbian3_path_patch="$bsp_source/patches/kernelhwsrv-htcleo-fat-log-symbian3-path.patch"
fat_log_result_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-fat-log-result-probe.patch"
retire_fat_log_result_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-retire-fat-log-result-probe.patch"
restore_fat_log_result_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-restore-fat-log-result-probe.patch"
post_startsystem_before_fat_writer_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-post-startsystem-before-fat-writer-probe.patch"
post_run_before_startsystem_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-post-run-before-startsystem-probe.patch"
add_post_run_before_startsystem_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-add-post-run-before-startsystem-probe.patch"
remove_malformed_startsystem_create_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-remove-malformed-startsystem-create-probe.patch"
drive2_read_result_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-drive2-read-result-probe.patch"
drive2_pre_read_boundary_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-drive2-pre-read-boundary-probe.patch"
post_removable_mount_loop_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-post-removable-mount-loop-probe.patch"
mount_removable_entry_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-mount-removable-entry-probe.patch"
post_local_drive_init_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-post-local-drive-init-probe.patch"
pre_startup_init_complete_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-pre-startup-init-complete-probe.patch"
post_local_drive_mapping_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-post-local-drive-mapping-probe.patch"
pre_local_drive_mapping_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-pre-local-drive-mapping-probe.patch"
pre_local_drive_init_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-pre-local-drive-init-probe.patch"
gate8_entry_regression_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-gate8-entry-regression-probe.patch"
estart_entry_regression_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-estart-entry-regression-probe.patch"
extension_progress_probe_transform="$project/scripts/apply-htcleo-extension-progress-probes.py"
estart_fat_progress_transform="$project/scripts/apply-htcleo-estart-fat-progress.py"
estart_localdrive_progress_transform="$project/scripts/apply-htcleo-localdrive-progress.py"
estart_localdrive_drive_progress_transform="$project/scripts/apply-htcleo-localdrive-drive-progress.py"
localmedia_caps_progress_transform="$project/scripts/apply-htcleo-localmedia-caps-progress.py"
localmedia_powerup_progress_transform="$project/scripts/apply-htcleo-localmedia-powerup-progress.py"
mmc_init_progress_transform="$project/scripts/apply-htcleo-mmc-init-progress.py"
mmc_post_powerup_progress_transform="$project/scripts/apply-htcleo-mmc-post-powerup-progress.py"
mmc_completion_handoff_progress_transform="$project/scripts/apply-htcleo-mmc-completion-handoff-progress.py"
mmc_disengage_progress_transform="$project/scripts/apply-htcleo-mmc-disengage-progress.py"
mmc_session_cleanup_progress_transform="$project/scripts/apply-htcleo-mmc-session-cleanup-progress.py"
mmc_assp_disengage_progress_transform="$project/scripts/apply-htcleo-mmc-assp-disengage-progress.py"
mmc_second_stage_media_open_progress_transform="$project/scripts/apply-htcleo-mmc-second-stage-media-open-progress.py"
mmc_media_driver_partition_progress_transform="$project/scripts/apply-htcleo-mmc-media-driver-partition-progress.py"
estart_first_fat_mount_progress_transform="$project/scripts/apply-htcleo-estart-first-fat-mount-progress.py"
fat_directory_cache_progress_transform="$project/scripts/apply-htcleo-fat-directory-cache-read-progress.py"
fat_media_read_progress_transform="$project/scripts/apply-htcleo-fat-media-read-progress.py"
fat_physical_read_progress_transform="$project/scripts/apply-htcleo-fat-physical-read-progress.py"
fat_sdcc_completion_progress_transform="$project/scripts/apply-htcleo-fat-sdcc-completion-progress.py"
fat_sd_finish_poll_progress_transform="$project/scripts/apply-htcleo-fat-sd-finish-poll-progress.py"
sd_explicit_stop_progress_transform="$project/scripts/apply-htcleo-sd-explicit-stop-progress.py"
fat_post_stop_return_progress_transform="$project/scripts/apply-htcleo-fat-post-stop-return-progress.py"
fat_cache_unwind_progress_transform="$project/scripts/apply-htcleo-fat-cache-unwind-progress.py"
fat_mount_log_boundary_progress_transform="$project/scripts/apply-htcleo-fat-mount-log-boundary-progress.py"
fat_log_writer_entry_progress_transform="$project/scripts/apply-htcleo-fat-log-writer-entry-progress.py"
fat_log_mount_fallback_progress_transform="$project/scripts/apply-htcleo-fat-log-mount-fallback-progress.py"
fat_log_remount_recovery_progress_transform="$project/scripts/apply-htcleo-fat-log-remount-recovery-progress.py"
efile_e_remount_progress_transform="$project/scripts/apply-htcleo-efile-e-remount-progress.py"
efat_e_mountl_progress_transform="$project/scripts/apply-htcleo-efat-e-mountl-progress.py"
fixed_boot_caps_recovery_progress_transform="$project/scripts/apply-htcleo-fixed-boot-caps-recovery-progress.py"
e_caps_route_progress_transform="$project/scripts/apply-htcleo-e-caps-route-progress.py"
known_fat_bootlog_progress_transform="$project/scripts/apply-htcleo-known-fat-bootlog-progress.py"
async_fat_bootlog_progress_transform="$project/scripts/apply-htcleo-async-fat-bootlog-progress.py"
efile_bootlog_write_progress_transform="$project/scripts/apply-htcleo-efile-bootlog-write-progress.py"
efile_bootlog_write_gate_fix_transform="$project/scripts/apply-htcleo-efile-bootlog-write-gate-fix.py"
fat_first_write_progress_transform="$project/scripts/apply-htcleo-fat-first-write-progress.py"
fat_cluster_allocation_progress_transform="$project/scripts/apply-htcleo-fat-cluster-allocation-progress.py"
fat_free_space_scanner_progress_transform="$project/scripts/apply-htcleo-fat-free-space-scanner-progress.py"
fat_synchronous_scan_progress_transform="$project/scripts/apply-htcleo-fat-synchronous-free-space-scan-progress.py"
loader_durable_log_transform="$project/scripts/apply-htcleo-loader-durable-log.py"
loader_completion_tail_transform="$project/scripts/apply-htcleo-loader-completion-tail-log.py"
loader_akncustcmd_retarget_transform="$project/scripts/apply-htcleo-akncustcmd-loader-log.py"
kernel_library_attach_progress_transform="$project/scripts/apply-htcleo-kernel-library-attach-progress.py"
restore_removable_mount_patch="$bsp_source/patches/kernelhwsrv-htcleo-restore-removable-mount.patch"
mount_removable_result_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-mount-removable-result-probe.patch"
local_drive2_caps_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-local-drive2-caps-probe.patch"
local_drive2_partial_cleanup_patch="$bsp_source/patches/kernelhwsrv-htcleo-local-drive2-partial-reapply-cleanup.patch"
local_drive2_stage_tag_probe_patch="$bsp_source/patches/kernelhwsrv-htcleo-local-drive2-stage-tag-probe.patch"
sdcc_command_diagnostic_result_patch="$bsp_source/patches/kernelhwsrv-htcleo-sdcc-command-diagnostic-result.patch"
local_drive2_read_trigger_patch="$bsp_source/patches/kernelhwsrv-htcleo-local-drive2-read-trigger.patch"
read_result_over_sentinel_patch="$bsp_source/patches/kernelhwsrv-htcleo-read-result-over-sentinel.patch"
live_socket_state_result_patch="$bsp_source/patches/kernelhwsrv-htcleo-live-socket-state-result.patch"
sdcc_kernel_udf_renderer_patch="$bsp_source/patches/kernelhwsrv-htcleo-sdcc-kernel-udf-renderer.patch"
output="$project/output/qsd8250-native-bsp"
log="$output/build-$mode.log"
configuration="arm.v5.$mode.gcce4_4_1.surge.hd2_roalign"

if [ -L "$bsp_stage" ]; then
    linked=$(readlink -f "$bsp_stage")
    if [ "$linked" != "$(readlink -f "$bsp_source")" ]; then
        echo "ERROR: $bsp_stage points to an unrelated package" >&2
        exit 1
    fi
    # The legacy GCCE host tools cannot stat some DrvFS inodes.  Replace only
    # this verified link with an ext4 staging directory.
    unlink "$bsp_stage"
fi

if [ -e "$bsp_stage" ] && [ ! -f "$bsp_stage/.stage-owner" ]; then
    echo "ERROR: refusing to overwrite unowned staging path: $bsp_stage" >&2
    exit 1
fi

mkdir -p "$bsp_stage"
cp -a "$bsp_source/." "$bsp_stage/"
# DrvFS archive timestamps can land within the same coarse timestamp window as
# the previous staged object. Force the actively iterated SDCC source newer so
# Raptor cannot reuse a stale object after a probe-only edit.
touch "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
touch_source="$bsp_stage/baseport/htcleo/input/htcleo_touch.cpp"
touch "$touch_source"

xmmu="$kernel_source/kernel/eka/memmodel/epoc/multiple/arm/xmmu.cpp"
if ! grep -q '__CPU_QSD8250__' "$xmmu"; then
    patch --batch --forward -d "$kernel_source" -p1 < "$kernel_patch"
fi
if ! grep -q 'first untouched ROM page raises IFSR 0x5' "$xmmu"; then
    patch --batch --forward -d "$kernel_source" -p1 < "$low_rom_pd_patch"
fi

mmc_stack="$kernel_source/kernel/eka/drivers/pbus/mmc/stack.cpp"
mmc_mmp="$kernel_source/kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/epbussd.mmp"
if ! grep -q 'HTCLEO bring-up compatibility: the first CMD0 completes' "$mmc_stack"; then
    test -s "$mmc_retry_gap_patch"
    patch --batch --forward -d "$kernel_source" -p1 < "$mmc_retry_gap_patch"
elif ! grep -q '__HTCLEO_MMC_SYNC_RETRY_GAP__' "$mmc_stack"; then
    # Migrate an already-patched checkout from the earlier ineffective
    # __CPU_QSD8250__ guard to the epbussd-local build marker.
    test -s "$mmc_retry_gap_migrate_patch"
    patch --batch --forward -d "$kernel_source" -p1 < "$mmc_retry_gap_migrate_patch"
fi
grep -q '__HTCLEO_MMC_SYNC_RETRY_GAP__' "$mmc_stack"
grep -q '__HTCLEO_MMC_SYNC_RETRY_GAP__' "$mmc_mmp"
if ! grep -q '__HTCLEO_MMC_SYNC_SESSION_TIMERS__' "$mmc_stack"; then
    test -s "$mmc_session_timers_patch"
    patch --batch --forward -d "$kernel_source" -p1 < "$mmc_session_timers_patch"
fi
grep -q '__HTCLEO_MMC_SYNC_SESSION_TIMERS__' "$mmc_stack"
grep -q '__HTCLEO_MMC_SYNC_SESSION_TIMERS__' "$mmc_mmp"

exstart="$kernel_source/kernel/eka/kernel/exstart.cpp"
if ! grep -q 'HtcleoGate2ScreenProbe' "$exstart"; then
    patch --batch --forward -d "$kernel_source" -p1 < "$gate2_probe_patch"
fi

efile_main="$kernel_source/userlibandfileserver/fileserver/sfile/sf_main.cpp"
efile_ldr="$kernel_source/userlibandfileserver/fileserver/sfile/sf_ldr.cpp"
efile_lepoc="$kernel_source/userlibandfileserver/fileserver/sfile/sf_lepoc.cpp"
efile_loader_logger="$kernel_source/userlibandfileserver/fileserver/sfile/HtcleoLoaderLog.cpp"
efile_loader_header="$kernel_source/userlibandfileserver/fileserver/sfile/HtcleoLoaderLog.h"
efile_cache="$kernel_source/userlibandfileserver/fileserver/sfile/sf_cache.cpp"
efile_sys="$kernel_source/userlibandfileserver/fileserver/sfile/sf_sys.cpp"
efile_drv="$kernel_source/userlibandfileserver/fileserver/sfile/sf_drv.cpp"
efile_file="$kernel_source/userlibandfileserver/fileserver/sfile/sf_file.cpp"
efile_ext="$kernel_source/userlibandfileserver/fileserver/sfile/sf_ext.cpp"
efile_mmp="$kernel_source/userlibandfileserver/fileserver/sfile/efile.mmp"
fat_mount_source="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_mnt32.cpp"
fat_mmp="$kernel_source/userlibandfileserver/fileserver/sfat32/efat32.mmp"
fat_bldinf="$kernel_source/userlibandfileserver/fileserver/sfat32/bld.inf"
fat_header="$kernel_source/userlibandfileserver/fileserver/sfat32/inc/sl_std.h"
fat_file_source="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_file.cpp"
fat_table_source="$kernel_source/userlibandfileserver/fileserver/sfat32/fat_table32.cpp"
fat_constructor="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_mnt.cpp"
fat_cache_header="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_cache.h"
fat_dynamic_cache_header="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_dir_cache.h"
fat_legacy_cache_source="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_cache.cpp"
fat_dynamic_cache_source="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_dir_cache.cpp"
fat_drive_source="$kernel_source/userlibandfileserver/fileserver/sfat32/sl_drv.cpp"
htcleo_estart_config="$bsp_stage/baseport/htcleo/rom/estart.txt"
estart_main="$kernel_source/userlibandfileserver/fileserver/estart/estartmain.cpp"
estart_source="$kernel_source/userlibandfileserver/fileserver/estart/estart.cpp"
estart_header="$kernel_source/userlibandfileserver/fileserver/estart/estart.h"
estart_mmp="$kernel_source/userlibandfileserver/fileserver/estart/estart.mmp"
putils="$kernel_source/kernel/eka/memmodel/epoc/putils.cpp"
uc_exe="$kernel_source/kernel/eka/euser/epoc/arm/uc_exe.cpp"
up_utl="$kernel_source/kernel/eka/euser/epoc/up_utl.cpp"
callfirstprocessfn="$kernel_source/kernel/eka/compsupp/symaehabi/callfirstprocessfn.cpp"
efile_probe_mmp="$bsp_stage/baseport/htcleo/probes/htcleo_efile_heap_result.mmp"
efile_probe_cia="$bsp_stage/baseport/htcleo/probes/htcleo_efile_heap_result.cia"
variant_mmh="$bsp_stage/baseport/htcleo/variant.mmh"
bsp_bldinf="$bsp_stage/baseport/htcleo/bld.inf"
variant_media="$bsp_stage/baseport/htcleo/specific/variantmediadef.h"
uart_source="$bsp_stage/baseport/htcleo/serial/htcleo_euart.cpp"
sound_source="$bsp_stage/baseport/htcleo/sound/htcleo_soundsc.cpp"
qdsp_source="$bsp_stage/baseport/htcleo/sound/htcleo_qdsp.cpp"
heap_hybrid="$kernel_source/kernel/eka/common/heap_hybrid.cpp"
variant_euser_mmp="$kernel_source/kernel/eka/euser/variant_euser.mmp"
ckernel="$kernel_source/kernel/eka/kernel/arm/ckernel.cpp"
ckernel_cia="$kernel_source/kernel/eka/kernel/arm/ckernel.cia"
vectors_cia="$kernel_source/kernel/eka/nkern/arm/vectors.cia"
sexec="$kernel_source/kernel/eka/kernel/sexec.cpp"
scodeseg_source="$kernel_source/kernel/eka/kernel/scodeseg.cpp"
execs_txt="$kernel_source/kernel/eka/kernel/execs.txt"
us_ksvr="$kernel_source/kernel/eka/euser/us_ksvr.cpp"
locmedia_source="$kernel_source/kernel/eka/drivers/locmedia/locmedia.cpp"
medmmc_source="$kernel_source/kernel/eka/drivers/medmmc/medmmc.cpp"
pbusmedia_source="$kernel_source/kernel/eka/drivers/pbus/pbusmedia.cpp"
spbus_source="$kernel_source/kernel/eka/drivers/pbus/spbus.cpp"
mmc_stack_source="$kernel_source/kernel/eka/drivers/pbus/mmc/stack.cpp"
mmc_session_source="$kernel_source/kernel/eka/drivers/pbus/mmc/session.cpp"
mmc_sdcard_source="$kernel_source/kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp"
mmc_header="$kernel_source/kernel/eka/include/drivers/mmc.h"
exported_mmc_header="$EPOCROOT/epoc32/include/platform/drivers/mmc.h"
sdcc_stage_source="$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
elocd_mmp="$kernel_source/kernel/eka/drivers/locmedia/elocd.mmp"
medmmc_mmp="$kernel_source/kernel/eka/drivers/medmmc/medmmc.mmp"
epbussd_mmp="$kernel_source/kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/epbussd.mmp"
	if ! grep -q 'HTCLEO_FAT_LOG_SUCCESS_LOCATION_UDF' "$estart_main"; then
	if grep -q 'TInt r=fsStart.StartSystem();' "$estart_main"; then
		test -s "$retire_estart_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$retire_estart_probe_patch"
	fi
	if ! grep -q 'HtcleoWriteFatBootRecord' "$estart_main"; then
		test -s "$fat_log_writer_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$fat_log_writer_patch"
	fi
	if grep -q 'E:\\\\HTCLEO\\\\BOOTLOG.TXT' "$estart_main"; then
		test -s "$fat_log_symbian3_path_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$fat_log_symbian3_path_patch"
	fi
	if ! grep -q 'HtcleoFatLogStageResult' "$estart_main"; then
		test -s "$fat_log_result_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$fat_log_result_probe_patch"
	fi
	if grep -Fq '(void)HtcleoWriteFatBootRecord();' "$estart_main" &&
		! grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_ESTART_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_POST_STARTSYSTEM_BOUNDARY_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_STARTSYSTEM_CREATE_RESULT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test -s "$restore_fat_log_result_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$restore_fat_log_result_probe_patch"
	fi
	if grep -q 'const TInt htcleoFatLogResult=HtcleoWriteFatBootRecord();' "$estart_main" &&
		! grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_ESTART_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test -s "$post_startsystem_before_fat_writer_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$post_startsystem_before_fat_writer_probe_patch"
	fi
	if grep -q 'HTCLEO_STARTSYSTEM_CREATE_RESULT_PROBE' "$estart_source"; then
		test -s "$remove_malformed_startsystem_create_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$remove_malformed_startsystem_create_probe_patch"
	fi
	if grep -q 'HTCLEO_POST_STARTSYSTEM_BOUNDARY_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test -s "$post_run_before_startsystem_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$post_run_before_startsystem_probe_patch"
	fi
	if ! grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_ESTART_ENTRY_REGRESSION_PROBE' "$estart_main" &&
		! grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" &&
		! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test "$(grep -c '0xe7f000f0' "$estart_main")" -eq 0
		test -s "$add_post_run_before_startsystem_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$add_post_run_before_startsystem_probe_patch"
	fi
	if grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main"; then
		test -s "$drive2_read_result_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$drive2_read_result_probe_patch"
	fi
	if grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source"; then
		test -s "$drive2_pre_read_boundary_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$drive2_pre_read_boundary_probe_patch"
	fi
	if grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source"; then
		test -s "$post_removable_mount_loop_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$post_removable_mount_loop_probe_patch"
	fi
	if grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source"; then
		test -s "$mount_removable_entry_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$mount_removable_entry_probe_patch"
	fi
	if grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source"; then
		test -s "$post_local_drive_init_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$post_local_drive_init_probe_patch"
	fi
	if grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test -s "$pre_startup_init_complete_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$pre_startup_init_complete_probe_patch"
	fi
	if grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source"; then
		test -s "$post_local_drive_mapping_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$post_local_drive_mapping_probe_patch"
	fi
	if grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source"; then
		test -s "$pre_local_drive_mapping_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$pre_local_drive_mapping_probe_patch"
	fi
	if grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source"; then
		test -s "$pre_local_drive_init_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$pre_local_drive_init_probe_patch"
	fi
	if grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"; then
		test -s "$gate8_entry_regression_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$gate8_entry_regression_probe_patch"
	fi
	if grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main"; then
		test -s "$estart_entry_regression_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$estart_entry_regression_probe_patch"
	fi
	fi
	test -s "$extension_progress_probe_transform"
	python3 "$extension_progress_probe_transform" "$kernel_source"
	if ! grep -q 'HTCLEO_MMC_POST_EC0A_PARTITION_ECAPS_PROGRESS_V14\|HTCLEO_ESTART_FIRST_FAT_MOUNT_PROGRESS_V15\|HTCLEO_ESTART_FIRST_FAT_MOUNT_RETIRED_V16' "$estart_source"; then
	if ! grep -q 'HTCLEO_LOCALDRIVE_PROGRESS_V2\|HTCLEO_LOCALDRIVE_DRIVE_PROGRESS_V3\|HTCLEO_LOCALMEDIA_CAPS_PROGRESS_V4\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS_V5\|HTCLEO_MMC_INIT_PROGRESS_V6\|HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$estart_fat_progress_transform"
		python3 "$estart_fat_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_LOCALDRIVE_DRIVE_PROGRESS_V3\|HTCLEO_LOCALMEDIA_CAPS_PROGRESS_V4\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS_V5\|HTCLEO_MMC_INIT_PROGRESS_V6\|HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$estart_localdrive_progress_transform"
		python3 "$estart_localdrive_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_LOCALMEDIA_CAPS_PROGRESS_V4\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS_V5\|HTCLEO_MMC_INIT_PROGRESS_V6\|HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$estart_localdrive_drive_progress_transform"
		python3 "$estart_localdrive_drive_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_LOCALMEDIA_POWERUP_PROGRESS_V5\|HTCLEO_MMC_INIT_PROGRESS_V6\|HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$localmedia_caps_progress_transform"
		python3 "$localmedia_caps_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_INIT_PROGRESS_V6\|HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$localmedia_powerup_progress_transform"
		python3 "$localmedia_powerup_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_POST_POWERUP_PROGRESS_V7\|HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_init_progress_transform"
		python3 "$mmc_init_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8\|HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_post_powerup_progress_transform"
		python3 "$mmc_post_powerup_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_DISENGAGE_PROGRESS_V9\|HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_completion_handoff_progress_transform"
		python3 "$mmc_completion_handoff_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10\|HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_disengage_progress_transform"
		python3 "$mmc_disengage_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11\|HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_session_cleanup_progress_transform"
		python3 "$mmc_session_cleanup_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12' "$estart_source"; then
		test -s "$mmc_assp_disengage_progress_transform"
		python3 "$mmc_assp_disengage_progress_transform" "$kernel_source"
	fi
	test -s "$mmc_second_stage_media_open_progress_transform"
	python3 "$mmc_second_stage_media_open_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_ESTART_FIRST_FAT_MOUNT_PROGRESS_V15\|HTCLEO_ESTART_FIRST_FAT_MOUNT_RETIRED_V16' "$estart_source"; then
		test -s "$mmc_media_driver_partition_progress_transform"
		python3 "$mmc_media_driver_partition_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_ESTART_FIRST_FAT_MOUNT_RETIRED_V16' "$estart_source"; then
		test -s "$estart_first_fat_mount_progress_transform"
		python3 "$estart_first_fat_mount_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_FAT_MEDIA_READ_PROGRESS_V21' "$fat_cache_header"; then
		test -s "$fat_directory_cache_progress_transform"
		python3 "$fat_directory_cache_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22' "$mmc_header"; then
		test -s "$fat_media_read_progress_transform"
		python3 "$fat_media_read_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23' "$mmc_header"; then
		test -s "$fat_physical_read_progress_transform"
		python3 "$fat_physical_read_progress_transform" "$kernel_source" "$sdcc_stage_source"
	fi
	test -s "$fat_sdcc_completion_progress_transform"
	python3 "$fat_sdcc_completion_progress_transform" "$kernel_source" "$sdcc_stage_source"
	test -s "$fat_sd_finish_poll_progress_transform"
	python3 "$fat_sd_finish_poll_progress_transform" "$kernel_source" "$sdcc_stage_source"
	test -s "$sd_explicit_stop_progress_transform"
	python3 "$sd_explicit_stop_progress_transform" "$kernel_source"
	test -s "$fat_post_stop_return_progress_transform"
	python3 "$fat_post_stop_return_progress_transform" "$kernel_source"
	test -s "$fat_cache_unwind_progress_transform"
	python3 "$fat_cache_unwind_progress_transform" "$kernel_source"
	if ! grep -q 'HTCLEO_FIXED_BOOT_CAPS_RECOVERY_PROGRESS_V34' "$fat_cache_header"; then
		test -s "$fat_mount_log_boundary_progress_transform"
		python3 "$fat_mount_log_boundary_progress_transform" "$kernel_source"
		test -s "$fat_log_writer_entry_progress_transform"
		python3 "$fat_log_writer_entry_progress_transform" "$kernel_source"
		test -s "$fat_log_mount_fallback_progress_transform"
		python3 "$fat_log_mount_fallback_progress_transform" "$kernel_source"
		test -s "$fat_log_remount_recovery_progress_transform"
		python3 "$fat_log_remount_recovery_progress_transform" "$kernel_source"
		test -s "$efile_e_remount_progress_transform"
		python3 "$efile_e_remount_progress_transform" "$kernel_source"
		test -s "$efat_e_mountl_progress_transform"
		python3 "$efat_e_mountl_progress_transform" "$kernel_source"
	fi
	# V35 retains the V34 fixed-slot repair but deliberately removes every
	# V34 FB reporter.  On an already-V35 tree, rerunning the V34 transformer
	# would mistake those retired reporters for a partial install.
	if ! grep -q 'HTCLEO_KNOWN_FAT_BOOTLOG_PROGRESS_V36' "$fat_cache_header"; then
		test -s "$fixed_boot_caps_recovery_progress_transform"
		python3 "$fixed_boot_caps_recovery_progress_transform" "$kernel_source"
		test -s "$e_caps_route_progress_transform"
		python3 "$e_caps_route_progress_transform" "$kernel_source"
	fi
	# V37 replaces the V36 writer body while retaining the V36 history marker
	# in the shared header.  Do not ask the V36 verifier to find its retired
	# ESTART body on an already-V37 tree.
	if ! grep -q 'HTCLEO_ASYNC_FAT_BOOTLOG_PROGRESS_V37' "$fat_cache_header"; then
		test -s "$known_fat_bootlog_progress_transform"
		python3 "$known_fat_bootlog_progress_transform" "$kernel_source"
	fi
	# V38 keeps the V37 writer behavior but retires its ESTART checkpoints.
	# Do not rerun the V37 verifier once those FE11-FE1A sites are gone.
	if ! grep -q 'HTCLEO_EFILE_BOOTLOG_WRITE_PROGRESS_V38' "$fat_cache_header"; then
		test -s "$async_fat_bootlog_progress_transform"
		python3 "$async_fat_bootlog_progress_transform" "$kernel_source"
	fi
	# V42 retains V41's exact C: BOOTLOG attribution but retires F111-F11A.
	# Replay V40/V41 only while migrating a pre-V42 checkout; their installed
	# verifiers must not inspect a tree after V42 removes the old reporters.
	if ! grep -q 'HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS_V42' "$fat_cache_header"; then
		if ! grep -q 'HTCLEO_FAT_FIRST_WRITE_PROGRESS_V40' "$fat_cache_header"; then
			test -s "$efile_bootlog_write_progress_transform"
			python3 "$efile_bootlog_write_progress_transform" "$kernel_source"
			test -s "$efile_bootlog_write_gate_fix_transform"
			python3 "$efile_bootlog_write_gate_fix_transform" "$kernel_source"
		fi
		test -s "$fat_first_write_progress_transform"
		python3 "$fat_first_write_progress_transform" "$kernel_source"
		test -s "$fat_cluster_allocation_progress_transform"
		python3 "$fat_cluster_allocation_progress_transform" "$kernel_source"
	fi
	if ! grep -q 'HTCLEO_FAT_SYNCHRONOUS_SCAN_PROGRESS_V43' "$fat_cache_header"; then
		test -s "$fat_free_space_scanner_progress_transform"
		python3 "$fat_free_space_scanner_progress_transform" "$kernel_source"
	fi
	# V43 retires the timer-dependent V42 scanner checkpoints and selects the
	# stock synchronous FAT32 scan for C: through the HTCLEO ESTART policy.
	test -s "$fat_synchronous_scan_progress_transform"
	python3 "$fat_synchronous_scan_progress_transform" "$kernel_source"
	test -s "$loader_durable_log_transform"
	if ! grep -q 'HTCLEO_AKNCUSTCMD_LOADER_RETARGET_V1' \
		"$efile_loader_logger" 2>/dev/null; then
		python3 "$loader_durable_log_transform" "$kernel_source"
	fi
	test -s "$loader_completion_tail_transform"
	python3 "$loader_completion_tail_transform" "$kernel_source"
	test -s "$loader_akncustcmd_retarget_transform"
	python3 "$loader_akncustcmd_retarget_transform" "$kernel_source"
	test -s "$kernel_library_attach_progress_transform"
	python3 "$kernel_library_attach_progress_transform" "$kernel_source"
	test "$(grep -c 'HTCLEO_KERNEL_LIBRARY_ATTACH_PROGRESS_V3' \
		"$scodeseg_source")" -eq 1
	test "$(grep -c 'HtcleoLibraryAttachProgress(&htcleoTrace' \
		"$scodeseg_source")" -eq 10
	grep -q 'TUint32(rawMaxEps) ==' "$scodeseg_source"
	grep -q '0x484c3432u' "$scodeseg_source"
	grep -q '0x42000100u' "$scodeseg_source"
	grep -q '0xff00ffffu' "$scodeseg_source"
	grep -q '0xa0b60000u' "$scodeseg_source"
	grep -q 'phase<1u || phase>6u' "$scodeseg_source"
	test "$(grep -c 'Kern::SemaphoreSignal(\*aTrace->iNotify)' \
		"$scodeseg_source")" -eq 1
	test "$(grep -c 'Kern::SemaphoreWait(\*aTrace->iAck)' \
		"$scodeseg_source")" -eq 1
	test "$(grep -c 'ObjectFromHandle(' "$scodeseg_source")" -ge 5
	test "$(grep -c 'ESemaphore' "$scodeseg_source")" -eq 4
	for attach_failure_word in b301 b302 b303 b304; do
		grep -q "0x${attach_failure_word}0000u" "$scodeseg_source"
	done
	grep -q 'aEpList+maxEps+1' "$scodeseg_source"
	grep -q 'aEpList+maxEps+2' "$scodeseg_source"
	! grep -q 'HalFunction\|User::After\|0xe7f000f0' "$scodeseg_source"
	test "$(grep -c 'HTCLEO_LOADER_DURABLE_LOG_V1' "$efile_loader_logger")" -eq 1
	test "$(grep -c 'HTCLEO_AKNCUSTCMD_LOADER_RETARGET_V1' "$efile_loader_logger")" -eq 1
	test "$(grep -c 'HTCLEO_LOADER_COMPLETION_TAIL_V2' "$efile_ldr")" -eq 1
	test "$(grep -c 'HtcleoLoaderLog(0x000060' "$efile_ldr")" -eq 11
	test "$(grep -c 'HtcleoLoaderTraceStop();' "$efile_ldr")" -eq 1
	test "$(grep -c '^MACRO[[:space:]]*__HTCLEO_LOADER_DURABLE_LOG__' "$efile_mmp")" -eq 1
	test "$(grep -c 'SOURCE[[:space:]]*HtcleoLoaderLog.cpp' "$efile_mmp")" -eq 1
	test "$(grep -c 'C:\\\\Symbian3\\\\AKNLDR.TXT' "$efile_loader_logger")" -eq 1
	test "$(grep -c 'akncustcmds.dll' "$efile_loader_logger")" -eq 1
	test "$(grep -c 'akncustcmds.dll' "$efile_ldr")" -eq 1
	! grep -q 'C:\\\\Symbian3\\\\LDRLOG.TXT\|nvgrenderstage.dll' \
		"$efile_loader_logger" "$efile_ldr"
	test "$(grep -h -c 'HtcleoLoaderLog(0x' "$efile_ldr" "$efile_lepoc" | awk -F: '{sum += $NF} END {print sum + 0}')" -ge 80
	! grep -q 'User::After\|User::WaitForRequest' "$efile_loader_logger"
	grep -q 'gTheLoaderFs' "$efile_loader_logger"
	! grep -q 'RFs fs' "$efile_loader_logger"
	# Raptor consumes the exported platform header for the BSP, MEDMMC and
	# EPBUSSD targets.  Refresh this exact export after adding only inline
	# accessors to the ABI-stable DMMCSession spare slot.
	cmp -s "$mmc_header" "$exported_mmc_header" ||
		cp "$mmc_header" "$exported_mmc_header"
	grep -q 'HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22' "$exported_mmc_header"
	grep -q 'HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23' "$exported_mmc_header"
	grep -q 'HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24' "$exported_mmc_header"
	grep -q 'HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25' "$exported_mmc_header"
	grep -q 'HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26' "$exported_mmc_header"
	if grep -B1 'MountRemovableDrives();' "$estart_source" |
		grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__'; then
		test -s "$restore_removable_mount_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$restore_removable_mount_patch"
	fi
	if ! grep -q 'htcleoMountResult' "$estart_source" &&
		! grep -q 'htcleoDrive2CapsResult' "$estart_source"; then
		test -s "$mount_removable_result_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$mount_removable_result_probe_patch"
	fi
	if grep -q 'htcleoMountResult' "$estart_source" &&
		grep -q 'htcleoDrive2CapsResult' "$estart_source"; then
		test -s "$local_drive2_partial_cleanup_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$local_drive2_partial_cleanup_patch"
	elif grep -q 'htcleoMountResult' "$estart_source"; then
		test -s "$local_drive2_caps_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$local_drive2_caps_probe_patch"
	fi
	if grep -q 'htcleoDrive2CapsResult=htcleoCapsResult' "$estart_source"; then
		test -s "$local_drive2_stage_tag_probe_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$local_drive2_stage_tag_probe_patch"
	fi
	if ! grep -q 'EHalGroupPlatformSpecific1,0,0,0' "$estart_source"; then
		test -s "$sdcc_command_diagnostic_result_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$sdcc_command_diagnostic_result_patch"
	fi
	if ! grep -q 'htcleoDrive2.Read(0,512,htcleoSector0)' "$estart_source"; then
		test -s "$local_drive2_read_trigger_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$local_drive2_read_trigger_patch"
	fi
	if ! grep -q 'htcleoSdccDiagnostic!=0xdfe00000u' "$estart_source"; then
		test -s "$read_result_over_sentinel_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$read_result_over_sentinel_patch"
	fi
	if ! grep -q 'EHalGroupPlatformSpecific1,1,0,0' "$estart_source"; then
		test -s "$live_socket_state_result_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$live_socket_state_result_patch"
	fi
	if ! grep -q 'HTCLEO_KERNEL_EXCEPTION_SCREEN_PROBE_RETIRED_V1' "$ckernel" &&
		! grep -q 'mode==EUserMode || mode==ESvcMode' "$ckernel"; then
		test -s "$sdcc_kernel_udf_renderer_patch"
		patch --batch --forward -d "$kernel_source" -p1 < "$sdcc_kernel_udf_renderer_patch"
	fi
	if { ! grep -q 'HtcleoEstartInitCompleteFixedExceptionScreenProbe' "$ckernel" &&
		! grep -q 'HTCLEO_KERNEL_EXCEPTION_SCREEN_PROBE_RETIRED_V1' "$ckernel"; } ||
		! grep -q '__HTCLEO_LOW_ROM_PD_FIX_PROBE__' "$variant_mmh" ||
		! grep -q '__HTCLEO_LOW_ROM_PD_FIX_PROBE__' "$efile_probe_mmp" ||
		grep -q '0xef00120' "$efile_probe_cia" ||
		grep -q '0xe7f0023[4-7]\|dirProbe' "$efile_main" ||
		grep -q '0xe7f00236\|HtcleoEstartLoaderCacheStateProbe' "$efile_cache" ||
		! grep -q 'gDriveFileNamesCache\[EDriveZ\] = pDH' "$efile_cache" ||
		grep -q '0xe7f0022[1-9]\|0xe7f0023[0-3]' "$efile_ldr" ||
		grep -q 'HtcleoLoaderNakedEntry' "$efile_ldr" ||
		grep -q '__HTCLEO_LOW_ROM_PD_FIX_PROBE__\|0x4c323231u\|mov pc, r12' "$heap_hybrid" ||
		[ "$(grep -c '0xe7f000f0' "$estart_main")" -ne 1 ] ||
		[ "$(grep -c 'HtcleoWriteFatBootRecord' "$estart_main")" -ne 2 ] ||
		grep -q 'HtcleoFatLogStageResult' "$estart_main" ||
		grep -Fq '(void)HtcleoWriteFatBootRecord();' "$estart_main" ||
		! grep -q 'const TInt htcleoFatLogResult=HtcleoWriteFatBootRecord();' "$estart_main" ||
		grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main" ||
		grep -q 'TInt htcleoGate8Result=fsStart.StartSystem();' "$estart_main" ||
		grep -q 'HTCLEO_ESTART_ENTRY_REGRESSION_PROBE' "$estart_main" ||
		! grep -q 'HTCLEO_FAT_LOG_SUCCESS_LOCATION_UDF' "$estart_main" ||
		! grep -q 'sub r0,pc,#4\\n\\t.word 0xe7f000f0' "$estart_main" ||
		grep -q 'mov r0,#0' "$estart_main" ||
		! grep -q 'HTCLEO_ESTART_FAT_PROGRESS_V1' "$estart_header" ||
		! grep -q 'HTCLEO_ESTART_FIRST_FAT_MOUNT_RETIRED_V16' "$estart_source" ||
		grep -q 'HTCLEO_EFILE_CHECKMOUNT_FAT_PROGRESS_V16\|HTCLEO_EFILE_DRIVE_FAT_PROGRESS_V16' "$efile_sys" "$efile_drv" ||
		[ "$(grep -h 'HTCLEO_FAT_MEDIA_READ_PROGRESS_V21' "$fat_cache_header" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_drive_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -c 'HTCLEO_FAT_PHYSICAL_READ_SDCC_PROGRESS_V22' "$sdcc_stage_source")" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -c 'HTCLEO_FAT_SDCC_COMPLETION_SDCC_PROGRESS_V23' "$sdcc_stage_source")" -ne 2 ] ||
		[ "$(grep -h 'HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -c 'HTCLEO_FAT_SD_FINISH_POLL_SDCC_PROGRESS_V24' "$sdcc_stage_source")" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_POST_STOP_USER_RETURN_PROGRESS_V26' "$fat_cache_header" "$fat_constructor" "$fat_drive_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27' "$fat_cache_header" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_mount_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_MOUNT_LOG_BOUNDARY_PROGRESS_V28' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_LOG_WRITER_ENTRY_PROGRESS_V29' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FIXED_BOOT_CAPS_RECOVERY_PROGRESS_V34' "$fat_cache_header" "$fat_mount_source" "$locmedia_source" "$pbusmedia_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_E_CAPS_ROUTE_PROGRESS_V35' "$fat_cache_header" "$locmedia_source" "$pbusmedia_source" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_KNOWN_FAT_BOOTLOG_PROGRESS_V36' "$fat_cache_header" "$estart_main" | wc -l)" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_ASYNC_FAT_BOOTLOG_PROGRESS_V37' "$fat_cache_header" "$estart_main" | wc -l)" -ne 2 ] ||
		[ "$(grep -h 'HTCLEO_EFILE_BOOTLOG_WRITE_PROGRESS_V38' "$fat_cache_header" "$estart_main" "$efile_file" | wc -l)" -ne 3 ] ||
		[ "$(grep -h 'HTCLEO_EFILE_BOOTLOG_WRITE_GATE_FIX_V39' "$fat_cache_header" "$estart_main" "$efile_file" | wc -l)" -ne 3 ] ||
		[ "$(grep -h 'HTCLEO_FAT_FIRST_WRITE_PROGRESS_V40' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_mmp" | wc -l)" -ne 6 ] ||
		[ "$(grep -h 'HTCLEO_FAT_CLUSTER_ALLOCATION_PROGRESS_V41' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -ne 7 ] ||
		[ "$(grep -h -E 'HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS_V42([^B]|$)' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -ne 7 ] ||
		[ "$(grep -c 'HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS_V42B' "$fat_table_source")" -ne 1 ] ||
		[ "$(grep -c 'HTCLEO_FAT_SCANNER_HANDOFF_ORDER_FIX_V1' "$fat_table_source")" -ne 1 ] ||
		[ "$(grep -h 'HTCLEO_FAT_SYNCHRONOUS_SCAN_PROGRESS_V43' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -ne 7 ] ||
		grep -q 'HTCLEO_EFILE_E_REMOUNT_PROGRESS_SYS_V32\|HTCLEO_EFILE_E_REMOUNT_PROGRESS_DRV_V32' "$efile_sys" "$efile_drv" ||
		[ "$(grep -c '__HTCLEO_SD_EXPLICIT_STOP_TRANSMISSION__' "$epbussd_mmp")" -ne 1 ] ||
		grep -q 'HTCLEO_FAT_FIRST_DIRENTRY_PROGRESS_V19\|HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc0\|HTCLEO_FAT_MOUNT_PROGRESS_V17\|HTCLEO_FAT_POSTTABLE_VOLUME_PROGRESS_V18\|HTCLEO_FAT_DIRENTRY_PROGRESS(0xfb0\|HTCLEO_FAT_MOUNT_PROGRESS(0xf00\|HTCLEO_FAT_POSTTABLE_PROGRESS(0xfa0' "$fat_mount_source" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_drive_source" ||
		grep -q 'iHtcleoMountProgressPhase\|gHtcleoFirstFatMountPhase\|static volatile' "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_constructor" "$fat_cache_header" "$fat_dynamic_cache_header" "$fat_legacy_cache_source" "$fat_dynamic_cache_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" ||
		[ "$(grep -c 'THtcleoFatDirReadTrace htcleoTrace;' "$fat_constructor")" -ne 1 ] ||
		grep -q '0xfd0[1-9a]0000u' "$fat_drive_source" "$efile_ext" "$locmedia_source" "$medmmc_source" ||
		grep -q '0xfe0[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xff0[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf10[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf20[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf30[1-9a]0000u' "$fat_drive_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf40[1-9a]0000u' "$fat_drive_source" "$fat_dynamic_cache_source" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf50[1-9a]0000u' "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf60[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf70[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf80[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xf90[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xfa1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source" ||
		grep -q '0xfb1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xfc1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xfd1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		[ "$(grep -c '0xfe1[1-9a]0000u' "$estart_main")" -ne 0 ] ||
		grep -q '0xfe1[1-9a]0000u' "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xf01[1-9a]0000u' "$fat_file_source" "$fat_table_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xf11[1-9a]0000u' "$fat_file_source" "$fat_table_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xf12[1-9a]0000u' "$fat_table_source" "$fat_file_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		[ "$(grep -c '0xf13[1-9a]0000u' "$fat_table_source")" -ne 10 ] ||
		grep -q '0xf13[1-9a]0000u' "$fat_file_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q '0xff1[1-9a]0000u' "$efile_file" "$fat_file_source" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source" ||
		grep -q 'gHtcleoEstartBootlogWritePhase\|HTCLEO_EFILE_BOOTLOG_WRITE_PROGRESS(' "$efile_file" ||
		grep -q 'iHtcleoFirstWritePhase' "$fat_header" "$fat_file_source" ||
		[ "$(grep -c 'iHtcleoFirstAllocTraceArmed' "$fat_header")" -ne 1 ] ||
		[ "$(grep -c 'iHtcleoClusterAllocPhase' "$fat_header")" -ne 1 ] ||
		! grep -Fq 'Drive().DriveNumber() == EDriveC' "$fat_file_source" ||
		! grep -Fq 'aMessage.SecureId().iId == 0x10272c04u' "$fat_file_source" ||
		! grep -Fq 'aPos == 0 && aLength == 109' "$fat_file_source" ||
		grep -q 'gHtcleoLocalMediaPowerupTrace' "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" ||
		! grep -q 'iSocket->iSocketNumber == 0' "$pbusmedia_source" ||
		! grep -q 'iSocket->iState=EPBusOff;' "$pbusmedia_source" ||
		! grep -q 'iPBusState=EPBusOff;' "$pbusmedia_source" ||
		grep -q 'gHtcleoEstartERemountPhase' "$efile_sys" "$efile_drv" ||
		grep -Fq 'User::After(100000);' "$estart_main" ||
		grep -Fq 'fs.RemountDrive(' "$estart_main" ||
		grep -Fq 'fs.FileSystemName(' "$estart_main" ||
		grep -Fq 'fs.DismountFileSystem(' "$estart_main" ||
		grep -Fq 'fs.MountFileSystem(' "$estart_main" ||
		[ "$(grep -Fc 'fs.MkDirAll(KLogDir)' "$estart_main")" -ne 1 ] ||
		grep -Fq 'fs.Volume(volume,EDriveC);' "$estart_main" ||
		! grep -Fq 'fs.Volume(volume,EDriveC,volumeStatus);' "$estart_main" ||
		! grep -Fq 'User::WaitForRequest(volumeStatus);' "$estart_main" ||
		[ "$(grep -c 'htcleoTrace.iPhase = 0u;' "$fat_constructor")" -ne 1 ] ||
		[ "$(grep -c 's.FillCommandDesc(ECmdStopTransmission, 0);' "$mmc_sdcard_source")" -ne 1 ] ||
		! grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_MOUNT_PROGRESS__' "$fat_mmp" ||
		grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_FIRST_WRITE_PROGRESS__' "$fat_mmp" ||
		grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_CLUSTER_ALLOCATION_PROGRESS__' "$fat_mmp" ||
		grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS__' "$fat_mmp" ||
		! grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_SYNCHRONOUS_SCAN_PROGRESS__' "$fat_mmp" ||
		[ "$(grep -c '^\[DriveC\]$' "$htcleo_estart_config")" -ne 1 ] ||
		[ "$(grep -c '^FAT_FAT32_AsynchMount 0$' "$htcleo_estart_config")" -ne 1 ] ||
		grep -q 'FAT_FAT32_AsynchMount=' "$htcleo_estart_config" ||
		! grep -q '^ALWAYS_BUILD_AS_ARM' "$fat_mmp" ||
		grep -q 'HTCLEO_ESTART_PROGRESS(0xe100000' "$estart_main" "$estart_source" ||
		grep -q 'HTCLEO_ESTART_PROGRESS(0xe20' "$estart_main" "$estart_source" ||
		grep -q 'HTCLEO_ESTART_PROGRESS(0xe30' "$estart_main" "$estart_source" ||
		grep -q 'HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xe40' "$locmedia_source" "$medmmc_source" ||
		grep -q 'HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe50' "$locmedia_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" ||
		grep -q 'HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe60\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0' "$locmedia_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" ||
		grep -q 'HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0' "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" ||
		[ "$(grep -c 'HTCLEO_ESTART_PROGRESS(0xee0' "$estart_source")" -ne 0 ] ||
		[ "$(grep -c 'HTCLEO_EFILE_MOUNT_PROGRESS(0xee0' "$efile_sys")" -ne 0 ] ||
		[ "$(grep -c 'HTCLEO_EFILE_CHECKMOUNT_PROGRESS(0xef0' "$efile_sys")" -ne 0 ] ||
		[ "$(grep -c 'HTCLEO_EFILE_DRIVE_FAT_PROGRESS(0xef0' "$efile_drv")" -ne 0 ] ||
		grep -q 'HTCLEO_ESTART_PROGRESS(0xee0' "$estart_main" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" ||
		grep -q 'HTCLEO_EFILE_MOUNT_PROGRESS(0xee0' "$efile_main" "$efile_ldr" "$efile_cache" "$efile_drv" "$estart_main" "$estart_source" "$locmedia_source" "$medmmc_source" ||
		grep -q 'HTCLEO_EFILE_CHECKMOUNT_PROGRESS(0xef0' "$efile_main" "$efile_ldr" "$efile_cache" "$efile_drv" "$estart_main" "$estart_source" "$locmedia_source" "$medmmc_source" ||
		grep -q 'HTCLEO_EFILE_DRIVE_FAT_PROGRESS(0xef0' "$efile_main" "$efile_ldr" "$efile_cache" "$efile_sys" "$estart_main" "$estart_source" "$locmedia_source" "$medmmc_source" ||
		grep -q 'gHtcleoFirstCapsMediaOpenTrace' "$locmedia_source" ||
		grep -q 'gHtcleoFirstMmcMediaOpenTrace' "$medmmc_source" ||
		[ "$(grep -h 'HTCLEO_LOCALMEDIA_POWERUP_RETURNING_REPORTER' "$pbusmedia_source" "$spbus_source" "$mmc_stack_source" | wc -l)" -ne 3 ] ||
		[ "$(grep -c '__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__' "$elocd_mmp")" -ne 1 ] ||
		[ "$(grep -c '__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__' "$epbussd_mmp")" -ne 1 ] ||
		! grep -q 'UserSvr::HalFunction(EHalGroupPlatformSpecific1,2,' "$estart_header" ||
		! grep -q 'HTCLEO_EXTENSION_PROGRESS_LOCATION_PROBE' "$putils" ||
		[ "$(grep -c 'HtcleoExtensionProgressLocationScreenProbe(' "$putils")" -ne 4 ] ||
		[ "$(grep -c '0xa0000000u |' "$putils")" -ne 1 ] ||
		[ "$(grep -c '0xb0000000u |' "$putils")" -ne 1 ] ||
		[ "$(grep -c '0xc0000000u |' "$putils")" -ne 1 ] ||
		grep -q 'HTCLEO_POST_STARTSYSTEM_BOUNDARY_PROBE' "$estart_main" ||
		grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main" ||
		! grep -q 'C:\\\\Symbian3\\\\BOOTLOG.TXT' "$estart_main" ||
		grep -q 'E:\\\\Symbian3\\\\BOOTLOG.TXT' "$estart_main" ||
		! grep -q 'HTCLEO_FAT_LOG_V2' "$estart_main" ||
		! grep -q '^[[:space:]]*fsStart.StartSystem();' "$estart_main" ||
		grep -q 'TInt r=fsStart.StartSystem()' "$estart_main" ||
		grep -q '0xe7f0024[0-9]\|0xe7f0025[0-9]' "$estart_main" ||
		[ "$(grep -c '0xe7f000f0' "$estart_source")" -ne 0 ] ||
		grep -q 'HTCLEO_STARTSYSTEM_CREATE_RESULT_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source" ||
		grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source" ||
		[ "$(grep -c '0xe7f000f0' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp")" -ne 0 ] ||
		grep -q 'ShowEstartProgress\|DrawEstartProgressHexRow\|aFunction == 2\|0xc6400000' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		grep -q 'StopWithSdccDiagnostic\|gHtcleoSdccPostTargetDeselect' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q 'HtcleoRecordTaggedCommandResult(Session(), command.iCommand, command.iArgument' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q 'command.iCommand == 7u && TUint32(command.iArgument) == 0u' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q '? 0x0eu : 4u' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q 'KCmdProgramEnable = 1u << 11' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q 'KProgramDone = 1u << 23' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		! grep -q 'KMMCErrBusyTimeOut' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" ||
		grep -q 'htcleoMountResult' "$estart_source" ||
		! grep -q 'htcleoDrive2CapsResult' "$estart_source" ||
		! grep -q '0xca000000u' "$estart_source" ||
		! grep -q '0xcb000000u' "$estart_source" ||
		! grep -q '0xc0000000u' "$estart_source" ||
		! grep -q 'htcleoDrive2.Read(0,512,htcleoSector0)' "$estart_source" ||
		! grep -q 'htcleoSdccDiagnostic!=0xdfe00000u' "$estart_source" ||
		! grep -q 'EHalGroupPlatformSpecific1,1,0,0' "$estart_source" ||
		! grep -q 'EHalGroupPlatformSpecific1,0,0,0' "$estart_source" ||
		! grep -q '0xf0000000u)==0xd0000000u' "$estart_source" ||
		grep -q 'HtcleoEstartRunProgress\|0xe7f0024[0-9]\|0xe7f0025[0-9]' "$estart_source" ||
		! grep -q 'ROM-only bring-up has no writable hal.dat to restore' "$estart_source" ||
		! grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__' "$estart_source" ||
		! grep -q 'htcleoRomName = KServerPathSysBin()' "$estart_source" ||
		! grep -q "htcleoRomName\[0\] = (TText)'Z'" "$estart_source" ||
		! grep -q 'ws.Create(htcleoRomName,KNullDesC,TUidType())' "$estart_source" ||
		! grep -q 'TBool dmCreated=CreateServer(list,KDmManagerFileNameLit)' "$estart_source" ||
		[ "$(grep -c '0xe7f000f0' "$us_ksvr")" -ne 0 ] ||
		[ "$(grep -c '0xe7f000f0' "$efile_ldr")" -ne 0 ] ||
		[ "$(grep -c '0xe7f000f0' "$efile_cache")" -ne 0 ] ||
		! grep -B1 'r = AddNotifications()' "$efile_cache" | grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__' ||
		! grep -q 'TInt r=loader.Connect()' "$us_ksvr" ||
		! grep -q '^MACRO[[:space:]]*__HTCLEO_LOW_ROM_PD_FIX_PROBE__' "$efile_mmp" ||
		! grep -q '^FIRSTLIB[[:space:]]*htcleo_efile_low_rom_pd_fix.lib' "$efile_mmp" ||
        ! grep -q '^ALWAYS_BUILD_AS_ARM' "$efile_mmp" ||
        ! grep -q '^ALWAYS_BUILD_AS_ARM' "$estart_mmp" ||
		! grep -q '^MACRO[[:space:]]*__HTCLEO_LOW_ROM_PD_FIX_PROBE__' "$estart_mmp"; then
    if grep -q 'HtcleoHandleGate3UserEntryUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate4EfileE32MainUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate3PostTlsUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate3PostHeapUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate3HeapResultUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate3PageSizeUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate3PageSizeArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate4EfileE32MainArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate6EstartE32MainAllArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate5EfileStartupThreadAllArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate5EfilePreCreateAllArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleEfileCommonInitMidAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileCommonInitNotifierAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileCommonInitLoaderAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileInitLoaderPostCreateAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileInitLoaderPostResumeAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileInitLoaderPostWaitResultAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleEfileLoaderThreadEntryAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleSecondThreadPostHeapResultAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleSecondThreadPostTlsResultAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleRunThreadLoaderCookieAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleLoaderKernelEntryCookieAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleLoaderResumeStateAllArmUdf' "$ckernel" ||
			grep -q 'HtcleoHandleLoaderThreadCreateResultAllArmUdf' "$ckernel" ||
            grep -q 'HtcleoHandleGate7StartSystemAllArmUdf' "$ckernel" ||
            grep -q 'HtcleoEfileE32MainScreenProbe' "$efile_main" ||
            grep -q '__HTCLEO_EFILE_E32MAIN_UDF_PROBE__' "$efile_main" ||
            grep -q '^FIRSTLIB[[:space:]]*htcleo_efile_entry.lib' "$efile_mmp" ||
            grep -q '^FIRSTLIB[[:space:]]*htcleo_efile_post_tls.lib' "$efile_mmp" ||
            grep -q '^FIRSTLIB[[:space:]]*htcleo_efile_post_heap.lib' "$efile_mmp" ||
            grep -q '^FIRSTLIB[[:space:]]*htcleo_efile_heap_result.lib' "$efile_mmp"; then
		echo "ERROR: kernelhwsrv contains an intermediate probe tree; migrate it to iteration 183 first" >&2
        exit 1
    else
        git -C "$kernel_source" apply "$first_user_probe_patch"
    fi
fi

# Iteration 431 retires the final active exception-to-framebuffer path after
# all historical source migrations have converged.  The transform is
# idempotent, and touching the translation unit prevents a stale kernel object
# from retaining the old renderer.
test -s "$retire_kernel_exception_screen_transform"
python3 "$retire_kernel_exception_screen_transform" "$kernel_source"
touch "$ckernel"

mkdir -p "$output"
sh "$project/scripts/phase1-generate-aligned-linker-script.sh"

cd "$bsp_stage/baseport/htcleo"

# Clean once when crossing from the old EXSTART renderer or gate-3 FIRSTLIB.
# Raptor otherwise can retain an object whose target name did not change.
needs_clean=no
old_exstart_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/exstart_dll/armv5/$mode/exstart.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_exstart_obj" ] && \
        "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_exstart_obj" |
        grep -q 'c6400000'; then
    needs_clean=yes
fi
old_efile_map="$EPOCROOT/epoc32/release/armv5/$mode/efile.exe.map"
if [ -s "$old_efile_map" ] &&
		grep -q '/htcleo_efile_[^/]*\.lib' "$old_efile_map" &&
		! grep -q '/htcleo_efile_low_rom_pd_fix\.lib' "$old_efile_map"; then
	needs_clean=yes
fi
if [ -s "$old_efile_map" ] &&
		grep -q 'htcleo_loader_e32startup_entry' "$old_efile_map"; then
	needs_clean=yes
fi
if [ -s "$old_efile_map" ] &&
		! grep -q 'HtcleoLoaderLog' "$old_efile_map"; then
	# Adding a new EFILE translation unit changes the target graph.  Clean the
	# exact BSP build once so no pre-415 object set can survive that graph edge.
	needs_clean=yes
fi
old_heap_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_euser_dll/armv5/$mode/heap_hybrid.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_heap_obj" ] && \
        "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_heap_obj" |
        grep -q 'e3540009\|de42\|HtcleoHeapChunkResultArmProbe'; then
    needs_clean=yes
fi
if grep -q '^#define __BUILD_VARIANT_EUSER_AS_ARM__' "$bsp_stage/baseport/htcleo/variant.mmh" &&
        [ -n "$old_heap_obj" ] &&
        "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_heap_obj" |
        grep -q 'R_ARM_THM_CALL'; then
    needs_clean=yes
fi
old_euser_map="$EPOCROOT/epoc32/release/armv5/$mode/_htcleo_euser.dll.map"
if [ -s "$old_euser_map" ] && grep -q 'htcleo_heap_pre_chunk_arm' "$old_euser_map"; then
    needs_clean=yes
fi
if [ -s "$old_euser_map" ] && grep -q 'htcleo_heap_chunk_result_arm' "$old_euser_map"; then
    needs_clean=yes
fi
if [ -s "$old_euser_map" ] && grep -q 'htcleo_rchunk_pre_exec_arm' "$old_euser_map"; then
    needs_clean=yes
fi
old_sexec_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/sexec.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_sexec_obj" ] && \
        "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_sexec_obj" |
        grep -q 'HtcleoGate3ChunkCreateEntryScreenProbe'; then
    needs_clean=yes
fi
old_estart_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/e32strt_exe/armv5/$mode/estartmain.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_estart_obj" ] &&
        "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_estart_obj" |
        grep -q '48313532'; then
    needs_clean=yes
fi
old_efile_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_main.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_efile_obj" ] &&
		"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_efile_obj" |
		grep -q '48313537'; then
	needs_clean=yes
fi
old_efile_ldr_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_ldr.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_efile_ldr_obj" ] &&
		"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_efile_ldr_obj" |
		grep -q '48313631'; then
	needs_clean=yes
fi
if [ -n "$old_efile_ldr_obj" ] &&
		"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_efile_ldr_obj" |
		grep -q '4c323231'; then
	needs_clean=yes
fi
old_efile_dispatch_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/htcleo_call_thread_proc_loader_only_lib/armv5/$mode/callfirstprocessfn.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_efile_dispatch_obj" ] &&
		[ -s "$old_efile_map" ] &&
		grep -q 'htcleo_call_thread_proc_loader_only' "$old_efile_map"; then
	needs_clean=yes
fi
old_up_utl_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/_htcleo_euser_dll/armv5/$mode/up_utl.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_up_utl_obj" ] &&
		"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_up_utl_obj" |
		grep -q '4c32303[6-9]\|4c32313[0-3]\|ef00120[6-9]\|ef00121[0-3]'; then
	needs_clean=yes
fi
old_scodeseg_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/_htcleo_ekern_exe/armv5/$mode/scodeseg.o" -type f 2>/dev/null | head -n 1)
if [ -n "$old_scodeseg_obj" ]; then
	if ! "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_scodeseg_obj" |
			grep -q 'HtcleoLibraryAttachProgress' ||
			! "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_scodeseg_obj" |
			grep -q '42000100' ||
			! "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$old_scodeseg_obj" |
			grep -q 'SemaphoreWait'; then
		needs_clean=yes
	fi
fi
if [ "$needs_clean" = yes ]; then
    "$SBS_HOME/bin/sbs" \
        --configpath="$project/config" \
        -b bld.inf -c "$configuration" CLEAN \
        >"$output/clean-stale-probe-$mode.log" 2>&1
fi

set +e
"$SBS_HOME/bin/sbs" \
    --configpath="$project/config" \
    -b bld.inf \
    -c "$configuration" \
    -k -j 4 >"$log" 2>&1
rc=$?
set -e

tail -100 "$log"
if [ "$rc" -ne 0 ]; then
    exit "$rc"
fi

# epbussd.dll is a generic media component and is not part of the HTCLEO BSP
# bld.inf above.  Build it from the same patched source tree so the synchronous
# RetryGapTimerSM compatibility path is present in the binary placed in ROM.
generic_media_bldinf="$kernel_source/kernel/eka/drivers/media/bld.inf"
generic_configuration="arm.v5.$mode.gcce4_4_1.surge"
generic_log="$output/build-epbussd-$mode.log"
set +e
"$SBS_HOME/bin/sbs" \
    -b "$generic_media_bldinf" \
    -c "$generic_configuration" \
    -j 4 >"$generic_log" 2>&1
generic_rc=$?
set -e
tail -60 "$generic_log"
if [ "$generic_rc" -ne 0 ]; then
    exit "$generic_rc"
fi

# efat32.fsy is not part of the HTCLEO BSP bld.inf.  Build it explicitly from
# the same kernelhwsrv tree, and clean this one target first so an older stock
# sl_mnt32.o cannot survive a probe-only source change.
fat_configuration="arm.v5.$mode.gcce4_4_1.surge.hd2_roalign"
fat_clean_log="$output/clean-efat32-$mode.log"
fat_log="$output/build-efat32-$mode.log"
"$SBS_HOME/bin/sbs" \
    --configpath="$project/config" \
    -b "$fat_bldinf" \
    -c "$fat_configuration" CLEAN >"$fat_clean_log" 2>&1
set +e
"$SBS_HOME/bin/sbs" \
    --configpath="$project/config" \
    -b "$fat_bldinf" \
    -c "$fat_configuration" \
    -j 4 >"$fat_log" 2>&1
fat_rc=$?
set -e
tail -60 "$fat_log"
if [ "$fat_rc" -ne 0 ]; then
    exit "$fat_rc"
fi

release="$EPOCROOT/epoc32/release/armv5/$mode"
boot="$EPOCROOT/epoc32/release/armv5/_htcleo_bootloader_bootrom.bin"
for artifact in \
    "$boot" \
    "$release/_htcleo_ekern.exe" \
    "$release/exstart.dll" \
    "$release/_htcleo_kahtcleo.dll" \
    "$release/_htcleo_euser.dll" \
    "$release/_htcleo_ekdata.dll" \
    "$release/e32strt.exe" \
    "$release/efile.exe" \
	"$release/efat32.fsy" \
    "$release/_htcleo_lcd.dll" \
    "$release/_htcleo_hal.dll" \
    "$release/display.ldd" \
	"$release/_htcleo_exmoncommon.dll" \
	"$release/_htcleo_exmondebug.dll" \
	"$release/kdebug.dll" \
	"$release/_htcleo_euart1.pdd" \
	"$release/ecomm.ldd" \
	"$release/elocd.ldd" \
	"$release/_htcleo_epointer.dll" \
	"$release/_htcleo_medint.pdd" \
	"$release/_htcleo_ekeyb.dll" \
	"$release/_htcleo_soundsc.pdd" \
	"$release/esoundsc.ldd" \
	"$release/_htcleo_epbussdiov.dll" \
	"$release/epbussd.dll" \
	"$release/emmcptn.dll" \
	"$release/medmmc.pdd" \
    "$release/htcleo_sdcc_contract.lib"
do
    if [ ! -s "$artifact" ]; then
        echo "ERROR: SBS succeeded but artifact is missing or empty: $artifact" >&2
        exit 1
    fi
    sha256sum "$artifact"
done

sha256sum "$release/_htcleo_epointer.dll" \
    >"$output/htcleo-touch-$mode.sha256"
sha256sum "$release/_htcleo_kahtcleo.dll" \
    >"$output/htcleo-qsd8k-hal-variant-$mode.sha256"

# Stage-0 FAT-log foundation: compile the clean-room SDCC2 contract with the
# production GCCE configuration, but do not place the static library in ROM.
sdcc_contract="$release/htcleo_sdcc_contract.lib"
sdcc_contract_symbols="$output/htcleo-sdcc-contract-$mode.symbols"
"$SBS_GCCE441BIN/arm-none-symbianelf-nm" -g "$sdcc_contract" >"$sdcc_contract_symbols"
grep -q 'HtcleoSdccBringupCommandSupported' "$sdcc_contract_symbols"
grep -q 'HtcleoSdcc2PhysicalBase' "$sdcc_contract_symbols"

# Full Syborg-device compatibility closure: every runtime component which is
# still needed by the complete ROM must be built from a real HTCLEO/QSD8K path.
for component in \
    '../../../../os/kernelhwsrv/kernel/eka/kernel/exmoncommon' \
    'monitor/htcleo_exmondebug' \
    '../../../../os/kernelhwsrv/kernel/eka/kernel/kdebug' \
    '../../../../os/kernelhwsrv/kernel/eka/drivers/ecomm/ecomm' \
    '../../../../os/kernelhwsrv/kernel/eka/drivers/medint/medint' \
    '../../../../os/kernelhwsrv/kernel/eka/drivers/locmedia/elocd' \
    '../../../../os/kernelhwsrv/kernel/eka/drivers/soundsc/soundsc' \
    'input/htcleo_keys' \
    'input/htcleo_touch' \
    'serial/htcleo_euart' \
    'sound/htcleo_soundsc'
do
    grep -Fq "$component" "$bsp_bldinf"
done
grep -q '^#define MMC0_DRIVECOUNT 2$' "$variant_media"
grep -q '^#define MMC0_DRIVELIST  2,1$' "$variant_media"
if grep -q '^#define NVMEM1_' "$variant_media"; then
    echo "ERROR: the retired emulator NVM media definition is still active" >&2
    exit 1
fi
grep -Fq 'HtcleoClockSetRate(33u, 7372800u)' "$uart_source"
grep -Fq 'HtcleoClockEnable(33u, ETrue)' "$uart_source"
if grep -Eq 'HtcleoProcComm\((38|42)u' "$uart_source"; then
    echo "ERROR: UART retains non-QSD8K clock ProcComm opcodes" >&2
    exit 1
fi
grep -Fq 'TDalPort TheAudioPort("DSP_DAL_AQ_AUD")' "$qdsp_source"
grep -Fq 'TDalPort TheModemPort("SMD_DAL00")' "$qdsp_source"
grep -Fq 'KAudioEventBufferDone' "$qdsp_source"
grep -Fq 'KAudioBufferPhysical | KAudioBufferStart' "$qdsp_source"
grep -Fq 'KAcdbGetDeviceTable' "$qdsp_source"
grep -Fq 'KAdieAnalogOff' "$qdsp_source"
grep -Fq 'KAdieDigitalOff' "$qdsp_source"
grep -Fq 'KHeadsetAmpGpio = 157u' "$qdsp_source"
grep -Fq 'KMicBiasGpio = 158u' "$qdsp_source"
grep -Fq 'TheAudioPort.Unregister(aSession->iClient)' "$qdsp_source"
grep -Fq 'TheQdsp.ReleasePath(aSession->iRecord)' "$qdsp_source"
grep -Fq 'if (!HtcleoQdspPoll(iSession, result, bytes))' "$sound_source"
grep -Fq 'EHalGroupPlatformSpecific2, TouchDiagnosticHal, 0' "$touch_source"
grep -Fq 'EPOCALLOWDLLDATA' \
    "$bsp_stage/baseport/htcleo/input/htcleo_touch.mmp"
test "$(grep -F -c 'r != KErrNone && r != KErrTimedOut' \
    "$touch_source")" -eq 2
test "$(grep -F -c 'r != KErrNone && r != KErrTimedOut' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp")" -eq 2
grep -Fq 'void I2cWriteDelay()' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
test "$(grep -F -c 'I2cWriteDelay();' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp")" -eq 2
grep -Fq 'Kern::NanoWait(6000u)' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
grep -Fq 'if (aLength == 1)' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
grep -Fq 'TInt aAttempts' \
    "$bsp_stage/baseport/htcleo/specific/htcleo_qsd8k.h"
grep -Fq 'TUint32* aDiagnostic' \
    "$bsp_stage/baseport/htcleo/specific/htcleo_qsd8k.h"
grep -Fq 'CaptureI2cDiagnostic(aDiagnostic, 4u, status)' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
grep -Fq 'CaptureI2cDiagnostic(aDiagnostic, 5u, status)' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
grep -Fq 'KI2cLastByte | 0xffu' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"
grep -Fq 'HtcleoI2cRead(KTouchAddress, id, 4, 17, &i2cDiagnostic)' \
    "$touch_source"
grep -Fq 'HtcleoI2cRead(KTouchAddress, packet, sizeof(packet), 1,' \
    "$touch_source"
test "$(grep -F -c 'attempt < aAttempts' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp")" -eq 2
if grep -Fq 'gHtcleoI2cDiagnostic' \
        "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp"; then
    echo "ERROR: QSD8K I2C diagnostic still depends on variant DLL data" >&2
    exit 1
fi
grep -Fq 'gHtcleoTouchSamples' "$touch_source"
grep -Fq 'gHtcleoTouchEvents' "$touch_source"
for touch_stage in \
    54000001 54000002 \
    54000100 54000101 54000102 54000103 54000104 54000106 54000107 \
    54000108 54000109 \
    54000201 54000202 54000203 \
    54000300 54000301 54000302 54000304 54000307 \
    54000401 54000402 54000403 54000404 54000405 \
    54000501 54000502 54000503
do
    test "$(grep -c "0x${touch_stage}u" "$touch_source")" -eq 1
done
test "$(grep -c '0x54000200u' "$touch_source")" -eq 2
test "$(grep -c 'Kern::AddEvent(event)' "$touch_source")" -eq 2
grep -Fq 'TInt ResetPanelOnce(TInt aCycle, TBool& aIrqLow);' "$touch_source"
grep -Fq 'for (TInt cycle = 0; cycle < 3; ++cycle)' "$touch_source"
grep -Fq 'for (TInt i = 0; i < 50; ++i)' "$touch_source"
grep -Fq 'iPollDfc.SetDfcQ(Kern::DfcQue0());' "$touch_source"
grep -Fq 'const TInt timerResult = iTimer.OneShot(KTouchPollTicks, iPollDfc);' \
    "$touch_source"
test "$(grep -F -c 'self->Sample();' "$touch_source")" -eq 3
grep -Fq 'HTCLEO_TYPE2A_HIGH_LEVEL_FALLBACK_V1' "$touch_source"
grep -Fq 'KTouchHighFallbackPolls = 10u' "$touch_source"
grep -Fq 'gHtcleoTouchEvents != eventsBefore' "$touch_source"
grep -Fq 'gHtcleoTouchRawTransitions != transitionsBefore' "$touch_source"
grep -Fq 'gHtcleoTouchPoints != 0u' "$touch_source"
grep -Fq 'HTCLEO_TYPE2A_IRQ_READY_GATED_POLL_V1' "$touch_source"
grep -Fq 'HtcleoGpioRead(92u, irqHigh)' "$touch_source"
grep -Fq 'else if (!irqHigh)' "$touch_source"
grep -Fq 'gHtcleoTouchReadyReads' "$touch_source"
grep -Fq 'gHtcleoTouchNotReadySkips' "$touch_source"
grep -Fq 'HTCLEO_TYPE2A_FOCUS_REARM_DELAYED_V2' "$touch_source"
grep -Fq 'KTouchFocusRearmDelayPolls = 25u' "$touch_source"
grep -Fq 'gHtcleoTouchRearmPending' "$touch_source"
grep -Fq 'gHtcleoTouchRearmDelay' "$touch_source"
if grep -Fq 'if (self->iPointerOn)' "$touch_source"; then
    echo "ERROR: touchscreen sampling is still gated by cursor visibility" >&2
    exit 1
fi
grep -Fq 'TInt timerResult = self->iTimer.Again(KTouchPollTicks);' \
    "$touch_source"
grep -Fq 'timerResult = self->iTimer.OneShot(KTouchPollTicks,' \
    "$touch_source"
grep -Fq 'EGptDivider = 0x20' \
    "$bsp_stage/baseport/htcleo/specific/htcleo.h"
grep -Fq 'WriteReg(KHwBaseCsr, EGptDivider, 3u);' \
    "$bsp_stage/baseport/htcleo/specific/assp.cpp"
grep -Fq 'HtcleoTouchBeforeFirstSample()' "$touch_source"
grep -Fq 'HtcleoTouchVicState()' "$touch_source"
grep -Fq 'HtcleoTouchGptState()' "$touch_source"
grep -Fq 'static_cast<TInt>(NKern::TickCount())' "$touch_source"
grep -Fq 'EVicRawStatus0   = 0x0a0' \
    "$bsp_stage/baseport/htcleo/specific/htcleo.h"
grep -Fq 'EVicIrqVectorPending = 0x0d4' \
    "$bsp_stage/baseport/htcleo/specific/htcleo.h"
grep -Fq 'asm("ldr r5, [r4, #208]");' \
    "$bsp_stage/baseport/htcleo/specific/interrupts.cia"
grep -Fq 'asm("ldr r5, [r4, #212]");' \
    "$bsp_stage/baseport/htcleo/specific/interrupts.cia"
grep -Fq 'ACK an edge before running its handler' \
    "$bsp_stage/baseport/htcleo/specific/interrupts.cia"
grep -Fq 'asm("Dispatch:");' \
    "$bsp_stage/baseport/htcleo/specific/interrupts.cia"
grep -Fq 'asm("adr lr, Dispatch");' \
    "$bsp_stage/baseport/htcleo/specific/interrupts.cia"
if grep -Fq 'asm("adr lr, Clear");' \
        "$bsp_stage/baseport/htcleo/specific/interrupts.cia"; then
    echo "ERROR: VIC edge ACK still occurs after the device handler" >&2
    exit 1
fi
if grep -Fq 'asm("adr lr, Return");' \
        "$bsp_stage/baseport/htcleo/specific/interrupts.cia"; then
    echo "ERROR: VIC dispatcher still exits after only one vector" >&2
    exit 1
fi
test "$(grep -F -c 'const TUint32 transferDiagnostic =' \
    "$bsp_stage/baseport/htcleo/specific/qsd8k_hal.cpp")" -eq 2
if sed -n '/void DDriverHtcleoSoundScPdd::TimerExpired/,/^    }/p' "$sound_source" |
        grep -Eq 'PlayCallback|RecordCallback'; then
    echo "ERROR: SoundSc timer fabricates a successful hardware completion" >&2
    exit 1
fi
if grep -RniE 'virtio|syborg' "$bsp_stage/baseport/htcleo/sound"; then
    echo "ERROR: SoundSc/QDSP source still depends on an emulator transport" >&2
    exit 1
fi

# Fail closed unless the build retains the registered ROM-only bypasses, one
# returning shared extension-progress reporter and one final ESTART UDF. The
# source-built SSM rendezvous repair is audited by the complete-ROM build.
objdump="$SBS_GCCE441BIN/arm-none-symbianelf-objdump"
exstart_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/exstart_dll/armv5/$mode/exstart.o" -type f | head -n 1)
estart_main_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/e32strt_exe/armv5/$mode/estartmain.o" -type f | head -n 1)
estart_init_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/e32strt_exe/armv5/$mode/estart.o" -type f | head -n 1)
efile_main_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_main.o" -type f | head -n 1)
efile_sys_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_sys.o" -type f | head -n 1)
efile_drv_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_drv.o" -type f | head -n 1)
efile_file_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_file.o" -type f | head -n 1)
efile_ext_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_ext.o" -type f | head -n 1)
efile_ldr_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_ldr.o" -type f | head -n 1)
efile_lepoc_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_lepoc.o" -type f | head -n 1)
efile_loader_logger_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/HtcleoLoaderLog.o" -type f | head -n 1)
efile_cache_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/efile_exe/armv5/$mode/sf_cache.o" -type f | head -n 1)
efile_entry_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/eexe_lib/armv5/$mode/uc_exe_.o" -type f | head -n 1)
efile_custom_runthread_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/htcleo_efile_low_rom_pd_fix_lib/armv5/$mode/uc_exe.o" -type f | head -n 1)
efile_dispatch_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/htcleo_efile_low_rom_pd_fix_lib/armv5/$mode/callfirstprocessfn.o" -type f | head -n 1)
efile_custom_entry_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/htcleo_efile_low_rom_pd_fix_lib/armv5/$mode/htcleo_efile_heap_result_.o" -type f | head -n 1)
stock_runthread_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/eexe_lib/armv5/$mode/uc_exe.o" -type f | head -n 1)
heap_hybrid_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_euser_dll/armv5/$mode/heap_hybrid.o" -type f | head -n 1)
up_utl_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/_htcleo_euser_dll/armv5/$mode/up_utl.o" -type f | head -n 1)
ckernel_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/ckernel.o" -type f | head -n 1)
putils_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/putils.o" -type f | head -n 1)
ckernel_cia_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/ckernel_.o" -type f | head -n 1)
vectors_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/vectors*.o" -type f | head -n 1)
sexec_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_ekern_exe/armv5/$mode/sexec.o" -type f | head -n 1)
scodeseg_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/_htcleo_ekern_exe/armv5/$mode/scodeseg.o" -type f | head -n 1)
us_ksvr_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_euser_dll/armv5/$mode/us_ksvr.o" -type f | head -n 1)
lcd_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_lcd_dll/armv5/$mode/htcleo_display.o" -type f | head -n 1)
sdcc_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path "*/_htcleo_epbussdiov_dll/armv5/$mode/htcleo_sdcc.o" -type f | head -n 1)
generic_stack_obj=$(find "$EPOCROOT/epoc32/build/media" \
    -path "*/epbussd_dll/armv5/$mode/stack.o" -type f | head -n 1)
generic_session_obj=$(find "$EPOCROOT/epoc32/build/media" \
    -path "*/epbussd_dll/armv5/$mode/session.o" -type f | head -n 1)
generic_sdcard_obj=$(find "$EPOCROOT/epoc32/build/media" \
    -path "*/epbussd_dll/armv5/$mode/sdcard.o" -type f | head -n 1)
locmedia_obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
	-path "*/elocd_ldd/armv5/$mode/locmedia.o" -type f | head -n 1)
medmmc_obj=$(find "$EPOCROOT/epoc32/build/media" \
	-path "*/medmmc_pdd/armv5/$mode/medmmc.o" -type f | head -n 1)
pbusmedia_obj=$(find "$EPOCROOT/epoc32/build/media" \
	-path "*/epbussd_dll/armv5/$mode/pbusmedia.o" -type f | head -n 1)
spbus_obj=$(find "$EPOCROOT/epoc32/build/media" \
	-path "*/epbussd_dll/armv5/$mode/spbus.o" -type f | head -n 1)
# sfat32 can retain an object tree generated by an older MMP/config hash.
# Always audit the object produced by the build immediately above instead of
# whichever hash directory happens to sort first.
fat_mount_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_mnt32.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_common_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_mnt.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_dynamic_cache_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_dir_cache.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_legacy_cache_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_cache.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_drive_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_drv.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_file_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/sl_file.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
fat_table_obj=$(find "$EPOCROOT/epoc32/build/sfat32" \
	-path "*/efat32_fsy/armv5/$mode/fat_table32.o" -type f \
	-printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
test -n "$exstart_obj" && test -s "$exstart_obj"
test -n "$estart_main_obj" && test -s "$estart_main_obj"
test -n "$estart_init_obj" && test -s "$estart_init_obj"
test -n "$efile_main_obj" && test -s "$efile_main_obj"
test -n "$efile_sys_obj" && test -s "$efile_sys_obj"
test -n "$efile_drv_obj" && test -s "$efile_drv_obj"
test -n "$efile_file_obj" && test -s "$efile_file_obj"
test -n "$efile_ext_obj" && test -s "$efile_ext_obj"
test -n "$efile_ldr_obj" && test -s "$efile_ldr_obj"
test -n "$efile_lepoc_obj" && test -s "$efile_lepoc_obj"
test -n "$efile_loader_logger_obj" && test -s "$efile_loader_logger_obj"
test -n "$efile_cache_obj" && test -s "$efile_cache_obj"
test -n "$efile_entry_obj" && test -s "$efile_entry_obj"
test -n "$efile_custom_runthread_obj" && test -s "$efile_custom_runthread_obj"
test -n "$efile_dispatch_obj" && test -s "$efile_dispatch_obj"
test -n "$efile_custom_entry_obj" && test -s "$efile_custom_entry_obj"
test -n "$stock_runthread_obj" && test -s "$stock_runthread_obj"
test -n "$heap_hybrid_obj" && test -s "$heap_hybrid_obj"
test -n "$up_utl_obj" && test -s "$up_utl_obj"
test -n "$ckernel_obj" && test -s "$ckernel_obj"
test -n "$putils_obj" && test -s "$putils_obj"
test -n "$ckernel_cia_obj" && test -s "$ckernel_cia_obj"
test -n "$vectors_obj" && test -s "$vectors_obj"
test -n "$sexec_obj" && test -s "$sexec_obj"
test -n "$scodeseg_obj" && test -s "$scodeseg_obj"
test -n "$us_ksvr_obj" && test -s "$us_ksvr_obj"
test -n "$lcd_obj" && test -s "$lcd_obj"
test -n "$sdcc_obj" && test -s "$sdcc_obj"
test -n "$generic_stack_obj" && test -s "$generic_stack_obj"
test -n "$generic_session_obj" && test -s "$generic_session_obj"
test -n "$generic_sdcard_obj" && test -s "$generic_sdcard_obj"
test -n "$locmedia_obj" && test -s "$locmedia_obj"
test -n "$medmmc_obj" && test -s "$medmmc_obj"
test -n "$pbusmedia_obj" && test -s "$pbusmedia_obj"
test -n "$spbus_obj" && test -s "$spbus_obj"
test -n "$fat_mount_obj" && test -s "$fat_mount_obj"
test -n "$fat_common_obj" && test -s "$fat_common_obj"
test -n "$fat_dynamic_cache_obj" && test -s "$fat_dynamic_cache_obj"
test -n "$fat_legacy_cache_obj" && test -s "$fat_legacy_cache_obj"
test -n "$fat_drive_obj" && test -s "$fat_drive_obj"
test -n "$fat_file_obj" && test -s "$fat_file_obj"
test -n "$fat_table_obj" && test -s "$fat_table_obj"

exstart_disasm="$output/exstart-no-screen-probe-$mode.disasm"
estart_main_disasm="$output/estart-fat-log-result-probe-$mode.disasm"
estart_init_disasm="$output/estart-no-returning-checkmount-fat-progress-$mode.disasm"
efile_main_disasm="$output/efile-stock-startupthread-l302-$mode.disasm"
efile_sys_disasm="$output/efile-checkmount-cache-progress-$mode.disasm"
efile_drv_disasm="$output/efile-drive-fat-progress-$mode.disasm"
efile_file_disasm="$output/efile-no-bootlog-write-progress-$mode.disasm"
efile_ldr_disasm="$output/efile-loader-no-probe-l302-$mode.disasm"
efile_loader_log_disasm="$output/efile-loader-durable-log-$mode.disasm"
efile_loader_image_log_disasm="$output/efile-loader-image-durable-log-$mode.disasm"
efile_loader_logger_disasm="$output/efile-loader-logger-$mode.disasm"
efile_cache_disasm="$output/efile-checkloadercacheinit-addnotifications-bypass-no-probe-l302-$mode.disasm"
efile_initloader_disasm="$output/efile-stock-initloader-l302-$mode.disasm"
efile_entry_disasm="$output/efile-stock-entry-$mode.disasm"
efile_custom_runthread_disasm="$output/euser-loader-runthread-stock-custom-lib-$mode.disasm"
efile_dispatch_disasm="$output/euser-stock-call-thread-proc-all-arm-$mode.disasm"
efile_custom_entry_disasm="$output/euser-loader-stock-entry-l302-$mode.disasm"
stock_runthread_disasm="$output/euser-stock-runthread-$mode.disasm"
heap_hybrid_disasm="$output/euser-stock-heap-l302-$mode.disasm"
up_utl_disasm="$output/euser-stock-setupthreadheap-l302-$mode.disasm"
ckernel_disasm="$output/ckernel-exception-screen-retired-$mode.disasm"
putils_disasm="$output/putils-extension-progress-location-$mode.disasm"
ckernel_cia_disasm="$output/ckernel-stock-thread-handoff-$mode.disasm"
vectors_disasm="$output/vectors-stock-swi-low-rom-pd-fix-$mode.disasm"
sexec_disasm="$output/sexec-stock-threadcreate-resume-$mode.disasm"
scodeseg_disasm="$output/scodeseg-library-attach-progress-$mode.disasm"
us_ksvr_disasm="$output/euser-rloader-stock-no-probe-l302-$mode.disasm"
lcd_disasm="$output/lcd-allocate-$mode.disasm"
sdcc_disasm="$output/sdcc-fat-physical-read-progress-$mode.disasm"
generic_stack_disasm="$output/epbussd-stack-fat-physical-read-progress-$mode.disasm"
generic_session_disasm="$output/epbussd-session-fat-physical-read-progress-$mode.disasm"
generic_sdcard_disasm="$output/epbussd-sdcard-fat-physical-read-progress-$mode.disasm"
generic_retrygap_disasm="$output/epbussd-retry-gap-only-$mode.disasm"
generic_pollgap_disasm="$output/epbussd-poll-gap-only-$mode.disasm"
generic_program_disasm="$output/epbussd-program-timer-only-$mode.disasm"
locmedia_powerup_disasm="$output/elocd-tagged-fat-media-read-$mode.disasm"
medmmc_progress_disasm="$output/medmmc-fat-physical-read-progress-$mode.disasm"
pbusmedia_progress_disasm="$output/epbussd-pbusmedia-fixed-boot-caps-progress-$mode.disasm"
efile_media_read_disasm="$output/efile-tagged-fat-media-read-$mode.disasm"
fat_mount_specific_disasm="$output/efat32-directory-cache-mount32-support-$mode.disasm"
fat_mount_common_disasm="$output/efat32-directory-cache-mount-progress-$mode.disasm"
fat_dynamic_cache_disasm="$output/efat32-directory-cache-dynamic-progress-$mode.disasm"
fat_legacy_cache_disasm="$output/efat32-directory-cache-legacy-support-$mode.disasm"
fat_drive_disasm="$output/efat32-tagged-media-read-$mode.disasm"
fat_file_disasm="$output/efat32-no-first-write-progress-$mode.disasm"
fat_table_disasm="$output/efat32-synchronous-free-space-scan-progress-$mode.disasm"
fat_mount_disasm="$output/tagged-fat-physical-read-progress-$mode.disasm"
"$objdump" -dr "$exstart_obj" >"$exstart_disasm"
"$objdump" -dr "$estart_main_obj" >"$estart_main_disasm"
"$objdump" -dr "$estart_init_obj" >"$estart_init_disasm"
"$objdump" -dr "$efile_main_obj" >"$efile_main_disasm"
"$objdump" -dr "$efile_sys_obj" >"$efile_sys_disasm"
"$objdump" -dr "$efile_drv_obj" >"$efile_drv_disasm"
"$objdump" -dr "$efile_file_obj" >"$efile_file_disasm"
"$objdump" -dr "$efile_ext_obj" >"$efile_media_read_disasm"
"$objdump" -dr "$efile_ldr_obj" >"$efile_ldr_disasm"
cp "$efile_ldr_disasm" "$efile_loader_log_disasm"
"$objdump" -dr "$efile_lepoc_obj" >"$efile_loader_image_log_disasm"
"$objdump" -dr "$efile_loader_logger_obj" >"$efile_loader_logger_disasm"
"$objdump" -dr "$efile_cache_obj" >"$efile_cache_disasm"
grep -q 'HtcleoLoaderLog' "$efile_loader_log_disasm"
grep -q 'HtcleoLoaderLog' "$efile_loader_image_log_disasm"
test "$(grep -h -c 'R_ARM_.*CALL.*HtcleoLoaderLog' \
    "$efile_loader_log_disasm" "$efile_loader_image_log_disasm" | \
    awk '{sum += $1} END {print sum + 0}')" -ge 80
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$efile_loader_logger_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$efile_loader_logger_disasm"
strings "$efile_loader_logger_obj" | grep -q 'HTCLEO_LDR '
strings "$efile_loader_logger_obj" | grep -Fq 'akncustcmds.dll'
strings "$efile_ldr_obj" | grep -Fq 'akncustcmds.dll'
strings -el "$efile_loader_logger_obj" | grep -Fq 'C:\Symbian3\AKNLDR.TXT'
test "$(grep -h -c 'e7f000f0' "$efile_loader_log_disasm" \
    "$efile_loader_image_log_disasm" "$efile_loader_logger_disasm" | \
    awk '{sum += $1} END {print sum + 0}')" -eq 0
sha256sum "$release/efile.exe" >"$output/efile-$mode.sha256"
sha256sum "$efile_ldr_obj" >"$output/efile-loader-dispatch-$mode.sha256"
sha256sum "$efile_lepoc_obj" >"$output/efile-loader-image-$mode.sha256"
sha256sum "$efile_loader_logger_obj" >"$output/efile-loader-logger-$mode.sha256"
sed -n '/<_Z10InitLoaderv>:/,/^$/p' "$efile_ldr_disasm" >"$efile_initloader_disasm"
"$objdump" -dr "$efile_entry_obj" >"$efile_entry_disasm"
"$objdump" -dr "$efile_custom_runthread_obj" >"$efile_custom_runthread_disasm"
"$objdump" -dr "$efile_dispatch_obj" >"$efile_dispatch_disasm"
"$objdump" -dr "$efile_custom_entry_obj" >"$efile_custom_entry_disasm"
"$objdump" -dr "$stock_runthread_obj" >"$stock_runthread_disasm"
"$objdump" -dr "$heap_hybrid_obj" >"$heap_hybrid_disasm"
"$objdump" -dr "$up_utl_obj" >"$up_utl_disasm"
"$objdump" -dr "$ckernel_obj" >"$ckernel_disasm"
"$objdump" -dr "$putils_obj" >"$putils_disasm"
"$objdump" -dr "$ckernel_cia_obj" >"$ckernel_cia_disasm"
"$objdump" -dr "$vectors_obj" >"$vectors_disasm"
"$objdump" -dr "$sexec_obj" >"$sexec_disasm"
"$objdump" -dr "$scodeseg_obj" >"$scodeseg_disasm"
grep -q 'HtcleoLibraryAttachProgress' "$scodeseg_disasm"
test "$(grep -c 'bl.*HtcleoLibraryAttachProgress' "$scodeseg_disasm")" -eq 10
grep -q 'HtcleoLibraryAttachExchange' "$scodeseg_disasm"
grep -q '42000100' "$scodeseg_disasm"
grep -q 'a0b60000' "$scodeseg_disasm"
grep -q 'KUSafeWrite' "$scodeseg_disasm"
grep -q 'SemaphoreSignal' "$scodeseg_disasm"
grep -q 'SemaphoreWait' "$scodeseg_disasm"
grep -q 'ObjectFromHandle' "$scodeseg_disasm"
grep -q 'ExecHandler.*LibraryAttach' "$scodeseg_disasm"
if grep -q 'e7f000f0' "$scodeseg_disasm"; then
	echo "ERROR: LibraryAttach progress object contains a display UDF" >&2
	exit 1
fi
sha256sum "$scodeseg_obj" >"$output/scodeseg-library-attach-progress-$mode.sha256"
"$objdump" -dr "$us_ksvr_obj" >"$us_ksvr_disasm"
"$objdump" -dr "$lcd_obj" |
    sed -n '/AllocateFrameBufferEv>:/,/^$/p' >"$lcd_disasm"
"$objdump" -dr "$sdcc_obj" >"$sdcc_disasm"
"$objdump" -dr -C "$generic_stack_obj" >"$generic_stack_disasm"
"$objdump" -dr -C "$generic_session_obj" >"$generic_session_disasm"
"$objdump" -dr -C "$generic_sdcard_obj" >"$generic_sdcard_disasm"
"$objdump" -dr "$locmedia_obj" >"$locmedia_powerup_disasm"
"$objdump" -dr "$medmmc_obj" >"$medmmc_progress_disasm"
"$objdump" -dr "$pbusmedia_obj" >"$pbusmedia_progress_disasm"
"$objdump" -dr "$fat_mount_obj" >"$fat_mount_specific_disasm"
"$objdump" -dr "$fat_common_obj" >"$fat_mount_common_disasm"
"$objdump" -dr "$fat_dynamic_cache_obj" >"$fat_dynamic_cache_disasm"
"$objdump" -dr "$fat_legacy_cache_obj" >"$fat_legacy_cache_disasm"
"$objdump" -dr "$fat_drive_obj" >"$fat_drive_disasm"
"$objdump" -dr "$fat_file_obj" >"$fat_file_disasm"
"$objdump" -dr "$fat_table_obj" >"$fat_table_disasm"
cat "$fat_mount_common_disasm" "$fat_mount_specific_disasm" \
    >"$fat_mount_disasm"
{
    sed -n '/<DMMCStack::RetryGapTimerSM()>:/,/^$/p' "$generic_stack_disasm"
    sed -n '/<DMMCStack::RetryGapTimerSMST(void\*)>:/,/^$/p' "$generic_stack_disasm"
} >"$generic_retrygap_disasm"
{
    sed -n '/<DMMCStack::PollGapTimerSM()>:/,/^$/p' "$generic_stack_disasm"
    sed -n '/<DMMCStack::PollGapTimerSMST(void\*)>:/,/^$/p' "$generic_stack_disasm"
} >"$generic_pollgap_disasm"
{
    sed -n '/<DMMCStack::ProgramTimerSM()>:/,/^$/p' "$generic_stack_disasm"
    sed -n '/<DMMCStack::ProgramTimerSMST(void\*)>:/,/^$/p' "$generic_stack_disasm"
} >"$generic_program_disasm"
test -s "$generic_retrygap_disasm"
grep -q 'Kern::NanoWait' "$generic_retrygap_disasm"
if grep -q 'NTimer::OneShot' "$generic_retrygap_disasm"; then
    echo "ERROR: rebuilt epbussd still contains asynchronous RetryGapTimerSM" >&2
    exit 1
fi
test -s "$generic_pollgap_disasm"
grep -q 'Kern::NanoWait' "$generic_pollgap_disasm"
if grep -q 'NTimer::OneShot' "$generic_pollgap_disasm"; then
    echo "ERROR: rebuilt epbussd still contains asynchronous PollGapTimerSM" >&2
    exit 1
fi
test -s "$generic_program_disasm"
grep -q 'Kern::NanoWait' "$generic_program_disasm"
if grep -q 'NTimer::OneShot' "$generic_program_disasm"; then
    echo "ERROR: rebuilt epbussd still contains asynchronous ProgramTimerSM" >&2
    exit 1
fi
sha256sum "$release/epbussd.dll" >"$output/epbussd-$mode.sha256"

if grep -q 'c6400000' "$exstart_disasm"; then
    echo "ERROR: iteration-135 EXSTART screen renderer remains in gate-6 build" >&2
    exit 1
fi
if grep -q 'de44\|48313531\|HtcleoGate4ArmProbe' "$efile_main_disasm"; then
    echo "ERROR: EFILE retains an older gate-4 probe" >&2
    exit 1
fi
grep -q '<_Z7E32Mainv>:' "$efile_main_disasm"
grep -A2 '<_Z7E32Mainv>:' "$efile_main_disasm" | grep -q 'e1a0c00d'
if grep -q 'e7f000f0\|48313537\|e7f0022[1-9]\|e7f0023[0-9]\|e7f0024[0-9]' "$efile_main_disasm"; then
	echo "ERROR: iteration-262 EFILE main contains a stale probe" >&2
	exit 1
fi
if grep -q 'e7f0022[1-9]\|e7f0023[0-9]\|e7f0024[0-9]\|HtcleoEstartLoaderCacheStateProbe' "$efile_cache_disasm"; then
	echo "ERROR: iteration-262 cache object contains a stale probe" >&2
	exit 1
fi
grep -q '<_Z10InitLoaderv>:' "$efile_ldr_disasm"
grep -A2 '<_Z10InitLoaderv>:' "$efile_ldr_disasm" | grep -q 'e1a0c00d'
if grep -q '48313631' "$efile_ldr_disasm"; then
	echo "ERROR: iteration-161 LoaderThread entry probe remains active" >&2
	exit 1
fi
grep -q 'LoaderThread' "$efile_initloader_disasm"
grep -q 'RThread.*Create' "$efile_initloader_disasm"
if grep -q '4c323231\|e7f0022[1-9]\|e7f0023[0-3]' "$efile_initloader_disasm"; then
	echo "ERROR: iteration-262 InitLoader/LoaderThread path is not stock" >&2
	exit 1
fi
grep -q '<_Z13StartupThreadPv>:' "$efile_main_disasm"
grep -A2 '<_Z13StartupThreadPv>:' "$efile_main_disasm" | grep -q 'e1a0c00d'
grep -q '<_Z7E32Mainv>:' "$estart_main_disasm"
grep -A2 '<_Z7E32Mainv>:' "$estart_main_disasm" | grep -q 'e1a0c00d'
test "$(grep -c 'e7f000f0' "$estart_main_disasm")" -eq 1
! grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main"
! grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main"
! grep -q 'TInt htcleoGate8Result=fsStart.StartSystem();' "$estart_main"
	grep -q 'HTCLEO_FAT_LOG_SUCCESS_LOCATION_UDF' "$estart_main"
	grep -q 'sub r0,pc,#4\\n\\t.word 0xe7f000f0' "$estart_main"
	! grep -q 'mov r0,#0' "$estart_main"
	grep -q 'e24f0004' "$estart_main_disasm"
	grep -q 'HTCLEO_ESTART_FAT_PROGRESS_V1' "$estart_header"
	grep -q 'HTCLEO_ESTART_FIRST_FAT_MOUNT_RETIRED_V16' "$estart_source"
	! grep -q 'HTCLEO_EFILE_CHECKMOUNT_FAT_PROGRESS_V16\|HTCLEO_EFILE_DRIVE_FAT_PROGRESS_V16' "$efile_sys" "$efile_drv"
	test "$(grep -h 'HTCLEO_FAT_MEDIA_READ_PROGRESS_V21' "$fat_cache_header" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_drive_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -eq 1
	test "$(grep -c 'HTCLEO_FAT_PHYSICAL_READ_SDCC_PROGRESS_V22' "$sdcc_stage_source")" -eq 1
	test "$(grep -h 'HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -eq 1
	test "$(grep -c 'HTCLEO_FAT_SDCC_COMPLETION_SDCC_PROGRESS_V23' "$sdcc_stage_source")" -eq 2
	test "$(grep -h 'HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -eq 1
	test "$(grep -c 'HTCLEO_FAT_SD_FINISH_POLL_SDCC_PROGRESS_V24' "$sdcc_stage_source")" -eq 1
	test "$(grep -h 'HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26' "$mmc_header" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_POST_STOP_USER_RETURN_PROGRESS_V26' "$fat_cache_header" "$fat_constructor" "$fat_drive_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27' "$fat_cache_header" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_mount_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_MOUNT_LOG_BOUNDARY_PROGRESS_V28' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_LOG_WRITER_ENTRY_PROGRESS_V29' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33' "$fat_cache_header" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_FIXED_BOOT_CAPS_RECOVERY_PROGRESS_V34' "$fat_cache_header" "$fat_mount_source" "$locmedia_source" "$pbusmedia_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_E_CAPS_ROUTE_PROGRESS_V35' "$fat_cache_header" "$locmedia_source" "$pbusmedia_source" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_KNOWN_FAT_BOOTLOG_PROGRESS_V36' "$fat_cache_header" "$estart_main" | wc -l)" -eq 1
	test "$(grep -h 'HTCLEO_ASYNC_FAT_BOOTLOG_PROGRESS_V37' "$fat_cache_header" "$estart_main" | wc -l)" -eq 2
	test "$(grep -h 'HTCLEO_EFILE_BOOTLOG_WRITE_PROGRESS_V38' "$fat_cache_header" "$estart_main" "$efile_file" | wc -l)" -eq 3
	test "$(grep -h 'HTCLEO_EFILE_BOOTLOG_WRITE_GATE_FIX_V39' "$fat_cache_header" "$estart_main" "$efile_file" | wc -l)" -eq 3
	test "$(grep -h 'HTCLEO_FAT_FIRST_WRITE_PROGRESS_V40' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_mmp" | wc -l)" -eq 6
	test "$(grep -h 'HTCLEO_FAT_CLUSTER_ALLOCATION_PROGRESS_V41' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -eq 7
	test "$(grep -h -E 'HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS_V42([^B]|$)' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -eq 7
	test "$(grep -c 'HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS_V42B' "$fat_table_source")" -eq 1
	test "$(grep -c 'HTCLEO_FAT_SCANNER_HANDOFF_ORDER_FIX_V1' "$fat_table_source")" -eq 1
	test "$(grep -h 'HTCLEO_FAT_SYNCHRONOUS_SCAN_PROGRESS_V43' "$fat_cache_header" "$estart_main" "$efile_file" "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_mmp" | wc -l)" -eq 7
	! grep -q 'HTCLEO_EFILE_E_REMOUNT_PROGRESS_SYS_V32\|HTCLEO_EFILE_E_REMOUNT_PROGRESS_DRV_V32' "$efile_sys" "$efile_drv"
	test "$(grep -c '__HTCLEO_SD_EXPLICIT_STOP_TRANSMISSION__' "$epbussd_mmp")" -eq 1
	! grep -q 'HTCLEO_FAT_FIRST_DIRENTRY_PROGRESS_V19\|HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc0\|HTCLEO_FAT_MOUNT_PROGRESS_V17\|HTCLEO_FAT_POSTTABLE_VOLUME_PROGRESS_V18\|HTCLEO_FAT_DIRENTRY_PROGRESS(0xfb0\|HTCLEO_FAT_MOUNT_PROGRESS(0xf00\|HTCLEO_FAT_POSTTABLE_PROGRESS(0xfa0' "$fat_mount_source" "$fat_constructor" "$fat_dynamic_cache_source" "$fat_drive_source"
	! grep -q 'iHtcleoMountProgressPhase\|gHtcleoFirstFatMountPhase\|static volatile' "$fat_header" "$fat_file_source" "$fat_table_source" "$fat_constructor" "$fat_cache_header" "$fat_dynamic_cache_header" "$fat_legacy_cache_source" "$fat_dynamic_cache_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main"
	test "$(grep -c 'THtcleoFatDirReadTrace htcleoTrace;' "$fat_constructor")" -eq 1
	! grep -q '0xfd0[1-9a]0000u' "$fat_drive_source" "$efile_ext" "$locmedia_source" "$medmmc_source"
	! grep -q '0xfe0[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xff0[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf10[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf20[1-9a]0000u' "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf30[1-9a]0000u' "$fat_drive_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf40[1-9a]0000u' "$fat_drive_source" "$fat_dynamic_cache_source" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf50[1-9a]0000u' "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$estart_main" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf60[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf70[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf80[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xf90[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xfa1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$sdcc_stage_source"
	! grep -q '0xfb1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xfc1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xfd1[1-9a]0000u' "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	test "$(grep -c '0xfe1[1-9a]0000u' "$estart_main")" -eq 0
	! grep -q '0xfe1[1-9a]0000u' "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xf01[1-9a]0000u' "$fat_file_source" "$fat_table_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xf11[1-9a]0000u' "$fat_file_source" "$fat_table_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xf12[1-9a]0000u' "$fat_table_source" "$fat_file_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	test "$(grep -c '0xf13[1-9a]0000u' "$fat_table_source")" -eq 10
	! grep -q '0xf13[1-9a]0000u' "$fat_file_source" "$efile_file" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q '0xff1[1-9a]0000u' "$efile_file" "$fat_file_source" "$estart_main" "$fat_constructor" "$fat_mount_source" "$efile_sys" "$efile_drv" "$estart_source" "$fat_drive_source" "$fat_dynamic_cache_source" "$locmedia_source" "$medmmc_source" "$pbusmedia_source" "$mmc_session_source" "$mmc_stack_source" "$mmc_sdcard_source" "$spbus_source" "$sdcc_stage_source"
	! grep -q 'gHtcleoEstartBootlogWritePhase\|HTCLEO_EFILE_BOOTLOG_WRITE_PROGRESS(' "$efile_file"
	! grep -q 'iHtcleoFirstWritePhase' "$fat_header" "$fat_file_source"
	test "$(grep -c 'iHtcleoFirstAllocTraceArmed' "$fat_header")" -eq 1
	test "$(grep -c 'iHtcleoClusterAllocPhase' "$fat_header")" -eq 1
	grep -Fq 'Drive().DriveNumber() == EDriveC' "$fat_file_source"
	grep -Fq 'aMessage.SecureId().iId == 0x10272c04u' "$fat_file_source"
	grep -Fq 'aPos == 0 && aLength == 109' "$fat_file_source"
	! grep -q 'gHtcleoLocalMediaPowerupTrace' "$pbusmedia_source" "$spbus_source" "$mmc_stack_source"
	grep -q 'iSocket->iSocketNumber == 0' "$pbusmedia_source"
	grep -q 'iSocket->iState=EPBusOff;' "$pbusmedia_source"
	grep -q 'iPBusState=EPBusOff;' "$pbusmedia_source"
	! grep -q 'gHtcleoEstartERemountPhase' "$efile_sys" "$efile_drv"
	! grep -Fq 'User::After(100000);' "$estart_main"
	! grep -Fq 'fs.RemountDrive(' "$estart_main"
	! grep -Fq 'fs.FileSystemName(' "$estart_main"
	! grep -Fq 'fs.DismountFileSystem(' "$estart_main"
	! grep -Fq 'fs.MountFileSystem(' "$estart_main"
	test "$(grep -Fc 'fs.MkDirAll(KLogDir)' "$estart_main")" -eq 1
	! grep -Fq 'fs.Volume(volume,EDriveC);' "$estart_main"
	grep -Fq 'fs.Volume(volume,EDriveC,volumeStatus);' "$estart_main"
	grep -Fq 'User::WaitForRequest(volumeStatus);' "$estart_main"
	grep -q 'C:\\\\Symbian3\\\\BOOTLOG.TXT' "$estart_main"
	grep -q 'HTCLEO_FAT_LOG_V2' "$estart_main"
	test "$(grep -c 'htcleoTrace.iPhase = 0u;' "$fat_constructor")" -eq 1
	test "$(grep -c 's.FillCommandDesc(ECmdStopTransmission, 0);' "$mmc_sdcard_source")" -eq 1
	grep -q 'virtual TUint32 HtcleoTraceKind() const=0;' "$fat_cache_header"
	grep -q 'return 1;' "$fat_dynamic_cache_source"
	grep -q 'return 2;' "$fat_legacy_cache_source"
	grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_MOUNT_PROGRESS__' "$fat_mmp"
	! grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_FIRST_WRITE_PROGRESS__' "$fat_mmp"
	! grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_CLUSTER_ALLOCATION_PROGRESS__' "$fat_mmp"
	! grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_FREE_SPACE_SCANNER_PROGRESS__' "$fat_mmp"
	grep -q '^MACRO[[:space:]]*__HTCLEO_FAT_SYNCHRONOUS_SCAN_PROGRESS__' "$fat_mmp"
	test "$(grep -c '^\[DriveC\]$' "$htcleo_estart_config")" -eq 1
	test "$(grep -c '^FAT_FAT32_AsynchMount 0$' "$htcleo_estart_config")" -eq 1
	! grep -q 'FAT_FAT32_AsynchMount=' "$htcleo_estart_config"
	grep -q '^ALWAYS_BUILD_AS_ARM' "$fat_mmp"
	! grep -q 'HTCLEO_ESTART_PROGRESS(0xe100000' "$estart_main" "$estart_source"
	! grep -q 'HTCLEO_ESTART_PROGRESS(0xe20' "$estart_main" "$estart_source"
	! grep -q 'HTCLEO_ESTART_PROGRESS(0xe30' "$estart_main" "$estart_source"
	! grep -q 'HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xe40' "$locmedia_source" "$medmmc_source"
	! grep -q 'HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe50' "$locmedia_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source"
	! grep -q 'HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe60\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0\|HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0' "$locmedia_source" "$pbusmedia_source" "$spbus_source" "$mmc_stack_source"
	test "$(grep -c 'HTCLEO_ESTART_PROGRESS(0xee0' "$estart_source")" -eq 0
	test "$(grep -c 'HTCLEO_EFILE_MOUNT_PROGRESS(0xee0' "$efile_sys")" -eq 0
	test "$(grep -c 'HTCLEO_EFILE_CHECKMOUNT_PROGRESS(0xef0' "$efile_sys")" -eq 0
	test "$(grep -c 'HTCLEO_EFILE_DRIVE_FAT_PROGRESS(0xef0' "$efile_drv")" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$estart_main_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$estart_init_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$efile_sys_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$efile_drv_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$efile_file_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_drive_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$efile_media_read_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$locmedia_powerup_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$medmmc_progress_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$pbusmedia_progress_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$generic_session_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$generic_stack_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$generic_sdcard_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$sdcc_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_dynamic_cache_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_mount_common_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_mount_specific_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_mount_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_file_disasm" | wc -l)" -eq 0
	test "$(grep -E 'e24f[0-9a-f]008' "$fat_table_disasm" | wc -l)" -eq 10
	test "$(grep -hE 'e24f[0-9a-f]008' "$estart_main_disasm" "$estart_init_disasm" "$efile_sys_disasm" "$efile_drv_disasm" "$efile_file_disasm" "$fat_mount_disasm" "$fat_file_disasm" "$fat_table_disasm" "$locmedia_powerup_disasm" "$pbusmedia_progress_disasm" | wc -l)" -eq 10
	test "$(grep -h 'e7f000f0' "$estart_init_disasm" "$efile_sys_disasm" "$efile_drv_disasm" "$efile_file_disasm" "$fat_mount_disasm" "$fat_file_disasm" "$fat_table_disasm" "$locmedia_powerup_disasm" "$medmmc_progress_disasm" "$pbusmedia_progress_disasm" | wc -l)" -eq 0
	sha256sum "$release/efat32.fsy" >"$output/efat32-$mode.sha256"
	grep -q 'UserSvr::HalFunction(EHalGroupPlatformSpecific1,2,' "$estart_header"
	grep -q 'HTCLEO_EXTENSION_PROGRESS_LOCATION_PROBE' "$putils"
	grep -q 'HtcleoExtensionProgressLocationScreenProbe' "$putils_disasm"
	test "$(grep -c 'HtcleoExtensionProgressLocationScreenProbe' "$putils_disasm")" -ge 4
grep -q '^[[:space:]]*fsStart.StartSystem();' "$estart_main"
if grep -q 'TInt r=fsStart.StartSystem()' "$estart_main"; then
    echo "ERROR: retired StartSystem result probe remains in source" >&2
    exit 1
fi
if grep -q '48313532\|e7f0022[1-9]\|e7f0023[0-9]\|e7f0024[0-9]\|e7f0025[0-9]' "$estart_main_disasm"; then
    echo "ERROR: source-built ESTART E32Main contains a stale numbered probe in iteration 267" >&2
    exit 1
fi
grep -q 'ROM-only bring-up has no writable hal.dat to restore' "$estart_source"
grep -q 'secondary process through the not-yet-proven loader path' "$estart_source"
grep -B1 'r=LoadCodePageDll()' "$estart_source" | grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__'
test "$(grep -c '^[[:space:]]*MountRemovableDrives();' "$estart_source")" -eq 1
if grep -B1 'MountRemovableDrives();' "$estart_source" |
        grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__'; then
    echo "ERROR: removable-drive mount remains bypassed" >&2
    exit 1
fi
grep -q 'htcleoRomName = KServerPathSysBin()' "$estart_source"
grep -q "htcleoRomName\[0\] = (TText)'Z'" "$estart_source"
grep -q 'ws.Create(htcleoRomName,KNullDesC,TUidType())' "$estart_source"
grep -q 'TBool dmCreated=CreateServer(list,KDmManagerFileNameLit)' "$estart_source"
test "$(grep -c 'e7f000f0' "$estart_init_disasm")" -eq 0
test "$(grep -c 'e7f000f0' "$estart_main_disasm")" -eq 1
test "$(grep -c 'e7f000f0' "$sdcc_disasm")" -eq 0
grep -q '__attribute__((noinline)) TMMCErr RecordCommandResult' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
! grep -q 'HtcleoFatLogStageResult' "$estart_main"
! grep -Fq '(void)HtcleoWriteFatBootRecord();' "$estart_main"
grep -q 'const TInt htcleoFatLogResult=HtcleoWriteFatBootRecord();' "$estart_main"
! grep -q 'HTCLEO_GATE8_ENTRY_REGRESSION_PROBE' "$estart_main"
! grep -q 'HTCLEO_ESTART_ENTRY_REGRESSION_PROBE' "$estart_main"
grep -q 'HTCLEO_FAT_LOG_SUCCESS_LOCATION_UDF' "$estart_main"
! grep -q 'HTCLEO_POST_STARTSYSTEM_BOUNDARY_PROBE' "$estart_main"
! grep -q 'HTCLEO_POST_RUN_BOUNDARY_PROBE' "$estart_main"
! grep -q 'HTCLEO_STARTSYSTEM_CREATE_RESULT_PROBE' "$estart_source"
! grep -q 'HTCLEO_DRIVE2_READ_RESULT_PROBE' "$estart_source"
! grep -q 'HTCLEO_DRIVE2_PRE_READ_BOUNDARY_PROBE' "$estart_source"
! grep -q 'HTCLEO_POST_REMOVABLE_MOUNT_LOOP_PROBE' "$estart_source"
! grep -q 'HTCLEO_MOUNT_REMOVABLE_ENTRY_PROBE' "$estart_source"
! grep -q 'HTCLEO_POST_LOCAL_DRIVE_INIT_PROBE' "$estart_source"
! grep -q 'HTCLEO_PRE_STARTUP_INIT_COMPLETE_PROBE' "$estart_source"
! grep -q 'HTCLEO_POST_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source"
! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_MAPPING_PROBE' "$estart_source"
! grep -q 'HTCLEO_PRE_LOCAL_DRIVE_INIT_PROBE' "$estart_source"
test "$(grep -c 'e7f000f0' "$estart_source")" -eq 0
! grep -q 'StopWithSdccDiagnostic\|gHtcleoSdccPostTargetDeselect' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
# Iteration 431 retires the last active screen renderer.  Keep the read-only
# SD diagnostics on function 0/1, but fail closed if function 2 or the HTCLEO
# framebuffer mapping can reappear in source or emitted code.
! grep -q 'ShowEstartProgress\|DrawEstartProgressHexRow\|aFunction == 2\|0xc6400000' \
    "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'DiagnosticHal' "$sdcc_disasm"
! sed -n '/DiagnosticHalEPviS0_S0_>:/,/^$/p' "$sdcc_disasm" | \
    grep -Eq 'cmp[[:space:]]+(r[0-9]+|ip|lr), #2'
test "$(grep -c '0xc6400000' "$sdcc_disasm")" -eq 0
! grep -Eq '(cmp|mov)[[:space:]]+r[0-9]+, #800' "$sdcc_disasm"
grep -q 'HtcleoRecordTaggedCommandResult(Session(), command.iCommand, command.iArgument' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'command.iCommand == 7u && TUint32(command.iArgument) == 0u' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q '? 0x0eu : 4u' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KCmdProgramEnable = 1u << 11' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KProgramDone = 1u << 23' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KMMCErrBusyTimeOut' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'Kern::NanoWait(KMMCRetryGapInMilliseconds \* 1000000u)' "$mmc_stack"
grep -q '__HTCLEO_MMC_SYNC_RETRY_GAP__' "$mmc_mmp"
grep -Fq 'Kern::NanoWait(KMMCPollGapInMilliseconds * 1000000u);' "$mmc_stack"
grep -Fq 'const TUint32 htcleoProgramPeriod = ProgramPeriodInMilliSeconds();' "$mmc_stack"
grep -Fq 'Kern::NanoWait(htcleoProgramPeriod * 1000000u);' "$mmc_stack"
grep -q '__HTCLEO_MMC_SYNC_SESSION_TIMERS__' "$mmc_mmp"
grep -q 'HTCLEO_KERNEL_EXCEPTION_SCREEN_PROBE_RETIRED_V1' "$ckernel"
grep -q 'htcleoDrive2CapsResult' "$estart_source"
grep -q 'htcleoDrive2.Connect(2,htcleoChanged)' "$estart_source"
grep -q 'htcleoDrive2.Read(0,512,htcleoSector0)' "$estart_source"
grep -q 'htcleoSdccDiagnostic!=0xdfe00000u' "$estart_source"
grep -q 'EHalGroupPlatformSpecific1,1,0,0' "$estart_source"
grep -q 'KDriveAttRemovable' "$estart_source"
grep -q '0xca000000u' "$estart_source"
grep -q '0xcb000000u' "$estart_source"
grep -q '0xc0000000u' "$estart_source"
if grep -q 'e7f0022[1-9]\|e7f0023[0-9]\|e7f0024[0-9]\|e7f0025[0-9]\|HtcleoEstartRunProgress' "$estart_init_disasm"; then
    echo "ERROR: source-built ESTART Init/Run contains a stale probe in iteration 302" >&2
    exit 1
fi
test "$(grep -c 'e7f000f0' "$us_ksvr_disasm")" -eq 0
test "$(grep -c 'e7f000f0' "$efile_ldr_disasm")" -eq 0
test "$(grep -c 'e7f000f0' "$efile_cache_disasm")" -eq 0
grep -B1 'r = AddNotifications()' "$efile_cache" | grep -q '#ifndef __HTCLEO_LOW_ROM_PD_FIX_PROBE__'
sed -n '/<_ZN14CSessionLoader8ServiceLERK9RMessage2>:/,/^$/p' \
    "$efile_ldr_disasm" | grep -q 'R_ARM_CALL.*CheckLoaderCacheInit'
grep -q 'RLoader.*Connect' "$us_ksvr_disasm"
grep -q 'RLoader.*LoadProcess' "$us_ksvr_disasm"
grep -q 'ws.Create(htcleoRomName,KNullDesC,TUidType())' "$estart_source"
grep -q '<_E32Startup>:' "$efile_entry_disasm"
grep -q 'e31f0000' "$efile_entry_disasm"
if grep -q 'e7f000f0' "$efile_entry_disasm"; then
    echo "ERROR: iteration-137 entry UDF remains active" >&2
    exit 1
fi
grep -q '<RunThread>:' "$efile_custom_runthread_disasm"
grep -q 'SetupThreadHeap' "$efile_custom_runthread_disasm"
grep -q 'DllSetTls' "$efile_custom_runthread_disasm"
grep -q 'CallThrdProcEntry' "$efile_custom_runthread_disasm"
if grep -q 'HtcleoSetupThreadHeapLocal\|CreateThreadHeap\|SwitchAllocator\|4c323231\|e7f0022[1-9]\|e7f0023[0-3]' "$efile_custom_runthread_disasm"; then
	echo "ERROR: iteration-262 custom RunThread is not stock" >&2
	exit 1
fi
if grep -q 'e7f000f0\|ef00118[4-9]\|ef00119[0-9]\|ef00120[0-9]\|ef00121[0-3]' "$efile_custom_runthread_disasm"; then
	echo "ERROR: userspace RunThread contains a stale Loader probe" >&2
	exit 1
fi
grep -q '<_Z12LoaderThreadPv>:' "$efile_ldr_disasm"
grep -A2 '<_Z12LoaderThreadPv>:' "$efile_ldr_disasm" | grep -q 'e1a0c00d'
grep -A5 '<_Z12LoaderThreadPv>:' "$efile_ldr_disasm" | grep -q 'push.*{.*fp, ip, lr, pc}'
if grep -q '4c323231\|e7f0022[1-9]\|e7f0023[0-3]' "$efile_ldr_disasm"; then
	echo "ERROR: iteration-262 LoaderThread contains a probe" >&2
	exit 1
fi
if grep -q '<_Z22HtcleoLoaderNakedEntryPv>:' "$efile_ldr_disasm"; then
	echo "ERROR: iteration-218 naked target remains in iteration 262" >&2
	exit 1
fi
grep -q '<_E32Startup>:' "$efile_custom_entry_disasm"
grep -A8 '<_E32Startup>:' "$efile_custom_entry_disasm" | grep -q 'e31f0000'
grep -A8 '<_E32Startup>:' "$efile_custom_entry_disasm" | grep -q 'e3540001'
if grep -q 'e7f000f0\|e7f0021[8-9]\|ef00118[4-9]\|ef00119[0-9]\|ef00120[0-9]\|ef00121[0-8]' "$efile_custom_entry_disasm"; then
	echo "ERROR: an E32 entry probe remains active in iteration 262" >&2
	exit 1
fi
if grep -q 'e7f000f0' "$efile_dispatch_disasm"; then
	echo "ERROR: iteration-168 CallThrdProcEntry probe remains active" >&2
	exit 1
fi
grep -A80 '<CallThrdProcEntry>:' "$efile_dispatch_disasm" | grep -q 'blx'
if grep -q 'e7f000f0\|ef00118[4-9]\|ef00119[0-6]\|48313633\|48313634\|48313635\|48313636\|48313637\|48313638\|48313639\|48313730\|48313731\|48313732\|48313733\|48313734\|48313735\|48313736\|48313737\|48313738\|48313739\|48313830\|4c313831\|4c313832\|4c313833\|4c313836\|4c313837\|4c313838\|4c313839\|4c313930\|4c313931\|4c313932\|4c313933\|4c313934\|4c313935\|4c313936' "$stock_runthread_disasm"; then
	echo "ERROR: an EFILE probe leaked into stock eexe.lib" >&2
	exit 1
fi
if grep -q 'e7f000f0\|de42\|48313433\|HtcleoHeapChunkResultArmProbe\|ef00118[6-9]\|ef00119[0-6]\|ef00121[2-5]\|4c31393[0-6]\|4c32313[2-5]' "$heap_hybrid_disasm"; then
    echo "ERROR: a stale inline heap probe remains active" >&2
    exit 1
fi
# Writable-E bring-up retains the low-ROM PDE, Z: cache, elocd, and the three
# still-required optional bypasses. Removable-drive mounting is restored now
# that the native SDCC2 PSL is in the ROM.
grep -q 'name = ChunkCreate' "$execs_txt"
grep -q 'Exec::ChunkCreate(aCreateInfo.iOwnerType, ptrName, info)' "$kernel_source/kernel/eka/euser/us_ksvr.cpp"
grep -q '<_ZN6RChunk6CreateER16TChunkCreateInfo>:' "$us_ksvr_disasm"
grep -q 'R_ARM_.*CALL.*Exec.*ChunkCreate' "$us_ksvr_disasm"
grep -A2 '<_ZN8UserHeap16CreateThreadHeap' "$heap_hybrid_disasm" | grep -q 'e1a0c00d'
grep -q 'R_ARM_.*CALL.*RChunk.*Create' "$heap_hybrid_disasm"
if grep -q '__HTCLEO_LOW_ROM_PD_FIX_PROBE__\|4c323231\|e7f0022[1-9]\|e7f0023[0-3]\|ef00122[1-9]' "$heap_hybrid" "$heap_hybrid_disasm"; then
	echo "ERROR: iteration-262 requires stock CreateThreadHeap" >&2
	exit 1
fi
grep -q '<_ZN11ExecHandler12ThreadCreateERK6TDesC810TOwnerTypeR17SThreadCreateInfo>:' "$sexec_disasm"
if grep -q 'c6400000\|HtcleoGate3ChunkCreateEntryScreenProbe' "$sexec_disasm"; then
    echo "ERROR: iteration-146 direct kernel renderer remains active" >&2
    exit 1
fi
grep -q '<_ZN8UserHeap15SetupThreadHeapEiR24SStdEpocThreadCreateInfo>:' "$up_utl_disasm"
grep -q 'CreateThreadHeap' "$up_utl_disasm"
grep -A4 '<_ZN8UserHeap15SetupThreadHeapEiR24SStdEpocThreadCreateInfo>:' "$up_utl_disasm" | grep -q 'mov.*ip, sp'
grep -A6 '<_ZN8UserHeap15SetupThreadHeapEiR24SStdEpocThreadCreateInfo>:' "$up_utl_disasm" | grep -q 'push.*{.*fp, ip, lr, pc}'
grep -A8 '<_ZN8UserHeap15SetupThreadHeapEiR24SStdEpocThreadCreateInfo>:' "$up_utl_disasm" | grep -q 'sub.*fp, ip, #4'
if grep -q '__HTCLEO_LOADER_.*PROBE__\|4c32313[2-9]\|ef00121[2-9]\|e7f0021[8-9]' "$up_utl" "$up_utl_disasm"; then
	echo "ERROR: iteration-262 ESTART probe leaked into SetupThreadHeap" >&2
	exit 1
fi
if grep -q 'e7f000f0\|ef00118[4-9]\|ef00119[0-9]\|ef00120[0-9]\|ef00121[0-1]' "$up_utl_disasm"; then
	echo "ERROR: SetupThreadHeap contains an earlier visible probe" >&2
	exit 1
fi
if grep -q '300000000u' "$ckernel"; then
	echo "ERROR: iteration-283 Domain Manager pre-SendReceive probe must halt without a delay/resume path" >&2
	exit 1
fi
grep -q '<__ArmVectorAbortPrefetch>:' "$vectors_disasm"
grep -q '<__ArmVectorUndef>:' "$vectors_disasm"
if grep -q 'HtcleoEstartInitCompleteFixedExceptionScreenProbe\|KHexGlyphs\|0xc6400000\|0xc6300000\|0x03839000\|0x556500c3' \
		"$ckernel" "$ckernel_disasm"; then
	echo "ERROR: iteration-431 retired kernel exception screen renderer remains active" >&2
	exit 1
fi
if grep -q 'ef001217\|ef001218\|ef001219\|ef001220\|ef001221\|ef001222\|ef001223\|ef001224\|ef001225\|HtcleoLoaderNakedEntryScreenProbe\|HtcleoLoaderFetchExceptionScreenProbe\|HtcleoLoaderSourceExceptionScreenProbe\|HtcleoLoaderFaultStatusExceptionScreenProbe\|HtcleoLowRomPdFixExceptionScreenProbe\|HtcleoEstartEntryExceptionScreenProbe\|HtcleoStockLoaderEntryExceptionScreenProbe\|HtcleoLoaderRendezvousExceptionScreenProbe\|HtcleoLoaderReadyExceptionScreenProbe\|HtcleoPostInitLoaderExceptionScreenProbe\|HtcleoEstartE32MainExceptionScreenProbe\|HtcleoStartupThreadExceptionScreenProbe\|HtcleoPreEstartCreateExceptionScreenProbe\|HtcleoPostEstartCreateExceptionScreenProbe\|HtcleoEstartCreateResultExceptionScreenProbe\|HtcleoEstartFileEntryResultExceptionScreenProbe' "$vectors_disasm"; then
	echo "ERROR: iteration-262 must keep the SWI vector stock" >&2
	exit 1
fi
if grep -q 'e7f000f0\|ef001184\|ef001185\|ef001186\|ef001187\|ef001188\|ef001189\|ef001190\|ef001191\|ef001192\|ef001193\|ef001194\|ef001195\|ef001196\|ef001197\|ef001198\|ef001199\|ef001200\|ef001201\|ef001202\|ef001203\|ef001204\|ef001205\|ef001206\|ef001207\|ef001208\|ef001209\|ef001210\|ef001211\|ef001212\|ef001213\|ef001214\|ef001215\|4c313833\|4c313836\|4c313837\|4c313838\|4c313839\|4c313930\|4c313931\|4c313932\|4c313933\|4c313934\|4c313935\|4c313936\|4c313938\|4c313939\|4c323030\|4c323032\|4c323033\|4c323034\|4c323035\|4c323036\|4c323037\|4c323038\|4c323039\|4c323130\|4c323131\|4c323132\|4c323133\|4c323134\|4c323135' "$ckernel_cia_disasm" "$vectors_disasm"; then
	echo "ERROR: an earlier Loader/UDF/SWI probe remains active" >&2
	exit 1
fi
if grep -q 'e7f000f0\|48313738\|48313739\|48313830\|4c313738\|4c313739\|4c313830\|4c313831\|4c313832\|4c313833' "$sexec_disasm"; then
	echo "ERROR: iteration-177 ThreadResume/ThreadCreate probe remains active" >&2
	exit 1
fi
grep -q 'aThread->Resume();' "$sexec"
efile_map="$release/efile.exe.map"
test -s "$efile_map"
grep -q 'htcleo_efile_low_rom_pd_fix' "$efile_map"
if grep -q 'htcleo_loader_e32startup_entry\|htcleo_loader_user_target_pc\|htcleo_loader_user_target_r7' "$efile_map"; then
	echo "ERROR: a stale EFILE probe FIRSTLIB remains active" >&2
	exit 1
fi
grep -q '0x00008000[[:space:]]*_E32Startup' "$efile_map"
grep -q '[[:space:]]*_Z7E32Mainv' "$efile_map"
kernel_map="$release/_htcleo_ekern.exe.map"
test -s "$kernel_map"
grep -q 'ExecHandler.*ThreadCreate' "$kernel_map"
euser_map="$release/_htcleo_euser.dll.map"
test -s "$euser_map"
if grep -q 'htcleo_heap_pre_chunk_arm' "$euser_map"; then
    echo "ERROR: iteration-149 pre-chunk helper remains linked" >&2
    exit 1
fi
if grep -q '[[:space:]]strh[[:space:]]' "$lcd_disasm"; then
    echo "ERROR: iteration-134 LCD black-clear loop remains in gate-6 build" >&2
    exit 1
fi
grep -q 'LoaderThread,KLoaderStackSize' "$efile_ldr"
grep -q 'KHeapMinSize,maxsize,NULL' "$efile_ldr"
grep -q 'first untouched ROM page raises IFSR 0x5' "$xmmu"
grep -q 'CopyPdes(newpd, kpd, romBase, romEnd)' "$xmmu"
grep -a -q 'HTCLEO_FAT_LOG_V2' "$estart_main_obj"
grep -q 'virtual void SetBusWidth' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'blockLength << 4' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KDataRead | KDataReadPending' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q '^#define MMC0_DRIVECOUNT 2$' "$bsp_stage/baseport/htcleo/specific/variantmediadef.h"
grep -q '^#define MMC0_DRIVELIST  2,1$' "$bsp_stage/baseport/htcleo/specific/variantmediadef.h"
grep -q 'MMCSocket()->iVcc->SetState(EPsuOnCurLimit)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'const TUint32 KHtcleoSdOcr2850 = 0x00010000u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'aInfo.iVoltageSupported = KHtcleoSdOcr2850;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'gHtcleoSdccDiagnostic = 0xdfe00000u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'gHtcleoSdccPowerUpDiagnostic = 0xd9ff0000u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'RecordPowerUpResult(2u, gHtcleoSdccLastPowerResult)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'RecordPowerUpResult(0xfeu, KErrNone)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KProcClockRegimeEnable = 50u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KProcClockRegimeSelectSpeed = 58u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KProcLeoSdcc2Clock = 67u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KProcLeoSdcc2PClock = 16u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'data2 = HtcleoClockSpeed(aRate);' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KClockLinearBase   = 0xC6700000u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc_regs.h"
grep -q 'KClockGlobalSdcc2Gate = 1u << 8;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'global = global | KClockGlobalSdcc2Gate;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'KHwPhysClockCtl.*EQU.*0xa8600000' "$bsp_stage/baseport/htcleo/bootstrap/htcleo.inc"
grep -q 'HW_MAPPING.*KHwPhysClockCtl' "$bsp_stage/baseport/htcleo/bootstrap/htcleo.s"
sed -n '/DHtcleoSdStack::DoPowerUpSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_BEGIN'
sed -n '/DHtcleoSdStack::DoPowerUpSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_END'
sed -n '/DHtcleoSdStack::InitClockOnSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_BEGIN'
sed -n '/DHtcleoSdStack::InitClockOnSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_END'
sed -n '/DHtcleoSdStack::IssueMMCCommandSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_BEGIN'
sed -n '/DHtcleoSdStack::IssueMMCCommandSM()/,/^    }/p' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | grep -q 'SMF_END'
if sed -n '/DHtcleoSdStack::ASSPDisengage()/,/^    }/p' \
    "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp" | \
    grep -q '^[[:space:]]*ReportASSPDisengaged();'; then
    echo "ERROR: ASSPDisengage still dereferences detached iSessionP through ReportASSPDisengaged" >&2
    exit 1
fi
grep -q 'ReportASSPDisengaged() operates on iSessionP' \
    "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
if grep -q 'KProcClockEnable = 20u;\|KProcClockSetRate = 24u;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"; then
    echo "ERROR: generic CLKCTL RPC remains in the HTC Leo SDCC path" >&2
    exit 1
fi
grep -q 'DPBusSocket::SocketFromId(0)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'socket->iState == EPBusCardAbsent' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'socket->iState = EPBusOff;' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q '0xd8000000u | (socketState << 20)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q 'Kern::AddHalEntry(EHalGroupPlatformSpecific1, DiagnosticHal, 0)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
grep -q '((aCommand & 0x3fu) << 20)' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"
if grep -q 'iVoltageSupported = 0x00300000u' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"; then
    echo "ERROR: stale 3.2-3.4V SDCC OCR mask remains active" >&2
    exit 1
fi
if grep -q 'ESlot1Internal' "$bsp_stage/baseport/htcleo/mmc/htcleo_sdcc.cpp"; then
    echo "ERROR: removable SD slot is marked internal" >&2
    exit 1
fi
echo "HTCLEO_FAT_F13_BRINGUP_AUDIT_OK mode=$mode active_physical_udf=1 returning_reporter=efat32-synchronous-free-space-scan checkpoints=10 checkpoint_split=estart-0-efile-0-efat32-10-elocd-0-epbussd-0 checkpoint_scope=efat32-drive-c-stock-synchronous-free-space-scan-through-exact-bootlog-allocation probe_gate=drive-sid-pos-length-empty-file-arm-per-fat-table-phase final_probe=fat-write-flush-close-exact-runtime-udf gate7=verified-pass-on-361 run_return=verified-pass-on-388 fat_log=c-fat-mount-and-read-verified-through-388 replace=verified-pass-fe16-on-397 efile_write_preflight=verified-pass-ff19-on-399 fat_write_frontier=verified-f121-scanner-working-timer-wait-on-402 sync_volume=blocked-after-fd12-on-396 async_volume=enabled-on-397 drive_c_fat32_async_mount=disabled-for-stock-synchronous-scan e_drive=unmapped-fc18-kerrnotready-on-395 fixed_boot_quickcheck=socket0-absent-to-off-preserved recovery=no-media-remount media_remount=forbidden-not-used timer=bypassed-in-fat-free-space-scan-after-f121-on-402 sdcc2_psl=native-pio sdcc2_explicit_stop=verified-pass-on-385-card-tran-state4 sdcc2_assp_disengage=null-safe-generic-session-state-owner-verified-on-372 sdcc2_second_stage_media_open=verified-pass-on-373 sdcc2_partition_ecaps=verified-pass-on-374 sdcc2_clock=leo-wince-regime-plus-global-gate sdcc2_retry_gap=bounded-sync-10ms sdcc2_session_timers=bounded-sync-poll-program sdcc2_r1b=program-enable-plus-busy-wait sdcc2_cmd7_rca0_timeout=generic-expected-filtered sdcc2_target_select=verified-pass-on-341 sdcc2_post_select_deselect=first-result-and-second-entry-verified-on-344-no-different-tuple-on-345 sdcc2_cmd8=verified-pass-on-333 sdcc2_powerup_smf=child-frame-pop-repaired sdcc2_initclock_smf=child-frame-pop-repaired sdcc2_command_smf=child-frame-pop-repaired sdcc2_ocr=2.8-2.9v-at-2850mv sdcc2_card_presence=fixed-boot-media removable_mount=active addnotifications=deferred-until-post-ui-compatibility halsettings=deferred-until-post-ui-persistence codepage=default-conversion-until-multilingual-fat-validation media_hal=generic-elocd-native-sdcc2 z_drive_cache=on-demand low_rom_user_pd=copy-rom-pdes-from-init-pd syborg_runtime=closed product_profile=htcleo-qsd8250-noncellular cellular_startup=disabled-payloads-retained native_debug=artifacts-present-permanently-not-autostarted native_input=artifacts-present-keys-type2a-temporarily-deferred native_iram=artifact-present-medint-temporarily-deferred native_audio=qsd8k-smd-dal-adie-acdb"

echo "HTCLEO_NATIVE_BSP_OK mode=$mode log=$log"
