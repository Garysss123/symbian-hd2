#!/bin/sh
# Build the complete S60/Avkon ROM with the source-native HTCLEO/QSD8250 BSP.
# This script creates local artifacts only and never writes to an SD card.
set -eu

project=/path/to/hd2-legacy-lab
build_mode=${HD2_BUILD_MODE:-incremental}
incremental_parent=${HD2_INCREMENTAL_PARENT:-}
case "$incremental_parent" in
    901-symbian3-full-filemanager-refresh-worker-c-only|902-symbian3-full-filemanager-worker-normal-priority-c-only|903-symbian3-full-filemanager-view-request-incremental|904-symbian3-full-filemanager-async-local-view-incremental|905-symbian3-full-filemanager-view-client-incremental|906-symbian3-full-home-ready-walk-retired-incremental|907-symbian3-full-home-view-state-incremental|908-symbian3-full-home-view-queue-incremental|909-symbian3-full-hscontent-ecom-error-guard-incremental|910-symbian3-full-filemanager-view-wrapper-incremental)
        echo 'ERROR: this composite ROM/C lineage requires its dedicated identity-checked builder. The legacy pipeline must not reset C-layer provenance or overwrite the retained GFLM worker fix. For903 use build-htcleo-filemanager-view-request.py.' >&2
        exit 1
        ;;
    842-symbian3-full-about-no-global-rescan-recovery)
        echo 'ERROR: 842 frozen after original842/new-cache control died in CenRep USER-EXEC3/KERN4 before Home. Restore immutable840 functional state; no About/black/CBA stacking on842.' >&2
        exit 1
        ;;
    843-symbian3-full-gsapp-black-background-incremental)
        echo 'ERROR: 843 frozen after pre-Home SSM USER-EXEC3/KERN4. Original842 also failed; restore immutable840 functional state, not this branch.' >&2
        exit 1
        ;;
    841-symbian3-full-about-entry-incremental)
        echo 'ERROR: 841 frozen after pre-Home SSM USER-EXEC3/KERN4 and incomplete AppArc cache. Use840 plus one isolated recovery; no black-background or CBA changes on841.' >&2
        exit 1
        ;;
    804-symbian3-full-hsps-header-cache-recovery-incremental)
        # Same804 regained Home after explicit storage repair; keep that parent.
        # Only the declared single launch-plugin continuation may proceed here.
        test "${HD2_INCREMENTAL_RESOURCE_POLICY:-}" = gate17-menu-task-enumeration-on804
        test "${HD2_INCREMENTAL_CHANGED_BINARIES:-}" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
        ;;
    802-symbian3-full-wserv-find-notfound-incremental|803-symbian3-full-menu-task-enumeration-incremental)
        echo 'ERROR: 802/803 frozen after Home startup regression. Use801 plus one attributed recovery change; keep exact742/801 WServ. Do not stack on the failed branch.' >&2
        exit 1
        ;;
    800-symbian3-full-menu-task-lookup-control-incremental)
        #800 exposed a real non-resource completion abort and is frozen.
        #Only the attributed single-watcher recovery/control may use it.
        test "${HD2_INCREMENTAL_RESOURCE_POLICY:-}" = gate17-mcs-operation-completion
        test "${HD2_INCREMENTAL_CHANGED_BINARIES:-}" = /root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll
        ;;
    799-symbian3-full-mcs-notifier-stop-incremental)
        #799 is NOT a functional baseline: UI stalls after Settings. Permit
        #only this declared single-plugin recovery/control, not general stacking.
        test "${HD2_INCREMENTAL_RESOURCE_POLICY:-}" = gate17-menu-task-lookup-control
        test "${HD2_INCREMENTAL_CHANGED_BINARIES:-}" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
        ;;
    789-symbian3-full-settings-deferred-activation-incremental)
        echo 'ERROR: 789 frozen after repeated Home-to-Matrix failure. Use788 recovery base; only a declared single-difference control may replay deferred worker activation. Do not stack CBA/WServ/priority fixes.' >&2
        exit 1
        ;;
    786-symbian3-full-settings-worker-run-incremental)
        echo 'ERROR: 786 frozen after Home-to-Matrix regression. Use785 plus the isolated startup-witness control; do not stack on786 or change CBA/WServ/input without evidence.' >&2
        exit 1
        ;;
    780-symbian3-full-settings-only-ready-registration-incremental)
        echo 'ERROR: 780 frozen after repeated pre-UI failure before ailaunch/Settings worker. Use778 recovery or a justified single-variable control; inspect Matrix A12D packed-config IPC, do not stack Settings/font/CBA changes.' >&2
        exit 1
        ;;
    779-symbian3-full-rom-app-catalog-font-observer-incremental)
        echo 'ERROR: 779 frozen after first-boot pre-UI SSM USER-EXEC3/KERN4. Use778 plus one Settings-only change; no font/global-version experiment.' >&2
        exit 1
        ;;
    776-symbian3-full-bluetooth-cmi-bypass-incremental)
        echo 'ERROR: 776 is frozen after pre-Home C32:ESock_DIP fatal. Use775 plus the reviewed offline network closure, without a checkpoint retest.' >&2
        exit 1
        ;;
    774-symbian3-full-native-crash-notice-incremental)
        # Clean-log774r1 restored UI and caught the original late KERN4 without
        # CBA input. The early failure was log-state-confounded, not a proven
        # observer regression. Permit this exact diagnostic partial parent.
        test "$(sha256sum "$project/Symbian/output/$incremental_parent/Symbian3/initrd.gz" | awk '{print $1}')" = \
            7c6203594472a8c6533bfbcaef06b0655bd3fe59b6c74e6bb143fdd80b3fd540
        ;;
    773-symbian3-full-kernel-fault-badge-incremental)
        echo 'ERROR: 773 is frozen after early white-screen/Matrix-init regression. Use772 and restore its pinned core; do not stack repairs on773.' >&2
        exit 1
        ;;
    768-symbian3-full-matrix-context-recovery-incremental)
        echo 'ERROR: 768 observer failed lookup after caption rename; use766 plus corrected SID discovery.' >&2
        exit 1
        ;;
    767-symbian3-full-async-service-context-incremental)
        echo 'ERROR: 767 is frozen after Matrix-to-Home input regression; use766 plus a single diagnostic change.' >&2
        exit 1
        ;;
    764-symbian3-full-sparse-fat-logs-incremental)
        echo 'ERROR: 764 is frozen after white-screen regression with and without retained logs; use763 as recovery parent.' >&2
        exit 1
        ;;
    759-symbian3-full-matrix-stale-focus-no-redraw-incremental)
        echo 'ERROR: 759 is frozen after Home-to-Matrix regression; use the 758 recovery control.' >&2
        exit 1
        ;;
    761-symbian3-full-independent-clock-watch-incremental)
        echo 'ERROR: 761 is frozen after Matrix input regression; use the 760 recovery control.' >&2
        exit 1
        ;;
esac
incremental_changed_binaries=${HD2_INCREMENTAL_CHANGED_BINARIES:-}
incremental_resource_policy=${HD2_INCREMENTAL_RESOURCE_POLICY:-}
about_entry_policy=off
home_background_priority_ab_policy=off
home_menu_handoff_policy=priority-freeze-real-ordinal-restore-no-render-wait-175b-175c
ui_control_policy=aifw-eb6e34b8-exact-xn3layoutengine-743-b9fd5ebf-native-focus
if [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    home_background_priority_ab_policy=Home-only-handoff-ComputeOff2-to-Disabled0-retain-current-priority-one-byte-AB-not-global-fix
    home_menu_handoff_policy=priority-retain-real-ordinal-no-render-wait-175b-175c-840-AB
    ui_control_policy=aifw742-exact-xn743-plus840-one-byte-background-priority-AB
fi
if [ "$incremental_parent" = 775-symbian3-full-kern4-exit-subject-incremental ]; then
    test "$incremental_resource_policy" = disable-offline-ip-closure
    test -z "$incremental_changed_binaries"
fi
if [ -n "$incremental_resource_policy" ]; then
    test "$build_mode" = incremental
    case "$incremental_resource_policy" in
        disable-offline-ip-closure)
            test -z "$incremental_changed_binaries"
            test "$incremental_parent" = 775-symbian3-full-kern4-exit-subject-incremental ;;
        gate17-font-settings)
            test -z "$incremental_changed_binaries"
            test "$incremental_parent" = 777-symbian3-full-offline-ip-closure-incremental
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 1
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-catalog-observer|gate17-settings-only)
            test "$incremental_parent" = 778-symbian3-full-english-font-settings-entry-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-settings-ready-781)
            test "$incremental_parent" = 781-symbian3-full-packed-layout-ipc-trace-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-matrix-pointer-frontier)
            test "$incremental_parent" = 782-symbian3-full-settings-ready-on-781-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-matrix-list-release)
            test "$incremental_parent" = 783-symbian3-full-matrix-pointer-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-matrix-system-fade)
            test "$incremental_parent" = 784-symbian3-full-matrix-list-release-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-settings-direct-registration)
            test "$incremental_parent" = 790-symbian3-full-settings-query-off-control-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-action-frontier)
            test "$incremental_parent" = 791-symbian3-full-settings-direct-registration-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-launch-frontier)
            test "$incremental_parent" = 792-symbian3-full-menu-action-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 1
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-attribute-frontier)
            test "$incremental_parent" = 793-symbian3-full-menu-launch-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-request-frontier)
            test "$incremental_parent" = 794-symbian3-full-menu-attribute-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-server-exit-watch)
            test "$incremental_parent" = 795-symbian3-full-menu-request-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-software-exception)
            test "$incremental_parent" = 796-symbian3-full-menu-server-exit-watch-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-exception-stack)
            test "$incremental_parent" = 797-symbian3-full-menu-software-exception-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-mcs-notifier-stop)
            test "$incremental_parent" = 798-symbian3-full-menu-exception-stack-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenu.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-task-lookup-control)
            test "$incremental_parent" = 799-symbian3-full-mcs-notifier-stop-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-mcs-operation-completion)
            test "$incremental_parent" = 800-symbian3-full-menu-task-lookup-control-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsservice.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-wserv-find-notfound)
            test "$incremental_parent" = 801-symbian3-full-mcs-operation-completion-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/wserv_nga.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-task-enumeration)
            test "$incremental_parent" = 801-symbian3-full-mcs-operation-completion-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-hsps-header-cache)
            test "$incremental_parent" = 801-symbian3-full-mcs-operation-completion-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/hspsthemeserver.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-statuspane-frontier)
            test "$incremental_parent" = 814-symbian3-full-gsapp-appinfo-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-appinfo-frontier)
            test "$incremental_parent" = 813-symbian3-full-gsapp-eikbase-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-eikbase-frontier)
            test "$incremental_parent" = 812-symbian3-full-gsapp-sgc-params-local-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-view-frontier)
            test "$incremental_parent" = 816-symbian3-full-gsapp-sgc-fade-local-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-focus-frontier)
            test "$incremental_parent" = 817-symbian3-full-gsapp-view-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate19-filemanager-registration)
            test "$incremental_parent" = 899-symbian3-full-filemanager-cdl-tail-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-font-family-binding)
            test "$incremental_parent" = 851-symbian3-full-avkon-common-geometry-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/FontProvider.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-avkon-common-geometry)
            test "$incremental_parent" = 850-symbian3-full-gsapp-root-bitmap-background-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcoctl.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-black-background)
            test "$incremental_parent" = 849-symbian3-full-gsapp-root-paint-witness-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-about-no-global-rescan)
            test "$incremental_parent" = 840-symbian3-full-home-background-priority-ab-incremental
            test -z "$incremental_changed_binaries"
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-about-entry)
            test "$incremental_parent" = 840-symbian3-full-home-background-priority-ab-incremental
            test -z "$incremental_changed_binaries"
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-home-background-priority-ab)
            test "$incremental_parent" = 839-symbian3-full-home-kernel-watch-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/xn3layoutengine.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-home-kernel-watch)
            test "$incremental_parent" = 838-symbian3-full-vws-session-deactivation-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-vws-session-deactivation)
            test "$incremental_parent" = 837-symbian3-full-vws-server-event-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-vws-server-event)
            test "$incremental_parent" = 836-symbian3-full-viewsrv-source-control-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-viewsrv-source-control)
            test "$incremental_parent" = 835-symbian3-full-vws-client-state-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewsrv.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-vws-client-state)
            test "$incremental_parent" = 834-symbian3-full-vws-client-queue-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-vws-client-queue)
            test "$incremental_parent" = 833-symbian3-full-viewcli-source-control-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-viewcli-source-control)
            test "$incremental_parent" = 832-symbian3-full-home-view-event-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/viewcli.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-home-view-event)
            test "$incremental_parent" = 831-symbian3-full-gsapp-cone-view-event-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-cone-view-event)
            test "$incremental_parent" = 830-symbian3-full-gsapp-view-transition-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-view-transition)
            test "$incremental_parent" = 829-symbian3-full-gsapp-async-view-event-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-async-view-event)
            test "$incremental_parent" = 828-symbian3-full-gsapp-list-activation-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-list-activation)
            test "$incremental_parent" = 827-symbian3-full-gsapp-child-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-child-frontier)
            test "$incremental_parent" = 826-symbian3-full-gsapp-ecom-create-retry-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-ecom-create-retry)
            test "$incremental_parent" = 825-symbian3-full-gsapp-ecom-notify-guard-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/ecom.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-ecom-notify-guard)
            test "$incremental_parent" = 824-symbian3-full-gsapp-exception-witness-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-exception-witness)
            test "$incremental_parent" = 823-symbian3-full-gsapp-lifetime-observer-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-lifetime-observer)
            test "$incremental_parent" = 822-symbian3-full-gsapp-redraw-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-redraw-frontier)
            test "$incremental_parent" = 821-symbian3-full-gsapp-plugin-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-plugin-frontier)
            test "$incremental_parent" = 820-symbian3-full-gsapp-activation-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 1
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-activation-frontier)
            test "$incremental_parent" = 819-symbian3-full-gsapp-keyblock-local-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-keyblock-local)
            test "$incremental_parent" = 818-symbian3-full-gsapp-focus-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-sgc-fade-local)
            test "$incremental_parent" = 815-symbian3-full-gsapp-statuspane-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-sgc-params-local)
            test "$incremental_parent" = 811-symbian3-full-gsapp-appui-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-appui-frontier)
            test "$incremental_parent" = 810-symbian3-full-gsapp-sgc-local-layout-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-sgc-local-layout)
            test "$incremental_parent" = 809-symbian3-full-gsapp-aknenv-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-aknenv-frontier)
            test "$incremental_parent" = 808-symbian3-full-gsapp-env-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/stem_avkon.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-env-frontier)
            test "$incremental_parent" = 807-symbian3-full-gsapp-eikstart-frontier-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-eikstart-frontier)
            test "$incremental_parent" = 806-symbian3-full-gsapp-startup-observer-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-gsapp-startup-observer)
            test "$incremental_parent" = 805-symbian3-full-menu-task-enumeration-on804-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-menu-task-enumeration-on804)
            test "$incremental_parent" = 804-symbian3-full-hsps-header-cache-recovery-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/mcsmenuhandler.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        gate17-layout-ipc-trace)
            test "$incremental_parent" = 778-symbian3-full-english-font-settings-entry-incremental
            test "$incremental_changed_binaries" = /root/symbian3-full/epoc32/release/armv5/urel/akncapserverclient.dll
            test "${HD2_INCREMENTAL_MIGRATION:-0}" = 0
            test "${HD2_REBUILD_NATIVE_BSP:-0}" = 0 ;;
        *) echo 'ERROR: unknown incremental resource policy' >&2; exit 1 ;;
    esac
fi
incremental_migration=${HD2_INCREMENTAL_MIGRATION:-0}
rebuild_native_bsp=${HD2_REBUILD_NATIVE_BSP:-0}
preflight_only=${HD2_PREFLIGHT_ONLY:-0}
native_epocroot=/root/symbian
native_kernel_binary="$native_epocroot/epoc32/release/armv5/urel/_htcleo_ekern.exe"
full_epocroot=/root/symbian3-full
if grep -q htcleofmwait900.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-wait-boundary.py" "$full_epocroot" --restore
fi
if grep -q htcleofmdestroy898.inl "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ecom-destroy.py" "$full_epocroot" --restore
fi
if grep -q htcleofmasync897.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-async-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmlate896.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-late-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmsystemfade895.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-system-fade.py" "$full_epocroot" --restore
fi
if grep -q htcleofmprogress894.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknProgressDialog.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-progress-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmcallback893.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-callback-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmready892.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ready-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmws891.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ws-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmactivation890.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknViewAppUi.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-activation-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmredraw889.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEPRIV.CPP"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ui-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmfocus888.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-focus-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmfep887.inl "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEFEP.CPP"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-fep-frontier.py" "$full_epocroot" --restore
fi
if grep -q htcleofmsgcguard886.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-sgc-local.py" "$full_epocroot" --restore
fi
if grep -q htcleofmsgc885.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-sgc.py" "$full_epocroot" --restore
fi
if grep -q htcleofmaknenv884.inl "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknenv.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-aknenv.py" "$full_epocroot" --restore
fi
if grep -q htcleofmenv883.inl "$full_epocroot/sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-env.py" "$full_epocroot" --restore
fi
if grep -q htcleofmstartup882.inl "$full_epocroot/sf/mw/classicui/commonuisupport/uikon/coresrc/EIKSTART.CPP"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-startup.py" "$full_epocroot" --restore
fi
if grep -q htcleofmlifewatch881.inl "$full_epocroot/sf/mw/homescreensrv/menucontentsrv/handlersrc/menuapphandler.cpp"; then
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-lifetime.py" "$full_epocroot" --restore
fi
gsapp_font_server_lifetime="$project/Symbian/scripts/apply-htcleo-gsapp-font-server-lifetime.py"
gsapp_font_server_lifetime_policy=off
if grep -q HTCLEO_GS_FONT_SERVER_LIFETIME_858 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_font_server_lifetime" "$full_epocroot" --restore
fi
gsapp_font_load_boundary="$project/Symbian/scripts/apply-htcleo-gsapp-font-load-boundary.py"
gsapp_font_load_boundary_policy=off
if grep -q HTCLEO_GS_FONT_LOAD_BOUNDARY_855 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_font_load_boundary" "$full_epocroot" --restore
fi
gsapp_font_census="$project/Symbian/scripts/apply-htcleo-gsapp-font-census.py"
gsapp_font_census_policy=off
if grep -q HTCLEO_GS_FONT_CENSUS_854 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_font_census" "$full_epocroot" --restore
fi
gsapp_text_witness="$project/Symbian/scripts/apply-htcleo-gsapp-text-witness.py"
gsapp_text_witness_policy=off
if grep -q HTCLEO_GS_TEXT_WITNESS_853 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_text_witness" "$full_epocroot" --restore
fi
font_family_binding="$project/Symbian/scripts/apply-htcleo-font-family-binding.py"
font_family_binding_policy=off
fbs_rom_rasterizer="$project/Symbian/scripts/apply-htcleo-fbs-rom-rasterizer.py"
fbs_rom_rasterizer_policy=off
avkon_common_geometry="$project/Symbian/scripts/apply-htcleo-avkon-common-geometry.py"
avkon_common_geometry_policy=off
if grep -q 'include "htcleoavkongeometry851.inl"' "$full_epocroot/sf/mw/classicui/uifw/EikStd/coctlsrc/EIKCOLIB.CPP"; then
    python3 "$avkon_common_geometry" "$full_epocroot" --restore
fi
gsapp_root_bitmap_background="$project/Symbian/scripts/apply-htcleo-gsapp-root-bitmap-background.py"
gsapp_root_bitmap_background_policy=off
if grep -q HTCLEO_GS_ROOT_BITMAP_BACKGROUND_850 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_root_bitmap_background" "$full_epocroot" --restore
fi
gsapp_root_paint_witness="$project/Symbian/scripts/apply-htcleo-gsapp-root-paint-witness.py"
gsapp_root_paint_witness_policy=off
if grep -q HTCLEO_GS_ROOT_PAINT_WITNESS_849 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_root_paint_witness" "$full_epocroot" --restore
fi
gsapp_root_background_owner="$project/Symbian/scripts/apply-htcleo-gsapp-root-background-owner.py"
gsapp_root_background_owner_policy=off
if grep -q HTCLEO_GS_ROOT_BACKGROUND_OWNER_848 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_root_background_owner" "$full_epocroot" --restore
fi
gsapp_root_skin_background="$project/Symbian/scripts/apply-htcleo-gsapp-root-skin-background.py"
gsapp_root_skin_background_policy=off
if grep -q HTCLEO_GS_ROOT_SKIN_BACKGROUND_847 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_root_skin_background" "$full_epocroot" --restore
fi
gsapp_window_background="$project/Symbian/scripts/apply-htcleo-gsapp-window-background.py"
gsapp_window_background_policy=off
if grep -q HTCLEO_GS_ROOT_WINDOW_BACKGROUND_846 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp"; then
    python3 "$gsapp_window_background" "$full_epocroot" --restore
fi
gsapp_black_background="$project/Symbian/scripts/apply-htcleo-gsapp-black-background.py"
gsapp_black_background_policy=off
gsapp_static_background="$project/Symbian/scripts/apply-htcleo-gsapp-static-background.py"
gsapp_static_background_policy=off
if grep -q HTCLEO_GS_STATIC_BACKGROUND_845 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSUi.cpp"; then
    python3 "$gsapp_static_background" "$full_epocroot" --restore
fi
if grep -q HTCLEO_GS_LOCAL_BLACK_BACKGROUND_843 "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSUi.cpp"; then
    python3 "$gsapp_black_background" "$full_epocroot" --restore
fi
home_kernel_watch="$project/Symbian/scripts/apply-htcleo-home-kernel-watch.py"
python3 "$home_kernel_watch" "$full_epocroot" --restore
home_kernel_watch_policy=off
external_thread_watch_policy=ailaunch-matrix-kernel21-v2-readyqueue-endpoint-sync766-1m
vws_session_deactivation="$project/Symbian/scripts/apply-htcleo-vws-session-deactivation.py"
python3 "$vws_session_deactivation" "$full_epocroot" --restore
vws_session_deactivation_policy=off
vws_server_event="$project/Symbian/scripts/apply-htcleo-vws-server-event.py"
python3 "$vws_server_event" "$full_epocroot" --restore
vws_server_event_policy=off
viewsrv_binary="$full_epocroot/epoc32/release/armv5/urel/viewsrv.dll"
viewsrv_source_control_policy=off
vws_client_state="$project/Symbian/scripts/apply-htcleo-vws-client-state.py"
python3 "$vws_client_state" "$full_epocroot" --restore
vws_client_state_policy=off
vws_client_queue="$project/Symbian/scripts/apply-htcleo-vws-client-queue.py"
python3 "$vws_client_queue" "$full_epocroot" --restore
vws_client_queue_policy=off
viewcli_binary="$full_epocroot/epoc32/release/armv5/urel/viewcli.dll"
viewcli_source_control_policy=off
home_view_event="$project/Symbian/scripts/apply-htcleo-home-view-event.py"
python3 "$home_view_event" "$full_epocroot" --restore
home_view_event_policy=off
gsapp_cone_event="$project/Symbian/scripts/apply-htcleo-gsapp-cone-view-event.py"
python3 "$gsapp_cone_event" "$full_epocroot" --restore
gsapp_cone_event_policy=off
gsapp_transition="$project/Symbian/scripts/apply-htcleo-gsapp-view-transition.py"
python3 "$gsapp_transition" "$full_epocroot" --restore
gsapp_transition_policy=off
gsapp_async="$project/Symbian/scripts/apply-htcleo-gsapp-async-view-event.py"
python3 "$gsapp_async" "$full_epocroot" --restore
gsapp_async_policy=off
gsapp_list="$project/Symbian/scripts/apply-htcleo-gsapp-input-activation.py"
python3 "$gsapp_list" "$full_epocroot" --restore
gsapp_list_policy=off
gsapp_child="$project/Symbian/scripts/apply-htcleo-gsapp-child-frontier.py"
python3 "$gsapp_child" "$full_epocroot" --restore
gsapp_child_policy=off
gsapp_exception="$project/Symbian/scripts/apply-htcleo-gsapp-exception-witness.py"
python3 "$gsapp_exception" "$full_epocroot" --restore
gsapp_exception_policy=off
gsapp_notify="$project/Symbian/scripts/apply-htcleo-gsapp-ecom-notify-guard.py"
python3 "$gsapp_notify" "$full_epocroot" --restore
gsapp_notify_policy=off
ecom_server_exception="$project/Symbian/scripts/apply-htcleo-ecom-server-exception.py"
ecom_server_exception_policy=off
ecom_missing_interface="$project/Symbian/scripts/apply-htcleo-ecom-missing-interface-empty.py"
ecom_missing_interface_policy=off-860-frozen
ecom_font_getinfo="$project/Symbian/scripts/apply-htcleo-ecom-font-getinfo.py"
ecom_font_getinfo_policy=off
if grep -q HTCLEO_ECOM_FONT_GETINFO_863 "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp"; then
    python3 "$ecom_font_getinfo" "$full_epocroot" --restore
fi
ecom_font_registry="$project/Symbian/scripts/apply-htcleo-ecom-font-registry.py"
ecom_font_registry_policy=off
if grep -q HTCLEO_ECOM_FONT_REGISTRY_862 "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp"; then
    python3 "$ecom_font_registry" "$full_epocroot" --restore
fi
home_external_empty="$project/Symbian/scripts/apply-htcleo-home-external-empty.py"
home_external_empty_policy=off
if grep -q HTCLEO_HOME_EXTERNAL_EMPTY_861 "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp"; then
    python3 "$home_external_empty" "$full_epocroot" --restore
fi
if grep -q htcleoecserverexception.inl "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComServerStart.cpp"; then
    python3 "$ecom_server_exception" "$full_epocroot" --restore
fi
font_ecom_reconnect="$project/Symbian/scripts/apply-htcleo-font-ecom-list-reconnect.py"
font_ecom_reconnect_policy=off
if grep -q HTCLEO_FONT_ECOM_LIST_RECONNECT_856 "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"; then
    python3 "$font_ecom_reconnect" "$full_epocroot" --restore
fi
gsapp_create="$project/Symbian/scripts/apply-htcleo-gsapp-ecom-create-retry.py"
python3 "$gsapp_create" "$full_epocroot" --restore
gsapp_create_policy=off
wserv_control_policy=b8a2fb688e3a920923330d12819a1e8b048bca52cbfe2142721ab446889c421b
wserv_find_policy=off
wserv_find_notfound="$project/Symbian/scripts/apply-htcleo-wserv-find-notfound.py"
python3 "$wserv_find_notfound" "$full_epocroot" --restore
hsps_header_cache="$project/Symbian/scripts/apply-htcleo-hsps-header-cache-recovery.py"
python3 "$hsps_header_cache" "$full_epocroot" --restore
gsapp_lifetime="$project/Symbian/scripts/apply-htcleo-gsapp-lifetime-observer.py"
gsapp_redraw="$project/Symbian/scripts/apply-htcleo-gsapp-redraw-frontier.py"
gsapp_plugin="$project/Symbian/scripts/apply-htcleo-gsapp-plugin-frontier.py"
gsframework_binary="$full_epocroot/epoc32/release/armv5/urel/gsframework.dll"
gsapp_activation="$project/Symbian/scripts/apply-htcleo-gsapp-activation-frontier.py"
python3 "$gsapp_lifetime" "$full_epocroot" --restore
gsapp_lifetime_policy=off
python3 "$gsapp_redraw" "$full_epocroot" --restore
gsapp_redraw_policy=off
python3 "$gsapp_plugin" "$full_epocroot" --restore
gsapp_plugin_policy=off
python3 "$gsapp_activation" "$full_epocroot" --restore
gsapp_activation_policy=off
gsapp_keyblock="$project/Symbian/scripts/apply-htcleo-gsapp-keyblock-local.py"
python3 "$gsapp_keyblock" "$full_epocroot" --restore
gsapp_keyblock_policy=off
gsapp_focus="$project/Symbian/scripts/apply-htcleo-gsapp-focus-frontier.py"
python3 "$gsapp_focus" "$full_epocroot" --restore
gsapp_focus_policy=off
gsapp_view="$project/Symbian/scripts/apply-htcleo-gsapp-view-frontier.py"
python3 "$gsapp_view" "$full_epocroot" --restore
gsapp_view_policy=off
gsapp_sgc_fade="$project/Symbian/scripts/apply-htcleo-gsapp-sgc-fade-local.py"
python3 "$gsapp_sgc_fade" "$full_epocroot" --restore
gsapp_sgc_fade_policy=off
gsapp_statuspane="$project/Symbian/scripts/apply-htcleo-gsapp-statuspane-frontier.py"
python3 "$gsapp_statuspane" "$full_epocroot" --restore
gsapp_statuspane_policy=off
gsapp_appinfo="$project/Symbian/scripts/apply-htcleo-gsapp-appinfo-frontier.py"
python3 "$gsapp_appinfo" "$full_epocroot" --restore
gsapp_appinfo_policy=off
gsapp_eikbase="$project/Symbian/scripts/apply-htcleo-gsapp-eikbase-frontier.py"
python3 "$gsapp_eikbase" "$full_epocroot" --restore
gsapp_eikbase_policy=off
gsapp_sgc_params="$project/Symbian/scripts/apply-htcleo-gsapp-sgc-params-local.py"
python3 "$gsapp_sgc_params" "$full_epocroot" --restore
gsapp_sgc_params_policy=off
gsapp_appui="$project/Symbian/scripts/apply-htcleo-gsapp-appui-frontier.py"
python3 "$gsapp_appui" "$full_epocroot" --restore
gsapp_appui_policy=off
gsapp_sgc="$project/Symbian/scripts/apply-htcleo-gsapp-sgc-local-layout.py"
python3 "$gsapp_sgc" "$full_epocroot" --restore
gsapp_sgc_policy=off
gsapp_aknenv="$project/Symbian/scripts/apply-htcleo-gsapp-aknenv-frontier.py"
python3 "$gsapp_aknenv" "$full_epocroot" --restore
gsapp_aknenv_policy=off
gsapp_env="$project/Symbian/scripts/apply-htcleo-gsapp-env-frontier.py"
python3 "$gsapp_env" "$full_epocroot" --restore
gsapp_env_policy=off
gsapp_eikstart="$project/Symbian/scripts/apply-htcleo-gsapp-eikstart-frontier.py"
python3 "$gsapp_eikstart" "$full_epocroot" --restore
gsapp_eikstart_policy=off
gsapp_observer="$project/Symbian/scripts/apply-htcleo-gsapp-startup-observer.py"
python3 "$gsapp_observer" "$full_epocroot" --restore
gsapp_observer_policy=off
gate17_observer="$project/Symbian/scripts/apply-htcleo-gate17-observer.py"
python3 "$gate17_observer" "$full_epocroot" --restore
filemanager_registration="$project/Symbian/scripts/apply-htcleo-apparc-exit-watch.py"
filemanager_registration_policy=off
apparc_forced_native="$project/Symbian/scripts/apply-htcleo-apparc-forced-native.py"
python3 "$apparc_forced_native" "$full_epocroot" --restore
apparc_forced_native_policy=off
filemanager_launch_prep="$project/Symbian/scripts/apply-htcleo-filemanager-launch-prep.py"
python3 "$filemanager_launch_prep" "$full_epocroot" --restore
filemanager_launch_prep_policy=off
apparc_preload_publication="$project/Symbian/scripts/apply-htcleo-apparc-preload-publication.py"
python3 "$apparc_preload_publication" "$full_epocroot" --restore
apparc_preload_publication_policy=off
apparc_empty_icon_name="$project/Symbian/scripts/apply-htcleo-apparc-empty-icon-name.py"
python3 "$apparc_empty_icon_name" "$full_epocroot" --restore
apparc_empty_icon_name_policy=off
apparc_enumeration_end="$project/Symbian/scripts/apply-htcleo-apparc-enumeration-end.py"
python3 "$apparc_enumeration_end" "$full_epocroot" --restore
apparc_enumeration_end_policy=off
apparc_terminal_exception="$project/Symbian/scripts/apply-htcleo-apparc-terminal-exception.py"
python3 "$apparc_terminal_exception" "$full_epocroot" --restore
apparc_terminal_exception_policy=off
if grep -Eq 'HTCLEO_FILEMANAGER_REGISTRATION_866|HTCLEO_FILEMANAGER_CLIENT_BOUNDARY_867|HTCLEO_FILEMANAGER_REGISTRATION_CENSUS_868|HTCLEO_APPARC_EXIT_WATCH_870' "$full_epocroot/sf/mw/homescreensrv/idlefw/hslaunch/src/htcleog17settings.inl"; then
    python3 "$filemanager_registration" "$full_epocroot" --restore
fi
gate17_settings="$project/Symbian/scripts/apply-htcleo-g17-settings.py"
python3 "$gate17_settings" "$full_epocroot" --restore
packed_layout_trace="$project/Symbian/scripts/apply-htcleo-packed-layout-trace.py"
python3 "$packed_layout_trace" "$full_epocroot" --restore
matrix_pointer_frontier="$project/Symbian/scripts/apply-htcleo-matrix-pointer-frontier.py"
python3 "$matrix_pointer_frontier" "$full_epocroot" --restore
matrix_list_release="$project/Symbian/scripts/apply-htcleo-matrix-list-release.py"
python3 "$matrix_list_release" "$full_epocroot" --restore
matrix_system_fade="$project/Symbian/scripts/apply-htcleo-matrix-system-fade.py"
python3 "$matrix_system_fade" "$full_epocroot" --restore
mcs_operation_completion="$project/Symbian/scripts/apply-htcleo-mcs-operation-completion.py"
python3 "$mcs_operation_completion" "$full_epocroot" --restore
mcs_server_exit_watch="$project/Symbian/scripts/apply-htcleo-mcs-server-exit-watch.py"
python3 "$mcs_server_exit_watch" "$full_epocroot" --restore
mcs_action_frontier="$project/Symbian/scripts/apply-htcleo-mcs-action-frontier.py"
python3 "$mcs_action_frontier" "$full_epocroot" --restore
menu_task_enumeration="$project/Symbian/scripts/apply-htcleo-menu-task-enumeration.py"
python3 "$menu_task_enumeration" "$full_epocroot" --restore
menu_task_lookup="$project/Symbian/scripts/apply-htcleo-menu-task-lookup-control.py"
python3 "$menu_task_lookup" "$full_epocroot" --restore
menu_launch_frontier="$project/Symbian/scripts/apply-htcleo-menu-launch-frontier.py"
python3 "$menu_launch_frontier" "$full_epocroot" --restore
mcs_notifier_stop="$project/Symbian/scripts/apply-htcleo-mcs-applist-notifier.py"
mcs_notifier_reconnect="$project/Symbian/scripts/apply-htcleo-mcs-notifier-reconnect.py"
python3 "$mcs_notifier_reconnect" "$full_epocroot" --restore
mcs_notifier_reconnect_policy=off
python3 "$mcs_notifier_stop" "$full_epocroot" --restore
mcs_exception_stack="$project/Symbian/scripts/apply-htcleo-mcs-exception-stack.py"
python3 "$mcs_exception_stack" "$full_epocroot" --restore
mcs_software_exception="$project/Symbian/scripts/apply-htcleo-mcs-software-exception-observer.py"
python3 "$mcs_software_exception" "$full_epocroot" --restore
menu_request_frontier="$project/Symbian/scripts/apply-htcleo-menu-request-frontier.py"
python3 "$menu_request_frontier" "$full_epocroot" --restore
menu_attribute_frontier="$project/Symbian/scripts/apply-htcleo-menu-attribute-frontier.py"
python3 "$menu_attribute_frontier" "$full_epocroot" --restore
external_thread_watch="$project/Symbian/scripts/apply-htcleo-external-thread-watch.py"
python3 "$external_thread_watch" "$full_epocroot" --restore
shell_resume_fastpath="$project/Symbian/scripts/apply-htcleo-shell-resume-fastpath.py"
sparse_fat_logs="$project/Symbian/scripts/apply-htcleo-sparse-fat-logs.py"
python3 "$sparse_fat_logs" "$full_epocroot" --restore
menulog_capacity="$project/Symbian/scripts/apply-htcleo-menulog-shared-capacity.py"
python3 "$menulog_capacity" "$full_epocroot" --restore
# Revalidate the exact predecessor with the existing source transforms before
# the reviewed 763 overlay is applied immediately ahead of compilation.
python3 "$shell_resume_fastpath" "$full_epocroot" --restore
htcleo_touch_source="$project/Symbian/hd2/qsd8250-native-bsp/baseport/htcleo/input/htcleo_touch.cpp"
htcleo_hal_values="$project/Symbian/hd2/qsd8250-native-bsp/baseport/htcleo/hal/values.hda"
stem="$full_epocroot/pdk304-stemkit/syborg_stem.rom.oby"
work=/root/symbian3-full-work/htcleo-native
output="$project/Symbian/output/qsd8250-native-full-rom"
build_output="$output/Symbian3/build"
default_skin_repository_source="$full_epocroot/epoc32/data/z/private/10202be9/101F876F.txt"
default_skin_repository_output="$output/htcleo-personalisation-101F876F.txt"
default_skin_repository_transform="$project/Symbian/scripts/prepare-htcleo-default-skin-repository.py"
rombuild="$native_epocroot/epoc32/tools/rombuild"
prepared="$work/full-prepared.oby"
recipe="$work/htcleo_symbian3_full_native.oby"
image="$work/htcleo_symbian3_full_native.img"
log="$output/rombuild.log"
probe_map="$output/HTCLEO-PROBE-MAP.txt"
loader_log_map="$output/HTCLEO-LOADER-LOG-MAP.txt"
loader_log_map_tool="$project/Symbian/scripts/create-htcleo-loader-log-map.py"
canonicalizer="$project/Symbian/scripts/canonicalize-htcleo-full-rom-no-displays.py"
rom_space_audit="$project/Symbian/scripts/audit-htcleo-rom-space.py"
rom_space_report="$output/HTCLEO-ROM-SPACE-AUDIT.txt"
canonical_image="$build_output/htcleo_symbian3_full_canonical_no_displays.img"
canonical_map="$build_output/HTCLEO-CANONICAL-NO-DISPLAY-MAP.txt"
ssm_component="$full_epocroot/sf/os/devicesrv/sysstatemgmt/systemstatemgr"
ssm_main="$ssm_component/ssm/src/main.cpp"
ssm_cle_executor="$ssm_component/cle/src/cmdlistexecutor.cpp"
ssm_cle_bldinf="$ssm_component/cle/group/bld.inf"
ssm_bldinf="$ssm_component/ssm/group/bld.inf"
ssm_patch="$project/Symbian/hd2/qsd8250-native-bsp/patches/sysstatemgr-htcleo-startup-rendezvous.patch"
ssm_log_transform="$project/Symbian/scripts/apply-htcleo-sysstatemgr-durable-log.py"
ssm_cle_log_transform="$project/Symbian/scripts/apply-htcleo-cle-durable-log.py"
ssm_custom_transform="$project/Symbian/scripts/apply-htcleo-custom-command-durable-log.py"
ssm_custom_load_split_transform="$project/Symbian/scripts/apply-htcleo-akncustcmd-library-load-split-log.py"
ssm_custom_init_trace_transform="$project/Symbian/scripts/apply-htcleo-akncustcmd-library-init-entrypoint-log.py"
ssm_custom_component="$ssm_component/cmd"
ssm_custom_source="$ssm_custom_component/src/cmdcustomcommand.cpp"
ssm_custom_header="$ssm_custom_component/inc/cmdmultiplewait.h"
ssm_custom_mmp="$ssm_custom_component/group/ssmcmd.mmp"
ssm_custom_bldinf="$ssm_custom_component/group/bld.inf"
ssm_custom_def="$ssm_custom_component/eabi/ssmcmd_v1u.def"
ssm_custom_binary="$full_epocroot/epoc32/release/armv5/urel/ssmcmd.dll"
apparc_component="$full_epocroot/sf/mw/appsupport/appfw/apparchitecture"
apparc_transform="$project/Symbian/scripts/apply-htcleo-apparc-durable-log.py"
apparc_sync_scan_transform="$project/Symbian/scripts/apply-htcleo-apparc-first-scan-synchronous.py"
apparc_restart_recovery_transform="$project/Symbian/scripts/apply-htcleo-apparc-restart-optional-recovery.py"
apparc_restart_recognizer_transform="$project/Symbian/scripts/apply-htcleo-apparc-restart-optional-recognizer.py"
apparc_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/apparc-build/bld.inf"
apparc_aplist_source="$apparc_component/aplist/aplapplist.cpp"
apparc_apsstart_source="$apparc_component/apserv/APSSTART.CPP"
apparc_apsserv_source="$apparc_component/apserv/APSSERV.CPP"
apparc_apsses_source="$apparc_component/apserv/APSSES.CPP"
apparc_aplist_logger="$apparc_component/aplist/htcleoapplistlog.cpp"
apparc_apserv_logger="$apparc_component/apserv/htcleoapalog.cpp"
apparc_aplist_mmp="$apparc_component/group/APLIST.MMP"
apparc_apserv_mmp="$apparc_component/group/APSERV.MMP"
apparc_aplist_binary="$full_epocroot/epoc32/release/armv5/urel/aplist.dll"
apparc_apserv_binary="$full_epocroot/epoc32/release/armv5/urel/apserv.dll"
apparc_apsexe_binary="$full_epocroot/epoc32/release/armv5/urel/apsexe.exe"
apparc_launch_component="$full_epocroot/sf/mw/classicui/uifw/AknGlobalUI/AknCapServer"
apparc_launch_source="$apparc_launch_component/clientsrc/AknCapServerClient.cpp"
apparc_launch_mmp="$apparc_launch_component/group/AknCapServerClient.mmp"
apparc_launch_transform="$project/Symbian/scripts/apply-htcleo-apparc-launch-durable-log.py"
apparc_launch_held_process_transform="$project/Symbian/scripts/apply-htcleo-akncap-client-held-process-rendezvous.py"
apparc_launch_property_ready_transform="$project/Symbian/scripts/apply-htcleo-akncap-client-property-ready-handshake.py"
apparc_launch_property_poll_transform="$project/Symbian/scripts/apply-htcleo-akncap-client-property-poll-ready.py"
apparc_launch_fire_forget_transform="$project/Symbian/scripts/apply-htcleo-akncap-client-fire-and-forget-ready.py"
apparc_launch_matrixmenu_connect_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-matrixmenu-durable-log.py"
apparc_launch_matrixmenu_no_timer_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-no-timer-retry.py"
apparc_launch_matrixmenu_bounded_retry_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-bounded-no-timer-retry.py"
apparc_launch_matrixmenu_reuse_child_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-reuse-inflight-child-trace.py"
apparc_launch_matrixmenu_ready_wait_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-ready-property-wait.py"
apparc_launch_matrixmenu_discover_server_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-discover-registered-server.py"
apparc_launch_matrixmenu_single_attempt_transform="$project/Symbian/scripts/apply-htcleo-aknui-connect-matrixmenu-single-attempt.py"
apparc_launch_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/akncapserverclient-build/bld.inf"
apparc_launch_binary="$full_epocroot/epoc32/release/armv5/urel/akncapserverclient.dll"
akncapserver_component="$full_epocroot/sf/mw/classicui/uifw/AknGlobalUI/AknCapServer"
akncapserver_source="$akncapserver_component/src/AknCapServerEntry.cpp"
akncapserver_ipc_source="$akncapserver_component/src/AknCapServer.cpp"
akncapserver_mmp="$akncapserver_component/group/AknCapServer.mmp"
akncapserver_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-startup-durable-log.py"
akncapserver_eikcore_bridge="$project/Symbian/scripts/apply-htcleo-akncapserver-eikcore-trace-bridge.py"
akncapserver_rendezvous_ready_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-rendezvous-ready-compat.py"
akncapserver_property_ready_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-property-ready-signal.py"
akncapserver_ofn_bypass_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-ofn-bypass.py"
akncapserver_postcritical_filelog_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-postcritical-filelog-retirement.py"
akncapserver_postcritical_property_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-postcritical-property-breadcrumb.py"
akncapserver_e100_pre_retirement_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-e100-pre-retirement.py"
akncapserver_criticality_bypass_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-criticality-bypass.py"
akncapserver_nonleo_startup_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-nonleo-startup-bypasses.py"
akncapserver_registration_lifetime_transform="$project/Symbian/scripts/apply-htcleo-akncapserver-registration-lifetime-repair.py"
akncapserver_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/akncapserver-build/bld.inf"
akncapserver_binary="$full_epocroot/epoc32/release/armv5/urel/akncapserver.exe"
eikcore_component="$full_epocroot/sf/mw/classicui/commonuisupport/uikon"
eikcore_apf_inc="$full_epocroot/sf/mw/appsupport/appfw/apparchitecture/inc"
eikcore_source="$eikcore_component/coresrc/EIKENV.CPP"
eikstart_source="$eikcore_component/coresrc/EIKSTART.CPP"
eikappui_source="$eikcore_component/coresrc/EIKAPPUI.CPP"
eikcore_compat_source="$eikcore_component/coresrc/eikprivate.cpp"
eikcore_mmp="$eikcore_component/group/EIKCORE.MMP"
eikcore_frozen_def="$eikcore_component/eabi/EIKCOREU.DEF"
eikcore_transform="$project/Symbian/scripts/apply-htcleo-eikcore-prefactory-progress.py"
eikcore_postprocess_gap_transform="$project/Symbian/scripts/apply-htcleo-eikcore-postprocess-gap-trace.py"
eikcore_akncap_priority_defer_transform="$project/Symbian/scripts/apply-htcleo-eikcore-akncap-priority-defer.py"
eikcore_constructl_transform="$project/Symbian/scripts/apply-htcleo-eikcore-constructl-progress.py"
eikcore_postappui_transform="$project/Symbian/scripts/apply-htcleo-eikcore-postappui-progress.py"
eikcore_matrixmenu_taskname_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-unchanged-taskname-defer.py"
eikcore_matrixmenu_appready_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-appready-publish-defer.py"
eikcore_matrixmenu_startup_view_ao_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-startup-view-ao-arm.py"
eikcore_matrixmenu_startup_view_priority_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-startup-view-priority.py"
eikcore_matrixmenu_direct_startup_view_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-direct-startup-view.py"
eikcore_matrixmenu_startup_view_retire_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-startup-view-retire.py"
eikcore_matrixmenu_view_init_retire_transform="$project/Symbian/scripts/apply-htcleo-eikcore-matrixmenu-view-init-retire.py"
eikcore_homescreen_constructapp_trace_transform="$project/Symbian/scripts/apply-htcleo-eikcore-homescreen-constructapp-trace.py"
eikstart_homescreen_trace_transform="$project/Symbian/scripts/apply-htcleo-eikstart-homescreen-trace.py"
eikappui_baseconstruct_transform="$project/Symbian/scripts/apply-htcleo-eikappui-baseconstruct-durable-log.py"
eikappui_matrixmenu_final_screen_transform="$project/Symbian/scripts/apply-htcleo-eikappui-matrixmenu-final-screenchange-defer.py"
eikappui_homescreen_baseconstruct_trace_transform="$project/Symbian/scripts/apply-htcleo-eikappui-homescreen-baseconstruct-trace.py"
eikappui_homescreen_foreground_trace_transform="$project/Symbian/scripts/apply-htcleo-eikappui-homescreen-foreground-trace.py"
eikcore_abi_audit="$project/Symbian/scripts/audit-htcleo-eikcore-abi.py"
eikcore_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/eikcore-build/bld.inf"
eikcore_binary="$full_epocroot/epoc32/release/armv5/urel/eikcore.dll"
eikcore_stock_442="$output/eikcore-stock-442.dll"
eikcoctl_component="$full_epocroot/sf/mw/classicui/uifw/EikStd"
eikcoctl_source="$eikcoctl_component/coctlsrc/EIKCOLIB.CPP"
eikcoctl_statuspane_source="$eikcoctl_component/coctlsrc/eikspane.cpp"
eikcoctl_statusmodel_source="$eikcoctl_component/coctlsrc/eikspmod.cpp"
eikcoctl_cba_source="$eikcoctl_component/coctlsrc/eikcba.cpp"
eikcoctl_btgpc_source="$eikcoctl_component/coctlsrc/EIKBTGPC.CPP"
eikcoctl_physics_source="$eikcoctl_component/coctlsrc/aknstyluspopupmenuphysicshandler.cpp"
eikcoctl_list_item_source="$eikcoctl_component/coctlsrc/EIKLBI.CPP"
eikcoctl_mmp="$eikcoctl_component/coctlsrc/EIKCOCTL.MMP"
eikcoctl_frozen_def="$eikcoctl_component/EABI/EIKCOCTLU.DEF"
eikcoctl_abi_audit="$project/Symbian/scripts/audit-htcleo-eikcoctl-abi.py"
eikcoctl_touch_header="$full_epocroot/epoc32/include/mw/akntouchpane.h"
eikcoctl_edwin_header="$full_epocroot/epoc32/include/mw/eikedwin.h"
eikcoctl_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-appinfo-durable-log.py"
eikcoctl_statuspane_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-statuspane-durable-log.py"
eikcoctl_statuspane_scale_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-matrixmenu-statuspane-scale.py"
eikcoctl_cba_inner_redraw_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-matrixmenu-cba-inner-redraw.py"
eikcoctl_cba_wrapper_redraw_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-matrixmenu-cba-wrapper-redraw.py"
eikcoctl_statuslayout_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-statuslayout-durable-log.py"
eikcoctl_statustree_layout_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-statustree-layout-durable-log.py"
eikcoctl_combined_visibility_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-combined-pane-visibility-log.py"
eikcoctl_matrixmenu_fade_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-matrixmenu-fade-failclosed.py"
eikcoctl_matrixmenu_clientrect_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-matrixmenu-clientrect-scale.py"
eikcoctl_homescreen_geometry_transform="$project/Symbian/scripts/apply-htcleo-eikcoctl-homescreen-geometry-scale.py"
eikcoctl_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/eikcoctl-build/bld.inf"
eikcoctl_config_path="$project/Symbian/config"
eikcoctl_config=arm.v5.urel.gcce4_4_1.eikcoctl_permissive
eikcoctl_config_file="$eikcoctl_config_path/eikcoctl-gcce.xml"
eikcoctl_binary="$full_epocroot/epoc32/release/armv5/urel/eikcoctl.dll"
eikcoctl_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/515-eikcoctl-parent.txt"
eikcoctl_stock_515="$output/eikcoctl-stock-515.dll"
eiksrvc_source="$eikcore_component/srvsrc/EIKSRVC.CPP"
eiksrvc_mmp="$eikcore_component/group/EIKSRVC.MMP"
eiksrvc_frozen_def="$eikcore_component/eabi/EIKSRVCU.DEF"
eiksrvc_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-connect-durable-log.py"
eiksrvc_timeout_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-rendezvous-timeout-compat.py"
eiksrvc_cancel_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-rendezvous-cancel-compat.py"
eiksrvc_ready_retry_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-single-child-ready-retry.py"
eiksrvc_compact_poll_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-compact-ready-poll-log.py"
eiksrvc_ready_wait_transform="$project/Symbian/scripts/apply-htcleo-eiksrvc-rendezvous-ready-wait.py"
eiksrvc_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/eiksrvc-build/bld.inf"
eiksrvc_binary="$full_epocroot/epoc32/release/armv5/urel/eiksrvc.dll"
eiksrvc_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/462-eiksrvc-parent.txt"
eiksrvc_compat_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/463-eiksrvc-parent.txt"
eiksrvc_cancel_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/464-eiksrvc-parent.txt"
eiksrvc_ready_retry_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/465-eiksrvc-parent.txt"
eiksrvc_compact_poll_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/466-eiksrvc-parent.txt"
eiksrvs_source="$eikcore_component/srvsrc/EIKSRVS.CPP"
eiksrvs_mmp="$eikcore_component/group/EIKSRVS.MMP"
eiksrvs_transform="$project/Symbian/scripts/apply-htcleo-eiksrvs-startup-durable-log.py"
eiksrvs_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/eiksrvs-build/bld.inf"
eiksrvs_binary="$full_epocroot/epoc32/release/armv5/urel/eiksrvs.exe"
eiksrvs_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/454-eiksrvs-parent.txt"
eiksrv_source="$eikcore_component/srvsrc/eiksrv.cpp"
eiksrv_mmp="$eikcore_component/group/eiksrv.mmp"
eiksrv_transform="$project/Symbian/scripts/apply-htcleo-eiksrv-server-construct-durable-log.py"
eiksrv_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/eiksrv-build/bld.inf"
eiksrv_binary="$full_epocroot/epoc32/release/armv5/urel/eiksrv.dll"
eiksrv_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/455-eiksrv-parent.txt"
eiksrvui_source="$full_epocroot/sf/mw/classicui/uifw/EikStd/srvuisrc/EIKSRVUI.CPP"
eiksrvui_mmp="$full_epocroot/sf/incubator/stemkit/breakdeps/EIKSRVUI.MMP"
eiksrvui_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-constructl-durable-log.py"
eiksrvui_initialize_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-initialize-durable-log.py"
eiksrvui_c32_failopen_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-c32-ui-fail-open.py"
eiksrvui_notify_alert_failopen_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-notify-alert-ui-fail-open.py"
eiksrvui_construct_entry_split_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-construct-entry-split-log.py"
eiksrvui_system_attribute_failopen_transform="$project/Symbian/scripts/apply-htcleo-eiksrvui-system-attribute-ui-fail-open.py"
aknappui_baseconstruct_transform="$project/Symbian/scripts/apply-htcleo-aknappui-baseconstruct-durable-log.py"
aknappui_homescreen_baseconstruct_trace_transform="$project/Symbian/scripts/apply-htcleo-aknappui-homescreen-baseconstruct-trace.py"
aknappui_homescreen_postcoe_trace_transform="$project/Symbian/scripts/apply-htcleo-aknappui-homescreen-postcoe-trace.py"
aknappui_homescreen_focus_keyblock_transform="$project/Symbian/scripts/apply-htcleo-aknappui-homescreen-focus-keyblock-compat.py"
avkon_focus_touch_rearm_transform="$project/Symbian/scripts/apply-htcleo-avkon-focus-touch-rearm-entry.py"
clock_watch_transform="$project/Symbian/scripts/apply-htcleo-clock-watch.py"
aknappui_homescreen_focus_log_route_transform="$project/Symbian/scripts/apply-htcleo-aknappui-homescreen-focus-log-route.py"
aknappui_homescreen_foreground_trace_transform="$project/Symbian/scripts/apply-htcleo-aknappui-homescreen-foreground-trace.py"
aknsgc_homescreen_system_fade_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-homescreen-system-fade-handle-compat.py"
aknappui_matrixmenu_ui_first_transform="$project/Symbian/scripts/apply-htcleo-aknappui-matrixmenu-ui-first-compat.py"
aknappui_postcoe_layout_transform="$project/Symbian/scripts/apply-htcleo-aknappui-postcoe-layout-durable-log.py"
aknappui_matrixmenu_postcoe_fixed_transform="$project/Symbian/scripts/apply-htcleo-aknappui-matrixmenu-postcoe-fixed-screen.py"
aknsgc_matrixmenu_setparams_defer_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-matrixmenu-setparams-defer.py"
aknsgc_homescreen_setparams_defer_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-homescreen-setparams-defer.py"
aknenv_matrixmenu_transform="$project/Symbian/scripts/apply-htcleo-aknenv-matrixmenu-durable-log.py"
aknenv_matrixmenu_cdl_reconnect_transform="$project/Symbian/scripts/apply-htcleo-aknenv-matrixmenu-cdl-reconnect.py"
aknenv_homescreen_trace_cdl_reconnect_transform="$project/Symbian/scripts/apply-htcleo-aknenv-homescreen-trace-cdl-reconnect.py"
aknsgc_matrixmenu_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-matrixmenu-durable-log.py"
aknsgc_matrixmenu_akncap_failopen_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-matrixmenu-akncap-fail-open.py"
aknsgc_homescreen_trace_akncap_failopen_transform="$project/Symbian/scripts/apply-htcleo-aknsgc-homescreen-trace-akncap-fail-open.py"
akngrid_matrixmenu_background_transform="$project/Symbian/scripts/apply-htcleo-akngrid-preserve-cpu-background.py"
stem_avkon_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
stem_avkon_viewappui_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknViewAppUi.cpp"
stem_avkon_aknenv_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknenv.cpp"
stem_avkon_sgc_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
stem_avkon_lists_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknlists.cpp"
stem_avkon_grid_source="$full_epocroot/sf/mw/classicui/uifw/AvKon/src/akngridview.cpp"
stem_avkon_mmp="$full_epocroot/sf/incubator/stemkit/breakdeps/avkon.mmp"
stem_avkon_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/stem-avkon-build/bld.inf"
stem_avkon_config_path="$project/Symbian/config"
stem_avkon_config=arm.v5.urel.gcce4_4_1.avkon_permissive
stem_avkon_config_file="$stem_avkon_config_path/avkon-gcce.xml"
stem_avkon_cc_wrapper="$project/Symbian/scripts/htcleo-gcce-avkon-cc-wrapper.sh"
stem_avkon_abi_promoter="$project/Symbian/scripts/promote-htcleo-avkon-frozen-abi.py"
stem_avkon_abi_audit="$project/Symbian/scripts/audit-htcleo-avkon-abi.py"
stem_avkon_frozen_def="$full_epocroot/sf/mw/classicui/uifw/AvKon/EABI/AVKONU.DEF"
stem_avkon_frozen_def_alias="$full_epocroot/sf/mw/classicui/uifw/AvKon/EABI/AVKONu.DEF"
stem_avkon_binary="$full_epocroot/epoc32/release/armv5/urel/stem_avkon.dll"
stem_avkon_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/474-stem-avkon-parent.txt"
stem_avkon_stock_473="$output/stem-avkon-stock-473.dll"
stem_avkon_stock_473_dump_input="$work/stem-avkon-stock-473.dll"
eiksrvui_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/stem-eiksrvui-build/bld.inf"
eiksrvui_binary="$full_epocroot/epoc32/release/armv5/urel/stem_eiksrvui.dll"
eiksrvui_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/456-stem-eiksrvui-parent.txt"
eiksrvui_initialize_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/467-stem-eiksrvui-parent.txt"
c32_component="$full_epocroot/sf/os/commsfw/commsprocess/commsrootserverconfig"
c32root_source="$c32_component/rootsrv/c32root.cpp"
c32start_source="$c32_component/configurator/src/c32start.cpp"
c32root_mmp="$c32_component/group/c32root.mmp"
c32_transform="$project/Symbian/scripts/apply-htcleo-c32-startup-durable-log.py"
c32_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/c32-startup-build/bld.inf"
c32root_binary="$full_epocroot/epoc32/release/armv5/urel/c32root.dll"
c32start_binary="$full_epocroot/epoc32/release/armv5/urel/c32start.exe"
c32root_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/468-c32root-parent.txt"
c32start_parent="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/468-c32start-parent.txt"
c32root_stock_468="$output/c32root-stock-468.dll"
c32start_stock_468="$output/c32start-stock-468.exe"
aknskins_component="$full_epocroot/sf/mw/uiresources/skins/AknSkins"
aknskinsrv_source="$aknskins_component/srvsrc/AknsSrv.cpp"
aknskinsrv_client_source="$aknskins_component/srvsrc/AknsSrvClient.cpp"
aknskinsrv_settings_source="$aknskins_component/srvsrc/AknsSrvSettings.cpp"
aknskinsrv_mxml_compat="$aknskins_component/srvinc/MXMLAttributes.h"
aknskinsrv_mmp="$aknskins_component/group/AknSkinSrv.mmp"
aknskinsrv_frozen_def="$aknskins_component/EABI/AKNSKINSRVU.DEF"
aknskinsrv_transform="$project/Symbian/scripts/apply-htcleo-aknskinsrv-durable-log.py"
aknskinsrv_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/aknskinsrv-build/bld.inf"
aknskinsrv_binary="$full_epocroot/epoc32/release/armv5/urel/AKNSKINSRV.dll"
aknskinsrv_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/458-aknskinsrv-parent.txt"
featmgr_component="$full_epocroot/sf/os/persistentdata/featuremgmt/featuremgr"
featmgr_source="$featmgr_component/src/clientdll/featmgr.cpp"
featmgr_tls_source="$featmgr_component/src/clientdll/featmgrtlsdata.cpp"
featmgr_client_source="$featmgr_component/src/clientdll/featmgrclient.cpp"
featmgr_header="$featmgr_component/src/inc/htcleo_featmgr_trace.h"
featmgr_mmp="$featmgr_component/group/featmgr.mmp"
featmgr_frozen_def="$featmgr_component/eabi/featmgru.def"
featmgr_transform="$project/Symbian/scripts/apply-htcleo-featmgr-akncap-trace.py"
featmgr_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/featmgr-build/bld.inf"
featmgr_binary="$full_epocroot/epoc32/release/armv5/urel/featmgr.dll"
featmgr_stock_444="$output/featmgr-stock-444.dll"
featmgrserver_source="$featmgr_component/src/serverexe/featmgrserver.cpp"
featmgrserver_startup_source="$featmgr_component/src/serverexe/featmgrstartup.cpp"
featmgrserver_header="$featmgr_component/src/inc/htcleo_featmgrserver_trace.h"
featmgrserver_mmp="$featmgr_component/group/featmgrserver.mmp"
featmgrserver_transform="$project/Symbian/scripts/apply-htcleo-featmgrserver-startup-fix-trace.py"
featmgrserver_loadplugins_transform="$project/Symbian/scripts/apply-htcleo-featmgrserver-loadplugins-trace.py"
featmgrserver_zero_plugin_transform="$project/Symbian/scripts/apply-htcleo-featmgrserver-zero-plugin-compat.py"
featmgrserver_binary="$full_epocroot/epoc32/release/armv5/urel/featmgrserver.exe"
featmgrserver_stock_445="$output/featmgrserver-stock-445.exe"
akn_custom_component="$full_epocroot/sf/mw/classicui/uifw/AknGlobalUI/akncustcmds"
akn_custom_source="$akn_custom_component/src/akncapserverstart.cpp"
akn_custom_mmp="$akn_custom_component/group/akncustcmds.mmp"
akn_custom_bldinf="$akn_custom_component/group/bld.inf"
akn_custom_binary="$full_epocroot/epoc32/release/armv5/urel/akncustcmds.dll"
stem_state_transform="$project/Symbian/scripts/apply-htcleo-disable-cooperating-state-change.py"
stem_startup_mode_transform="$project/Symbian/scripts/apply-htcleo-local-normal-startup-mode.py"
stem_splash_transform="$project/Symbian/scripts/apply-htcleo-disable-splashscreen.py"
stem_resource_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/stemkit-resource-build/bld.inf"
stem_critical_cmdlist_source="$full_epocroot/sf/incubator/stemkit/startup/stem_criticalappscmdlist.rss"
stem_noncritical_cmdlist_source="$full_epocroot/sf/incubator/stemkit/startup/stem_noncriticalcmdlist.rss"
stem_startup_dir="$full_epocroot/sf/incubator/stemkit/startup"
stem_cone_component="$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone"
stem_cone_source="$stem_cone_component/src/COEPRIV.CPP"
stem_cone_main_source="$stem_cone_component/src/COEMAIN.CPP"
stem_cone_appui_source="$stem_cone_component/src/COEAUI.CPP"
stem_cone_envextra_source="$stem_cone_component/src/CoeEnvExtra.cpp"
stem_cone_transform="$project/Symbian/scripts/apply-htcleo-cone-redrawer-arm-before-ready.py"
stem_cone_event_transform="$project/Symbian/scripts/apply-htcleo-cone-event-pump-durable-trace.py"
stem_cone_ready_ao_transform="$project/Symbian/scripts/apply-htcleo-cone-ready-ao-identity-trace.py"
stem_cone_homescreen_ao_transform="$project/Symbian/scripts/apply-htcleo-cone-homescreen-ao-trace.py"
stem_cone_homescreen_foreground_transform="$project/Symbian/scripts/apply-htcleo-cone-homescreen-foreground-trace.py"
stem_cone_ready_ao_source="$stem_cone_component/src/htcleoschedulertrace.cpp"
stem_cone_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/stem-cone-build/bld.inf"
stem_cone_binary="$full_epocroot/epoc32/release/armv5/urel/stem_cone.dll"
stem_cone_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/592-stem-cone-parent.txt"
stem_cone_stock_592="$output/stem-cone-stock-592.dll"
liw_component="$full_epocroot/sf/mw/serviceapifw/languageinterworkingfw/servicehandler"
liw_monitor_source="$liw_component/src/liwecommonitor.cpp"
liw_monitor_transform="$project/Symbian/scripts/apply-htcleo-liw-ecom-monitor-status-guard.py"
liw_bldinf="$liw_component/group/bld.inf"
liw_binary="$full_epocroot/epoc32/release/armv5/urel/liwServiceHandler.dll"
liw_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/669-liwservicehandler-parent.txt"
liw_stock_669="$output/liwservicehandler-stock-669.dll"
matrixmenu_component="$full_epocroot/sf/app/homescreen/menufw/menufwui/matrixmenu"
matrixmenu_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-durable-log.py"
matrixmenu_log_capacity_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-log-capacity-expand.py"
matrixmenu_log_capacity_1m_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-log-capacity-1m.py"
matrixmenu_scheduler_kick_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-scheduler-entry-kick.py"
matrixmenu_initial_statuslayout_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-initial-statuslayout-defer.py"
matrixmenu_dummy_grid_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-dummy-grid-result-trace.py"
matrixmenu_dummy_container_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-dummy-container-bypass.py"
matrixmenu_hnengine_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-hnengine-result-trace.py"
matrixmenu_postinit_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-postinit-ui-first-defer.py"
matrixmenu_late_haze_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-late-haze-activation.py"
matrixmenu_haze_notify_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-haze-notify-redraw.py"
matrixmenu_first_container_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-synchronous-first-container.py"
matrixmenu_full_grid_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-full-grid-invalidation.py"
matrixmenu_ui_first_container_compat_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-ui-first-container-compat.py"
matrixmenu_rom_presentation_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-rom-presentation-fallback.py"
matrixmenu_first_frame_finish_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-first-frame-finish.py"
matrixmenu_precontainer_suite_init_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-precontainer-suite-init-defer.py"
matrixmenu_runtime_event_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-runtime-event-trace.py"
matrixmenu_redundant_focus_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-redundant-focus-fastpath.py"
matrixmenu_focus_quarantine_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-focus-quarantine.py"
matrixmenu_focus_restore_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-focus-restore-attribution.py"
matrixmenu_stale_focus_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-stale-focus-no-redraw.py"
matrixmenu_shell_transition_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-shell-transition-trace.py"
matrixmenu_noncellular_return_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-permanent-noncellular-return.py"
matrixmenu_home_ordinal_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-home-priority-safe-ordinal.py"
matrixmenu_home_async_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-home-handoff-async.py"
matrixmenu_home_owning_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-home-owning-window-switch.py"
matrixmenu_home_owner_binding_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-home-owner-binding.py"
matrixmenu_native_activation_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-native-message-activation.py"
matrixmenu_scheduler_retirement_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-scheduler-log-retirement.py"
matrixmenu_visual_skin_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-skin-refresh-without-requery.py"
matrixmenu_exception_type_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-exception-type-trace.py"
matrixmenu_abort_stack_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-abort-stack-trace.py"
matrixmenu_terminate_retirement_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-terminate-handler-retirement.py"
matrixmenu_caller_stack_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-caller-stack-trace.py"
matrixmenu_startup_foreground_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-startup-foreground-commit.py"
matrixmenu_foreground_ordinal_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-foreground-ordinal-no-system-event.py"
matrixmenu_redundant_ordinal_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-skip-redundant-foreground-ordinal.py"
matrixmenu_final_cba_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-final-cba-commit.py"
ui_frame_stage_correlation_transform="$project/Symbian/scripts/apply-htcleo-ui-frame-stage-correlation.py"
matrixmenu_stack_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-stack-headroom.py"
matrixmenu_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/matrixmenu-build/bld.inf"
matrixmenu_config_path="$project/Symbian/config"
matrixmenu_config=arm.v5.urel.gcce4_4_1.matrixmenu_permissive
matrixmenu_config_file="$matrixmenu_config_path/matrixmenu-gcce.xml"
matrixmenu_mmp="$matrixmenu_component/group/matrixmenu.mmp"
matrixmenu_entry_source="$matrixmenu_component/src/mmgui.cpp"
matrixmenu_app_source="$matrixmenu_component/src/mmapplication.cpp"
matrixmenu_document_source="$matrixmenu_component/src/mmdocument.cpp"
matrixmenu_appui_source="$matrixmenu_component/src/mmappui.cpp"
matrixmenu_appui_header="$matrixmenu_component/inc/mmappui.h"
matrixmenu_touch_suite="$full_epocroot/epoc32/data/z/private/101F4CD2/import/suites/foldersuite_touch/suite.xml"
matrixmenu_logger_source="$matrixmenu_component/src/htcleomenulog.cpp"
matrixmenu_binary="$full_epocroot/epoc32/release/armv5/urel/matrixmenu.exe"
matrixmenu_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/492-matrixmenu-parent.txt"
matrixmenu_stock_492="$output/matrixmenu-stock-492.exe"
homescreen_component="$full_epocroot/sf/mw/homescreensrv/idlefw"
homescreen_log_transform="$project/Symbian/scripts/apply-htcleo-homescreen-durable-log.py"
homescreen_launch_transform="$project/Symbian/scripts/apply-htcleo-stem-homescreen-launch.py"
homescreen_late_launch_transform="$project/Symbian/scripts/apply-htcleo-stem-homescreen-late-launch.py"
homescreen_post_launch_transform="$project/Symbian/scripts/apply-htcleo-stem-homescreen-post-matrixmenu-launch.py"
homescreen_controller_transform="$project/Symbian/scripts/apply-htcleo-homescreen-controller-trace.py"
homescreen_restart_transform="$project/Symbian/scripts/apply-htcleo-homescreen-bounded-restart.py"
homescreen_exit_category_transform="$project/Symbian/scripts/apply-htcleo-homescreen-exit-category-trace.py"
homescreen_closure_audit="$project/Symbian/scripts/audit-htcleo-homescreen-import-closure.py"
homescreen_closure_report="$output/HOMESCREEN-CLOSURE-AUDIT.txt"
homescreen_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/homescreen-build/bld.inf"
homescreen_main_source="$homescreen_component/src/framework/main.cpp"
homescreen_aifw_source="$homescreen_component/src/framework/aifw.cpp"
homescreen_controller_source="$homescreen_component/src/framework/aiuicontrollermanager.cpp"
homescreen_idle_source="$homescreen_component/src/idleint/aiidleappregister.cpp"
homescreen_launch_source="$homescreen_component/hslaunch/src/hslaunch.cpp"
homescreen_logger_source="$homescreen_component/src/common/htcleohomelog.cpp"
homescreen_aifw_binary="$full_epocroot/epoc32/release/armv5/urel/aifw.dll"
homescreen_idle_binary="$full_epocroot/epoc32/release/armv5/urel/aiidleint.dll"
homescreen_launch_binary="$full_epocroot/epoc32/release/armv5/urel/ailaunch.exe"
homescreen_binary="$full_epocroot/epoc32/release/armv5/urel/homescreen.exe"
homescreen_aifw_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/670-aifw-parent.txt"
homescreen_idle_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/670-aiidleint-parent.txt"
homescreen_launch_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/670-ailaunch-parent.txt"
homescreen_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/670-homescreen-parent.txt"
homescreen_aifw_stock_670="$output/aifw-stock-670.dll"
homescreen_idle_stock_670="$output/aiidleint-stock-670.dll"
homescreen_launch_stock_670="$output/ailaunch-stock-670.exe"
homescreen_stock_670="$output/homescreen-stock-670.exe"
ai3xml_component="$full_epocroot/sf/app/homescreen/idlehomescreen/xmluicontroller"
ai3xml_trace_transform="$project/Symbian/scripts/apply-htcleo-ai3xmluimain-startup-trace.py"
ai3xml_onlineoffline_transform="$project/Symbian/scripts/apply-htcleo-ai3xml-onlineoffline-optional.py"
ai3xml_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/ai3xmluimain-build/bld.inf"
ai3xml_mmp="$ai3xml_component/group/aixmluimain.mmp"
ai3xml_controller_source="$ai3xml_component/src/xmluicontroller.cpp"
ai3xml_application_source="$ai3xml_component/src/application.cpp"
ai3xml_document_source="$ai3xml_component/src/document.cpp"
ai3xml_appui_source="$ai3xml_component/src/appui.cpp"
ai3xml_contentpublisher_source="$ai3xml_component/src/contentpublisher.cpp"
ai3xml_logger_source="$ai3xml_component/src/htcleoai3xmllog.cpp"
ai3xml_binary="$full_epocroot/epoc32/release/armv5/urel/ai3xmluimain.dll"
ai3xml_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/675-ai3xmluimain-parent.txt"
ai3xml_stock_675="$output/ai3xmluimain-stock-675.dll"
xn3layout_component="$full_epocroot/sf/app/homescreen/idlehomescreen/xmluirendering/uiengine"
xn3layout_trace_transform="$project/Symbian/scripts/apply-htcleo-xnappuiadapter-startup-trace.py"
xn3layout_impl_trace_transform="$project/Symbian/scripts/apply-htcleo-xnappuiadapterimpl-startup-trace.py"
xn3layout_loadui_trace_transform="$project/Symbian/scripts/apply-htcleo-xnviewmanager-loadui-trace.py"
xn3layout_view_load_trace_transform="$project/Symbian/scripts/apply-htcleo-xnodtparser-view-load-trace.py"
xn3layout_transient_view_transform="$project/Symbian/scripts/apply-htcleo-xnroot-transient-view-preserve.py"
xn3layout_nonvisual_factory_transform="$project/Symbian/scripts/apply-htcleo-xnodtparser-nonvisual-factory-failopen.py"
xn3layout_zero_factory_general_transform="$project/Symbian/scripts/apply-htcleo-xnodtparser-zero-factory-general-node.py"
xn3layout_metadata_factory_transform="$project/Symbian/scripts/apply-htcleo-xnodtparser-metadata-factory-failopen.py"
xn3layout_menu_group_transform="$project/Symbian/scripts/apply-htcleo-xnodtparser-menu-group-failopen.py"
homescreen_high_frequency_log_retirement_transform="$project/Symbian/scripts/apply-htcleo-homescreen-high-frequency-log-retirement.py"
xn_hd2_client_geometry_transform="$project/Symbian/scripts/apply-htcleo-xn-hd2-client-geometry.py"
xn_client_window_commit_transform="$project/Symbian/scripts/apply-htcleo-xn-client-window-commit.py"
home_msk_center_transform="$project/Symbian/scripts/apply-htcleo-home-msk-center.py"
home_native_focus_transform="$project/Symbian/scripts/apply-htcleo-home-native-focus-state.py"
home_liveness_transform="$project/Symbian/scripts/apply-htcleo-home-liveness-evidence.py"
wserv_shell_handoff_transform="$project/Symbian/scripts/apply-htcleo-wserv-shell-handoff-trace.py"
wserv_nonblocking_log_transform="$project/Symbian/scripts/apply-htcleo-wserv-nonblocking-log.py"
wserv_worker_retirement_transform="$project/Symbian/scripts/apply-htcleo-wserv-worker-retirement.py"
shell_pointer_log_retirement_transform="$project/Symbian/scripts/apply-htcleo-shell-pointer-log-retirement.py"
ui_742_control_pin="$project/Symbian/scripts/pin-htcleo-742-ui-controls.py"
ui_743_xn_focus_promoter="$project/Symbian/scripts/promote-htcleo-743-xn-native-focus-control.py"
matrixmenu_focus_touch_rearm_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-touch-rearm.py"
hspsprovider_log_retirement_transform="$project/Symbian/scripts/apply-htcleo-hspsprovider-log-retirement.py"
wserv_low_rate_touch_transform="$project/Symbian/scripts/apply-htcleo-wserv-low-rate-touch-heartbeat.py"
xn3layout_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/xn3layoutengine-build/bld.inf"
xn3layout_mmp="$xn3layout_component/group/xnlayoutengine.mmp"
xn3layout_source="$xn3layout_component/src/xnappuiadapter.cpp"
xn3layout_impl_source="$xn3layout_component/src/xnappuiadapterimpl.cpp"
xn3layout_viewmanager_source="$xn3layout_component/src/xnviewmanager.cpp"
xn3layout_rootdata_source="$xn3layout_component/src/xnrootdata.cpp"
xn3layout_composer_source="$xn3layout_component/src/xncomposer.cpp"
xn3layout_odtparser_source="$xn3layout_component/src/xnodtparser.cpp"
xn3layout_viewdata_source="$xn3layout_component/src/xnviewdata.cpp"
xn3layout_mxml_header="$xn3layout_component/inc/MXMLAttributes.h"
xn3layout_binary="$full_epocroot/epoc32/release/armv5/urel/xn3layoutengine.dll"
xn3layout_frozen_def="$xn3layout_component/eabi/xn3layoutengineu.def"
xn3layout_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/680-xn3layoutengine-parent.txt"
xn3layout_stock_680="$output/xn3layoutengine-stock-680.dll"
xn3layout_stock_dump_input="$work/xn3layoutengine-stock-680.dll"
xn3layout_config_path="$project/Symbian/config"
xn3layout_config=arm.v5.urel.gcce4_4_1.xn3layoutengine_permissive
xn3layout_config_file="$xn3layout_config_path/xn3layoutengine-gcce.xml"
xn3layout_cc_wrapper="$project/Symbian/scripts/htcleo-gcce-xn3layoutengine-cc-wrapper.sh"
xn3layout_abi_promoter="$project/Symbian/scripts/promote-htcleo-xn3layoutengine-frozen-abi.py"
xn3layout_abi_audit="$project/Symbian/scripts/audit-htcleo-xn3layoutengine-abi.py"
xn3utils_stock_binary="$full_epocroot/epoc32/release/armv5/urel/xn3utils.dll"
xn3utils_stock_sha256=fc978092e1ae97f2fea7768662f7b2840153942d0e1c51ecb6f9d6cc22f045c2
hspluginsettings_component="$full_epocroot/sf/mw/homescreensrv/homescreenpluginsrv/homescreen_settings_api"
hspluginsettings_source="$hspluginsettings_component/src/hspluginsettings.cpp"
hspluginsettings_mmp="$hspluginsettings_component/group/hspluginsettings.mmp"
hspluginsettings_frozen_def="$hspluginsettings_component/eabi/hspluginsettings.def"
hspluginsettings_transform="$project/Symbian/scripts/apply-htcleo-hspluginsettings-startup-trace.py"
hspluginsettings_abi_audit="$project/Symbian/scripts/audit-htcleo-hspluginsettings-abi.py"
hspluginsettings_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/hspluginsettings-build/bld.inf"
hspluginsettings_binary="$full_epocroot/epoc32/release/armv5/urel/hspluginsettings.dll"
hspluginsettings_config_path="$project/Symbian/config"
hspluginsettings_config=arm.v5.urel.gcce4_4_1.hspluginsettings_permissive
hspluginsettings_config_file="$hspluginsettings_config_path/hspluginsettings-gcce.xml"
hspluginsettings_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/689-hspluginsettings-parent.txt"
hspluginsettings_stock_689="$output/hspluginsettings-stock-689.dll"
hspluginsettings_stock_dump_input="$work/hspluginsettings-stock-689.dll"
hspsthemeserver_component="$full_epocroot/sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager"
hspsthemeserver_source="$hspsthemeserver_component/src/hspsthemeserver.cpp"
hspsthemeserver_family_source="$hspsthemeserver_component/src/hspsfamily.cpp"
hspsthemeserver_rominstaller_source="$hspsthemeserver_component/src/hspsrominstaller.cpp"
hspsthemeserver_installation_source="$hspsthemeserver_component/src/hspsinstallationhandler.cpp"
hspsthemeserver_mmp="$hspsthemeserver_component/group/hspsthemeserver.mmp"
hspsthemeserver_transform="$project/Symbian/scripts/apply-htcleo-hspsthemeserver-hd2-family-compat.py"
hspsthemeserver_skeleton_trace_transform="$project/Symbian/scripts/apply-htcleo-hsps-install-skeleton-trace.py"
hspsthemeserver_root_self_heal_transform="$project/Symbian/scripts/apply-htcleo-hsps-active-root-self-heal.py"
hspsthemeserver_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/hspsthemeserver-build/bld.inf"
hspsthemeserver_binary="$full_epocroot/epoc32/release/armv5/urel/hspsthemeserver.exe"
hspsthemeserver_config_path="$project/Symbian/config"
hspsthemeserver_config=arm.v5.urel.gcce4_4_1.hspsthemeserver_permissive
hspsthemeserver_config_file="$hspsthemeserver_config_path/hspsthemeserver-gcce.xml"
hspsthemeserver_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/690-hspsthemeserver-parent.txt"
hspsthemeserver_stock_690="$output/hspsthemeserver-stock-690.exe"
hspsthemeserver_stock_dump_input="$work/hspsthemeserver-stock-690.exe"
hsps_definition_component="$full_epocroot/sf/mw/homescreensrv/homescreenpluginsrv/hspsdefinitionengine/hspsdefinitionengine"
hsps_definition_source="$hsps_definition_component/src/hspsdefinitionengine.cpp"
hsps_definition_proxy_source="$hsps_definition_component/src/hspsdefinitionengineproxy.cpp"
hsps_definition_mmp="$hsps_definition_component/group/hspsdefinitionengine.mmp"
hsps_definition_bldinf="$hsps_definition_component/group/bld.inf"
hsps_definition_binary="$full_epocroot/epoc32/release/armv5/urel/hspsdefinitionengine.dll"
hsps_definition_transform="$project/Symbian/scripts/apply-htcleo-hspsdefinitionengine-lazy-parser.py"
hsps_definition_ecom_recovery_transform="$project/Symbian/scripts/apply-htcleo-hspsdefinitionengine-ecom-recovery-trace.py"
hsps_definition_libxml_closure_transform="$project/Symbian/scripts/apply-htcleo-hspsdefinitionengine-libxml-rom-closure.py"
hsps_definition_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/697-hspsdefinitionengine-parent.txt"
hsps_definition_stock_697="$output/hspsdefinitionengine-stock-697.dll"
hsps_definition_stock_dump_input="$work/hspsdefinitionengine-stock-697.dll"
libxml_sax_binary="$full_epocroot/epoc32/release/armv5/urel/xmlenginesaxplugin.dll"
libxml_sax_resource="$full_epocroot/epoc32/data/z/resource/plugins/xmlenginesaxplugin.rsc"
libxml_sax_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/701-xmlenginesaxplugin-parent.txt"
hspsprovider_component="$full_epocroot/sf/mw/homescreensrv/homescreensrv_plat/sapi_homescreenplugin"
hspsprovider_source="$hspsprovider_component/src/hspsliwutilities.cpp"
hspsprovider_mmp="$hspsprovider_component/group/hspsprovider.mmp"
hspsprovider_transform="$project/Symbian/scripts/apply-htcleo-hspsprovider-plugin-map-compat.py"
hspsprovider_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/hspsprovider-build/bld.inf"
hspsprovider_binary="$full_epocroot/epoc32/release/armv5/urel/hspsprovider.dll"
hspsprovider_resource="$full_epocroot/epoc32/data/z/resource/plugins/hspsprovider.rsc"
hspsprovider_config_path="$project/Symbian/config"
hspsprovider_config=arm.v5.urel.gcce4_4_1.hspsprovider_permissive
hspsprovider_config_file="$hspsprovider_config_path/hspsprovider-gcce.xml"
hspsprovider_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/703-hspsprovider-parent.txt"
hspsprovider_stock_703="$output/hspsprovider-stock-703.dll"
hspsprovider_stock_resource_703="$output/hspsprovider-stock-703.rsc"
hspsprovider_stock_dump_input="$work/hspsprovider-stock-703.dll"
mmwidgets_component="$full_epocroot/sf/app/homescreen/menufw/menufwui/mmwidgets"
mmwidgets_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-dummy-grid-durable-log.py"
mmwidgets_grid_handle_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-grid-window-handle-publish.py"
mmwidgets_haze_background_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-haze-screen-background.py"
mmwidgets_cpu_haze_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-cpu-haze-background.py"
mmwidgets_full_wallpaper_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-full-client-wallpaper.py"
mmwidgets_touch_diagnostic_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-touch-diagnostic.py"
mmwidgets_deferred_ao_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-postprocess-ao-trace.py"
mmwidgets_post_bounds_transform="$project/Symbian/scripts/apply-htcleo-mmwidgets-postprocess-bounds-guard.py"
mmwidgets_bldinf="$mmwidgets_component/group/bld.inf"
mmwidgets_mmp="$mmwidgets_component/group/mmwidgets.mmp"
mmwidgets_widget_source="$mmwidgets_component/src/mmwidgetcontainer.cpp"
mmwidgets_grid_source="$mmwidgets_component/src/mmgridcontainer.cpp"
mmwidgets_post_source="$mmwidgets_component/src/mmpostevaluationprocessor.cpp"
mmwidgets_drawer_source="$mmwidgets_component/src/mmdraweranimator.cpp"
mmwidgets_grid_control_source="$mmwidgets_component/src/mmgrid.cpp"
mmwidgets_logger_source="$mmwidgets_component/src/htcleommwlog.cpp"
mmwidgets_binary="$full_epocroot/epoc32/release/armv5/urel/mmwidgets.dll"
mmwidgets_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/525-mmwidgets-parent.txt"
mmwidgets_stock_525="$output/mmwidgets-stock-525.dll"
hnengine_component="$full_epocroot/sf/app/homescreen/menufw/hierarchynavigator/hnengine"
hnengine_transform="$project/Symbian/scripts/apply-htcleo-hnengine-durable-log.py"
hnengine_initialize_transform="$project/Symbian/scripts/apply-htcleo-hnengine-initialize-durable-log.py"
hnengine_bldinf="$hnengine_component/group/bld.inf"
hnengine_mmp="$hnengine_component/group/hnengine.mmp"
hnengine_source="$hnengine_component/src/hnengine.cpp"
hnengine_binary="$full_epocroot/epoc32/release/armv5/urel/hnengine.dll"
hnengine_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/528-hnengine-parent.txt"
hnengine_stock_528="$output/hnengine-stock-528.dll"
hnmetadata_component="$full_epocroot/sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel"
hnmetadata_transform="$project/Symbian/scripts/apply-htcleo-hnmetadatamodel-durable-log.py"
hnmetadata_showfolder_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-showfolder-defer.py"
hnmetadata_evaluation_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-evaluation-durable-log.py"
hnmetadata_capacity_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-log-capacity-expand.py"
hnmetadata_notify_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-notify-ui-first-compat.py"
hnmetadata_initial_coalesce_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-coalesce-initial-notification.py"
hnmetadata_capacity_1m_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-log-capacity-1m.py"
hnmetadata_retire_redundant_refresh_transform="$project/Symbian/scripts/apply-htcleo-hnmetadata-retire-redundant-refresh.py"
hnmetadata_bldinf="$hnmetadata_component/group/bld.inf"
hnmetadata_mmp="$hnmetadata_component/group/hnmetadatamodel.mmp"
hnmetadata_source="$hnmetadata_component/src/hnmdmodel.cpp"
hnmetadata_suite_source="$hnmetadata_component/src/hnmdsuite.cpp"
hnmetadata_query_source="$hnmetadata_component/src/hnqueryresultcollector.cpp"
hnmetadata_item_source="$hnmetadata_component/src/hnmditem.cpp"
hnmetadata_query_header="$hnmetadata_component/inc/hnqueryresultcollector.h"
hnmetadata_notify_source="$hnmetadata_component/src/hnmdnotifyrequests.cpp"
hnmetadata_notify_request_source="$hnmetadata_component/src/hnmdnotifyrequest.cpp"
hnmetadata_notify_request_header="$hnmetadata_component/inc/hnmdnotifyrequest.h"
hnmetadata_binary="$full_epocroot/epoc32/release/armv5/urel/hnmetadatamodel.dll"
hnmetadata_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/529-hnmetadatamodel-parent.txt"
hnmetadata_stock_529="$output/hnmetadatamodel-stock-529.dll"
mcsmenu_component="$full_epocroot/sf/mw/homescreensrv/menucontentsrv"
mcsmenu_transform="$project/Symbian/scripts/apply-htcleo-mcs-ui-first-compat.py"
mcsmenu_apparc_transform="$project/Symbian/scripts/apply-htcleo-mcs-apparc-ui-first-failopen.py"
mcsmenu_engine_transform="$project/Symbian/scripts/apply-htcleo-menueng-durable-log.py"
mcsmenu_ram_fallback_transform="$project/Symbian/scripts/apply-htcleo-menueng-ram-missing-rom-fallback.py"
mcsmenu_first_change_transform="$project/Symbian/scripts/apply-htcleo-menueng-first-change-ram-commit.py"
mcsmenu_context_transform="$project/Symbian/scripts/apply-htcleo-mcs-server-context-trace.py"
mcsmenu_startup_no_io_transform="$project/Symbian/scripts/apply-htcleo-mcs-startup-no-file-io.py"
mcsmenu_pid_ready_transform="$project/Symbian/scripts/apply-htcleo-mcs-pid-ready-handshake.py"
mcsmenu_persistent_server_transform="$project/Symbian/scripts/apply-htcleo-mcsmenu-persistent-server.py"
mcsmenu_scanner_optional_transform="$project/Symbian/scripts/apply-htcleo-mcs-scanner-optional-construct-failopen.py"
mcsmenu_apparc_retry_transform="$project/Symbian/scripts/apply-htcleo-mcs-apparc-bounded-retry.py"
mcsmenu_apparc_returned_retry_transform="$project/Symbian/scripts/apply-htcleo-mcs-apparc-returned-retry.py"
mcsmenu_apparc_restart_transform="$project/Symbian/scripts/apply-htcleo-mcs-apparc-server-restart.py"
mcsmenu_hn_ready_transform="$project/Symbian/scripts/apply-htcleo-mcs-hn-ready-generation.py"
hn_ready_request_guard_transform="$project/Symbian/scripts/apply-htcleo-hn-ready-generation-request-guard.py"
mcsmenu_hn_ready_signal_transform="$project/Symbian/scripts/apply-htcleo-mcs-hn-ready-property-subscribe.py"
mcsmenu_hn_commit_requery_transform="$project/Symbian/scripts/apply-htcleo-menueng-hn-commit-requery.py"
mcsmenu_getlist_count_transform="$project/Symbian/scripts/apply-htcleo-mcs-getlist-count-property.py"
mcsmenu_getlist_session_transform="$project/Symbian/scripts/apply-htcleo-mcs-getlist-session-buffer.py"
mcsmenu_getlist_session_v2_transform="$project/Symbian/scripts/apply-htcleo-mcs-getlist-session-buffer-v2.py"
mcsmenu_getlist_atomic_transform="$project/Symbian/scripts/apply-htcleo-mcs-getlist-atomic-transfer.py"
hn_getlist_synchronous_transform="$project/Symbian/scripts/apply-htcleo-hn-getlist-synchronous.py"
hn_sync_completion_transform="$project/Symbian/scripts/apply-htcleo-hn-sync-completion-queued-runl.py"
hn_sync_direct_safe_transform="$project/Symbian/scripts/apply-htcleo-hn-sync-direct-safe-tail.py"
hn_getlist_provider_sync_pump_transform="$project/Symbian/scripts/apply-htcleo-hn-getlist-provider-sync-pump-mode.py"
hn_results_consumption_transform="$project/Symbian/scripts/apply-htcleo-hn-results-consumption-trace.py"
mcsservice_component="$full_epocroot/sf/mw/homescreensrv/homescreensrv_plat/sapi_menucontent/mcsservice"
mcsservice_transform="$project/Symbian/scripts/apply-htcleo-mcs-getlist-sync-pump.py"
mcsservice_bldinf="$mcsservice_component/group/bld.inf"
mcsservice_mmp="$mcsservice_component/group/mcsservice.mmp"
mcsservice_source="$mcsservice_component/src/mcsgetlistimpl.cpp"
mcsservice_binary="$full_epocroot/epoc32/release/armv5/urel/mcsservice.dll"
mcs_notification_transform="$project/Symbian/scripts/apply-htcleo-mcs-notification-contract.py"
mcsprovider_binary="$full_epocroot/epoc32/release/armv5/urel/mcsprovider.dll"
mcsprovider_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/mcsprovider-build/bld.inf"
mcsprovider_pin="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/740-mcsprovider-parent.txt"
mcsprovider_resource="$full_epocroot/epoc32/data/z/resource/plugins/mcsprovider.rsc"
mcsprovider_stock="$output/mcsprovider-stock-739.dll"
mcsprovider_stock_resource="$output/mcsprovider-stock-739.rsc"
mcsservice_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/583-mcsservice-parent.txt"
mcsservice_stock_582="$output/mcsservice-stock-582.dll"
mcsmenu_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/mcsmenu-build/bld.inf"
mcsmenu_mmp="$mcsmenu_component/group/mcsmenu.mmp"
mcsmenu_core_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/mcsmenueng-build/bld.inf"
mcsmenu_core_mmp="$mcsmenu_component/group/mcsmenueng.mmp"
mcsmenu_engine_source="$mcsmenu_component/srvsrc/menusrveng.cpp"
mcsmenu_server_source="$mcsmenu_component/srvsrc/menusrv.cpp"
mcsmenu_menueng_source="$mcsmenu_component/engsrc/menueng.cpp"
mcsmenu_menueng_header="$mcsmenu_component/enginc/menuengobject.h"
mcsmenu_menueng_state_header="$mcsmenu_component/enginc/menueng.h"
mcsmenu_utils_source="$mcsmenu_component/srvsrc/menusrvengutils.cpp"
mcsmenu_utils_header="$mcsmenu_component/srvinc/menusrvengutils.h"
mcsmenu_scanner_source="$mcsmenu_component/srvsrc/menusrvappscanner.cpp"
mcsmenu_scanner_header="$mcsmenu_component/srvinc/menusrvappscanner.h"
mcsmenu_getlist_source="$mcsmenu_component/srvsrc/mcsgetlisthandler.cpp"
mcsmenu_api_source="$mcsmenu_component/src/menusapi.cpp"
mcsmenu_session_source="$mcsmenu_component/srvsrc/menusrvsession.cpp"
mcsmenu_session_header="$mcsmenu_component/srvinc/menusrvsession.h"
mcsmenu_binary="$full_epocroot/epoc32/release/armv5/urel/mcsmenu.dll"
mcsmenu_core_binary="$full_epocroot/epoc32/release/armv5/urel/mcsmenueng.dll"
mcsmenu_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/535-mcsmenu-parent.txt"
mcsmenu_stock_535="$output/mcsmenu-stock-535.dll"
menuhandler_binary="$full_epocroot/epoc32/release/armv5/urel/mcsmenuhandler.dll"
menuhandler_resource="$full_epocroot/epoc32/data/z/resource/plugins/mcsmenuhandler.rsc"
menuhandler_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/menuhandler-build/bld.inf"
menuhandler_pin="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/793-menuhandler-parent.txt"
menuhandler_stock="$output/mcsmenuhandler-stock-792.dll"
menuhandler_stock_resource="$output/mcsmenuhandler-stock-792.rsc"
mcsmenu_core_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/536-mcsmenueng-parent.txt"
mcsmenu_core_stock_536="$output/mcsmenueng-stock-536.dll"
ssm_binary="$full_epocroot/epoc32/release/armv5/urel/sysstatemgr.exe"
wserv_component="$full_epocroot/sf/os/graphics/windowing/windowserver"
wserv_main="$wserv_component/nga/SERVER/openwfc/WSTOP.CPP"
wserv_plugin_manager="$wserv_component/nga/SERVER/openwfc/wspluginmanager.cpp"
wserv_screen="$wserv_component/nga/SERVER/openwfc/screen.cpp"
wserv_screen_redraw="$wserv_component/nga/SERVER/openwfc/ScreenRedraw.cpp"
wserv_render_stage_manager="$wserv_component/nga/SERVER/renderstagemanager.cpp"
wserv_mmp="$wserv_component/group/openwfc/WServ_nga.MMP"
wserv_case_wrapper="$wserv_component/inc/Graphics/WSGRAPHICDRAWERINTERFACE.H"
wserv_constants_wrapper="$wserv_component/inc/graphics/windowserverconstants.h"
wserv_wstypes="$wserv_component/nga/SERVER/wstypes.h"
wserv_log_transform="$project/Symbian/scripts/apply-htcleo-wserv-durable-log.py"
wserv_plugin_transform="$project/Symbian/scripts/apply-htcleo-wserv-plugin-manager-progress.py"
wserv_screen_transform="$project/Symbian/scripts/apply-htcleo-wserv-screen-construct-progress.py"
wserv_client_window_transform="$project/Symbian/scripts/apply-htcleo-wserv-client-window-create-trace.py"
wserv_matrixmenu_command_buffer_transform="$project/Symbian/scripts/apply-htcleo-wserv-matrixmenu-command-buffer-compat.py"
wserv_type2a_pointer_transform="$project/Symbian/scripts/apply-htcleo-wserv-type2a-pointer-enable.py"
wserv_type2a_raw_trace_transform="$project/Symbian/scripts/apply-htcleo-wserv-type2a-raw-path-trace.py"
wserv_event_hook_counter_transform="$project/Symbian/scripts/apply-htcleo-wserv-event-hook-touch-counter.py"
wserv_runl_trace_bound_transform="$project/Symbian/scripts/apply-htcleo-wserv-runl-trace-bound.py"
wserv_absrect_pointer_fallback_transform="$project/Symbian/scripts/apply-htcleo-wserv-absrect-pointer-hit-fallback.py"
wserv_published_grid_fallback_transform="$project/Symbian/scripts/apply-htcleo-wserv-published-grid-hit-fallback.py"
wserv_published_grid_capture_transform="$project/Symbian/scripts/apply-htcleo-wserv-published-grid-pointer-capture.py"
matrixmenu_teardown_attribution_transform="$project/Symbian/scripts/apply-htcleo-matrixmenu-teardown-attribution.py"
wserv_matrixmenu_panic_category_transform="$project/Symbian/scripts/apply-htcleo-wserv-matrixmenu-panic-category.py"
wserv_touch_only_log_transform="$project/Symbian/scripts/apply-htcleo-wserv-touch-only-log.py"
wserv_client_source="$wserv_component/nga/SERVER/openwfc/CLIENT.CPP"
wserv_client_window_source="$wserv_component/nga/SERVER/openwfc/cliwin.cpp"
wserv_pointer_source="$wserv_component/nga/SERVER/POINTER.CPP"
wserv_event_source="$wserv_component/nga/SERVER/EVENT.CPP"
wserv_event_header="$wserv_component/nga/SERVER/EVENT.H"
wserv_rootwin_source="$wserv_component/nga/SERVER/ROOTWIN.CPP"
wserv_walkwindowtree_header="$wserv_component/nga/SERVER/openwfc/walkwindowtree.h"
wserv_build_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/wserv-nga-build/bld.inf"
wserv_binary="$full_epocroot/epoc32/release/armv5/urel/wserv_nga.exe"
wserv_parent_640_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/640-wserv-parent.txt"
display_component="$full_epocroot/sf/os/graphics/windowing/windowserverplugins/openwfc"
display_plugin="$display_component/src/stdplugin.cpp"
display_factory="$display_component/src/displayrenderstagefactory.cpp"
display_stage="$display_component/src/displayrenderstage.cpp"
display_openwfc="$display_component/src/openwfcwrapper.cpp"
display_target="$display_component/src/rendertarget.cpp"
display_policy="$display_component/src/displaypolicy.cpp"
display_fb_factory="$display_component/src/fbrenderstagefactory.cpp"
display_fb_stage="$display_component/src/fbrenderstage.cpp"
display_mmp="$display_component/group/stdplugin.mmp"
display_bldinf="$display_component/group/BLD.INF"
display_log_transform="$project/Symbian/scripts/apply-htcleo-display-render-stage-durable-log.py"
display_cpu_blit_transform="$project/Symbian/scripts/apply-htcleo-display-cpu-framebuffer-blit.py"
display_flicker_cpu_blit_transform="$project/Symbian/scripts/apply-htcleo-flicker-cpu-framebuffer-blit.py"
display_frame_signature_transform="$project/Symbian/scripts/apply-htcleo-display-frame-signature-trace.py"
display_region_blit_transform="$project/Symbian/scripts/apply-htcleo-display-region-aware-blit.py"
display_scheduler_blank_guard_transform="$project/Symbian/scripts/apply-htcleo-display-scheduler-blank-layer-guard.py"
display_high_frequency_log_retirement_transform="$project/Symbian/scripts/apply-htcleo-display-high-frequency-log-retirement.py"
display_binary="$full_epocroot/epoc32/release/armv5/urel/10286378.dll"
display_resource="$full_epocroot/epoc32/data/z/resource/plugins/10286378.rsc"
wfc_component="$full_epocroot/sf/os/graphics/graphicscomposition/openwfcompositionengine"
wfc_context="$wfc_component/composition/src/wfccontext.c"
wfc_display_context="$wfc_component/adaptation/src/Platform/Graphics/symbian/owfdisplaycontext.cpp"
wfc_screen="$wfc_component/adaptation/src/Platform/Graphics/symbian/owfscreen_displaychannel.cpp"
wfc_stream="$wfc_component/adaptation/src/Platform/Graphics/symbian/owfnativestreamstub.cpp"
wfc_logger="$wfc_component/composition/src/htcleowfclog.cpp"
wfc_header="$wfc_component/composition/include/htcleowfclog.h"
wfc_image_header="$wfc_component/common/include/owfimage.h"
wfc_display_header="$wfc_component/adaptation/include/owfdisplaycontextgeneral.h"
wfc_stream_header="$wfc_component/adaptation/include/owfnativestream.h"
wfc_mmp="$wfc_component/group/openwfc.mmp"
wfc_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/openwfc-build/bld.inf"
wfc_log_transform="$project/Symbian/scripts/apply-htcleo-openwfc-context-durable-log.py"
wfc_binary="$full_epocroot/epoc32/release/armv5/urel/libWFC.dll"
nvg_component="$full_epocroot/sf/mw/uiresources/uigraphics/NVGRenderStage"
nvg_plugin="$nvg_component/src/nvgrenderstageplugin.cpp"
nvg_factory="$nvg_component/src/nvgrenderstagefactory.cpp"
nvg_stage="$nvg_component/src/nvgrenderstage.cpp"
nvg_mmp="$nvg_component/group/nvgrenderstage.mmp"
nvg_bldinf="$nvg_component/group/bld.inf"
nvg_log_transform="$project/Symbian/scripts/apply-htcleo-nvgrenderstage-durable-log.py"
nvg_binary="$full_epocroot/epoc32/release/armv5/urel/nvgrenderstage.dll"
nvg_resource="$full_epocroot/epoc32/data/z/resource/plugins/nvgrenderstage.rsc"
ecom_component="$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework"
ecom_session="$ecom_component/frame/EComSession.cpp"
ecom_load_manager="$ecom_component/frame/LoadManager.cpp"
ecom_unload_policy="$ecom_component/frame/UnloadPolicy.cpp"
ecom_logger="$ecom_component/frame/HtcleoEcomLog.cpp"
ecom_logger_header="$ecom_component/frame/HtcleoEcomLog.h"
ecom_mmp="$ecom_component/MMPFiles/ECom.mmp"
ecom_log_transform="$project/Symbian/scripts/apply-htcleo-ecom-client-durable-log.py"
ecom_load_split_transform="$project/Symbian/scripts/apply-htcleo-ecom-library-load-split-log.py"
ecom_init_entrypoint_transform="$project/Symbian/scripts/apply-htcleo-ecom-library-init-entrypoint-log.py"
ecom_featmgr_list_transform="$project/Symbian/scripts/apply-htcleo-ecom-featmgr-list-trace.py"
ecom_server_transform="$project/Symbian/scripts/apply-htcleo-ecom-server-list-trace.py"
ecom_featureinfo_empty_transform="$project/Symbian/scripts/apply-htcleo-ecom-featureinfo-empty-list-compat.py"
ecom_matrixmenu_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-matrixmenu-server-retry.py"
ecom_matrixmenu_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-matrixmenu-list-retry.py"
ecom_homescreen_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-list-retry.py"
ecom_homescreen_action_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-action-list-retry.py"
ecom_homescreen_nonvisual_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-nonvisual-list-retry.py"
ecom_homescreen_menubar_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-menubar-list-retry.py"
ecom_homescreen_rendering_list_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-rendering-list-retry.py"
ecom_homescreen_retry_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-server-retry.py"
ecom_homescreen_server_trace_transform="$project/Symbian/scripts/apply-htcleo-ecom-homescreen-server-create-trace.py"
ecom_hsps_definition_resolve_transform="$project/Symbian/scripts/apply-htcleo-ecom-hsps-definition-direct-resolve.py"
ecom_hsps_persistent_trace_transform="$project/Symbian/scripts/apply-htcleo-ecom-hsps-persistent-trace.py"
ecom_hsps_response_trace_transform="$project/Symbian/scripts/apply-htcleo-ecom-hsps-response-trace.py"
ecom_hsps_client_load_trace_transform="$project/Symbian/scripts/apply-htcleo-ecom-hsps-client-load-trace.py"
ecom_spi_base="$full_epocroot/pdk304-stemkit/ecom-0-0.spi"
ecom_spi_tool="$full_epocroot/epoc32/tools/spitool.pl"
ecom_spi_perl_compat="$project/Symbian/scripts/apply-legacy-perl-defined-hash-compat.py"
ecom_spi_manifest="$project/Symbian/config/htcleo-homescreen-ecom-spi-resources.txt"
ecom_spi_additions=30
ecom_spi_total=138
gate17_plan="$output/GATE17-ENTRY-PLAN.json"
if [ "$incremental_resource_policy" = gate17-font-settings ] || \
   [ "$incremental_resource_policy" = gate17-catalog-observer ] || \
   [ "$incremental_resource_policy" = gate17-settings-only ] || \
   [ "$incremental_resource_policy" = gate17-layout-ipc-trace ] || \
   [ "$incremental_resource_policy" = gate17-settings-ready-781 ] || \
   [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ] || \
   [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    ecom_spi_manifest="$project/Symbian/config/htcleo-gate17-ecom-spi-resources.txt"
    ecom_spi_additions=33
    ecom_spi_total=141
fi
about_entry_plan="$output/ABOUT-ENTRY-PLAN.json"
about_entry_config="$project/Symbian/config/htcleo-gate17-about-entry.json"
if [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
    about_entry_config="$project/Symbian/config/htcleo-gate17-about-no-global-rescan.json"
fi
if [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
    about_entry_policy=stock-minimal3-about-chain16-new-assets-catalog-version-preserve840
    if [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
        about_entry_policy=stock-minimal3-about-chain-exact840-version-no-global-rescan-recovery
    fi
    ecom_spi_manifest="$project/Symbian/config/htcleo-gate17-about-ecom-spi-resources.txt"
    ecom_spi_additions=35
    ecom_spi_total=143
    python3 "$project/Symbian/scripts/prepare-htcleo-about-entry.py" \
        --parent "$project/Symbian/output/$incremental_parent/Symbian3" --plan "$about_entry_plan" --config "$about_entry_config"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-black-background ]; then
    #844/845 retain the private palette on the recovered840 lineage.
    #Do not silently inherit the withdrawn841/842 About membership/SPI changes.
    test "$incremental_parent" = 849-symbian3-full-gsapp-root-paint-witness-incremental
    test "$ecom_spi_total" = 141
    test "$about_entry_policy" = off
fi
ecom_spi_audit="$project/Symbian/scripts/audit-htcleo-homescreen-ecom-spi.py"
ecom_spi_dir="$work/ecom-spi"
ecom_spi_extended="$ecom_spi_dir/ecom-0-0.spi"
ecom_spi_report="$output/HTCLEO-HOMESCREEN-ECOM-SPI-AUDIT.txt"
ecom_build_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/ecom-client-build/bld.inf"
ecom_binary="$full_epocroot/epoc32/release/armv5/urel/ecom.dll"
ecom_server_session="$ecom_component/frame/EComServerSession.cpp"
ecom_server_source="$ecom_component/frame/EComServer.cpp"
ecom_server_start="$ecom_component/frame/EComServerStart.cpp"
ecom_server_rom_resolver="$ecom_component/frame/RomOnlyResolver.cpp"
ecom_server_default_resolver="$ecom_component/frame/DefaultResolver.cpp"
ecom_server_transaction="$ecom_component/frame/RegistryResolveTransaction.cpp"
ecom_server_registry_data="$ecom_component/frame/RegistryData.cpp"
ecom_server_logger="$ecom_component/frame/HtcleoEcomServerLog.cpp"
ecom_server_logger_header="$ecom_component/frame/HtcleoEcomServerLog.h"
ecom_server_mmp="$ecom_component/MMPFiles/EComServer.mmp"
ecom_server_build_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/ecom-server-build/bld.inf"
ecom_server_binary="$full_epocroot/epoc32/release/armv5/urel/ecomserver.exe"
ptiengine_component="$full_epocroot/sf/mw/inputmethods/textinput/ptienginev2"
ptiengine_source="$ptiengine_component/src/PtiDefaultCore.cpp"
ptiengine_mmp="$ptiengine_component/group/ptienginev2.mmp"
ptiengine_transform="$project/Symbian/scripts/apply-htcleo-ptiengine-english-fallback.py"
ptiengine_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/ptiengine-build/bld.inf"
ptiengine_binary="$full_epocroot/epoc32/release/armv5/urel/PtiEngine.dll"
ptiengine_frozen_def="$ptiengine_component/EABI/PtiEngineU.DEF"
ptiengine_stock_657="$output/ptiengine-stock-657.dll"
ptiengine_parent_migration="$project/Symbian/hd2/qsd8250-native-bsp/incremental-migrations/657-ptiengine-parent.txt"
stem_backend_component="$full_epocroot/sf/os/ossrv/genericopenlibs/openenvcore/backend"
stem_backend_source="$stem_backend_component/src/corebackend/localif.cpp"
stem_backend_header="$stem_backend_component/inc/sysif.h"
stem_backend_mmp="$full_epocroot/sf/incubator/stemkit/breakdeps/backend.mmp"
stem_backend_transform="$project/Symbian/scripts/apply-htcleo-stem-backend-constructor-log.py"
stem_backend_timezone_transform="$project/Symbian/scripts/apply-htcleo-stem-backend-timezone-defer.py"
stem_backend_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/stem-backend-build/bld.inf"
stem_backend_binary="$full_epocroot/epoc32/release/armv5/urel/stem_backend.dll"
stem_backend_frozen_def="$stem_backend_component/eabi/backendu.def"
hitchcock_component="$full_epocroot/sf/mw/uiaccelerator/uiacceltk/hitchcock/coretoolkit"
hitchcock_mmp="$hitchcock_component/group/coretoolkit.mmp"
hitchcock_source="$hitchcock_component/src/htcleohitchcockentrytrace.cpp"
hitchcock_frozen_def="$hitchcock_component/eabi/hitchcocku.DEF"
hitchcock_transform="$project/Symbian/scripts/apply-htcleo-hitchcock-entrypoint-durable-log.py"
hitchcock_import_dso_tool="$project/Symbian/scripts/prepare-htcleo-hitchcock-import-dsos.py"
hitchcock_bldinf="$project/Symbian/hd2/qsd8250-native-bsp/hitchcock-build/bld.inf"
hitchcock_config_path="$project/Symbian/config"
hitchcock_config=arm.v5.urel.gcce4_4_1.hitchcock_permissive
hitchcock_binary="$full_epocroot/epoc32/release/armv5/urel/hitchcock.dll"
hitchcock_sym="$full_epocroot/epoc32/release/armv5/urel/hitchcock.dll.sym"
hitchcock_map="$full_epocroot/epoc32/release/armv5/urel/hitchcock.dll.map"
hitchcock_cc_wrapper="$project/Symbian/scripts/htcleo-gcce-hitchcock-cc-wrapper.sh"
hitchcock_abi_promoter="$project/Symbian/scripts/promote-htcleo-hitchcock-frozen-template-abi.py"
ssm_config=arm.v5.urel.gcce4_4_1

case "$build_mode" in
    incremental|full-clean) ;;
    *) echo "ERROR: HD2_BUILD_MODE must be incremental or full-clean" >&2; exit 1 ;;
esac
case "$rebuild_native_bsp" in
    0|1) ;;
    *) echo "ERROR: HD2_REBUILD_NATIVE_BSP must be 0 or 1" >&2; exit 1 ;;
esac
case "$incremental_migration" in
    0|1) ;;
    *) echo "ERROR: HD2_INCREMENTAL_MIGRATION must be 0 or 1" >&2; exit 1 ;;
esac
case "$preflight_only" in
    0|1) ;;
    *) echo "ERROR: HD2_PREFLIGHT_ONLY must be 0 or 1" >&2; exit 1 ;;
esac

case "$work" in
    /root/symbian3-full-work/htcleo-native) ;;
    *) echo "ERROR: unsafe work path: $work" >&2; exit 1 ;;
esac

test -s "$stem"
test -x "$rombuild"
test -s "$loader_log_map_tool"
test -s "$canonicalizer"
test -s "$rom_space_audit"
mkdir -p "$work" "$build_output"

incremental_parent_release_manifest=
incremental_eiksrvs_resume=0
incremental_eiksrv_resume=0
incremental_eiksrvui_resume=0
incremental_aknskinsrv_resume=0
incremental_eiksrvc_resume=0
incremental_guard_manifest="$work/incremental-start-release.sha256"
incremental_parent_preflight_log="$output/incremental-parent-preflight.log"
incremental_binary_diff="$output/INCREMENTAL-BINARY-DIFF.txt"
incremental_release_cache="$build_output/incremental-release-cache"
if [ "$build_mode" = incremental ]; then
    test -n "$incremental_parent" || {
        echo "ERROR: incremental mode requires HD2_INCREMENTAL_PARENT" >&2
        exit 1
    }
    incremental_parent_root="$project/Symbian/output/$incremental_parent/Symbian3"
    incremental_parent_build="$incremental_parent_root/build"
    test -s "$incremental_parent_root/VERSION.txt"
    test -s "$incremental_parent_root/initrd.gz"
    test -d "$incremental_parent_build"
    grep -Fqx "Package: $incremental_parent" \
        "$incremental_parent_root/VERSION.txt"
    # A failed component rebuild can occur after the mutable working canonical
    # was removed but before a replacement ROM was emitted. Resume only by
    # restoring the byte-identical immutable parent payload; an existing but
    # mismatched image still fails closed below.
    if [ ! -s "$canonical_image" ]; then
        cp "$incremental_parent_root/initrd.gz" "$canonical_image"
        echo "HTCLEO_INCREMENTAL_CANONICAL_RESUMED parent=$incremental_parent"
    fi
    test "$(sha256sum "$canonical_image" | awk '{print $1}')" = \
        "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"

    parent_cache="$incremental_parent_build/incremental-release-cache"
    parent_cache_manifest="$parent_cache/RELEASE-CACHE-MANIFEST.tsv"
    if [ -s "$parent_cache_manifest" ]; then
        while IFS="$(printf '\t')" read -r cache_hash target_path cache_name
        do
            cache_file="$parent_cache/$cache_name"
            test -s "$cache_file"
            test "$(sha256sum "$cache_file" | awk '{print $1}')" = \
                "$cache_hash"
            cp "$cache_file" "$target_path"
        done <"$parent_cache_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_RESTORED parent=$incremental_parent"
    elif [ "$incremental_migration" -ne 1 ]; then
        echo "ERROR: parent package has no incremental release cache; use the one-time HD2_INCREMENTAL_MIGRATION=1 boundary" >&2
        exit 1
    fi

    incremental_parent_release_manifest="$work/incremental-parent-release.sha256"
    find "$incremental_parent_build" -type f -name '*-urel.sha256' \
        -exec cat {} \; | \
        awk '$2 ~ /^\/root\/.*\/epoc32\/release\// {print tolower($1) "  " $2}' | \
        sort -u >"$incremental_parent_release_manifest"
    # 778 adds stock entry dependencies to the immutable release cache, but
    # these have no legacy source-build *-urel.sha256 sidecars. Carry their
    # pinned cache records forward instead of losing seven tracked inputs.
    if [ "$incremental_parent" = 778-symbian3-full-english-font-settings-entry-incremental ] || \
       [ "$incremental_parent" = 781-symbian3-full-packed-layout-ipc-trace-incremental ] || \
       [ "$incremental_parent" = 782-symbian3-full-settings-ready-on-781-incremental ] || \
       [ "$incremental_parent" = 783-symbian3-full-matrix-pointer-frontier-incremental ] || \
       [ "$incremental_parent" = 784-symbian3-full-matrix-list-release-incremental ] || \
       [ "$incremental_parent" = 785-symbian3-full-matrix-local-fade-guard-incremental ] || \
       [ "$incremental_parent" = 787-symbian3-full-settings-worker-observe-on-785-incremental ] || \
       [ "$incremental_parent" = 788-symbian3-full-settings-worker-state-incremental ] || \
       [ "$incremental_parent" = 790-symbian3-full-settings-query-off-control-incremental ] || \
       [ "$incremental_parent" = 791-symbian3-full-settings-direct-registration-incremental ] || \
       [ "$incremental_parent" = 792-symbian3-full-menu-action-frontier-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 61
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 61
    fi
    if [ "$incremental_parent" = 793-symbian3-full-menu-launch-frontier-incremental ] || \
       [ "$incremental_parent" = 794-symbian3-full-menu-attribute-frontier-incremental ] || \
       [ "$incremental_parent" = 795-symbian3-full-menu-request-frontier-incremental ] || \
       [ "$incremental_parent" = 796-symbian3-full-menu-server-exit-watch-incremental ] || \
       [ "$incremental_parent" = 797-symbian3-full-menu-software-exception-incremental ] || \
       [ "$incremental_parent" = 798-symbian3-full-menu-exception-stack-incremental ] || \
       [ "$incremental_parent" = 799-symbian3-full-mcs-notifier-stop-incremental ] || \
       [ "$incremental_parent" = 800-symbian3-full-menu-task-lookup-control-incremental ] || \
       [ "$incremental_parent" = 801-symbian3-full-mcs-operation-completion-incremental ] || \
       [ "$incremental_parent" = 804-symbian3-full-hsps-header-cache-recovery-incremental ] || \
       [ "$incremental_parent" = 805-symbian3-full-menu-task-enumeration-on804-incremental ] || \
       [ "$incremental_parent" = 806-symbian3-full-gsapp-startup-observer-incremental ] || \
       [ "$incremental_parent" = 807-symbian3-full-gsapp-eikstart-frontier-incremental ] || \
       [ "$incremental_parent" = 808-symbian3-full-gsapp-env-frontier-incremental ] || \
       [ "$incremental_parent" = 809-symbian3-full-gsapp-aknenv-frontier-incremental ] || \
       [ "$incremental_parent" = 810-symbian3-full-gsapp-sgc-local-layout-incremental ] || \
       [ "$incremental_parent" = 811-symbian3-full-gsapp-appui-frontier-incremental ] || \
       [ "$incremental_parent" = 812-symbian3-full-gsapp-sgc-params-local-incremental ] || \
       [ "$incremental_parent" = 813-symbian3-full-gsapp-eikbase-frontier-incremental ] || \
       [ "$incremental_parent" = 814-symbian3-full-gsapp-appinfo-frontier-incremental ] || \
       [ "$incremental_parent" = 815-symbian3-full-gsapp-statuspane-frontier-incremental ] || \
       [ "$incremental_parent" = 816-symbian3-full-gsapp-sgc-fade-local-incremental ] || \
       [ "$incremental_parent" = 817-symbian3-full-gsapp-view-frontier-incremental ] || \
       [ "$incremental_parent" = 818-symbian3-full-gsapp-focus-frontier-incremental ] || \
       [ "$incremental_parent" = 819-symbian3-full-gsapp-keyblock-local-incremental ] || \
       [ "$incremental_parent" = 820-symbian3-full-gsapp-activation-frontier-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 62
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 62
    fi
    #821 already tracks GSFramework; keep all63 parent entries.
    if [ "$incremental_parent" = 821-symbian3-full-gsapp-plugin-frontier-incremental ] || \
       [ "$incremental_parent" = 822-symbian3-full-gsapp-redraw-frontier-incremental ] || \
       [ "$incremental_parent" = 823-symbian3-full-gsapp-lifetime-observer-incremental ] || \
       [ "$incremental_parent" = 824-symbian3-full-gsapp-exception-witness-incremental ] || \
       [ "$incremental_parent" = 825-symbian3-full-gsapp-ecom-notify-guard-incremental ] || \
       [ "$incremental_parent" = 826-symbian3-full-gsapp-ecom-create-retry-incremental ] || \
       [ "$incremental_parent" = 827-symbian3-full-gsapp-child-frontier-incremental ] || \
       [ "$incremental_parent" = 828-symbian3-full-gsapp-list-activation-incremental ] || \
       [ "$incremental_parent" = 829-symbian3-full-gsapp-async-view-event-incremental ] || \
       [ "$incremental_parent" = 830-symbian3-full-gsapp-view-transition-incremental ] || \
       [ "$incremental_parent" = 831-symbian3-full-gsapp-cone-view-event-incremental ] || \
       [ "$incremental_parent" = 832-symbian3-full-home-view-event-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 63
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 63
    fi
    if [ "$incremental_parent" = 833-symbian3-full-viewcli-source-control-incremental ] || \
       [ "$incremental_parent" = 834-symbian3-full-vws-client-queue-incremental ] || \
       [ "$incremental_parent" = 835-symbian3-full-vws-client-state-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 64
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 64
    fi
    if [ "$incremental_parent" = 836-symbian3-full-viewsrv-source-control-incremental ] || \
       [ "$incremental_parent" = 837-symbian3-full-vws-server-event-incremental ] || \
       [ "$incremental_parent" = 838-symbian3-full-vws-session-deactivation-incremental ] || \
       [ "$incremental_parent" = 839-symbian3-full-home-kernel-watch-incremental ] || \
       [ "$incremental_parent" = 840-symbian3-full-home-background-priority-ab-incremental ] || \
       [ "$incremental_parent" = 844-symbian3-full-gsapp-black-on840-incremental ] || \
       [ "$incremental_parent" = 845-symbian3-full-gsapp-static-background-incremental ] || \
       [ "$incremental_parent" = 846-symbian3-full-gsapp-window-background-incremental ] || \
       [ "$incremental_parent" = 847-symbian3-full-gsapp-root-skin-background-incremental ] || \
       [ "$incremental_parent" = 848-symbian3-full-gsapp-root-background-owner-incremental ] || \
       [ "$incremental_parent" = 849-symbian3-full-gsapp-root-paint-witness-incremental ] || \
       [ "$incremental_parent" = 850-symbian3-full-gsapp-root-bitmap-background-incremental ] || \
       [ "$incremental_parent" = 851-symbian3-full-avkon-common-geometry-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 65
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 65
    fi
    if [ "$incremental_parent" = 852-symbian3-full-font-family-binding-incremental ] || \
       [ "$incremental_parent" = 856-symbian3-full-font-ecom-list-reconnect-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 66
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 66
    fi
    if [ "$incremental_parent" = 899-symbian3-full-filemanager-cdl-tail-incremental ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 68
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 68
        #900 retains899's already-controlled CDL and its historical original-code proof.
        cp "$incremental_parent_root/build/CDL-PARENT-898-CODE.json" "$output/CDL-PARENT-898-CODE.json"
        cdl_binary="$full_epocroot/epoc32/release/armv5/urel/CdlEngine.dll"
    fi
    if [ "$incremental_parent" = 842-symbian3-full-about-no-global-rescan-recovery ]; then
        test "$(wc -l <"$parent_cache_manifest")" -eq 68
        awk -F '\t' '{print tolower($1) "  " $2}' "$parent_cache_manifest" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 68
    fi
    # 836 adds only the already-present stock ViewServer to the working cache.
    if [ "$incremental_resource_policy" = gate17-viewsrv-source-control ]; then
        python3 "$project/Symbian/scripts/verify-htcleo-viewsrv-source-control.py" --parent-proof \
            >"$output/VIEWSRV-PARENT-PROOF.json"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 64
        ! grep -Fq "  $viewsrv_binary" "$incremental_parent_release_manifest"
        viewsrv_stock="$project/Symbian/output/iteration-evidence/836-viewsrv-source-control/viewsrv-stock-835.dll"
        test "$(sha256sum "$viewsrv_stock" | awk '{print $1}')" = fe031c4e1ab4d2d44c16871af7ca56145d664fcee74937a36b8437013d8fcab9
        cp "$viewsrv_stock" "$viewsrv_binary"
        printf 'fe031c4e1ab4d2d44c16871af7ca56145d664fcee74937a36b8437013d8fcab9  %s\n' "$viewsrv_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 65
        echo 'HTCLEO_INCREMENTAL_PARENT_EXPANDED=835-viewsrv-attributed-stock-only-64-to65'
    fi
    # 833 tracks the already-present ViewCLI input for the first time.
    # Prove the whole stock code against832 using declared self/import relocations,
    # then extend only the mutable working manifest; immutable832 stays untouched.
    if [ "$incremental_resource_policy" = gate17-viewcli-source-control ]; then
        python3 "$project/Symbian/scripts/verify-htcleo-viewcli-source-control.py" --parent-proof \
            >"$output/VIEWCLI-PARENT-PROOF.json"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 63
        ! grep -Fq "  $viewcli_binary" "$incremental_parent_release_manifest"
        viewcli_stock="$project/Symbian/output/iteration-evidence/833-vws-client-queue/viewcli-stock-832.dll"
        test "$(sha256sum "$viewcli_stock" | awk '{print $1}')" = 15accd51bf36e6d6d1667bff4b3ed9319c68465156433b1fa24e2b6ff23b8fd2
        cp "$viewcli_stock" "$viewcli_binary"
        printf '15accd51bf36e6d6d1667bff4b3ed9319c68465156433b1fa24e2b6ff23b8fd2  %s\n' "$viewcli_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 64
        echo 'HTCLEO_INCREMENTAL_PARENT_EXPANDED=832-viewcli-attributed-stock-only-63-to64'
    fi
    # 765 restored the tested763 MCS binaries, but its two legacy hash files
    # were left over from the frozen764 build because these units were skipped.
    # Reconcile only those pinned metadata records against the immutable cache;
    # never rebuild/replace the tested binaries to fit stale metadata.
    if [ "$incremental_parent" = \
        765-symbian3-full-menulog-shared-capacity-incremental ]; then
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            6657ae68945ffcf368d23739fa77b6fa7a42c3e75901185dd0374f4c618c98f6
        for metadata_record in \
            mcsmenu.dll:adcf05ef859805f303116beadd2c91d72121d5caa0d04e4fb3f2c231c11a186f:bda192888a7e12d99306a3f29a582aa2994f7795ee2798384ca0ec9b20f9bde8 \
            mcsmenueng.dll:1c77ea7c9767f6961bfc303080f868d96f1d20700a1f8d079204ee8c4841700c:6b203091c351cc9446f96f7167660b083d93c063a808e7a47ee9a33790712424
        do
            metadata_name=${metadata_record%%:*}
            metadata_hashes=${metadata_record#*:}
            metadata_old=${metadata_hashes%%:*}
            metadata_cache_hash=${metadata_hashes#*:}
            metadata_path="$full_epocroot/epoc32/release/armv5/urel/$metadata_name"
            grep -qx "$metadata_old  $metadata_path" "$incremental_parent_release_manifest"
            test "$(awk -F '\t' -v path="$metadata_path" '$2 == path {print $1}' "$parent_cache_manifest")" = \
                "$metadata_cache_hash"
            test "$(sha256sum "$metadata_path" | awk '{print $1}')" = "$metadata_cache_hash"
            awk -v path="$metadata_path" -v hash="$metadata_cache_hash" \
                '$2 == path {print hash "  " $2; next} {print}' \
                "$incremental_parent_release_manifest" >"$work/incremental-parent-release-metadata-fixed.sha256"
            mv "$work/incremental-parent-release-metadata-fixed.sha256" "$incremental_parent_release_manifest"
            echo "HTCLEO_PARENT_METADATA_RECONCILED parent=765 binary=$metadata_name unchanged-cache=$metadata_cache_hash"
        done
    fi
    if [ "$rebuild_native_bsp" = 1 ]; then
        awk '$2 !~ /^\/root\/symbian\/+epoc32\/release\//' \
            "$incremental_parent_release_manifest" \
            >"$work/incremental-parent-userspace-release.sha256"
        mv "$work/incremental-parent-userspace-release.sha256" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_NATIVE_BSP_REBUILD_SCOPE=source-rebuilt-native-paths-excluded-from-parent-cache-guard"
    fi
    # Iteration 454 predates tracking eiksrvs.exe as an incremental release
    # input.  Expand the cache exactly once from a pinned parent binary, parent
    # image and parent recipe tuple without mutating the immutable 454 package.
    if [ "$incremental_parent" = \
        454-symbian3-full-ecom-featureinfo-empty-list-compat-incremental ] && \
        ! grep -Fq "  $eiksrvs_binary" "$incremental_parent_release_manifest"
    then
        test -s "$eiksrvs_parent_migration"
        migration_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvs_parent_migration")
        migration_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvs_parent_migration")
        migration_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvs_parent_migration")
        migration_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvs_parent_migration")
        migration_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvs_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$migration_parent" = "$incremental_parent"
        test "$migration_path" = "$eiksrvs_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$migration_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$migration_recipe"
        test "$(grep -F "$eiksrvs_binary" "$parent_recipe" | \
            grep -F '"sys\bin\eiksrvs.exe"' | wc -l)" -eq 1
        eiksrvs_current_hash=$(sha256sum "$eiksrvs_binary" | awk '{print $1}')
        if [ "$eiksrvs_current_hash" != "$migration_hash" ]; then
            # A failed attempt may already have relinked the sole allowlisted
            # output before a later disassembly assertion stopped the script.
            # Resume only with the exact successful parent-expansion receipt
            # and transformed source; the target is deleted below so SBS must
            # reconstruct it rather than accepting an arbitrary drifted file.
            test -s "$output/incremental-eiksrvs-parent-migration.txt"
            grep -qx 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK' \
                "$output/incremental-eiksrvs-parent-migration.txt"
            grep -Fqx "SHA256=$migration_hash" \
                "$output/incremental-eiksrvs-parent-migration.txt"
            grep -q 'HTCLEO_EIKSRVS_STARTUP_DURABLE_LOG_V1' \
                "$eiksrvs_source"
            incremental_eiksrvs_resume=1
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANSION_RESUME binary=$eiksrvs_binary"
        fi
        printf '%s  %s\n' "$migration_hash" "$eiksrvs_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        printf 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK\nPARENT=%s\nBINARY=%s\nSHA256=%s\nPARENT_RECIPE_SHA256=%s\n' \
            "$incremental_parent" "$eiksrvs_binary" "$migration_hash" \
            "$migration_recipe" \
            >"$output/incremental-eiksrvs-parent-migration.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED binary=$eiksrvs_binary"
    fi
    # Iteration 455 proves the next frontier lies in eiksrv.dll, but that
    # stock ROM input was not yet part of the incremental cache. Expand the
    # verified cache once from the immutable 455 image/recipe/binary tuple.
    if [ "$incremental_parent" = \
        455-symbian3-full-eiksrvs-startup-rendezvous-trace-incremental ] && \
        ! grep -Fq "  $eiksrv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$eiksrv_parent_migration"
        migration_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrv_parent_migration")
        migration_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrv_parent_migration")
        migration_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrv_parent_migration")
        migration_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrv_parent_migration")
        migration_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrv_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$migration_parent" = "$incremental_parent"
        test "$migration_path" = "$eiksrv_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$migration_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$migration_recipe"
        test "$(grep -F "$eiksrv_binary" "$parent_recipe" | \
            grep -F '"sys\bin\eiksrv.dll"' | wc -l)" -eq 1
        eiksrv_current_hash=$(sha256sum "$eiksrv_binary" | awk '{print $1}')
        if [ "$eiksrv_current_hash" != "$migration_hash" ]; then
            test -s "$output/incremental-eiksrv-parent-migration.txt"
            grep -qx 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK' \
                "$output/incremental-eiksrv-parent-migration.txt"
            grep -Fqx "SHA256=$migration_hash" \
                "$output/incremental-eiksrv-parent-migration.txt"
            grep -q 'HTCLEO_EIKSRV_SERVER_CONSTRUCT_DURABLE_LOG_V1' \
                "$eiksrv_source"
            incremental_eiksrv_resume=1
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANSION_RESUME binary=$eiksrv_binary"
        fi
        printf '%s  %s\n' "$migration_hash" "$eiksrv_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        printf 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK\nPARENT=%s\nBINARY=%s\nSHA256=%s\nPARENT_RECIPE_SHA256=%s\n' \
            "$incremental_parent" "$eiksrv_binary" "$migration_hash" \
            "$migration_recipe" \
            >"$output/incremental-eiksrv-parent-migration.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED binary=$eiksrv_binary"
    fi
    # Iteration 456 reaches the call into the ROM's EiksrvUi factory product.
    # The recipe maps stem_eiksrvui.dll, rather than the ordinary EikStd
    # eiksrvui.dll, to sys\bin\eiksrvui.dll. Expand the verified cache once
    # from that exact immutable parent image/recipe/binary tuple.
    if [ "$incremental_parent" = \
        456-symbian3-full-eiksrv-newl-constructl-trace-incremental ] && \
        ! grep -Fq "  $eiksrvui_binary" "$incremental_parent_release_manifest"
    then
        test -s "$eiksrvui_parent_migration"
        migration_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvui_parent_migration")
        migration_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvui_parent_migration")
        migration_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvui_parent_migration")
        migration_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvui_parent_migration")
        migration_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvui_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$migration_parent" = "$incremental_parent"
        test "$migration_path" = "$eiksrvui_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$migration_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$migration_recipe"
        test "$(grep -F "$eiksrvui_binary" "$parent_recipe" | \
            grep -F '"sys\bin\eiksrvui.dll"' | wc -l)" -eq 1
        eiksrvui_current_hash=missing
        if [ -s "$eiksrvui_binary" ]; then
            eiksrvui_current_hash=$(sha256sum "$eiksrvui_binary" | awk '{print $1}')
        fi
        if [ "$eiksrvui_current_hash" != "$migration_hash" ]; then
            test -s "$output/incremental-eiksrvui-parent-migration.txt"
            grep -qx 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK' \
                "$output/incremental-eiksrvui-parent-migration.txt"
            grep -Fqx "SHA256=$migration_hash" \
                "$output/incremental-eiksrvui-parent-migration.txt"
            grep -q 'HTCLEO_EIKSRVUI_CONSTRUCT_DURABLE_LOG_V1' \
                "$eiksrvui_source"
            incremental_eiksrvui_resume=1
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANSION_RESUME binary=$eiksrvui_binary"
        fi
        printf '%s  %s\n' "$migration_hash" "$eiksrvui_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        printf 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK\nPARENT=%s\nBINARY=%s\nSHA256=%s\nPARENT_RECIPE_SHA256=%s\n' \
            "$incremental_parent" "$eiksrvui_binary" "$migration_hash" \
            "$migration_recipe" \
            >"$output/incremental-eiksrvui-parent-migration.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED binary=$eiksrvui_binary"
    fi
    # Iteration 458 proves the UI server blocks inside skin initialization.
    # The stock AKNSKINSRV.dll used by that immutable parent was not part of
    # the 22-file cache, so pin and expand exactly that ROM input before
    # rebuilding it with client/server startup logging.
    if [ "$incremental_parent" = \
        458-symbian3-full-eiksrvui-skin-result-trace-incremental ] && \
        ! grep -Fq "  $aknskinsrv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$aknskinsrv_parent_migration"
        migration_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$aknskinsrv_parent_migration")
        migration_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$aknskinsrv_parent_migration")
        migration_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$aknskinsrv_parent_migration")
        migration_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$aknskinsrv_parent_migration")
        migration_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$aknskinsrv_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$migration_parent" = "$incremental_parent"
        test "$migration_path" = "$aknskinsrv_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$migration_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$migration_recipe"
        test "$(grep -F "$aknskinsrv_binary" "$parent_recipe" | \
            grep -F '"sys\bin\aknskinsrv.dll"' | wc -l)" -eq 1
        aknskinsrv_current_hash=missing
        if [ -s "$aknskinsrv_binary" ]; then
            aknskinsrv_current_hash=$(sha256sum "$aknskinsrv_binary" | awk '{print $1}')
        fi
        if [ "$aknskinsrv_current_hash" != "$migration_hash" ]; then
            test -s "$output/incremental-aknskinsrv-parent-migration.txt"
            grep -qx 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK' \
                "$output/incremental-aknskinsrv-parent-migration.txt"
            grep -Fqx "SHA256=$migration_hash" \
                "$output/incremental-aknskinsrv-parent-migration.txt"
            grep -q 'HTCLEO_AKNSKINSRV_DURABLE_LOG_V1' \
                "$aknskinsrv_source"
            incremental_aknskinsrv_resume=1
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANSION_RESUME binary=$aknskinsrv_binary"
        fi
        printf '%s  %s\n' "$migration_hash" "$aknskinsrv_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        printf 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK\nPARENT=%s\nBINARY=%s\nSHA256=%s\nPARENT_RECIPE_SHA256=%s\n' \
            "$incremental_parent" "$aknskinsrv_binary" "$migration_hash" \
            "$migration_recipe" \
            >"$output/incremental-aknskinsrv-parent-migration.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED binary=$aknskinsrv_binary"
    fi
    # Iteration 462 completes the skin/DRM path and proves the next frontier is
    # inside the client-side REikAppUiSession::Connect implementation.  The
    # parent recipe contains stock eiksrvc.dll, but the 23-file cache predates
    # tracking it.  Pin and expand that exact immutable ROM input once.
    if [ "$incremental_parent" = \
        462-symbian3-full-aknskinsrv-boot-drm-defer-eabi-incremental ] && \
        ! grep -Fq "  $eiksrvc_binary" "$incremental_parent_release_manifest"
    then
        test -s "$eiksrvc_parent_migration"
        migration_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvc_parent_migration")
        migration_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvc_parent_migration")
        migration_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvc_parent_migration")
        migration_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvc_parent_migration")
        migration_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvc_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$migration_parent" = "$incremental_parent"
        test "$migration_path" = "$eiksrvc_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$migration_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$migration_recipe"
        test "$(grep -F "$eiksrvc_binary" "$parent_recipe" | \
            grep -F '"sys\bin\eiksrvc.dll"' | wc -l)" -eq 1
        eiksrvc_current_hash=missing
        if [ -s "$eiksrvc_binary" ]; then
            eiksrvc_current_hash=$(sha256sum "$eiksrvc_binary" | awk '{print $1}')
        fi
        if [ "$eiksrvc_current_hash" != "$migration_hash" ]; then
            test -s "$output/incremental-eiksrvc-parent-migration.txt"
            grep -qx 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK' \
                "$output/incremental-eiksrvc-parent-migration.txt"
            grep -Fqx "SHA256=$migration_hash" \
                "$output/incremental-eiksrvc-parent-migration.txt"
            grep -q 'HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1' \
                "$eiksrvc_source"
            incremental_eiksrvc_resume=1
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANSION_RESUME binary=$eiksrvc_binary"
        fi
        printf '%s  %s\n' "$migration_hash" "$eiksrvc_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        printf 'STATUS=HTCLEO_INCREMENTAL_PARENT_EXPANSION_OK\nPARENT=%s\nBINARY=%s\nSHA256=%s\nPARENT_RECIPE_SHA256=%s\n' \
            "$incremental_parent" "$eiksrvc_binary" "$migration_hash" \
            "$migration_recipe" \
            >"$output/incremental-eiksrvc-parent-migration.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED binary=$eiksrvc_binary"
    fi
    # Iteration 463 already tracks eiksrvc.dll in its verified 24-file cache.
    # Pin that exact tested parent tuple before applying the bounded QSD8250
    # rendezvous-notification compatibility change for iteration 464.
    if [ "$incremental_parent" = \
        463-symbian3-full-eiksrvc-connect-session-trace-incremental ]
    then
        test -s "$eiksrvc_compat_parent"
        compat_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvc_compat_parent")
        compat_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvc_compat_parent")
        compat_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvc_compat_parent")
        compat_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvc_compat_parent")
        compat_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvc_compat_parent")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$compat_parent" = "$incremental_parent"
        test "$compat_path" = "$eiksrvc_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$compat_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$compat_recipe"
        test "$(sha256sum "$eiksrvc_binary" | awk '{print $1}')" = \
            "$compat_hash"
        cp "$eiksrvc_compat_parent" \
            "$output/incremental-eiksrvc-parent-463.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_PIN_OK parent=$incremental_parent binary=$eiksrvc_binary"
    fi
    # Iteration 464 proves that CreateLocal succeeds but the known-broken
    # HTCLEO NTimer/DFC path never completes the timeout request.  Pin the
    # exact tested 464 binary before replacing only that timer workaround with
    # EKA2's synchronous RendezvousCancel contract.
    if [ "$incremental_parent" = \
        464-symbian3-full-eiksrvc-rendezvous-timeout-compat-incremental ]
    then
        test -s "$eiksrvc_cancel_parent"
        cancel_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvc_cancel_parent")
        cancel_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvc_cancel_parent")
        cancel_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvc_cancel_parent")
        cancel_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvc_cancel_parent")
        cancel_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvc_cancel_parent")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$cancel_parent" = "$incremental_parent"
        test "$cancel_path" = "$eiksrvc_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$cancel_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$cancel_recipe"
        test "$(sha256sum "$eiksrvc_binary" | awk '{print $1}')" = \
            "$cancel_hash"
        cp "$eiksrvc_cancel_parent" \
            "$output/incremental-eiksrvc-parent-464.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_PIN_OK parent=$incremental_parent binary=$eiksrvc_binary"
    fi
    # Iteration 465 proves synchronous cancellation releases AknCap, but the
    # stock retry loop immediately creates four competing EikSrv children and
    # exhausts before !EikAppUiServer registers.  Pin the exact tested 465
    # binary before changing only AknCap's retry policy to one child plus a
    # bounded CreateSession readiness loop.
    if [ "$incremental_parent" = \
        465-symbian3-full-eiksrvc-rendezvous-cancel-compat-incremental ]
    then
        test -s "$eiksrvc_ready_retry_parent"
        ready_retry_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvc_ready_retry_parent")
        ready_retry_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvc_ready_retry_parent")
        ready_retry_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvc_ready_retry_parent")
        ready_retry_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvc_ready_retry_parent")
        ready_retry_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvc_ready_retry_parent")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$ready_retry_parent" = "$incremental_parent"
        test "$ready_retry_path" = "$eiksrvc_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$ready_retry_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$ready_retry_recipe"
        test "$(sha256sum "$eiksrvc_binary" | awk '{print $1}')" = \
            "$ready_retry_hash"
        cp "$eiksrvc_ready_retry_parent" \
            "$output/incremental-eiksrvc-parent-465.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_PIN_OK parent=$incremental_parent binary=$eiksrvc_binary"
    fi
    # Iteration 466 proves the single-child policy and complete EikSrv
    # construction, but four durable flushes per repeated readiness attempt
    # consume the one-minute hardware window.  Pin exact 466 before compacting
    # repeated polling to the single E941 result/yield record.
    if [ "$incremental_parent" = \
        466-symbian3-full-eiksrvc-single-child-ready-retry-incremental ]
    then
        test -s "$eiksrvc_compact_poll_parent"
        compact_poll_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvc_compact_poll_parent")
        compact_poll_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvc_compact_poll_parent")
        compact_poll_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvc_compact_poll_parent")
        compact_poll_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvc_compact_poll_parent")
        compact_poll_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvc_compact_poll_parent")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$compact_poll_parent" = "$incremental_parent"
        test "$compact_poll_path" = "$eiksrvc_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$compact_poll_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$compact_poll_recipe"
        test "$(sha256sum "$eiksrvc_binary" | awk '{print $1}')" = \
            "$compact_poll_hash"
        cp "$eiksrvc_compact_poll_parent" \
            "$output/incremental-eiksrvc-parent-466.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_PIN_OK parent=$incremental_parent binary=$eiksrvc_binary"
    fi
    # Iteration 467 exhausts all 64 compact readiness polls and proves the
    # single EikSrv child stops between E775/E776, inside the real STEM
    # CEikServAppUiBase::InitializeL.  Pin the exact 467 STEM image before
    # adding only internal durable checkpoints for iteration 468.
    if [ "$incremental_parent" = \
        467-symbian3-full-eiksrvc-compact-ready-poll-incremental ]
    then
        test -s "$eiksrvui_initialize_parent"
        initialize_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eiksrvui_initialize_parent")
        initialize_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eiksrvui_initialize_parent")
        initialize_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eiksrvui_initialize_parent")
        initialize_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eiksrvui_initialize_parent")
        initialize_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eiksrvui_initialize_parent")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$initialize_parent" = "$incremental_parent"
        test "$initialize_path" = "$eiksrvui_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$initialize_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$initialize_recipe"
        test "$(sha256sum "$eiksrvui_binary" | awk '{print $1}')" = \
            "$initialize_hash"
        cp "$eiksrvui_initialize_parent" \
            "$output/incremental-eiksrvui-parent-467.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_PIN_OK parent=$incremental_parent binary=$eiksrvui_binary"
    fi
    # Iteration 468 reaches the existing synchronous StartC32 call and stops
    # between E7D7/E7D8.  c32root.dll and c32start.exe were stock ROM inputs
    # outside the 24-file cache, so expand the immutable parent from pinned
    # stock copies before rebuilding only this coupled client/configurator pair.
    if [ "$incremental_parent" = \
        468-symbian3-full-eiksrvui-initialize-durable-trace-incremental ]
    then
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test -s "$parent_recipe"
        for c32_pin in "$c32root_parent" "$c32start_parent"
        do
            test -s "$c32_pin"
            c32_parent_package=$(sed -n 's/^PARENT_PACKAGE=//p' "$c32_pin")
            c32_parent_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' "$c32_pin")
            c32_parent_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' "$c32_pin")
            c32_parent_path=$(sed -n 's/^BINARY_PATH=//p' "$c32_pin")
            c32_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' "$c32_pin")
            test "$c32_parent_package" = "$incremental_parent"
            test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
                "$c32_parent_initrd"
            test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
                "$c32_parent_recipe"
            case "$c32_parent_path" in
                "$c32root_binary")
                    c32_parent_stock="$c32root_stock_468"
                    c32_parent_dest='sys\bin\c32root.dll'
                    ;;
                "$c32start_binary")
                    c32_parent_stock="$c32start_stock_468"
                    c32_parent_dest='sys\bin\c32start.exe'
                    ;;
                *) echo "ERROR: unexpected C32 parent binary: $c32_parent_path" >&2; exit 1 ;;
            esac
            test -s "$c32_parent_stock"
            test "$(sha256sum "$c32_parent_stock" | awk '{print $1}')" = \
                "$c32_parent_hash"
            test "$(grep -F "$c32_parent_path" "$parent_recipe" | \
                grep -F "\"$c32_parent_dest\"" | wc -l)" -eq 1
            cp "$c32_parent_stock" "$c32_parent_path"
            test "$(sha256sum "$c32_parent_path" | awk '{print $1}')" = \
                "$c32_parent_hash"
            if ! grep -Fq "  $c32_parent_path" "$incremental_parent_release_manifest"; then
                printf '%s  %s\n' "$c32_parent_hash" "$c32_parent_path" \
                    >>"$incremental_parent_release_manifest"
            fi
        done
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$c32root_parent" "$output/incremental-c32root-parent-468.txt"
        cp "$c32start_parent" "$output/incremental-c32start-parent-468.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binaries=c32root.dll,c32start.exe"
    fi
    # Iteration 473 enters the active STEM Avkon BaseConstructL but does not
    # return. stem_avkon.dll was a stock ROM input outside the 26-file cache.
    # Expand the immutable 473 parent once, then retain it in every later cache.
    if [ "$incremental_parent" = \
        473-symbian3-full-eiksrvui-system-attribute-ui-fail-open-incremental ] && \
        ! grep -Fq "  $stem_avkon_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$stem_avkon_parent_migration"
        avkon_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$stem_avkon_parent_migration")
        avkon_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$stem_avkon_parent_migration")
        avkon_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$stem_avkon_parent_migration")
        avkon_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$stem_avkon_parent_migration")
        avkon_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$stem_avkon_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$avkon_parent" = "$incremental_parent"
        test "$avkon_path" = "$stem_avkon_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$avkon_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$avkon_recipe"
        test "$(grep -F "$stem_avkon_binary" "$parent_recipe" | \
            grep -F '"sys\bin\avkon.dll"' | wc -l)" -eq 1
        avkon_current_hash=$(sha256sum "$stem_avkon_binary" | awk '{print $1}')
        if [ "$avkon_current_hash" = "$avkon_hash" ]; then
            if [ ! -s "$stem_avkon_stock_473" ]; then
                cp "$stem_avkon_binary" "$stem_avkon_stock_473"
            fi
        else
            test -s "$stem_avkon_stock_473"
            test "$(sha256sum "$stem_avkon_stock_473" | awk '{print $1}')" = \
                "$avkon_hash"
            cp "$stem_avkon_stock_473" "$stem_avkon_binary"
        fi
        test "$(sha256sum "$stem_avkon_binary" | awk '{print $1}')" = \
            "$avkon_hash"
        test "$(sha256sum "$stem_avkon_stock_473" | awk '{print $1}')" = \
            "$avkon_hash"
        printf '%s  %s\n' "$avkon_hash" "$stem_avkon_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$stem_avkon_parent_migration" \
            "$output/incremental-stem-avkon-parent-473.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=stem_avkon.dll"
    fi
    # Iteration 492 completes AppArc and reaches the critical-apps
    # MatrixMenu deferred StartApp/MultipleWait boundary. matrixmenu.exe was a
    # stock ROM input outside the 27-file cache, so expand the exact immutable
    # 492 tuple once before adding lifecycle-only logging.
    if [ "$incremental_parent" = \
        492-symbian3-full-apparc-first-scan-sync-incremental ] && \
        ! grep -Fq "  $matrixmenu_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$matrixmenu_parent_migration"
        matrix_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$matrixmenu_parent_migration")
        matrix_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$matrixmenu_parent_migration")
        matrix_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$matrixmenu_parent_migration")
        matrix_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$matrixmenu_parent_migration")
        matrix_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$matrixmenu_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$matrix_parent" = "$incremental_parent"
        test "$matrix_path" = "$matrixmenu_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$matrix_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$matrix_recipe"
        test "$(grep -F "$matrixmenu_binary" "$parent_recipe" | \
            grep -F '"sys\bin\matrixmenu.exe"' | wc -l)" -eq 1
        matrix_current_hash=$(sha256sum "$matrixmenu_binary" | awk '{print $1}')
        if [ "$matrix_current_hash" = "$matrix_hash" ]; then
            if [ ! -s "$matrixmenu_stock_492" ]; then
                cp "$matrixmenu_binary" "$matrixmenu_stock_492"
            fi
        else
            test -s "$matrixmenu_stock_492"
            test "$(sha256sum "$matrixmenu_stock_492" | awk '{print $1}')" = \
                "$matrix_hash"
            cp "$matrixmenu_stock_492" "$matrixmenu_binary"
        fi
        test "$(sha256sum "$matrixmenu_binary" | awk '{print $1}')" = \
            "$matrix_hash"
        test "$(sha256sum "$matrixmenu_stock_492" | awk '{print $1}')" = \
            "$matrix_hash"
        printf '%s  %s\n' "$matrix_hash" "$matrixmenu_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$matrixmenu_parent_migration" \
            "$output/incremental-matrixmenu-parent-492.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=matrixmenu.exe"
    fi
    # Iteration 592 attributes the final white frame to CONE scheduler entry.
    # stem_cone.dll was a stock STEM ROM input outside the 35-file cache; pin
    # its exact immutable parent tuple once before rebuilding CCoeRedrawer.
    if [ "$incremental_parent" = \
        592-symbian3-full-ui-frame-stage-correlation-incremental ] && \
        ! grep -Fq "  $stem_cone_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$stem_cone_parent_migration"
        cone_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$stem_cone_parent_migration")
        cone_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$stem_cone_parent_migration")
        cone_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$stem_cone_parent_migration")
        cone_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$stem_cone_parent_migration")
        cone_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$stem_cone_parent_migration")
        cone_destination=$(sed -n 's/^ROM_DESTINATION=//p' \
            "$stem_cone_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$cone_parent" = "$incremental_parent"
        test "$cone_path" = "$stem_cone_binary"
        test "$cone_destination" = 'sys\bin\cone.dll'
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$cone_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$cone_recipe"
        test "$(grep -F "$stem_cone_binary" "$parent_recipe" | \
            grep -F '"sys\bin\cone.dll"' | wc -l)" -eq 1
        cone_current_hash=$(sha256sum "$stem_cone_binary" | awk '{print $1}')
        if [ "$cone_current_hash" = "$cone_hash" ]; then
            if [ ! -s "$stem_cone_stock_592" ]; then
                cp "$stem_cone_binary" "$stem_cone_stock_592"
            fi
        else
            test -s "$stem_cone_stock_592"
            test "$(sha256sum "$stem_cone_stock_592" | awk '{print $1}')" = \
                "$cone_hash"
            cp "$stem_cone_stock_592" "$stem_cone_binary"
        fi
        test "$(sha256sum "$stem_cone_binary" | awk '{print $1}')" = \
            "$cone_hash"
        test "$(sha256sum "$stem_cone_stock_592" | awk '{print $1}')" = \
            "$cone_hash"
        printf '%s  %s\n' "$cone_hash" "$stem_cone_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$stem_cone_parent_migration" \
            "$output/incremental-stem-cone-parent-592.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=stem_cone.dll"
    fi
    # Iteration 525 proves MatrixMenu blocks inside the stock mmwidgets dummy
    # grid constructor.  mmwidgets.dll predates the 29-file incremental cache;
    # pin the exact immutable 525 image before adding diagnostic-only logging.
    if [ "$incremental_parent" = \
        525-symbian3-full-matrixmenu-dummy-grid-result-trace-incremental ] && \
        ! grep -Fq "  $mmwidgets_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$mmwidgets_parent_migration"
        mmwidgets_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$mmwidgets_parent_migration")
        mmwidgets_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$mmwidgets_parent_migration")
        mmwidgets_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$mmwidgets_parent_migration")
        mmwidgets_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$mmwidgets_parent_migration")
        mmwidgets_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$mmwidgets_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$mmwidgets_parent" = "$incremental_parent"
        test "$mmwidgets_path" = "$mmwidgets_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$mmwidgets_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$mmwidgets_recipe"
        test "$(grep -F "$mmwidgets_binary" "$parent_recipe" | \
            grep -F '"sys\bin\mmwidgets.dll"' | wc -l)" -eq 1
        mmwidgets_current_hash=$(sha256sum "$mmwidgets_binary" | awk '{print $1}')
        if [ "$mmwidgets_current_hash" = "$mmwidgets_hash" ]; then
            if [ ! -s "$mmwidgets_stock_525" ]; then
                cp "$mmwidgets_binary" "$mmwidgets_stock_525"
            fi
        else
            test -s "$mmwidgets_stock_525"
            test "$(sha256sum "$mmwidgets_stock_525" | awk '{print $1}')" = \
                "$mmwidgets_hash"
            cp "$mmwidgets_stock_525" "$mmwidgets_binary"
        fi
        test "$(sha256sum "$mmwidgets_binary" | awk '{print $1}')" = \
            "$mmwidgets_hash"
        test "$(sha256sum "$mmwidgets_stock_525" | awk '{print $1}')" = \
            "$mmwidgets_hash"
        printf '%s  %s\n' "$mmwidgets_hash" "$mmwidgets_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$mmwidgets_parent_migration" \
            "$output/incremental-mmwidgets-parent-525.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=mmwidgets.dll"
    fi
    # Iteration 528 proves CHnEngine::NewL blocks internally.  hnengine.dll is
    # still outside the 30-file cache, so pin its exact immutable parent tuple
    # before adding constructor-only HNLOG tracing.
    if [ "$incremental_parent" = \
        528-symbian3-full-matrixmenu-hnengine-result-trace-incremental ] && \
        ! grep -Fq "  $hnengine_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hnengine_parent_migration"
        hnengine_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hnengine_parent_migration")
        hnengine_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hnengine_parent_migration")
        hnengine_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hnengine_parent_migration")
        hnengine_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$hnengine_parent_migration")
        hnengine_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$hnengine_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$hnengine_parent" = "$incremental_parent"
        test "$hnengine_path" = "$hnengine_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$hnengine_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$hnengine_recipe"
        test "$(grep -F "$hnengine_binary" "$parent_recipe" | \
            grep -F '"sys\bin\hnengine.dll"' | wc -l)" -eq 1
        hnengine_current_hash=missing
        if [ -s "$hnengine_binary" ]; then
            hnengine_current_hash=$(sha256sum "$hnengine_binary" | awk '{print $1}')
        fi
        if [ "$hnengine_current_hash" = "$hnengine_hash" ]; then
            if [ ! -s "$hnengine_stock_528" ]; then
                cp "$hnengine_binary" "$hnengine_stock_528"
            fi
        else
            test -s "$hnengine_stock_528"
            test "$(sha256sum "$hnengine_stock_528" | awk '{print $1}')" = \
                "$hnengine_hash"
            cp "$hnengine_stock_528" "$hnengine_binary"
        fi
        test "$(sha256sum "$hnengine_binary" | awk '{print $1}')" = \
            "$hnengine_hash"
        test "$(sha256sum "$hnengine_stock_528" | awk '{print $1}')" = \
            "$hnengine_hash"
        printf '%s  %s\n' "$hnengine_hash" "$hnengine_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hnengine_parent_migration" \
            "$output/incremental-hnengine-parent-528.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hnengine.dll"
    fi
    # Iteration 529 proves CHnMdModel::NewL blocks internally.  Pin the exact
    # stock metadata-model DLL from immutable parent 529 before adding
    # constructor-only MDLOG tracing; no behavior is normalized.
    if [ "$incremental_parent" = \
        529-symbian3-full-hnengine-constructor-durable-trace-incremental ] && \
        ! grep -Fq "  $hnmetadata_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hnmetadata_parent_migration"
        hnmetadata_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hnmetadata_parent_migration")
        hnmetadata_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hnmetadata_parent_migration")
        hnmetadata_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hnmetadata_parent_migration")
        hnmetadata_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$hnmetadata_parent_migration")
        hnmetadata_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$hnmetadata_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$hnmetadata_parent" = "$incremental_parent"
        test "$hnmetadata_path" = "$hnmetadata_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$hnmetadata_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$hnmetadata_recipe"
        test "$(grep -F "$hnmetadata_binary" "$parent_recipe" | \
            grep -F '"sys\bin\hnmetadatamodel.dll"' | wc -l)" -eq 1
        hnmetadata_current_hash=missing
        if [ -s "$hnmetadata_binary" ]; then
            hnmetadata_current_hash=$(sha256sum "$hnmetadata_binary" | awk '{print $1}')
        fi
        if [ "$hnmetadata_current_hash" = "$hnmetadata_hash" ]; then
            if [ ! -s "$hnmetadata_stock_529" ]; then
                cp "$hnmetadata_binary" "$hnmetadata_stock_529"
            fi
        else
            test -s "$hnmetadata_stock_529"
            test "$(sha256sum "$hnmetadata_stock_529" | awk '{print $1}')" = \
                "$hnmetadata_hash"
            cp "$hnmetadata_stock_529" "$hnmetadata_binary"
        fi
        test "$(sha256sum "$hnmetadata_binary" | awk '{print $1}')" = \
            "$hnmetadata_hash"
        test "$(sha256sum "$hnmetadata_stock_529" | awk '{print $1}')" = \
            "$hnmetadata_hash"
        printf '%s  %s\n' "$hnmetadata_hash" "$hnmetadata_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hnmetadata_parent_migration" \
            "$output/incremental-hnmetadatamodel-parent-529.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hnmetadatamodel.dll"
    fi
    # Iteration 582 proves the forced synchronous LIW mode cannot return a
    # MenuContent value: the provider requires a callback and emits only its
    # ErrorCode parameter for a null callback.  Pin the exact immutable parent
    # mcsservice.dll before rebuilding its existing GetList AO as a
    # MatrixMenu-only synchronous IPC pump with the stock LIW callback tail.
    if [ "$incremental_parent" = \
        582-symbian3-full-hn-sync-direct-safe-tail-incremental ] && \
        ! grep -Fq "  $mcsservice_binary" "$incremental_parent_release_manifest"
    then
        test -s "$mcsservice_parent_migration"
        mcsservice_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$mcsservice_parent_migration")
        mcsservice_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$mcsservice_parent_migration")
        mcsservice_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$mcsservice_parent_migration")
        mcsservice_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$mcsservice_parent_migration")
        mcsservice_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$mcsservice_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$mcsservice_parent" = "$incremental_parent"
        test "$mcsservice_path" = "$mcsservice_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$mcsservice_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$mcsservice_recipe"
        test "$(grep -F "$mcsservice_binary" "$parent_recipe" | \
            grep -F '"sys\bin\mcsservice.dll"' | wc -l)" -eq 1
        mcsservice_current_hash=$(sha256sum "$mcsservice_binary" | awk '{print $1}')
        if [ "$mcsservice_current_hash" = "$mcsservice_hash" ]; then
            if [ ! -s "$mcsservice_stock_582" ]; then
                cp "$mcsservice_binary" "$mcsservice_stock_582"
            fi
        else
            test -s "$mcsservice_stock_582"
            test "$(sha256sum "$mcsservice_stock_582" | awk '{print $1}')" = \
                "$mcsservice_hash"
            cp "$mcsservice_stock_582" "$mcsservice_binary"
        fi
        test "$(sha256sum "$mcsservice_binary" | awk '{print $1}')" = \
            "$mcsservice_hash"
        test "$(sha256sum "$mcsservice_stock_582" | awk '{print $1}')" = \
            "$mcsservice_hash"
        printf '%s  %s\n' "$mcsservice_hash" "$mcsservice_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$mcsservice_parent_migration" \
            "$output/incremental-mcsservice-parent-582.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=mcsservice.dll"
    fi
    # Iteration 515 proves that MatrixMenu enters
    # CEikAppUiFactory::ReadAppInfoResourceL but stops before returning to
    # eikcore. eikcoctl.dll was still a stock ROM input outside the 28-file
    # cache. Expand the exact immutable 515 tuple once, then rebuild only this
    # component with close-only MatrixMenu tracing.
    if [ "$incremental_parent" = \
        515-symbian3-full-matrixmenu-eikappui-final-screenchange-defer-incremental ] && \
        ! grep -Fq "  $eikcoctl_binary" "$incremental_parent_release_manifest"
    then
        test -s "$eikcoctl_parent_migration"
        eikcoctl_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$eikcoctl_parent_migration")
        eikcoctl_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$eikcoctl_parent_migration")
        eikcoctl_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$eikcoctl_parent_migration")
        eikcoctl_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$eikcoctl_parent_migration")
        eikcoctl_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$eikcoctl_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$eikcoctl_parent" = "$incremental_parent"
        test "$eikcoctl_path" = "$eikcoctl_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$eikcoctl_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$eikcoctl_recipe"
        test "$(grep -F "$eikcoctl_binary" "$parent_recipe" | \
            grep -F '"sys\bin\eikcoctl.dll"' | wc -l)" -eq 1
        eikcoctl_current_hash=$(sha256sum "$eikcoctl_binary" | awk '{print $1}')
        if [ "$eikcoctl_current_hash" = "$eikcoctl_hash" ]; then
            if [ ! -s "$eikcoctl_stock_515" ]; then
                cp "$eikcoctl_binary" "$eikcoctl_stock_515"
            fi
        else
            test -s "$eikcoctl_stock_515"
            test "$(sha256sum "$eikcoctl_stock_515" | awk '{print $1}')" = \
                "$eikcoctl_hash"
            cp "$eikcoctl_stock_515" "$eikcoctl_binary"
        fi
        test "$(sha256sum "$eikcoctl_binary" | awk '{print $1}')" = \
            "$eikcoctl_hash"
        test "$(sha256sum "$eikcoctl_stock_515" | awk '{print $1}')" = \
            "$eikcoctl_hash"
        printf '%s  %s\n' "$eikcoctl_hash" "$eikcoctl_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$eikcoctl_parent_migration" \
            "$output/incremental-eikcoctl-parent-515.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=eikcoctl.dll"
    fi
    # Iteration 535 proves the mandatory MenuContent GetList reaches provider
    # creation but mcsmenuserver terminates while constructing its eager Nokia
    # service graph.  mcsmenu.dll predates the release cache, so pin and add
    # the exact immutable 535 parent binary before the UI-first server repair.
    if [ "$incremental_parent" = \
        535-symbian3-full-audited-ui-first-compat-sweep-incremental ] && \
        ! grep -Fq "  $mcsmenu_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$mcsmenu_parent_migration"
        mcsmenu_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$mcsmenu_parent_migration")
        mcsmenu_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$mcsmenu_parent_migration")
        mcsmenu_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$mcsmenu_parent_migration")
        mcsmenu_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$mcsmenu_parent_migration")
        mcsmenu_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$mcsmenu_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$mcsmenu_parent" = "$incremental_parent"
        test "$mcsmenu_path" = "$mcsmenu_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$mcsmenu_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$mcsmenu_recipe"
        test "$(grep -F "$mcsmenu_binary" "$parent_recipe" | \
            grep -F '"sys\bin\mcsmenu.dll"' | wc -l)" -eq 1
        mcsmenu_current_hash=$(sha256sum "$mcsmenu_binary" | awk '{print $1}')
        if [ "$mcsmenu_current_hash" = "$mcsmenu_hash" ]; then
            if [ ! -s "$mcsmenu_stock_535" ]; then
                cp "$mcsmenu_binary" "$mcsmenu_stock_535"
            fi
        else
            test -s "$mcsmenu_stock_535"
            test "$(sha256sum "$mcsmenu_stock_535" | awk '{print $1}')" = \
                "$mcsmenu_hash"
            cp "$mcsmenu_stock_535" "$mcsmenu_binary"
        fi
        test "$(sha256sum "$mcsmenu_binary" | awk '{print $1}')" = \
            "$mcsmenu_hash"
        test "$(sha256sum "$mcsmenu_stock_535" | awk '{print $1}')" = \
            "$mcsmenu_hash"
        printf '%s  %s\n' "$mcsmenu_hash" "$mcsmenu_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$mcsmenu_parent_migration" \
            "$output/incremental-mcsmenu-parent-535.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=mcsmenu.dll"
    fi
    # Iteration 536 localizes the remaining failure to CMenuEng::NewL, which
    # lives in mcsmenueng.dll rather than the already tracked mcsmenu.dll.
    # Expand the exact immutable 536 tuple once for close-only core tracing.
    if [ "$incremental_parent" = \
        536-symbian3-full-mcs-ui-first-compat-incremental ] && \
        ! grep -Fq "  $mcsmenu_core_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$mcsmenu_core_parent_migration"
        mcsmenu_core_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$mcsmenu_core_parent_migration")
        mcsmenu_core_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$mcsmenu_core_parent_migration")
        mcsmenu_core_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$mcsmenu_core_parent_migration")
        mcsmenu_core_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$mcsmenu_core_parent_migration")
        mcsmenu_core_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$mcsmenu_core_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$mcsmenu_core_parent" = "$incremental_parent"
        test "$mcsmenu_core_path" = "$mcsmenu_core_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$mcsmenu_core_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$mcsmenu_core_recipe"
        test "$(grep -F "$mcsmenu_core_binary" "$parent_recipe" | \
            grep -F '"sys\bin\mcsmenueng.dll"' | wc -l)" -eq 1
        mcsmenu_core_current_hash=$(sha256sum "$mcsmenu_core_binary" | awk '{print $1}')
        if [ "$mcsmenu_core_current_hash" = "$mcsmenu_core_hash" ]; then
            if [ ! -s "$mcsmenu_core_stock_536" ]; then
                cp "$mcsmenu_core_binary" "$mcsmenu_core_stock_536"
            fi
        else
            test -s "$mcsmenu_core_stock_536"
            test "$(sha256sum "$mcsmenu_core_stock_536" | awk '{print $1}')" = \
                "$mcsmenu_core_hash"
            cp "$mcsmenu_core_stock_536" "$mcsmenu_core_binary"
        fi
        test "$(sha256sum "$mcsmenu_core_binary" | awk '{print $1}')" = \
            "$mcsmenu_core_hash"
        test "$(sha256sum "$mcsmenu_core_stock_536" | awk '{print $1}')" = \
            "$mcsmenu_core_hash"
        printf '%s  %s\n' "$mcsmenu_core_hash" "$mcsmenu_core_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$mcsmenu_core_parent_migration" \
            "$output/incremental-mcsmenueng-parent-536.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=mcsmenueng.dll"
    fi
    # Iteration 549 carries the source-built WServ object evidence but predates
    # adding the final wserv_nga.exe tuple to the incremental release cache.
    # Expand that exact parent once from its pinned canonical image and the
    # still-matching native binary hash; the immutable package is not modified.
    if [ "$incremental_parent" = \
        549-symbian3-full-matrixmenu-rom-presentation-fallback-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            47e607f60f2e42d952ab923c106a1f4f77554639b3216d7cbc8646046fdfee6f
        test -s "$output/wserv-nga-urel.sha256"
        grep -qx \
            "1a861870a9849a93b0c07e04151cf7e1fa5863077feafa5ff200588065c0282d  $wserv_binary" \
            "$output/wserv-nga-urel.sha256"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            1a861870a9849a93b0c07e04151cf7e1fa5863077feafa5ff200588065c0282d
        cat "$output/wserv-nga-urel.sha256" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    # Iteration 550's verified 35-file cache already contains WServ, while its
    # legacy release-evidence scan still only sees copied *-urel.sha256 files.
    # Import exactly that cache-manifest tuple so later WServ iterations do not
    # require another migration boundary.
    if [ "$incremental_parent" = \
        550-symbian3-full-wserv-client-window-create-trace-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "385b4d4bc38b631b7559aa610fdbca30a6541fe1784e6343d88354dc06510b7f  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            385b4d4bc38b631b7559aa610fdbca30a6541fe1784e6343d88354dc06510b7f
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        551-symbian3-full-wserv-client-window-log-capacity-512-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "9d4d78122c2b3907e32e60b56a78bef9e18e2bc450564cd6a017dd7d5562992b  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            9d4d78122c2b3907e32e60b56a78bef9e18e2bc450564cd6a017dd7d5562992b
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        552-symbian3-full-wserv-matrixmenu-window-trace-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "76e92fc421fb37298a96a479ed7ef6a2d7531cd39fe0c331566063eab735590d  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            76e92fc421fb37298a96a479ed7ef6a2d7531cd39fe0c331566063eab735590d
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        553-symbian3-full-wserv-exact-grid-window-trace-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "9676923e9d27c713009fcf96e986f54ff9c18dd702fd25062ae37dfcfeb9f0d9  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            9676923e9d27c713009fcf96e986f54ff9c18dd702fd25062ae37dfcfeb9f0d9
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        554-symbian3-full-wserv-grid-owner-trace-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "ca5b1f349749866e6787720c3af98fab7d9397d9691525968fc1fa9dabd9ff41  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            ca5b1f349749866e6787720c3af98fab7d9397d9691525968fc1fa9dabd9ff41
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        555-symbian3-full-wserv-property-armed-grid-request-trace-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "037856ebaa2c256f17c57fa936e7045e165ecac0e8a63ec8826fb5b9c6caa904  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            037856ebaa2c256f17c57fa936e7045e165ecac0e8a63ec8826fb5b9c6caa904
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    if [ "$incremental_parent" = \
        556-symbian3-full-wserv-matrixmenu-command-buffer-compat-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test -s "$parent_cache_manifest"
        wserv_cache_record=$(awk -F '\t' -v path="$wserv_binary" \
            '$2 == path { print $1 "  " $2 }' "$parent_cache_manifest")
        test "$wserv_cache_record" = \
            "06f24c74d868bb59357917a222354677817b8174f991e94b320a7b076f97817c  $wserv_binary"
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            06f24c74d868bb59357917a222354677817b8174f991e94b320a7b076f97817c
        printf '%s\n' "$wserv_cache_record" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        echo "HTCLEO_INCREMENTAL_PARENT_CACHE_EVIDENCE_IMPORTED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    # Gate 15 baseline 640 still carries the proven WServ binary in its ROM,
    # but its 38-file release cache never imported that tuple.  Pin the exact
    # immutable parent recipe/initrd/binary before the Gate 16 pointer fix.
    if [ "$incremental_parent" = \
        640-symbian3-full-mcs-atomic-size-data-transfer-incremental ] && \
        ! grep -Fq "  $wserv_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$wserv_parent_640_migration"
        wserv_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$wserv_parent_640_migration")
        wserv_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$wserv_parent_640_migration")
        wserv_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$wserv_parent_640_migration")
        wserv_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$wserv_parent_640_migration")
        wserv_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$wserv_parent_640_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$wserv_parent" = "$incremental_parent"
        test "$wserv_path" = "$wserv_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$wserv_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$wserv_recipe"
        test "$(grep -F "$wserv_binary" "$parent_recipe" | \
            grep -F '"sys\bin\ewsrv.exe"' | wc -l)" -eq 1
        test "$(sha256sum "$wserv_binary" | awk '{print $1}')" = \
            "$wserv_hash"
        printf '%s  %s\n' "$wserv_hash" "$wserv_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$wserv_parent_640_migration" \
            "$output/incremental-wserv-parent-640.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=wserv_nga.exe"
    fi
    # Iteration 657 first identifies PtiEngine's missing-keymap KErrCorrupt,
    # while PtiEngine.dll was still an untracked stock ROM input.  Import the
    # exact immutable stock tuple once before rebuilding only that DLL.
    if [ "$incremental_parent" = \
        657-symbian3-full-ecom-matrixmenu-list-failopen-incremental ] && \
        ! grep -Fq "  $ptiengine_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$ptiengine_parent_migration"
        pti_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$ptiengine_parent_migration")
        pti_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$ptiengine_parent_migration")
        pti_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$ptiengine_parent_migration")
        pti_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$ptiengine_parent_migration")
        pti_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$ptiengine_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$pti_parent" = "$incremental_parent"
        test "$pti_path" = "$ptiengine_binary"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$pti_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$pti_recipe"
        test "$(grep -F "$ptiengine_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\ptiengine.dll"' | wc -l)" -eq 1
        test -s "$ptiengine_stock_657"
        test "$(sha256sum "$ptiengine_stock_657" | awk '{print $1}')" = \
            "$pti_hash"
        if [ "$(sha256sum "$ptiengine_binary" | awk '{print $1}')" != \
            "$pti_hash" ]; then
            cp "$ptiengine_stock_657" "$ptiengine_binary"
        fi
        test "$(sha256sum "$ptiengine_binary" | awk '{print $1}')" = \
            "$pti_hash"
        printf '%s  %s\n' "$pti_hash" "$ptiengine_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$ptiengine_parent_migration" \
            "$output/incremental-ptiengine-parent-657.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=PtiEngine.dll"
    fi
    # Iteration 669 identifies the final ready AO as CLiwEcomMonitor from the
    # previously untracked liwServiceHandler.dll.  Pin the exact 669 binary and
    # immutable ROM tuple before adding the status-aware notification guard.
    if [ "$incremental_parent" = \
        669-symbian3-full-cone-ready-ao-identity-trace-incremental ] && \
        ! grep -Fq "  $liw_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$liw_parent_migration"
        liw_parent=$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$liw_parent_migration")
        liw_initrd=$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$liw_parent_migration")
        liw_recipe=$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$liw_parent_migration")
        liw_path=$(sed -n 's/^BINARY_PATH=//p' \
            "$liw_parent_migration")
        liw_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$liw_parent_migration")
        liw_destination=$(sed -n 's/^ROM_DESTINATION=//p' \
            "$liw_parent_migration")
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$liw_parent" = "$incremental_parent"
        test "$liw_path" = "$liw_binary"
        test "$liw_destination" = 'sys\bin\liwservicehandler.dll'
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$liw_initrd"
        test -s "$parent_recipe"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$liw_recipe"
        test "$(grep -F "$liw_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\liwservicehandler.dll"' | wc -l)" -eq 1
        test -s "$liw_stock_669"
        test "$(sha256sum "$liw_stock_669" | awk '{print $1}')" = \
            "$liw_hash"
        if [ "$(sha256sum "$liw_binary" | awk '{print $1}')" != \
            "$liw_hash" ]; then
            cp "$liw_stock_669" "$liw_binary"
        fi
        test "$(sha256sum "$liw_binary" | awk '{print $1}')" = \
            "$liw_hash"
        printf '%s  %s\n' "$liw_hash" "$liw_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$liw_parent_migration" \
            "$output/incremental-liwservicehandler-parent-669.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=liwServiceHandler.dll"
    fi
    # Iteration 670 is the first hardware-proven Gate 14/15 baseline, but its
    # release cache predates the four stock HomeScreen executables rebuilt by
    # the Gate 16 closure.  Import each immutable 670 tuple before touching
    # source so incremental identity remains fail-closed.
    if [ "$incremental_parent" = \
        670-symbian3-full-liw-ecom-monitor-status-guard-incremental ]
    then
        for homescreen_migration_spec in \
            "aifw|$homescreen_aifw_binary|$homescreen_aifw_stock_670|$homescreen_aifw_parent_migration|sys\\bin\\aifw.dll" \
            "aiidleint|$homescreen_idle_binary|$homescreen_idle_stock_670|$homescreen_idle_parent_migration|sys\\bin\\aiidleint.dll" \
            "ailaunch|$homescreen_launch_binary|$homescreen_launch_stock_670|$homescreen_launch_parent_migration|sys\\bin\\ailaunch.exe" \
            "homescreen|$homescreen_binary|$homescreen_stock_670|$homescreen_parent_migration|sys\\bin\\homescreen.exe"
        do
            old_ifs=$IFS
            IFS='|'
            set -- $homescreen_migration_spec
            IFS=$old_ifs
            homescreen_label=$1
            homescreen_path=$2
            homescreen_stock=$3
            homescreen_migration=$4
            homescreen_destination=$5
            if grep -Fq "  $homescreen_path" \
                "$incremental_parent_release_manifest"; then
                continue
            fi
            test "$incremental_migration" = 1
            test -s "$homescreen_migration"
            test "$(sed -n 's/^PARENT_PACKAGE=//p' \
                "$homescreen_migration")" = "$incremental_parent"
            test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
                "$homescreen_migration")" = \
                "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
            parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
            test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
                "$homescreen_migration")" = \
                "$(sha256sum "$parent_recipe" | awk '{print $1}')"
            test "$(sed -n 's/^BINARY_PATH=//p' \
                "$homescreen_migration")" = "$homescreen_path"
            test "$(sed -n 's/^ROM_DESTINATION=//p' \
                "$homescreen_migration")" = "$homescreen_destination"
            homescreen_parent_hash=$(sed -n \
                's/^PARENT_BINARY_SHA256=//p' "$homescreen_migration")
            test -s "$homescreen_stock"
            test "$(sha256sum "$homescreen_stock" | awk '{print $1}')" = \
                "$homescreen_parent_hash"
            test "$(grep -F "$homescreen_path" "$parent_recipe" | \
                grep -Fi "\"$homescreen_destination\"" | wc -l)" -eq 1
            if [ "$(sha256sum "$homescreen_path" | awk '{print $1}')" != \
                "$homescreen_parent_hash" ]; then
                cp "$homescreen_stock" "$homescreen_path"
            fi
            test "$(sha256sum "$homescreen_path" | awk '{print $1}')" = \
                "$homescreen_parent_hash"
            printf '%s  %s\n' "$homescreen_parent_hash" \
                "$homescreen_path" >>"$incremental_parent_release_manifest"
            cp "$homescreen_migration" \
                "$output/incremental-homescreen-$homescreen_label-parent-670.txt"
            echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=$homescreen_label"
        done
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
    fi
    # Iteration 675 proves that the stock XML controller resolves through the
    # repaired ECom SPI, then EikStart exits before the HomeScreen becomes
    # visible.  ai3xmluimain.dll was an untracked stock ROM input, so pin its
    # exact 675 image/recipe/binary tuple before the first source-built trace.
    if [ "$incremental_parent" = \
        675-symbian3-full-homescreen-ecom-spi-registry-repair-incremental ] && \
        ! grep -Fq "  $ai3xml_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$ai3xml_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$ai3xml_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$ai3xml_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$ai3xml_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$ai3xml_parent_migration")" = "$ai3xml_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$ai3xml_parent_migration")" = 'sys\bin\ai3xmluimain.dll'
        ai3xml_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$ai3xml_parent_migration")
        test -s "$ai3xml_stock_675"
        test "$(sha256sum "$ai3xml_stock_675" | awk '{print $1}')" = \
            "$ai3xml_parent_hash"
        test "$(grep -F "$ai3xml_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\ai3xmluimain.dll"' | wc -l)" -eq 1
        if [ ! -s "$ai3xml_binary" ] || \
            [ "$(sha256sum "$ai3xml_binary" | awk '{print $1}')" != \
                "$ai3xml_parent_hash" ]; then
            cp "$ai3xml_stock_675" "$ai3xml_binary"
        fi
        test "$(sha256sum "$ai3xml_binary" | awk '{print $1}')" = \
            "$ai3xml_parent_hash"
        printf '%s  %s\n' "$ai3xml_parent_hash" "$ai3xml_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$ai3xml_parent_migration" \
            "$output/incremental-ai3xmluimain-parent-675.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=ai3xmluimain.dll"
    fi
    # Iteration 680 first enters the real Xn AppUi adapter.  Its stock ROM DLL
    # predates the release cache, so pin the exact parent image/recipe/binary
    # tuple before the first source-built behavior-neutral trace.
    if [ "$incremental_parent" = \
        680-symbian3-full-aknsgc-homescreen-local-layout-incremental ] && \
        ! grep -Fq "  $xn3layout_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$xn3layout_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$xn3layout_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$xn3layout_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$xn3layout_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$xn3layout_parent_migration")" = "$xn3layout_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$xn3layout_parent_migration")" = 'sys\bin\xn3layoutengine.dll'
        xn3layout_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$xn3layout_parent_migration")
        test -s "$xn3layout_stock_680"
        test "$(sha256sum "$xn3layout_stock_680" | awk '{print $1}')" = \
            "$xn3layout_parent_hash"
        test "$(grep -F "$xn3layout_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\xn3layoutengine.dll"' | wc -l)" -eq 1
        if [ ! -s "$xn3layout_binary" ] || \
            [ "$(sha256sum "$xn3layout_binary" | awk '{print $1}')" != \
                "$xn3layout_parent_hash" ]; then
            cp "$xn3layout_stock_680" "$xn3layout_binary"
        fi
        test "$(sha256sum "$xn3layout_binary" | awk '{print $1}')" = \
            "$xn3layout_parent_hash"
        printf '%s  %s\n' "$xn3layout_parent_hash" "$xn3layout_binary" \
            >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$xn3layout_parent_migration" \
            "$output/incremental-xn3layoutengine-parent-680.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=xn3layoutengine.dll"
    fi
    # Iteration 689 reaches the stock HomeScreen settings API for the first
    # time.  Pin its exact ROM input before adding behavior-neutral LIW/TLS
    # checkpoints in the source-built DLL.
    if [ "$incremental_parent" = \
        689-symbian3-full-xnappuiimpl-startup-trace-incremental ] && \
        ! grep -Fq "  $hspluginsettings_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hspluginsettings_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hspluginsettings_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hspluginsettings_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hspluginsettings_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$hspluginsettings_parent_migration")" = "$hspluginsettings_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$hspluginsettings_parent_migration")" = 'sys\bin\hspluginsettings.dll'
        hspluginsettings_parent_hash=$(sed -n \
            's/^PARENT_BINARY_SHA256=//p' "$hspluginsettings_parent_migration")
        if [ ! -s "$hspluginsettings_stock_689" ]; then
            test "$(sha256sum "$hspluginsettings_binary" | awk '{print $1}')" = \
                "$hspluginsettings_parent_hash"
            cp "$hspluginsettings_binary" "$hspluginsettings_stock_689"
        fi
        test "$(sha256sum "$hspluginsettings_stock_689" | awk '{print $1}')" = \
            "$hspluginsettings_parent_hash"
        test "$(grep -F "$hspluginsettings_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\hspluginsettings.dll"' | wc -l)" -eq 1
        if [ ! -s "$hspluginsettings_binary" ] || \
            [ "$(sha256sum "$hspluginsettings_binary" | awk '{print $1}')" != \
                "$hspluginsettings_parent_hash" ]; then
            cp "$hspluginsettings_stock_689" "$hspluginsettings_binary"
        fi
        test "$(sha256sum "$hspluginsettings_binary" | awk '{print $1}')" = \
            "$hspluginsettings_parent_hash"
        printf '%s  %s\n' "$hspluginsettings_parent_hash" \
            "$hspluginsettings_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hspluginsettings_parent_migration" \
            "$output/incremental-hspluginsettings-parent-689.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hspluginsettings.dll"
    fi
    # Hardware 690 proves the LIW dispatch enters HSPS but receives
    # KErrNotFound because the server has no installed HomeScreen ODT.  The
    # stock server executable predates the release cache, so pin its exact
    # 690 image/recipe/binary tuple before the first HTC Leo family rebuild.
    if [ "$incremental_parent" = \
        690-symbian3-full-hspluginsettings-startup-trace-incremental ] && \
        ! grep -Fq "  $hspsthemeserver_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hspsthemeserver_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hspsthemeserver_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hspsthemeserver_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hspsthemeserver_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$hspsthemeserver_parent_migration")" = "$hspsthemeserver_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$hspsthemeserver_parent_migration")" = 'sys\bin\hspsthemeserver.exe'
        hspsthemeserver_parent_hash=$(sed -n \
            's/^PARENT_BINARY_SHA256=//p' "$hspsthemeserver_parent_migration")
        if [ ! -s "$hspsthemeserver_stock_690" ]; then
            test "$(sha256sum "$hspsthemeserver_binary" | awk '{print $1}')" = \
                "$hspsthemeserver_parent_hash"
            cp "$hspsthemeserver_binary" "$hspsthemeserver_stock_690"
        fi
        test "$(sha256sum "$hspsthemeserver_stock_690" | awk '{print $1}')" = \
            "$hspsthemeserver_parent_hash"
        test "$(grep -F "$hspsthemeserver_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\hspsthemeserver.exe"' | wc -l)" -eq 1
        if [ ! -s "$hspsthemeserver_binary" ] || \
            [ "$(sha256sum "$hspsthemeserver_binary" | awk '{print $1}')" != \
                "$hspsthemeserver_parent_hash" ]; then
            cp "$hspsthemeserver_stock_690" "$hspsthemeserver_binary"
        fi
        test "$(sha256sum "$hspsthemeserver_binary" | awk '{print $1}')" = \
            "$hspsthemeserver_parent_hash"
        printf '%s  %s\n' "$hspsthemeserver_parent_hash" \
            "$hspsthemeserver_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hspsthemeserver_parent_migration" \
            "$output/incremental-hspsthemeserver-parent-690.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hspsthemeserver.exe"
    fi
    # Hardware 697 proves the stock definition-engine DLL is found and loaded,
    # but its factory leaves while constructing a nested ECom XML parser.  Pin
    # the exact 697 PDK binary before the first source-built lazy-parser fix.
    if [ "$incremental_parent" = \
        697-symbian3-full-hsps-client-load-trace-incremental ] && \
        ! grep -Fq "  $hsps_definition_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hsps_definition_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hsps_definition_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hsps_definition_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hsps_definition_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$hsps_definition_parent_migration")" = "$hsps_definition_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$hsps_definition_parent_migration")" = \
            'sys\bin\hspsdefinitionengine.dll'
        hsps_definition_parent_hash=$(sed -n \
            's/^PARENT_BINARY_SHA256=//p' \
            "$hsps_definition_parent_migration")
        test "$(sha256sum "$hsps_definition_stock_697" | awk '{print $1}')" = \
            "$hsps_definition_parent_hash"
        test "$(grep -F "$hsps_definition_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\hspsdefinitionengine.dll"' | wc -l)" -eq 1
        cp "$hsps_definition_stock_697" "$hsps_definition_binary"
        test "$(sha256sum "$hsps_definition_binary" | awk '{print $1}')" = \
            "$hsps_definition_parent_hash"
        printf '%s  %s\n' "$hsps_definition_parent_hash" \
            "$hsps_definition_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hsps_definition_parent_migration" \
            "$output/incremental-hspsdefinitionengine-parent-697.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hspsdefinitionengine.dll"
    fi
    # Iteration 701 proves that the HSPS definition engine requests the stock
    # libxml2 SAX ECom variant, while the Syborg STEM recipe contains only the
    # legacy expat parser.  Track the exact missing Nokia DLL as a one-time
    # parent-cache expansion before adding its DLL/resource/SPI tuple to ROM.
    if [ "$incremental_parent" = \
        701-symbian3-full-hsps-parser-ecom-recovery-incremental ] && \
        ! grep -Fq "  $libxml_sax_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$libxml_sax_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$libxml_sax_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$libxml_sax_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$libxml_sax_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$libxml_sax_parent_migration")" = "$libxml_sax_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$libxml_sax_parent_migration")" = \
            'sys\bin\xmlenginesaxplugin.dll'
        libxml_sax_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$libxml_sax_parent_migration")
        test "$(sha256sum "$libxml_sax_binary" | awk '{print $1}')" = \
            "$libxml_sax_parent_hash"
        test "$(sed -n 's/^RESOURCE_PATH=//p' \
            "$libxml_sax_parent_migration")" = "$libxml_sax_resource"
        test "$(sed -n 's/^RESOURCE_DESTINATION=//p' \
            "$libxml_sax_parent_migration")" = \
            'resource\plugins\xmlenginesaxplugin.rsc'
        test "$(sed -n 's/^RESOURCE_SHA256=//p' \
            "$libxml_sax_parent_migration")" = \
            "$(sha256sum "$libxml_sax_resource" | awk '{print $1}')"
        test "$(sed -n 's/^ECOM_IMPLEMENTATION_UID=//p' \
            "$libxml_sax_parent_migration")" = 101f9783
        ! grep -Fiq '"sys\bin\xmlenginesaxplugin.dll"' "$parent_recipe"
        ! grep -Fiq '"resource\plugins\xmlenginesaxplugin.rsc"' "$parent_recipe"
        printf '%s  %s\n' "$libxml_sax_parent_hash" \
            "$libxml_sax_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$libxml_sax_parent_migration" \
            "$output/incremental-xmlenginesaxplugin-parent-701.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=xmlenginesaxplugin.dll"
    fi
    # Hardware 703 reaches the real root ODT and max_child=3, but the LIW
    # application configuration exposes zero plug-in maps.  Pin the exact
    # provider and its unchanged ECom resource before the first source repair.
    if [ "$incremental_parent" = \
        703-symbian3-full-xn-loadui-root-view-trace-incremental ] && \
        ! grep -Fq "  $hspsprovider_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test -s "$hspsprovider_parent_migration"
        test "$(sed -n 's/^PARENT_PACKAGE=//p' \
            "$hspsprovider_parent_migration")" = "$incremental_parent"
        test "$(sed -n 's/^PARENT_INITRD_SHA256=//p' \
            "$hspsprovider_parent_migration")" = \
            "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' \
            "$hspsprovider_parent_migration")" = \
            "$(sha256sum "$parent_recipe" | awk '{print $1}')"
        test "$(sed -n 's/^BINARY_PATH=//p' \
            "$hspsprovider_parent_migration")" = "$hspsprovider_binary"
        test "$(sed -n 's/^ROM_DESTINATION=//p' \
            "$hspsprovider_parent_migration")" = 'sys\bin\hspsprovider.dll'
        hspsprovider_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' \
            "$hspsprovider_parent_migration")
        test "$(sha256sum "$hspsprovider_stock_703" | awk '{print $1}')" = \
            "$hspsprovider_parent_hash"
        test "$(sed -n 's/^RESOURCE_PATH=//p' \
            "$hspsprovider_parent_migration")" = "$hspsprovider_resource"
        test "$(sed -n 's/^RESOURCE_DESTINATION=//p' \
            "$hspsprovider_parent_migration")" = \
            'resource\plugins\hspsprovider.rsc'
        test "$(sed -n 's/^RESOURCE_SHA256=//p' \
            "$hspsprovider_parent_migration")" = \
            "$(sha256sum "$hspsprovider_stock_resource_703" | awk '{print $1}')"
        test "$(grep -F "$hspsprovider_binary" "$parent_recipe" | \
            grep -Fi '"sys\bin\hspsprovider.dll"' | wc -l)" -eq 1
        test "$(grep -F "$hspsprovider_resource" "$parent_recipe" | \
            grep -Fi '"resource\plugins\hspsprovider.rsc"' | wc -l)" -eq 1
        cp "$hspsprovider_stock_703" "$hspsprovider_binary"
        cp "$hspsprovider_stock_resource_703" "$hspsprovider_resource"
        printf '%s  %s\n' "$hspsprovider_parent_hash" \
            "$hspsprovider_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" \
            "$incremental_parent_release_manifest"
        cp "$hspsprovider_parent_migration" \
            "$output/incremental-hspsprovider-parent-703.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=hspsprovider.dll"
    fi
    # Pin the previously stock provider before the first notification repair.
    # Existing immutable 739 contents are never edited or expanded in place.
    if [ "$incremental_parent" = 739-symbian3-full-home-menu-after-pointer-dispatch-incremental ] && \
        ! grep -Fq "  $mcsprovider_binary" "$incremental_parent_release_manifest"
    then
        test "$(sed -n 's/^PARENT_PACKAGE=//p' "$mcsprovider_pin")" = "$incremental_parent"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$(sed -n 's/^PARENT_INITRD_SHA256=//p' "$mcsprovider_pin")"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' "$mcsprovider_pin")"
        test "$(grep -F "$mcsprovider_binary" "$parent_recipe" | grep -F '"sys\bin\mcsprovider.dll"' | wc -l)" -eq 1
        mcsprovider_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' "$mcsprovider_pin")
        if [ ! -s "$mcsprovider_stock" ]; then
            test "$(sha256sum "$mcsprovider_binary" | awk '{print $1}')" = "$mcsprovider_parent_hash"
            cp "$mcsprovider_binary" "$mcsprovider_stock"
        fi
        test "$(sha256sum "$mcsprovider_stock" | awk '{print $1}')" = "$mcsprovider_parent_hash"
        test "$(wc -c <"$mcsprovider_stock" | tr -d ' ')" = 5402
        cp "$mcsprovider_stock" "$mcsprovider_binary"
        if [ ! -s "$mcsprovider_stock_resource" ]; then
            cp "$mcsprovider_resource" "$mcsprovider_stock_resource"
        fi
        test "$(sha256sum "$mcsprovider_stock_resource" | awk '{print $1}')" = \
            "$(sed -n 's/^RESOURCE_SHA256=//p' "$mcsprovider_pin")"
        cp "$mcsprovider_stock_resource" "$mcsprovider_resource"
        printf '%s  %s\n' "$mcsprovider_parent_hash" "$mcsprovider_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        cp "$mcsprovider_pin" "$output/incremental-mcsprovider-parent-739.txt"
        echo "HTCLEO_INCREMENTAL_PARENT_EXPANDED parent=$incremental_parent binary=mcsprovider.dll"
    fi
    #793 tracks an ALREADY packaged plugin; no new ROM member or service.
    if [ "$incremental_resource_policy" = gate17-menu-launch-frontier ]; then
        test "$incremental_migration" = 1
        test "$(sed -n 's/^PARENT_PACKAGE=//p' "$menuhandler_pin")" = "$incremental_parent"
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            "$(sed -n 's/^PARENT_INITRD_SHA256=//p' "$menuhandler_pin")"
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            "$(sed -n 's/^PARENT_RECIPE_SHA256=//p' "$menuhandler_pin")"
        test "$(grep -F "$menuhandler_binary" "$parent_recipe" | grep -F '"sys\bin\mcsmenuhandler.dll"' | wc -l)" -eq 1
        ! grep -Fq "  $menuhandler_binary" "$incremental_parent_release_manifest"
        menuhandler_parent_hash=$(sed -n 's/^PARENT_BINARY_SHA256=//p' "$menuhandler_pin")
        if [ ! -s "$menuhandler_stock" ]; then
            test "$(sha256sum "$menuhandler_binary" | awk '{print $1}')" = "$menuhandler_parent_hash"
            cp "$menuhandler_binary" "$menuhandler_stock"
        fi
        test "$(sha256sum "$menuhandler_stock" | awk '{print $1}')" = "$menuhandler_parent_hash"
        test "$(wc -c <"$menuhandler_stock" | tr -d ' ')" = 4327
        cp "$menuhandler_stock" "$menuhandler_binary"
        if [ ! -s "$menuhandler_stock_resource" ]; then
            cp "$menuhandler_resource" "$menuhandler_stock_resource"
        fi
        test "$(sha256sum "$menuhandler_stock_resource" | awk '{print $1}')" = \
            "$(sed -n 's/^RESOURCE_SHA256=//p' "$menuhandler_pin")"
        cp "$menuhandler_stock_resource" "$menuhandler_resource"
        printf '%s  %s\n' "$menuhandler_parent_hash" "$menuhandler_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 62
        cp "$menuhandler_pin" "$output/incremental-menuhandler-parent-792.txt"
        echo 'HTCLEO_INCREMENTAL_PARENT_EXPANDED existing-menuhandler cache61-to62 pinned792'
    fi
    #821 tracks the already-present stock GSFramework without changing820.
    if [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ]; then
        test "$incremental_migration" = 1
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = c0586f069435ef7c40438dd4e0593e7189050debac8c2a0979c010153345b2cb
        test "$(sha256sum "$incremental_parent_build/htcleo_symbian3_full_native.oby" | awk '{print $1}')" = e3a2eb86193236813055b908e3e98f67e1c08318a5742d60038b3ae71d2b2d3d
        test "$(grep -F "$gsframework_binary" "$incremental_parent_build/htcleo_symbian3_full_native.oby" | grep -F '"sys\bin\gsframework.dll"' | wc -l)" -eq 1
        gsframework_stock="$project/Symbian/output/iteration-evidence/821-gsapp-plugin-frontier/gsframework-stock-820.dll"
        test "$(sha256sum "$gsframework_stock" | awk '{print $1}')" = e7f097ce4829130ef6333598796f6dc67ce86e5a8c7bc2ef7eee190e576b8ac5
        ! grep -Fq "  $gsframework_binary" "$incremental_parent_release_manifest"
        cp "$gsframework_stock" "$gsframework_binary"
        printf '%s  %s\n' e7f097ce4829130ef6333598796f6dc67ce86e5a8c7bc2ef7eee190e576b8ac5 "$gsframework_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        test "$(wc -l <"$incremental_parent_release_manifest")" -eq 63
        echo 'HTCLEO_INCREMENTAL_PARENT_EXPANDED existing-gsframework cache62-to63 pinned820'
    fi
    # 773: track the previously reused core as an explicit incremental input.
    # Pin the772 image/recipe/core tuple, keep an immutable local recovery copy,
    # and never expand the tested772 package in place.
    if [ "$incremental_parent" = 772-symbian3-full-logless-liveness-badge-incremental ] && \
        ! grep -Fq "  $native_kernel_binary" "$incremental_parent_release_manifest"
    then
        test "$incremental_migration" = 1
        test "$(sha256sum "$incremental_parent_root/initrd.gz" | awk '{print $1}')" = \
            d4e52aa30389957d689a02df67f3b59aae19f13c6ce463a094f5450ee8dea793
        parent_recipe="$incremental_parent_build/htcleo_symbian3_full_native.oby"
        test "$(sha256sum "$parent_recipe" | awk '{print $1}')" = \
            1a66d01247517a817239cf1d573befc56cf63cf66c59888716d39c60e1a3c663
        test "$(grep -F "$native_kernel_binary" "$parent_recipe" | wc -l)" -eq 1
        kernel_parent_hash=11b1e892ed118d8002d1bc1813b7c432b591e400bbd14cd351235e772e32e055
        kernel_parent_copy="$output/773-parent-kernel.exe"
        if [ ! -s "$kernel_parent_copy" ]; then
            test "$(sha256sum "$native_kernel_binary" | awk '{print $1}')" = "$kernel_parent_hash"
            cp "$native_kernel_binary" "$kernel_parent_copy"
        fi
        test "$(sha256sum "$kernel_parent_copy" | awk '{print $1}')" = "$kernel_parent_hash"
        cp "$kernel_parent_copy" "$native_kernel_binary"
        printf '%s  %s\n' "$kernel_parent_hash" "$native_kernel_binary" >>"$incremental_parent_release_manifest"
        sort -u -o "$incremental_parent_release_manifest" "$incremental_parent_release_manifest"
        printf 'PARENT_PACKAGE=%s\nPARENT_KERNEL_SHA256=%s\nBINARY_PATH=%s\n' \
            "$incremental_parent" "$kernel_parent_hash" "$native_kernel_binary" \
            >"$output/incremental-kernel-parent-772.txt"
        echo 'HTCLEO_INCREMENTAL_PARENT_EXPANDED core-kernel cache53-to54 pinned772'
    fi
    if [ -s "$output/773-parent-kernel.exe" ] && \
        ! grep -Fq "  $native_kernel_binary" "$incremental_parent_release_manifest"; then
        test "$(sha256sum "$native_kernel_binary" | awk '{print $1}')" = \
            11b1e892ed118d8002d1bc1813b7c432b591e400bbd14cd351235e772e32e055 || {
            echo 'ERROR: older parent does not track the modified core; restore its verified core before building.' >&2
            exit 1
        }
    fi
    if [ "$incremental_resource_policy" = gate17-font-settings ]; then
        python3 "$project/Symbian/scripts/prepare-htcleo-gate17-entry.py" \
            --sdk "$full_epocroot" --parent "$incremental_parent_root" \
            --plan "$gate17_plan" --extend-release-manifest "$incremental_parent_release_manifest"
    fi
    if [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
        python3 "$project/Symbian/scripts/prepare-htcleo-about-entry.py" \
            --parent "$incremental_parent_root" --plan "$about_entry_plan" --config "$about_entry_config" \
            --extend-release-manifest "$incremental_parent_release_manifest"
        echo 'HTCLEO_ABOUT_CACHE_ADDITIONS=65-original-plus3-pinned-stock-inputs'
    fi
    test -s "$incremental_parent_release_manifest"
    if [ "$incremental_resource_policy" = gate17-font-family-binding ]; then
        python3 "$font_family_binding" --extend-release-manifest "$incremental_parent_release_manifest"
    fi
    if awk '{print $2}' "$incremental_parent_release_manifest" | \
        sort | uniq -d | grep -q .; then
        echo "ERROR: conflicting parent release hashes" >&2
        exit 1
    fi
    if [ "$incremental_migration" = 1 ]; then
        : >"$incremental_guard_manifest"
        while read -r _parent_hash binary_path
        do
            test -s "$binary_path"
            sha256sum "$binary_path" >>"$incremental_guard_manifest"
        done <"$incremental_parent_release_manifest"
        printf 'MIGRATION_PARENT=%s\nREASON=parent-package-predates-release-cache\n' \
            "$incremental_parent" >"$incremental_parent_preflight_log"
        echo "HTCLEO_INCREMENTAL_MIGRATION_SEED_OK parent=$incremental_parent"
    else
        if [ "$incremental_eiksrvs_resume" = 1 ]; then
            grep -Fv "  $eiksrvs_binary" \
                "$incremental_parent_release_manifest" \
                >"$work/incremental-parent-release-resume-check.sha256"
            sha256sum -c "$work/incremental-parent-release-resume-check.sha256" \
                >"$incremental_parent_preflight_log"
            printf 'RESUMED_ALLOWLIST=%s\n' "$eiksrvs_binary" \
                >>"$incremental_parent_preflight_log"
        elif [ "$incremental_eiksrv_resume" = 1 ]; then
            grep -Fv "  $eiksrv_binary" \
                "$incremental_parent_release_manifest" \
                >"$work/incremental-parent-release-resume-check.sha256"
            sha256sum -c "$work/incremental-parent-release-resume-check.sha256" \
                >"$incremental_parent_preflight_log"
            printf 'RESUMED_ALLOWLIST=%s\n' "$eiksrv_binary" \
                >>"$incremental_parent_preflight_log"
        elif [ "$incremental_eiksrvui_resume" = 1 ]; then
            grep -Fv "  $eiksrvui_binary" \
                "$incremental_parent_release_manifest" \
                >"$work/incremental-parent-release-resume-check.sha256"
            sha256sum -c "$work/incremental-parent-release-resume-check.sha256" \
                >"$incremental_parent_preflight_log"
            printf 'RESUMED_ALLOWLIST=%s\n' "$eiksrvui_binary" \
                >>"$incremental_parent_preflight_log"
        elif [ "$incremental_aknskinsrv_resume" = 1 ]; then
            grep -Fv "  $aknskinsrv_binary" \
                "$incremental_parent_release_manifest" \
                >"$work/incremental-parent-release-resume-check.sha256"
            sha256sum -c "$work/incremental-parent-release-resume-check.sha256" \
                >"$incremental_parent_preflight_log"
            printf 'RESUMED_ALLOWLIST=%s\n' "$aknskinsrv_binary" \
                >>"$incremental_parent_preflight_log"
        elif [ "$incremental_eiksrvc_resume" = 1 ]; then
            grep -Fv "  $eiksrvc_binary" \
                "$incremental_parent_release_manifest" \
                >"$work/incremental-parent-release-resume-check.sha256"
            sha256sum -c "$work/incremental-parent-release-resume-check.sha256" \
                >"$incremental_parent_preflight_log"
            printf 'RESUMED_ALLOWLIST=%s\n' "$eiksrvc_binary" \
                >>"$incremental_parent_preflight_log"
        else
            sha256sum -c "$incremental_parent_release_manifest" \
                >"$incremental_parent_preflight_log"
        fi
        cp "$incremental_parent_release_manifest" "$incremental_guard_manifest"
    fi
    for changed_binary in $incremental_changed_binaries; do
        grep -Fq "  $changed_binary" "$incremental_parent_release_manifest" || {
            echo "ERROR: changed binary is not in parent evidence: $changed_binary" >&2
            exit 1
        }
    done
    incremental_parent_binary_count=$(wc -l <"$incremental_parent_release_manifest")
    echo "HTCLEO_INCREMENTAL_PARENT_OK parent=$incremental_parent binaries=$incremental_parent_binary_count"
fi

if [ "$preflight_only" = 1 ]; then
    echo "HTCLEO_BUILD_PREFLIGHT_ONLY_OK mode=$build_mode"
    exit 0
fi

rm -f "$canonical_image" "$canonical_map"

# The PDK SSM server enters its permanent active-scheduler loop without
# completing the process rendezvous that ESTART waits on.  Apply the durable
# source repair once, then rebuild just sysstatemgr.exe for the full-ROM tree.
test -s "$ssm_patch"
test -s "$ssm_log_transform"
test -s "$ssm_cle_log_transform"
test -s "$ssm_custom_transform"
test -s "$ssm_custom_load_split_transform"
test -s "$ssm_custom_init_trace_transform"
test -s "$ssm_custom_source"
test -s "$ssm_custom_header"
test -s "$ssm_custom_mmp"
test -s "$ssm_custom_bldinf"
test -s "$ssm_custom_def"
test -s "$apparc_transform"
test -s "$apparc_sync_scan_transform"
test -s "$apparc_restart_recovery_transform"
test -s "$apparc_restart_recognizer_transform"
test -s "$apparc_bldinf"
test -s "$apparc_aplist_source"
test -s "$apparc_apsstart_source"
test -s "$apparc_apsserv_source"
test -s "$apparc_apsses_source"
test -s "$stem_state_transform"
test -s "$stem_startup_mode_transform"
test -s "$stem_splash_transform"
test -s "$stem_resource_bldinf"
test -s "$stem_critical_cmdlist_source"
test -s "$stem_noncritical_cmdlist_source"
test -s "$stem_cone_transform"
test -s "$stem_cone_event_transform"
test -s "$stem_cone_ready_ao_transform"
test -s "$stem_cone_homescreen_ao_transform"
test -s "$stem_cone_homescreen_foreground_transform"
test -s "$stem_cone_source"
test -s "$stem_cone_main_source"
test -s "$stem_cone_appui_source"
test -s "$stem_cone_envextra_source"
test -s "$stem_cone_bldinf"
test -s "$stem_cone_parent_migration"
test -s "$liw_monitor_transform"
test -s "$liw_monitor_source"
test -s "$liw_bldinf"
test -s "$liw_parent_migration"
test -s "$liw_stock_669"
test -s "$matrixmenu_transform"
test -s "$matrixmenu_log_capacity_transform"
test -s "$matrixmenu_log_capacity_1m_transform"
test -s "$matrixmenu_scheduler_kick_transform"
test -s "$matrixmenu_initial_statuslayout_transform"
test -s "$matrixmenu_dummy_grid_transform"
test -s "$matrixmenu_dummy_container_transform"
test -s "$matrixmenu_hnengine_transform"
test -s "$matrixmenu_postinit_transform"
test -s "$matrixmenu_late_haze_transform"
test -s "$matrixmenu_haze_notify_transform"
test -s "$matrixmenu_first_container_transform"
test -s "$matrixmenu_full_grid_transform"
test -s "$matrixmenu_first_frame_finish_transform"
test -s "$matrixmenu_precontainer_suite_init_transform"
test -s "$matrixmenu_runtime_event_transform"
test -s "$matrixmenu_redundant_focus_transform"
test -s "$matrixmenu_focus_quarantine_transform"
test -s "$matrixmenu_focus_restore_transform"
test -s "$matrixmenu_stale_focus_transform"
test -s "$matrixmenu_shell_transition_transform"
test -s "$matrixmenu_noncellular_return_transform"
test -s "$matrixmenu_home_ordinal_transform"
test -s "$matrixmenu_home_async_transform"
test -s "$matrixmenu_home_owning_transform"
test -s "$matrixmenu_home_owner_binding_transform"
test -s "$matrixmenu_native_activation_transform"
test -s "$matrixmenu_scheduler_retirement_transform"
test -s "$matrixmenu_visual_skin_transform"
test -s "$matrixmenu_exception_type_transform"
test -s "$matrixmenu_abort_stack_transform"
test -s "$matrixmenu_terminate_retirement_transform"
test -s "$matrixmenu_caller_stack_transform"
test -s "$matrixmenu_startup_foreground_transform"
test -s "$matrixmenu_foreground_ordinal_transform"
test -s "$matrixmenu_redundant_ordinal_transform"
test -s "$matrixmenu_final_cba_transform"
test -s "$ui_frame_stage_correlation_transform"
test -s "$matrixmenu_stack_transform"
test -s "$mmwidgets_transform"
test -s "$mmwidgets_grid_handle_transform"
test -s "$mmwidgets_haze_background_transform"
test -s "$mmwidgets_cpu_haze_transform"
test -s "$mmwidgets_full_wallpaper_transform"
test -s "$mmwidgets_touch_diagnostic_transform"
test -s "$mmwidgets_deferred_ao_transform"
test -s "$mmwidgets_post_bounds_transform"
test -s "$mmwidgets_bldinf"
test -s "$mmwidgets_mmp"
test -s "$mmwidgets_widget_source"
test -s "$mmwidgets_post_source"
test -s "$mmwidgets_drawer_source"
test -s "$mmwidgets_grid_source"
test -s "$mmwidgets_grid_control_source"
test -s "$hnengine_transform"
test -s "$hnengine_initialize_transform"
test -s "$hnengine_bldinf"
test -s "$hnengine_mmp"
test -s "$hnengine_source"
test -s "$hnmetadata_transform"
test -s "$hnmetadata_showfolder_transform"
test -s "$hnmetadata_evaluation_transform"
test -s "$hnmetadata_capacity_transform"
test -s "$hnmetadata_notify_transform"
test -s "$hnmetadata_initial_coalesce_transform"
test -s "$hnmetadata_capacity_1m_transform"
test -s "$hnmetadata_retire_redundant_refresh_transform"
test -s "$hnmetadata_bldinf"
test -s "$hnmetadata_mmp"
test -s "$hnmetadata_source"
test -s "$hnmetadata_suite_source"
test -s "$hnmetadata_query_source"
test -s "$hnmetadata_query_header"
test -s "$hnmetadata_notify_source"
test -s "$hnmetadata_notify_request_source"
test -s "$hnmetadata_notify_request_header"
test -s "$mcsmenu_transform"
test -s "$mcsmenu_apparc_transform"
test -s "$mcsmenu_engine_transform"
test -s "$mcsmenu_ram_fallback_transform"
test -s "$mcsmenu_first_change_transform"
test -s "$mcsmenu_context_transform"
test -s "$mcsmenu_startup_no_io_transform"
test -s "$mcsmenu_pid_ready_transform"
test -s "$mcsmenu_persistent_server_transform"
test -s "$mcsmenu_scanner_optional_transform"
test -s "$mcsmenu_apparc_retry_transform"
test -s "$mcsmenu_apparc_returned_retry_transform"
test -s "$mcsmenu_apparc_restart_transform"
test -s "$mcsmenu_hn_ready_transform"
test -s "$hn_ready_request_guard_transform"
test -s "$mcsmenu_hn_ready_signal_transform"
test -s "$mcsmenu_hn_commit_requery_transform"
test -s "$mcsmenu_getlist_count_transform"
test -s "$mcsmenu_getlist_session_transform"
test -s "$mcsmenu_getlist_session_v2_transform"
test -s "$mcsmenu_getlist_atomic_transform"
test -s "$hn_getlist_synchronous_transform"
test -s "$hn_sync_completion_transform"
test -s "$hn_sync_direct_safe_transform"
test -s "$hn_getlist_provider_sync_pump_transform"
test -s "$hn_results_consumption_transform"
test -s "$mcsservice_transform"
test -s "$mcs_notification_transform"
test -s "$mcsprovider_bldinf"
test -s "$mcsservice_bldinf"
test -s "$mcsservice_mmp"
test -s "$mcsservice_source"
test -s "$mcsmenu_getlist_source"
test -s "$mcsmenu_session_source"
test -s "$mcsmenu_session_header"
test -s "$hnmetadata_item_source"
test -s "$mcsmenu_bldinf"
test -s "$mcsmenu_mmp"
test -s "$mcsmenu_core_bldinf"
test -s "$mcsmenu_core_mmp"
test -s "$mcsmenu_engine_source"
test -s "$mcsmenu_menueng_source"
test -s "$mcsmenu_menueng_header"
test -s "$mcsmenu_utils_source"
test -s "$mcsmenu_utils_header"
test -s "$mcsmenu_scanner_source"
test -s "$matrixmenu_bldinf"
test -s "$matrixmenu_config_file"
grep -Fq '<var name="matrixmenu_permissive">' "$matrixmenu_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$matrixmenu_config_file"
test -s "$matrixmenu_mmp"
test -s "$matrixmenu_entry_source"
test -s "$matrixmenu_app_source"
test -s "$matrixmenu_document_source"
test -s "$matrixmenu_appui_source"
test -s "$homescreen_log_transform"
test -s "$homescreen_launch_transform"
test -s "$homescreen_late_launch_transform"
test -s "$homescreen_post_launch_transform"
test -s "$homescreen_controller_transform"
test -s "$homescreen_restart_transform"
test -s "$homescreen_exit_category_transform"
test -s "$homescreen_closure_audit"
test -s "$homescreen_bldinf"
test -s "$homescreen_main_source"
test -s "$homescreen_aifw_source"
test -s "$homescreen_controller_source"
test -s "$homescreen_idle_source"
test -s "$homescreen_launch_source"
test -s "$homescreen_aifw_parent_migration"
test -s "$homescreen_idle_parent_migration"
test -s "$homescreen_launch_parent_migration"
test -s "$homescreen_parent_migration"
test -s "$homescreen_aifw_stock_670"
test -s "$homescreen_idle_stock_670"
test -s "$homescreen_launch_stock_670"
test -s "$homescreen_stock_670"
test -s "$ai3xml_trace_transform"
test -s "$ai3xml_onlineoffline_transform"
test -s "$ai3xml_bldinf"
test -s "$ai3xml_mmp"
test -s "$ai3xml_controller_source"
test -s "$ai3xml_application_source"
test -s "$ai3xml_document_source"
test -s "$ai3xml_appui_source"
test -s "$ai3xml_contentpublisher_source"
test -s "$ai3xml_parent_migration"
test -s "$ai3xml_stock_675"
test -s "$xn3layout_trace_transform"
test -s "$xn3layout_impl_trace_transform"
test -s "$xn3layout_loadui_trace_transform"
test -s "$xn3layout_view_load_trace_transform"
test -s "$xn3layout_transient_view_transform"
test -s "$xn3layout_nonvisual_factory_transform"
test -s "$xn3layout_zero_factory_general_transform"
test -s "$xn3layout_metadata_factory_transform"
test -s "$xn3layout_menu_group_transform"
test -s "$homescreen_high_frequency_log_retirement_transform"
test -s "$xn_hd2_client_geometry_transform"
test -s "$xn_client_window_commit_transform"
test -s "$home_msk_center_transform"
test -s "$home_native_focus_transform"
test -s "$home_liveness_transform"
test -s "$wserv_shell_handoff_transform"
test -s "$wserv_nonblocking_log_transform"
test -s "$wserv_worker_retirement_transform"
test -s "$shell_pointer_log_retirement_transform"
test -s "$ui_742_control_pin"
test -s "$ui_743_xn_focus_promoter"
test -s "$matrixmenu_focus_touch_rearm_transform"
test -s "$hspsprovider_log_retirement_transform"
test -s "$wserv_low_rate_touch_transform"
test -s "$xn3layout_bldinf"
test -s "$xn3layout_mmp"
test -s "$xn3layout_source"
test -s "$xn3layout_impl_source"
test -s "$xn3layout_viewmanager_source"
test -s "$xn3layout_rootdata_source"
test -s "$xn3layout_composer_source"
test -s "$xn3layout_odtparser_source"
test -s "$xn3layout_viewdata_source"
test -s "$xn3layout_frozen_def"
test -s "$xn3layout_parent_migration"
test -s "$xn3layout_stock_680"
test -s "$xn3layout_config_file"
test -x "$xn3layout_cc_wrapper"
test -s "$xn3layout_abi_promoter"
test -s "$xn3layout_abi_audit"
test "$(sha256sum "$xn3utils_stock_binary" | awk '{print $1}')" = \
    "$xn3utils_stock_sha256"
test "$(sha256sum "$xn3layout_stock_680" | awk '{print $1}')" = \
    90bb8a35701181b316e5180e9d34ea75eb4802b88a3c406fc6531abdf965a7a6
test -s "$hspluginsettings_source"
test -s "$hspluginsettings_mmp"
test -s "$hspluginsettings_frozen_def"
test -s "$hspluginsettings_transform"
test -s "$hspluginsettings_abi_audit"
test -s "$hspluginsettings_bldinf"
test -s "$hspluginsettings_config_file"
grep -Fq '<var name="hspluginsettings_permissive">' \
    "$hspluginsettings_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$hspluginsettings_config_file"
test -s "$hspluginsettings_parent_migration"
test -s "$hspluginsettings_stock_689"
test "$(sha256sum "$hspluginsettings_stock_689" | awk '{print $1}')" = \
    15f32da0e07ee9edf4d573cd131e2afa6f05bf7b1a9645d77650decd32bb4633
test -s "$hspsthemeserver_source"
test -s "$hspsthemeserver_family_source"
test -s "$hspsthemeserver_rominstaller_source"
test -s "$hspsthemeserver_installation_source"
test -s "$hspsthemeserver_mmp"
test -s "$hspsthemeserver_transform"
test -s "$hspsthemeserver_skeleton_trace_transform"
test -s "$hspsthemeserver_root_self_heal_transform"
test -s "$hspsthemeserver_bldinf"
test -s "$hspsthemeserver_config_file"
grep -Fq '<var name="hspsthemeserver_permissive">' \
    "$hspsthemeserver_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$hspsthemeserver_config_file"
test -s "$hspsthemeserver_parent_migration"
test -s "$hspsthemeserver_stock_690"
test "$(sha256sum "$hspsthemeserver_stock_690" | awk '{print $1}')" = \
    bd7e64d96662e99445f9ee944764ef866d50234858f21dc0c30f085f8cb0c855
test -s "$hsps_definition_source"
test -s "$hsps_definition_proxy_source"
test -s "$hsps_definition_mmp"
test -s "$hsps_definition_bldinf"
test -s "$hsps_definition_transform"
test -s "$hsps_definition_ecom_recovery_transform"
test -s "$hsps_definition_libxml_closure_transform"
test -s "$hsps_definition_parent_migration"
test -s "$hsps_definition_stock_697"
test "$(sha256sum "$hsps_definition_stock_697" | awk '{print $1}')" = \
    f89f909dff8120d9292306a321950dd61d369a1940fe9703b6c7f732710bb2d2
test -s "$libxml_sax_binary"
test -s "$libxml_sax_resource"
test -s "$libxml_sax_parent_migration"
test "$(sha256sum "$libxml_sax_binary" | awk '{print $1}')" = \
    96430037c5be707c411fab36799fa4be626b6104bce2edd931cb9b9390b2d6fd
test "$(sha256sum "$libxml_sax_resource" | awk '{print $1}')" = \
    68d5aaa0623a1283292f57329ef9f0ea5beb7ede313af89325893f56358d9611
test -s "$hspsprovider_source"
test -s "$hspsprovider_mmp"
test -s "$hspsprovider_transform"
test -s "$hspsprovider_bldinf"
test -s "$hspsprovider_config_file"
grep -Fq '<var name="hspsprovider_permissive">' \
    "$hspsprovider_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$hspsprovider_config_file"
test -s "$hspsprovider_parent_migration"
test -s "$hspsprovider_stock_703"
test -s "$hspsprovider_stock_resource_703"
test "$(sha256sum "$hspsprovider_stock_703" | awk '{print $1}')" = \
    ffabd10822a7c5fa9a5edaca507db457478b9a510a9f411d2c086f9c052c95f0
test "$(sha256sum "$hspsprovider_stock_resource_703" | awk '{print $1}')" = \
    55bd6b71b8af2af0789db905b45b6389f5ad67b6812efb1271eec51be9989633
test -s "$wserv_log_transform"
test -s "$wserv_plugin_transform"
test -s "$wserv_screen_transform"
test -s "$wserv_client_window_transform"
test -s "$wserv_matrixmenu_command_buffer_transform"
test -s "$wserv_type2a_pointer_transform"
test -s "$wserv_type2a_raw_trace_transform"
test -s "$wserv_event_hook_counter_transform"
test -s "$wserv_runl_trace_bound_transform"
test -s "$wserv_absrect_pointer_fallback_transform"
test -s "$wserv_published_grid_fallback_transform"
test -s "$wserv_published_grid_capture_transform"
test -s "$matrixmenu_teardown_attribution_transform"
test -s "$wserv_matrixmenu_panic_category_transform"
test -s "$wserv_touch_only_log_transform"
test -s "$wserv_build_bldinf"
test -s "$display_log_transform"
test -s "$display_cpu_blit_transform"
test -s "$display_flicker_cpu_blit_transform"
test -s "$display_frame_signature_transform"
test -s "$display_region_blit_transform"
test -s "$display_scheduler_blank_guard_transform"
test -s "$display_high_frequency_log_retirement_transform"
test -s "$display_bldinf"
test -s "$wfc_log_transform"
test -s "$wfc_bldinf"
test -s "$nvg_log_transform"
test -s "$nvg_bldinf"
test -s "$ecom_log_transform"
test -s "$ecom_load_split_transform"
test -s "$ecom_init_entrypoint_transform"
test -s "$ecom_featmgr_list_transform"
test -s "$ecom_server_transform"
test -s "$ecom_featureinfo_empty_transform"
test -s "$ecom_matrixmenu_retry_transform"
test -s "$ecom_matrixmenu_list_retry_transform"
test -s "$ecom_homescreen_list_retry_transform"
test -s "$ecom_homescreen_action_list_retry_transform"
test -s "$ecom_homescreen_nonvisual_list_retry_transform"
test -s "$ecom_homescreen_menubar_list_retry_transform"
test -s "$ecom_homescreen_rendering_list_retry_transform"
test -s "$ecom_homescreen_retry_transform"
test -s "$ecom_homescreen_server_trace_transform"
test -s "$ecom_hsps_definition_resolve_transform"
test -s "$ecom_hsps_persistent_trace_transform"
test -s "$ecom_hsps_response_trace_transform"
test -s "$ecom_hsps_client_load_trace_transform"
test -s "$ecom_server_logger_header"
test -s "$ecom_spi_base"
test -s "$ecom_spi_tool"
test -s "$ecom_spi_perl_compat"
test -s "$ecom_spi_manifest"
test -s "$ecom_spi_audit"
test -s "$ptiengine_transform"
test -s "$ptiengine_bldinf"
test -s "$ptiengine_source"
test -s "$ptiengine_mmp"
test -s "$ptiengine_frozen_def"
test -s "$ptiengine_parent_migration"
test -s "$ecom_build_bldinf"
test -s "$ecom_server_build_bldinf"
test -s "$stem_backend_transform"
test -s "$stem_backend_timezone_transform"
test -s "$stem_backend_bldinf"
test -s "$stem_backend_mmp"
test -s "$stem_backend_source"
test -s "$stem_backend_header"
test -s "$stem_backend_frozen_def"
test -s "$hitchcock_transform"
test -s "$hitchcock_import_dso_tool"
test -s "$hitchcock_bldinf"
test -s "$hitchcock_mmp"
test -s "$hitchcock_frozen_def"
test -s "$hitchcock_cc_wrapper"
test -s "$hitchcock_abi_promoter"
chmod +x "$hitchcock_cc_wrapper" "$hitchcock_abi_promoter"
test -s "$wserv_main"
test -s "$wserv_plugin_manager"
test -s "$wserv_screen"
test -s "$wserv_screen_redraw"
test -s "$wserv_render_stage_manager"
test -s "$wserv_mmp"
test -s "$display_plugin"
test -s "$display_factory"
test -s "$display_stage"
test -s "$display_openwfc"
test -s "$display_target"
test -s "$display_policy"
test -s "$display_fb_factory"
test -s "$display_fb_stage"
test -s "$display_mmp"
test -s "$wfc_context"
test -s "$wfc_display_context"
test -s "$wfc_screen"
test -s "$wfc_stream"
test -s "$wfc_mmp"
test -s "$wfc_image_header"
test -s "$wfc_display_header"
test -s "$wfc_stream_header"
test -s "$ssm_main"
test -s "$ssm_cle_executor"
test -s "$ssm_cle_bldinf"
test -s "$ssm_bldinf"
test -s "$apparc_launch_source"
test -s "$apparc_launch_mmp"
test -s "$apparc_launch_transform"
test -s "$apparc_launch_held_process_transform"
test -s "$apparc_launch_property_ready_transform"
test -s "$apparc_launch_property_poll_transform"
test -s "$apparc_launch_fire_forget_transform"
test -s "$apparc_launch_matrixmenu_connect_transform"
test -s "$apparc_launch_matrixmenu_no_timer_transform"
test -s "$apparc_launch_matrixmenu_bounded_retry_transform"
test -s "$apparc_launch_matrixmenu_reuse_child_transform"
test -s "$apparc_launch_matrixmenu_ready_wait_transform"
test -s "$apparc_launch_matrixmenu_discover_server_transform"
test -s "$apparc_launch_matrixmenu_single_attempt_transform"
test -s "$apparc_launch_bldinf"
test -s "$akncapserver_source"
test -s "$akncapserver_ipc_source"
test -s "$akncapserver_mmp"
test -s "$akncapserver_transform"
test -s "$akncapserver_eikcore_bridge"
test -s "$akncapserver_rendezvous_ready_transform"
test -s "$akncapserver_property_ready_transform"
test -s "$akncapserver_ofn_bypass_transform"
test -s "$akncapserver_postcritical_filelog_transform"
test -s "$akncapserver_postcritical_property_transform"
test -s "$akncapserver_e100_pre_retirement_transform"
test -s "$akncapserver_criticality_bypass_transform"
test -s "$akncapserver_nonleo_startup_transform"
test -s "$akncapserver_registration_lifetime_transform"
test -s "$akncapserver_bldinf"
test -s "$eikcore_source"
test -s "$eikstart_source"
test -s "$eikappui_source"
test -s "$eikcore_compat_source"
test -s "$eikcore_mmp"
test -s "$eikcore_frozen_def"
test -s "$eikcore_transform"
test -s "$eikcore_postprocess_gap_transform"
test -s "$eikcore_akncap_priority_defer_transform"
test -s "$eikcore_constructl_transform"
test -s "$eikcore_postappui_transform"
test -s "$eikcore_matrixmenu_taskname_transform"
test -s "$eikcore_matrixmenu_appready_transform"
test -s "$eikcore_matrixmenu_startup_view_ao_transform"
test -s "$eikcore_matrixmenu_startup_view_priority_transform"
test -s "$eikcore_matrixmenu_direct_startup_view_transform"
test -s "$eikcore_matrixmenu_startup_view_retire_transform"
test -s "$eikcore_matrixmenu_view_init_retire_transform"
test -s "$eikcore_homescreen_constructapp_trace_transform"
test -s "$eikstart_homescreen_trace_transform"
test -s "$eikappui_baseconstruct_transform"
test -s "$eikappui_matrixmenu_final_screen_transform"
test -s "$eikappui_homescreen_baseconstruct_trace_transform"
test -s "$eikappui_homescreen_foreground_trace_transform"
test -s "$eikcore_abi_audit"
test -s "$eikcore_bldinf"
test -s "$eikcore_stock_442"
test "$(sha256sum "$eikcore_stock_442" | awk '{print $1}')" = \
    6196051ec6d1f029db9cadb5192903a1cfe4447f1686e8fea89aaf1dc8669e34
test -s "$eikcoctl_source"
test -s "$eikcoctl_statuspane_source"
test -s "$eikcoctl_statusmodel_source"
test -s "$eikcoctl_cba_source"
test -s "$eikcoctl_btgpc_source"
test -s "$eikcoctl_physics_source"
test -s "$eikcoctl_list_item_source"
test -s "$eikcoctl_mmp"
test -s "$eikcoctl_frozen_def"
test -s "$eikcoctl_abi_audit"
test -s "$eikcoctl_touch_header"
test -s "$eikcoctl_edwin_header"
test -s "$eikcoctl_transform"
test -s "$eikcoctl_statuspane_transform"
test -s "$eikcoctl_statuspane_scale_transform"
test -s "$eikcoctl_cba_inner_redraw_transform"
test -s "$eikcoctl_cba_wrapper_redraw_transform"
test -s "$eikcoctl_statuslayout_transform"
test -s "$eikcoctl_statustree_layout_transform"
test -s "$eikcoctl_combined_visibility_transform"
test -s "$eikcoctl_matrixmenu_fade_transform"
test -s "$eikcoctl_matrixmenu_clientrect_transform"
test -s "$eikcoctl_homescreen_geometry_transform"
test -s "$eikcoctl_bldinf"
test -s "$eikcoctl_config_file"
grep -Fq '<var name="eikcoctl_permissive">' "$eikcoctl_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$eikcoctl_config_file"
test -s "$eikcoctl_parent_migration"
test -s "$eikcoctl_stock_515"
test "$(sha256sum "$eikcoctl_stock_515" | awk '{print $1}')" = \
    b931311e960f7353254440eab5a0b4bde96af7dd5b4a4bf6dfca401042ded803
test -s "$eiksrvc_source"
test -s "$eiksrvc_mmp"
test -s "$eiksrvc_frozen_def"
test -s "$eiksrvc_transform"
test -s "$eiksrvc_timeout_transform"
test -s "$eiksrvc_cancel_transform"
test -s "$eiksrvc_ready_retry_transform"
test -s "$eiksrvc_compact_poll_transform"
test -s "$eiksrvc_ready_wait_transform"
test -s "$eiksrvc_bldinf"
test -s "$eiksrvc_parent_migration"
test -s "$eiksrvc_compat_parent"
test -s "$eiksrvc_cancel_parent"
test -s "$eiksrvc_ready_retry_parent"
test -s "$eiksrvc_compact_poll_parent"
test -s "$eiksrvs_source"
test -s "$eiksrvs_mmp"
test -s "$eiksrvs_transform"
test -s "$eiksrvs_bldinf"
test -s "$eiksrvs_parent_migration"
test -s "$eiksrv_source"
test -s "$eiksrv_mmp"
test -s "$eiksrv_transform"
test -s "$eiksrv_bldinf"
test -s "$eiksrv_parent_migration"
test -s "$eiksrvui_source"
test -s "$eiksrvui_mmp"
test -s "$eiksrvui_transform"
test -s "$eiksrvui_initialize_transform"
test -s "$eiksrvui_c32_failopen_transform"
test -s "$eiksrvui_notify_alert_failopen_transform"
test -s "$eiksrvui_construct_entry_split_transform"
test -s "$eiksrvui_system_attribute_failopen_transform"
test -s "$aknappui_baseconstruct_transform"
test -s "$aknappui_homescreen_baseconstruct_trace_transform"
test -s "$aknappui_homescreen_postcoe_trace_transform"
test -s "$aknappui_homescreen_focus_keyblock_transform"
test -s "$avkon_focus_touch_rearm_transform"
test -s "$clock_watch_transform"
test -s "$aknappui_homescreen_focus_log_route_transform"
test -s "$aknappui_homescreen_foreground_trace_transform"
test -s "$aknsgc_homescreen_system_fade_transform"
test -s "$aknappui_matrixmenu_ui_first_transform"
test -s "$aknappui_postcoe_layout_transform"
test -s "$aknappui_matrixmenu_postcoe_fixed_transform"
test -s "$aknsgc_matrixmenu_setparams_defer_transform"
test -s "$aknsgc_homescreen_setparams_defer_transform"
test -s "$aknenv_matrixmenu_transform"
test -s "$aknenv_matrixmenu_cdl_reconnect_transform"
test -s "$aknenv_homescreen_trace_cdl_reconnect_transform"
test -s "$aknsgc_matrixmenu_transform"
test -s "$aknsgc_matrixmenu_akncap_failopen_transform"
test -s "$aknsgc_homescreen_trace_akncap_failopen_transform"
test -s "$stem_avkon_source"
test -s "$stem_avkon_viewappui_source"
test -s "$stem_avkon_aknenv_source"
test -s "$stem_avkon_sgc_source"
test -s "$stem_avkon_lists_source"
test -s "$stem_avkon_grid_source"
test -s "$akngrid_matrixmenu_background_transform"
test -s "$stem_avkon_mmp"
test -s "$stem_avkon_bldinf"
test -s "$stem_avkon_config_file"
test -s "$stem_avkon_cc_wrapper"
test -s "$stem_avkon_abi_promoter"
test -s "$stem_avkon_abi_audit"
chmod +x "$stem_avkon_cc_wrapper" "$stem_avkon_abi_promoter"
test -s "$stem_avkon_parent_migration"
test -s "$eiksrvui_bldinf"
test -s "$eiksrvui_parent_migration"
test -s "$eiksrvui_initialize_parent"
test -s "$c32root_source"
test -s "$c32start_source"
test -s "$c32root_mmp"
test -s "$c32_transform"
test -s "$c32_bldinf"
test -s "$c32root_parent"
test -s "$c32start_parent"
test -s "$c32root_stock_468"
test -s "$c32start_stock_468"
test -s "$aknskinsrv_source"
test -s "$aknskinsrv_client_source"
test -s "$aknskinsrv_mmp"
test -s "$aknskinsrv_transform"
test -s "$aknskinsrv_bldinf"
test -s "$aknskinsrv_parent_migration"
test -s "$featmgr_source"
test -s "$featmgr_tls_source"
test -s "$featmgr_client_source"
test -s "$featmgr_mmp"
test -s "$featmgr_frozen_def"
test -s "$featmgr_transform"
test -s "$featmgr_bldinf"
test -s "$featmgr_stock_444"
test "$(sha256sum "$featmgr_stock_444" | awk '{print $1}')" = \
    005ed0e4bd80bc87b25fac2d9f71d09a44326203bdf9bd098efe73a8103ac640
test -s "$featmgrserver_source"
test -s "$featmgrserver_startup_source"
test -s "$featmgrserver_mmp"
test -s "$featmgrserver_transform"
test -s "$featmgrserver_loadplugins_transform"
test -s "$featmgrserver_zero_plugin_transform"
test -s "$featmgrserver_stock_445"
test "$(sha256sum "$featmgrserver_stock_445" | awk '{print $1}')" = \
    58fa528a9cc298c8407ff00b2a16a9f5506a649931c9673cccf98aeacdd948f0
test -s "$akn_custom_source"
test -s "$akn_custom_mmp"
test -s "$akn_custom_bldinf"
rendezvous_count=$(grep -c 'RProcess::Rendezvous(KErrNone)' "$ssm_main" || true)
if [ "$rendezvous_count" -eq 0 ]; then
    patch -d "$full_epocroot" -p1 <"$ssm_patch"
elif [ "$rendezvous_count" -ne 1 ]; then
    echo "ERROR: duplicate sysstatemgr rendezvous patch state" >&2
    exit 1
fi
test "$(grep -c 'RProcess::Rendezvous(KErrNone)' "$ssm_main")" -eq 1
python3 "$ssm_log_transform" "$full_epocroot"
python3 "$ssm_cle_log_transform" "$full_epocroot"
python3 "$ssm_custom_transform" "$full_epocroot"
python3 "$ssm_custom_load_split_transform" "$full_epocroot"
python3 "$ssm_custom_init_trace_transform" "$full_epocroot"
python3 "$apparc_transform" "$full_epocroot"
python3 "$apparc_sync_scan_transform" "$full_epocroot"
python3 "$apparc_restart_recovery_transform" "$full_epocroot"
python3 "$apparc_restart_recognizer_transform" "$full_epocroot"
python3 "$apparc_launch_transform" "$full_epocroot"
python3 "$apparc_launch_held_process_transform" "$full_epocroot"
python3 "$apparc_launch_property_ready_transform" "$full_epocroot"
python3 "$apparc_launch_property_poll_transform" "$full_epocroot"
python3 "$apparc_launch_fire_forget_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_connect_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_no_timer_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_bounded_retry_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_reuse_child_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_ready_wait_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_discover_server_transform" "$full_epocroot"
python3 "$apparc_launch_matrixmenu_single_attempt_transform" "$full_epocroot"
python3 "$akncapserver_transform" "$full_epocroot"
python3 "$akncapserver_eikcore_bridge" "$full_epocroot"
python3 "$akncapserver_rendezvous_ready_transform" "$full_epocroot"
python3 "$akncapserver_property_ready_transform" "$full_epocroot"
python3 "$akncapserver_ofn_bypass_transform" "$full_epocroot"
python3 "$akncapserver_postcritical_filelog_transform" "$full_epocroot"
python3 "$akncapserver_postcritical_property_transform" "$full_epocroot"
python3 "$akncapserver_e100_pre_retirement_transform" "$full_epocroot"
python3 "$akncapserver_criticality_bypass_transform" "$full_epocroot"
python3 "$akncapserver_nonleo_startup_transform" "$full_epocroot"
python3 "$akncapserver_registration_lifetime_transform" "$full_epocroot"
python3 "$eiksrvc_transform" "$full_epocroot"
python3 "$eiksrvc_timeout_transform" "$full_epocroot"
python3 "$eiksrvc_cancel_transform" "$full_epocroot"
python3 "$eiksrvc_ready_retry_transform" "$full_epocroot"
python3 "$eiksrvc_compact_poll_transform" "$full_epocroot"
python3 "$eiksrvc_ready_wait_transform" "$full_epocroot"
python3 "$eiksrvs_transform" "$full_epocroot"
python3 "$eiksrv_transform" "$full_epocroot"
python3 "$eiksrvui_transform" "$full_epocroot"
python3 "$eiksrvui_initialize_transform" "$full_epocroot"
python3 "$eiksrvui_c32_failopen_transform" "$full_epocroot"
python3 "$eiksrvui_notify_alert_failopen_transform" "$full_epocroot"
python3 "$eiksrvui_construct_entry_split_transform" "$full_epocroot"
python3 "$eiksrvui_system_attribute_failopen_transform" "$full_epocroot"
python3 "$aknappui_baseconstruct_transform" "$full_epocroot"
python3 "$aknappui_matrixmenu_ui_first_transform" "$full_epocroot"
python3 "$aknappui_postcoe_layout_transform" "$full_epocroot"
python3 "$aknappui_matrixmenu_postcoe_fixed_transform" "$full_epocroot"
python3 "$aknappui_homescreen_baseconstruct_trace_transform" "$full_epocroot"
python3 "$aknappui_homescreen_postcoe_trace_transform" "$full_epocroot"
python3 "$aknsgc_matrixmenu_setparams_defer_transform" "$full_epocroot"
python3 "$aknsgc_homescreen_setparams_defer_transform" "$full_epocroot"
python3 "$aknenv_matrixmenu_transform" "$full_epocroot"
python3 "$aknenv_matrixmenu_cdl_reconnect_transform" "$full_epocroot"
python3 "$aknenv_homescreen_trace_cdl_reconnect_transform" "$full_epocroot"
python3 "$aknsgc_matrixmenu_transform" "$full_epocroot"
python3 "$aknsgc_matrixmenu_akncap_failopen_transform" "$full_epocroot"
python3 "$aknsgc_homescreen_trace_akncap_failopen_transform" "$full_epocroot"
python3 "$aknappui_homescreen_focus_keyblock_transform" "$full_epocroot"
python3 "$avkon_focus_touch_rearm_transform" "$full_epocroot"
python3 "$clock_watch_transform" "$full_epocroot"
python3 "$aknappui_homescreen_focus_log_route_transform" "$full_epocroot"
python3 "$aknappui_homescreen_foreground_trace_transform" "$full_epocroot"
python3 "$aknsgc_homescreen_system_fade_transform" "$full_epocroot"
python3 "$akngrid_matrixmenu_background_transform" "$full_epocroot"
python3 "$c32_transform" "$full_epocroot"
python3 "$aknskinsrv_transform" "$full_epocroot"
python3 "$eikcore_transform" "$full_epocroot"
python3 "$eikcore_postprocess_gap_transform" "$full_epocroot"
python3 "$eikcore_akncap_priority_defer_transform" "$full_epocroot"
python3 "$eikcore_constructl_transform" "$full_epocroot"
python3 "$eikcore_postappui_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_taskname_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_appready_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_startup_view_ao_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_startup_view_priority_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_direct_startup_view_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_startup_view_retire_transform" "$full_epocroot"
python3 "$eikcore_matrixmenu_view_init_retire_transform" "$full_epocroot"
python3 "$eikcore_homescreen_constructapp_trace_transform" "$full_epocroot"
python3 "$eikstart_homescreen_trace_transform" "$full_epocroot"
python3 "$eikappui_baseconstruct_transform" "$full_epocroot"
python3 "$eikappui_matrixmenu_final_screen_transform" "$full_epocroot"
python3 "$eikappui_homescreen_baseconstruct_trace_transform" "$full_epocroot"
python3 "$eikappui_homescreen_foreground_trace_transform" "$full_epocroot"
python3 "$eikcoctl_transform" "$full_epocroot"
python3 "$eikcoctl_statuspane_transform" "$full_epocroot"
python3 "$eikcoctl_statuspane_scale_transform" "$full_epocroot"
python3 "$eikcoctl_cba_inner_redraw_transform" "$full_epocroot"
python3 "$eikcoctl_cba_wrapper_redraw_transform" "$full_epocroot"
python3 "$eikcoctl_statuslayout_transform" "$full_epocroot"
python3 "$eikcoctl_statustree_layout_transform" "$full_epocroot"
python3 "$eikcoctl_combined_visibility_transform" "$full_epocroot"
python3 "$eikcoctl_matrixmenu_fade_transform" "$full_epocroot"
python3 "$eikcoctl_matrixmenu_clientrect_transform" "$full_epocroot"
python3 "$eikcoctl_homescreen_geometry_transform" "$full_epocroot"
python3 "$featmgr_transform" "$full_epocroot"
python3 "$featmgrserver_transform" "$full_epocroot"
python3 "$featmgrserver_loadplugins_transform" "$full_epocroot"
python3 "$featmgrserver_zero_plugin_transform" "$full_epocroot"
python3 "$stem_state_transform" "$full_epocroot"
python3 "$stem_startup_mode_transform" "$full_epocroot"
python3 "$stem_splash_transform" "$full_epocroot"
python3 "$homescreen_launch_transform" "$full_epocroot"
python3 "$homescreen_late_launch_transform" "$full_epocroot"
python3 "$homescreen_post_launch_transform" "$full_epocroot"
python3 "$stem_cone_transform" "$full_epocroot"
python3 "$stem_cone_event_transform" "$full_epocroot"
python3 "$stem_cone_ready_ao_transform" "$full_epocroot"
python3 "$stem_cone_homescreen_ao_transform" "$full_epocroot"
python3 "$stem_cone_homescreen_foreground_transform" "$full_epocroot"
python3 "$liw_monitor_transform" "$full_epocroot"
python3 "$matrixmenu_transform" "$full_epocroot"
python3 "$matrixmenu_log_capacity_transform" "$full_epocroot"
python3 "$matrixmenu_log_capacity_1m_transform" "$full_epocroot"
python3 "$matrixmenu_scheduler_kick_transform" "$full_epocroot"
python3 "$matrixmenu_initial_statuslayout_transform" "$full_epocroot"
python3 "$matrixmenu_dummy_grid_transform" "$full_epocroot"
python3 "$matrixmenu_dummy_container_transform" "$full_epocroot"
python3 "$matrixmenu_hnengine_transform" "$full_epocroot"
python3 "$matrixmenu_postinit_transform" "$full_epocroot"
python3 "$matrixmenu_late_haze_transform" "$full_epocroot"
python3 "$matrixmenu_haze_notify_transform" "$full_epocroot"
python3 "$matrixmenu_first_container_transform" "$full_epocroot"
python3 "$matrixmenu_full_grid_transform" "$full_epocroot"
python3 "$matrixmenu_ui_first_container_compat_transform" "$full_epocroot"
python3 "$matrixmenu_rom_presentation_transform" "$full_epocroot"
python3 "$matrixmenu_first_frame_finish_transform" "$full_epocroot"
python3 "$matrixmenu_precontainer_suite_init_transform" "$full_epocroot"
python3 "$matrixmenu_runtime_event_transform" "$full_epocroot"
python3 "$matrixmenu_redundant_focus_transform" "$full_epocroot"
python3 "$matrixmenu_focus_quarantine_transform" "$full_epocroot"
python3 "$matrixmenu_exception_type_transform" "$full_epocroot"
python3 "$matrixmenu_abort_stack_transform" "$full_epocroot"
python3 "$matrixmenu_terminate_retirement_transform" "$full_epocroot"
python3 "$matrixmenu_caller_stack_transform" "$full_epocroot"
python3 "$matrixmenu_startup_foreground_transform" "$full_epocroot"
python3 "$matrixmenu_foreground_ordinal_transform" "$full_epocroot"
python3 "$matrixmenu_redundant_ordinal_transform" "$full_epocroot"
python3 "$matrixmenu_final_cba_transform" "$full_epocroot"
python3 "$matrixmenu_focus_restore_transform" "$full_epocroot"
python3 "$matrixmenu_shell_transition_transform" "$full_epocroot"
python3 "$matrixmenu_noncellular_return_transform" "$full_epocroot"
python3 "$matrixmenu_home_ordinal_transform" "$full_epocroot"
python3 "$matrixmenu_home_async_transform" "$full_epocroot"
python3 "$matrixmenu_home_owning_transform" "$full_epocroot"
python3 "$matrixmenu_home_owner_binding_transform" "$full_epocroot"
python3 "$matrixmenu_stale_focus_transform" "$full_epocroot" --restore
python3 "$matrixmenu_native_activation_transform" "$full_epocroot"
python3 "$matrixmenu_stack_transform" "$full_epocroot"
python3 "$homescreen_log_transform" "$full_epocroot"
python3 "$homescreen_controller_transform" "$full_epocroot"
python3 "$homescreen_restart_transform" "$full_epocroot"
python3 "$homescreen_exit_category_transform" "$full_epocroot"
python3 "$ai3xml_trace_transform" "$full_epocroot"
python3 "$ai3xml_onlineoffline_transform" "$full_epocroot"
python3 "$xn3layout_trace_transform" "$full_epocroot"
python3 "$xn3layout_impl_trace_transform" "$full_epocroot"
python3 "$xn3layout_loadui_trace_transform" "$full_epocroot"
python3 "$xn3layout_view_load_trace_transform" "$full_epocroot"
python3 "$xn3layout_transient_view_transform" "$full_epocroot"
python3 "$xn3layout_nonvisual_factory_transform" "$full_epocroot"
python3 "$xn3layout_zero_factory_general_transform" "$full_epocroot"
python3 "$xn3layout_metadata_factory_transform" "$full_epocroot"
python3 "$xn3layout_menu_group_transform" "$full_epocroot"
python3 "$homescreen_high_frequency_log_retirement_transform" "$full_epocroot"
python3 "$xn_hd2_client_geometry_transform" "$full_epocroot"
python3 "$xn_client_window_commit_transform" "$full_epocroot"
python3 "$home_msk_center_transform" "$full_epocroot"
python3 "$home_native_focus_transform" "$full_epocroot"
python3 "$hspluginsettings_transform" "$full_epocroot"
python3 "$hspsthemeserver_transform" "$full_epocroot"
python3 "$hspsthemeserver_skeleton_trace_transform" "$full_epocroot"
python3 "$hspsthemeserver_root_self_heal_transform" "$full_epocroot"
python3 "$hsps_definition_transform" "$full_epocroot"
python3 "$hsps_definition_ecom_recovery_transform" "$full_epocroot"
python3 "$hsps_definition_libxml_closure_transform" "$full_epocroot"
python3 "$hspsprovider_transform" "$full_epocroot"
python3 "$hspsprovider_log_retirement_transform" "$full_epocroot"
python3 "$mmwidgets_transform" "$full_epocroot"
python3 "$mmwidgets_grid_handle_transform" "$full_epocroot"
python3 "$mmwidgets_haze_background_transform" "$full_epocroot"
python3 "$mmwidgets_cpu_haze_transform" "$full_epocroot"
python3 "$mmwidgets_full_wallpaper_transform" "$full_epocroot"
python3 "$mmwidgets_touch_diagnostic_transform" "$full_epocroot"
python3 "$mmwidgets_deferred_ao_transform" "$full_epocroot"
python3 "$mmwidgets_post_bounds_transform" "$full_epocroot"
python3 "$hnengine_transform" "$full_epocroot"
python3 "$hnengine_initialize_transform" "$full_epocroot"
python3 "$hnmetadata_transform" "$full_epocroot"
python3 "$hnmetadata_showfolder_transform" "$full_epocroot"
python3 "$hnmetadata_evaluation_transform" "$full_epocroot"
python3 "$hnmetadata_capacity_transform" "$full_epocroot"
python3 "$hnmetadata_notify_transform" "$full_epocroot"
python3 "$hnmetadata_initial_coalesce_transform" "$full_epocroot"
python3 "$hnmetadata_capacity_1m_transform" "$full_epocroot"
python3 "$mcsmenu_transform" "$full_epocroot"
python3 "$mcsmenu_apparc_transform" "$full_epocroot"
python3 "$mcsmenu_engine_transform" "$full_epocroot"
python3 "$mcsmenu_ram_fallback_transform" "$full_epocroot"
python3 "$mcsmenu_first_change_transform" "$full_epocroot"
python3 "$mcsmenu_context_transform" "$full_epocroot"
python3 "$mcsmenu_startup_no_io_transform" "$full_epocroot"
python3 "$mcsmenu_pid_ready_transform" "$full_epocroot"
python3 "$mcsmenu_persistent_server_transform" "$full_epocroot"
python3 "$mcsmenu_scanner_optional_transform" "$full_epocroot"
python3 "$mcsmenu_apparc_retry_transform" "$full_epocroot"
python3 "$mcsmenu_apparc_returned_retry_transform" "$full_epocroot"
python3 "$mcsmenu_apparc_restart_transform" "$full_epocroot"
python3 "$mcsmenu_hn_ready_transform" "$full_epocroot"
python3 "$hn_ready_request_guard_transform" "$full_epocroot"
python3 "$mcsmenu_hn_ready_signal_transform" "$full_epocroot"
python3 "$hnmetadata_retire_redundant_refresh_transform" "$full_epocroot"
python3 "$mcsmenu_hn_commit_requery_transform" "$full_epocroot"
python3 "$mcsmenu_getlist_count_transform" "$full_epocroot"
python3 "$mcsmenu_getlist_session_transform" "$full_epocroot"
python3 "$mcsmenu_getlist_session_v2_transform" "$full_epocroot"
python3 "$mcsmenu_getlist_atomic_transform" "$full_epocroot"
python3 "$hn_getlist_synchronous_transform" "$full_epocroot"
python3 "$hn_sync_completion_transform" "$full_epocroot"
python3 "$hn_sync_direct_safe_transform" "$full_epocroot"
python3 "$hn_getlist_provider_sync_pump_transform" "$full_epocroot"
python3 "$mcsservice_transform" "$full_epocroot"
python3 "$mcs_notification_transform" "$full_epocroot"
python3 "$hn_results_consumption_transform" "$full_epocroot"
python3 "$matrixmenu_focus_touch_rearm_transform" "$full_epocroot"
test -s "$matrixmenu_logger_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_DURABLE_LOG_V1' \
    "$matrixmenu_logger_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_LOG_CAPACITY_1M_V1' \
    "$matrixmenu_logger_source")" -eq 1
test "$(grep -c 'position <= ((16384 \* 64) - 64)' \
    "$matrixmenu_logger_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK_RETIRED_V1' \
    "$matrixmenu_entry_source")" -eq 1
! grep -q 'htcleoSchedulerEntryKick\|User::RequestComplete' "$matrixmenu_entry_source"
test "$(grep -c '0x4D4D1013u' "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_stage in 0313 0314 0315 0316 0317 0318
do
    test "$(grep -c "0x4D4D${matrixmenu_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_PRECONTAINER_SUITE_INIT_DEFER_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -ci '0x4D4D0334u' "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'if (isHiddenFromFS && !iCurrentContainer)' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_RUNTIME_EVENT_TRACE_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'type == EEventFocusGained && htcleoRuntimeState == 0x0Fu' \
    "$matrixmenu_appui_source")" -eq 1
matrixmenu_focus_fast_block=$(sed -n \
    '/HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4/,/if ( ( type == EEventFocusLost/p' \
    "$matrixmenu_appui_source")
for matrixmenu_focus_rearm_token in \
    'iHasFocus = ETrue;' 'EHalGroupPlatformSpecific2, 10' \
    'EHalGroupPlatformSpecific2, 11' '0x4D4D1268u'
do
    printf '%s\n' "$matrixmenu_focus_fast_block" | \
        grep -F -q "$matrixmenu_focus_rearm_token"
done
! printf '%s\n' "$matrixmenu_focus_fast_block" | \
    grep -q 'HandleFocusGainedL();\|DrawNow\|Finish()\|SetOrdinal\|RefreshIconsL();\|RefreshUiPanesL\|MakeVisible'
test "$(grep -c 'HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1' \
    "$matrixmenu_appui_source")" -eq 1
! grep -q 'HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1\|htcleoFocusQuarantine' \
    "$matrixmenu_appui_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_FOREGROUND_ORDINAL_NO_SYSTEM_EVENT_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL_SKIP_V1' \
    "$matrixmenu_appui_source")" -eq 1
! grep -q 'htcleoTask.BringToForeground()\|htcleoMenuTask.BringToForeground()' \
    "$matrixmenu_appui_source"
test "$(grep -c 'htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)' \
    "$matrixmenu_appui_source")" -eq 1
! grep -q 'htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)' \
    "$matrixmenu_appui_source"
test "$(grep -c 'me.BringToForeground()' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_focus_restore_stage in 1206 1207 1208 1209 120A 120B
do
    test "$(grep -ci "0x4D4D${matrixmenu_focus_restore_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
for matrixmenu_runtime_stage in \
    1200 1201 1202 120A 1210 1211 1220 1221 1230 1231 1240 1241 1290 1291
do
    test "$(grep -ci "0x4D4D${matrixmenu_runtime_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_HOMESCREEN_UID_BOOTSTRAP_V1' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_shell_stage in \
    1400 1401 1402 1410 1411 1412 141F \
    1420 1421 1422 1423 1424 1425 1426 1427 1428 1429 142A 142B 142C 142D 142E \
    1430 1431 1432 1433 1434 1435 1436 143F \
    1440 1441 1442 1443 1444 1445 1446 1447 1448 1449
do
    test "$(grep -ci "0x4D4D${matrixmenu_shell_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1' \
    "$matrixmenu_appui_source")" -eq 2
test "$(grep -c 'HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1' \
    "$matrixmenu_appui_header")" -eq 1
test "$(grep -c 'iHtcleoHomeHandoff->CallBack();' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'TInt CMmAppUi::HtcleoHomeHandoffTick' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_STALE_FOCUS_NO_REDRAW_V1' \
    "$matrixmenu_appui_source")" -eq 0
test "$(grep -c 'const TInt htcleoFocusFinish = htcleoFocusWs.Finish();' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'SetOwningWindowGroup(task.WgId());' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'KOrdinalPositionSwitchToOwningWindow' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_home_owner_stage in 144A 144B
do
    test "$(grep -ci "0x4D4D${matrixmenu_home_owner_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_foreground_stage in 0350 0351 0352 0353 0354 0355 0356
do
    test "$(grep -ci "0x4D4D${matrixmenu_foreground_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V4' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_cba_stage in 0372 0373 0374 0375
do
    test "$(grep -ci "0x4D4D${matrixmenu_cba_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'htcleoCbaWindow->SetOrdinalPosition(0, ECoeWinPriorityHigh);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'Cba()->SetBoundingRect(TRect(TPoint(0, 0), TSize(480, 800)));' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'Cba()->DrawNow();' "$matrixmenu_appui_source")" -eq 2
for matrixmenu_stage in 0320 0321 0322 0323 0324 0325 0326 0327 0328 0329 \
    032A 032B 032C 0330 0331 0332 0333
do
    test "$(grep -c "0x4D4D${matrixmenu_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'StatusPane()->MakeVisible(ETrue);' \
    "$matrixmenu_appui_source")" -eq 2
test "$(grep -c '0x4D4D0305u, KErrNotSupported, 0x5452414Eu' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_ROM_PRESENTATION_FALLBACK_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_FIRST_FRAME_FINISH_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c '0x4D4D0319u' "$matrixmenu_appui_source")" -eq 1
test "$(grep -c '0x4D4D031Au' "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'iCoeEnv->WsSession().Finish();' \
    "$matrixmenu_appui_source")" -eq 4
for matrixmenu_stage in 0340 0341 0342
do
    test "$(grep -c "0x4D4D${matrixmenu_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test -s "$matrixmenu_touch_suite"
test "$(grep -F -c 'type="grid|list"' "$matrixmenu_touch_suite")" -eq 1
test "$(grep -F -c 'template="logical_template_3|list_single_hc_apps_pane"' \
    "$matrixmenu_touch_suite")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MENULOG.TXT' \
    "$matrixmenu_logger_source")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*htcleomenulog.cpp' \
    "$matrixmenu_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$matrixmenu_mmp")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_GCCE_STACK_HEADROOM_V1' \
    "$matrixmenu_mmp")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_INITIAL_STATUSLAYOUT_DEFER_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D0307u, KErrNotSupported, 0x53504C59u);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -F -c 'StatusPane()->SwitchLayoutL( R_AVKON_STATUS_PANE_LAYOUT_USUAL );' \
    "$matrixmenu_appui_source")" -eq 1
! grep -q 'HTCLEO_MATRIXMENU_DUMMY_GRID_RESULT_TRACE_V1\|htcleoDummyGridResult' \
    "$matrixmenu_appui_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_DUMMY_CONTAINER_UI_FIRST_BYPASS_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D0309u, KErrNotSupported, 0x44554D59u);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D030Au, KErrNotSupported, 0x44554D59u);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_HNENGINE_RESULT_TRACE_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D030Bu, htcleoHnEngineResult,' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(htcleoHnEngineResult);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D030Fu, KErrNotSupported, 0x4558544Eu);' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'HtcleoMenuLog(0x4D4D0310u, htcleoHazeResult, 0x534B494Eu);' \
    "$matrixmenu_appui_source")" -eq 1
! grep -q 'CMMExtensionManager::NewL' \
    "$matrixmenu_appui_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'SetAllDefinitionSets(htcleoHazePid)' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_haze_stage in 0360 0361 0362
do
    test "$(grep -ci "0x4D4D${matrixmenu_haze_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW_V1' \
    "$matrixmenu_appui_source")" -eq 1
test "$(grep -c 'iSkinSrvSession.EnableSkinChangeNotify();' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_haze_notify_stage in 0363 0364 0365
do
    test "$(grep -ci "0x4D4D${matrixmenu_haze_notify_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MMWIDGETS_HAZE_SCREEN_BACKGROUND_V1' \
    "$mmwidgets_widget_source")" -eq 1
test "$(grep -c 'KAknsIIDQsnBgScreen, Rect(), EFalse' \
    "$mmwidgets_widget_source")" -eq 1
! grep -q 'KAknsIIDQsnBgAreaMainAppsGrid, Rect(), EFalse' \
    "$mmwidgets_widget_source"
test "$(grep -c 'HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND_V1' \
    "$mmwidgets_component/src/mmlistboxitemdrawer.cpp")" -eq 1
for mmwidgets_cpu_haze_stage in 0170 0171
do
    test "$(grep -ci "0x4D57${mmwidgets_cpu_haze_stage}u" \
        "$mmwidgets_component/src/mmlistboxitemdrawer.cpp")" -eq 1
done
test "$(grep -c 'HTCLEO_MMWIDGETS_TYPE2A_REDRAW_SNAPSHOT_V1' \
    "$mmwidgets_component/src/mmlistboxitemdrawer.cpp")" -eq 1
for mmwidgets_touch_redraw_stage in 0178 0179 017A
do
    test "$(grep -ci "0x4D57${mmwidgets_touch_redraw_stage}u" \
        "$mmwidgets_component/src/mmlistboxitemdrawer.cpp")" -eq 1
done
test "$(grep -c 'EPOCSTACKSIZE[[:space:]]*0x10000' \
    "$matrixmenu_mmp")" -eq 1
for matrixmenu_stage in \
    4D4D0000 4D4D0001 4D4D0002 4D4D0003 \
    4D4D0100 4D4D0101 \
    4D4D0200 4D4D0201 4D4D0210 4D4D0211 4D4D0212 4D4D0220 4D4D0221 \
    4D4D0300 4D4D0301 4D4D0302 4D4D0303 4D4D0304 4D4D0305 \
    4D4D0306 4D4D0307 4D4D0308 4D4D0309 4D4D030A 4D4D030B \
    4D4D030C 4D4D030D 4D4D030E 4D4D030F 4D4D0310 4D4D0311 4D4D0312 \
    4D4D1000 4D4D1001 4D4D1002 4D4D1003 4D4D1004 4D4D1005 \
    4D4D1006 4D4D1007 4D4D1008 4D4D1009 4D4D100A 4D4D100B \
    4D4D100C 4D4D100D 4D4D100E 4D4D100F 4D4D1010 4D4D1011 4D4D1012
do
    test "$(grep -h "0x${matrixmenu_stage}u" \
        "$matrixmenu_entry_source" "$matrixmenu_app_source" \
        "$matrixmenu_document_source" "$matrixmenu_appui_source" | wc -l)" -eq 1
done
test "$(grep -c 'HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE_V1' \
    "$matrixmenu_entry_source")" -eq 1
for matrixmenu_exception_stage in 12A0 12A1
do
    test "$(grep -ci "0x4D4D${matrixmenu_exception_stage}u" \
        "$matrixmenu_entry_source")" -eq 1
done
test "$(grep -c 'User::SetExceptionHandler(' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'User::Panic(KHtcleoMatrixMenuException, 3)' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -ci '0x4D4D12A5u' "$matrixmenu_entry_source")" -eq 1
test "$(grep -ci '0x4D4D12A6u' "$matrixmenu_entry_source")" -eq 1
test "$(grep -ci '0x4D4D12B0u+' "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'htcleoCallerStackIndex<96' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c '__attribute__((naked))' \
    "$matrixmenu_entry_source")" -eq 1
test "$(grep -c 'HtcleoMatrixMenuExceptionHandlerBody(' \
    "$matrixmenu_entry_source")" -eq 2
! grep -q 'TUint32 htcleoStackWords\[32\]\|htcleoStackIndex<32' \
    "$matrixmenu_entry_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1' \
    "$matrixmenu_entry_source")" -eq 1
for matrixmenu_retired_abort_stage in 12A2 12A3 12A4
do
    ! grep -qi "0x4D4D${matrixmenu_retired_abort_stage}u" \
        "$matrixmenu_entry_source"
done
! grep -q 'User::After\|HalFunction' \
    "$matrixmenu_logger_source" "$matrixmenu_entry_source" \
    "$matrixmenu_app_source" "$matrixmenu_document_source" \
    "$matrixmenu_appui_source"
test -s "$mmwidgets_logger_source"
test "$(grep -c 'HTCLEO_MMWIDGETS_DUMMY_GRID_DURABLE_LOG_V1' \
    "$mmwidgets_logger_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MMWLOG.TXT' \
    "$mmwidgets_logger_source")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*htcleommwlog.cpp' \
    "$mmwidgets_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$mmwidgets_mmp")" -eq 1
test "$(grep -h 'HtcleoMmwLog(0x4D57' \
    "$mmwidgets_widget_source" "$mmwidgets_grid_source" | wc -l)" -eq 54
test "$(grep -c 'HTCLEO_MMWIDGETS_TYPE2A_DIAGNOSTIC_V1' \
    "$mmwidgets_widget_source")" -eq 1
for mmwidgets_touch_stage in 0172 0173 0174 0175 0176 0177
do
    test "$(grep -ci "0x4D57${mmwidgets_touch_stage}u" \
        "$mmwidgets_widget_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MMWIDGETS_GRID_POINTER_TRACE_V1' \
    "$mmwidgets_grid_control_source")" -eq 1
for mmwidgets_pointer_stage in 0180 0181
do
    test "$(grep -ci "0x4D57${mmwidgets_pointer_stage}u" \
        "$mmwidgets_grid_control_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MMWIDGETS_GRID_WINDOW_HANDLE_PUBLISH_V1' \
    "$mmwidgets_grid_source")" -eq 1
test "$(grep -c '0x7F4D5701u' "$mmwidgets_grid_source")" -eq 1
test "$(grep -c 'HtcleoMmwLog(0x4D570144u, htcleoGridHandleResult, (TUint32)this);' \
    "$mmwidgets_grid_source")" -eq 1
test "$(grep -c 'HTCLEO_MMWIDGETS_POSTPROCESS_AO_TRACE_V1' \
    "$mmwidgets_post_source")" -eq 1
test "$(grep -c 'HTCLEO_MMWIDGETS_POSTPROCESS_BOUNDS_GUARD_V1' \
    "$mmwidgets_post_source")" -eq 1
test "$(grep -ci '0x4D570216u' "$mmwidgets_post_source")" -eq 1
test "$(grep -c 'HTCLEO_MMWIDGETS_DRAWER_AO_TRACE_V1' \
    "$mmwidgets_drawer_source")" -eq 1
test "$(grep -c 'HTCLEO_MMWIDGETS_LOG_CAPACITY_1M_V1' \
    "$mmwidgets_logger_source")" -eq 1
test "$(grep -c 'position <= ((16384 \* 64) - 64)' \
    "$mmwidgets_logger_source")" -eq 1
test "$(grep -h -c 'HtcleoMmwLog(0x4D5702' \
    "$mmwidgets_post_source" "$mmwidgets_widget_source" \
    "$mmwidgets_drawer_source" | awk '{s += $1} END {print s}')" -eq 29
! grep -q 'User::After\|HalFunction' \
    "$mmwidgets_logger_source"
test "$(grep -c 'HTCLEO_HNENGINE_DURABLE_LOG_V1' \
    "$hnengine_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HNLOG.TXT' \
    "$hnengine_source")" -eq 1
test "$(grep -c 'HtcleoHnLog(0x484E' "$hnengine_source")" -eq 41
test "$(grep -c 'HTCLEO_HNENGINE_INITIALIZE_DURABLE_LOG_V1' \
    "$hnengine_source")" -eq 1
test "$(grep -c 'HTCLEO_HNENGINE_BUILD_CLOSURE_V1' \
    "$hnengine_mmp")" -eq 1
! grep -q 'User::After\|HalFunction' "$hnengine_source"
test "$(grep -c 'HTCLEO_HNMETADATAMODEL_DURABLE_LOG_V1' \
    "$hnmetadata_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MDLOG.TXT' \
    "$hnmetadata_source")" -eq 1
test "$(grep -c 'HtcleoMdLog(0x4D44' "$hnmetadata_source")" -eq 33
test "$(grep -c 'HTCLEO_HNMETADATAMODEL_BUILD_CLOSURE_V1' \
    "$hnmetadata_mmp")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATAMODEL_FROZEN_ABI_CLOSURE_V1' \
    "$hnmetadata_component/inc/hnmdevent.h")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_SHOWFOLDER_UI_FIRST_DEFER_V1' \
    "$hnmetadata_source")" -eq 1
test "$(grep -c 'HtcleoMdLog(0x4D44012Cu, KErrNotSupported, 0x53464F4Cu);' \
    "$hnmetadata_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_EVALUATION_DURABLE_LOG_V1' \
    "$hnmetadata_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMDSUITE_EVALUATION_DURABLE_LOG_V1' \
    "$hnmetadata_suite_source")" -eq 1
test "$(grep -c 'HtcleoMdSuiteLog(0x4D44' \
    "$hnmetadata_suite_source")" -eq 20
test "$(grep -c 'HTCLEO_HNQUERY_EVALUATION_DURABLE_LOG_V1' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'HtcleoMdQueryLog(0x4D44' \
    "$hnmetadata_query_source")" -eq 47
test "$(grep -h -c 'HTCLEO_HN.*LOG_CAPACITY_16K_V1' \
    "$hnmetadata_source" "$hnmetadata_suite_source" \
    "$hnmetadata_query_source" | awk '{s += $1} END {print s}')" -eq 3
test "$(grep -h -c 'HTCLEO_HNMETADATA_LOG_CAPACITY_1M_V1' \
    "$hnmetadata_source" "$hnmetadata_suite_source" \
    "$hnmetadata_query_source" "$hnmetadata_notify_source" | \
    awk '{s += $1} END {print s}')" -eq 4
test "$(grep -h -c 'position <= ((16384 \* 64) - 64)' \
    "$hnmetadata_source" "$hnmetadata_suite_source" \
    "$hnmetadata_query_source" "$hnmetadata_notify_source" | \
    awk '{s += $1} END {print s}')" -eq 4
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_UI_FIRST_COMPAT_V1' \
    "$hnmetadata_notify_source")" -eq 1
test "$(grep -h -c 'HtcleoMdNotifyLog(0x4D44' \
    "$hnmetadata_notify_source" "$hnmetadata_notify_request_source" | \
    awk '{s += $1} END {print s}')" -eq 19
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_RECONNECT_REQUERY_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_LIFETIME_TRACE_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_CALLBACK_ENTRY_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_HIGH_REFRESH_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_NOTIFY_USER_INPUT_REFRESH_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_REDUNDANT_ASYNC_REFRESH_RETIRED_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
! grep -q 'new (ELeave) CAsyncCallBack\|iHtcleoInitialRefresh->CallBack();' \
    "$hnmetadata_notify_request_source"
test "$(grep -ci '0x4D440513u' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -ci '0x4D440514u' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_INITIAL_NOTIFICATION_COALESCE_V1' \
    "$hnmetadata_notify_request_source")" -eq 1
! sed -n '/HTCLEO_HNMETADATA_INITIAL_NOTIFICATION_COALESCE_V1/,/return err;/p' \
    "$hnmetadata_notify_request_source" | grep -q 'HtcleoMdNotifyLog'
! grep -q 'CActive::EPriorityUserInput' "$hnmetadata_notify_request_source"
! grep -q 'CActive::EPriorityHigh' "$hnmetadata_notify_request_source"
! grep -q 'CActive::EPriorityStandard' "$hnmetadata_notify_request_source"
! grep -q 'CActive::EPriorityIdle' "$hnmetadata_notify_request_source"
test "$(grep -c 'HtcleoResetServiceHandler' \
    "$hnmetadata_notify_request_source")" -eq 1
test "$(grep -c 'CAsyncCallBack\* iHtcleoInitialRefresh' \
    "$hnmetadata_notify_request_header")" -eq 1
test "$(grep -c 'HTCLEO_HNMETADATA_LOG_CAPACITY_1M_V1' \
    "$hnmetadata_notify_source")" -eq 1
! grep -q 'User::After\|HalFunction' \
    "$hnmetadata_source" "$hnmetadata_suite_source" \
    "$hnmetadata_query_source" "$hnmetadata_notify_source" \
    "$hnmetadata_notify_request_source"
test "$(grep -c 'HTCLEO_MCS_UI_FIRST_COMPAT_V1' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MCSLOG.TXT' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'HtcleoMcsLog(0x4D43' \
    "$mcsmenu_engine_source")" -eq 24
test "$(grep -c 'HTCLEO_MCS_SERVER_CONTEXT_TRACE_V1' \
    "$mcsmenu_server_source")" -eq 1
for mcsmenu_context_stage in 142 143 144 145 146 147 148 149 14A 14B 14C 14D 14E 14F 150
do
    mcsmenu_stage_count=1
    case "$mcsmenu_context_stage" in 144|145) mcsmenu_stage_count=2 ;; esac
    test "$(grep -hi "0x4D430${mcsmenu_context_stage}u" \
        "$mcsmenu_server_source" "$mcsmenu_engine_source" | wc -l)" -eq "$mcsmenu_stage_count"
done
test "$(grep -c 'HTCLEO_MCS_SERVER_PERSISTENT_LIFETIME_V1' \
    "$mcsmenu_server_source")" -eq 1
for mcsmenu_server_lifetime_stage in 151 152
do
    test "$(grep -ci "0x4D430${mcsmenu_server_lifetime_stage}u" \
        "$mcsmenu_server_source")" -eq 1
done
! grep -q 'iExitTimer->After( TTimeIntervalMicroSeconds32( 0 ) );' \
    "$mcsmenu_server_source"
! grep -q 'iExitTimer->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );' \
    "$mcsmenu_server_source"
test "$(grep -c 'HTCLEO_MCS_ENGINE_PERSISTENT_LIFETIME_V1' \
    "$mcsmenu_engine_source")" -eq 1
for mcsmenu_lifetime_stage in 131 132 133 134 135
do
    test "$(grep -ci "0x4D430${mcsmenu_lifetime_stage}u" \
        "$mcsmenu_engine_source")" -eq 1
done
test "$(grep -c 'iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'HTCLEO_MENUENG_DURABLE_LOG_V1' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MCSLOG.TXT' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'HtcleoMenuEngLog(0x4D45' \
    "$mcsmenu_menueng_source")" -eq 53
test "$(grep -c 'HTCLEO_MENUENG_RAM_MISSING_ROM_FALLBACK_V1' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1' \
    "$mcsmenu_menueng_state_header")" -eq 1
for mcsmenu_ram_commit_stage in 530 531
do
    test "$(grep -ci "0x4D450${mcsmenu_ram_commit_stage}u" \
        "$mcsmenu_menueng_source")" -eq 1
done
test "$(grep -c 'iFs.Entry(iRamFileName, htcleoRamEntry)' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c '0x524F4D46u' "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'iEngine->LoadL( \*iTree, iRamFileName )' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'iEngine->LoadL( \*iTree, fname )' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'HTCLEO_MENUENG_FROZEN_ABI_CLOSURE_V1' \
    "$mcsmenu_core_mmp")" -eq 1
test "$(grep -c 'DEFFILE[[:space:]]*mcsmenueng.def' \
    "$mcsmenu_core_mmp")" -eq 1
test "$(grep -c 'HTCLEO_MENUENG_NUMATTRIBUTES_LOCAL_ABI_V1' \
    "$mcsmenu_menueng_header")" -eq 1
! grep -q 'IMPORT_C TInt NumAttributes() const' "$mcsmenu_menueng_header"
test "$(grep -c 'iEng = CMenuEng::NewL' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'CMcsGetlistHandler::NewL' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'CMenuSrvAppScanner::NewL' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_UI_FIRST_FAILOPEN_V1' \
    "$mcsmenu_utils_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1' \
    "$mcsmenu_engine_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1' \
    "$mcsmenu_utils_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_SCANNER_TRACE_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_SCANNER_ASYNC_NOTIFY_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_SCANNER_OPTIONAL_CONSTRUCT_FAILOPEN_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_SCANNER_POINTER_INIT_V1' \
    "$mcsmenu_scanner_source")" -eq 1
for mcsmenu_optional_stage in 160 161 162 163 164
do
    test "$(grep -ci "0x4D430${mcsmenu_optional_stage}u" \
        "$mcsmenu_scanner_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1' \
    "$mcsmenu_utils_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1' \
    "$mcsmenu_scanner_header")" -eq 1
for mcsmenu_retry_stage in 165 166 167
do
    test "$(grep -ci "0x4D430${mcsmenu_retry_stage}u" \
        "$mcsmenu_scanner_source")" -eq 1
done
test "$(grep -c 'KHtcleoApaRetryLimit = 12' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'KHtcleoApaRetryDelayUs = 250000' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'iHtcleoApaRetryTimer.After' \
    "$mcsmenu_scanner_source")" -eq 1
! grep -q 'User::After' "$mcsmenu_scanner_source"
test "$(grep -c 'HTCLEO_MCS_APPARC_RETURNED_RETRY_V2' \
    "$mcsmenu_utils_source")" -eq 2
test "$(grep -c 'HTCLEO_MCS_APPARC_RETURNED_RETRY_V2' \
    "$mcsmenu_utils_header")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_RETURNED_RETRY_V2' \
    "$mcsmenu_scanner_header")" -eq 1
test "$(grep -c 'TInt ReloadApaItemsL();' \
    "$mcsmenu_utils_header")" -eq 1
test "$(grep -c 'return htcleoApaReconnectResult != KErrNone' \
    "$mcsmenu_utils_source")" -eq 1
! grep -q 'User::Leave(htcleoApaReconnectResult' "$mcsmenu_utils_source"
test "$(grep -c 'iHtcleoApaReloadResult = iSrvEngUtils.ReloadApaItemsL();' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_APPARC_SERVER_RESTART_V1' \
    "$mcsmenu_utils_source")" -eq 2
for mcsmenu_restart_stage in 168 169 16A 16B
do
    test "$(grep -ci "0x4D430${mcsmenu_restart_stage}u" \
        "$mcsmenu_utils_source")" -eq 1
done
test "$(grep -c 'server.Create(KHtcleoApaServerExe' \
    "$mcsmenu_utils_source")" -eq 1
test "$(grep -c 'User::WaitForRequest(status)' \
    "$mcsmenu_utils_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_READY_GENERATION_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_READY_GENERATION_V1' \
    "$hnmetadata_notify_source")" -eq 1
test "$(grep -ci '0x4D43016Cu' "$mcsmenu_scanner_source")" -eq 1
for hn_ready_stage in 50E 50F 510
do
    test "$(grep -ci "0x4D440${hn_ready_stage}u" \
        "$hnmetadata_notify_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HN_READY_GENERATION_REQUEST_GUARD_V1' \
    "$hnmetadata_notify_source")" -eq 1
test "$(grep -ci '0x4D440511u' "$hnmetadata_notify_source")" -eq 1
test "$(grep -c 'if (!htcleoNotifySent)' \
    "$hnmetadata_notify_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1' \
    "$hnmetadata_notify_source")" -eq 2
test "$(grep -ci '0x4D440512u' "$hnmetadata_notify_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_COMMIT_REQUERY_V1' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_COMMIT_REQUERY_V1' \
    "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_HN_COMMIT_REQUERY_V1' \
    "$hnmetadata_query_source")" -eq 2
test "$(grep -c 'HTCLEO_MCS_HN_COMMIT_REQUERY_V1' \
    "$hnmetadata_query_header")" -eq 1
test "$(grep -ci '0x4D450532u' "$mcsmenu_menueng_source")" -eq 1
for hn_query_retry_stage in 460 461 462 463 464
do
    test "$(grep -ci "0x4D440${hn_query_retry_stage}u" \
        "$hnmetadata_query_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HN_GETLIST_SYNCHRONOUS_V1' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -ci '0x4D440465u' "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'HTCLEO_HN_GETLIST_PROVIDER_SYNC_PUMP_MODE_V1' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'htcleoQueryMode = EServiceModeAsynchronous' \
    "$hnmetadata_query_source")" -eq 1
! grep -q 'htcleoQueryMode = EServiceModeSynchronous' \
    "$hnmetadata_query_source"
test "$(grep -c 'HTCLEO_MCS_GETLIST_SYNC_PUMP_V6' \
    "$mcsservice_source")" -eq 1
test "$(grep -c 'TRAP(htcleoGetListResult, GetListL())' \
    "$mcsservice_source")" -eq 1
test "$(grep -c 'NotifyRequestResultL(htcleoGetListResult)' \
    "$mcsservice_source")" -eq 1
test "$(grep -c '0x101F4CD2u' "$mcsservice_source")" -eq 6
! grep -q 'HTCLEO_MCS_GETLIST_RETURN_COUNT_PROPERTY_V1\|0x7F4D4302u' \
    "$mcsservice_source"
test "$(grep -c 'HTCLEO_MCS_GETLIST_ICON_ITEM_FAILOPEN_V1' \
    "$mcsservice_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_ICON_ERROR_RESET_V1' \
    "$mcsservice_source")" -eq 1
test "$(grep -c '0x7F4D4303u' "$mcsservice_source")" -eq 6
test "$(grep -c 'HTCLEO_MCS_GETLIST_OUTER_ERROR_RAW_RESULT_V1' \
    "$mcsservice_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_SYNC_RESULT_PROPERTY_V1' \
    "$mcsservice_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_SERVER_COUNT_PROPERTY_V1' \
    "$mcsmenu_getlist_source")" -eq 1
test "$(grep -c '0x7F4D4302u' "$mcsmenu_getlist_source")" -eq 1
test "$(grep -c 'outputList->Count()' "$mcsmenu_getlist_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2' \
    "$mcsmenu_session_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2' \
    "$mcsmenu_session_header")" -eq 1
test "$(grep -c 'iHtcleoGetListOutput.Copy(htcleoSharedOutput)' \
    "$mcsmenu_session_source")" -eq 1
for mcs_getlist_session_stage in 170 171 172 173 174 175
do
    test "$(grep -ci "0x4D430${mcs_getlist_session_stage}u" \
        "$mcsmenu_session_source")" -eq 1
done
test "$(grep -c 'HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1' \
    "$mcsmenu_api_source")" -eq 1
test "$(grep -c 'HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1' \
    "$mcsmenu_session_source")" -eq 1
test "$(grep -c 'KHtcleoAtomicGetListCapacity = 0x10000' \
    "$mcsmenu_api_source")" -eq 1
for mcs_getlist_atomic_stage in 176 177 178 179
do
    test "$(grep -ci "0x4D430${mcs_getlist_atomic_stage}u" \
        "$mcsmenu_session_source")" -eq 1
done
! grep -q 'User::After\|RTimer\|AppendL( htcleo' "$mcsservice_source"
test "$(grep -c 'HTCLEO_HN_QUERY_CONSUMPTION_TRACE_V1' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'HTCLEO_HN_ITEM_RESULTS_TRACE_V8' \
    "$hnmetadata_item_source")" -eq 2
for hn_query_tail_stage in 467 468 469 46A 46B 46C
do
    test "$(grep -ci "0x4D440${hn_query_tail_stage}u" \
        "$hnmetadata_query_source")" -eq 1
done
for hn_item_stage in 470 471 472 473 474 475 476 477 480 481 482 483 484 \
    485 486 487 490 491 492 493 494 495 496 497 498 499 49A 49B 49C 49D
do
    test "$(grep -ci "0x4D440${hn_item_stage}u" \
        "$hnmetadata_item_source")" -eq 1
done
test "$(grep -c 'observersNotified && htcleoVisibleItemsAfterEvaluation > 0' \
    "$hnmetadata_item_source")" -eq 1
test "$(grep -c 'observersNotified && htcleoVisibleItemsAfterEvaluation == 0' \
    "$hnmetadata_item_source")" -eq 1
! grep -q 'User::After\|RTimer\|AppendL( htcleo' \
    "$hnmetadata_query_source" "$hnmetadata_item_source"
test "$(grep -c 'HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -ci '0x4D440466u' "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'iStatus != KRequestPending' \
    "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1' \
    "$hnmetadata_query_source")" -eq 3
test "$(grep -c 'RunL();' "$hnmetadata_query_source")" -eq 1
test "$(grep -c 'HTCLEO_HN_SYNC_OWNED_SIGNAL_CONSUME_V1' "$hnmetadata_query_source")" -eq 1
test "$(grep -F -c 'User::WaitForRequest(iStatus);' "$hnmetadata_query_source")" -eq 1
! grep -q 'User::RequestComplete(htcleoQueuedStatus' \
    "$hnmetadata_query_source"
test "$(grep -c '0x4D43016Cu, KErrNotReady' \
    "$mcsmenu_scanner_source")" -eq 1
test "$(grep -c '0x7F4D4301u' "$mcsmenu_scanner_source")" -eq 0
test "$(grep -c '0x7F4D4301u' "$hnmetadata_notify_source")" -eq 1
test "$(grep -c '0x7F4D4301u' "$mcsmenu_menueng_source")" -eq 1
test "$(grep -c '0x7F4D4301u' "$hnmetadata_query_source")" -eq 2
test "$(grep -c 'User::WaitForRequest(htcleoReadyStatus)' \
    "$hnmetadata_notify_source")" -eq 1
! grep -q 'RTimer htcleoReadyTimer\|htcleoReadyAttempts' \
    "$hnmetadata_notify_source"
! grep -q 'HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1\|HTCLEO_MCS_APPARC_SCANNER_BOUNDED_WAIT_V1\|CActiveSchedulerWait\|CPeriodic' \
    "$mcsmenu_scanner_source" "$mcsmenu_scanner_header"
test "$(grep -c '!iApaLsSession.Handle()' \
    "$mcsmenu_utils_source")" -eq 5
! grep -q '0x41505053u' "$mcsmenu_engine_source"
test "$(grep -c 'iApaLsSession.Connect()' \
    "$mcsmenu_utils_source")" -eq 3
test "$(grep -c 'HTCLEO_MCS_LOGGER_EXPORT_V1' \
    "$mcsmenu_engine_source")" -eq 1
for mcsmenu_scanner_stage in 128 129 12A
do
    test "$(grep -ci "0x4D430${mcsmenu_scanner_stage}u" \
        "$mcsmenu_scanner_source")" -eq 1
done
for mcsmenu_reconnect_stage in 12B 12C
do
    test "$(grep -ci "0x4D430${mcsmenu_reconnect_stage}u" \
        "$mcsmenu_utils_source")" -eq 1
done
for mcsmenu_sync_stage in 12D 12E 12F
do
    test "$(grep -ci "0x4D430${mcsmenu_sync_stage}u" \
        "$mcsmenu_scanner_source")" -eq 1
done
test "$(grep -ci '0x4D430130u' "$mcsmenu_scanner_source")" -eq 1
! grep -q 'iWidgetSession.Connect\|iWsSession.Connect\|iWidgetSession.IsWidget' \
    "$mcsmenu_utils_source"
test "$(grep -c 'iCenRepSession = CRepository::NewL' \
    "$mcsmenu_scanner_source")" -eq 1
! grep -q 'StartListeningL\|CMcsSatNotifier::NewL\|CMcsFreeSpaceObserver::NewL\|CMcsSatHandler::CheckVisibility' \
    "$mcsmenu_scanner_source"
! grep -q 'User::After\|HalFunction' \
    "$mcsmenu_engine_source" "$mcsmenu_menueng_source" "$mcsmenu_utils_source" \
    "$mcsmenu_scanner_source"
python3 "$wserv_log_transform" "$full_epocroot"
python3 "$wserv_plugin_transform" "$full_epocroot"
python3 "$wserv_screen_transform" "$full_epocroot"
python3 "$wserv_client_window_transform" "$full_epocroot"
python3 "$wserv_matrixmenu_command_buffer_transform" "$full_epocroot"
python3 "$wserv_type2a_pointer_transform" "$full_epocroot"
python3 "$wserv_type2a_raw_trace_transform" "$full_epocroot"
python3 "$wserv_event_hook_counter_transform" "$full_epocroot"
python3 "$wserv_runl_trace_bound_transform" "$full_epocroot"
python3 "$wserv_absrect_pointer_fallback_transform" "$full_epocroot"
python3 "$wserv_published_grid_fallback_transform" "$full_epocroot"
python3 "$wserv_published_grid_capture_transform" "$full_epocroot"
python3 "$matrixmenu_teardown_attribution_transform" "$full_epocroot"
python3 "$wserv_matrixmenu_panic_category_transform" "$full_epocroot"
python3 "$wserv_touch_only_log_transform" "$full_epocroot"
python3 "$wserv_low_rate_touch_transform" "$full_epocroot"
python3 "$home_liveness_transform" "$full_epocroot"
python3 "$wserv_shell_handoff_transform" "$full_epocroot"
python3 "$wserv_worker_retirement_transform" "$full_epocroot"
python3 "$display_log_transform" "$full_epocroot"
python3 "$display_cpu_blit_transform" "$full_epocroot"
python3 "$display_flicker_cpu_blit_transform" "$full_epocroot"
python3 "$display_frame_signature_transform" "$full_epocroot"
python3 "$display_region_blit_transform" "$full_epocroot"
python3 "$ui_frame_stage_correlation_transform" "$full_epocroot"
python3 "$matrixmenu_scheduler_retirement_transform" "$full_epocroot"
python3 "$shell_pointer_log_retirement_transform" "$full_epocroot"
python3 "$matrixmenu_visual_skin_transform" "$full_epocroot"
python3 "$display_scheduler_blank_guard_transform" "$full_epocroot"
python3 "$display_high_frequency_log_retirement_transform" "$full_epocroot"
python3 "$wfc_log_transform" "$full_epocroot"
python3 "$nvg_log_transform" "$full_epocroot"
python3 "$ecom_log_transform" "$full_epocroot"
python3 "$ecom_load_split_transform" "$full_epocroot"
python3 "$ecom_init_entrypoint_transform" "$full_epocroot"
python3 "$ecom_featmgr_list_transform" "$full_epocroot"
python3 "$ecom_server_transform" "$full_epocroot"
python3 "$ecom_homescreen_server_trace_transform" "$full_epocroot"
python3 "$ecom_hsps_definition_resolve_transform" "$full_epocroot"
python3 "$ecom_hsps_persistent_trace_transform" "$full_epocroot"
python3 "$ecom_hsps_response_trace_transform" "$full_epocroot"
python3 "$ecom_hsps_client_load_trace_transform" "$full_epocroot"
python3 "$ecom_featureinfo_empty_transform" "$full_epocroot"
python3 "$ecom_matrixmenu_retry_transform" "$full_epocroot"
python3 "$ecom_matrixmenu_list_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_list_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_action_list_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_nonvisual_list_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_menubar_list_retry_transform" "$full_epocroot"
python3 "$ecom_homescreen_rendering_list_retry_transform" "$full_epocroot"
python3 "$ptiengine_transform" "$full_epocroot"
python3 "$stem_backend_transform" "$full_epocroot"
python3 "$stem_backend_timezone_transform" "$full_epocroot"
python3 "$hitchcock_transform" "$full_epocroot"
test "$(grep -c 'HTCLEO_SSM_DURABLE_LOG_V1' "$ssm_main")" -eq 1
test "$(grep -c 'HTCLEO_CLE_DURABLE_LOG_V1' "$ssm_cle_executor")" -eq 1
test "$(grep -c 'HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG_V1' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_LOAD_SPLIT_V1' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_INIT_ENTRYPOINT_LOG_V1' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '#include <e32ldr_private.h>' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '#include <e32const_private.h>' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '#include <e32panic.h>' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '#include <exec_enum.h>' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '#include <u32std.h>' \
    "$ssm_custom_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\CUSTLOG.TXT' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'aInfo->Ordinal() == 1' "$ssm_custom_source")" -eq 1
test "$(grep -c 'aInfo->FileName().CompareF(KHtcleoAknCustCmdDll)' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'HtcleoCustomCmdLog(0x0000C' \
    "$ssm_custom_source")" -eq 65
for ssm_load_split_stage in 0 1 2 3 4 5 6 7 8
do
    test "$(grep -c "0x0000C10${ssm_load_split_stage}u" \
        "$ssm_custom_source")" -eq 1
done
test "$(grep -c 'htcleoLoader.LoadLibrary(htcleoHandle,' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'err = iLibrary.Init();' \
    "$ssm_custom_source")" -eq 0
test "$(grep -c 'err = HtcleoAknLibraryInit(iLibrary,' \
    "$ssm_custom_source")" -eq 1
for ssm_init_stage in 1 2 3 4 5 6 7 8 9
do
    test "$(grep -c "0x0000C20${ssm_init_stage}u" \
        "$ssm_custom_source")" -eq 1
done
test "$(grep -c '0x0000C210u' "$ssm_custom_source")" -eq 1
test "$(grep -c '0x0000C211u' "$ssm_custom_source")" -eq 1
for ssm_attach_watch_stage in 00 01 02 04
do
    test "$(grep -c "0x0000CA${ssm_attach_watch_stage}u" \
        "$ssm_custom_source")" -eq 1
done
test "$(grep -c '0x0000CA03u' "$ssm_custom_source")" -eq 2
test "$(grep -c '0x0000CA05u' "$ssm_custom_source")" -eq 2
test "$(grep -c '0x0000CA10u + step' "$ssm_custom_source")" -eq 1
test "$(grep -c '0x0000CB00u' "$ssm_custom_source")" -eq 1
test "$(grep -c '0x0000CB06u' "$ssm_custom_source")" -eq 1
test "$(grep -c '0x0000CB10u + (TUint32)phase' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c '0x0000CB20u + (TUint32)phase' \
    "$ssm_custom_source")" -eq 1
test "$(grep -c 'HtcleoAknAttachBootstrap(' \
    "$ssm_custom_source")" -eq 2
test "$(grep -c 'HtcleoAknAttachTraceStart(' \
    "$ssm_custom_source")" -eq 2
test "$(grep -c 'HtcleoAknAttachTraceStop(' \
    "$ssm_custom_source")" -eq 4
test "$(grep -c 'HTCLEO_GCCE_PRIVATE_TIMER_EXPORT_ABI_V1' \
    "$ssm_custom_header")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG__' \
    "$ssm_custom_mmp")" -eq 1
test "$(grep -c 'deffile[[:space:]]*ssmcmd_v1.def' \
    "$ssm_custom_mmp")" -eq 1
test "$(grep -c 'deffile[[:space:]]*ssmcmd.def' \
    "$ssm_custom_mmp")" -eq 1
! grep -q 'NOSTRICTDEF' "$ssm_custom_mmp"
test "$(grep -c 'HTCLEO_AKN_CUSTOM_COMMAND_DURABLE_LOG_V1' \
    "$akn_custom_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\CUSTLOG.TXT' \
    "$akn_custom_source")" -eq 1
test "$(grep -c 'HtcleoAknCustomLog(0x0000D' \
    "$akn_custom_source")" -eq 9
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_AKN_CUSTOM_COMMAND_DURABLE_LOG__' \
    "$akn_custom_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$akn_custom_mmp")" -eq 1
! grep -q 'User::After' "$ssm_custom_source" "$akn_custom_source"
test "$(grep -c 'User::WaitForRequest(' "$ssm_custom_source")" -eq 2
! grep -q 'User::WaitForRequest' "$akn_custom_source"
test "$(grep -c 'HTCLEO_APPARC_DURABLE_LOG_V1' "$apparc_apserv_logger")" -eq 1
test "$(grep -c 'HTCLEO_APPARC_DURABLE_LOG_V1' "$apparc_aplist_logger")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\APALOG.TXT' "$apparc_apserv_logger")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\APALOG.TXT' "$apparc_aplist_logger")" -eq 1
test "$(grep -c '__HTCLEO_APPARC_DURABLE_LOG__' "$apparc_apserv_mmp")" -eq 1
test "$(grep -c '__HTCLEO_APPARC_DURABLE_LOG__' "$apparc_aplist_mmp")" -eq 1
test "$(grep -c 'HTCLEO_APPARC_RESTART_OPTIONAL_RECOVERY_V1' \
    "$apparc_apsserv_source")" -eq 1
for apparc_restart_gap_stage in 0000020B 0000020C 0000020D 0000020E 0000020F
do
    test "$(grep -c "0x${apparc_restart_gap_stage}u" \
        "$apparc_apsserv_source")" -eq 1
done
test "$(grep -c 'htcleoUpdateRecoveryResult != KErrServerTerminated' \
    "$apparc_apsserv_source")" -eq 1
test "$(grep -c 'HTCLEO_APPARC_RESTART_OPTIONAL_RECOGNIZER_V1' \
    "$apparc_apsserv_source")" -eq 1
test "$(grep -c 'htcleoRecognizerResult != KErrServerTerminated' \
    "$apparc_apsserv_source")" -eq 1
test "$(grep -c 'if(iMimeTypeRecognizer &&' \
    "$apparc_apsserv_source")" -eq 1
! grep -q 'User::After\|User::WaitForRequest' \
    "$apparc_apserv_logger" "$apparc_aplist_logger"
test "$(grep -c 'HTCLEO_APPARC_LAUNCH_DURABLE_LOG_V1' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_APPARC_LAUNCH_EXIT_CATEGORY_LOG_V2' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAP_THREAD_EXIT_CATEGORY_LOG_V3' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAP_CLIENT_HELD_PROCESS_RENDEZVOUS_V4' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1' \
    "$apparc_launch_source")" -eq 2
test "$(grep -c 'HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG_V1' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_MATRIXMENU_BOUNDED_RETRY_V3' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_REUSE_INFLIGHT_CHILD_TRACE_V4' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_DISCOVER_REGISTERED_SERVER_V1' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNUI_CONNECT_MATRIXMENU_SINGLE_ATTEMPT_V1' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'const TInt htcleoAknUiRetryLimit = 1;' \
    "$apparc_launch_source")" -eq 1
! grep -q '(htcleoAknUiCallerSid == 0x101f4cd2u) ? 64 : 1' \
    "$apparc_launch_source"
test "$(grep -c 'User::WaitForRequest(htcleoMatrixReadyStatus);' \
    "$apparc_launch_source")" -eq 2
test "$(grep -c 'HTCLEO_AKNCAPSERVER_OFN_BYPASS_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E102u, KErrNone, 0x4F464E00u);' \
    "$akncapserver_source")" -eq 1
! grep -q '^[[:space:]]*InitiateOFNStatus();' "$akncapserver_source"
test "$(grep -c 'HTCLEO_AKNCAPSERVER_POSTCRITICAL_FILELOG_RETIREMENT_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'static TBool gHtcleoAknCapFileLogRetired = EFalse;' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E100u, KErrNone, 0x4E4F494Fu);' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'if (aStage == 0x0000E100u)' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_POSTCRITICAL_PROPERTY_BREADCRUMB_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'TUid::Uid(0x10207218), 0x7f044301u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_E100_PRE_RETIREMENT_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'gHtcleoAknCapFileLogRetired = ETrue;' \
    "$akncapserver_source")" -eq 2
test "$(grep -c 'HTCLEO_AKNCAPSERVER_CRITICALITY_BYPASS_V1' \
    "$akncapserver_source")" -eq 1
! grep -q 'User::SetCritical(User::ESystemCritical);' "$akncapserver_source"
test "$(grep -c 'HTCLEO_AKNCAPSERVER_NONLEO_STARTUP_BYPASSES_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_NO_HWRM_SLIDE_OBSERVER_V1' \
    "$akncapserver_component/src/aknKeyFilter.cpp")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_NO_MMC_PASSWORD_IPC_GUARD_V1' \
    "$akncapserver_ipc_source")" -eq 1
test "$(grep -c 'if (!iAppUi->MMCUnlock())' \
    "$akncapserver_ipc_source")" -eq 1
test "$(grep -c 'if (!err && iAppUi->MMCUnlock())' \
    "$akncapserver_ipc_source")" -eq 1
test "$(grep -c 'if (iAppUi->MMCUnlock())' \
    "$akncapserver_ipc_source")" -eq 1
! grep -q '^[[:space:]]*DoProductSpecificHalFunction();' "$akncapserver_source"
! grep -q 'CAknMMCPasswordRequester::NewL();' "$akncapserver_source"
! grep -q 'CAknCapServerDiscreetPopupHandler::CreateDiscreetPopupHandlerL();' \
    "$akncapserver_source"
! grep -q '^[[:space:]]*LoadAlternateFsPlugin();' "$akncapserver_source"
! grep -q '^[[:space:]]*ProcessInitFlipStatus();' "$akncapserver_source"
! grep -q 'CAknSlideStatusNotifier::NewL( this )' \
    "$akncapserver_component/src/aknKeyFilter.cpp"
test "$(grep -c 'iFSControl= new (ELeave) CAknFastSwapWindowControl' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_POSTPROCESS_GAP_TRACE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_AKNCAP_PRIORITY_DEFER_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'htcleoDeferBackgroundPriority' \
    "$eikcore_source")" -eq 3
test "$(grep -c 'RProcess().SecureId().iId == 0x10207218u' \
    "$eikcore_source")" -ge 1
for eikcore_gap_stage in 312 313 314 315 316 317 318 319 31A 31B 31C 31D 31E
do
    test "$(grep -c "HtcleoEikCorePreFactoryTrace(0xE${eikcore_gap_stage}u" \
        "$eikcore_source")" -eq 1
done
test "$(grep -F -c 'C:\\Symbian3\\MENULOG.TXT' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'htcleoAknUiCallerSid != 0x101f4cd2u' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'User::After(500000);' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c '0x50535754u' \
    "$apparc_launch_source")" -eq 1
! grep -q '0x4E4F544Du' "$apparc_launch_source"
test "$(grep -c '0x4D4DA21Du' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c '0x4D4DA21Eu' \
    "$apparc_launch_source")" -eq 1
for aknui_discovery_stage in 228 229 22A
do
    test "$(grep -c "0x4D4DA${aknui_discovery_stage}u" \
        "$apparc_launch_source")" -eq 1
done
test "$(grep -F -c '"*_10207218_AppServer"' \
    "$apparc_launch_source")" -eq 1
for aknui_reuse_stage in 21F 220 221
do
    test "$(grep -c "0x4D4DA${aknui_reuse_stage}u" \
        "$apparc_launch_source")" -eq 1
done
test "$(grep -c 'KHtcleoEikCoreTraceKey = 0x7f044301u' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'if (!htcleoReuseInflightChild)' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'htcleoAknUiRetryLimit' \
    "$apparc_launch_source")" -eq 3
for aknui_connect_stage in \
    200 201 202 203 204 205 \
    210 211 212 213 214 215 216 217 218 219 21A 21B 21C
do
    test "$(grep -c "0x4D4DA${aknui_connect_stage}u" \
        "$apparc_launch_source")" -eq 1
done
test "$(grep -F -c 'C:\\Symbian3\\APASTART.TXT' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c '__HTCLEO_APPARC_LAUNCH_DURABLE_LOG__' \
    "$apparc_launch_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$apparc_launch_mmp")" -eq 1
test "$(grep -c 'HtcleoApaLaunchLog(0x0000A00' \
    "$apparc_launch_source")" -eq 7
test "$(grep -c 'HtcleoApaLaunchLog(0x0000B00' \
    "$apparc_launch_source")" -eq 7
test "$(grep -c 'HtcleoApaLaunchLog(0x0000A20' \
    "$apparc_launch_source")" -eq 13
test "$(grep -c 'HtcleoApaLaunchLog(0x0000B10' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'htcleoAknProcess.CreateWithStackOverride' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'htcleoAknProcess.Rendezvous(' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'htcleoAknProcess.Resume()' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'htcleoAknReadyProperty.Subscribe' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'htcleoAknProcess.Logon' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'WaitForRequest(htcleoAknReadyStatus' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'htcleoAknReadyProperty.Get(htcleoAknReadyValue)' \
    "$apparc_launch_source")" -eq 2
test "$(grep -c 'KHtcleoAknReadyPollLimit' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'User::After(10000);' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'for(; htcleoAknPollCount' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'RProperty::Delete(' \
    "$apparc_launch_source")" -eq 0
test "$(grep -c 'KHtcleoAknReadyKey = 0x7f044302u' \
    "$apparc_launch_source")" -eq 1
! grep -Fq 'apa.StartApp(*cmdLine, dummy, &requestStatusForRendezvous)' \
    "$apparc_launch_source"
test "$(grep -c 'htcleoAknThread.ExitCategory()' \
    "$apparc_launch_source")" -eq 1
test "$(grep -c 'server.ExitCategory()' "$apparc_launch_source")" -eq 0
test "$(grep -c 'HtcleoPackApaExitCategory' \
    "$apparc_launch_source")" -eq 5
! grep -q 'LeaveIfError(htcleoApaStartResult)' "$apparc_launch_source"
test "$(grep -c 'HTCLEO_AKNCAPSERVER_STARTUP_DURABLE_LOG_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_EIKSTART_DURABLE_LOG_V2' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_CONSTRUCTOR_ERROR_V4' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_EIKCORE_TRACE_BRIDGE_V5' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT_V1' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNCAPSERVER_PROPERTY_READY_SIGNAL_V1' \
    "$akncapserver_source")" -eq 2
test "$(grep -c 'HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1' \
    "$akncapserver_source")" -eq 1
! grep -q 'env->ConstructorError\|env->CoeEnvConstructorError' \
    "$akncapserver_source"
test "$(grep -c 'env->HtcleoConstructorError()' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'CEikonEnv::Static() == env' \
    "$akncapserver_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\AKNCAP.TXT' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_AKNCAPSERVER_STARTUP_LOG__' \
    "$akncapserver_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$akncapserver_mmp")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E' \
    "$akncapserver_source")" -eq 78
test "$(grep -c 'HtcleoAknCapLog(0x0000E213u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E214u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E215u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E216u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E217u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoAknCapLog(0x0000E218u' \
    "$akncapserver_source")" -eq 1
for akncap_registration_stage in 219 21A 21B
do
    test "$(grep -c "HtcleoAknCapLog(0x0000E${akncap_registration_stage}u" \
        "$akncapserver_source")" -eq 1
done
test "$(grep -c 'RProcess::Rendezvous(KErrNone)' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'KHtcleoEikCoreTraceKey = 0x7f044301u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'KHtcleoAknReadyKey = 0x7f044302u' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'HtcleoRunAknCapApplication(NewApplication)' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'env->ConstructAppFromCommandLineL' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'position >= (512 \* 65)' \
    "$akncapserver_source")" -eq 1
! grep -q 'User::After\|User::WaitForRequest' "$akncapserver_source"
test "$(grep -c 'appServer->ConstructL(expectedName)' \
    "$akncapserver_source")" -eq 1
test "$(grep -c 'htcleoAknReadyValue' "$akncapserver_source")" -eq 3
test "$(grep -c '(void)RProperty::Delete(' "$akncapserver_source" || true)" -eq 0
test "$(grep -c 'HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVC_SINGLE_CHILD_READY_RETRY_V1' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVC_COMPACT_READY_POLL_LOG_V1' \
    "$eiksrvc_source")" -eq 1
! grep -q 'HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT_V1' \
    "$eiksrvc_source"
test "$(grep -F -c 'C:\\Symbian3\\EIKCONN.TXT' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x10207218u' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'HtcleoEikConnTarget()' "$eiksrvc_source")" -eq 3
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKSRVC_CONNECT_LOG__' \
    "$eiksrvc_mmp")" -eq 1
test "$(grep -c 'library[[:space:]]*efsrv.lib' "$eiksrvc_mmp")" -eq 1
for eiksrvc_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E \
    10 11 12 13 14 15 16 17 18 19 1A 1B 1C
do
    test "$(grep -c "HtcleoEikConnLog(0x0000E9${eiksrvc_stage}u" \
        "$eiksrvc_source")" -eq 1
done
test "$(grep -c 'CreateSession(EIKAPPUI_SERVER_NAME,Version())' \
    "$eiksrvc_source")" -eq 1
for eiksrvc_compat_stage in 50 51
do
    test "$(grep -c "HtcleoEikConnLog(0x0000E9${eiksrvc_compat_stage}u" \
        "$eiksrvc_source")" -eq 1
done
for eiksrvc_ready_stage in 40 41 42
do
    test "$(grep -c "HtcleoEikConnLog(0x0000E9${eiksrvc_ready_stage}u" \
        "$eiksrvc_source")" -eq 1
done
test "$(grep -c 'TInt retry=KNumConnectRetries;' "$eiksrvc_source")" -eq 1
test "$(grep -c 'retry=64;' "$eiksrvc_source")" -eq 1
test "$(grep -c 'htcleoServerStartIssued=ETrue;' "$eiksrvc_source")" -eq 1
test "$(grep -c 'const TBool htcleoReadinessPoll=' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'htcleoSingleChildRetry && htcleoServerStartIssued;' \
    "$eiksrvc_source")" -eq 1
test "$(grep -c 'if (!htcleoReadinessPoll)' \
    "$eiksrvc_source")" -eq 2
test "$(grep -c 'if (htcleoReadinessPoll)' \
    "$eiksrvc_source")" -eq 1
! grep -q 'User::WaitForRequest(stat, htcleoTimeoutStatus)' \
    "$eiksrvc_source"
test "$(grep -c 'User::WaitForRequest(stat)' "$eiksrvc_source")" -eq 1
! grep -q 'server.RendezvousCancel(stat)' "$eiksrvc_source"
! grep -q 'RTimer htcleoRendezvousTimer\|TTimeIntervalMicroSeconds32' \
    "$eiksrvc_source"
! grep -q 'User::After' "$eiksrvc_source"
test "$(grep -c 'HTCLEO_EIKSRVS_STARTUP_DURABLE_LOG_V1' \
    "$eiksrvs_source")" -eq 1
test "$(grep -c 'HtcleoEikSrvLog(0x0000E7' "$eiksrvs_source")" -eq 17
for eiksrvs_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10
do
    test "$(grep -c "HtcleoEikSrvLog(0x0000E7${eiksrvs_stage}u" \
        "$eiksrvs_source")" -eq 1
done
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKSRVS_STARTUP_LOG__' \
    "$eiksrvs_mmp")" -eq 1
test "$(grep -c 'library[[:space:]]*efsrv.lib' "$eiksrvs_mmp")" -eq 1
! grep -q 'User::After' "$eiksrvs_source"
test "$(grep -c 'HTCLEO_EIKSRV_SERVER_CONSTRUCT_DURABLE_LOG_V1' \
    "$eiksrv_source")" -eq 1
for eiksrv_stage in \
    20 21 22 23 24 25 26 27 \
    30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F \
    40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F \
    50 51 52 53 54 55 56 57
do
    test "$(grep -c "HtcleoEikSrvDeepLog(0x0000E7${eiksrv_stage}u" \
        "$eiksrv_source")" -eq 1
done
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKSRV_SERVER_CONSTRUCT_LOG__' \
    "$eiksrv_mmp")" -eq 1
! grep -q 'User::After' "$eiksrv_source"
test "$(grep -c 'HTCLEO_EIKSRVUI_CONSTRUCT_DURABLE_LOG_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_SKIN_RESULT_RELEAVE_V2' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_INITIALIZE_DURABLE_LOG_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_NOTIFIER_SERVER_UI_FAIL_OPEN_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_LOG_CLOSE_ONLY_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_LOG_FRONTIER_TAIL_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_OPTIONAL_UI_TAIL_BYPASS_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -F -c 'aStage >= 0x0000E7DCu && aStage <= 0x0000E7E2u' \
    "$eiksrvui_source")" -eq 1
test "$(grep -F -c 'aStage >= 0x0000E776u && aStage <= 0x0000E79Bu' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'file.Flush();' "$eiksrvui_source")" -eq 0
test "$(grep -c 'iNotifyServer = CEikServNotifyServer::NewL' \
    "$eiksrvui_source")" -eq 0
test "$(grep -c 'iEikServExtra->iNotifierServerStarter = CIdle::NewL' \
    "$eiksrvui_source")" -eq 0
test "$(grep -c '0x4E465953u' "$eiksrvui_source")" -eq 3
test "$(grep -c 'TRAP_IGNORE(EnsureExternalKeyHandlerAppStreamExistsL());' \
    "$eiksrvui_source")" -eq 0
test "$(grep -c 'const TInt htcleoKeySoundResult =' \
    "$eiksrvui_source")" -eq 0
test "$(grep -c 'iAknAnimDll = new(ELeave)RAnimDll(wsSession);' \
    "$eiksrvui_source")" -eq 0
test "$(grep -c 'ReplaceKeySoundsL(0x100053D0);' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'LoadBitmapCursorsL();' "$eiksrvui_source")" -eq 1
test "$(grep -c '0x4558544Bu' "$eiksrvui_source")" -eq 2
test "$(grep -c '0x4B534E44u' "$eiksrvui_source")" -eq 10
test "$(grep -c '0x43555253u' "$eiksrvui_source")" -eq 2
test "$(grep -c 'HTCLEO_EIKSRVUI_CONSTRUCT_ENTRY_SPLIT_LOG_V1' \
    "$eiksrvui_source")" -eq 1
for eiksrvui_entry_stage in E7F0 E7F1 E7F2 E7F3 E7F4
do
    if [ "$eiksrvui_entry_stage" = E7F3 ]; then
        test "$(grep -c 'HtcleoEikSrvUiLog(0x0000E7F3u, KErrNotSupported, 0x53595301u)' \
            "$eiksrvui_source")" -eq 1
    else
        test "$(grep -c "HtcleoEikSrvUiLog(0x0000${eiksrvui_entry_stage}u, KErrNone, 0u)" \
            "$eiksrvui_source")" -eq 1
    fi
done
test "$(grep -c 'HTCLEO_EIKSRVUI_SYSTEM_ATTRIBUTE_UI_FAIL_OPEN_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'iEikonEnv->SetSystem(ETrue);' "$eiksrvui_source")" -eq 0
test "$(grep -c 'groupWin.SetName(__EIKON_SERVER_NAME);' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKSRVUI_BASECONSTRUCT_RESULT_LOG_V1' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'TRAP(htcleoBaseConstructResult,' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c '0x42415345u' "$eiksrvui_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(htcleoBaseConstructResult);' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_SCREEN_CHANGE_UI_FIRST_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_FIXED_SCREEN_SIZE_UI_FIRST_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_TACTILE_FEEDBACK_UI_FIRST_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_EIKSRV_TRANSITION_EFFECTS_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_LOG_CLOSE_ONLY_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_MATRIXMENU_UI_FIRST_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c '(aStage < 0x0000B51Cu || aStage > 0x0000B520u))' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_POSTCOE_LAYOUT_DURABLE_LOG_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_POSTCOE_FIXED_SCREEN_SIZE_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_MATRIXMENU_POSTCOE_FIXED_SCREEN_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_CPU_BACKGROUND_V1' \
    "$stem_avkon_grid_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x101F4CD2u' \
    "$stem_avkon_grid_source")" -eq 2
test "$(grep -c 'HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_EMPTY_CELLS_V1' \
    "$stem_avkon_grid_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG_V1' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT_V1' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT_V1' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MENULOG.TXT' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c 'htcleoSid != 0x101f4cd2u && !htcleoHome' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x102750f0u);' \
    "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c 'HTCLEO_HAK  ' "$stem_avkon_aknenv_source")" -eq 1
test "$(grep -c '1048576 - 128' "$stem_avkon_aknenv_source")" -eq 1
for aknenv_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \
    10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E
do
    test "$(grep -c "0x4D4DA0${aknenv_stage}u" \
        "$stem_avkon_aknenv_source")" -eq 1
done
! grep -q 'User::After\|HalFunction' "$stem_avkon_aknenv_source"
test "$(grep -c 'HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_MATRIXMENU_AKNCAP_FAIL_OPEN_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK_COMPAT_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK_COMPAT_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HtcleoAknAppUiBaseLog(0x0000C594u' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'UserSvr::HalFunction' "$stem_avkon_source")" -eq 3
avkon_focus_rearm_block=$(sed -n \
    '/HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1/,/HtcleoAknAppUiBaseLog(0x0000C568u/p' \
    "$stem_avkon_source")
for avkon_focus_rearm_token in \
    'EHalGroupPlatformSpecific2, 10' 'EHalGroupPlatformSpecific2, 11' \
    '0x0000C594u'
do
    printf '%s\n' "$avkon_focus_rearm_block" | \
        grep -F -q "$avkon_focus_rearm_token"
done
! printf '%s\n' "$avkon_focus_rearm_block" | \
    grep -q 'HtcleoI2c\|ResetAndDetect\|User::After\|RTimer\|WaitForRequest\|LeaveIfError\|RequestComplete\|SetOrdinal\|DrawNow\|Finish()'
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'aStage >= 0x0000C560u && aStage <= 0x0000C59Fu' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c '!htcleoHomeFocusStage' \
    "$stem_avkon_source")" -eq 1
for htcleo_home_focus_stage in \
    560 561 562 563 564 565 566 567 568 569 56A 56B 56C 56D 56E
do
    test "$(grep -c "HtcleoAknAppUiBaseLog(0x0000C${htcleo_home_focus_stage}u" \
        "$stem_avkon_source")" -eq 1
done
for htcleo_home_keyblock_stage in 570 571 572 573 574 575 576
do
    test "$(grep -c "0x0000C${htcleo_home_keyblock_stage}u" \
        "$stem_avkon_sgc_source")" -eq 1
done
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE_V1' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE_V1' \
    "$stem_avkon_viewappui_source")" -eq 1
for htcleo_home_foreground_stage in \
    580 581 582 583 584 585 586 587 588 589 58A 58B 58C 58D 58E 58F \
    590 591 592 593
do
    test "$(grep -ci "0x0000C${htcleo_home_foreground_stage}u" \
        "$stem_avkon_source")" -eq 1
done
for htcleo_home_view_foreground_stage in 598 599 59A 59B 59C 59D 59E
do
    test "$(grep -ci "0x0000C${htcleo_home_view_foreground_stage}u" \
        "$stem_avkon_viewappui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_HANDLE_COMPAT_V1' \
    "$stem_avkon_sgc_source")" -eq 1
for htcleo_home_fade_stage in 577 578 579 57A 57B 57C 57D 57E 57F
do
    test "$(grep -ci "0x0000C${htcleo_home_fade_stage}u" \
        "$stem_avkon_sgc_source")" -eq 1
done
test "$(grep -c 'htcleoHomeSystemFade && htcleoAknSrvHandle == 0' \
    "$stem_avkon_sgc_source")" -eq 2
test "$(grep -c 'iAknSrv.IsSystemFaded(fade);' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'iAknSrv.SetSystemFaded(aFade);' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'htcleoHomeKeyBlock && htcleoAknSrvHandle == 0' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'iAknSrv.SetKeyblockMode(aMode);' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MENULOG.TXT' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'htcleoSid != 0x101f4cd2u && !htcleoHome' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x102750f0u) &&' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_HSG  ' "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c '1048576 - 128' "$stem_avkon_sgc_source")" -eq 1
for aknsgc_stage in \
    A100 A101 A102 A103 A104 A105 A106 A107 \
    A110 A111 A112 A113 A114 A115 \
    A120 A121 A122 A123 A124 A125 A126 A127 A128 A129 \
    A12A A12B A12C A12D A12E A12F A130 A131 A132 A133
do
    test "$(grep -c "0x4D4D${aknsgc_stage}u" \
        "$stem_avkon_sgc_source")" -eq 1
done
! grep -q 'User::After\|HalFunction' "$stem_avkon_sgc_source"
test "$(grep -c 'HTCLEO_AKNSGC_HANDLECHANGE_DURABLE_LOG_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_EIKSRV_FOREGROUND_QUERY_COMPAT_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_EIKSRV_SETSGCPARAMS_COMPAT_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_MATRIXMENU_SETSGCPARAMS_DEFER_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'const TBool htcleoDeferForegroundQuery =' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'if (!htcleoDeferForegroundQuery)' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'foreground = topAppUi->IsForeground();' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c '0x46475244u' "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'const TBool htcleoDeferSgcParams =' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_DEFER_V1' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'htcleoSgcProcessSid == 0x101F4CD2u;' \
    "$stem_avkon_sgc_source")" -eq 0
test "$(grep -F -c 'htcleoSgcProcessSid == 0x101F4CD2u ||' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'htcleoSgcProcessSid == 0x102750F0u;' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'if (!htcleoDeferSgcParams)' \
    "$stem_avkon_sgc_source")" -eq 2
test "$(grep -F -c 'iAknSrv.SetSgcParams(' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'User::LeaveIfError(htcleoSgcSetResult);' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c '0x53474350u' "$stem_avkon_sgc_source")" -eq 1
test "$(grep -F -c 'if (!htcleoUiFirstFixedPanel)' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'iEikonEnv->RootWin().EnableScreenChangeEvents();' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c 'htcleoScreenChangeResult, 0x5343524Eu' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'RProcess().SecureId().iId == 0x10003A4A;' \
    "$stem_avkon_source")" -eq 0
test "$(grep -F -c 'htcleoAppSid == 0x10003A4Au || htcleoMatrixMenuUiFirst;' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'htcleoPostCoeSid == 0x101F4CD2u;' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c '            iCoeEnv->ScreenDevice()->SizeInPixels();' \
    "$stem_avkon_source")" -eq 2
test "$(grep -F -c 'iAppUiBaseExtension->iApplicationRect = TSize(480, 800);' \
    "$stem_avkon_source")" -eq 2
test "$(grep -c 'htcleoUseFixedScreenSize ? 0x53495A45u : 0u' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'const TBool htcleoDeferTactileFeedback = htcleoUseFixedScreenSize;' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'CTouchFeedbackAdaptation::NewL();' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c '0x48415054u' "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'const TBool htcleoDeferTransitionEffects =' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'if (!htcleoDeferTransitionEffects)' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c '!htcleoDeferTransitionEffects) //does start idle time' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'iAvkonEnv->TransitionEvent(KAknTransitionEventFlags);' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);' \
    "$stem_avkon_source")" -eq 1
test "$(grep -c '0x54524E46u' "$stem_avkon_source")" -eq 1
test "$(grep -c '0x54524E53u' "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'r = file.Write(record);' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'file.Flush();' "$stem_avkon_source")" -eq 0
test "$(grep -c 'HTCLEO_AVKON_GCCE_C1_ALIAS_V1' \
    "$stem_avkon_lists_source")" -eq 1
test "$(grep -c '\.global _ZN23AknListBoxLinesTemplate' \
    "$stem_avkon_lists_source")" -eq 3
test "$(grep -F -c 'C:\\Symbian3\\AKNBASE.TXT' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'const TBool htcleoLogHomeScreen = htcleoLogSid == 0x102750F0u;' \
    "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'if (!htcleoLogEikSrv && !htcleoLogMatrixMenu &&' \
    "$stem_avkon_source")" -eq 1
for htcleo_home_trace_bound in \
    'aStage >= 0x0000B500u && aStage <= 0x0000B520u' \
    'aStage >= 0x0000B530u && aStage <= 0x0000B547u' \
    'aStage >= 0x0000C500u && aStage <= 0x0000C52Cu'
do
    test "$(grep -F -c "$htcleo_home_trace_bound" \
        "$stem_avkon_source")" -eq 1
done
test "$(grep -F -c '1048576 - 128' "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'HTCLEO_HAB  ' "$stem_avkon_source")" -eq 1
test "$(grep -F -c 'if (htcleoLogEikSrv &&' \
    "$stem_avkon_source")" -eq 1
for aknappui_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \
    10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20
do
    test "$(grep -c "HtcleoAknAppUiBaseLog(0x0000B5${aknappui_stage}u" \
        "$stem_avkon_source")" -eq 1
done
for aknappui_postcoe_stage in \
    30 31 32 33 34 35 40 41 42 43 44 45 46 47
do
    test "$(grep -c "HtcleoAknAppUiBaseLog(0x0000B5${aknappui_postcoe_stage}u" \
        "$stem_avkon_source")" -eq 1
done
for aknsgc_stage in \
    00 01 02 03 04 \
    10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D \
    20 21 22 23 24 25 26 27 28 29 2A 2B 2C
do
    test "$(grep -c "0x0000C5${aknsgc_stage}u" \
        "$stem_avkon_sgc_source")" -eq 1
done
test "$(grep -c 'extern void HtcleoAknAppUiBaseLog' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'iAknSrv.SetSgcParams(' \
    "$stem_avkon_sgc_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__' \
    "$stem_avkon_mmp")" -eq 1
grep -q 'TARGET[[:space:]]*stem_avkon.dll' "$stem_avkon_mmp"
! grep -q 'OPTION[[:space:]]*GCCE[[:space:]]*-fpermissive' \
    "$stem_avkon_mmp"
for stem_avkon_case_library in \
    AknNotify.lib findutil.lib ServiceHandler.lib NumberGrouping.lib
do
    test "$(grep -F -c "LIBRARY         $stem_avkon_case_library" \
        "$stem_avkon_mmp")" -eq 1
done
test "$(grep -c 'DEFFILE[[:space:]]*/root/symbian3-full/sf/mw/classicui/uifw/AvKon/EABI/AVKON.DEF' \
    "$stem_avkon_mmp")" -eq 1
! grep -q 'DEFFILE[[:space:]]*/sf/mw/classicui/uifw/AvKon/~/AVKON.def' \
    "$stem_avkon_mmp"
test -s "$stem_avkon_frozen_def_alias"
cmp -s "$stem_avkon_frozen_def_alias" \
    "$full_epocroot/sf/mw/classicui/uifw/AvKon/EABI/AVKONU.DEF"
grep -Fq '<var name="avkon_permissive">' "$stem_avkon_config_file"
grep -Fq '<set name="CC_ERRORS_CONTROL_OPTION" value="-fpermissive"/>' \
    "$stem_avkon_config_file"
grep -Fq '<set name="CC" value="/path/to/hd2-legacy-lab/Symbian/scripts/htcleo-gcce-avkon-cc-wrapper.sh"/>' \
    "$stem_avkon_config_file"
grep -Fq 'value="-Wl,--undefined=_ZTI17AknPopupListEmptyI24CEikFormattedCellListBoxE -Wl,--undefined=_ZTV17AknPopupListEmptyI24CEikFormattedCellListBoxE"/>' \
    "$stem_avkon_config_file"
test "$(grep -c 'StartC32();' "$eiksrvui_source")" -eq 0
test "$(grep -c 'HtcleoEikSrvUiLog(0x0000E7D8u, err, 0xC32F0001u)' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'TInt err = KErrNotSupported;' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'CEikServNotifyAlert\* alert = NULL;' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'alert->ConstructL();' "$eiksrvui_source")" -eq 0
test "$(grep -c 'HtcleoEikSrvUiLog(0x0000E774u, KErrNotSupported, 0xA17F0001u)' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'TRAP(htcleoSkinInitResult, AknsUtils::InitSkinSupportL())' \
    "$eiksrvui_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(htcleoSkinInitResult)' \
    "$eiksrvui_source")" -eq 1
for eiksrvui_stage in \
    60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F \
    70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F \
    90 91 92 93 94 95 96 97 98 99 9A 9B \
    A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF B0
do
    test "$(grep -c "HtcleoEikSrvUiLog(0x0000E7${eiksrvui_stage}u" \
        "$eiksrvui_source")" -eq 1
done
for eiksrvui_initialize_stage in \
    C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF \
    D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF \
    E0 E1 E2
do
    test "$(grep -c "HtcleoEikSrvUiLog(0x0000E7${eiksrvui_initialize_stage}u" \
        "$eiksrvui_source")" -eq 1
done
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKSRVUI_CONSTRUCT_LOG__' \
    "$eiksrvui_mmp")" -eq 1
grep -q 'TARGET[[:space:]]*stem_eiksrvui.dll' "$eiksrvui_mmp"
! sed -n \
    '/^EXPORT_C void CEikServAppUiBase::InitializeL/,/^EXPORT_C void CEikServAppUiBase::HandleThreadExitL/p' \
    "$eiksrvui_source" | grep -q 'User::After'
test "$(grep -c 'HTCLEO_C32ROOT_DURABLE_LOG_V1' "$c32root_source")" -eq 1
test "$(grep -c 'HTCLEO_C32START_DURABLE_LOG_V1' "$c32start_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\C32ROOT.TXT' "$c32root_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\C32START.TXT' "$c32start_source")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' "$c32root_mmp")" -eq 1
for c32root_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \
    10 11 12 13 14 15 16 17 18 19
do
    test "$(grep -c "HtcleoC32RootLog(0x0000C7${c32root_stage}u" \
        "$c32root_source")" -eq 1
done
for c32start_stage in \
    800 801 802 803 804 805 806 807 808 809 80A 80B 80C \
    820 821 822 823 824 825 826 827 828 829 82A 82B 82C \
    840 841 842 843 844 845 846 847 848 849 84A 84B 84C 84D 84E 84F \
    860 861 862 863 864 865 866 867 \
    870 871 872 873 874 875 876 877 878 879
do
    test "$(grep -c "HtcleoC32StartLog(0x0000C${c32start_stage}u" \
        "$c32start_source")" -eq 1
done
test "$(sed -n '/^static TInt DoStartC32/,/^EXPORT_C TInt StartC32()/p' \
    "$c32root_source" | grep -c 'User::WaitForRequest')" -eq 4
! grep -q 'User::After' "$c32root_source" "$c32start_source"
test "$(grep -c 'HTCLEO_AKNSKINSRV_DURABLE_LOG_V1' \
    "$aknskinsrv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_FALLBACK_MERGE_TRACE_V1' \
    "$aknskinsrv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_RESTORE_DEFAULT_TRACE_V1' \
    "$aknskinsrv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_BOOT_DRM_DEFER_V1' \
    "$aknskinsrv_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_SETTINGS_DEFAULT_TRACE_V1' \
    "$aknskinsrv_settings_source")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_CLIENT_TRACE_V1' \
    "$aknskinsrv_client_source")" -eq 1
test "$(grep -c 'HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_COMPAT_V1' \
    "$aknskinsrv_mxml_compat")" -eq 1
test "$(grep -c '^class MXMLAttributes;$' \
    "$aknskinsrv_mxml_compat")" -eq 1
for aknskinsrv_case_alias in \
    "$aknskins_component/srvinc/ImageConversion.h" \
    "$aknskins_component/srvinc/ICLExifImageFrame.h" \
    "$aknskins_component/srvinc/icl/Icl_UIDS.hrh"
do
    test "$(grep -c 'HTCLEO_AKNSKINSRV_CASE_ALIAS_COMPAT_V1' \
        "$aknskinsrv_case_alias")" -eq 1
done
test "$(grep -c 'HTCLEO_SVG_SAVE_DOM_QUALIFICATION_COMPAT_V1' \
    "$aknskins_component/srvinc/SVGEngineInterfaceImpl.h")" -eq 1
! grep -q 'CSvgEngineInterfaceImpl::SaveSvgDom' \
    "$aknskins_component/srvinc/SVGEngineInterfaceImpl.h"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/DRMHelper.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/drmhelper.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/imageconversion.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/ImageConversion.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/bitmaptransforms.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/BitmapTransforms.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/SVGEngine.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/SvgEngine.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/centralrepository.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/CentralRepository.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/cenrepnotifhandler.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/CenRepNotifHandler.dso"
cmp -s "$full_epocroot/epoc32/release/armv5/lib/platformenv.dso" \
    "$full_epocroot/epoc32/release/armv5/lib/PlatformEnv.dso"
test "$(grep -F -c 'C:\\Symbian3\\SKINLOG.TXT' \
    "$aknskinsrv_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_AKNSKINSRV_DURABLE_LOG__' \
    "$aknskinsrv_mmp")" -eq 1
test "$(grep -c 'HTCLEO_AKNSKINSRV_EABI_FROZEN_DEF_V1' \
    "$aknskinsrv_mmp")" -eq 1
! grep -q 'DEFFILE' "$aknskinsrv_mmp"
cmp -s "$aknskinsrv_frozen_def" \
    "$aknskins_component/BMARM/AKNSKINSRVU.DEF"
test -s "$aknskins_component/BMARM/AKNSKINSRVU.DEF.htcleo-armcc-original"
! cmp -s "$aknskinsrv_frozen_def" \
    "$aknskins_component/BMARM/AKNSKINSRVU.DEF.htcleo-armcc-original"
for aknskin_stage in \
    A800 A801 A802 A810 A811 A812 A813 A814 A820 A821 A822 A823 A824 A82F
do
    test "$(grep -c "0x0000${aknskin_stage}u" \
        "$aknskinsrv_client_source")" -eq 1
done
for aknskin_stage in \
    B800 B801 B802 B803 B804 B805 B806 B807 B808 B809 \
    C800 C801 C802 C803 C804 C805 C806 C807 C808 C809 \
    D800 D801 D802 D803 D804 D805 D806 D807 D808 D809 D80A D80B D80C D80D \
    D80E D80F D810 D811 D812 D813 D814 D815 D816 D817 D818 D819 D81A D81B \
    D81C D81D D840 D841 D842 D843 D844 D845 D846 D847 D848 \
    D860 D861 D862 D863 D864 D865 D870 D871 D872 D873 D874 D875 \
    D880 D881 D882 D883 D884 D885
do
    test "$(grep -c "0x0000${aknskin_stage}u" \
        "$aknskinsrv_source")" -eq 1
done
for aknskin_stage in \
    D890 D891 D892 D893 D894 D895 \
    D8A0 D8A1 D8A2 D8A3 D8A4 D8A5 D8A6 D8A7 \
    D8B0 D8B1 D8B2 D8B3 D8B4 D8B5 D8B6 D8B7 D8B8
do
    test "$(grep -c "0x0000${aknskin_stage}u" \
        "$aknskinsrv_settings_source")" -eq 1
done
! grep -q 'User::After' "$aknskinsrv_source" "$aknskinsrv_client_source"
! grep -q 'EHalGroupPlatformSpecific1, 2\|c6400000' \
    "$akncapserver_source"
test "$(grep -c 'HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_PREFACTORY_DURABLE_LOG_V2' \
    "$eikcore_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\MENULOG.TXT' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_AKNCAP_CONSTRUCTL_TRACE_V2' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG_V1' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_TRACE_V1' \
    "$eikappui_source")" -eq 1
for htcleo_eik_foreground_stage in \
    370 371 372 373 374 375 376 377 378 379 \
    380 381 382 383 384 385 386 387
do
    test "$(grep -ci "0x0000E${htcleo_eik_foreground_stage}u" \
        "$eikappui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKAPPUI_MATRIXMENU_FINAL_SCREEN_CHANGE_DEFER_V1' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKAPPUI_MATRIXMENU_LOG_CLOSE_ONLY_V1' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'HTCLEO_GCCE_UNLIMITED_FILENAME_OFFSET_V1' \
    "$eikcore_compat_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE__' \
    "$eikcore_mmp")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKAPPUI_BASECONSTRUCT_LOG__' \
    "$eikcore_mmp")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_POSTAPPUI_TRACE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_STARTUP_VIEW_ACTIVATOR_TRACE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_UNCHANGED_TASKNAME_DEFER_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_APPREADY_PUBLISH_DEFER_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_POST_CONTAINER_VIEW_RETIRE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'appUi.ActivateTopViewL();' "$eikcore_source")" -eq 0
test "$(grep -c 'HtcleoEikCorePreFactoryTrace(0xE367u, KErrNotSupported)' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_VIEW_INIT_RETIRE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c '0xE369u' "$eikcore_source")" -eq 1
test "$(grep -c '0xE36Au' "$eikcore_source")" -eq 1
test "$(grep -c 'appUi.CheckInitializeViewsL' "$eikcore_source")" -eq 1
test "$(grep -c 'HtcleoEikCorePreFactoryTrace(0xE3' \
    "$eikcore_source")" -eq 87
test "$(grep -c 'HtcleoEikCorePreFactoryTrace(0xE4' \
    "$eikcore_source")" -eq 38
test "$(grep -c '(void)RProperty::Set(' "$eikcore_source")" -eq 2
test "$(grep -c 'sid == KHtcleoAknCapTraceCategory.iUid' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'sid == KHtcleoMatrixMenuSid' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'KHtcleoHomeScreenSid = 0x102750f0u' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'sid == KHtcleoHomeScreenSid' \
    "$eikcore_source")" -eq 1
test "$(grep -c 'HtcleoEikCoreHomeScreenTrace(' \
    "$eikcore_source")" -eq 2
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikcore_source")" -eq 1
test "$(grep -c '1048576 - 128' "$eikcore_source")" -eq 1
test "$(grep -c 'HTCLEO_HCE  ' "$eikcore_source")" -eq 1
! grep -q 'AKNCAP.TXT\|User::After\|HalFunction' \
    "$eikcore_source"
test "$(grep -c 'HTCLEO_EIKSTART_HOMESCREEN_TRACE_V1' \
    "$eikstart_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId != 0x102750F0u' \
    "$eikstart_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x102750F0u' \
    "$eikstart_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikstart_source")" -eq 1
test "$(grep -c '1048576 - 128' "$eikstart_source")" -eq 1
for eikstart_home_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12
do
    test "$(grep -ci "0x485900${eikstart_home_stage}u" \
        "$eikstart_source")" -eq 1
done
test "$(grep -c 'GetCommandLineFromProcessEnvironment(commandLine)' \
    "$eikstart_source")" -eq 1
test "$(grep -c 'env->ConstructAppFromCommandLineL(aApplicationFactory, \*commandLine)' \
    "$eikstart_source")" -eq 1
! grep -q 'CApaCommandLine::New\|User::After\|HalFunction' \
    "$eikstart_source"
for eikappui_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \
    10 11 12 13 14 15
do
    test "$(grep -c "HtcleoEikAppUiBaseLog(0x0000B6${eikappui_stage}u" \
        "$eikappui_source")" -eq 1
done
test "$(grep -F -c 'C:\\Symbian3\\EIKBASE.TXT' \
    "$eikappui_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'htcleoEikBaseSid != 0x10003A4Au' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'htcleoEikBaseSid != 0x101F4CD2u' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'htcleoEikBaseSid == 0x102750F0u' \
    "$eikappui_source")" -eq 1
test "$(grep -c '1048576 - 128' "$eikappui_source")" -eq 1
test "$(grep -F -c 'HTCLEO_HEB  ' "$eikappui_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x101F4CD2u;' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'TInt htcleoEikScreenChangeResult = KErrNotSupported;' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'if (!htcleoDeferFinalScreenChange)' \
    "$eikappui_source")" -eq 1
test "$(grep -c 'iCoeEnv->RootWin().EnableScreenChangeEvents();' \
    "$eikappui_source")" -eq 1
! grep -q 'file.Flush();' "$eikappui_source"
! grep -q 'User::After\|HalFunction' "$eikappui_source"
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_APPINFO_DURABLE_LOG_V1' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_TRACE_V1' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'HTCLEO_GCCE_EIKCOCTL_INTEGER_ABS_COMPAT_V1' \
    "$eikcoctl_physics_source")" -eq 1
test "$(grep -c 'if ( Abs( iPrevOffset )' \
    "$eikcoctl_physics_source")" -eq 1
! grep -q 'if ( abs( iPrevOffset )' "$eikcoctl_physics_source"
test "$(grep -c 'HTCLEO_GCCE_EIKCOCTL_INLINE_EXPORT_COMPAT_V1' \
    "$eikcoctl_list_item_source")" -eq 1
test "$(grep -c 'EXPORT_C const CFont\* CTextListItemDrawer::Font' \
    "$eikcoctl_list_item_source")" -eq 1
! grep -q 'EXPORT_C inline const CFont\* CTextListItemDrawer::Font' \
    "$eikcoctl_list_item_source"
test "$(grep -c 'HTCLEO_GCCE_EIKCOCTL_TOUCH_DTOR_EXPORT_COMPAT_V1' \
    "$eikcoctl_touch_header")" -eq 1
test "$(grep -c 'IMPORT_C ~CAknTouchPane();' \
    "$eikcoctl_touch_header")" -eq 1
test "$(grep -c 'HTCLEO_GCCE_EIKCOCTL_PICTO_RTTI_EXPORT_COMPAT_V1' \
    "$eikcoctl_edwin_header")" -eq 1
test "$(grep -c 'class __attribute__((visibility("default"))) TAknEdwinPictographDrawer' \
    "$eikcoctl_edwin_header")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_EIKCOCTL_APPINFO_LOG__' \
    "$eikcoctl_mmp")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\EIKBASE.TXT' \
    "$eikcoctl_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'htcleoEikAppInfoSid != 0x101F4CD2u' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'htcleoEikAppInfoSid == 0x102750F0u' \
    "$eikcoctl_source")" -eq 1
test "$(grep -F -c 'HTCLEO_HEI  ' "$eikcoctl_source")" -eq 1
test "$(grep -F -c '(1024 * 1024) : (512 * 64)' \
    "$eikcoctl_source")" -eq 1
for eikcoctl_stage in \
    20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31
do
    test "$(grep -c "HtcleoEikAppInfoLog(0x0000B6${eikcoctl_stage}u" \
        "$eikcoctl_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_DURABLE_LOG_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_STATUSMODEL_DURABLE_LOG_V1' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_HOMESCREEN_STATUSPANE_TRACE_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_HOMESCREEN_STATUSMODEL_TRACE_V1' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\EIKBASE.TXT' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\EIKBASE.TXT' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$eikcoctl_statusmodel_source")" -eq 1
for eikcoctl_status_source in \
    "$eikcoctl_statuspane_source" "$eikcoctl_statusmodel_source"
do
    test "$(grep -c 'htcleoStatusPaneSid != 0x101F4CD2u' \
        "$eikcoctl_status_source")" -eq 1
    test "$(grep -c 'htcleoStatusPaneSid == 0x102750F0u' \
        "$eikcoctl_status_source")" -eq 1
    test "$(grep -F -c '(1024 * 1024) : (512 * 64)' \
        "$eikcoctl_status_source")" -eq 1
done
test "$(grep -F -c 'HTCLEO_HSP  ' "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -F -c 'HTCLEO_HSM  ' "$eikcoctl_statusmodel_source")" -eq 1
for eikcoctl_pane_stage in \
    40 41 42 43 44 \
    50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F \
    60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F \
    70 71 72 73 74 75 76 77 78 79 7A 7B
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B6${eikcoctl_pane_stage}u" \
        "$eikcoctl_statuspane_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_COMBINED_PANE_VISIBILITY_LOG_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
for eikcoctl_combined_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B7${eikcoctl_combined_stage}u" \
        "$eikcoctl_statuspane_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_FADE_FAILCLOSED_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_HOMESCREEN_FADE_FAILCLOSED_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'htcleoAknSrv->Handle() == 0' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'htcleoFadeSid == 0x101F4CD2u' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'htcleoFadeSid == 0x102750F0u' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'isFaded = IsFaded();' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HtcleoStatusPaneLog(0x0000B70Eu' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HtcleoStatusPaneLog(0x0000B70Fu' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2' \
    "$eikcoctl_source")" -eq 1
for eikcoctl_clientrect_stage in 10 11
do
    test "$(grep -c "HtcleoEikAppInfoLog(0x0000B7${eikcoctl_clientrect_stage}u" \
        "$eikcoctl_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1' \
    "$eikcoctl_statuspane_source")" -eq 1
for eikcoctl_statuspane_scale_stage in 12 13
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B7${eikcoctl_statuspane_scale_stage}u" \
        "$eikcoctl_statuspane_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2' \
    "$eikcoctl_cba_source")" -eq 1
test "$(grep -c 'htcleoMatrixMenuCba' "$eikcoctl_cba_source")" -eq 2
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_CBA_BOUNDING_SCALE_V1' \
    "$eikcoctl_cba_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_CBA_SIZE_SCALE_V1' \
    "$eikcoctl_cba_source")" -eq 1
test "$(grep -c 'SetRect( htcleoCbaScreenRect );' \
    "$eikcoctl_cba_source")" -eq 1
test "$(grep -c 'if ( redrawNeeded || !isVisible || IsEmpty() )' \
    "$eikcoctl_cba_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3' \
    "$eikcoctl_btgpc_source")" -eq 1
test "$(grep -c 'htcleoRealButtonGroup->SetRect(Rect());' \
    "$eikcoctl_btgpc_source")" -eq 1
test "$(grep -c 'htcleoRealButtonGroup->DrawDeferred();' \
    "$eikcoctl_btgpc_source")" -eq 1
test "$(grep -c 'htcleoRealButtonGroup->DrawableWindow();' \
    "$eikcoctl_btgpc_source")" -eq 1
test "$(grep -F -c 'static_cast<RWindow*>(htcleoDrawableWindow)->Invalidate(' \
    "$eikcoctl_btgpc_source")" -eq 1
test "$(grep -c 'htcleoRealButtonGroup->DrawNow(htcleoRedrawRect);' \
    "$eikcoctl_btgpc_source")" -eq 1
for htcleo_home_geometry_source in \
    "$eikcoctl_source" "$eikcoctl_statuspane_source" \
    "$eikcoctl_cba_source" "$eikcoctl_btgpc_source"
do
    test "$(grep -c 'HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1' \
        "$htcleo_home_geometry_source")" -eq 1
done
test "$(grep -c 'htcleoGeometrySid == 0x102750F0u' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'htcleoPaneSid == 0x102750F0u' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c '== 0x102750F0u' "$eikcoctl_cba_source")" -eq 3
test "$(grep -c 'htcleoCbaWrapperSid == 0x102750F0u' \
    "$eikcoctl_btgpc_source")" -eq 1
! grep -h -q 'HTCLEO_AKNAPPUI_HOMESCREEN_FIXED_SCREEN_SIZE_V1' \
    "$stem_avkon_source"
test "$(grep -c 'HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION_V1' \
    "$matrixmenu_appui_source")" -eq 1
for matrixmenu_full_grid_stage in 0370 0371
do
    test "$(grep -ci "0x4D4D${matrixmenu_full_grid_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
for eikcoctl_model_stage in \
    90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F \
    A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B6${eikcoctl_model_stage}u" \
        "$eikcoctl_statusmodel_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_STATUSLAYOUT_DURABLE_LOG_V1' \
    "$eikcoctl_statusmodel_source")" -eq 1
for eikcoctl_layout_stage in \
    B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF \
    C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB \
    D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B6${eikcoctl_layout_stage}u" \
        "$eikcoctl_statusmodel_source")" -eq 1
done
test "$(grep -c 'HTCLEO_EIKCOCTL_MATRIXMENU_STATUSTREE_LAYOUT_DURABLE_LOG_V1' \
    "$eikcoctl_statusmodel_source")" -eq 1
for eikcoctl_tree_layout_stage in \
    E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA F0 F1 F2 F3 F4 F5
do
    test "$(grep -c "HtcleoStatusPaneLog(0x0000B6${eikcoctl_tree_layout_stage}u" \
        "$eikcoctl_statusmodel_source")" -eq 1
done
test "$(grep -c 'position <= (htcleoEikAppInfoCapacity - 128)' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'position <= (htcleoStatusPaneCapacity - 128)' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'position <= (htcleoStatusPaneCapacity - 128)' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(statusPaneConstructResult)' \
    "$eikcoctl_statuspane_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(statusModelConstructResult)' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(statusLayoutConstructResult)' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(statusTreeConstructResult)' \
    "$eikcoctl_statusmodel_source")" -eq 1
test "$(grep -c 'CCoeEnv::Static()->ReadResourceAsDes8L' \
    "$eikcoctl_source")" -ge 1
test "$(grep -c 'iExtension->ReadAppInfoResourceExtensionL' \
    "$eikcoctl_source")" -eq 1
test "$(grep -c 'iMenuBar->ConstructL' "$eikcoctl_source")" -ge 1
test "$(grep -c 'iStatusPane = CEikStatusPane::NewL' \
    "$eikcoctl_source")" -ge 1
test "$(grep -c 'CAknSgcClient::HandleChangeL();' \
    "$eikcoctl_source")" -ge 2
test "$(grep -c 'iExtension->iCba = CEikButtonGroupContainer::NewL' \
    "$eikcoctl_source")" -eq 1
! grep -q 'file.Flush();\|User::After\|HalFunction' "$eikcoctl_source"
test "$(grep -c 'HTCLEO_FEATMGR_AKNCAP_TRACE_V1' \
    "$featmgr_source")" -eq 1
test "$(grep -c 'HTCLEO_FEATMGR_AKNCAP_TRACE_V1_HEADER' \
    "$featmgr_header")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_FEATMGR_AKNCAP_TRACE__' \
    "$featmgr_mmp")" -eq 1
test "$(grep -h 'HtcleoFeatMgrAknCapTrace(0xE5' \
    "$featmgr_source" "$featmgr_tls_source" "$featmgr_client_source" | \
    sed -n 's/.*Trace(0x\(E[0-9A-F][0-9A-F][0-9A-F]\)u.*/\1/p' | \
    sort -u | wc -l)" -eq 30
test "$(grep -c '(void)RProperty::Set(' "$featmgr_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId != KHtcleoFeatMgrTraceCategory.iUid' \
    "$featmgr_source")" -eq 1
test "$(grep -c 'User::WaitForRequest( stat )' \
    "$featmgr_client_source")" -eq 1
! grep -q 'AKNCAP.TXT\|User::After\|HalFunction' \
    "$featmgr_source" "$featmgr_tls_source" "$featmgr_client_source"
test "$(grep -c 'HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE_V1' \
    "$featmgrserver_startup_source")" -eq 1
test "$(grep -c 'HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE_V1_HEADER' \
    "$featmgrserver_header")" -eq 1
test "$(grep -c 'HTCLEO_FEATMGRSERVER_DEEPEST_STAGE_PRESERVE_V2' \
    "$featmgrserver_startup_source")" -eq 1
test "$(grep -c 'HTCLEO_FEATMGRSERVER_LOADPLUGINS_TRACE_V1' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c 'HTCLEO_FEATMGRSERVER_ZERO_PLUGIN_COMPAT_V1' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c '#include <ecom/ecomerrorcodes.h>' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c 'listResult == KEComErrNoInterfaceIdentified' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE__' \
    "$featmgrserver_mmp")" -eq 1
test "$(grep -h 'HtcleoFeatMgrServerTrace(0xE6' \
    "$featmgrserver_startup_source" "$featmgrserver_source" | \
    sed -n 's/.*Trace(0x\(E[0-9A-F][0-9A-F][0-9A-F]\)u.*/\1/p' | \
    sort -u | wc -l)" -eq 49
test "$(grep -c 'iRegistry = CFeatMgrFeatureRegistry::NewL(iFs, \*this);' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c 'TFileName temp(iRegistry->GetFeaturesFilePathAndName());' \
    "$featmgrserver_source")" -eq 1
test "$(grep -c 'const TInt serverTraceRead = RProperty::Get(' \
    "$featmgr_client_source")" -eq 1
test "$(grep -c 'const TInt serverTraceRead = RProperty::Get(' \
    "$featmgrserver_startup_source")" -eq 1
test "$(grep -c 'serverTraceStage < 0xE610u || serverTraceStage > 0xE64Fu' \
    "$featmgrserver_startup_source")" -eq 1
test "$(grep -c 'serverStage >= 0xE600u && serverStage <= 0xE64Fu' \
    "$featmgr_client_source")" -eq 1
test "$(grep -c 'TRAP(listResult,' "$featmgrserver_source")" -eq 2
test "$(grep -c 'User::LeaveIfError(listResult);' \
    "$featmgrserver_source")" -eq 1
! grep -q 'AKNCAP.TXT\|User::After\|HalFunction' \
    "$featmgrserver_startup_source" "$featmgrserver_source"
for stem_list in \
    stem_uiservicescmdlist.rss \
    stem_criticalappscmdlist.rss \
    stem_noncriticalcmdlist.rss \
    stem_shutdowncmdlists.rss
do
    test "$(grep -c 'HTCLEO_NO_COOPERATING_SYSTEM_STATE_CHANGE' \
        "$stem_startup_dir/$stem_list")" -eq 1
    ! grep -q '^[[:space:]]*r_cmd_sastate,' "$stem_startup_dir/$stem_list"
    test "$(grep -c 'RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_sastate' \
        "$stem_startup_dir/$stem_list")" -eq 1
done
test "$(grep -c 'HTCLEO_LOCAL_NORMAL_STARTUP_MODE' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
! grep -q '^[[:space:]]*r_cmd_startupmode,' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss"
test "$(grep -c '^[[:space:]]*r_cmd_htcleo_startupmode,' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -c '^[[:space:]]*r_cmd_htcleo_startupreason,' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -c 'RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupmode' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -c 'RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupreason' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -c 'RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_startupmode' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -c 'HTCLEO_NO_STARTUP_SPLASHSCREEN' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
! grep -q '^[[:space:]]*r_cmd_splash,' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss"
test "$(grep -c 'RESOURCE SSM_START_PROCESS_INFO r_cmd_splash' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -F -c 'name = "Z:\\sys\\bin\\splashscreen.exe";' \
    "$stem_startup_dir/stem_uiservicescmdlist.rss")" -eq 1
test "$(grep -R -Fh 'C:\\Symbian3\\SSMLOG.TXT' \
    "$ssm_component/ssm/src" | wc -l)" -eq 1
test "$(grep -R -Fh 'C:\\Symbian3\\CLELOG.TXT' \
    "$ssm_component/cle/src" | wc -l)" -eq 1
test "$(grep -c 'HTCLEO_WSERV_DURABLE_LOG_V1' "$wserv_main")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_CLIENT_WINDOW_CREATE_TRACE_V1' \
    "$wserv_client_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_CLIENT_WINDOW_CONSTRUCT_TRACE_V1' \
    "$wserv_client_window_source")" -eq 1
test "$(grep -h -c 'aClient->SecureId().iId' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -h -c '0x00000430u' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -h -c '0x00000431u' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -h -c '0x00000432u' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -h -c 'HTCLEO_WSERV_ARMED_REQUEST_TRACE_V2' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -h -c 'htcleoHandleResult != KErrNotFound' \
    "$wserv_client_source" "$wserv_client_window_source" | \
    awk '{ total += $1 } END { print total }')" -eq 2
test "$(grep -c 'HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V2' \
    "$wserv_client_source")" -eq 1
test "$(grep -c 'htcleoMatrixMenuTraceCount < 32' \
    "$wserv_client_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_MATRIXMENU_FATAL_COMPLETION_V1' \
    "$wserv_client_source")" -eq 1
for wserv_buffer_stage in 0440 0441 0442 0443 0444 0445
do
    test "$(grep -c "0x0000${wserv_buffer_stage}u" \
        "$wserv_client_source")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_TYPE2A_POINTER_ENABLE_V1' \
    "$wserv_pointer_source")" -eq 1
test "$(grep -c 'iXyInputType = EXYInputPointer' \
    "$wserv_pointer_source")" -eq 1
for wserv_pointer_stage in 0450 0451
do
    test "$(grep -ci "0x0000${wserv_pointer_stage}u" \
        "$wserv_pointer_source")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_TYPE2A_RAW_RECEIVER_TRACE_V1' \
    "$wserv_event_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_TYPE2A_HITTEST_TRACE_V1' \
    "$wserv_pointer_source")" -eq 1
for wserv_raw_stage in 0452 0453 0454
do
    test "$(grep -ci "0x0000${wserv_raw_stage}u" \
        "$wserv_event_source")" -eq 1
done
for wserv_hit_stage in 0458 0459
do
    test "$(grep -ci "0x0000${wserv_hit_stage}u" \
        "$wserv_pointer_source")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_V2' \
    "$wserv_event_header")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_IMPL_V2' \
    "$wserv_event_source")" -eq 1
for wserv_hook_stage in 045A 045B 045C 045D 045E 045F 0460 0461 \
    0462 0463 0464 0465
do
    test "$(grep -ci "0x0000${wserv_hook_stage}u" \
        "$wserv_event_source")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_RUNL_TRACE_BOUND_V1' \
    "$wserv_event_source")" -eq 1
test "$(grep -c 'htcleoRunLTraceCount < 32' \
    "$wserv_event_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK_V1' \
    "$wserv_rootwin_source")" -eq 1
for wserv_absrect_stage in 0466 0467
do
    test "$(grep -ci "0x0000${wserv_absrect_stage}u" \
        "$wserv_rootwin_source")" -eq 1
done
test "$(grep -c 'htcleoWin->AbsRect().Contains(aInPos)' \
    "$wserv_rootwin_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK_V1' \
    "$wserv_rootwin_source")" -eq 1
for wserv_published_stage in 0468 0469
do
    test "$(grep -ci "0x0000${wserv_published_stage}u" \
        "$wserv_rootwin_source")" -eq 1
done
test "$(grep -c 'iHandle(aHandle), iFound(NULL)' \
    "$wserv_walkwindowtree_header")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE_V1' \
    "$wserv_client_window_source")" -eq 1
for wserv_capture_stage in 046A 046B
do
    test "$(grep -h -ci "0x0000${wserv_capture_stage}u" \
        "$wserv_client_window_source" "$wserv_rootwin_source" | \
        awk '{ total += $1 } END { print total }')" -eq 1
done
test "$(grep -c 'gHtcleoPublishedGridWindow==this' \
    "$wserv_client_window_source")" -eq 1
test "$(grep -h -c 'HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1' \
    "$wserv_client_source" "$wserv_client_window_source" \
    "$mmwidgets_grid_source" "$matrixmenu_appui_source" | \
    awk '{ total += $1 } END { print total }')" -eq 4
for wserv_teardown_stage in 046C 046D
do
    test "$(grep -h -ci "0x0000${wserv_teardown_stage}u" \
        "$wserv_client_source" "$wserv_client_window_source" | \
        awk '{ total += $1 } END { print total }')" -eq 1
done
test "$(grep -ci '0x4D570182u' "$mmwidgets_grid_source")" -eq 1
for matrixmenu_teardown_stage in 1250 1251 1252 1253 1254 1255
do
    test "$(grep -ci "0x4D4D${matrixmenu_teardown_stage}u" \
        "$matrixmenu_appui_source")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY_V1' \
    "$wserv_client_source")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_TOUCH_ONLY_LOG_V1' \
    "$wserv_main")" -eq 1
test "$(grep -c 'aStage >= 0x0000045Au && aStage <= 0x00000465u' \
    "$wserv_main")" -eq 1
test "$(grep -c 'aStage >= 0x0000046Cu && aStage <= 0x00000476u' \
    "$wserv_main")" -eq 1
test "$(grep -ci '0x0000046Eu' "$wserv_client_source")" -eq 1
test "$(grep -ci '0x0000046Fu+' "$wserv_client_source")" -eq 1
test "$(grep -c 'htcleoCategoryIndex<8' "$wserv_client_source")" -eq 1
test "$(grep -c 'HTCLEO_TYPE2A_DIGITISER_HAL_V1' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'EHalGroupDigitiser, DigitiserHal' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'HTCLEO_TYPE2A_DUAL_HAL_COMPAT_V1' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'EHalGroupMouse, MouseHal' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'HTCLEO_TYPE2A_RAW_PACKET_SNAPSHOT_V1' \
    "$htcleo_touch_source")" -eq 1
for touch_hal_function in 6 7 8 9
do
    test "$(grep -c "case ${touch_hal_function}:" \
        "$htcleo_touch_source")" -eq 1
done
for touch_hal_function in 10 11 12 13 14 15 16 17 18 19 20
do
    test "$(grep -c "case ${touch_hal_function}:" \
        "$htcleo_touch_source")" -eq 1
done
test "$(grep -c 'HTCLEO_TYPE2A_FOCUS_REARM_V1' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'HTCLEO_TYPE2A_FOCUS_REARM_DELAYED_V2' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'KTouchFocusRearmDelayPolls = 25u' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'gHtcleoTouchRearmPending' \
    "$htcleo_touch_source")" -eq 4
test "$(grep -c 'gHtcleoTouchRearmDelay' \
    "$htcleo_touch_source")" -eq 6
test "$(grep -c '__e32_atomic_store_rel32(' \
    "$htcleo_touch_source")" -eq 2
test "$(grep -c '__e32_atomic_load_acq32(' \
    "$htcleo_touch_source")" -eq 5
touch_hal_rearm_block=$(sed -n \
    '/static TInt TouchDiagnosticHal/,/class DHtcleoTouch/p' \
    "$htcleo_touch_source")
! printf '%s\n' "$touch_hal_rearm_block" | \
    grep -q 'HtcleoI2c\|NanoWait\|iTimer\|iPollDfc'
touch_poll_rearm_block=$(sed -n \
    '/HTCLEO_TYPE2A_FOCUS_REARM_V1/,/EMouseHalSetMouseState controls/p' \
    "$htcleo_touch_source")
printf '%s\n' "$touch_poll_rearm_block" | grep -q 'HtcleoI2cWrite'
! printf '%s\n' "$touch_poll_rearm_block" | \
    grep -q 'ResetAndDetect\|NanoWait\|iTimer.Cancel\|iPollDfc.Cancel'
test "$(grep -c 'HTCLEO_TYPE2A_IRQ_READY_GATED_POLL_V1' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'HtcleoGpioRead(92u, irqHigh)' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'gHtcleoTouchReadyReads' \
    "$htcleo_touch_source")" -eq 4
test "$(grep -c 'gHtcleoTouchNotReadySkips' \
    "$htcleo_touch_source")" -eq 4
test "$(grep -c 'self->Sample();' "$htcleo_touch_source")" -eq 3
test "$(grep -c 'HTCLEO_TYPE2A_HIGH_LEVEL_FALLBACK_V1' \
    "$htcleo_touch_source")" -eq 1
test "$(grep -c 'KTouchHighFallbackPolls = 10u' \
    "$htcleo_touch_source")" -eq 1
for touch_fallback_evidence in \
    'gHtcleoTouchEvents != eventsBefore' \
    'gHtcleoTouchRawTransitions != transitionsBefore' \
    'gHtcleoTouchPoints != 0u' \
    '0x54000406u' '0x54000407u'
do
    grep -Fq "$touch_fallback_evidence" "$htcleo_touch_source"
done
touch_ready_poll_block=$(sed -n \
    '/HTCLEO_TYPE2A_IRQ_READY_GATED_POLL_V1/,/TInt timerResult = self->iTimer.Again/p' \
    "$htcleo_touch_source")
printf '%s\n' "$touch_ready_poll_block" | \
    grep -F -q 'else if (!irqHigh)'
printf '%s\n' "$touch_ready_poll_block" | \
    grep -F -q 'HtcleoTouchTrace(0x54000404u, KErrNone,'
! printf '%s\n' "$touch_ready_poll_block" | \
    grep -q 'HalFunction\|User::After\|ResetAndDetect\|iTimer.Cancel'
test "$(grep -c '^EPen=1$' "$htcleo_hal_values")" -eq 1
test "$(grep -c '^EPenX=480$' "$htcleo_hal_values")" -eq 1
test "$(grep -c '^EPenY=800$' "$htcleo_hal_values")" -eq 1
test "$(grep -c 'TRAPD(htcleoCommandError,' \
    "$wserv_client_source")" -eq 1
test "$(grep -c 'User::Leave(htcleoCommandError);' \
    "$wserv_client_source")" -eq 1
for wserv_client_stage in 0400 0401 0402 0403 0404 0405 0406 0407 \
    0410 0411 0412 0413 0414 0415 0416 0417 0418 0419 041A 041B 041C 041D \
    0420 0421
do
    test "$(grep -h -c "0x0000${wserv_client_stage}u" \
        "$wserv_client_source" "$wserv_client_window_source" | \
        awk '{ total += $1 } END { print total }')" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_LOG_CAPACITY_512_V1' "$wserv_main")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_LOG_RING_1M_V1' "$wserv_main")" -eq 1
test "$(grep -c 'KCapacity = 1048576' "$wserv_main")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT_V1' "$wserv_event_source")" -eq 1
! grep -q 'gHtcleoWsLogSequence >= 96' "$wserv_main"
test "$(grep -c 'HTCLEO_WSERV_PLUGIN_PROGRESS_V2' "$wserv_plugin_manager")" -eq 1
for wserv_plugin_stage in \
    40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F \
    50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F \
    60 61 62 63 64 6A
do
    test "$(grep -c "0x000000${wserv_plugin_stage}u" "$wserv_plugin_manager")" -eq 1
done
test "$(grep -c 'HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_SCREEN' \
    "$wserv_screen")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_REDRAW' \
    "$wserv_screen_redraw")" -eq 1
test "$(grep -c 'HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_MANAGER' \
    "$wserv_render_stage_manager")" -eq 1
test "$(grep -c 'HtcleoWsLog(0x000001' "$wserv_screen")" -eq 21
test "$(grep -c 'HtcleoWsLog(0x000002' "$wserv_screen_redraw")" -eq 11
test "$(grep -c 'HtcleoWsLog(0x000003' "$wserv_render_stage_manager")" -eq 17
test "$(grep -c 'C:\\\\Symbian3\\\\WSLOG.TXT' "$wserv_main")" -eq 1
test "$(grep -c 'MACRO             __HTCLEO_WSERV_DURABLE_LOG__' \
    "$wserv_mmp")" -eq 1
test "$(grep -c '#include <graphics/wsgraphicdrawerinterface.h>' \
    "$wserv_case_wrapper")" -eq 1
test "$(grep -c '#include <Graphics/windowserverconstants.h>' \
    "$wserv_constants_wrapper")" -eq 1
! grep -q 'TRegion::iCount\|TRegion::iAllocedRects' "$wserv_wstypes"
test "$(grep -c 'HTCLEO_DISPLAY_DURABLE_LOG_V1' "$display_plugin")" -eq 1
test "$(grep -R -Fh 'C:\\Symbian3\\DSPRLOG.TXT' \
    "$display_component/src" | wc -l)" -eq 1
test "$(grep -c 'macro __HTCLEO_DISPLAY_DURABLE_LOG__' "$display_mmp")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_CPU_FRAME_LOOP_V1' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_FLICKER_CPU_FRAMEBUFFER_EXPORT_V1' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT_V1' \
    "$display_fb_stage")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_BUILD_V1' \
    "$display_mmp")" -eq 1
test "$(grep -c 'macro __HTCLEO_CPU_FRAMEBUFFER_BLIT__' \
    "$display_mmp")" -eq 1
test "$(grep -c 'SgUtils::TransferPixels' "$display_stage")" -eq 2
test "$(grep -c 'UserSvr::ScreenInfo' "$display_stage")" -eq 1
test "$(grep -c 'UserSvr::HalFunction' "$display_stage")" -eq 1
test "$(grep -c 'EDisplayHalWsSwitchOnScreen' "$display_stage")" -eq 1
! grep -q 'RDisplayChannel displayChannel' "$display_stage"
for display_cpu_stage in 1900 1901 1902 1903 1904 1905 1906 1907 1908 1909
do
    test "$(grep -c "0x0000${display_cpu_stage}u" \
        "$display_stage")" -eq 1
done
for display_cpu_loop_stage in 1910 1911
do
    test "$(grep -c "0x0000${display_cpu_loop_stage}u" \
        "$display_stage")" -eq 1
done
test "$(grep -c 'iOpenWfcWrapper->Begin(aRegion);' "$display_stage")" -eq 1
test "$(grep -c 'iOpenWfcWrapper->End();' "$display_stage")" -eq 2
test "$(grep -c 'HtcleoCpuFramebufferBlit(' "$display_stage")" -eq 2
test "$(grep -c 'HtcleoCpuFramebufferBlit(' "$display_fb_stage")" -eq 2
for display_flicker_cpu_stage in 1920 1921
do
    test "$(grep -c "0x0000${display_flicker_cpu_stage}u" \
        "$display_fb_stage")" -eq 1
done
test "$(grep -c 'HTCLEO_DISPLAY_FRAME_SIGNATURE_TRACE_V1' \
    "$display_stage")" -eq 1
for display_signature_stage in 1930 1931
do
    test "$(grep -c "0x0000${display_signature_stage}u" \
        "$display_stage")" -eq 1
done
test "$(grep -c 'HTCLEO_DSPR_LOG_CAPACITY_2048_V1' \
    "$display_plugin")" -eq 1
test "$(grep -c 'position < (2048 \* 42)' \
    "$display_plugin")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_REGION_AWARE_BLIT_V1' \
    "$display_stage")" -eq 1
test "$(grep -c '0x00001932u' "$display_stage")" -eq 1
test "$(grep -c 'aUpdateRegion->RectangleList()' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_FRAME_STAGE_CORRELATION_V1' \
    "$display_stage")" -eq 1
test "$(grep -c '0x00001933u' "$display_stage")" -eq 1
test "$(grep -c '0x7F4D5702u' "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V3' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT_V1' \
    "$display_plugin")" -eq 1
test "$(grep -c '(aStage & 0xFFFFu) != 0x1000u' \
    "$display_plugin")" -eq 1
test "$(grep -c '0x00001934u' "$display_stage")" -eq 1
test "$(grep -c '0x4D4D1013u' "$display_stage")" -eq 1
test "$(grep -c 'htcleoSourceNonWhite == 0u' "$display_stage")" -eq 1
test "$(grep -c 'htcleoDestinationBeforeNonWhite > 0u' \
    "$display_stage")" -eq 1
test "$(grep -c 'htcleoBounds.Size() == TSize(360, 640)' \
    "$display_stage")" -eq 1
test "$(grep -c 'htcleoRectCount == 2' "$display_stage")" -eq 1
test "$(grep -c '(htcleoRectCount == 1 || htcleoRectCount == 2)' \
    "$display_stage")" -eq 1
test "$(grep -c 'htcleoBounds.Size() == TSize(480, 800)' \
    "$display_stage")" -eq 1
test "$(grep -c 'HTCLEO_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1' \
    "$matrixmenu_logger_source")" -eq 1
test "$(grep -c '0x7F4D5702u' "$matrixmenu_logger_source")" -eq 1
test "$(grep -c 'HTCLEO_EIKCORE_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1' \
    "$eikcore_source")" -eq 1
test "$(grep -c '0x7F4D5702u' "$eikcore_source")" -eq 1
test "$(grep -c '(void)RProperty::Set(' "$eikcore_source")" -eq 2
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' "$display_mmp")" -eq 1
! grep -q 'position < (256 \* 42)' "$display_plugin"
! grep -R -q 'gHtcleoDspr' "$display_component/src"
for display_stage_id in 00001001 00001031 00001104 00001212 \
    00001320 00001516 00001614 00001705 00001805 00001828
do
    test "$(grep -R -c "0x${display_stage_id}u" \
        "$display_component/src" | awk -F: '{sum += $2} END {print sum + 0}')" -eq 1
done
test -s "$wfc_logger"
test -s "$wfc_header"
test "$(grep -c 'HTCLEO_WFC_CONTEXT_DURABLE_LOG_V1' "$wfc_logger")" -eq 1
test "$(grep -R -Fh 'C:\\Symbian3\\WFCLOG.TXT' \
    "$wfc_component/composition/src" | wc -l)" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_WFC_CONTEXT_LOG__' \
    "$wfc_mmp")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__KHRONOS_TYPES_H__' "$wfc_mmp")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*WFC_API_CALL=EXPORT_C' \
    "$wfc_mmp")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*SUPPORT_565_OUTPUT' "$wfc_mmp")" -eq 1
! grep -q 'OPTION[[:space:]]*GCCE[[:space:]]*-fvisibility=default' "$wfc_mmp"
test "$(grep -c 'SOURCE[[:space:]]*htcleowfclog.cpp' "$wfc_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' "$wfc_mmp")" -eq 1
test "$(grep -c 'position < (256 \* 42)' "$wfc_logger")" -eq 1
test "$(grep -c 'HTCLEO_OWF_DISPCTX_TYPEDEF_COMPAT_V1' \
    "$wfc_image_header")" -eq 1
test "$(grep -c 'HTCLEO_OWF_DISPCTX_TYPEDEF_COMPAT_V1' \
    "$wfc_display_header")" -eq 1
test "$(grep -c 'HTCLEO_WFC_NATIVE_STREAM_TYPEDEF_COMPAT_V1' \
    "$wfc_stream_header")" -eq 1
for wfc_stage_id in 00002000 00002033 00002100 00002105 \
    00002200 00002233 00002300 00002316
do
    test "$(grep -R -c "0x${wfc_stage_id}u" \
        "$wfc_context" "$wfc_display_context" "$wfc_screen" "$wfc_stream" | \
        awk -F: '{sum += $2} END {print sum + 0}')" -eq 1
done
! grep -q 'User::After' "$wfc_context" "$wfc_display_context" \
    "$wfc_screen" "$wfc_stream" "$wfc_logger"
test "$(grep -c 'HTCLEO_NVG_DURABLE_LOG_V2' "$nvg_plugin")" -eq 1
! grep -q 'gHtcleoNvgLog' "$nvg_plugin"
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_NVG_DURABLE_LOG__' \
    "$nvg_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' "$nvg_mmp")" -eq 1
test "$(grep -R -Fh 'C:\\Symbian3\\NVGLOG.TXT' \
    "$nvg_component/src" | wc -l)" -eq 1
for nvg_stage_id in \
    01 02 10 11 20 21 30 31 40 41 42 43 50 51 52 53 54 55 56 57 58
do
    test "$(grep -R -c "0x000000${nvg_stage_id}u" \
        "$nvg_component/src" | awk -F: '{sum += $2} END {print sum + 0}')" -eq 1
done
test "$(grep -R -c '0xE0000020u' "$nvg_component/src" | \
    awk -F: '{sum += $2} END {print sum + 0}')" -eq 1
! grep -R -q 'User::After' "$nvg_plugin" "$nvg_factory" "$nvg_stage"
test "$(grep -c 'HTCLEO_ECOM_CLIENT_DURABLE_LOG_V1' "$ecom_logger")" -eq 1
test "$(grep -h -c 'HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1' \
    "$ecom_logger_header" "$ecom_logger" "$ecom_session" \
    "$ecom_load_manager" "$ecom_unload_policy" | \
    awk '{sum += $1} END {print sum}')" -eq 5
test "$(grep -F -c 'C:\\Symbian3\\HSPSECOM.TXT' \
    "$ecom_logger")" -eq 1
test "$(grep -c '1048576 - 128' "$ecom_logger")" -eq 1
for ecom_hsps_client_stage in \
    700 701 702 703 704 705 706 707 \
    710 711 712 713 714 715 716 717 718 719 71A 71B 71C 71D \
    720 721 722 723 724 725 726 727 728 729 \
    730 731 732 733 734 735 736 737 738
do
    test "$(grep -h -ci "0x0000C${ecom_hsps_client_stage}u" \
        "$ecom_session" "$ecom_load_manager" "$ecom_unload_policy" | \
        awk '{sum += $1} END {print sum}')" -eq 1
done
test "$(grep -c 'HTCLEO_ECOM_LOG_CAPACITY_16384_V2' "$ecom_logger")" -eq 1
test "$(grep -c 'position < (16384 \* 45)' "$ecom_logger")" -eq 1
test "$(grep -c 'position / 45), EHex, 4' "$ecom_logger")" -eq 1
! grep -q 'position < (256 \* 43)' "$ecom_logger"
test "$(grep -c 'HTCLEO_ECOM_LIBRARY_LOAD_SPLIT_V2' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V6' \
    "$ecom_unload_policy")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_FEATMGR_LIST_TRACE_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HtcleoEcomLog(0x0000F2' "$ecom_session")" -eq 45
test "$(grep -c '0x10205054u' "$ecom_session")" -eq 3
test "$(grep -c '0x10205057u' "$ecom_session")" -eq 2
test "$(grep -c 'HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x101F4CD2u' \
    "$ecom_session")" -eq 2
test "$(grep -c 'htcleoSendResult == KErrServerTerminated' \
    "$ecom_session")" -eq 1
test "$(grep -c 'TRAPD(htcleoReconnectResult, ConstructL())' \
    "$ecom_session")" -eq 1
for ecom_matrixmenu_retry_stage in 10 11 12 13 14
do
    test "$(grep -ci "0x000003${ecom_matrixmenu_retry_stage}u" \
        "$ecom_session")" -eq 1
done
test "$(grep -c 'HTCLEO_ECOM_MATRIXMENU_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'htcleoUiShellList && error == KErrServerTerminated' \
    "$ecom_session")" -eq 1
test "$(grep -c 'htcleoUiShellListFailOpen && error == KErrServerTerminated' \
    "$ecom_session")" -eq 1
test "$(grep -c 'aInterfaceUid.iUid == 0x200286DFu' \
    "$ecom_session")" -eq 1
test "$(grep -c 'aInterfaceUid.iUid == 0x20019592u' \
    "$ecom_session")" -eq 2
test "$(grep -F -c 'htcleoHomeScreenResolverType.Compare(_L8("action")) == 0' \
    "$ecom_session")" -eq 1
test "$(grep -F -c 'htcleoHomeScreenResolverType.Compare(_L8("actions")) == 0' \
    "$ecom_session")" -eq 1
test "$(grep -F -c 'htcleoHomeScreenResolverType.Compare(_L8("event")) == 0' \
    "$ecom_session")" -eq 1
test "$(grep -c 'const TBool htcleoHomeScreenRenderingFactoryList' \
    "$ecom_session")" -eq 1
test "$(grep -F -c 'htcleoHomeScreenResolverType.Compare(_L8("menubar")) == 0' \
    "$ecom_session")" -eq 0
test "$(grep -c 'htcleoHomeScreenNonvisualFactoryList;' \
    "$ecom_session")" -eq 1
test "$(grep -c 'TRAPD(htcleoListReconnectResult, ConstructL())' \
    "$ecom_session")" -eq 1
test "$(grep -c 'error = KEComErrNoInterfaceIdentified' \
    "$ecom_session")" -eq 1
for ecom_matrixmenu_list_stage in 15 16 17 18 19 1A
do
    test "$(grep -ci "0x000003${ecom_matrixmenu_list_stage}u" \
        "$ecom_session")" -eq 1
done
test "$(grep -c 'HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK_V1' \
    "$ptiengine_source")" -eq 1
test "$(grep -c 'KPtiKeymappingsDefaultImplementation = 0x10281897' \
    "$ptiengine_source")" -eq 1
test "$(grep -c 'dataImpl.AppendL(KPtiKeymappingsDefaultImplementation)' \
    "$ptiengine_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x101F4CD2u' \
    "$ptiengine_source")" -eq 1
test "$(grep -c 'TRAP(htcleoFactoryResult,' "$ptiengine_source")" -eq 1
test "$(grep -c 'CleanupStack::PopAndDestroy(&dataImpl)' \
    "$ptiengine_source")" -eq 1
grep -q 'library[[:space:]]*euser.lib bafl.lib efsrv.lib ecom.lib estor.lib' \
    "$ptiengine_mmp"
! grep -q 'EUSER.LIB\|BAFL.LIB\|EFSRV.LIB\|ECOM.LIB\|ESTOR.LIB' \
    "$ptiengine_mmp"
test "$(grep -c 'MACRO __HTCLEO_ECOM_CLIENT_DURABLE_LOG__' "$ecom_mmp")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*HtcleoEcomLog.cpp' "$ecom_mmp")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_SERVER_FEATMGR_LIST_TRACE_V1' \
    "$ecom_server_start")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_SERVER_DURABLE_LOG_V1' \
    "$ecom_server_logger")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_SERVER_EXACT_REQUEST_ARM_V2' \
    "$ecom_server_logger")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_SERVER_LOG_CAPACITY_16384_V2' \
    "$ecom_server_logger")" -eq 1
test "$(grep -c 'position < (16384 \* 45)' \
    "$ecom_server_logger")" -eq 1
test "$(grep -c 'position / 45), EHex, 4' \
    "$ecom_server_logger")" -eq 1
! grep -q 'position < (256 \* 43)' "$ecom_server_logger"
test "$(grep -c 'HTCLEO_ECOM_SERVER_EXACT_REQUEST_ARM_V2' \
    "$ecom_server_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_SERVER_REGISTRY_LIST_TRACE_V3' \
    "$ecom_server_registry_data")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_FEATUREINFO_EMPTY_LIST_COMPAT_V1' \
    "$ecom_server_registry_data")" -eq 1
test "$(grep -c '0x0000F401u' "$ecom_server_registry_data")" -eq 1
test "$(grep -c 'aInterfaceUid.iUid == 0x10205057u' \
    "$ecom_server_registry_data")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\ECOMSRV.TXT' \
    "$ecom_server_logger")" -eq 2
test "$(grep -c 'if(!gHtcleoEcomServerArmed)' \
    "$ecom_server_logger")" -eq 1
test "$(grep -c 'HtcleoEcomServerArm();' \
    "$ecom_server_session")" -eq 2
test "$(grep -c 'HtcleoEcomServerDisarm();' \
    "$ecom_server_session")" -eq 1
test "$(grep -R -h -o '0x10009D92u' \
    "$ecom_server_session" "$ecom_server_source" | wc -l)" -eq 2
test "$(grep -c 'MACRO __HTCLEO_ECOM_SERVER_DURABLE_LOG__' \
    "$ecom_server_mmp")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*HtcleoEcomServerLog.cpp' \
    "$ecom_server_mmp")" -eq 1
test "$(grep -R -h -o 'HtcleoEcomServerLog(0x0000F3[0-9A-F][0-9A-F]u' \
    "$ecom_server_start" "$ecom_server_session" "$ecom_server_source" \
    "$ecom_server_rom_resolver" "$ecom_server_default_resolver" \
    "$ecom_server_transaction" | wc -l)" -eq 146
test "$(grep -c 'HtcleoEcomServerLog(0x0000F3\|HtcleoEcomServerLog(0x0000F400u' \
    "$ecom_server_registry_data")" -eq 33
test "$(grep -R -h -o '0x10205057u' \
    "$ecom_server_session" "$ecom_server_source" \
    "$ecom_server_rom_resolver" "$ecom_server_default_resolver" \
    "$ecom_server_transaction" | wc -l)" -eq 6
! grep -q 'User::After\|HalFunction' "$ecom_server_logger"
test "$(grep -R -Fh 'C:\\Symbian3\\ECOMLOG.TXT' \
    "$ecom_component/frame" | wc -l)" -eq 1
test "$(grep -R -c 'HtcleoEcomLog(0x00000' \
    "$ecom_session" "$ecom_load_manager" "$ecom_unload_policy" \
    "$ecom_component/frame/loadmanager.inl" | \
    awk -F: '{sum += $2} END {print sum + 0}')" -eq 104
for ecom_load_split_stage in 1 2 3 4 5 6 7 8 9
do
    test "$(grep -c "0x0000080${ecom_load_split_stage}u" \
        "$ecom_unload_policy")" -eq 1
done
for ecom_init_stage in 1 2 3 4 5 6 7 8 9
do
    test "$(grep -c "0x0000090${ecom_init_stage}u" \
        "$ecom_unload_policy")" -eq 1
done
test "$(grep -c '0x00000910u' "$ecom_unload_policy")" -eq 1
test "$(grep -c '0x00000911u' "$ecom_unload_policy")" -eq 1
for ecom_attach_watch_stage in 00 01 02 04
do
    test "$(grep -c "0x00000a${ecom_attach_watch_stage}u" \
        "$ecom_unload_policy")" -eq 1
done
test "$(grep -c '0x00000a03u' "$ecom_unload_policy")" -eq 2
test "$(grep -c '0x00000a05u' "$ecom_unload_policy")" -eq 2
test "$(grep -c '0x00000a10u + step' "$ecom_unload_policy")" -eq 1
test "$(grep -c '0x0000b000u' "$ecom_unload_policy")" -eq 1
test "$(grep -c '0x0000b006u' "$ecom_unload_policy")" -eq 1
test "$(grep -c '0x0000b100u + (TUint32)phase' \
    "$ecom_unload_policy")" -eq 1
test "$(grep -c '0x0000b200u + (TUint32)phase' \
    "$ecom_unload_policy")" -eq 1
test "$(grep -c 'HtcleoNvgAttachBootstrap(' \
    "$ecom_unload_policy")" -eq 2
test "$(grep -c 'HtcleoNvgLibraryAttachExec' \
    "$ecom_unload_policy")" -eq 4
test "$(grep -c 'if(attachResult != KErrNone)' \
    "$ecom_unload_policy")" -eq 1
grep -q '0x42000100u' "$ecom_unload_policy"
grep -q '0xa0b60000u' "$ecom_unload_policy"
test "$(grep -c 'asm("bx pc")' "$ecom_unload_policy")" -eq 2
test "$(grep -c 'asm(".code 32")' "$ecom_unload_policy")" -eq 2
test "$(grep -c 'asm(".code 16")' "$ecom_unload_policy")" -eq 2
test "$(grep -c 'HtcleoNvgAttachTraceStart(' "$ecom_unload_policy")" -eq 2
test "$(grep -c 'HtcleoNvgAttachTraceStop(' "$ecom_unload_policy")" -eq 4
! grep -q 'HtcleoNvgAttachTraceObserve\|iObserve' "$ecom_unload_policy"
test "$(grep -c 'iThread.SetPriority(EPriorityMuchLess)' \
    "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelNotify.CreateLocal(0)' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelNotify.Wait()' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelNotify.Signal()' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelAck.CreateLocal(0)' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelAck.Signal()' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelNotify.Handle()' "$ecom_unload_policy")" -eq 1
test "$(grep -c 'iKernelAck.Handle()' "$ecom_unload_policy")" -eq 1
grep -q 'KMaxLibraryEntryPoints + 3' "$ecom_unload_policy"
grep -q '0x484c3432u' "$ecom_unload_policy"
grep -q 'EExecLibraryAttach = 159' \
    "$full_epocroot/epoc32/include/platform/exec_enum.h"
grep -q 'EExecLibraryAttached = 160' \
    "$full_epocroot/epoc32/include/platform/exec_enum.h"
! grep -q 'User::After' "$ecom_logger"
test "$(grep -c 'HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG_V1' \
    "$stem_backend_source")" -eq 1
test "$(grep -c 'MACRO __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__' \
    "$stem_backend_mmp")" -eq 1
test "$(grep -c 'HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_V1' \
    "$stem_backend_source")" -eq 1
test "$(grep -c 'MACRO __HTCLEO_STEM_BACKEND_TIMEZONE_DEFER__' \
    "$stem_backend_mmp")" -eq 1
test "$(grep -c 'HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_MMP_V1' \
    "$stem_backend_mmp")" -eq 1
test "$(grep -c 'MACRO SYMBIAN_OE_POSIX_SIGNALS' \
    "$stem_backend_mmp")" -eq 1
test "$(grep -c 'MACRO SYMBIAN_OE_LIBRT' "$stem_backend_mmp")" -eq 1
test "$(grep -c 'HTCLEO_STEM_BACKEND_FINDTIMER_EXPORT_FIX_V1' \
    "$stem_backend_header")" -eq 1
test "$(grep -c 'HtcleoStemBackendLog(0x0000D1' \
    "$stem_backend_source")" -eq 37
for stem_backend_stage in $(seq 1 36)
do
    stage_hex=$(printf '%02X' "$stem_backend_stage")
    test "$(grep -c "0x0000D1${stage_hex}u" \
        "$stem_backend_source")" -eq 1
done
test "$(grep -c '0x0000D125u' "$stem_backend_source")" -eq 1
test "$(grep -c 'err == KErrNotFound || err == KErrServerTerminated' \
    "$stem_backend_source")" -eq 1
test "$(grep -c 'iTzServer.Close();' "$stem_backend_source")" -eq 2
test "$(grep -A10 'HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_V1' \
    "$stem_backend_source" | grep -c 'err = KErrNone;')" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\ECOMLOG.TXT' \
    "$stem_backend_source")" -eq 1
! sed -n '/HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG_V1/,/^#endif$/p' \
    "$stem_backend_source" | grep -q 'User::After\|User::WaitForRequest'
test "$(grep -c 'HTCLEO_HITCHCOCK_ENTRYPOINT_DURABLE_LOG_V1' \
    "$hitchcock_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_HITCHCOCK_ENTRYPOINT_LOG__' \
    "$hitchcock_mmp")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*htcleohitchcockentrytrace.cpp' \
    "$hitchcock_mmp")" -eq 1
test "$(grep -c '__wrap__E32Dll_Body(TInt aReason)' \
    "$hitchcock_source")" -eq 1
test "$(grep -c 'HtcleoHitchcockAttachLog(0x0000CC0' \
    "$hitchcock_source")" -eq 6
! grep -q 'NOSTRICTDEF' "$hitchcock_mmp"
! grep -q 'User::After\|User::WaitForRequest\|HalFunction\|UDF' \
    "$hitchcock_source"
grep -Fq 'htcleo-gcce-hitchcock-cc-wrapper.sh' \
    "$hitchcock_config_path/hitchcock-gcce.xml"
grep -Fq -- '--wrap=_E32Dll_Body' \
    "$hitchcock_config_path/hitchcock-gcce.xml"
! grep -q 'User::After' \
    "$ssm_component/ssm/src/main.cpp" \
    "$ssm_component/ssm/src/ssmserver.cpp" \
    "$ssm_component/ssm/src/ssmstatetransitionengine.cpp"
test "$(grep -c 'HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1' \
    "$stem_cone_source")" -eq 1
test "$(sed -n '/HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1/,/^\t}/p' \
    "$stem_cone_source" | grep -c 'iWsSession.RedrawReady(&iStatus);')" -eq 2
! sed -n '/HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1/,/^\t}/p' \
    "$stem_cone_source" | grep -q 'User::After\|RTimer\|RequestComplete'
test "$(grep -c 'HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'HTCLEO_CONE_REDRAW_PUMP_DURABLE_TRACE_V1' \
    "$stem_cone_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\CONELOG.TXT' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -h -c '0x434F0' "$stem_cone_main_source" \
    "$stem_cone_source" "$stem_cone_appui_source" \
    "$stem_cone_envextra_source" | awk '{s += $1} END {print s}')" -eq 48
! grep -q 'file.Flush' "$stem_cone_main_source"
test -s "$stem_cone_ready_ao_source"
test "$(grep -c 'HTCLEO_CONE_READY_AO_IDENTITY_TRACE_V1' \
    "$stem_cone_ready_ao_source")" -eq 1
test "$(grep -c 'HtcleoTraceReadyAo(this);' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'source  htcleoschedulertrace.cpp' \
    "$full_epocroot/sf/incubator/stemkit/breakdeps/CONE.MMP")" -eq 1
test "$(grep -c '0x414F010' "$stem_cone_ready_ao_source")" -eq 4
test "$(grep -c 'HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1' \
    "$stem_cone_ready_ao_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSCONE.TXT' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c '1048576 - 128' "$stem_cone_main_source")" -eq 1
test "$(grep -c '0x102750F0u' "$stem_cone_main_source")" -eq 2
test "$(grep -c '0x102750F0u' "$stem_cone_ready_ao_source")" -eq 1
test "$(grep -c 'HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE_V1' \
    "$stem_cone_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE_V1' \
    "$stem_cone_envextra_source")" -eq 1
for htcleo_cone_focus_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
do
    test "$(grep -ci "0x434F05${htcleo_cone_focus_stage}u" \
        "$stem_cone_appui_source")" -eq 1
done
for htcleo_cone_observer_stage in 20 21 22 23 24
do
    test "$(grep -ci "0x434F05${htcleo_cone_observer_stage}u" \
        "$stem_cone_envextra_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT_V1' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'htcleoConeStage == 0x050Fu' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'htcleoConeStage == 0x0207u' \
    "$stem_cone_main_source")" -eq 1
test "$(grep -c 'HTCLEO_LIW_ECOM_MONITOR_STATUS_GUARD_V1' \
    "$liw_monitor_source")" -eq 1
test "$(grep -c 'if (iStatus.Int() != KErrNone)' \
    "$liw_monitor_source")" -eq 1
test "$(grep -c 'iSynchronizeCallBack.CallBack();' \
    "$liw_monitor_source")" -eq 1
test "$(grep -c 'iEcomSession.NotifyOnChange(iStatus);' \
    "$liw_monitor_source")" -eq 1
test "$(grep -c 'HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1' \
    "$stem_critical_cmdlist_source")" -eq 1
test "$(grep -c 'HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1' \
    "$stem_critical_cmdlist_source")" -eq 1
test "$(grep -c 'HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1' \
    "$stem_critical_cmdlist_source")" -eq 1
test "$(grep -F -c 'name = "z:\\sys\\bin\\ailaunch.exe";' \
    "$stem_critical_cmdlist_source")" -eq 1
test "$(grep -c 'HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1' \
    "$stem_noncritical_cmdlist_source")" -eq 1
test "$(grep -c 'HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1' \
    "$stem_noncritical_cmdlist_source")" -eq 1
test "$(grep -F -c 'name = "z:\\sys\\bin\\ailaunch.exe";' \
    "$stem_noncritical_cmdlist_source")" -eq 0
test "$(grep -c 'RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait' \
    "$stem_critical_cmdlist_source")" -eq 1
test "$(grep -c 'HTCLEO_HOMESCREEN_DURABLE_LOG_V1' \
    "$homescreen_logger_source")" -eq 1
test "$(grep -c '1048576 - 128' "$homescreen_logger_source")" -eq 1
test "$(grep -c '0x484F01FFu' "$homescreen_aifw_source")" -eq 1
test "$(grep -c '5000000, 5000000' "$homescreen_aifw_source")" -eq 1
test "$(grep -c 'HTCLEO_HOMESCREEN_ECOM_STATUS_GUARD_V1' \
    "$homescreen_component/src/framework/aiecomobserver.cpp")" -eq 1
test "$(grep -c '0x484F0144u' "$homescreen_idle_source")" -eq 1
test "$(grep -c '0x484F0234u' "$homescreen_launch_source")" -eq 1
test "$(grep -c 'HTCLEO_HOMESCREEN_CONTROLLER_TRACE_V1' \
    "$homescreen_controller_source")" -eq 1
for homescreen_controller_stage in 0130 0131 0132 0133 0134 0135 0136 0137
do
    test "$(grep -c "0x484F${homescreen_controller_stage}u" \
        "$homescreen_controller_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1' \
    "$homescreen_launch_source")" -eq 1
test "$(grep -c 'KHtcleoMaxStartupCrashes = 3' \
    "$homescreen_launch_source")" -eq 1
for homescreen_restart_stage in 0240 0241 0242 0243 0244 0245
do
    test "$(grep -c "0x484F${homescreen_restart_stage}u" \
        "$homescreen_launch_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HOMESCREEN_EXIT_CATEGORY_TRACE_V1' \
    "$homescreen_launch_source")" -eq 1
test "$(grep -c '0x484F0246u' "$homescreen_launch_source")" -eq 1
test "$(grep -c '0x484F0247u +' "$homescreen_launch_source")" -eq 1
test "$(grep -c 'aExitCategory.Length() < 16' \
    "$homescreen_launch_source")" -eq 1
for ai3xml_trace_source in "$ai3xml_controller_source" \
    "$ai3xml_application_source" "$ai3xml_document_source" \
    "$ai3xml_appui_source"
do
    test "$(grep -c 'HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE_V1' \
        "$ai3xml_trace_source")" -eq 1
done
test "$(grep -c 'HTCLEO_AI3XMLUIMAIN_DURABLE_LOG_V1' \
    "$ai3xml_logger_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$ai3xml_logger_source")" -eq 1
test "$(grep -c '1048576 - 128' "$ai3xml_logger_source")" -eq 1
test "$(grep -c 'SOURCE[[:space:]]*htcleoai3xmllog.cpp' \
    "$ai3xml_mmp")" -eq 1
for ai3xml_stage in \
    0100 0101 0102 0103 0104 0110 0111 0112 0120 0121 \
    0130 0131 0140 0141 0142 0143 0150 0151 0160 0161 \
    0170 0171 0180 0181 0182 0183 0184 0185 0186 0187 \
    0190 0191 0192 0193 0194 0195 0196 0197 0198 0199 \
    019A 019B 019C 019D 019E 019F 01A0 01A1 01A2 01A3 \
    01A4 0200 0201 0202 0203 0204 0205 0206
do
    test "$(grep -h -oi "0x4858${ai3xml_stage}u" \
        "$ai3xml_controller_source" "$ai3xml_application_source" \
        "$ai3xml_document_source" "$ai3xml_appui_source" | wc -l)" -eq 1
done
test "$(grep -c 'User::LeaveIfError( htcleoRunResult )' \
    "$ai3xml_controller_source")" -eq 1
test "$(grep -c 'HTCLEO_AI3XML_ONLINEOFFLINE_OPTIONAL_V1' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'HTCLEO_AI3XML_ONLINEOFFLINE_OPTIONAL_V1' \
    "$ai3xml_contentpublisher_source")" -eq 1
test "$(grep -c 'TRAPD( htcleoOnlineOfflineError,' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'htcleoOnlineOfflineError != KErrNotFound' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'htcleoOnlineOfflineError != KErrServerTerminated' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'iHelper ? iHelper->ShowOnlineItem() : EFalse' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'iHelper ? iHelper->ShowOfflineItem() : EFalse' \
    "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'if ( iHelper )' "$ai3xml_appui_source")" -eq 1
test "$(grep -c 'if ( !helper )' \
    "$ai3xml_contentpublisher_source")" -eq 1
test "$(grep -c 'helper->HandleConnectionQueryL' \
    "$ai3xml_contentpublisher_source")" -eq 1
! grep -q 'AppUi()->Helper()->HandleConnectionQueryL' \
    "$ai3xml_contentpublisher_source"
! grep -q 'User::After\|HalFunction' "$ai3xml_logger_source" \
    "$ai3xml_controller_source" "$ai3xml_application_source" \
    "$ai3xml_document_source" "$ai3xml_appui_source" \
    "$ai3xml_contentpublisher_source"
test "$(grep -c 'HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE_V1' \
    "$xn3layout_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId != 0x102750f0u' \
    "$xn3layout_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$xn3layout_source")" -eq 1
test "$(grep -c '1048576 - 128' "$xn3layout_source")" -eq 1
test "$(grep -c 'HTCLEO_HXA  ' "$xn3layout_source")" -eq 1
for xn_adapter_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10
do
    test "$(grep -ci "0x485810${xn_adapter_stage}u" \
        "$xn3layout_source")" -eq 1
done
test "$(grep -c 'HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE_V1' \
    "$xn3layout_impl_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId != 0x102750f0u' \
    "$xn3layout_impl_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$xn3layout_impl_source")" -eq 1
test "$(grep -c '1048576 - 128' "$xn3layout_impl_source")" -eq 1
test "$(grep -c 'HTCLEO_HXI  ' "$xn3layout_impl_source")" -eq 1
for xn_adapter_impl_stage in \
    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \
    10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F \
    20 21 22 23 24
do
    test "$(grep -ci "0x485811${xn_adapter_impl_stage}u" \
        "$xn3layout_impl_source")" -eq 1
done
test "$(grep -c 'HTCLEO_XN_MXMLATTRIBUTES_FORWARD_DECL_V1' \
    "$xn3layout_mxml_header")" -eq 1
test "$(grep -c 'class MXMLAttributes;' \
    "$xn3layout_mxml_header")" -eq 1
grep -Fq '<var name="xn3layoutengine_permissive">' \
    "$xn3layout_config_file"
grep -Fq '<set name="CC" value="/path/to/hd2-legacy-lab/Symbian/scripts/htcleo-gcce-xn3layoutengine-cc-wrapper.sh"/>' \
    "$xn3layout_config_file"
! grep -q 'User::After\|HalFunction\|RTimer' "$xn3layout_source"
! grep -q 'User::After\|HalFunction\|RTimer' "$xn3layout_impl_source"
for xn_loadui_source in "$xn3layout_viewmanager_source" \
    "$xn3layout_rootdata_source" "$xn3layout_composer_source" \
    "$xn3layout_odtparser_source" "$xn3layout_viewdata_source"
do
    test "$(grep -c 'HTCLEO_XN_LOADUI_TRACE_V1' "$xn_loadui_source")" -eq 1
    test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' "$xn_loadui_source")" -eq 1
    test "$(grep -c '1048576 - 128' "$xn_loadui_source")" -eq 1
    ! grep -q 'User::After\|HalFunction\|RTimer' "$xn_loadui_source"
done
for xn_loadui_stage in 00 01 02 03 04 05 06 07 08 09 0A 0B 0C
do
    test "$(grep -ci "0x485815${xn_loadui_stage}u" \
        "$xn3layout_viewmanager_source")" -eq 1
done
for xn_loadui_stage in 10 11 12 13 14 15 20 21 22 23 24 25 26 27 \
    28 29 2A 2B 2C 2D
do
    test "$(grep -ci "0x485815${xn_loadui_stage}u" \
        "$xn3layout_rootdata_source")" -eq 1
done
for xn_loadui_stage in 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E
do
    test "$(grep -ci "0x485815${xn_loadui_stage}u" \
        "$xn3layout_composer_source")" -eq 1
done
for xn_loadui_stage in 50 51 52 53 54 55
do
    test "$(grep -ci "0x485815${xn_loadui_stage}u" \
        "$xn3layout_odtparser_source")" -eq 1
done
test "$(grep -c 'HTCLEO_XN_ODT_VIEW_LOAD_TRACE_V1' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE_V1' \
    "$xn3layout_rootdata_source")" -eq 1
for xn_view_stage in 70 71 72 73 74 75 76 77 78 \
    80 81 82 83 84 85 86 87 88 \
    90 91 92 93 94 95 96 97 98 \
    A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB
do
    test "$(grep -ci "0x485815${xn_view_stage}u" \
        "$xn3layout_odtparser_source")" -eq 1
done
test "$(grep -c 'HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN_V1' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'interfaceUid.iUid == 0x20019592u' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'HTCLEO_XN_MENU_GROUP_METADATA_FAILOPEN_V1' \
    "$xn3layout_odtparser_source")" -eq 1
for xn_nonvisual_constant in \
    KActionsHandlerNodeName KActionsNodeName KActionNodeName KEventNodeName \
    KDynMenuItemNodeName KWidgetMenuItemNodeName KDescNodeName \
    KTextZoomNodeName KConfigurationNodeName KSettingsConfigurationNodeName \
    KContentSourceNodeName KMenuExtensionNodeName
do
    test "$(grep -F -c "aName == $xn_nonvisual_constant" \
        "$xn3layout_odtparser_source")" -eq 1
done
for xn_menu_group_type in menuitemgrouping menuitemgroup
do
    test "$(grep -F -c "aName.Compare(_L8(\"$xn_menu_group_type\")) == 0" \
        "$xn3layout_odtparser_source")" -eq 1
done
for htcleo_xn_retired_source in \
    "$xn3layout_viewmanager_source" "$xn3layout_rootdata_source" \
    "$xn3layout_composer_source" "$xn3layout_odtparser_source" \
    "$xn3layout_viewdata_source"
do
    test "$(grep -c 'HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT_V1' \
        "$htcleo_xn_retired_source")" -eq 1
    test "$(grep -c 'htcleoLoadStage != 0x0Cu' \
        "$htcleo_xn_retired_source")" -eq 1
    test "$(grep -c 'htcleoLoadStage != 0x67u' \
        "$htcleo_xn_retired_source")" -eq 1
    test "$(grep -c 'htcleoLoadStage != 0x98u' \
        "$htcleo_xn_retired_source")" -eq 1
done
for xn_visual_constant in \
    KWidgetNodeName KTextNodeName KImageNodeName KViewNodeName KClockNodeName \
    KMenuBarNodeName KNewstickerNodeName KSliderNodeName KTextEditorNodeName
do
    ! sed -n '/const TBool htcleoHomeNonvisualFactory =/,/HtcleoXnLoadUiLog(0x485815A8u/p' \
        "$xn3layout_odtparser_source" | grep -Fq "aName == $xn_visual_constant"
done
test "$(grep -c 'TRAPD(htcleoFactoryListError,' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'User::LeaveIfError(htcleoFactoryListError)' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE_V1' \
    "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'count == 0' "$xn3layout_odtparser_source")" -eq 1
test "$(grep -c 'componentNodeImplNeeded = EFalse;' \
    "$xn3layout_odtparser_source")" -eq 1
for xn_transient_stage in 2E 2F
do
    test "$(grep -ci "0x485815${xn_transient_stage}u" \
        "$xn3layout_rootdata_source")" -eq 1
done
test "$(grep -c 'if ( err == KErrServerTerminated )' \
    "$xn3layout_rootdata_source")" -eq 1
test "$(grep -c 'if ( htcleoFallbackError == KErrServerTerminated )' \
    "$xn3layout_rootdata_source")" -eq 1
for xn_loadui_stage in 60 61 62 63 64 65 66 67
do
    test "$(grep -ci "0x485815${xn_loadui_stage}u" \
        "$xn3layout_viewdata_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE_V1' \
    "$hspluginsettings_source")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId != 0x102750f0u' \
    "$hspluginsettings_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$hspluginsettings_source")" -eq 1
test "$(grep -c '1048576 - 128' "$hspluginsettings_source")" -eq 1
test "$(grep -c 'HTCLEO_HPS  ' "$hspluginsettings_source")" -eq 1
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_HSPLUGINSETTINGS_TRACE__' \
    "$hspluginsettings_mmp")" -eq 1
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$hspluginsettings_mmp")" -eq 1
for hspluginsettings_stage in \
    00 01 02 03 04 05 06 07 08 09 0A \
    10 11 12 13 14 15 16 17 \
    20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E \
    30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F
do
    test "$(grep -ci "0x485812${hspluginsettings_stage}u" \
        "$hspluginsettings_source")" -eq 1
done
! grep -q 'User::After\|HalFunction\|RTimer' "$hspluginsettings_source"
test "$(grep -h -c 'HTCLEO_HSPSTHEMESERVER_HD2_FAMILY_COMPAT_V1' \
    "$hspsthemeserver_source" "$hspsthemeserver_family_source" \
    "$hspsthemeserver_rominstaller_source" | awk '{sum += $1} END {print sum}')" -eq 3
test "$(grep -c 'HTCLEO_HSPS_INSTALLATION_CONSTRUCT_TRACE_V1' \
    "$hspsthemeserver_installation_source")" -eq 1
test "$(grep -c 'HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_V1' \
    "$hspsthemeserver_source")" -eq 1
test "$(grep -c 'gHtcleoRootRepairAttempted = ETrue' \
    "$hspsthemeserver_source")" -eq 1
test "$(grep -c 'ReinstallConfL(aRetrievedODT.RootUid()' \
    "$hspsthemeserver_source")" -eq 1
for hspsthemeserver_root_stage in E0 E1 E2 E3 E4
do
    test "$(grep -ci "0x485813${hspsthemeserver_root_stage}u" \
        "$hspsthemeserver_source")" -eq 1
done
test "$(grep -c 'MACRO[[:space:]]*__HTCLEO_HSPS_HD2_FAMILY_COMPAT__' \
    "$hspsthemeserver_mmp")" -eq 1
test "$(grep -h -F -c 'C:\\Symbian3\\HSPSSRV.TXT' \
    "$hspsthemeserver_source" "$hspsthemeserver_family_source" \
    "$hspsthemeserver_rominstaller_source" \
    "$hspsthemeserver_installation_source" | \
    awk '{sum += $1} END {print sum}')" -eq 4
test "$(grep -h -c '1048576 - 128' \
    "$hspsthemeserver_source" "$hspsthemeserver_family_source" \
    "$hspsthemeserver_rominstaller_source" \
    "$hspsthemeserver_installation_source" | \
    awk '{sum += $1} END {print sum}')" -eq 4
test "$(grep -c 'case 800:' "$hspsthemeserver_family_source")" -eq 1
test "$(grep -c 'aFamily.Append(KFamilyQhd);' \
    "$hspsthemeserver_family_source")" -eq 1
test "$(grep -c 'htcleoHomeRootPresent' "$hspsthemeserver_source")" -ge 6
for hspsthemeserver_stage in \
    00 01 0B 0C 10 11 12 13 30 31 32 33 34 35 36 40 41 \
    50 51 52 53 54 55 56 57 58 59 5A \
    60 61 62 63 64 65 70 71 72 73 74 75 76 77 78 79 \
    7A 7B 7C 7D 7E F0 F1
do
    test "$(grep -h -ci "0x485813${hspsthemeserver_stage}u" \
        "$hspsthemeserver_source" "$hspsthemeserver_family_source" \
        "$hspsthemeserver_rominstaller_source" \
        "$hspsthemeserver_installation_source" | \
        awk '{sum += $1} END {print sum}')" -eq 1
done
test "$(grep -c 'REComSession::FinalClose();' \
    "$hspsthemeserver_installation_source")" -eq 3
test "$(grep -c '== KErrServerTerminated' \
    "$hspsthemeserver_installation_source")" -eq 2
test "$(grep -c 'HTCLEO_HSPS_INSTALL_SKELETON_TRACE_V1' \
    "$hspsthemeserver_installation_source")" -eq 1
for hsps_install_stage in A0 A1 A2 A3 A4 A5 C0 C1 C2 C3 C4 C5 C6 C7 \
    C8 C9 CA CB CC CD D0 D1 D2 D3 D4
do
    test "$(grep -ci "0x485813${hsps_install_stage}u" \
        "$hspsthemeserver_installation_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HSPS_INSTALL_HANDOFF_TRACE_V1' \
    "$hspsthemeserver_installation_source")" -eq 1
for hsps_handoff_stage in B0 B1 B2 B3 B4 B5 B6
do
    test "$(grep -ci "0x485813${hsps_handoff_stage}u" \
        "$hspsthemeserver_installation_source")" -eq 1
done
test "$(grep -c 'iRequestStatus ? iRequestStatus->Int() : KErrNone' \
    "$hspsthemeserver_installation_source")" -eq 1
test "$(grep -c 'HTCLEO_HSPS_ROMINSTALLER_HANDOFF_TRACE_V1' \
    "$hspsthemeserver_rominstaller_source")" -eq 1
for hsps_rom_handoff_stage in 5B 5C 5D 5E 5F 90 91
do
    test "$(grep -ci "0x485813${hsps_rom_handoff_stage}u" \
        "$hspsthemeserver_rominstaller_source")" -eq 1
done
grep -q 'iDefEngine->CreateDOM( iFsSession, \*iXmlFile, aOdt )' \
    "$hspsthemeserver_installation_source"
grep -q 'iDefinitionRepository.SetOdtL( \*iOdt )' \
    "$hspsthemeserver_installation_source"
! grep -q 'User::After\|RTimer' "$hspsthemeserver_installation_source" \
    "$hspsthemeserver_rominstaller_source"
test "$(grep -c 'HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT_V1' \
    "$hspsprovider_source")" -eq 1
test "$(grep -F -c 'C:\\Symbian3\\HSXML.TXT' \
    "$hspsprovider_source")" -eq 1
test "$(grep -c '1048576 - 128' "$hspsprovider_source")" -eq 1
test "$(grep -c 'aConfigurationNode.ChildNodes().FindByName( KControlElement )' \
    "$hspsprovider_source")" -eq 1
test "$(grep -c 'controlNode->ChildNodes().FindByName( KPluginsElement )' \
    "$hspsprovider_source")" -eq 1
for hspsprovider_stage in 10 11 12 13 14 15
do
    hspsprovider_stage_count=1
    if [ "$hspsprovider_stage" = 12 ]; then
        hspsprovider_stage_count=2
    fi
    test "$(grep -ci "0x485816${hspsprovider_stage}u" \
        "$hspsprovider_source")" -eq "$hspsprovider_stage_count"
done
test "$(grep -c 'LIBRARY[[:space:]]*efsrv.lib' \
    "$hspsprovider_mmp")" -eq 1
! grep -q 'User::After\|RTimer\|HalFunction' "$hspsprovider_source"
test "$(grep -c 'HTCLEO_HSPS_DEFINITION_ENGINE_LAZY_PARSER_V1' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c ': ihspsXMLHandler( NULL )' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'TRAPD( parserInitError,' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'ihspsXMLHandler = ChspsXMLHandler::NewL()' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'ihspsXMLHandler->ParseXmlDocL' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'HTCLEO_HSPS_DEFINITION_ECOM_RECOVERY_TRACE_V1' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'parserInitError == KErrServerTerminated' \
    "$hsps_definition_source")" -eq 1
test "$(grep -c 'HTCLEO_HSPS_LIBXML2_ROM_CLOSURE_V1' \
    "$hsps_definition_source")" -eq 1
! grep -q 'REComSession::FinalClose();' "$hsps_definition_source"
for hsps_definition_stage in E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB
do
    test "$(grep -ci "0x485814${hsps_definition_stage}u" \
        "$hsps_definition_source")" -eq 1
done
test "$(grep -c 'HTCLEO_HSPS_XML_HANDLER_TRACE_V1' \
    "$hsps_definition_component/src/hspsxmlhandler.cpp")" -eq 1
for hsps_xml_stage in F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB
do
    test "$(grep -ci "0x485814${hsps_xml_stage}u" \
        "$hsps_definition_component/src/hspsxmlhandler.cpp")" -eq 1
done
! grep -q 'User::After\|RTimer\|HalFunction' "$hsps_definition_source"
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY_V1' \
    "$ecom_session")" -eq 1
test "$(grep -c 'RProcess().SecureId().iId == 0x102750F0u' \
    "$ecom_session")" -eq 4
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1' \
    "$ecom_server_session")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1' \
    "$ecom_server_source")" -eq 1
test "$(grep -c 'HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1' \
    "$ecom_component/frame/RegistryData.cpp")" -eq 1
for ecom_home_session_stage in \
    500 501 502 503 504 505 506 507 508 509 50A 50B 50C 50D 50F 510 511
do
    test "$(grep -ci "0x0000F${ecom_home_session_stage}u" \
        "$ecom_server_session")" -eq 1
done
for ecom_home_server_stage in 520 521 522 523 524
do
    test "$(grep -ci "0x0000F${ecom_home_server_stage}u" \
        "$ecom_server_source")" -eq 1
done
for ecom_home_registry_stage in 530 531 532 533 534 535 536 537 538 539
do
    test "$(grep -ci "0x0000F${ecom_home_registry_stage}u" \
        "$ecom_component/frame/RegistryData.cpp")" -eq 1
done
test "$(grep -h -c 'HTCLEO_ECOM_HSPS_DEFINITION_DIRECT_RESOLVE_V1' \
    "$ecom_server_session" "$ecom_server_source" | \
    awk '{sum += $1} END {print sum}')" -eq 2
test "$(grep -c '0x200159C8' "$ecom_server_source")" -eq 1
for ecom_hsps_stage in 540 541 542 543 544 545 546
do
    test "$(grep -ci "0x0000F${ecom_hsps_stage}u" \
        "$ecom_server_source")" -eq 1
done
test "$(grep -h -c 'HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1' \
    "$ecom_server_logger_header" "$ecom_server_logger" \
    "$ecom_server_session" "$ecom_server_source" \
    "$ecom_server_registry_data" | awk '{sum += $1} END {print sum}')" -eq 5
test "$(grep -F -c 'C:\\Symbian3\\HSPSECOM.TXT' \
    "$ecom_server_logger")" -eq 2
test "$(grep -c '1048576 - 128' "$ecom_server_logger")" -eq 1
for ecom_hsps_persistent_stage in \
    600 601 602 610 611 612 613 614 615 616 \
    620 621 622 623 624 625 626 627 628
do
    test "$(grep -h -ci "0x0000F${ecom_hsps_persistent_stage}u" \
        "$ecom_server_session" "$ecom_server_source" \
        "$ecom_server_registry_data" | \
        awk '{sum += $1} END {print sum}')" -eq 1
done
test "$(grep -h -c 'HTCLEO_ECOM_HSPS_RESPONSE_TRACE_V1' \
    "$ecom_server_session" "$ecom_server_source" | \
    awk '{sum += $1} END {print sum}')" -eq 2
for ecom_hsps_response_stage in \
    603 604 605 606 607 608 609 60A 60B 60C 60D 60E 60F \
    617 631 632 633 634 640 641 642
do
    test "$(grep -h -ci "0x0000F${ecom_hsps_response_stage}u" \
        "$ecom_server_session" "$ecom_server_source" | \
        awk '{sum += $1} END {print sum}')" -eq 1
done

python3 "$shell_resume_fastpath" "$full_epocroot"
python3 "$menulog_capacity" "$full_epocroot" \
    --report "$output/MENULOG-CAPACITY-POLICY.json"
python3 "$external_thread_watch" "$full_epocroot"
if [ "$incremental_resource_policy" = gate17-catalog-observer ]; then
    python3 "$gate17_observer" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-settings-only ] || \
   [ "$incremental_resource_policy" = gate17-settings-ready-781 ] || \
   [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ] || \
   [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gate17_settings" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-layout-ipc-trace ] || \
   [ "$incremental_resource_policy" = gate17-settings-ready-781 ] || \
   [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ] || \
   [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$packed_layout_trace" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ] || \
   [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$matrix_pointer_frontier" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$matrix_list_release" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$matrix_system_fade" "$full_epocroot"
fi

if [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_action_frontier" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$menu_launch_frontier" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$menu_attribute_frontier" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$menu_request_frontier" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_server_exit_watch" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_software_exception" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_exception_stack" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_notifier_stop" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$menu_task_lookup" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$mcs_operation_completion" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$menu_task_enumeration" "$full_epocroot"
fi
if [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$hsps_header_cache" "$full_epocroot"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_observer" "$full_epocroot"
    gsapp_observer_policy=native-startup128-owned-ui5s-GSBOOT1m-no-UI-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_eikstart" "$full_epocroot"
    gsapp_eikstart_policy=native-local-6002-6070-6082-no-bypass-shared-eikcore-unchanged
fi

if [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_env" "$full_epocroot"
    gsapp_env_policy=sid100058ec-existing-E300-E320-E400-E425-GSBOOT1m-no-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_aknenv" "$full_epocroot"
    gsapp_aknenv_policy=sid100058ec-existing-A000-A01E-GSBOOT1m-no-CDL-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_sgc" "$full_epocroot"
    gsapp_sgc_policy=sid100058ec-notfound-or-terminated-nullhandle-native-local-layout-GSBOOT1m
fi

if [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_appui" "$full_epocroot"
    gsapp_appui_policy=sid100058ec-B500-B547-B560-B57F-GSBOOT1m-no-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_sgc_params" "$full_epocroot"
    gsapp_sgc_params_policy=sid100058ec-nullhandle-local-fields-no-SetSgcParams-firstchange64-GSBOOT1m
fi

if [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_eikbase" "$full_epocroot"
    gsapp_eikbase_policy=sid100058ec-existing-B600-B615-GSBOOT1m-no-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_appinfo" "$full_epocroot"
    gsapp_appinfo_policy=sid100058ec-B61F-B631-GSBOOT1m-native-resource-furniture-unchanged
fi

if [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_statuspane" "$full_epocroot"
    gsapp_statuspane_policy=sid100058ec-B640-B67B-GSBOOT1m-native-statuspane-unchanged
fi

if [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_sgc_fade" "$full_epocroot"
    gsapp_sgc_fade_policy=sid100058ec-handle0-real-local-fade-firstget3-GSBOOT1m
fi

if [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_view" "$full_epocroot"
    gsapp_view_policy=ws-first8-nonpointer-native-pass-through-first-activation-60A0-A9-GSBOOT-existing
fi

if [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_focus" "$full_epocroot"
    gsapp_focus_policy=first-GS-FocusGained-logonly-private-ext-bit5-C560-C56E-C594-C5E0
fi

if [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_keyblock" "$full_epocroot"
    gsapp_keyblock_policy=GS-only-zero-session-no-keyblock-IPC-firstcall4-private-bit6
fi

if [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_activation" "$full_epocroot"
    gsapp_activation_policy=GS-no-active-view-transaction64-native-activation-cleanup-unchanged
fi

if [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_plugin" "$full_epocroot"
    gsapp_plugin_policy=GS-root-first2-native-RunL-LoadNext-RunError-no-recovery-or-priority-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_redraw" "$full_epocroot"
    gsapp_redraw_policy=GS-first-native-redraw32-and-pre-native-panic-no-queue-or-drawing-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_lifetime" "$full_epocroot"
    gsapp_lifetime_policy=Home-existing-clock5s-native-GS-process-thread-exit-CLOCKLOG-padding-no-new-io-writer
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_notify" "$full_epocroot"
    gsapp_notify_policy=GS-negative-notify-retire-C730-no-list-no-rearm-success-native
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$project/Symbian/scripts/prepare-htcleo-ecom-825-source-control.py" "$full_epocroot"
    python3 "$gsapp_create" "$full_epocroot"
    gsapp_create_policy=GS-create-minus15-one-native-reconnect-C731-C733-real-result-no-empty-fallback
fi

if [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_child" "$full_epocroot"
    gsapp_child_policy=GS-root-and-General-first2-C734-parent-no-loading-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_list" "$full_epocroot"
    gsapp_list_policy=GS-first8-list-events-index-block-type-native-activation-60C0-C6-no-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_async" "$full_epocroot"
    gsapp_async_policy=GS-root-native-CreateActivateViewEventL-no-sync-completion-wait-no-forced-view
fi

if [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_transition" "$full_epocroot"
    gsapp_transition_policy=GS-enqueue-C603-C604-C607-all-GS-native-ActivationTick64-no-policy-change
fi
if [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_cone_event" "$full_epocroot"
    gsapp_cone_event_policy=GS-only-registration-inbound-dispatch32-native-policy-no-new-trap
fi
if [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$home_view_event" "$full_epocroot"
    home_view_event_policy=Home-plus-GS-native-view-events-deactivation32-separate-owner-sinks-no-policy-change
fi

if [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$gsapp_exception" "$full_epocroot"
    gsapp_exception_policy=GS-no-existing-handler-install60E0-GSX1-bounded240-terminal-restore-reraise
fi

export EPOCROOT="$full_epocroot/"
export SBS_HOME=/root/symbian/linux_build/sbsv2/raptor
export SBS_GCCE441BIN=/root/gcce-native-4.4.1/bin
export PERL5LIB=/root/symbian/linux_build/cross-plat-dev-utils
export PERL_USE_UNSAFE_INC=1

# Incremental iterations preserve the verified parent build cache and let SBS
# rebuild only stale targets.  Full CLEAN remains available explicitly for ABI,
# recipe, BSP or build-cache recovery work.
sbs_clean()
{
    if [ "$build_mode" = full-clean ]; then
        "$SBS_HOME/bin/sbs" "$@" CLEAN
    fi
}

incremental_wants_binary()
{
    candidate=$1
    for changed_binary in $incremental_changed_binaries
    do
        if [ "$candidate" = "$changed_binary" ]; then
            return 0
        fi
    done
    return 1
}

# Some isolated SBS units intentionally contain a tightly coupled client/server
# pair.  Asking SBS to rebuild one member can relink the unchanged sibling as a
# side effect.  Keep the ROM delta exact by restoring any non-allowlisted
# sibling from the verified parent cache before the global binary-diff guard.
restore_incremental_sibling_output()
{
    sibling=$1
    if [ "$build_mode" != incremental ] || \
        incremental_wants_binary "$sibling"; then
        return
    fi
    sibling_record=$(awk -F '\t' -v path="$sibling" \
        '$2 == path { print $1 "\t" $3 }' \
        "$parent_cache/RELEASE-CACHE-MANIFEST.tsv")
    test "$(printf '%s\n' "$sibling_record" | sed '/^$/d' | wc -l)" -eq 1
    sibling_hash=$(printf '%s\n' "$sibling_record" | cut -f1)
    sibling_cache_name=$(printf '%s\n' "$sibling_record" | cut -f2)
    test -s "$parent_cache/$sibling_cache_name"
    test "$(sha256sum "$parent_cache/$sibling_cache_name" | awk '{print $1}')" = \
        "$sibling_hash"
    cp "$parent_cache/$sibling_cache_name" "$sibling"
    test "$(sha256sum "$sibling" | awk '{print $1}')" = "$sibling_hash"
    echo "HTCLEO_INCREMENTAL_SIBLING_RESTORED path=$sibling"
}

# Arguments before -- are every release output produced by one isolated SBS
# invocation. In incremental mode the invocation is skipped unless at least
# one output is explicitly allowlisted; cached objects remain available for
# the unchanged validation steps below.
sbs_build_for()
{
    requested=0
    labels=
    while [ "$#" -gt 0 ] && [ "$1" != -- ]
    do
        labels="$labels $1"
        if incremental_wants_binary "$1"; then
            requested=1
        fi
        shift
    done
    test "$#" -gt 0 && test "$1" = --
    shift
    if [ "$build_mode" = full-clean ] || [ "$requested" = 1 ]; then
        "$SBS_HOME/bin/sbs" "$@"
    else
        echo "HTCLEO_INCREMENTAL_SBS_REUSED outputs=$labels"
    fi
}
# 775: no core relink or instruction patch. The crash notification is
# observed through the existing BTrace API from the resident epointer extension.
if incremental_wants_binary "$native_kernel_binary" || [ "$rebuild_native_bsp" != 0 ]; then
    echo 'ERROR: native crash diagnostics must preserve the exact772 core and cannot rebuild the BSP.' >&2
    exit 1
fi
test "$(sha256sum "$native_kernel_binary" | awk '{print $1}')" = \
    11b1e892ed118d8002d1bc1813b7c432b591e400bbd14cd351235e772e32e055
sha256sum "$native_kernel_binary" >"$output/kernel-restored-772-urel.sha256"
# Native thread-state query is an isolated epointer extension build. The whole
# kernel/BSP and all hardware behavior remain parent-controlled. The final
# global binary-diff guard must allow exactly this extension plus ailaunch.
thread_state_pdd="$native_epocroot//epoc32/release/armv5/urel/_htcleo_epointer.dll"
if [ "$build_mode" = incremental ] && incremental_wants_binary "$thread_state_pdd"; then
    test "$rebuild_native_bsp" = 0
    bash "$project/Symbian/scripts/build-htcleo-thread-state-hal.sh"
fi

# Rebuild the STEM CONE control environment only when explicitly allowlisted.
# The isolated bld.inf avoids relinking unrelated STEM UI binaries.
stem_cone_config=arm.v5.urel.gcce4_4_1
if [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ]; then
    test "$(sha256sum "$stem_cone_binary" | awk '{print $1}')" = b0b7b853a0ac3bba6d79054484f366887d4e3ef2a33e70a918d6e5f83e602897
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/stem_cone.dll
fi
if [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ]; then
    rm -f "$stem_cone_binary"
fi
if [ "$incremental_resource_policy" != gate19-filemanager-registration ]; then
    sbs_clean -b "$stem_cone_bldinf" -c "$stem_cone_config"
    sbs_build_for "$stem_cone_binary" -- \
        -b "$stem_cone_bldinf" -c "$stem_cone_config" -j 4
fi
test -s "$stem_cone_binary"
test "$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEPRIV.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEMAIN.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEAUI.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/*' -iname 'CoeEnvExtra.o' \
    -type f | wc -l)" -eq 1
stem_cone_redraw_obj=$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEPRIV.o' -type f)
stem_cone_event_obj=$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEMAIN.o' -type f)
stem_cone_appui_obj=$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/COEAUI.o' -type f)
stem_cone_envextra_obj=$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/*' -iname 'CoeEnvExtra.o' -type f)
stem_cone_ready_ao_obj=$(find "$full_epocroot/epoc32/build/stem-cone-build" \
    -path '*/stem_cone_dll/armv5/urel/htcleoschedulertrace.o' -type f)
test -n "$stem_cone_ready_ao_obj" && test -s "$stem_cone_ready_ao_obj"
stem_cone_redraw_disasm="$output/stem-cone-redrawer-arm-before-ready-urel.disasm"
stem_cone_event_disasm="$output/stem-cone-event-pump-durable-trace-urel.disasm"
stem_cone_ready_ao_disasm="$output/stem-cone-ready-ao-identity-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_cone_redraw_obj" >"$stem_cone_redraw_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_cone_event_obj" >"$stem_cone_event_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_cone_appui_obj" >>"$stem_cone_event_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_cone_envextra_obj" >>"$stem_cone_event_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_cone_ready_ao_obj" >"$stem_cone_ready_ao_disasm"
stem_cone_expected_ready_calls=2
if [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    #GS observation causes a compiler split, not an extra request per call.
    #The822 audit below verifies all three native path orders and source inverse.
    stem_cone_expected_ready_calls=3
fi
test "$(grep -c 'R_ARM_.*CALL.*11RedrawReadyEP14TRequestStatus' \
    "$stem_cone_redraw_disasm")" -eq "$stem_cone_expected_ready_calls"
test "$(grep -c 'R_ARM_.*CALL.*SetActive' \
    "$stem_cone_redraw_disasm")" -ge 2
grep -q 'R_ARM_.*CALL.*SecureId' "$stem_cone_redraw_disasm"
grep -q 'HtcleoConeLog' "$stem_cone_redraw_disasm"
grep -q 'HtcleoConeLog' "$stem_cone_event_disasm"
grep -qi '434f0500' "$stem_cone_event_disasm"
grep -qi '434f050f' "$stem_cone_event_disasm"
grep -qi '434f0520' "$stem_cone_event_disasm"
grep -qi '434f0524' "$stem_cone_event_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_cone_event_disasm"
grep -q 'HtcleoConeLog' "$stem_cone_ready_ao_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$stem_cone_event_disasm"
# Matrix scheduler file logger is retired; the compiler removes its dead I/O
# strings. Home's retained low-rate route must still be present below.
! strings "$stem_cone_event_obj" | grep -Fq 'HTCLEO_COE '
! strings -el "$stem_cone_event_obj" | grep -Fq 'C:\Symbian3\CONELOG.TXT'
strings "$stem_cone_event_obj" | grep -Fq 'HTCLEO_HCOE '
strings -el "$stem_cone_event_obj" | grep -Fq 'C:\Symbian3\HSCONE.TXT'
! grep -q 'User::After\|WaitForRequest\|RequestComplete' \
    "$stem_cone_redraw_disasm" "$stem_cone_event_disasm" \
    "$stem_cone_ready_ao_disasm"
sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
if [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_cone_binary" >"$output/cone-redraw-822-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-redraw-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/822-gsapp-redraw-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-REDRAW-OBJECTS.json"
    cp "$stem_cone_binary.map" "$output/stem_cone.dll.map"
    cp "$stem_cone_binary.sym" "$output/stem_cone.dll.sym"
    cp "$stem_cone_source" "$output/COEPRIV-822.CPP"
fi
if [ "$incremental_resource_policy" = gate17-home-view-event ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_cone_binary" >"$output/cone-home-view-832-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-home-view-event.py" \
        --baseline "$project/Symbian/output/iteration-evidence/832-home-view-event/BASE-OBJECTS.json" \
        --native "$output" --report "$output/HOME-VIEW-EVENT-OBJECTS.json"
    cp "$stem_cone_binary.map" "$output/cone-home-view-832.map"
    cp "$stem_cone_binary.sym" "$output/cone-home-view-832.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/coevwman.cpp" "$output/coevwman-832.cpp"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_cone_binary" >"$output/cone-view-event-831-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-cone-view-event.py" \
        --baseline "$project/Symbian/output/iteration-evidence/831-gsapp-cone-view-event/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-CONE-EVENT-OBJECTS.json"
    cp "$stem_cone_binary.map" "$output/cone-view-event-831.map"
    cp "$stem_cone_binary.sym" "$output/cone-view-event-831.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/coevwman.cpp" "$output/coevwman-831.cpp"
fi
sha256sum "$stem_cone_event_obj" >"$output/stem-cone-event-object-urel.sha256"
sha256sum "$stem_cone_ready_ao_obj" \
    >"$output/stem-cone-ready-ao-object-urel.sha256"
if [ "$incremental_resource_policy" = gate17-viewcli-source-control ]; then
    # Native source is unchanged. Only the isolated VIEWCLI target is selected.
    rm -f "$viewcli_binary"
    sbs_build_for "$viewcli_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewcli-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewcli_binary" >"$output/viewcli-source-control-833-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-viewcli-source-control.py" \
        --native "$output" --report "$output/VIEWCLI-SOURCE-CONTROL-OBJECTS.json"
    sha256sum "$viewcli_binary" >"$output/viewcli-source-control-833-urel.sha256"
    cp "$viewcli_binary.map" "$output/viewcli-source-control-833.map"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/client/VIEWCLI.CPP" "$output/VIEWCLI-833.CPP"
    viewcli_source_control_policy=unmodified-native-ViewCLI-source-GCCE-control-no-new-log-or-behavior-patch
fi
if [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$home_kernel_watch" "$full_epocroot"
    home_kernel_watch_policy=existing5s-HAL21-sampler-known-newborn-Home-PID-unique-initial-thread-no-target-mutation
    external_thread_watch_policy=ailaunch-home-known-process-kernel21-v2-readyqueue-endpoint-sync766-1m
fi
if [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    # Keep current client/server source overlays without rebuilding either DLL.
    python3 "$vws_client_queue" "$full_epocroot"
    python3 "$vws_client_state" "$full_epocroot"
    python3 "$vws_server_event" "$full_epocroot"
    python3 "$vws_session_deactivation" "$full_epocroot"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
    vws_client_state_policy=Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change
    viewsrv_source_control_policy=retained836-control-base-with837-event-observation
    vws_server_event_policy=Home-GS-Matrix-activation-ack-timeout-complete32-no-state-policy-change
    vws_session_deactivation_policy=UI-session-deactivation-created-processing-send-ack32-no-policy-change
fi
if [ "$incremental_resource_policy" = gate17-vws-session-deactivation ]; then
    python3 "$vws_client_queue" "$full_epocroot"
    python3 "$vws_client_state" "$full_epocroot"
    python3 "$vws_server_event" "$full_epocroot"
    python3 "$vws_session_deactivation" "$full_epocroot"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
    vws_client_state_policy=Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change
    viewsrv_source_control_policy=retained836-control-base-with837-event-observation
    vws_server_event_policy=Home-GS-Matrix-activation-ack-timeout-complete32-no-state-policy-change
    rm -f "$viewsrv_binary"
    sbs_build_for "$viewsrv_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewsrv-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewsrv_binary" >"$output/viewsrv-session-838-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-vws-session-deactivation.py" \
        --baseline "$project/Symbian/output/iteration-evidence/838-vws-session-deactivation/BASE-OBJECTS.json" \
        --native "$output" --report "$output/VWS-SESSION-DEACTIVATION-OBJECTS.json"
    sha256sum "$viewsrv_binary" >"$output/viewsrv-session-838-urel.sha256"
    cp "$viewsrv_binary.map" "$output/viewsrv-session-838.map"
    cp "$viewsrv_binary.sym" "$output/viewsrv-session-838.sym"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/server/VWSSEVNT.CPP" "$output/VWSSEVNT-838.CPP"
    vws_session_deactivation_policy=UI-session-deactivation-created-processing-send-ack32-no-policy-change
fi
if [ "$incremental_resource_policy" = gate17-vws-server-event ]; then
    python3 "$vws_client_queue" "$full_epocroot"
    python3 "$vws_client_state" "$full_epocroot"
    python3 "$vws_server_event" "$full_epocroot"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
    vws_client_state_policy=Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change
    rm -f "$viewsrv_binary"
    sbs_build_for "$viewsrv_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewsrv-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewsrv_binary" >"$output/viewsrv-event-837-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-vws-server-event.py" \
        --baseline "$project/Symbian/output/iteration-evidence/837-vws-server-event/BASE-OBJECTS.json" \
        --native "$output" --report "$output/VWS-SERVER-EVENT-OBJECTS.json"
    sha256sum "$viewsrv_binary" >"$output/viewsrv-event-837-urel.sha256"
    cp "$viewsrv_binary.map" "$output/viewsrv-event-837.map"
    cp "$viewsrv_binary.sym" "$output/viewsrv-event-837.sym"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/server/VWSEVENT.CPP" "$output/VWSEVENT-837.CPP"
    viewsrv_source_control_policy=retained836-control-base-with837-event-observation
    vws_server_event_policy=Home-GS-Matrix-activation-ack-timeout-complete32-no-state-policy-change
fi
if [ "$incremental_resource_policy" = gate17-viewsrv-source-control ]; then
    # Retain the already-tested client source and binary; do not relink it.
    python3 "$vws_client_queue" "$full_epocroot"
    python3 "$vws_client_state" "$full_epocroot"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
    vws_client_state_policy=Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change
    rm -f "$viewsrv_binary"
    sbs_build_for "$viewsrv_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewsrv-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewsrv_binary" >"$output/viewsrv-source-control-836-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-viewsrv-source-control.py" \
        --native "$output" --report "$output/VIEWSRV-SOURCE-CONTROL-OBJECTS.json"
    sha256sum "$viewsrv_binary" >"$output/viewsrv-source-control-836-urel.sha256"
    cp "$viewsrv_binary.map" "$output/viewsrv-source-control-836.map"
    cp "$viewsrv_binary.sym" "$output/viewsrv-source-control-836.sym"
    viewsrv_source_control_policy=unmodified-native-ViewServer-source-GCCE-control-no-new-log-or-timeout-change
fi
if [ "$incremental_resource_policy" = gate17-vws-client-state ]; then
    python3 "$vws_client_queue" "$full_epocroot"
    python3 "$vws_client_state" "$full_epocroot"
    rm -f "$viewcli_binary"
    sbs_build_for "$viewcli_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewcli-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewcli_binary" >"$output/viewcli-state-835-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-vws-client-state.py" \
        --baseline "$project/Symbian/output/iteration-evidence/835-vws-client-state/BASE-OBJECTS.json" \
        --native "$output" --report "$output/VWS-CLIENT-STATE-OBJECTS.json"
    sha256sum "$viewcli_binary" >"$output/viewcli-state-835-urel.sha256"
    cp "$viewcli_binary.map" "$output/viewcli-state-835.map"
    cp "$viewcli_binary.sym" "$output/viewcli-state-835.sym"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/client/VIEWCLI.CPP" "$output/VIEWCLI-835.CPP"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
    vws_client_state_policy=Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change
fi
if [ "$incremental_resource_policy" = gate17-vws-client-queue ]; then
    python3 "$vws_client_queue" "$full_epocroot"
    rm -f "$viewcli_binary"
    sbs_build_for "$viewcli_binary" -- \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/viewcli-build/bld.inf" \
        -c arm.v5.urel.gcce4_4_1 -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$viewcli_binary" >"$output/viewcli-queue-834-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-vws-client-queue.py" \
        --baseline "$project/Symbian/output/iteration-evidence/834-vws-client-queue/BASE-OBJECTS.json" \
        --native "$output" --report "$output/VWS-CLIENT-QUEUE-OBJECTS.json"
    sha256sum "$viewcli_binary" >"$output/viewcli-queue-834-urel.sha256"
    cp "$viewcli_binary.map" "$output/viewcli-queue-834.map"
    cp "$viewcli_binary.sym" "$output/viewcli-queue-834.sym"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/client/VIEWCLI.CPP" "$output/VIEWCLI-834.CPP"
    cp "$full_epocroot/sf/mw/appsupport/appfw/viewserver/group/VIEWCLI.MMP" "$output/VIEWCLI-834.MMP"
    viewcli_source_control_policy=retained833-control-base-with834-client-observation
    vws_client_queue_policy=Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer
fi
# Iteration 669 identifies the fatal ready object by canonical-ROM vtable as
# CLiwEcomMonitor.  Rebuild LIW with a narrow status guard: a negative ECom
# completion is not a registry change, so it must not synchronize providers or
# touch the failed notification session.  Successful notifications remain stock.
test -s "$full_epocroot/epoc32/release/armv5/lib/SenXml.dso"
ln -sfn SenXml.dso \
    "$full_epocroot/epoc32/release/armv5/lib/SenXML.dso"
if incremental_wants_binary "$liw_binary"; then
    rm -f "$liw_binary"
fi
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$liw_bldinf" -c "$matrixmenu_config"
sbs_build_for "$liw_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$liw_bldinf" -c "$matrixmenu_config" -j 4
test -s "$liw_binary"
test "$(find "$full_epocroot/epoc32/build/servicehandler" \
    -path '*/liwservicehandler_dll/armv5/urel/liwecommonitor.o' \
    -type f | wc -l)" -eq 1
liw_monitor_obj=$(find "$full_epocroot/epoc32/build/servicehandler" \
    -path '*/liwservicehandler_dll/armv5/urel/liwecommonitor.o' -type f)
liw_monitor_disasm="$output/liw-ecom-monitor-status-guard-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$liw_monitor_obj" >"$liw_monitor_disasm"
grep -q '_ZN15CLiwEcomMonitor4RunLEv' "$liw_monitor_disasm"
grep -A14 '<_ZN15CLiwEcomMonitor4RunLEv>' "$liw_monitor_disasm" | \
    grep -q 'cmp.*#0'
grep -A14 '<_ZN15CLiwEcomMonitor4RunLEv>' "$liw_monitor_disasm" | \
    grep -q 'bne'
grep -A24 '<_ZN15CLiwEcomMonitor4RunLEv>' "$liw_monitor_disasm" | \
    grep -q '_ZN15CLiwEcomMonitor15StartMonitoringEv'
! grep -q 'e7f000f0\|c6400000' "$liw_monitor_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$liw_binary" >"$output/liwservicehandler-e32-dump.txt"
grep -qi 'Secure ID: 2000b5d3' "$output/liwservicehandler-e32-dump.txt"
grep -qi 'Module Version: 10.2' "$output/liwservicehandler-e32-dump.txt"
grep -qi 'Number of exports = 226' "$output/liwservicehandler-e32-dump.txt"
sha256sum "$liw_binary" >"$output/liwservicehandler-urel.sha256"
sha256sum "$liw_monitor_obj" \
    >"$output/liw-ecom-monitor-object-urel.sha256"
sha256sum "$liw_stock_669" \
    >"$output/liwservicehandler-stock-669.sha256"
# Rebuild the active STEM startup command-list resources in isolation.  The
# full STEM bld.inf also parses unrelated binary projects that are not part of
# this ROM's source-native closure, so the checked-in isolated bld.inf exposes
# only ssmcmdlists.mmp.
sbs_clean -b "$stem_resource_bldinf" -c "$ssm_config"
if [ "$build_mode" = full-clean ] || \
    incremental_wants_binary "$homescreen_aifw_binary" || \
    incremental_wants_binary "$homescreen_idle_binary" || \
    incremental_wants_binary "$homescreen_launch_binary" || \
    incremental_wants_binary "$homescreen_binary" || \
    grep -q 'HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1' \
        "$stem_critical_cmdlist_source"
then
    "$SBS_HOME/bin/sbs" -b "$stem_resource_bldinf" \
        -c "$ssm_config" RESOURCE
else
    echo "HTCLEO_INCREMENTAL_SBS_REUSED outputs=stem-command-list-resources"
fi
stem_resource_hashes="$output/stem-command-list-resources.sha256"
: >"$stem_resource_hashes"
for stem_resource in \
    "$full_epocroot/epoc32/data/z/private/2000d75b/startup/0/stem_uiservicescmdlist.rsc" \
    "$full_epocroot/epoc32/data/z/private/2000d75b/startup/0/stem_criticalappscmdlist.rsc" \
    "$full_epocroot/epoc32/data/z/private/2000d75b/startup/0/stem_noncriticalcmdlist.rsc" \
    "$full_epocroot/epoc32/data/z/private/2000d75b/shutdown/stem_shutdowncmdlists.rsc"
do
    test -s "$stem_resource"
    sha256sum "$stem_resource" >>"$stem_resource_hashes"
done
test "$(wc -l <"$stem_resource_hashes")" -eq 4

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$filemanager_registration" "$full_epocroot"
    filemanager_registration_policy=retain869-registration-select-unique-live-AppArc-SID-after-member0-close-original-session-then-one-30s-Logon-exit-watch
fi

# Build the complete stock HomeScreen bootstrap/framework/idle integration as
# one isolated unit.  Four parent tuples are restored above, so this remains a
# bounded incremental delta while the product controller/rendering closure is
# supplied by the prepared ROM recipe.
test -s "$full_epocroot/epoc32/release/armv5/lib/AknNotify.dso"
ln -sfn AknNotify.dso \
    "$full_epocroot/epoc32/release/armv5/lib/aknnotify.dso"
for homescreen_changed_binary in \
    "$homescreen_aifw_binary" "$homescreen_idle_binary" \
    "$homescreen_launch_binary" "$homescreen_binary"
do
    if incremental_wants_binary "$homescreen_changed_binary"; then
        rm -f "$homescreen_changed_binary"
    fi
done
if [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$home_kernel_watch" "$full_epocroot"
    home_kernel_watch_policy=existing5s-HAL21-sampler-known-newborn-Home-PID-unique-initial-thread-no-target-mutation
    external_thread_watch_policy=ailaunch-home-known-process-kernel21-v2-readyqueue-endpoint-sync766-1m
    sbs_build_for "$homescreen_launch_binary" -- \
        --configpath="$matrixmenu_config_path" -b "$homescreen_bldinf" \
        -p hslaunch.mmp -c "$matrixmenu_config" -j 4
else
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$homescreen_bldinf" -c "$matrixmenu_config"
sbs_build_for "$homescreen_aifw_binary" "$homescreen_idle_binary" \
    "$homescreen_launch_binary" "$homescreen_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$homescreen_bldinf" -c "$matrixmenu_config" -j 4
fi
if [ "$incremental_resource_policy" = gate17-home-kernel-watch ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$homescreen_launch_binary" >"$output/ailaunch-home-watch-839-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-home-kernel-watch.py" \
        --native "$output" --report "$output/HOME-KERNEL-WATCH-OBJECTS.json"
    cp "$homescreen_launch_binary.map" "$output/ailaunch-home-watch-839.map"
    cp "$homescreen_launch_binary.sym" "$output/ailaunch-home-watch-839.sym"
    cp "$full_epocroot/sf/mw/homescreensrv/idlefw/hslaunch/src/htcleothreadwatch.inl" "$output/htcleothreadwatch-839.inl"
fi
for homescreen_output_binary in \
    "$homescreen_aifw_binary" "$homescreen_idle_binary" \
    "$homescreen_launch_binary" "$homescreen_binary"
do
    test -s "$homescreen_output_binary"
done
restore_incremental_sibling_output "$homescreen_aifw_binary"
restore_incremental_sibling_output "$homescreen_idle_binary"
restore_incremental_sibling_output "$homescreen_launch_binary"
restore_incremental_sibling_output "$homescreen_binary"

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-apparc-exit-watch.py" --native "$incremental_parent_root/build" --report "$output/APPARC-EXIT-WATCH-PARENT-870-OBJECTS.json"
    for retained_exit870 in ailaunch-exit-watch-870-full-dump.txt ailaunch-exit-watch-870.map ailaunch-exit-watch-870.sym htcleog17settings-870.inl; do
        cp "$incremental_parent_root/build/$retained_exit870" "$output/$retained_exit870"
    done
    cp "$incremental_parent_root/build/APPARC-EXIT-WATCH-PARENT-870-ROM.json" "$output/APPARC-EXIT-WATCH-PARENT-870-ROM.json"
    cp "$incremental_parent_root/build/APPARC-EXIT-WATCH-PARENT-870-CANONICAL.json" "$output/APPARC-EXIT-WATCH-PARENT-870-CANONICAL.json"
    for retained_fm868 in htcleog17settings-868.inl ailaunch-filemanager-868-full-dump.txt ailaunch-filemanager-868.map ailaunch-filemanager-868.sym; do
        cp "$incremental_parent_root/build/$retained_fm868" "$output/$retained_fm868"
    done
    for retained_fm_proof in OBJECTS ROM CANONICAL; do
        cp "$incremental_parent_root/build/FILEMANAGER-REGISTRATION-PARENT-868-$retained_fm_proof.json" "$output/FILEMANAGER-REGISTRATION-PARENT-868-$retained_fm_proof.json"
    done
    cp "$incremental_parent_root/build/FREETYPE-SPI-PARENT-864-ROM.json" "$output/FREETYPE-SPI-PARENT-864-ROM.json"
    cp "$incremental_parent_root/build/FREETYPE-SPI-PARENT-864-CANONICAL.json" "$output/FREETYPE-SPI-PARENT-864-CANONICAL.json"
fi
homescreen_build_root="$full_epocroot/epoc32/build/homescreen-build"
homescreen_main_obj=$(find "$homescreen_build_root" \
    -path '*/homescreen_exe/armv5/urel/main.o' -type f)
homescreen_aifw_obj=$(find "$homescreen_build_root" \
    -path '*/aifw_dll/armv5/urel/aifw.o' -type f)
homescreen_controller_obj=$(find "$homescreen_build_root" \
    -path '*/aifw_dll/armv5/urel/aiuicontrollermanager.o' -type f)
homescreen_ecom_obj=$(find "$homescreen_build_root" \
    -path '*/aifw_dll/armv5/urel/aiecomobserver.o' -type f)
homescreen_idle_obj=$(find "$homescreen_build_root" \
    -path '*/aiidleint_dll/armv5/urel/aiidleappregister.o' -type f)
homescreen_launch_obj=$(find "$homescreen_build_root" \
    -path '*/ailaunch_exe/armv5/urel/hslaunch.o' -type f)
for homescreen_object in "$homescreen_main_obj" "$homescreen_aifw_obj" \
    "$homescreen_controller_obj" \
    "$homescreen_ecom_obj" "$homescreen_idle_obj" "$homescreen_launch_obj"
do
    test -n "$homescreen_object" && test -s "$homescreen_object"
done
homescreen_disasm="$output/homescreen-gate16-durable-log-urel.disasm"
homescreen_controller_disasm="$output/homescreen-controller-ecom-retry-trace-urel.disasm"
homescreen_ecom_disasm="$output/homescreen-ecom-status-guard-urel.disasm"
homescreen_idle_disasm="$output/homescreen-active-idle-uid-urel.disasm"
homescreen_launch_disasm="$output/homescreen-ailaunch-supervisor-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$homescreen_aifw_obj" >"$homescreen_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$homescreen_controller_obj" >"$homescreen_controller_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$homescreen_ecom_obj" >"$homescreen_ecom_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$homescreen_idle_obj" >"$homescreen_idle_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$homescreen_launch_obj" >"$homescreen_launch_disasm"
grep -q 'HtcleoHomeLog' "$homescreen_disasm" "$homescreen_ecom_disasm" \
    "$homescreen_controller_disasm" "$homescreen_idle_disasm" \
    "$homescreen_launch_disasm"
grep -q 'CPeriodic' "$homescreen_disasm"
grep -q 'RProperty.*Set' "$homescreen_idle_disasm"
grep -q 'RProcess.*Create' "$homescreen_launch_disasm"
grep -q 'CAiUiController.*NewL' "$homescreen_controller_disasm"
grep -q 'KHtcleoMaxStartupCrashes\|484f0244' \
    "$homescreen_launch_disasm"
! grep -q 'e7f000f0\|c6400000' "$homescreen_disasm" \
    "$homescreen_ecom_disasm" "$homescreen_idle_disasm" \
    "$homescreen_launch_disasm"
for homescreen_dump_spec in \
    "aifw|$homescreen_aifw_binary" \
    "aiidleint|$homescreen_idle_binary" \
    "ailaunch|$homescreen_launch_binary" \
    "homescreen|$homescreen_binary"
do
    old_ifs=$IFS
    IFS='|'
    set -- $homescreen_dump_spec
    IFS=$old_ifs
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$2" >"$output/$1-e32-dump.txt"
    sha256sum "$2" >"$output/$1-urel.sha256"
done
sha256sum "$homescreen_main_obj" "$homescreen_aifw_obj" \
    "$homescreen_controller_obj" "$homescreen_ecom_obj" \
    "$homescreen_idle_obj" \
    "$homescreen_launch_obj" >"$output/homescreen-core-objects-urel.sha256"
sha256sum "$homescreen_aifw_stock_670" \
    >"$output/aifw-stock-670.sha256"
sha256sum "$homescreen_idle_stock_670" \
    >"$output/aiidleint-stock-670.sha256"
sha256sum "$homescreen_launch_stock_670" \
    >"$output/ailaunch-stock-670.sha256"
sha256sum "$homescreen_stock_670" \
    >"$output/homescreen-stock-670.sha256"

# Iteration 675 fixes discovery of the real XML controller, but EikStart still
# returns before a visible HomeScreen.  Source-build only ai3xmluimain.dll and
# trace its application/document/AppUi construction without normalizing any
# result.  The PDK ships ProfileEng.dso with mixed case; provide the Linux host
# spelling expected by the unchanged MMP.
test -s "$full_epocroot/epoc32/release/armv5/lib/ProfileEng.dso"
ln -sfn ProfileEng.dso \
    "$full_epocroot/epoc32/release/armv5/lib/profileeng.dso"
test -e "$full_epocroot/epoc32/release/armv5/lib/profileeng.dso"
if incremental_wants_binary "$ai3xml_binary"; then
    rm -f "$ai3xml_binary"
fi
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$ai3xml_bldinf" -c "$matrixmenu_config"
sbs_build_for "$ai3xml_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$ai3xml_bldinf" -c "$matrixmenu_config" -j 4
test -s "$ai3xml_binary"
ai3xml_build_root="$full_epocroot/epoc32/build/ai3xmluimain-build"
ai3xml_controller_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/xmluicontroller.o' -type f)
ai3xml_application_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/application.o' -type f)
ai3xml_document_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/document.o' -type f)
ai3xml_appui_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/appui.o' -type f)
ai3xml_contentpublisher_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/contentpublisher.o' -type f)
ai3xml_logger_obj=$(find "$ai3xml_build_root" \
    -path '*/ai3xmluimain_dll/armv5/urel/htcleoai3xmllog.o' -type f)
for ai3xml_object in "$ai3xml_controller_obj" "$ai3xml_application_obj" \
    "$ai3xml_document_obj" "$ai3xml_appui_obj" \
    "$ai3xml_contentpublisher_obj" "$ai3xml_logger_obj"
do
    test -n "$ai3xml_object" && test -s "$ai3xml_object"
done
ai3xml_disasm="$output/ai3xmluimain-startup-trace-urel.disasm"
: >"$ai3xml_disasm"
for ai3xml_object in "$ai3xml_controller_obj" "$ai3xml_application_obj" \
    "$ai3xml_document_obj" "$ai3xml_appui_obj" \
    "$ai3xml_contentpublisher_obj" "$ai3xml_logger_obj"
do
    "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
        "$ai3xml_object" >>"$ai3xml_disasm"
done
grep -q 'HtcleoAi3XmlLog' "$ai3xml_disasm"
grep -q 'EikStart.*RunApplication' "$ai3xml_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$ai3xml_disasm"
strings "$ai3xml_logger_obj" | grep -q 'HTCLEO_HXML '
strings -el "$ai3xml_logger_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|User::After\|HalFunction' \
    "$ai3xml_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$ai3xml_binary" >"$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Secure ID: 2001952a' "$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Vendor ID: 101fb657' "$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Uids:[[:space:]]*10000079 10009d8d 2001952a' \
    "$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Module Version: 10.0' "$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Number of exports = 1' "$output/ai3xmluimain-e32-dump.txt"
grep -qi 'Stack Size:[[:space:]]*00002000' \
    "$output/ai3xmluimain-e32-dump.txt"
sha256sum "$ai3xml_binary" >"$output/ai3xmluimain-urel.sha256"
sha256sum "$ai3xml_controller_obj" "$ai3xml_application_obj" \
    "$ai3xml_document_obj" "$ai3xml_appui_obj" \
    "$ai3xml_contentpublisher_obj" "$ai3xml_logger_obj" \
    >"$output/ai3xmluimain-core-objects-urel.sha256"
sha256sum "$ai3xml_stock_675" \
    >"$output/ai3xmluimain-stock-675.sha256"

# Iteration 680 reaches the real Xn adapter but terminates inside its exported
# ConstructL.  Build only xn3layoutengine.dll and record behavior-neutral
# boundaries around its base AppUi, toolbar/status-pane and implementation
# construction.  Linux aliases mirror the PDK's case-insensitive host lookup.
test -s "$full_epocroot/epoc32/release/armv5/lib/SvgEngine.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/MGFetch.dso"
ln -sfn SvgEngine.dso \
    "$full_epocroot/epoc32/release/armv5/lib/svgengine.dso"
ln -sfn MGFetch.dso \
    "$full_epocroot/epoc32/release/armv5/lib/mgfetch.dso"
test -e "$full_epocroot/epoc32/release/armv5/lib/svgengine.dso"
test -e "$full_epocroot/epoc32/release/armv5/lib/mgfetch.dso"
if incremental_wants_binary "$xn3layout_binary"; then
    rm -f "$xn3layout_binary"
fi
sbs_clean --configpath="$xn3layout_config_path" \
    -b "$xn3layout_bldinf" -c "$xn3layout_config"
sbs_build_for "$xn3layout_binary" -- \
    --configpath="$xn3layout_config_path" \
    -b "$xn3layout_bldinf" -c "$xn3layout_config" -j 4
test -s "$xn3layout_binary"
xn3layout_build_root="$full_epocroot/epoc32/build/xn3layoutengine-build"
xn3layout_generated_def=$(find "$xn3layout_build_root" \
    -path '*/xn3layoutengine_dll/armv5/urel/xn3layoutengine{000a0000}.def' \
    -type f -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
test -n "$xn3layout_generated_def" && test -s "$xn3layout_generated_def"
xn3layout_obj_dir=$(dirname "$xn3layout_generated_def")
xn3layout_adapter_obj="$xn3layout_obj_dir/xnappuiadapter.o"
xn3layout_adapter_impl_obj="$xn3layout_obj_dir/xnappuiadapterimpl.o"
xn3layout_engine_obj="$xn3layout_obj_dir/xnuiengineimpl.o"
xn3layout_utils_obj="$xn3layout_obj_dir/xnutils.o"
xn3layout_control_obj="$xn3layout_obj_dir/xncontroladapterimpl.o"
xn3layout_viewmanager_obj="$xn3layout_obj_dir/xnviewmanager.o"
xn3layout_rootdata_obj="$xn3layout_obj_dir/xnrootdata.o"
xn3layout_composer_obj="$xn3layout_obj_dir/xncomposer.o"
xn3layout_odtparser_obj="$xn3layout_obj_dir/xnodtparser.o"
xn3layout_viewdata_obj="$xn3layout_obj_dir/xnviewdata.o"
for xn3layout_object in "$xn3layout_adapter_obj" \
    "$xn3layout_adapter_impl_obj" "$xn3layout_engine_obj" \
    "$xn3layout_utils_obj" "$xn3layout_control_obj" \
    "$xn3layout_viewmanager_obj" "$xn3layout_rootdata_obj" \
    "$xn3layout_composer_obj" "$xn3layout_odtparser_obj" \
    "$xn3layout_viewdata_obj"
do
    test -s "$xn3layout_object"
done
for xn3layout_promote_object in "$xn3layout_engine_obj" \
    "$xn3layout_utils_obj" "$xn3layout_control_obj"
do
    xn3layout_promote_result=$(python3 "$xn3layout_abi_promoter" \
        "$xn3layout_promote_object")
    echo "$xn3layout_promote_result"
    printf '%s\n' "$xn3layout_promote_result" | grep -q '=installed '
done
python3 "$xn3layout_abi_audit" "$xn3layout_frozen_def" \
    "$xn3layout_generated_def" "$output"
grep -qx 'STATUS=HTCLEO_XN3LAYOUTENGINE_ABI_OK' \
    "$output/XN3LAYOUTENGINE-ABI-RESULT.txt"
grep -qx 'FROZEN_EXPORTS=278' \
    "$output/XN3LAYOUTENGINE-ABI-RESULT.txt"
grep -qx 'GENERATED_EXPORTS=281' \
    "$output/XN3LAYOUTENGINE-ABI-RESULT.txt"
xn3layout_disasm="$output/xn3layoutengine-appuiadapter-startup-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$xn3layout_adapter_obj" >"$xn3layout_disasm"
xn3layout_impl_disasm="$output/xn3layoutengine-appuiadapterimpl-startup-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$xn3layout_adapter_impl_obj" >"$xn3layout_impl_disasm"
grep -q 'HtcleoXnAdapterLog' "$xn3layout_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$xn3layout_disasm"
grep -q 'CXnAppUiAdapter.*ConstructL' "$xn3layout_disasm"
grep -q 'CAknViewAppUi.*BaseConstructL' "$xn3layout_disasm"
grep -qi '48581000' "$xn3layout_disasm"
grep -qi '48581010' "$xn3layout_disasm"
strings "$xn3layout_adapter_obj" | grep -Fq 'HTCLEO_HXA  '
strings -el "$xn3layout_adapter_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|User::After\|HalFunction' \
    "$xn3layout_disasm"
grep -q 'HtcleoXnAdapterImplLog' "$xn3layout_impl_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$xn3layout_impl_disasm"
grep -q 'CXnAppUiAdapterImpl.*ConstructL' "$xn3layout_impl_disasm"
grep -qi '48581100' "$xn3layout_impl_disasm"
grep -qi '48581124' "$xn3layout_impl_disasm"
strings "$xn3layout_adapter_impl_obj" | grep -Fq 'HTCLEO_HXI  '
strings -el "$xn3layout_adapter_impl_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|User::After\|HalFunction' \
    "$xn3layout_impl_disasm"
xn3layout_loadui_disasm="$output/xn3layoutengine-loadui-trace-urel.disasm"
: >"$xn3layout_loadui_disasm"
for xn3layout_loadui_obj in "$xn3layout_viewmanager_obj" \
    "$xn3layout_rootdata_obj" "$xn3layout_composer_obj" \
    "$xn3layout_odtparser_obj" "$xn3layout_viewdata_obj"
do
    "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
        "$xn3layout_loadui_obj" >>"$xn3layout_loadui_disasm"
done
grep -q 'HtcleoXnLoadUiLog' "$xn3layout_loadui_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$xn3layout_loadui_disasm"
grep -qi '48581500' "$xn3layout_loadui_disasm"
grep -qi '4858150c' "$xn3layout_loadui_disasm"
grep -qi '48581520' "$xn3layout_loadui_disasm"
grep -qi '4858153e' "$xn3layout_loadui_disasm"
grep -qi '48581555' "$xn3layout_loadui_disasm"
grep -qi '48581567' "$xn3layout_loadui_disasm"
grep -qi '48581570' "$xn3layout_loadui_disasm"
grep -qi '48581578' "$xn3layout_loadui_disasm"
grep -qi '485815a7' "$xn3layout_loadui_disasm"
grep -qi '485815ab' "$xn3layout_loadui_disasm"
grep -qi '4858152e' "$xn3layout_loadui_disasm"
grep -qi '4858152f' "$xn3layout_loadui_disasm"
! grep -q 'e7f000f0\|c6400000\|User::After\|HalFunction' \
    "$xn3layout_loadui_disasm"
cp "$xn3layout_stock_680" "$xn3layout_stock_dump_input"
test "$(sha256sum "$xn3layout_stock_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$xn3layout_stock_680" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$xn3layout_stock_dump_input" \
    >"$output/xn3layoutengine-stock-680-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$xn3layout_binary" \
    >"$output/xn3layoutengine-e32-dump.txt"
for xn3layout_dump in "$output/xn3layoutengine-stock-680-e32-dump.txt" \
    "$output/xn3layoutengine-e32-dump.txt"
do
    grep -qi 'Secure ID: 2001cb50' "$xn3layout_dump"
    grep -qi 'Vendor ID: 101fb657' "$xn3layout_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$xn3layout_dump"
    grep -qi 'Uids:.*10000079 1000008d 2001cb50' "$xn3layout_dump"
    grep -qi 'Module Version: 10.0' "$xn3layout_dump"
    grep -qi 'Stack Size:[[:space:]]*00002000' "$xn3layout_dump"
done
grep -q 'Export.*(278 entries)' \
    "$output/xn3layoutengine-stock-680-e32-dump.txt"
grep -q 'Export.*(281 entries)' "$output/xn3layoutengine-e32-dump.txt"
sha256sum "$xn3layout_binary" >"$output/xn3layoutengine-urel.sha256"
sha256sum "$xn3layout_adapter_obj" \
    >"$output/xn3layoutengine-appuiadapter-object-urel.sha256"
sha256sum "$xn3layout_adapter_impl_obj" \
    >"$output/xn3layoutengine-appuiadapterimpl-object-urel.sha256"
sha256sum "$xn3layout_viewmanager_obj" "$xn3layout_rootdata_obj" \
    "$xn3layout_composer_obj" "$xn3layout_odtparser_obj" \
    "$xn3layout_viewdata_obj" \
    >"$output/xn3layoutengine-loadui-objects-urel.sha256"
sha256sum "$xn3layout_stock_680" \
    >"$output/xn3layoutengine-stock-680.sha256"

# Hardware 689 returns from the complete Xn/Avkon base chain and stops inside
# CHomescreenSettings::InitializeL.  Source-build only hspluginsettings.dll and
# expose behavior-neutral TLS/LIW/HSPS boundaries through the shared HSXML log.
if incremental_wants_binary "$hspluginsettings_binary"; then
    rm -f "$hspluginsettings_binary"
fi
sbs_clean --configpath="$hspluginsettings_config_path" \
    -b "$hspluginsettings_bldinf" -c "$hspluginsettings_config"
sbs_build_for "$hspluginsettings_binary" -- \
    --configpath="$hspluginsettings_config_path" \
    -b "$hspluginsettings_bldinf" -c "$hspluginsettings_config" -j 4
test -s "$hspluginsettings_binary"
hspluginsettings_build_root="$full_epocroot/epoc32/build/hspluginsettings-build"
hspluginsettings_generated_def=$(find "$hspluginsettings_build_root" \
    -path '*/hspluginsettings_dll/armv5/urel/hspluginsettings{000a0000}.def' \
    -type f -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)
test -n "$hspluginsettings_generated_def" && test -s "$hspluginsettings_generated_def"
hspluginsettings_obj_dir=$(dirname "$hspluginsettings_generated_def")
hspluginsettings_obj="$hspluginsettings_obj_dir/hspluginsettings.o"
test -s "$hspluginsettings_obj"
python3 "$hspluginsettings_abi_audit" "$hspluginsettings_frozen_def" \
    "$hspluginsettings_generated_def" "$output"
grep -qx 'STATUS=HTCLEO_HSPLUGINSETTINGS_ABI_OK' \
    "$output/HSPLUGINSETTINGS-ABI-RESULT.txt"
grep -qx 'FROZEN_EXPORTS=90' \
    "$output/HSPLUGINSETTINGS-ABI-RESULT.txt"
grep -qx 'GENERATED_EXPORTS=90' \
    "$output/HSPLUGINSETTINGS-ABI-RESULT.txt"
hspluginsettings_disasm="$output/hspluginsettings-startup-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hspluginsettings_obj" >"$hspluginsettings_disasm"
grep -q 'HtcleoHsPluginSettingsLog' "$hspluginsettings_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hspluginsettings_disasm"
grep -q 'CHomescreenSettings.*InitializeL' "$hspluginsettings_disasm"
grep -q 'CLiwServiceHandler.*NewL' "$hspluginsettings_disasm"
grep -qi '48581200' "$hspluginsettings_disasm"
grep -qi '4858123f' "$hspluginsettings_disasm"
strings "$hspluginsettings_obj" | grep -Fq 'HTCLEO_HPS  '
strings -el "$hspluginsettings_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|User::After\|HalFunction' \
    "$hspluginsettings_disasm"
cp "$hspluginsettings_stock_689" "$hspluginsettings_stock_dump_input"
test "$(sha256sum "$hspluginsettings_stock_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$hspluginsettings_stock_689" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspluginsettings_stock_dump_input" \
    >"$output/hspluginsettings-stock-689-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspluginsettings_binary" \
    >"$output/hspluginsettings-e32-dump.txt"
for hspluginsettings_dump in \
    "$output/hspluginsettings-stock-689-e32-dump.txt" \
    "$output/hspluginsettings-e32-dump.txt"
do
    grep -qi 'Secure ID: 00000000' "$hspluginsettings_dump"
    grep -qi 'Vendor ID: 101fb657' "$hspluginsettings_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$hspluginsettings_dump"
    grep -qi 'Uids:.*10000079 20022fe0 00000000' "$hspluginsettings_dump"
    grep -qi 'Module Version: 10.0' "$hspluginsettings_dump"
    grep -qi 'Number of exports = 90' "$hspluginsettings_dump"
done
sha256sum "$hspluginsettings_stock_689" \
    >"$output/hspluginsettings-stock-689.sha256"
sha256sum "$hspluginsettings_binary" \
    >"$output/hspluginsettings-urel.sha256"
sha256sum "$hspluginsettings_obj" \
    >"$output/hspluginsettings-object-urel.sha256"

# Hardware 690 proves HSPS is reached but the real HomeScreen ODT is absent.
# Build only the Theme Server with an HTC Leo 480x800 -> shipped qhd_tch
# family mapping, a missing-root reinstall guard and a one-MiB bootstrap log.
if incremental_wants_binary "$hspsthemeserver_binary"; then
    rm -f "$hspsthemeserver_binary"
fi
hspsthemeserver_import_lib_dir="$full_epocroot/epoc32/release/armv5/lib"
test -s "$hspsthemeserver_import_lib_dir/syslangutil.dso"
if [ ! -s "$hspsthemeserver_import_lib_dir/SysLangUtil.dso" ]; then
    cp "$hspsthemeserver_import_lib_dir/syslangutil.dso" \
        "$hspsthemeserver_import_lib_dir/SysLangUtil.dso"
fi
cmp "$hspsthemeserver_import_lib_dir/syslangutil.dso" \
    "$hspsthemeserver_import_lib_dir/SysLangUtil.dso"
sbs_clean --configpath="$hspsthemeserver_config_path" \
    -b "$hspsthemeserver_bldinf" -c "$hspsthemeserver_config"
sbs_build_for "$hspsthemeserver_binary" -- \
    --configpath="$hspsthemeserver_config_path" \
    -b "$hspsthemeserver_bldinf" -c "$hspsthemeserver_config" -j 4
test -s "$hspsthemeserver_binary"
hspsthemeserver_build_root="$full_epocroot/epoc32/build/hspsthemeserver-build"
hspsthemeserver_server_obj=$(find "$hspsthemeserver_build_root" \
    -path '*/hspsthemeserver_exe/armv5/urel/hspsthemeserver.o' -type f)
hspsthemeserver_family_obj=$(find "$hspsthemeserver_build_root" \
    -path '*/hspsthemeserver_exe/armv5/urel/hspsfamily.o' -type f)
hspsthemeserver_rominstaller_obj=$(find "$hspsthemeserver_build_root" \
    -path '*/hspsthemeserver_exe/armv5/urel/hspsrominstaller.o' -type f)
hspsthemeserver_installation_obj=$(find "$hspsthemeserver_build_root" \
    -path '*/hspsthemeserver_exe/armv5/urel/hspsinstallationhandler.o' -type f)
test "$(printf '%s\n' "$hspsthemeserver_server_obj" | sed '/^$/d' | wc -l)" -eq 1
test "$(printf '%s\n' "$hspsthemeserver_family_obj" | sed '/^$/d' | wc -l)" -eq 1
test "$(printf '%s\n' "$hspsthemeserver_rominstaller_obj" | sed '/^$/d' | wc -l)" -eq 1
test "$(printf '%s\n' "$hspsthemeserver_installation_obj" | sed '/^$/d' | wc -l)" -eq 1
test -s "$hspsthemeserver_server_obj"
test -s "$hspsthemeserver_family_obj"
test -s "$hspsthemeserver_rominstaller_obj"
test -s "$hspsthemeserver_installation_obj"
hspsthemeserver_disasm="$output/hspsthemeserver-hd2-family-compat-urel.disasm"
for hspsthemeserver_obj in "$hspsthemeserver_server_obj" \
    "$hspsthemeserver_family_obj" "$hspsthemeserver_rominstaller_obj" \
    "$hspsthemeserver_installation_obj"
do
    "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
        "$hspsthemeserver_obj"
done >"$hspsthemeserver_disasm"
grep -q 'HtcleoHspsServerLog' "$hspsthemeserver_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hspsthemeserver_disasm"
grep -qi '485813f0' "$hspsthemeserver_disasm"
grep -qi '48581336' "$hspsthemeserver_disasm"
grep -qi '48581373' "$hspsthemeserver_disasm"
grep -qi '48581379' "$hspsthemeserver_disasm"
grep -qi '4858135b' "$hspsthemeserver_disasm"
grep -qi '48581390' "$hspsthemeserver_disasm"
grep -qi '485813b0' "$hspsthemeserver_disasm"
grep -qi '485813c0' "$hspsthemeserver_disasm"
grep -qi '485813d0' "$hspsthemeserver_disasm"
grep -qi '485813e0' "$hspsthemeserver_disasm"
grep -qi '485813e4' "$hspsthemeserver_disasm"
grep -q 'REComSession.*FinalClose' "$hspsthemeserver_disasm"
strings "$hspsthemeserver_family_obj" | grep -Fq 'HTCLEO_HSS  '
strings -el "$hspsthemeserver_family_obj" | \
    grep -Fq 'C:\Symbian3\HSPSSRV.TXT'
cp "$hspsthemeserver_stock_690" "$hspsthemeserver_stock_dump_input"
test "$(sha256sum "$hspsthemeserver_stock_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$hspsthemeserver_stock_690" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspsthemeserver_stock_dump_input" \
    >"$output/hspsthemeserver-stock-690-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspsthemeserver_binary" \
    >"$output/hspsthemeserver-e32-dump.txt"
for hspsthemeserver_dump in \
    "$output/hspsthemeserver-stock-690-e32-dump.txt" \
    "$output/hspsthemeserver-e32-dump.txt"
do
    grep -qi 'Secure ID: 200159c0' "$hspsthemeserver_dump"
    grep -qi 'Vendor ID: 101fb657' "$hspsthemeserver_dump"
    grep -q 'Capabilities: 00000000 000fffbe' "$hspsthemeserver_dump"
    grep -qi 'Uids:.*1000007a 1000008d 200159c0' "$hspsthemeserver_dump"
    grep -qi 'Module Version: 10.0' "$hspsthemeserver_dump"
    grep -qi 'Min Heap Size:[[:space:]]*00001000' "$hspsthemeserver_dump"
    grep -qi 'Max Heap Size:[[:space:]]*00400000' "$hspsthemeserver_dump"
    grep -qi 'Stack Size:[[:space:]]*00005000' "$hspsthemeserver_dump"
    grep -qi 'Number of exports = 0' "$hspsthemeserver_dump"
done
sha256sum "$hspsthemeserver_stock_690" \
    >"$output/hspsthemeserver-stock-690.sha256"
sha256sum "$hspsthemeserver_binary" \
    >"$output/hspsthemeserver-urel.sha256"
sha256sum "$hspsthemeserver_server_obj" "$hspsthemeserver_family_obj" \
    "$hspsthemeserver_rominstaller_obj" "$hspsthemeserver_installation_obj" \
    >"$output/hspsthemeserver-objects-urel.sha256"

# Hardware 697 proves the outer ECom response, DLL load, proxy lookup and
# instance bookkeeping all succeed; the real definition-engine factory leaves
# while ConstructL creates a nested ECom XML parser.  Build the plugin with the
# parser deferred until CreateDOM, after the outer factory has returned.
if incremental_wants_binary "$hsps_definition_binary"; then
    rm -f "$hsps_definition_binary"
fi
sbs_clean -b "$hsps_definition_bldinf" -c "$ssm_config"
sbs_build_for "$hsps_definition_binary" -- \
    -b "$hsps_definition_bldinf" -c "$ssm_config" -j 4
test -s "$hsps_definition_binary"
hsps_definition_build_root="$full_epocroot/epoc32/build/hspsdefinitionengine"
hsps_definition_obj=$(find "$hsps_definition_build_root" \
    -path '*/hspsdefinitionengine_dll/armv5/urel/hspsdefinitionengine.o' \
    -type f | head -n 1)
hsps_definition_proxy_obj=$(find "$hsps_definition_build_root" \
    -path '*/hspsdefinitionengine_dll/armv5/urel/hspsdefinitionengineproxy.o' \
    -type f | head -n 1)
hsps_definition_xml_obj=$(find "$hsps_definition_build_root" \
    -path '*/hspsdefinitionengine_dll/armv5/urel/hspsxmlhandler.o' \
    -type f | head -n 1)
for hsps_definition_artifact in "$hsps_definition_obj" \
    "$hsps_definition_proxy_obj" "$hsps_definition_xml_obj"
do
    test -n "$hsps_definition_artifact" && test -s "$hsps_definition_artifact"
done
hsps_definition_disasm="$output/hspsdefinitionengine-lazy-parser-urel.disasm"
for hsps_definition_trace_obj in "$hsps_definition_obj" "$hsps_definition_xml_obj"
do
    "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
        "$hsps_definition_trace_obj"
done >"$hsps_definition_disasm"
test "$(grep -c 'R_ARM_.*CALL.*ChspsXMLHandler4NewL' \
    "$hsps_definition_disasm")" -eq 1
grep -q 'ParseXmlDocL' "$hsps_definition_disasm"
grep -qi '485814e0' "$hsps_definition_disasm"
grep -qi '485814eb' "$hsps_definition_disasm"
grep -qi '485814f0' "$hsps_definition_disasm"
grep -qi '485814fb' "$hsps_definition_disasm"
! grep -q 'REComSession.*FinalClose' "$hsps_definition_disasm"
! grep -q 'User::After\|e7f000f0\|c6400000' "$hsps_definition_disasm"
cp "$hsps_definition_stock_697" "$hsps_definition_stock_dump_input"
test "$(sha256sum "$hsps_definition_stock_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$hsps_definition_stock_697" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hsps_definition_stock_dump_input" \
    >"$output/hspsdefinitionengine-stock-697-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hsps_definition_binary" \
    >"$output/hspsdefinitionengine-e32-dump.txt"
for hsps_definition_dump in \
    "$output/hspsdefinitionengine-stock-697-e32-dump.txt" \
    "$output/hspsdefinitionengine-e32-dump.txt"
do
    grep -qi 'Secure ID: 200159ba' "$hsps_definition_dump"
    grep -qi 'Vendor ID: 101fb657' "$hsps_definition_dump"
    grep -qi 'Uids:.*10000079 10009d8d 200159ba' "$hsps_definition_dump"
    grep -qi 'Module Version: 10.0' "$hsps_definition_dump"
    grep -qi 'Number of exports = 1' "$hsps_definition_dump"
done
sha256sum "$hsps_definition_stock_697" \
    >"$output/hspsdefinitionengine-stock-697.sha256"
sha256sum "$hsps_definition_binary" \
    >"$output/hspsdefinitionengine-urel.sha256"
sha256sum "$hsps_definition_obj" "$hsps_definition_proxy_obj" \
    "$hsps_definition_xml_obj" \
    >"$output/hspsdefinitionengine-objects-urel.sha256"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$libxml_sax_binary" \
    >"$output/xmlenginesaxplugin-e32-dump.txt"
grep -qi 'Secure ID: 101f9782' "$output/xmlenginesaxplugin-e32-dump.txt"
grep -qi 'Vendor ID: 70000001' "$output/xmlenginesaxplugin-e32-dump.txt"
grep -qi 'Uids:.*10000079 10009d8d 101f9782' \
    "$output/xmlenginesaxplugin-e32-dump.txt"
grep -qi 'Module Version: 10.0' "$output/xmlenginesaxplugin-e32-dump.txt"
grep -qi 'Number of exports = 1' "$output/xmlenginesaxplugin-e32-dump.txt"
sha256sum "$libxml_sax_binary" \
    >"$output/xmlenginesaxplugin-urel.sha256"
sha256sum "$libxml_sax_resource" \
    >"$output/xmlenginesaxplugin-resource.sha256"
cp "$libxml_sax_binary" "$output/xmlenginesaxplugin-stock-701.dll"
cp "$libxml_sax_resource" "$output/xmlenginesaxplugin-stock-701.rsc"

# Hardware 703 proves that the active root configuration survives through its
# real Xuikon ODT but reaches ComposeRoot with zero CPluginMap entries.  Build
# the SAPI provider with a schema-owned root plugins lookup and bounded trace.
if incremental_wants_binary "$hspsprovider_binary"; then
    rm -f "$hspsprovider_binary"
fi
sbs_clean --configpath="$hspsprovider_config_path" \
    -b "$hspsprovider_bldinf" -c "$hspsprovider_config"
sbs_build_for "$hspsprovider_binary" -- \
    --configpath="$hspsprovider_config_path" \
    -b "$hspsprovider_bldinf" -c "$hspsprovider_config" -j 4
test -s "$hspsprovider_binary"
hspsprovider_build_root="$full_epocroot/epoc32/build/hspsprovider-build"
hspsprovider_obj=$(find "$hspsprovider_build_root" \
    -path '*/hspsprovider_dll/armv5/urel/hspsliwutilities.o' \
    -type f | head -n 1)
test -n "$hspsprovider_obj" && test -s "$hspsprovider_obj"
hspsprovider_disasm="$output/hspsprovider-plugin-map-compat-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hspsprovider_obj" >"$hspsprovider_disasm"
grep -q 'HtcleoHspsProviderLog' "$hspsprovider_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hspsprovider_disasm"
test "$(grep -c 'HTCLEO_HSPSPROVIDER_LOG_RETIREMENT_V1' "$hspsprovider_source")" -eq 1
grep -qi '48581615' "$hspsprovider_disasm"
strings "$hspsprovider_obj" | grep -Fq 'HTCLEO_HPRV '
strings -el "$hspsprovider_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'User::After\|e7f000f0\|c6400000\|HalFunction' \
    "$hspsprovider_disasm"
cp "$hspsprovider_stock_703" "$hspsprovider_stock_dump_input"
test "$(sha256sum "$hspsprovider_stock_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$hspsprovider_stock_703" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspsprovider_stock_dump_input" \
    >"$output/hspsprovider-stock-703-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hspsprovider_binary" \
    >"$output/hspsprovider-e32-dump.txt"
for hspsprovider_dump in \
    "$output/hspsprovider-stock-703-e32-dump.txt" \
    "$output/hspsprovider-e32-dump.txt"
do
    grep -qi 'Secure ID: 200159b7' "$hspsprovider_dump"
    grep -qi 'Vendor ID: 101fb657' "$hspsprovider_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$hspsprovider_dump"
    grep -qi 'Uids:.*10000079 10009d8d 200159b7' "$hspsprovider_dump"
    grep -qi 'Module Version: 10.0' "$hspsprovider_dump"
    grep -qi 'Number of exports = 1' "$hspsprovider_dump"
done
# Keep the ECom registration payload byte-identical; 704 changes only code.
cp "$hspsprovider_stock_resource_703" "$hspsprovider_resource"
test "$(sha256sum "$hspsprovider_resource" | awk '{print $1}')" = \
    55bd6b71b8af2af0789db905b45b6389f5ad67b6812efb1271eec51be9989633
sha256sum "$hspsprovider_stock_703" \
    >"$output/hspsprovider-stock-703.sha256"
sha256sum "$hspsprovider_binary" \
    >"$output/hspsprovider-urel.sha256"
sha256sum "$hspsprovider_resource" \
    >"$output/hspsprovider-resource.sha256"
sha256sum "$hspsprovider_obj" \
    >"$output/hspsprovider-object-urel.sha256"
# Rebuild the CLE custom-command state machine with the exact AknCapServer
# ordinal-1 trace. Keep the PDK's first 91 frozen exports at their original
# ordinals; GCCE-only nested timer symbols may append at 92-100, never shift
# the frozen ABI.
sbs_clean -b "$ssm_custom_bldinf" -c "$ssm_config"
sbs_build_for "$ssm_custom_binary" -- \
    -b "$ssm_custom_bldinf" -c "$ssm_config" -j 4
test -s "$ssm_custom_binary"
test "$(find "$full_epocroot/epoc32/build/cmd" \
    -path '*/ssmcmd_dll/armv5/urel/cmdcustomcommand.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/cmd" \
    -path '*/ssmcmd_dll/armv5/urel/ssmcmd*.def' -type f | wc -l)" -eq 1
ssm_custom_obj=$(find "$full_epocroot/epoc32/build/cmd" \
    -path '*/ssmcmd_dll/armv5/urel/cmdcustomcommand.o' -type f)
ssm_custom_generated_def=$(find "$full_epocroot/epoc32/build/cmd" \
    -path '*/ssmcmd_dll/armv5/urel/ssmcmd*.def' -type f)
test -s "$ssm_custom_obj"
test -s "$ssm_custom_generated_def"
ssm_custom_disasm="$output/custom-command-state-machine-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ssm_custom_obj" >"$ssm_custom_disasm"
grep -q 'HtcleoCustomCmdLog' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*_ZN7RLoader7ConnectEv' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*_ZN7RLoader11LoadLibrary' "$ssm_custom_disasm"
test "$(grep -c '4778[[:space:]]*bx[[:space:]]*pc' \
    "$ssm_custom_disasm")" -eq 2
test "$(grep -c 'ef00009f.*svc' "$ssm_custom_disasm")" -eq 1
test "$(grep -c 'ef0000a0.*svc' "$ssm_custom_disasm")" -eq 1
test "$(grep -c 'e12fff1e[[:space:]]*bx[[:space:]]*lr' \
    "$ssm_custom_disasm")" -eq 2
! grep -q 'df9f.*svc\|dfa0.*svc' "$ssm_custom_disasm"
test "$(grep -c 'bl.*HtcleoAknLibraryAttachExec' \
    "$ssm_custom_disasm")" -eq 7
grep -q 'HtcleoAknAttachWatchThread' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*Create' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*SetPriority' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RSemaphore.*Wait' "$ssm_custom_disasm"
grep -q 'R_ARM_.*CALL.*RSemaphore.*Signal' "$ssm_custom_disasm"
! grep -q 'R_ARM_.*CALL.*_ZN8RLibrary4InitEv' "$ssm_custom_disasm"
# With the larger init-trace frame GCCE now folds 0x0000c100 through r7 and
# moves the shifted value to r0.  Require that exact construction, then require
# the remaining eight literal stages; do not require the obsolete r0-only fold.
grep -q 'movs[[:space:]]\+r7, #193.*0xc1' "$ssm_custom_disasm"
grep -q 'lsls[[:space:]]\+r0, r7, #8' "$ssm_custom_disasm"
for ssm_load_split_stage in 1 2 3 4 5 6 7 8
do
    grep -q "0000c10${ssm_load_split_stage}" "$ssm_custom_disasm"
done
strings "$ssm_custom_obj" | grep -Fq 'HTCLEO_CUST '
strings -el "$ssm_custom_obj" | grep -Fq 'C:\Symbian3\CUSTLOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$ssm_custom_disasm"
tr -d '\r' <"$ssm_custom_def" | sed '/^[[:space:]]*$/d' \
    >"$output/ssmcmd-frozen-exports.def"
tr -d '\r' <"$ssm_custom_generated_def" | sed '/^[[:space:]]*$/d' \
    >"$output/ssmcmd-generated-exports.def"
test "$(wc -l <"$output/ssmcmd-frozen-exports.def")" -eq 92
test "$(wc -l <"$output/ssmcmd-generated-exports.def")" -eq 102
head -n 92 "$output/ssmcmd-generated-exports.def" \
    >"$output/ssmcmd-generated-frozen-prefix.def"
diff -u "$output/ssmcmd-frozen-exports.def" \
    "$output/ssmcmd-generated-frozen-prefix.def"
test "$(sed -n '93p' "$output/ssmcmd-generated-exports.def")" = '; NEW:'
test "$(tail -n +94 "$output/ssmcmd-generated-exports.def" | \
    grep -E '@[[:space:]]+(9[2-9]|100)[[:space:]]+NONAME$' | wc -l)" -eq 9
for ssm_custom_export in \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimer10ConstructLEv @ 92 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimer10StartTimerEl @ 93 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimer4NewLERS_ @ 94 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimer4RunLEv @ 95 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimerC1ERS_ @ 96 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimerC2ERS_ @ 97 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimerD0Ev @ 98 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimerD1Ev @ 99 NONAME' \
    '_ZN16CCmdMultipleWait18CMultipleWaitTimerD2Ev @ 100 NONAME'
do
    grep -Fq "$ssm_custom_export" "$output/ssmcmd-generated-exports.def"
done
rm -f "$output/ssmcmd-generated-frozen-prefix.def"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$ssm_custom_binary" >"$output/ssmcmd-e32-dump.txt"
grep -q 'Secure ID: 2000d761' "$output/ssmcmd-e32-dump.txt"
grep -q 'Number of exports = 100' "$output/ssmcmd-e32-dump.txt"
sha256sum "$ssm_custom_binary" >"$output/ssmcmd-urel.sha256"
sha256sum "$ssm_custom_obj" \
    >"$output/ssmcmd-custom-command-object-urel.sha256"

# Rebuild the two CLE static libraries first. The PDK copies were produced by
# RVCT and otherwise leave hidden __ARM_switch8 references in a GCCE link.
sbs_clean -b "$ssm_cle_bldinf" -c "$ssm_config"
sbs_build_for "$ssm_binary" -- \
    -b "$ssm_cle_bldinf" -c "$ssm_config" -j 4
sbs_build_for "$ssm_binary" -- \
    -b "$ssm_bldinf" -c "$ssm_config" -j 4
test -s "$ssm_binary"

# Gate 11 is hardware-proven by iteration 430.  Rebuild the exact AppArc
# server/list pair now blocking the UI command list and record its initial
# application scan in APALOG.TXT.  CLEAN keeps the two new logger translation
# units and the circular APSERV/APLIST import libraries coherent.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$apparc_forced_native" "$full_epocroot"
    apparc_forced_native_policy=native-only-explicit-full-forced-path-on-SID-check-NotFound-no-unlisted-or-Java-bypass-1460
    sbs_build_for "$apparc_aplist_binary" -- \
        -b "$apparc_bldinf" -p APLIST.MMP -c "$ssm_config" -j 4
    python3 "$apparc_enumeration_end" "$full_epocroot"
    apparc_enumeration_end_policy=GetNextApp-empty-list-native-Complete-NotFound-not-Leave-no-other-errors-changed-1470
    python3 "$apparc_empty_icon_name" "$full_epocroot"
    apparc_empty_icon_name_policy=IconFileName-empty-native-Complete-NotFound-no-unwind-no-new-IO-no-style-or-other-error-change
    python3 "$apparc_preload_publication" "$full_epocroot"
    apparc_preload_publication_policy=ailaunch-SID200286e3-nonempty-offline-preload-normal-observed-scan-native-notify-other-installers-deferred-1480
    python3 "$filemanager_launch_prep" "$full_epocroot"
    filemanager_launch_prep_policy=FileManager-only-native-rule-and-opaque-IPC-boundaries-existing-MLAUNCH128-no-Flush-retry-or-policy-change-2c00-2c13
    sbs_build_for "$apparc_apserv_binary" -- \
        -b "$apparc_bldinf" -p APSERV.MMP -c "$ssm_config" -j 4
    python3 "$apparc_terminal_exception" "$full_epocroot"
    apparc_terminal_exception_policy=APSEXE-only-no-existing-handler-APX1-terminal1024-stack224-no-startup-IO-restore-reraise
    sbs_build_for "$apparc_apsexe_binary" -- \
        -b "$apparc_bldinf" -p APSEXE.MMP -c "$ssm_config" -j 4
else
    sbs_clean -b "$apparc_bldinf" -c "$ssm_config"
    sbs_build_for "$apparc_aplist_binary" "$apparc_apserv_binary" \
        "$apparc_apsexe_binary" -- \
        -b "$apparc_bldinf" -c "$ssm_config" -j 4
fi
test -s "$apparc_aplist_binary"
test -s "$apparc_apserv_binary"
test -s "$apparc_apsexe_binary"
# The AppArc bld.inf relinks its circular APSERV/APLIST pair together.  Keep an
# incremental first-scan iteration exact by restoring every non-allowlisted
# sibling from the verified immutable parent cache.
restore_incremental_sibling_output "$apparc_aplist_binary"
restore_incremental_sibling_output "$apparc_apserv_binary"
restore_incremental_sibling_output "$apparc_apsexe_binary"
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-apparc-forced-native.py" --native "$incremental_parent_root/build" --report "$output/APPARC-FORCED-NATIVE-PARENT-869-OBJECTS.json"
    for retained_forced869 in aplist-forced-native-869-full-dump.txt aplist-forced-native-869.map aplist-forced-native-869.sym aplappregfinder-869.cpp; do
        cp "$incremental_parent_root/build/$retained_forced869" "$output/$retained_forced869"
    done
    cp "$incremental_parent_root/build/APPARC-FORCED-NATIVE-PARENT-869-ROM.json" "$output/APPARC-FORCED-NATIVE-PARENT-869-ROM.json"
    cp "$incremental_parent_root/build/APPARC-FORCED-NATIVE-PARENT-869-CANONICAL.json" "$output/APPARC-FORCED-NATIVE-PARENT-869-CANONICAL.json"
    cp "$incremental_parent_root/build/APPARC-ENUMERATION-END-PARENT-872-OBJECTS.json" "$output/APPARC-ENUMERATION-END-PARENT-872-OBJECTS.json"
    for retained_end872 in apserv-enumeration-872-full-dump.txt apserv-enumeration-872.map apserv-enumeration-872.sym APSSES-872.CPP; do
        cp "$incremental_parent_root/build/$retained_end872" "$output/$retained_end872"
    done
    cp "$incremental_parent_root/build/APPARC-ENUMERATION-END-PARENT-872-ROM.json" "$output/APPARC-ENUMERATION-END-PARENT-872-ROM.json"
    cp "$incremental_parent_root/build/APPARC-ENUMERATION-END-PARENT-872-CANONICAL.json" "$output/APPARC-ENUMERATION-END-PARENT-872-CANONICAL.json"
    python3 "$project/Symbian/scripts/verify-htcleo-apparc-terminal-exception.py" --native "$incremental_parent_root/build" --report "$output/APPARC-TERMINAL-EXCEPTION-PARENT-873-OBJECTS.json"
    for retained_terminal873 in apsexe-exception-873-full-dump.txt apsexe-exception-873.map apsexe-exception-873.sym APSMAIN-873.CPP APSEXE-873.MMP; do
        cp "$incremental_parent_root/build/$retained_terminal873" "$output/$retained_terminal873"
    done
    cp "$incremental_parent_root/build/APPARC-TERMINAL-EXCEPTION-PARENT-873-ROM.json" "$output/APPARC-TERMINAL-EXCEPTION-PARENT-873-ROM.json"
    cp "$incremental_parent_root/build/APPARC-TERMINAL-EXCEPTION-PARENT-873-CANONICAL.json" "$output/APPARC-TERMINAL-EXCEPTION-PARENT-873-CANONICAL.json"
    for retained_icon874 in APPARC-EMPTY-ICON-NAME-OBJECTS.json APPARC-EMPTY-ICON-NAME-ROM.json APPARC-EMPTY-ICON-NAME-CANONICAL.json APSSES-874.CPP apserv-empty-icon-874-full-dump.txt apserv-empty-icon-874.map apserv-empty-icon-874.sym; do
        cp "$incremental_parent_root/build/$retained_icon874" "$output/$retained_icon874"
    done
    for retained_preload875 in APPARC-PRELOAD-PUBLICATION-OBJECTS.json APPARC-PRELOAD-PUBLICATION-ROM.json APPARC-PRELOAD-PUBLICATION-CANONICAL.json APSSES-875.CPP apserv-preload-875-full-dump.txt apserv-preload-875.map apserv-preload-875.sym; do
        cp "$incremental_parent_root/build/$retained_preload875" "$output/$retained_preload875"
    done
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$apparc_apserv_binary" >"$output/apserv-launch-prep-876-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-launch-prep.py" --native "$output" --report "$output/FILEMANAGER-LAUNCH-PREP-OBJECTS.json"
    cp "$apparc_apserv_binary.map" "$output/apserv-launch-prep-876.map"
    cp "$apparc_apserv_binary.sym" "$output/apserv-launch-prep-876.sym"
    cp "$full_epocroot/sf/mw/appsupport/appfw/apparchitecture/apserv/APSSES.CPP" "$output/APSSES-876.CPP"
fi
test "$(grep -c 'HTCLEO_APPARC_FIRST_SCAN_SYNCHRONOUS_V1' \
    "$apparc_aplist_source")" -eq 1
for apparc_sync_stage in 00001140 00001141 00001142 00001143
do
    test "$(grep -c "0x${apparc_sync_stage}u" \
        "$apparc_aplist_source")" -eq 1
done
grep -Fq 'iAppIdler->Start(KIdleStartDelay, htcleoIdleDelay,' \
    "$apparc_aplist_source"

apparc_aplist_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/aplist_dll/armv5/urel/aplapplist.o' -type f | head -n 1)
apparc_aplist_logger_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/aplist_dll/armv5/urel/htcleoapplistlog.o' -type f | head -n 1)
apparc_apsstart_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/apserv_dll/armv5/urel/*' -iname 'apsstart.o' -type f | head -n 1)
apparc_apsserv_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/apserv_dll/armv5/urel/*' -iname 'apsserv.o' -type f | head -n 1)
apparc_apsses_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/apserv_dll/armv5/urel/*' -iname 'apsses.o' -type f | head -n 1)
apparc_apserv_logger_obj=$(find "$full_epocroot/epoc32/build/apparc-build" \
    -path '*/apserv_dll/armv5/urel/htcleoapalog.o' -type f | head -n 1)
for apparc_obj in \
    "$apparc_aplist_obj" "$apparc_aplist_logger_obj" \
    "$apparc_apsstart_obj" "$apparc_apsserv_obj" \
    "$apparc_apsses_obj" "$apparc_apserv_logger_obj"
do
    test -n "$apparc_obj" && test -s "$apparc_obj"
done

apparc_aplist_disasm="$output/apparc-aplist-scan-durable-log-urel.disasm"
apparc_aplist_logger_disasm="$output/apparc-aplist-logger-urel.disasm"
apparc_apsstart_disasm="$output/apparc-server-start-durable-log-urel.disasm"
apparc_apsserv_disasm="$output/apparc-server-construct-durable-log-urel.disasm"
apparc_apsses_disasm="$output/apparc-session-observer-durable-log-urel.disasm"
apparc_apserv_logger_disasm="$output/apparc-server-logger-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_aplist_obj" >"$apparc_aplist_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_aplist_logger_obj" >"$apparc_aplist_logger_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_apsstart_obj" >"$apparc_apsstart_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_apsserv_obj" >"$apparc_apsserv_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_apsses_obj" >"$apparc_apsses_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_apserv_logger_obj" >"$apparc_apserv_logger_disasm"
grep -q 'HtcleoApaListLog' "$apparc_aplist_disasm"
grep -q 'HtcleoApaServerLog' "$apparc_apsstart_disasm"
grep -q 'HtcleoApaServerLog' "$apparc_apsserv_disasm"
grep -q 'HtcleoApaServerLog' "$apparc_apsses_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$apparc_aplist_logger_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$apparc_aplist_logger_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$apparc_apserv_logger_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$apparc_apserv_logger_disasm"
strings -el "$apparc_aplist_logger_obj" | grep -Fq 'C:\Symbian3\APALOG.TXT'
strings -el "$apparc_apserv_logger_obj" | grep -Fq 'C:\Symbian3\APALOG.TXT'
! grep -q 'e7f000f0\|c6400000' \
    "$apparc_aplist_disasm" "$apparc_apsstart_disasm" \
    "$apparc_apsserv_disasm" "$apparc_apsses_disasm"
sha256sum "$apparc_aplist_binary" >"$output/apparc-aplist-urel.sha256"
sha256sum "$apparc_apserv_binary" >"$output/apparc-apserv-urel.sha256"
sha256sum "$apparc_apsexe_binary" >"$output/apparc-apsexe-urel.sha256"
sha256sum "$apparc_aplist_logger_obj" \
    >"$output/apparc-aplist-logger-urel.sha256"
sha256sum "$apparc_apserv_logger_obj" \
    >"$output/apparc-server-logger-urel.sha256"

# The 492 hardware run completes AppArc and dispatches MatrixMenu as a
# deferred StartApp. Iteration 493 reaches E32Main but not NewApplication.
# Rebuild only MatrixMenu with the release EikStart flow expanded locally for
# durable pre-factory tracing; retain the deferred-startup contract and avoid
# changing shared eikcore.dll.
test -s "$full_epocroot/epoc32/release/armv5/lib/liwServiceHandler.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/AKNSWALLPAPERUTILS.dso"
ln -sfn liwServiceHandler.dso \
    "$full_epocroot/epoc32/release/armv5/lib/liwservicehandler.dso"
ln -sfn AKNSWALLPAPERUTILS.dso \
    "$full_epocroot/epoc32/release/armv5/lib/aknswallpaperutils.dso"
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$matrixmenu_bldinf" -c "$matrixmenu_config"
sbs_build_for "$matrixmenu_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$matrixmenu_bldinf" -c "$matrixmenu_config" -j 4
test -s "$matrixmenu_binary"
matrixmenu_entry_obj=$(find "$full_epocroot/epoc32/build/matrixmenu-build" \
    -path '*/matrixmenu_exe/armv5/urel/mmgui.o' -type f | head -n 1)
matrixmenu_app_obj=$(find "$full_epocroot/epoc32/build/matrixmenu-build" \
    -path '*/matrixmenu_exe/armv5/urel/mmapplication.o' -type f | head -n 1)
matrixmenu_document_obj=$(find "$full_epocroot/epoc32/build/matrixmenu-build" \
    -path '*/matrixmenu_exe/armv5/urel/mmdocument.o' -type f | head -n 1)
matrixmenu_appui_obj=$(find "$full_epocroot/epoc32/build/matrixmenu-build" \
    -path '*/matrixmenu_exe/armv5/urel/mmappui.o' -type f | head -n 1)
matrixmenu_logger_obj=$(find "$full_epocroot/epoc32/build/matrixmenu-build" \
    -path '*/matrixmenu_exe/armv5/urel/htcleomenulog.o' -type f | head -n 1)
for matrixmenu_obj in \
    "$matrixmenu_entry_obj" "$matrixmenu_app_obj" \
    "$matrixmenu_document_obj" "$matrixmenu_appui_obj" \
    "$matrixmenu_logger_obj"
do
    test -n "$matrixmenu_obj" && test -s "$matrixmenu_obj"
done
matrixmenu_entry_disasm="$output/matrixmenu-entry-durable-log-urel.disasm"
matrixmenu_app_disasm="$output/matrixmenu-application-durable-log-urel.disasm"
matrixmenu_document_disasm="$output/matrixmenu-document-durable-log-urel.disasm"
matrixmenu_appui_disasm="$output/matrixmenu-appui-durable-log-urel.disasm"
matrixmenu_logger_disasm="$output/matrixmenu-logger-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$matrixmenu_entry_obj" >"$matrixmenu_entry_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$matrixmenu_app_obj" >"$matrixmenu_app_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$matrixmenu_document_obj" >"$matrixmenu_document_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$matrixmenu_appui_obj" >"$matrixmenu_appui_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$matrixmenu_logger_obj" >"$matrixmenu_logger_disasm"
for matrixmenu_disasm in \
    "$matrixmenu_entry_disasm" "$matrixmenu_app_disasm" \
    "$matrixmenu_document_disasm" "$matrixmenu_appui_disasm"
do
    grep -q 'HtcleoMenuLog' "$matrixmenu_disasm"
done
grep -q 'HtcleoMatrixMenuExceptionHandlerBody' "$matrixmenu_entry_disasm"
grep -A8 '<.*HtcleoMatrixMenuExceptionHandler.*>:' \
    "$matrixmenu_entry_disasm" | grep -q 'mov.*r1, sp'
grep -A8 '<.*HtcleoMatrixMenuExceptionHandler.*>:' \
    "$matrixmenu_entry_disasm" | grep -Eq \
    'R_ARM_THM_JUMP(11|24).*HtcleoMatrixMenuExceptionHandlerBody'
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$matrixmenu_logger_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$matrixmenu_logger_disasm"
strings "$matrixmenu_logger_obj" | grep -Fq 'HTCLEO_MENU '
strings -el "$matrixmenu_logger_obj" | grep -Fq 'C:\Symbian3\MENULOG.TXT'
! grep -q 'e7f000f0\|c6400000' \
    "$matrixmenu_entry_disasm" "$matrixmenu_app_disasm" \
    "$matrixmenu_document_disasm" "$matrixmenu_appui_disasm" \
    "$matrixmenu_logger_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$matrixmenu_binary" >"$output/matrixmenu-e32-dump.txt"
grep -qi 'Secure ID: 101f4cd2' "$output/matrixmenu-e32-dump.txt"
grep -qi 'Stack Size:[[:space:]]*00010000' \
    "$output/matrixmenu-e32-dump.txt"
sha256sum "$matrixmenu_binary" >"$output/matrixmenu-urel.sha256"
sha256sum "$matrixmenu_entry_obj" \
    >"$output/matrixmenu-entry-object-urel.sha256"
sha256sum "$matrixmenu_appui_obj" \
    >"$output/matrixmenu-appui-object-urel.sha256"
sha256sum "$matrixmenu_logger_obj" \
    >"$output/matrixmenu-logger-object-urel.sha256"

# Iteration 525 proves NewGridContainerL blocks inside the stock mmwidgets
# implementation without returning or Leaving.  Rebuild only mmwidgets.dll
# with MatrixMenu-gated close-only constructor checkpoints.
test -s "$full_epocroot/epoc32/release/armv5/lib/AknCapServerClient.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/AKNSKINS.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/xmlenginedom.dso"
ln -sfn AknCapServerClient.dso \
    "$full_epocroot/epoc32/release/armv5/lib/AknCapserverClient.dso"
ln -sfn AKNSKINS.dso \
    "$full_epocroot/epoc32/release/armv5/lib/AknSkins.dso"
ln -sfn xmlenginedom.dso \
    "$full_epocroot/epoc32/release/armv5/lib/XmlEngineDOM.dso"
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$mmwidgets_bldinf" -c "$matrixmenu_config"
sbs_build_for "$mmwidgets_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$mmwidgets_bldinf" -c "$matrixmenu_config" -j 4
test -s "$mmwidgets_binary"
mmwidgets_widget_obj=$(find "$full_epocroot/epoc32/build/mmwidgets" \
    -path '*/mmwidgets_dll/armv5/urel/*' \
    -iname 'mmwidgetcontainer.o' -type f | head -n 1)
mmwidgets_grid_obj=$(find "$full_epocroot/epoc32/build/mmwidgets" \
    -path '*/mmwidgets_dll/armv5/urel/*' \
    -iname 'mmgridcontainer.o' -type f | head -n 1)
mmwidgets_logger_obj=$(find "$full_epocroot/epoc32/build/mmwidgets" \
    -path '*/mmwidgets_dll/armv5/urel/*' \
    -iname 'htcleommwlog.o' -type f | head -n 1)
mmwidgets_post_obj=$(find "$full_epocroot/epoc32/build/mmwidgets" \
    -path '*/mmwidgets_dll/armv5/urel/*' \
    -iname 'mmpostevaluationprocessor.o' -type f | head -n 1)
mmwidgets_drawer_obj=$(find "$full_epocroot/epoc32/build/mmwidgets" \
    -path '*/mmwidgets_dll/armv5/urel/*' \
    -iname 'mmdraweranimator.o' -type f | head -n 1)
for mmwidgets_obj in \
    "$mmwidgets_widget_obj" "$mmwidgets_grid_obj" "$mmwidgets_logger_obj" \
    "$mmwidgets_post_obj" "$mmwidgets_drawer_obj"
do
    test -n "$mmwidgets_obj" && test -s "$mmwidgets_obj"
done
mmwidgets_widget_disasm="$output/mmwidgets-widget-container-durable-log-urel.disasm"
mmwidgets_grid_disasm="$output/mmwidgets-grid-container-durable-log-urel.disasm"
mmwidgets_logger_disasm="$output/mmwidgets-logger-urel.disasm"
mmwidgets_post_disasm="$output/mmwidgets-postprocess-ao-trace-urel.disasm"
mmwidgets_drawer_disasm="$output/mmwidgets-drawer-ao-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mmwidgets_widget_obj" >"$mmwidgets_widget_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mmwidgets_grid_obj" >"$mmwidgets_grid_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mmwidgets_logger_obj" >"$mmwidgets_logger_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mmwidgets_post_obj" >"$mmwidgets_post_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mmwidgets_drawer_obj" >"$mmwidgets_drawer_disasm"
grep -q 'HtcleoMmwLog' "$mmwidgets_widget_disasm"
grep -q 'HtcleoMmwLog' "$mmwidgets_grid_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$mmwidgets_logger_disasm"
grep -q 'HtcleoMmwLog' "$mmwidgets_post_disasm"
grep -q 'HtcleoMmwLog' "$mmwidgets_drawer_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$mmwidgets_logger_disasm"
strings "$mmwidgets_logger_obj" | grep -Fq 'HTCLEO_MMW '
strings -el "$mmwidgets_logger_obj" | grep -Fq 'C:\Symbian3\MMWLOG.TXT'
! grep -q 'e7f000f0\|c6400000' \
    "$mmwidgets_widget_disasm" "$mmwidgets_grid_disasm" \
    "$mmwidgets_logger_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$mmwidgets_binary" >"$output/mmwidgets-e32-dump.txt"
grep -qi 'Secure ID: 2001e658' "$output/mmwidgets-e32-dump.txt"
grep -qi 'Number of exports = 42' "$output/mmwidgets-e32-dump.txt"
sha256sum "$mmwidgets_binary" >"$output/mmwidgets-urel.sha256"
sha256sum "$mmwidgets_widget_obj" \
    >"$output/mmwidgets-widget-object-urel.sha256"
sha256sum "$mmwidgets_grid_obj" \
    >"$output/mmwidgets-grid-object-urel.sha256"
sha256sum "$mmwidgets_logger_obj" \
    >"$output/mmwidgets-logger-object-urel.sha256"
sha256sum "$mmwidgets_post_obj" \
    >"$output/mmwidgets-postprocess-object-urel.sha256"
sha256sum "$mmwidgets_drawer_obj" \
    >"$output/mmwidgets-drawer-object-urel.sha256"

# Iteration 528 proves the core HN constructor blocks internally.  Rebuild
# only hnengine.dll with MatrixMenu-gated close-only constructor checkpoints.
test -s "$full_epocroot/epoc32/release/armv5/lib/hwrmlightclient.dso"
ln -sfn hwrmlightclient.dso \
    "$full_epocroot/epoc32/release/armv5/lib/HWRMLightClient.dso"
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$hnengine_bldinf" -c "$matrixmenu_config"
sbs_build_for "$hnengine_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$hnengine_bldinf" -c "$matrixmenu_config" -j 4
test -s "$hnengine_binary"
hnengine_obj=$(find "$full_epocroot/epoc32/build/hnengine" \
    -path '*/hnengine_dll/armv5/urel/*' \
    -iname 'hnengine.o' -type f | head -n 1)
test -n "$hnengine_obj" && test -s "$hnengine_obj"
hnengine_disasm="$output/hnengine-constructor-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnengine_obj" >"$hnengine_disasm"
grep -q 'HtcleoHnLog' "$hnengine_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hnengine_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$hnengine_disasm"
strings "$hnengine_obj" | grep -Fq 'HTCLEO_HN '
strings -el "$hnengine_obj" | grep -Fq 'C:\Symbian3\HNLOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$hnengine_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hnengine_binary" >"$output/hnengine-e32-dump.txt"
grep -qi 'Secure ID: 2000f8c5' "$output/hnengine-e32-dump.txt"
grep -qi 'Number of exports = 8' "$output/hnengine-e32-dump.txt"
sha256sum "$hnengine_binary" >"$output/hnengine-urel.sha256"
sha256sum "$hnengine_obj" >"$output/hnengine-object-urel.sha256"

# Iteration 529 proves CHnMdModel::NewL blocks after the suite-model container
# succeeds.  Rebuild only hnmetadatamodel.dll with MatrixMenu-gated close-only
# checkpoints around allocation/member construction and every ConstructL child.
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$hnmetadata_bldinf" -c "$matrixmenu_config"
sbs_build_for "$hnmetadata_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$hnmetadata_bldinf" -c "$matrixmenu_config" -j 4
test -s "$hnmetadata_binary"
hnmetadata_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnmdmodel.o' -type f | head -n 1)
hnmetadata_suite_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnmdsuite.o' -type f | head -n 1)
hnmetadata_query_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnqueryresultcollector.o' -type f | head -n 1)
hnmetadata_item_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnmditem.o' -type f | head -n 1)
hnmetadata_notify_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnmdnotifyrequests.o' -type f | head -n 1)
hnmetadata_notify_request_obj=$(find "$full_epocroot/epoc32/build/hnmetadatamodel" \
    -path '*/hnmetadatamodel_dll/armv5/urel/*' \
    -iname 'hnmdnotifyrequest.o' -type f | head -n 1)
for hnmetadata_evaluation_obj in \
    "$hnmetadata_obj" "$hnmetadata_suite_obj" "$hnmetadata_query_obj" \
    "$hnmetadata_item_obj" "$hnmetadata_notify_obj" \
    "$hnmetadata_notify_request_obj"
do
    test -n "$hnmetadata_evaluation_obj" && test -s "$hnmetadata_evaluation_obj"
done
hnmetadata_disasm="$output/hnmetadatamodel-constructor-durable-log-urel.disasm"
hnmetadata_suite_disasm="$output/hnmetadatamodel-suite-evaluation-durable-log-urel.disasm"
hnmetadata_query_disasm="$output/hnmetadatamodel-query-evaluation-durable-log-urel.disasm"
hnmetadata_item_disasm="$output/hnmetadatamodel-item-results-consumption-urel.disasm"
hnmetadata_notify_disasm="$output/hnmetadatamodel-notify-ui-first-compat-urel.disasm"
hnmetadata_notify_request_disasm="$output/hnmetadatamodel-notify-reconnect-requery-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_obj" >"$hnmetadata_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_suite_obj" >"$hnmetadata_suite_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_query_obj" >"$hnmetadata_query_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_item_obj" >"$hnmetadata_item_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_notify_obj" >"$hnmetadata_notify_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hnmetadata_notify_request_obj" >"$hnmetadata_notify_request_disasm"
grep -q 'HtcleoMdLog' "$hnmetadata_disasm"
grep -q 'HtcleoMdSuiteLog' "$hnmetadata_suite_disasm"
grep -q 'HtcleoMdQueryLog' "$hnmetadata_query_disasm"
grep -q 'HtcleoMdNotifyLog' "$hnmetadata_item_disasm"
grep -q 'HtcleoMdNotifyLog' "$hnmetadata_notify_disasm"
grep -q 'HtcleoMdNotifyLog' "$hnmetadata_notify_request_disasm"
! grep -q 'R_ARM_.*CALL.*CAsyncCallBack.*CallBack' \
    "$hnmetadata_notify_request_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hnmetadata_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hnmetadata_suite_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hnmetadata_query_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$hnmetadata_notify_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$hnmetadata_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$hnmetadata_suite_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$hnmetadata_query_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$hnmetadata_notify_disasm"
! grep -q 'User::After\|HalFunction' "$hnmetadata_notify_request_disasm"
strings "$hnmetadata_obj" | grep -Fq 'HTCLEO_MD '
strings "$hnmetadata_suite_obj" | grep -Fq 'HTCLEO_MD '
strings "$hnmetadata_query_obj" | grep -Fq 'HTCLEO_MD '
strings "$hnmetadata_notify_obj" | grep -Fq 'HTCLEO_MD '
strings -el "$hnmetadata_obj" | grep -Fq 'C:\Symbian3\MDLOG.TXT'
strings -el "$hnmetadata_suite_obj" | grep -Fq 'C:\Symbian3\MDLOG.TXT'
strings -el "$hnmetadata_query_obj" | grep -Fq 'C:\Symbian3\MDLOG.TXT'
strings -el "$hnmetadata_notify_obj" | grep -Fq 'C:\Symbian3\MDLOG.TXT'
! grep -q 'e7f000f0\|c6400000' \
    "$hnmetadata_disasm" "$hnmetadata_suite_disasm" \
    "$hnmetadata_query_disasm" "$hnmetadata_item_disasm" \
    "$hnmetadata_notify_disasm" \
    "$hnmetadata_notify_request_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hnmetadata_binary" >"$output/hnmetadatamodel-e32-dump.txt"
grep -qi 'Secure ID: 2000f8c7' "$output/hnmetadatamodel-e32-dump.txt"
grep -qi 'Number of exports = 46' "$output/hnmetadatamodel-e32-dump.txt"
sha256sum "$hnmetadata_binary" >"$output/hnmetadatamodel-urel.sha256"
sha256sum "$hnmetadata_obj" \
    >"$output/hnmetadatamodel-object-urel.sha256"
sha256sum "$hnmetadata_suite_obj" \
    >"$output/hnmetadatamodel-suite-object-urel.sha256"
sha256sum "$hnmetadata_query_obj" \
    >"$output/hnmetadatamodel-query-object-urel.sha256"
sha256sum "$hnmetadata_item_obj" \
    >"$output/hnmetadatamodel-item-object-urel.sha256"
sha256sum "$hnmetadata_notify_obj" \
    >"$output/hnmetadatamodel-notify-object-urel.sha256"
sha256sum "$hnmetadata_notify_request_obj" \
    >"$output/hnmetadatamodel-notify-request-object-urel.sha256"

# Iteration 582 proves that MenuContent's LIW synchronous mode rejects the
# null callback and therefore cannot return the real KReturnValue list.  Keep
# LIW's callback API, but synchronously pump the provider's existing real MCS
# IPC for MatrixMenu before returning through the stock callback/icon path.
if [ "$build_mode" = full-clean ] || incremental_wants_binary "$mcsservice_binary"
then
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$mcsservice_bldinf" -c "$matrixmenu_config"
sbs_build_for "$mcsservice_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$mcsservice_bldinf" -c "$matrixmenu_config" -j 4
test -s "$mcsservice_binary"
mcsservice_getlist_obj=$(find "$full_epocroot/epoc32/build/mcsservice" \
    -path '*/mcsservice_dll/armv5/urel/*' \
    -iname 'mcsgetlistimpl.o' -type f | head -n 1)
test -n "$mcsservice_getlist_obj" && test -s "$mcsservice_getlist_obj"
mcsservice_getlist_disasm="$output/mcsservice-getlist-sync-pump-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mcsservice_getlist_obj" >"$mcsservice_getlist_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*SecureId' "$mcsservice_getlist_disasm"
grep -q 'R_ARM_.*CALL.*RMenuSapi.*GetListL' "$mcsservice_getlist_disasm"
grep -q 'R_ARM_.*CALL.*NotifyRequestResultL' "$mcsservice_getlist_disasm"
! grep -q 'User::After\|RTimer\|HalFunction' "$mcsservice_getlist_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$mcsservice_binary" >"$output/mcsservice-e32-dump.txt"
grep -qi 'Secure ID: 2001242b' "$output/mcsservice-e32-dump.txt"
grep -qi 'Number of exports = 34' "$output/mcsservice-e32-dump.txt"
sha256sum "$mcsservice_binary" >"$output/mcsservice-urel.sha256"
sha256sum "$mcsservice_getlist_obj" \
    >"$output/mcsservice-getlist-object-urel.sha256"
else
    echo "HTCLEO_MCSSERVICE_REUSED parent=$incremental_parent"
fi


if [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ]; then
    test "$(sha256sum "$gsframework_binary" | awk '{print $1}')" = 1c9e75f7b6cd5a6cb00de8fba2fc4830e73d701ddacbf4f86bf685100ea357b5
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
    sbs_build_for "$gsframework_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/gsframework-build/bld.inf" \
        -c "$matrixmenu_config" -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$gsframework_binary" >"$output/gsframework-child-827-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-child-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/827-gsapp-child-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-CHILD-OBJECTS.json"
    cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSFramework/src/GSPluginLoader.cpp" "$output/GSPluginLoader-827.cpp"
    cp "$gsframework_binary.map" "$output/gsframework-child-827.map"
    cp "$gsframework_binary.sym" "$output/gsframework-child-827.sym"
    sha256sum "$gsframework_binary" >"$output/gsframework-urel.sha256"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ]; then
    test "$(sha256sum "$gsframework_binary" | awk '{print $1}')" = 4521bcec67615afffecb902868f4d3a356e87352d9feb20291c019ab8aac7b52
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
    sbs_build_for "$gsframework_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/gsframework-build/bld.inf" \
        -c "$matrixmenu_config" -j 4
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$gsframework_binary" >"$output/gsframework-notify-825-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-ecom-notify-guard.py" \
        --baseline "$project/Symbian/output/iteration-evidence/825-gsapp-ecom-notify-guard/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-NOTIFY-OBJECTS.json"
    cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSFramework/src/GSEComNotifier.cpp" "$output/GSEComNotifier-825.cpp"
    cp "$gsframework_binary.map" "$output/gsframework-notify-825.map"
    cp "$gsframework_binary.sym" "$output/gsframework-notify-825.sym"
    sha256sum "$gsframework_binary" >"$output/gsframework-urel.sha256"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ]; then
    #Host-only calibration: only GSPluginLoader.o differs among15 units.
    gsplugin_evidence="$project/Symbian/output/iteration-evidence/821-gsapp-plugin-frontier"
    test "$(sha256sum "$gsframework_binary" | awk '{print $1}')" = e7f097ce4829130ef6333598796f6dc67ce86e5a8c7bc2ef7eee190e576b8ac5
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/gsframework.dll
    sbs_build_for "$gsframework_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/gsframework-build/bld.inf" \
        -c "$matrixmenu_config" -j 4
    for gsplugin_file in gsframework-stock-820.dll gsframework-gcce-baseline-821.dll gsframework-stock-820-full-dump.txt gsframework-calibration-821-full-dump.txt; do
        cp "$gsplugin_evidence/$gsplugin_file" "$output/$gsplugin_file"
    done
    cp "$gsplugin_evidence/BASE-OBJECTS.json" "$output/GSAPP-PLUGIN-BASE-OBJECTS.json"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$gsframework_binary" >"$output/gsframework-plugin-821-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-plugin-frontier.py" \
        --baseline "$gsplugin_evidence/BASE-OBJECTS.json" --native "$output" \
        --report "$output/GSAPP-PLUGIN-OBJECTS.json"
    gsplugin_obj=$(find "$full_epocroot/epoc32/build/gsframework-build" -path '*/gsframework_dll/armv5/urel/GSPluginLoader.o' -type f)
    test -s "$gsplugin_obj"
    "$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$gsplugin_obj" >"$output/gsplugin-loader-821.disasm"
    grep -q HtcleoGsPluginLog "$output/gsplugin-loader-821.disasm"
    ! grep -q 'R_ARM_.*CALL.*RFile.*Flush\|R_ARM_.*CALL.*RFile.*Replace' "$output/gsplugin-loader-821.disasm"
    cp "$gsframework_binary.map" "$output/gsframework.dll.map"
    cp "$gsframework_binary.sym" "$output/gsframework.dll.sym"
    cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSFramework/src/GSPluginLoader.cpp" "$output/GSPluginLoader-821.cpp"
    sha256sum "$gsframework_binary" >"$output/gsframework-urel.sha256"
fi

if [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    # Restore retained GS layers without relinking. Appearance/About deferred;
    # newest font policy adds back the exact855 observer below.
    python3 "$gsapp_black_background" "$full_epocroot"
    python3 "$gsapp_static_background" "$full_epocroot"
    python3 "$gsapp_window_background" "$full_epocroot"
    python3 "$gsapp_root_skin_background" "$full_epocroot"
    python3 "$gsapp_root_background_owner" "$full_epocroot"
    python3 "$gsapp_root_paint_witness" "$full_epocroot"
    python3 "$gsapp_root_bitmap_background" "$full_epocroot"
    gsapp_black_background_policy=GS-private-window-control-black-white-palette-no-global-storage-or-UI-policy
    gsapp_static_background_policy=native-EAknDisableAnimationBackground-skin-MSK-singleclick-retained
    gsapp_window_background_policy=owned-root-RWindow-black-60F2-palette-60F3-view-no-draw-loop-or-geometry-change
    gsapp_root_skin_background_policy=root-column-data-skin-disabled-60F2-60F4-init-only-no-global-skin-change
    gsapp_root_background_owner_policy=private-Avkon-view-fill-once-native-foreground-temporary-mask-cleanup-no-geometry-or-filelog
    gsapp_root_paint_witness_policy=root-private-first-entry-gc-rect-fill-native-return-max7-per-view-no-behavior-change
    gsapp_root_bitmap_background_policy=root-owned-1x1-RGB565-black-DrawBitmap-native-foreground-fallback-on-allocation-error
    for retained_gs_file in GSAPP-BLACK-OBJECTS.json gsapp-black-850-full-dump.txt gsapp-black-850.map gsapp-black-850.sym GSUi-850.cpp GSMainContainer-850.cpp gsapp-e32-dump.txt; do
        cp "$incremental_parent_root/build/$retained_gs_file" "$output/$retained_gs_file"
    done
    if [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
       [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
        cp "$incremental_parent_root/build/GSAPP-BLACK-PARENT-850-ROM.json" "$output/GSAPP-BLACK-ROM.json"
        cp "$incremental_parent_root/build/GSAPP-BLACK-PARENT-850-CANONICAL.json" "$output/GSAPP-BLACK-CANONICAL.json"
        for retained_geometry_file in AVKON-GEOMETRY-OBJECTS.json eikcoctl-geometry-851-full-dump.txt eikcoctl-geometry-851.map eikcoctl-geometry-851.sym 851-EIKCOLIB.CPP 851-eikspane.cpp 851-eikcba.cpp 851-htcleoavkongeometry851.inl; do
            cp "$incremental_parent_root/build/$retained_geometry_file" "$output/$retained_geometry_file"
        done
        if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
            cp "$incremental_parent_root/build/AVKON-GEOMETRY-PARENT-851-ROM.json" "$output/AVKON-GEOMETRY-ROM.json"
            cp "$incremental_parent_root/build/AVKON-GEOMETRY-PARENT-851-CANONICAL.json" "$output/AVKON-GEOMETRY-CANONICAL.json"
            cp "$incremental_parent_root/build/FONT-FAMILY-PARENT-852-ROM.json" "$output/FONT-FAMILY-ROM.json"
            cp "$incremental_parent_root/build/FONT-FAMILY-PARENT-852-CANONICAL.json" "$output/FONT-FAMILY-CANONICAL.json"
        else
            cp "$incremental_parent_root/build/AVKON-GEOMETRY-ROM.json" "$output/AVKON-GEOMETRY-ROM.json"
            cp "$incremental_parent_root/build/AVKON-GEOMETRY-CANONICAL.json" "$output/AVKON-GEOMETRY-CANONICAL.json"
        fi
    else
        cp "$incremental_parent_root/build/GSAPP-BLACK-ROM.json" "$output/GSAPP-BLACK-ROM.json"
        cp "$incremental_parent_root/build/GSAPP-BLACK-CANONICAL.json" "$output/GSAPP-BLACK-CANONICAL.json"
    fi
fi

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    #856 keeps the complete855 GSApp and its observer; do not relink GS.
    python3 "$gsapp_text_witness" "$full_epocroot"
    python3 "$gsapp_font_census" "$full_epocroot"
    python3 "$gsapp_font_load_boundary" "$full_epocroot"
    gsapp_font_load_boundary_policy=first-root-entry-ecom-list-library-load-owned-FBS-add-request-release-remove-max19-no-startup-change
    gsapp_font_census_policy=retired854-replaced-by-font-load-boundary855
    gsapp_text_witness_policy=retired853-replaced-by-font-census854
    for retained_font_observer in GSAPP-TEXT-OBJECTS.json gsapp-font-load-855-full-dump.txt gsapp-font-load-855.map gsapp-font-load-855.sym GSMainContainer-855.cpp GSApplication-855.mmp; do
        cp "$incremental_parent_root/build/$retained_font_observer" "$output/$retained_font_observer"
    done
    cp "$incremental_parent_root/build/GSAPP-TEXT-PARENT-855-ROM.json" "$output/GSAPP-TEXT-PARENT-855-ROM.json"
    cp "$incremental_parent_root/build/GSAPP-TEXT-PARENT-855-CANONICAL.json" "$output/GSAPP-TEXT-PARENT-855-CANONICAL.json"
fi

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    # Retain858 source and binary, including the client-side process observer.
    python3 "$gsapp_font_server_lifetime" "$full_epocroot"
    gsapp_font_server_lifetime_policy=first-root-held-unique-ECom-SID-process-before-after-same-font-query13-no-server-mutation
    gsapp_font_load_boundary_policy=retired855-replaced-by-font-server-lifetime858
    for retained_gs858 in GSAPP-TEXT-OBJECTS.json gsapp-font-server-858-full-dump.txt gsapp-font-server-858.map gsapp-font-server-858.sym GSMainContainer-858.cpp GSApplication-858.mmp; do
        cp "$incremental_parent_root/build/$retained_gs858" "$output/$retained_gs858"
    done
    cp "$incremental_parent_root/build/GSAPP-TEXT-PARENT-858-ROM.json" "$output/GSAPP-TEXT-PARENT-858-ROM.json"
    cp "$incremental_parent_root/build/GSAPP-TEXT-PARENT-858-CANONICAL.json" "$output/GSAPP-TEXT-PARENT-858-CANONICAL.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ]; then
    gsapp_binary="$full_epocroot/epoc32/release/armv5/urel/gsapp.exe"
    gsapp_parent_sha=833f67e9c88528eac08b60efd2b374583d9a60e385879dc0d0f7c1f42f2d7829
    if [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ]; then
        gsapp_parent_sha=2a33806f404d498eb2f50e1c1dae46a0e2ff0323147c687e4666605367511972
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-list-activation ]; then
        gsapp_parent_sha=357f146ed426b06f5a6ab273c5bea146ebf7be4de622c9615b0004a6bd32b6eb
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ]; then
        gsapp_parent_sha=17cdfc53c31c54e33023f37f32d4f07024f5c2960e65c8547a98cac21363b008
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ]; then
        gsapp_parent_sha=fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ]; then
        gsapp_parent_sha=c2b4216e919af1d53333df8a3dd5507b9abb1dd96338e3644a7c4160c97c9b22
        python3 "$project/Symbian/scripts/prepare-htcleo-gsframework-import-library.py" \
            --report "$output/GSFRAMEWORK-IMPORT-IDENTITY-824.txt"
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-black-background ]; then
        gsapp_parent_sha=ae54c0d349ed923e1b9460898f6259bb3a4fc7ebe7361ef8e7840ebfc85d2b1d
        python3 "$gsapp_black_background" "$full_epocroot"
        python3 "$gsapp_static_background" "$full_epocroot"
        python3 "$gsapp_window_background" "$full_epocroot"
        python3 "$gsapp_root_skin_background" "$full_epocroot"
        python3 "$gsapp_root_background_owner" "$full_epocroot"
        python3 "$gsapp_root_paint_witness" "$full_epocroot"
        python3 "$gsapp_root_bitmap_background" "$full_epocroot"
        gsapp_black_background_policy=GS-private-window-control-black-white-palette-no-global-storage-or-UI-policy
        gsapp_static_background_policy=native-EAknDisableAnimationBackground-skin-MSK-singleclick-retained
        gsapp_window_background_policy=owned-root-RWindow-black-60F2-palette-60F3-view-no-draw-loop-or-geometry-change
        gsapp_root_skin_background_policy=root-column-data-skin-disabled-60F2-60F4-init-only-no-global-skin-change
        gsapp_root_background_owner_policy=private-Avkon-view-fill-once-native-foreground-temporary-mask-cleanup-no-geometry-or-filelog
        gsapp_root_paint_witness_policy=root-private-first-entry-gc-rect-fill-native-return-max7-per-view-no-behavior-change
        gsapp_root_bitmap_background_policy=root-owned-1x1-RGB565-black-DrawBitmap-native-foreground-fallback-on-allocation-error
    fi
    test "$(sha256sum "$gsapp_binary" | awk '{print $1}')" = "$gsapp_parent_sha"
    # Parent GSApp restored from immutable cache. Force this one local output
    # to relink rather than accepting a newer restored timestamp as up-to-date.
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/gsapp.exe
    sbs_build_for "$gsapp_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$project/Symbian/hd2/qsd8250-native-bsp/gsapp-build/bld.inf" \
        -c "$matrixmenu_config" -j 4
    test -s "$gsapp_binary"
    # Calibration target is host-only and never added to the recipe/cache.
    cp "$output/gsapp-stock-805.exe" "$work/gsapp-stock-805.exe"
    cp "$output/gsapp-gcce-baseline-806.exe" "$work/gsapp-gcce-baseline-806.exe"
    cmp -s "$output/gsapp-stock-805.exe" "$work/gsapp-stock-805.exe"
    cmp -s "$output/gsapp-gcce-baseline-806.exe" "$work/gsapp-gcce-baseline-806.exe"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$work/gsapp-stock-805.exe" >"$output/gsapp-stock-805-e32-dump.txt"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$work/gsapp-gcce-baseline-806.exe" >"$output/gsapp-gcce-baseline-e32-dump.txt"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$gsapp_binary" >"$output/gsapp-e32-dump.txt"
    if [ "$incremental_resource_policy" = gate17-gsapp-black-background ]; then
        cp "$output/gsapp-e32-dump.txt" "$output/gsapp-black-850-full-dump.txt"
        python3 "$project/Symbian/scripts/verify-htcleo-gsapp-black-background.py" \
            --profile 850 --native "$output" --report "$output/GSAPP-BLACK-OBJECTS.json"
        cp "$gsapp_binary.map" "$output/gsapp-black-850.map"
        cp "$gsapp_binary.sym" "$output/gsapp-black-850.sym"
        cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSUi.cpp" "$output/GSUi-850.cpp"
        cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp" "$output/GSMainContainer-850.cpp"
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ]; then
        cp "$output/gsapp-e32-dump.txt" "$output/gsapp-async-829-full-dump.txt"
        python3 "$project/Symbian/scripts/verify-htcleo-gsapp-async-view-event.py" \
            --baseline "$project/Symbian/output/iteration-evidence/829-gsapp-async-view-event/BASE-OBJECTS.json" \
            --native "$output" --report "$output/GSAPP-ASYNC-OBJECTS.json"
        cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp" "$output/GSMainContainer-829.cpp"
        cp "$gsapp_binary.map" "$output/gsapp-async-829.map"
        cp "$gsapp_binary.sym" "$output/gsapp-async-829.sym"
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-list-activation ]; then
        cp "$output/gsapp-e32-dump.txt" "$output/gsapp-list-828-full-dump.txt"
        python3 "$project/Symbian/scripts/verify-htcleo-gsapp-input-activation.py" \
            --baseline "$project/Symbian/output/iteration-evidence/828-gsapp-list-activation/BASE-OBJECTS.json" \
            --native "$output" --report "$output/GSAPP-LIST-OBJECTS.json"
        cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp" "$output/GSMainContainer-828.cpp"
        cp "$gsapp_binary.map" "$output/gsapp-list-828.map"
        cp "$gsapp_binary.sym" "$output/gsapp-list-828.sym"
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ]; then
        cp "$output/gsapp-e32-dump.txt" "$output/gsapp-exception-824-full-dump.txt"
        python3 "$project/Symbian/scripts/verify-htcleo-gsapp-exception-witness.py" \
            --baseline "$project/Symbian/output/iteration-evidence/824-gsapp-exception-witness/BASE-OBJECTS.json" \
            --native "$output" --report "$output/GSAPP-EXCEPTION-OBJECTS.json"
        cp "$full_epocroot/sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSApp.cpp" "$output/GSApp-824.cpp"
        cp "$gsapp_binary.map" "$output/gsapp-exception-824.map"
        cp "$gsapp_binary.sym" "$output/gsapp-exception-824.sym"
    fi
    if [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ]; then
        cp "$output/gsapp-e32-dump.txt" "$output/gsapp-view-817-full-dump.txt"
        python3 "$project/Symbian/scripts/verify-htcleo-gsapp-view-frontier.py" \
            --baseline "$project/Symbian/output/iteration-evidence/817-gsapp-view-frontier/BASE-OBJECTS.json" \
            --native "$output" --report "$output/GSAPP-VIEW-OBJECTS.json"
    fi
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$menuhandler_binary" >"$output/mcsmenuhandler-e32-dump.txt"
fi

if incremental_wants_binary "$menuhandler_binary" && [ "$incremental_resource_policy" != gate19-filemanager-registration ]; then
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$menuhandler_binary" >"$output/mcsmenuhandler-stock-792-e32-dump.txt"
    # Original Windows SDK header uses uppercase spelling on a Linux host.
    # Alias the exact SDK file, without changing plugin source/API behavior.
    menuhandler_scheme_dir="$full_epocroot/epoc32/include/platform/mw"
    for menuhandler_case_pair in SchemeHandler.inl:schemehandler.inl SchemeDefs.hrh:schemedefs.hrh; do
        menuhandler_case_name=${menuhandler_case_pair%%:*}
        menuhandler_case_source=${menuhandler_case_pair#*:}
        test -s "$menuhandler_scheme_dir/$menuhandler_case_source"
        if [ ! -e "$menuhandler_scheme_dir/$menuhandler_case_name" ]; then
            ln -s "$menuhandler_case_source" "$menuhandler_scheme_dir/$menuhandler_case_name"
        fi
        cmp -s "$menuhandler_scheme_dir/$menuhandler_case_name" "$menuhandler_scheme_dir/$menuhandler_case_source"
    done
    menuhandler_dso_dir="$full_epocroot/epoc32/release/armv5/lib"
    test -s "$menuhandler_dso_dir/SWInstCli.dso"
    if [ ! -e "$menuhandler_dso_dir/swinstcli.dso" ]; then
        ln -s SWInstCli.dso "$menuhandler_dso_dir/swinstcli.dso"
    fi
    cmp -s "$menuhandler_dso_dir/swinstcli.dso" "$menuhandler_dso_dir/SWInstCli.dso"
    sbs_build_for "$menuhandler_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$menuhandler_bldinf" -c "$matrixmenu_config" -j 4
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$menuhandler_binary" >"$output/mcsmenuhandler-e32-dump.txt"
    grep -qi 'Secure ID: 200113de' "$output/mcsmenuhandler-e32-dump.txt"
    grep -qi 'Vendor ID: 101fb657' "$output/mcsmenuhandler-e32-dump.txt"
    grep -qi 'Capabilities: 00000000 000ffffe' "$output/mcsmenuhandler-e32-dump.txt"
    grep -q 'Module Version: 10.0' "$output/mcsmenuhandler-e32-dump.txt"
    grep -q 'Number of exports = 1' "$output/mcsmenuhandler-e32-dump.txt"
    cp "$menuhandler_stock_resource" "$menuhandler_resource"
    sha256sum "$menuhandler_binary" >"$output/mcsmenuhandler-urel.sha256"
fi

if [ "$incremental_resource_policy" = gate17-hsps-header-cache ]; then
    # Reused801 plugin: neither analysis dump nor hash may remain from803.
    # These are read-only binary reports, not a rebuild or import allowance.
    cp "$menuhandler_stock" "$work/menuhandler-stock-792.dll"
    cmp -s "$menuhandler_stock" "$work/menuhandler-stock-792.dll"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$work/menuhandler-stock-792.dll" >"$output/mcsmenuhandler-stock-792-e32-dump.txt"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$menuhandler_binary" >"$output/mcsmenuhandler-e32-dump.txt"
    sha256sum "$menuhandler_binary" >"$output/mcsmenuhandler-urel.sha256"
fi

if [ "$build_mode" = full-clean ] || incremental_wants_binary "$mcsprovider_binary"
then
    sbs_build_for "$mcsprovider_binary" -- \
        --configpath="$matrixmenu_config_path" \
        -b "$mcsprovider_bldinf" -c "$matrixmenu_config" -j 4
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$mcsprovider_binary" >"$output/mcsprovider-e32-dump.txt"
    grep -qi 'Secure ID: 2001242c' "$output/mcsprovider-e32-dump.txt"
    grep -qi 'Number of exports = 1' "$output/mcsprovider-e32-dump.txt"
    sha256sum "$mcsprovider_binary" >"$output/mcsprovider-urel.sha256"
    # Recompiling an ECom DLL must not silently alter its registration resource.
    test "$(sha256sum "$mcsprovider_stock_resource" | awk '{print $1}')" = \
        "$(sed -n 's/^RESOURCE_SHA256=//p' "$mcsprovider_pin")"
    cp "$mcsprovider_stock_resource" "$mcsprovider_resource"
fi

# The mandatory initial GetList starts MenuContent through mcsmenu.dll.  Keep
# the actual menu engine, AppArc scanner, cache and GetList, but defer the
# server's eager Nokia-only dynamic services in one isolated rebuild.
if [ "$build_mode" = full-clean ] || incremental_wants_binary "$mcsmenu_binary"
then
test -s "$full_epocroot/epoc32/release/armv5/lib/DrmServerInterfaces.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/DrmRightsInfo.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/XCFW.dso"
ln -sfn DrmServerInterfaces.dso \
    "$full_epocroot/epoc32/release/armv5/lib/drmserverinterfaces.dso"
ln -sfn DrmRightsInfo.dso \
    "$full_epocroot/epoc32/release/armv5/lib/drmrightsinfo.dso"
ln -sfn XCFW.dso \
    "$full_epocroot/epoc32/release/armv5/lib/xcfw.dso"
#872 retires871 reconnect entirely; restored870 notifier remains installed.
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$mcsmenu_bldinf" -c "$matrixmenu_config"
sbs_build_for "$mcsmenu_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$mcsmenu_bldinf" -c "$matrixmenu_config" -j 4
test -s "$mcsmenu_binary"
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$mcsmenu_binary" >"$output/mcsmenu-notifier-871-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-mcs-notifier-reconnect.py" --native "$output" --report "$output/MCS-NOTIFIER-RECONNECT-OBJECTS.json"
    cp "$mcsmenu_binary.map" "$output/mcsmenu-notifier-871.map"
    cp "$mcsmenu_binary.sym" "$output/mcsmenu-notifier-871.sym"
    cp "$full_epocroot/sf/mw/homescreensrv/menucontentsrv/srvsrc/htcleomcsapplistnotifier.inl" "$output/htcleomcsapplistnotifier-871.inl"
fi
mcsmenu_engine_obj=$(find "$full_epocroot/epoc32/build/mcsmenu-build" \
    -path '*/mcsmenu_dll/armv5/urel/*' \
    -iname 'menusrveng.o' -type f | head -n 1)
mcsmenu_server_obj=$(find "$full_epocroot/epoc32/build/mcsmenu-build" \
    -path '*/mcsmenu_dll/armv5/urel/*' \
    -iname 'menusrv.o' -type f | head -n 1)
mcsmenu_utils_obj=$(find "$full_epocroot/epoc32/build/mcsmenu-build" \
    -path '*/mcsmenu_dll/armv5/urel/*' \
    -iname 'menusrvengutils.o' -type f | head -n 1)
mcsmenu_scanner_obj=$(find "$full_epocroot/epoc32/build/mcsmenu-build" \
    -path '*/mcsmenu_dll/armv5/urel/*' \
    -iname 'menusrvappscanner.o' -type f | head -n 1)
for mcsmenu_obj in \
    "$mcsmenu_engine_obj" "$mcsmenu_server_obj" \
    "$mcsmenu_utils_obj" "$mcsmenu_scanner_obj"
do
    test -n "$mcsmenu_obj" && test -s "$mcsmenu_obj"
done
mcsmenu_disasm="$output/mcsmenu-ui-first-compat-urel.disasm"
mcsmenu_server_disasm="$output/mcsmenu-persistent-server-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mcsmenu_engine_obj" >"$mcsmenu_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mcsmenu_server_obj" >"$mcsmenu_server_disasm"
grep -q 'HtcleoMcsLog' "$mcsmenu_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$mcsmenu_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$mcsmenu_disasm"
strings "$mcsmenu_engine_obj" | grep -Fq 'HTCLEO_MCS '
strings -el "$mcsmenu_engine_obj" | grep -Fq 'C:\Symbian3\MCSLOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$mcsmenu_disasm"
grep -q 'HtcleoMcsLog' "$mcsmenu_server_disasm"
grep -qi '4d430151' "$mcsmenu_server_disasm"
grep -qi '4d430152' "$mcsmenu_server_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$mcsmenu_binary" >"$output/mcsmenu-e32-dump.txt"
grep -qi 'Secure ID: 200113db' "$output/mcsmenu-e32-dump.txt"
grep -qi 'Number of exports = 82' "$output/mcsmenu-e32-dump.txt"
sha256sum "$mcsmenu_binary" >"$output/mcsmenu-urel.sha256"
sha256sum "$mcsmenu_engine_obj" \
    >"$output/mcsmenu-engine-object-urel.sha256"
sha256sum "$mcsmenu_utils_obj" \
    >"$output/mcsmenu-utils-object-urel.sha256"
sha256sum "$mcsmenu_scanner_obj" \
    >"$output/mcsmenu-scanner-object-urel.sha256"
else
    echo "HTCLEO_MCSMENU_REUSED parent=$incremental_parent"
    if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
        for retained_mcs870 in mcsmenu-e32-dump.txt mcsmenu-ui-first-compat-urel.disasm mcsmenu-engine-object-urel.sha256 mcsmenu-utils-object-urel.sha256 mcsmenu-scanner-object-urel.sha256; do
            cp "$incremental_parent_root/build/$retained_mcs870" "$output/$retained_mcs870"
        done
    fi
fi
# Even a reused unit must describe the restored parent binary, not a prior
# failed branch's mutable build output. Object/disassembly evidence is separate.
sha256sum "$mcsmenu_binary" >"$output/mcsmenu-urel.sha256"

# CMenuEng lives in the separate mcsmenueng.dll.  Rebuild only this core DLL
# for iteration 537; the real RAM/ROM XCFW load remains behavior-identical.
if [ "$build_mode" = full-clean ] || incremental_wants_binary "$mcsmenu_core_binary"
then
test -s "$full_epocroot/epoc32/release/armv5/lib/XCFW.dso"
ln -sfn XCFW.dso \
    "$full_epocroot/epoc32/release/armv5/lib/xcfw.dso"
sbs_clean --configpath="$matrixmenu_config_path" \
    -b "$mcsmenu_core_bldinf" -c "$matrixmenu_config"
sbs_build_for "$mcsmenu_core_binary" -- \
    --configpath="$matrixmenu_config_path" \
    -b "$mcsmenu_core_bldinf" -c "$matrixmenu_config" -j 4
test -s "$mcsmenu_core_binary"
mcsmenu_menueng_obj=$(find "$full_epocroot/epoc32/build/mcsmenueng-build" \
    -path '*/mcsmenueng_dll/armv5/urel/*' \
    -iname 'menueng.o' -type f | head -n 1)
test -n "$mcsmenu_menueng_obj" && test -s "$mcsmenu_menueng_obj"
mcsmenu_menueng_disasm="$output/mcsmenu-core-engine-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$mcsmenu_menueng_obj" >"$mcsmenu_menueng_disasm"
grep -q 'HtcleoMenuEngLog' "$mcsmenu_menueng_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$mcsmenu_menueng_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$mcsmenu_menueng_disasm"
strings "$mcsmenu_menueng_obj" | grep -Fq 'HTCLEO_MCS '
strings -el "$mcsmenu_menueng_obj" | grep -Fq 'C:\Symbian3\MCSLOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$mcsmenu_menueng_disasm"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$mcsmenu_core_binary" >"$output/mcsmenueng-e32-dump.txt"
grep -qi 'Secure ID: 200113dc' "$output/mcsmenueng-e32-dump.txt"
grep -qi 'Number of exports = 35' "$output/mcsmenueng-e32-dump.txt"
sha256sum "$mcsmenu_core_binary" >"$output/mcsmenueng-urel.sha256"
sha256sum "$mcsmenu_menueng_obj" \
    >"$output/mcsmenu-core-engine-object-urel.sha256"
else
    echo "HTCLEO_MCSMENUENG_REUSED parent=$incremental_parent"
fi
sha256sum "$mcsmenu_core_binary" >"$output/mcsmenueng-urel.sha256"

# Record the caller-side APSEXE launch and AknCapServer StartApp path.  This is
# deliberately separate from APALOG: the caller remains able to report an
# APSEXE loader/rendezvous failure even when APSEXE never reaches RunServerL.
sbs_clean -b "$apparc_launch_bldinf" -c "$ssm_config"
sbs_build_for "$apparc_launch_binary" -- \
    -b "$apparc_launch_bldinf" -c "$ssm_config" -j 4
test -s "$apparc_launch_binary"
apparc_launch_obj=$(find "$full_epocroot/epoc32/build/akncapserverclient-build" \
    -path '*/akncapserverclient_dll/armv5/urel/*' \
    -iname 'akncapserverclient.o' -type f | head -n 1)
test -n "$apparc_launch_obj" && test -s "$apparc_launch_obj"
apparc_launch_disasm="$output/apparc-launch-rendezvous-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$apparc_launch_obj" >"$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Create' "$apparc_launch_disasm"
# One rendezvous call remains in the independent APSEXE startup helper.  The
# AknCap launch path itself is source-guarded above and must use P&S readiness.
test "$(grep -c 'R_ARM_.*CALL.*RProcess.*Rendezvous' \
    "$apparc_launch_disasm")" -eq 1
grep -q 'R_ARM_.*CALL.*RProcess.*Resume' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Define' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Set' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Attach' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Get' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*Open' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProperty.*Delete' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*User.*After' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProperty.*Subscribe' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProperty.*Cancel' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProcess.*Logon' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProcess.*LogonCancel' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*ExitCategory' "$apparc_launch_disasm"
! grep -q 'R_ARM_.*CALL.*RProcess.*ExitCategory' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$apparc_launch_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$apparc_launch_disasm"
grep -q 'HtcleoAknUiConnectMenuLog' "$apparc_launch_disasm"
grep -qi '4d4da200' "$apparc_launch_disasm"
grep -qi '4d4da21c' "$apparc_launch_disasm"
strings "$apparc_launch_obj" | grep -Fq 'HTCLEO_APASTART '
strings -el "$apparc_launch_obj" | grep -Fq 'C:\Symbian3\APASTART.TXT'
strings "$apparc_launch_obj" | grep -Fq 'HTCLEO_MENU '
strings -el "$apparc_launch_obj" | grep -Fq 'C:\Symbian3\MENULOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$apparc_launch_disasm"
sha256sum "$apparc_launch_binary" >"$output/apparc-launch-client-urel.sha256"
sha256sum "$apparc_launch_obj" >"$output/apparc-launch-client-object-urel.sha256"

# Rebuild the shared Eikon core only after proving that the immutable 442 stock
# image is still available for comparison.  The source tree came from a
# case-insensitive host, while GCCE on Linux includes apfdef.h in lower case.
# The compatibility symlink changes no source content.  Existing ordinals
# 1-594 must remain byte-for-byte equivalent at the DEF semantic level; only
# ten reviewed GCCE constructor aliases may be appended at 595-604.
test -s "$eikcore_apf_inc/APFDEF.H"
ln -sfn APFDEF.H "$eikcore_apf_inc/apfdef.h"
if [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ]; then
    test "$(sha256sum "$eikcore_binary" | awk '{print $1}')" = 07cd59cab63934c014abdf2b0bc70ad9dfaf6b004dd44f14c7f2931b5b023f52
    # One generated local target only; immutable parent/cache remains untouched.
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll
fi
if [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ]; then
    test "$(sha256sum "$eikcore_binary" | awk '{print $1}')" = 6b890aff24a0be95baaba8616e27ca4cb2ab9fbc3e2e9834367209a47be5204d
    rm -f /root/symbian3-full/epoc32/release/armv5/urel/eikcore.dll
fi
if [ "$incremental_resource_policy" != gate19-filemanager-registration ]; then
    sbs_clean -b "$eikcore_bldinf" -c "$ssm_config"
    sbs_build_for "$eikcore_binary" -- \
        -b "$eikcore_bldinf" -c "$ssm_config" -j 4
fi
test -s "$eikcore_binary"
test "$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKENV.o' -type f | wc -l)" -eq 1
eikcore_obj=$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKENV.o' -type f)
test -s "$eikcore_obj"
test "$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKAPPUI.o' -type f | wc -l)" -eq 1
eikappui_obj=$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKAPPUI.o' -type f)
test -s "$eikappui_obj"
test "$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKSTART.o' -type f | wc -l)" -eq 1
eikstart_obj=$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/EIKSTART.o' -type f)
test -s "$eikstart_obj"
test "$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/eikcore{000a0000}.def' \
    -type f | wc -l)" -eq 1
eikcore_generated_def=$(find "$full_epocroot/epoc32/build/eikcore-build" \
    -path '*/eikcore_dll/armv5/urel/eikcore{000a0000}.def' -type f)
test -s "$eikcore_generated_def"
python3 "$eikcore_abi_audit" "$eikcore_frozen_def" \
    "$eikcore_generated_def" "$output"
grep -qx 'STATUS=HTCLEO_EIKCORE_ABI_OK' "$output/EIKCORE-ABI-RESULT.txt"
grep -qx 'FROZEN_EXPORTS=594' "$output/EIKCORE-ABI-RESULT.txt"
grep -qx 'GENERATED_EXPORTS=604' "$output/EIKCORE-ABI-RESULT.txt"

eikcore_disasm="$output/eikcore-akncap-prefactory-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eikcore_obj" >"$eikcore_disasm"
test "$(grep -c 'R_ARM_.*CALL.*_ZN9RProperty3SetE4TUidji' \
    "$eikcore_disasm")" -eq 2
test "$(grep -c 'R_ARM_.*CALL.*_ZN9RProperty6Define' \
    "$eikcore_disasm")" -eq 1
! grep -q 'R_ARM_.*CALL.*_ZN9RProperty\(3Get\|6Delete\)' \
    "$eikcore_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction' "$eikcore_disasm"
eikcore_home_construct_disasm="$output/eikcore-homescreen-constructapp-trace-urel.disasm"
cp "$eikcore_disasm" "$eikcore_home_construct_disasm"
grep -q 'HtcleoEikCoreHomeScreenTrace' "$eikcore_home_construct_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eikcore_home_construct_disasm"
strings "$eikcore_obj" | grep -Fq 'HTCLEO_HCE  '
strings -el "$eikcore_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User::After' \
    "$eikcore_home_construct_disasm"
eikappui_disasm="$output/eikappui-baseconstruct-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eikappui_obj" >"$eikappui_disasm"
grep -q 'HtcleoEikAppUiBaseLog' "$eikappui_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eikappui_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eikappui_disasm"
grep -q '0000b615' "$eikappui_disasm"
grep -qi '53434e32' "$eikappui_disasm"
strings "$eikappui_obj" | grep -Fq 'HTCLEO_EIKBASE '
strings -el "$eikappui_obj" | grep -Fq 'C:\Symbian3\EIKBASE.TXT'
strings "$eikappui_obj" | grep -Fq 'HTCLEO_HEB  '
strings -el "$eikappui_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
eikappui_home_disasm="$output/eikappui-homescreen-baseconstruct-trace-urel.disasm"
cp "$eikappui_disasm" "$eikappui_home_disasm"
grep -q 'HtcleoEikAppUiBaseLog' "$eikappui_home_disasm"
grep -q '0000b601' "$eikappui_home_disasm"
grep -q '0000b615' "$eikappui_home_disasm"
grep -qi '0000e370' "$eikappui_home_disasm"
grep -qi '0000e379' "$eikappui_home_disasm"
grep -qi '0000e380' "$eikappui_home_disasm"
grep -qi '0000e387' "$eikappui_home_disasm"
grep -q 'HandleAppToForeground' "$eikappui_home_disasm"
grep -q 'SetFaded' "$eikappui_home_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction' "$eikappui_disasm"

eikstart_home_disasm="$output/eikstart-homescreen-prefactory-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eikstart_obj" >"$eikstart_home_disasm"
grep -q 'HtcleoHomeEikStartLog' "$eikstart_home_disasm"
grep -q 'GetCommandLineFromProcessEnvironment' "$eikstart_home_disasm"
grep -q 'ConstructAppFromCommandLineL' "$eikstart_home_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eikstart_home_disasm"
strings "$eikstart_obj" | grep -Fq 'HTCLEO_HST  '
strings -el "$eikstart_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User::After' \
    "$eikstart_home_disasm"

eikcore_stock_work="$work/eikcore-stock-442.dll"
cp "$eikcore_stock_442" "$eikcore_stock_work"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eikcore_stock_work" >"$output/eikcore-stock-442-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eikcore_binary" >"$output/eikcore-e32-dump.txt"
for eikcore_dump in \
    "$output/eikcore-stock-442-e32-dump.txt" \
    "$output/eikcore-e32-dump.txt"
do
    grep -q 'Secure ID: 10004892' "$eikcore_dump"
    grep -q 'Vendor ID: 70000001' "$eikcore_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$eikcore_dump"
    grep -q 'Module Version: 10.0' "$eikcore_dump"
    grep -q 'Uids:.*10000079 1000008d 10004892' "$eikcore_dump"
    grep -q 'Dll ref table count: 20' "$eikcore_dump"
done
grep -q 'Export.*(594 entries)' "$output/eikcore-stock-442-e32-dump.txt"
grep -q 'Export.*(604 entries)' "$output/eikcore-e32-dump.txt"
sha256sum "$eikcore_stock_442" >"$output/eikcore-stock-442.sha256"
sha256sum "$eikcore_binary" >"$output/eikcore-urel.sha256"
sha256sum "$eikcore_obj" >"$output/eikcore-eikenv-object-urel.sha256"
sha256sum "$eikcore_obj" >"$output/eikcore-homescreen-constructapp-object-urel.sha256"
sha256sum "$eikappui_obj" >"$output/eikcore-eikappui-object-urel.sha256"
sha256sum "$eikappui_obj" \
    >"$output/eikcore-eikappui-homescreen-object-urel.sha256"
sha256sum "$eikstart_obj" >"$output/eikstart-homescreen-object-urel.sha256"
if [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$eikcore_binary" >"$output/eikcore-eikbase-813-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-eikbase-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/813-gsapp-eikbase-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-EIKBASE-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$eikcore_binary" >"$output/eikcore-env-808-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-env-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/808-gsapp-env-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-ENV-OBJECTS.json"
    # GSApp is reused byte-for-byte; do not leave analysis dumps from a dry run.
    cp "$incremental_parent_root/build/gsapp-e32-dump.txt" "$output/gsapp-e32-dump.txt"
fi



# Iteration 515 narrows MatrixMenu to the stock eikcoctl implementation of
# CEikAppUiFactory::ReadAppInfoResourceL, after the caller's B60E but before
# B60F. Preserve the complete 515 binary/header as the ABI reference and add
# close-only, SID-scoped B620-B631 breadcrumbs without changing behavior.
eikcoctl_stock_work="$work/eikcoctl-stock-515.dll"
cp "$eikcoctl_stock_515" "$eikcoctl_stock_work"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$eikcoctl_stock_work" \
    >"$output/eikcoctl-stock-515-e32-dump.txt"
# Original Windows EPOCROOT imports are case-insensitive. Preserve the existing
# DSOs and provide only the three exact-case aliases requested by this MMP.
test -s "$full_epocroot/epoc32/release/armv5/lib/akncapserverclient.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/ServiceHandler.dso"
test -s "$full_epocroot/epoc32/release/armv5/lib/aknlayout2.dso"
ln -sfn akncapserverclient.dso \
    "$full_epocroot/epoc32/release/armv5/lib/AknCapServerClient.dso"
ln -sfn ServiceHandler.dso \
    "$full_epocroot/epoc32/release/armv5/lib/servicehandler.dso"
ln -sfn aknlayout2.dso \
    "$full_epocroot/epoc32/release/armv5/lib/AknLayout2.dso"
sbs_clean --configpath="$eikcoctl_config_path" \
    -b "$eikcoctl_bldinf" -c "$eikcoctl_config"
if [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$avkon_common_geometry" "$full_epocroot"
    avkon_common_geometry_policy=portrait-client-status-cba-shared-360x640-to-480x800-logical-cba-reservation-no-app-whitelist
fi
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$eikcoctl_binary"
then
    rm -f "$eikcoctl_binary"
fi
sbs_build_for "$eikcoctl_binary" -- \
    --configpath="$eikcoctl_config_path" \
    -b "$eikcoctl_bldinf" -c "$eikcoctl_config" -j 4
test -s "$eikcoctl_binary"
test "$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/eikcoctl{000a0000}.def' \
    -type f | wc -l)" -eq 1
eikcoctl_generated_def=$(find \
    "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/eikcoctl{000a0000}.def' -type f)
test -s "$eikcoctl_generated_def"
python3 "$eikcoctl_abi_audit" "$eikcoctl_frozen_def" \
    "$eikcoctl_generated_def" "$output"
grep -qx 'STATUS=HTCLEO_EIKCOCTL_ABI_OK' \
    "$output/EIKCOCTL-ABI-RESULT.txt"
grep -qx 'FROZEN_EXPORTS=2018' "$output/EIKCOCTL-ABI-RESULT.txt"
grep -qx 'GENERATED_EXPORTS=2022' "$output/EIKCOCTL-ABI-RESULT.txt"
test "$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'EIKCOLIB.o' \
    -type f | wc -l)" -eq 1
eikcoctl_obj=$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'EIKCOLIB.o' -type f)
test -s "$eikcoctl_obj"
test "$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'eikspane.o' \
    -type f | wc -l)" -eq 1
eikcoctl_spane_obj=$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'eikspane.o' -type f)
test -s "$eikcoctl_spane_obj"
test "$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'eikspmod.o' \
    -type f | wc -l)" -eq 1
eikcoctl_spmod_obj=$(find "$full_epocroot/epoc32/build/eikcoctl-build" \
    -path '*/eikcoctl_dll/armv5/urel/*' -iname 'eikspmod.o' -type f)
test -s "$eikcoctl_spmod_obj"
eikcoctl_disasm="$output/eikcoctl-appinfo-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eikcoctl_obj" >"$eikcoctl_disasm"
eikcoctl_spane_disasm="$output/eikcoctl-homescreen-statuspane-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr -M force-thumb \
    "$eikcoctl_spane_obj" >"$eikcoctl_spane_disasm"
eikcoctl_spmod_disasm="$output/eikcoctl-aknlayoutrect-stack-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr -M force-thumb \
    "$eikcoctl_spmod_obj" >"$eikcoctl_spmod_disasm"
grep -q 'CEikStatusPaneLayoutTree13AknLayoutRect' "$eikcoctl_spmod_disasm"
grep -qi '0000b6f0\|b6f0' "$eikcoctl_spmod_disasm"
grep -q 'HtcleoEikAppInfoLog' "$eikcoctl_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eikcoctl_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eikcoctl_disasm"
grep -qi '0000b620\|b620' "$eikcoctl_disasm"
grep -qi '0000b631\|b631' "$eikcoctl_disasm"
grep -q 'ReadResourceAsDes8L' "$eikcoctl_disasm"
grep -q 'ReadAppInfoResourceExtensionL' "$eikcoctl_disasm"
grep -q 'CAknSgcClient.*HandleChangeL' "$eikcoctl_disasm"
strings "$eikcoctl_obj" | grep -Fq 'HTCLEO_EIKBASE '
strings "$eikcoctl_obj" | grep -Fq 'HTCLEO_HEI  '
strings -el "$eikcoctl_obj" | grep -Fq 'C:\Symbian3\EIKBASE.TXT'
strings -el "$eikcoctl_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction' "$eikcoctl_disasm"
grep -q 'HtcleoStatusPaneLog' "$eikcoctl_spane_disasm"
grep -qi '0000b640\|b640' "$eikcoctl_spane_disasm"
grep -qi '0000b67b\|b67b' "$eikcoctl_spane_disasm"
grep -qi '0000b70e\|b70e' "$eikcoctl_spane_disasm"
grep -qi '0000b70f\|b70f' "$eikcoctl_spane_disasm"
grep -qi '102750f0' "$eikcoctl_spane_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eikcoctl_spane_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eikcoctl_spane_disasm"
strings "$eikcoctl_spane_obj" | grep -Fq 'HTCLEO_HSP  '
strings -el "$eikcoctl_spane_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
strings "$eikcoctl_spmod_obj" | grep -Fq 'HTCLEO_HSM  '
strings -el "$eikcoctl_spmod_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$eikcoctl_binary" >"$output/eikcoctl-e32-dump.txt"
for eikcoctl_dump in \
    "$output/eikcoctl-stock-515-e32-dump.txt" \
    "$output/eikcoctl-e32-dump.txt"
do
    grep -qi 'Secure ID: 1000489e' "$eikcoctl_dump"
    grep -qi 'Vendor ID: 101fb657' "$eikcoctl_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$eikcoctl_dump"
    grep -q 'Module Version: 10.0' "$eikcoctl_dump"
    grep -qi 'Uids:.*10000079 1000008d 1000489e' "$eikcoctl_dump"
done
grep -q 'Export.*(2018 entries)' \
    "$output/eikcoctl-stock-515-e32-dump.txt"
grep -q 'Export.*(2022 entries)' "$output/eikcoctl-e32-dump.txt"
test "$(sed -n 's/^Export Description: Size=\([^,]*\),.*/\1/p' \
    "$output/eikcoctl-stock-515-e32-dump.txt")" = \
    "$(sed -n 's/^Export Description: Size=\([^,]*\),.*/\1/p' \
    "$output/eikcoctl-e32-dump.txt")"
sha256sum "$eikcoctl_stock_515" >"$output/eikcoctl-stock-515.sha256"
sha256sum "$eikcoctl_binary" >"$output/eikcoctl-urel.sha256"
if [ "$incremental_resource_policy" = gate17-avkon-common-geometry ]; then
    cp "$output/eikcoctl-e32-dump.txt" "$output/eikcoctl-geometry-851-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-avkon-common-geometry.py" \
        --native "$output" --report "$output/AVKON-GEOMETRY-OBJECTS.json"
    cp "$eikcoctl_binary.map" "$output/eikcoctl-geometry-851.map"
    cp "$eikcoctl_binary.sym" "$output/eikcoctl-geometry-851.sym"
    for geometry_source in EIKCOLIB.CPP eikspane.cpp eikcba.cpp htcleoavkongeometry851.inl; do
        cp "$full_epocroot/sf/mw/classicui/uifw/EikStd/coctlsrc/$geometry_source" "$output/851-$geometry_source"
    done
fi
if [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$eikcoctl_binary" >"$output/eikcoctl-appinfo-814-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-appinfo-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/814-gsapp-appinfo-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-APPINFO-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$eikcoctl_binary" >"$output/eikcoctl-statuspane-815-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-statuspane-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/815-gsapp-statuspane-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-STATUSPANE-OBJECTS.json"
fi
sha256sum "$eikcoctl_obj" \
    >"$output/eikcoctl-eikcolib-object-urel.sha256"
sha256sum "$eikcoctl_spane_obj" \
    >"$output/eikcoctl-eikspane-object-urel.sha256"
sha256sum "$eikcoctl_spmod_obj" \
    >"$output/eikcoctl-eikspmod-object-urel.sha256"

# Iteration 445 proves featmgrserver dies after Resume/WaitForRequest with
# EExitKill/KErrServerTerminated.  Iteration 446 fixes the stock iRegistry
# construction-order defect, but its unconditional E603 post-TRAP record hides
# the last E61x/E63x stage during unwind.  Rebuild both the frozen-ABI client DLL
# and stock-identity server with E603 restricted to a no-deep-stage fallback.
# The E6xx server trace remains P&S-only and is copied into the existing AknCap
# durable stream only when startup fails.
sbs_clean -b "$featmgr_bldinf" -c "$ssm_config"
sbs_build_for "$featmgr_binary" "$featmgrserver_binary" -- \
    -b "$featmgr_bldinf" -c "$ssm_config" -j 4
restore_incremental_sibling_output "$featmgr_binary"
restore_incremental_sibling_output "$featmgrserver_binary"
test -s "$featmgr_binary"
test -s "$featmgrserver_binary"
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgr.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgrclient.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgrtlsdata.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgr{000a0000}.def' \
    -type f | wc -l)" -eq 1
featmgr_obj=$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgr.o' -type f)
featmgr_client_obj=$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgrclient.o' -type f)
featmgr_tls_obj=$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgrtlsdata.o' -type f)
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgrserver_exe/armv5/urel/featmgrstartup.o' \
    -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgrserver_exe/armv5/urel/featmgrserver.o' \
    -type f | wc -l)" -eq 1
featmgrserver_startup_obj=$(find \
    "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgrserver_exe/armv5/urel/featmgrstartup.o' -type f)
featmgrserver_obj=$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgrserver_exe/armv5/urel/featmgrserver.o' -type f)
featmgr_generated_def=$(find "$full_epocroot/epoc32/build/featmgr-build" \
    -path '*/featmgr_dll/armv5/urel/featmgr{000a0000}.def' -type f)
for featmgr_artifact in "$featmgr_obj" "$featmgr_client_obj" \
    "$featmgr_tls_obj" "$featmgrserver_startup_obj" \
    "$featmgrserver_obj" "$featmgr_generated_def"
do
    test -s "$featmgr_artifact"
done

tr -d '\r' <"$featmgr_frozen_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/featmgr-frozen-exports.def"
tr -d '\r' <"$featmgr_generated_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/featmgr-generated-exports.def"
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/featmgr-frozen-exports.def" | wc -l)" -eq 58
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/featmgr-generated-exports.def" | wc -l)" -eq 58
test "$(grep -c 'ABSENT' "$output/featmgr-frozen-exports.def")" -eq 14
test "$(grep -c 'ABSENT' "$output/featmgr-generated-exports.def")" -eq 14
diff -u "$output/featmgr-frozen-exports.def" \
    "$output/featmgr-generated-exports.def"

featmgr_disasm="$output/featmgr-akncap-trace-urel.disasm"
featmgr_client_disasm="$output/featmgr-client-akncap-trace-urel.disasm"
featmgr_tls_disasm="$output/featmgr-tls-akncap-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$featmgr_obj" >"$featmgr_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$featmgr_client_obj" >"$featmgr_client_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$featmgr_tls_obj" >"$featmgr_tls_disasm"
test "$(grep -c 'R_ARM_THM_CALL.*_ZN9RProperty3SetE4TUidji' \
    "$featmgr_disasm")" -eq 1
test "$(grep -h -c 'R_ARM_THM_CALL.*HtcleoFeatMgrAknCapTrace' \
    "$featmgr_disasm" "$featmgr_client_disasm" \
    "$featmgr_tls_disasm" | awk '{s += $1} END {print s}')" -eq 36
grep -q 'R_ARM_THM_CALL.*_ZN9RProperty3GetE4TUidjRi' \
    "$featmgr_client_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction' \
    "$featmgr_disasm" "$featmgr_client_disasm" "$featmgr_tls_disasm"

featmgrserver_startup_disasm="$output/featmgrserver-deepest-stage-preserve-urel.disasm"
featmgrserver_disasm="$output/featmgrserver-registry-order-fix-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$featmgrserver_startup_obj" >"$featmgrserver_startup_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$featmgrserver_obj" >"$featmgrserver_disasm"
grep -q 'R_ARM_THM_CALL.*_ZN9RProperty6DefineE4TUidjiRK15TSecurityPolicyS3_i' \
    "$featmgrserver_startup_disasm"
grep -q 'R_ARM_THM_CALL.*_ZN9RProperty3SetE4TUidji' \
    "$featmgrserver_startup_disasm"
grep -q 'R_ARM_THM_CALL.*_ZN9RProperty3GetE4TUidjRi' \
    "$featmgrserver_startup_disasm"
grep -q 'R_ARM_THM_CALL.*HtcleoFeatMgrServerTrace' \
    "$featmgrserver_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$featmgrserver_startup_disasm" "$featmgrserver_disasm"

featmgr_stock_work="$work/featmgr-stock-444.dll"
cp "$featmgr_stock_444" "$featmgr_stock_work"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$featmgr_stock_work" \
    >"$output/featmgr-stock-444-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$featmgr_binary" >"$output/featmgr-e32-dump.txt"
for featmgr_dump in \
    "$output/featmgr-stock-444-e32-dump.txt" \
    "$output/featmgr-e32-dump.txt"
do
    grep -q 'Secure ID: 10005a2b' "$featmgr_dump"
    grep -q 'Vendor ID: 70000001' "$featmgr_dump"
    grep -q 'Capabilities: 00000000 000ffffe' "$featmgr_dump"
    grep -q 'Module Version: 10.0' "$featmgr_dump"
    grep -q 'Uids:.*10000079 1000008d 10005a2b' "$featmgr_dump"
    grep -q 'Dll ref table count: 4' "$featmgr_dump"
    grep -q 'Export.*(58 entries)' "$featmgr_dump"
done
sha256sum "$featmgr_stock_444" >"$output/featmgr-stock-444.sha256"
sha256sum "$featmgr_binary" >"$output/featmgr-urel.sha256"
sha256sum "$featmgr_obj" >"$output/featmgr-object-urel.sha256"
sha256sum "$featmgr_client_obj" >"$output/featmgr-client-object-urel.sha256"
sha256sum "$featmgr_tls_obj" >"$output/featmgr-tls-object-urel.sha256"

featmgrserver_stock_work="$work/featmgrserver-stock-445.exe"
cp "$featmgrserver_stock_445" "$featmgrserver_stock_work"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$featmgrserver_stock_work" \
    >"$output/featmgrserver-stock-445-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$featmgrserver_binary" \
    >"$output/featmgrserver-e32-dump.txt"
for featmgrserver_dump in \
    "$output/featmgrserver-stock-445-e32-dump.txt" \
    "$output/featmgrserver-e32-dump.txt"
do
    grep -q 'Secure ID: 10205054' "$featmgrserver_dump"
    grep -q 'Vendor ID: 70000001' "$featmgrserver_dump"
    grep -q 'Capabilities: 00000000 00000110' "$featmgrserver_dump"
    grep -q 'Module Version: 10.0' "$featmgrserver_dump"
    grep -q 'Uids:.*1000007a 10205054 10205054' "$featmgrserver_dump"
    grep -q 'Dll ref table count: 7' "$featmgrserver_dump"
done
sha256sum "$featmgrserver_stock_445" \
    >"$output/featmgrserver-stock-445.sha256"
sha256sum "$featmgrserver_binary" \
    >"$output/featmgrserver-urel.sha256"
sha256sum "$featmgrserver_startup_obj" \
    >"$output/featmgrserver-startup-object-urel.sha256"
sha256sum "$featmgrserver_obj" \
    >"$output/featmgrserver-object-urel.sha256"

# Rebuild the exact application process selected by UID 0x101FDFAE.  Iteration
# 437 proves APSEXE/AppArc and the caller-side StartApp request succeed but the
# process rendezvous completes with KErrServerTerminated.  These fail-open
# records therefore start at E32Main and bracket application/document/AppUi
# construction without changing any leave, panic, retry or scheduling rule.
# The PDK import DSOs were produced on a case-insensitive Windows host; expose
# only lower-case aliases expected by the unchanged MMP on Linux.
akncapserver_libdir="$full_epocroot/epoc32/release/armv5/lib"
for akncapserver_dso_pair in \
    'CommonEngine.dso commonengine.dso' \
    'PtiEngine.dso ptiengine.dso' \
    'WidgetRegistryClient.dso widgetregistryclient.dso' \
    'AknDynamicSoftNoteEventManager.dso akndynamicsoftnoteeventmanager.dso' \
    'EComPluginNotifier.dso ecompluginnotifier.dso'
do
    set -- $akncapserver_dso_pair
    test -s "$akncapserver_libdir/$1"
    ln -sfn "$1" "$akncapserver_libdir/$2"
done
sbs_clean -b "$akncapserver_bldinf" -c "$ssm_config"
sbs_build_for "$akncapserver_binary" -- \
    -b "$akncapserver_bldinf" -c "$ssm_config" -j 4
test -s "$akncapserver_binary"
test "$(find "$full_epocroot/epoc32/build/akncapserver-build" \
    -path '*/akncapserver_exe/armv5/urel/AknCapServerEntry.o' \
    -type f | wc -l)" -eq 1
akncapserver_obj=$(find "$full_epocroot/epoc32/build/akncapserver-build" \
    -path '*/akncapserver_exe/armv5/urel/AknCapServerEntry.o' -type f)
test -s "$akncapserver_obj"
akncapserver_disasm="$output/akncapserver-startup-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$akncapserver_obj" >"$akncapserver_disasm"
! grep -q 'R_ARM_.*CALL.*EikStart.*RunApplication' "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*GetCommandLineFromProcessEnvironment' \
    "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*ConstructAppFromCommandLineL' \
    "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*_ZN8RProcess10RendezvousEi' \
    "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Define' "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Set' "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*RProperty.*Get' "$akncapserver_disasm"
! grep -q 'R_ARM_.*CALL.*RProperty.*Delete' "$akncapserver_disasm"
test "$(grep -c 'R_ARM_.*CALL.*_ZN11TFindServer4Next' \
    "$akncapserver_disasm")" -eq 2
test "$(grep -c 'R_ARM_.*CALL.*_ZNK9CEikonEnv9AppServerEv' \
    "$akncapserver_disasm")" -eq 1
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$akncapserver_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$akncapserver_disasm"
strings "$akncapserver_obj" | grep -Fq 'HTCLEO_AKNCAP '
strings -el "$akncapserver_obj" | grep -Fq 'C:\Symbian3\AKNCAP.TXT'
! grep -q 'e7f000f0\|c6400000' "$akncapserver_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$akncapserver_binary" >"$output/akncapserver-e32-dump.txt"
grep -q 'Secure ID: 10207218' "$output/akncapserver-e32-dump.txt"
grep -q 'Uids:.*1000007a 100039ce 10207218' \
    "$output/akncapserver-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/akncapserver-e32-dump.txt"
sha256sum "$akncapserver_binary" >"$output/akncapserver-urel.sha256"
sha256sum "$akncapserver_obj" \
    >"$output/akncapserver-entry-object-urel.sha256"

# Iteration 462 proves the Eikon server reaches its rendezvous/scheduler
# boundary while AknCap remains inside REikAppUiSession::Connect.  Rebuild only
# the client-session DLL with an AknCap-SID-gated, fail-open durable trace that
# splits Close, CreateSession, StartServerL, rendezvous, retry and extension
# construction, the QSD8250 synchronous lost-rendezvous cancellation and the
# AknCap-only one-child bounded readiness retry. Server binaries and all
# established compatibility fixes stay byte-identical to the immutable parent.
if [ "$incremental_eiksrvc_resume" != 1 ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=h \
        --e32input="$eiksrvc_binary" \
        >"$output/eiksrvc-stock-466-e32-dump.txt"
fi
test -s "$output/eiksrvc-stock-466-e32-dump.txt"
grep -q 'Secure ID: 100053b1' "$output/eiksrvc-stock-466-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/eiksrvc-stock-466-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/eiksrvc-stock-466-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 100053b1' \
    "$output/eiksrvc-stock-466-e32-dump.txt"
sbs_clean -b "$eiksrvc_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$eiksrvc_binary"
then
    rm -f "$eiksrvc_binary"
fi
sbs_build_for "$eiksrvc_binary" -- \
    -b "$eiksrvc_bldinf" -c "$ssm_config" -j 4
test -s "$eiksrvc_binary"
test "$(find "$full_epocroot/epoc32/build/eiksrvc-build" \
    -path '*/eiksrvc_dll/armv5/urel/*' -iname 'eiksrvc.o' \
    -type f | wc -l)" -eq 1
eiksrvc_obj=$(find "$full_epocroot/epoc32/build/eiksrvc-build" \
    -path '*/eiksrvc_dll/armv5/urel/*' -iname 'eiksrvc.o' -type f)
test -s "$eiksrvc_obj"
eiksrvc_generated_def=$(find "$full_epocroot/epoc32/build/eiksrvc-build" \
    -path '*/eiksrvc_dll/armv5/urel/*' -iname 'eiksrvc*.def' \
    -type f | head -n 1)
test -n "$eiksrvc_generated_def" && test -s "$eiksrvc_generated_def"
tr -d '\r' <"$eiksrvc_frozen_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/eiksrvc-frozen-exports.def"
tr -d '\r' <"$eiksrvc_generated_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/eiksrvc-generated-exports.def"
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/eiksrvc-frozen-exports.def" | wc -l)" -eq 29
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/eiksrvc-generated-exports.def" | wc -l)" -eq 29
diff -u "$output/eiksrvc-frozen-exports.def" \
    "$output/eiksrvc-generated-exports.def"
eiksrvc_disasm="$output/eiksrvc-client-connect-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eiksrvc_obj" >"$eiksrvc_disasm"
grep -q 'HtcleoEikConnLog' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*RSessionBase.*CreateSession' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Create' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Rendezvous' "$eiksrvc_disasm"
grep -q 'R_ARM_.*CALL.*User.*WaitForRequest' "$eiksrvc_disasm"
strings "$eiksrvc_obj" | grep -Fq 'HTCLEO_EIKCONN '
strings -el "$eiksrvc_obj" | grep -Fq 'C:\Symbian3\EIKCONN.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$eiksrvc_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eiksrvc_binary" >"$output/eiksrvc-e32-dump.txt"
grep -q 'Secure ID: 100053b1' "$output/eiksrvc-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/eiksrvc-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' "$output/eiksrvc-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 100053b1' \
    "$output/eiksrvc-e32-dump.txt"
test "$(sed -n 's/^Export Description: Size=//p' \
    "$output/eiksrvc-e32-dump.txt")" = \
    "$(sed -n 's/^Export Description: Size=//p' \
        "$output/eiksrvc-stock-466-e32-dump.txt")"
sha256sum "$eiksrvc_binary" >"$output/eiksrvc-urel.sha256"
sha256sum "$eiksrvc_obj" >"$output/eiksrvc-object-urel.sha256"

# AknCap iteration 454 reaches iEikSrv.Connect() but never records its return.
# Rebuild only the Eikon server stub with a fail-open trace around CEikServEnv,
# CEikServAppUiServer and process Rendezvous.  Shared eiksrv/eikcore binaries
# remain byte-identical parent inputs.
sbs_clean -b "$eiksrvs_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$eiksrvs_binary"
then
    rm -f "$eiksrvs_binary"
fi
sbs_build_for "$eiksrvs_binary" -- \
    -b "$eiksrvs_bldinf" -c "$ssm_config" -j 4
test -s "$eiksrvs_binary"
test "$(find "$full_epocroot/epoc32/build/eiksrvs-build" \
    -path '*/eiksrvs_exe/armv5/urel/*' -iname 'eiksrvs.o' \
    -type f | wc -l)" -eq 1
eiksrvs_obj=$(find "$full_epocroot/epoc32/build/eiksrvs-build" \
    -path '*/eiksrvs_exe/armv5/urel/*' -iname 'eiksrvs.o' -type f)
test -s "$eiksrvs_obj"
eiksrvs_disasm="$output/eiksrvs-startup-rendezvous-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eiksrvs_obj" >"$eiksrvs_disasm"
grep -q 'HtcleoEikSrvLog' "$eiksrvs_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eiksrvs_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eiksrvs_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Rendezvous' "$eiksrvs_disasm"
grep -q 'R_ARM_.*CALL.*CEikonEnv.*ConstructL' "$eiksrvs_disasm"
grep -q 'R_ARM_.*CALL.*CEikServAppUiServer.*NewL' "$eiksrvs_disasm"
strings "$eiksrvs_obj" | grep -Fq 'HTCLEO_EIKSRV '
strings -el "$eiksrvs_obj" | grep -Fq 'C:\Symbian3\EIKSRV.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' "$eiksrvs_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eiksrvs_binary" >"$output/eiksrvs-e32-dump.txt"
grep -q 'Secure ID: 10003a4a' "$output/eiksrvs-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/eiksrvs-e32-dump.txt"
grep -q 'Capabilities: 00000000 00000180' "$output/eiksrvs-e32-dump.txt"
grep -q 'Uids:.*1000007a 1000008d 10003a4a' \
    "$output/eiksrvs-e32-dump.txt"
sha256sum "$eiksrvs_binary" >"$output/eiksrvs-urel.sha256"
sha256sum "$eiksrvs_obj" >"$output/eiksrvs-object-urel.sha256"

# Iteration 455 proves CEikServAppUiServer::NewL is entered but does not
# return. That implementation lives in eiksrv.dll, so trace its stock NewL and
# ConstructL dependency chain while retaining the verified parent executable,
# eikcore and all earlier components byte-for-byte.
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eiksrv_binary" >"$output/eiksrv-stock-455-e32-dump.txt"
grep -q 'Secure ID: 10003a4a' "$output/eiksrv-stock-455-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/eiksrv-stock-455-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/eiksrv-stock-455-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 10003a4a' \
    "$output/eiksrv-stock-455-e32-dump.txt"
sbs_clean -b "$eiksrv_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$eiksrv_binary"
then
    rm -f "$eiksrv_binary"
fi
sbs_build_for "$eiksrv_binary" -- \
    -b "$eiksrv_bldinf" -c "$ssm_config" -j 4
test -s "$eiksrv_binary"
test "$(find "$full_epocroot/epoc32/build/eiksrv-build" \
    -path '*/eiksrv_dll/armv5/urel/*' -iname 'eiksrv.o' \
    -type f | wc -l)" -eq 1
eiksrv_obj=$(find "$full_epocroot/epoc32/build/eiksrv-build" \
    -path '*/eiksrv_dll/armv5/urel/*' -iname 'eiksrv.o' -type f)
test -s "$eiksrv_obj"
eiksrv_disasm="$output/eiksrv-server-construct-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eiksrv_obj" >"$eiksrv_disasm"
grep -q 'HtcleoEikSrvDeepLog' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*FindWindowGroupIdentifier' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*CRepository' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*RLibrary.*Load' "$eiksrv_disasm"
grep -q 'R_ARM_.*CALL.*CServer2.*StartL' "$eiksrv_disasm"
strings "$eiksrv_obj" | grep -Fq 'HTCLEO_EIKSRV '
strings -el "$eiksrv_obj" | grep -Fq 'C:\Symbian3\EIKSRV.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' "$eiksrv_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eiksrv_binary" >"$output/eiksrv-e32-dump.txt"
grep -q 'Secure ID: 10003a4a' "$output/eiksrv-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/eiksrv-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' "$output/eiksrv-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 10003a4a' \
    "$output/eiksrv-e32-dump.txt"
test "$(sed -n 's/^Export Description: Size=//p' \
    "$output/eiksrv-e32-dump.txt")" = \
    "$(sed -n 's/^Export Description: Size=//p' \
    "$output/eiksrv-stock-455-e32-dump.txt")"
sha256sum "$eiksrv_binary" >"$output/eiksrv-urel.sha256"
sha256sum "$eiksrv_obj" >"$output/eiksrv-object-urel.sha256"

# Iteration 474 traces the active STEM Avkon BaseConstructL from B500 through
# B520. Iteration 475 skips only EikSrv's blocking fixed-screen screen-change
# subscription. Iteration 476 supplies the hardware-proven 480x800 panel size
# only to EikSrv after the stock synchronous size query blocked. Iteration 477
# also defers only EikSrv's optional tactile-feedback adaptation after hardware
# bracketed its NewL call at B506. Iteration 479 traces Post-Coe layout/SGC and
# reuses the same proven fixed panel for EikSrv's second synchronous size query;
# every other process retains all stock calls.
echo "HTCLEO_STEM_AVKON_BUILD_BEGIN binary=$stem_avkon_binary"
test -s "$stem_avkon_stock_473"
# The legacy 32-bit elf2e32 has a short-path limit. Keep the authoritative
# stock image under output, but use a hash-checked short working path to dump it.
cp "$stem_avkon_stock_473" "$stem_avkon_stock_473_dump_input"
test "$(sha256sum "$stem_avkon_stock_473_dump_input" | awk '{print $1}')" = \
    "$(sha256sum "$stem_avkon_stock_473" | awk '{print $1}')"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$stem_avkon_stock_473_dump_input" \
    >"$output/stem-avkon-stock-473-e32-dump.txt"
echo "HTCLEO_STEM_AVKON_STOCK_HEADER_OK"
# Preserve the isolated Avkon object cache during normal immutable incremental
# iterations.  Source/config dependency changes still rebuild their stale
# objects; full-clean remains available for toolchain or ABI recovery.
if [ "$build_mode" = full-clean ]; then
    sbs_clean --configpath="$stem_avkon_config_path" \
        -b "$stem_avkon_bldinf" -c "$stem_avkon_config"
fi
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$stem_avkon_binary" && \
    [ "$incremental_resource_policy" != gate19-filemanager-registration ]
then
    rm -f "$stem_avkon_binary"
fi
if [ "$incremental_resource_policy" != gate19-filemanager-registration ]; then
    sbs_build_for "$stem_avkon_binary" -- \
        --configpath="$stem_avkon_config_path" \
        -b "$stem_avkon_bldinf" -c "$stem_avkon_config" -j 4
fi
echo "HTCLEO_STEM_AVKON_SBS_RETURNED"
test -s "$stem_avkon_binary"
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknappui.o' \
    -type f | wc -l)" -eq 1
stem_avkon_obj=$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknappui.o' -type f)
test -s "$stem_avkon_obj"
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknviewappui.o' \
    -type f | wc -l)" -eq 1
stem_avkon_viewappui_obj=$(find \
    "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknviewappui.o' -type f)
test -s "$stem_avkon_viewappui_obj"
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknenv.o' \
    -type f | wc -l)" -eq 1
stem_avkon_aknenv_obj=$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknenv.o' -type f)
test -s "$stem_avkon_aknenv_obj"
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknsgcc.o' \
    -type f | wc -l)" -eq 1
stem_avkon_sgc_obj=$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknsgcc.o' -type f)
test -s "$stem_avkon_sgc_obj"
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknlists.o' \
    -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknlongtapdetector.o' \
    -type f | wc -l)" -eq 1
stem_avkon_lists_obj=$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknlists.o' -type f)
stem_avkon_longtap_obj=$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/*' -iname 'aknlongtapdetector.o' -type f)
python3 "$stem_avkon_abi_promoter" "$stem_avkon_lists_obj"
python3 "$stem_avkon_abi_promoter" "$stem_avkon_longtap_obj"
for stem_avkon_popup_comdat_name in \
    AknPopupField.o AknPopupSettingPage.o aknenv.o aknlib.o
do
    test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
        -path '*/stem_avkon_dll/armv5/urel/*' \
        -name "$stem_avkon_popup_comdat_name" -type f | wc -l)" -eq 1
    stem_avkon_popup_comdat_obj=$(find \
        "$full_epocroot/epoc32/build/stem-avkon-build" \
        -path '*/stem_avkon_dll/armv5/urel/*' \
        -name "$stem_avkon_popup_comdat_name" -type f)
    python3 "$stem_avkon_abi_promoter" "$stem_avkon_popup_comdat_obj"
done
test "$(find "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/stem_avkon{000a0000}.def' \
    -type f | wc -l)" -eq 1
stem_avkon_generated_def=$(find \
    "$full_epocroot/epoc32/build/stem-avkon-build" \
    -path '*/stem_avkon_dll/armv5/urel/stem_avkon{000a0000}.def' -type f)
python3 "$stem_avkon_abi_audit" "$stem_avkon_frozen_def" \
    "$stem_avkon_generated_def" "$output"
grep -qx 'STATUS=HTCLEO_AVKON_ABI_OK' \
    "$output/STEM-AVKON-ABI-RESULT.txt"
grep -qx 'FROZEN_EXPORTS=4604' "$output/STEM-AVKON-ABI-RESULT.txt"
grep -qx 'GENERATED_EXPORTS=4613' "$output/STEM-AVKON-ABI-RESULT.txt"
stem_avkon_disasm="$output/stem-avkon-baseconstruct-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_avkon_obj" >"$stem_avkon_disasm"
grep -q 'HtcleoAknAppUiBaseLog' "$stem_avkon_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_avkon_disasm"
grep -q 'R_ARM_.*CALL.*RWindowGroup24EnableScreenChangeEvents' \
    "$stem_avkon_disasm"
grep -qi '5343524e' "$stem_avkon_disasm"
grep -qi '53495a45' "$stem_avkon_disasm"
grep -qi '48415054' "$stem_avkon_disasm"
grep -q 'R_ARM_.*CALL.*CTouchFeedbackAdaptation4NewL' \
    "$stem_avkon_disasm"
# Iteration 483 hardware-proves B51B and shows that dense logger traffic is now
# the frontier. Keep Write/Close, reject the retired Flush, and verify the
# remaining B51C-B520 diagnostic bounds in the object.
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$stem_avkon_disasm"
# GCCE folds the entry checkpoint B500 into register arithmetic, while B501
# and the final B520 remain literal pool values.  Verify those durable bounds
# together with the source-transform fail-closed checks above.
grep -q '0000b501' "$stem_avkon_disasm"
grep -q '0000b51c' "$stem_avkon_disasm"
grep -q '0000b520' "$stem_avkon_disasm"
grep -q '0000b547' "$stem_avkon_disasm"
grep -qi '46495832' "$stem_avkon_disasm"
strings "$stem_avkon_obj" | grep -Fq 'HTCLEO_AKNBASE '
strings -el "$stem_avkon_obj" | grep -Fq 'C:\Symbian3\AKNBASE.TXT'
strings "$stem_avkon_obj" | grep -Fq 'HTCLEO_HAB  '
strings -el "$stem_avkon_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
stem_avkon_home_base_disasm="$output/stem-avkon-aknappui-homescreen-baseconstruct-trace-urel.disasm"
cp "$stem_avkon_disasm" "$stem_avkon_home_base_disasm"
grep -q 'HtcleoAknAppUiBaseLog' "$stem_avkon_home_base_disasm"
grep -q '0000b501' "$stem_avkon_home_base_disasm"
grep -q '0000b520' "$stem_avkon_home_base_disasm"
stem_avkon_home_postcoe_disasm="$output/stem-avkon-aknappui-homescreen-postcoe-trace-urel.disasm"
cp "$stem_avkon_disasm" "$stem_avkon_home_postcoe_disasm"
grep -q '0000b530' "$stem_avkon_home_postcoe_disasm"
grep -q '0000b547' "$stem_avkon_home_postcoe_disasm"
strings "$stem_avkon_obj" | grep -Fq 'HTCLEO_HAB  '
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_disasm"
stem_avkon_aknenv_disasm="$output/stem-avkon-aknenv-matrixmenu-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_avkon_aknenv_obj" >"$stem_avkon_aknenv_disasm"
grep -q 'HtcleoAknEnvMenuLog' "$stem_avkon_aknenv_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_avkon_aknenv_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$stem_avkon_aknenv_disasm"
grep -qi '4d4da001' "$stem_avkon_aknenv_disasm"
grep -qi '4d4da01a' "$stem_avkon_aknenv_disasm"
strings "$stem_avkon_aknenv_obj" | grep -Fq 'HTCLEO_MENU '
strings "$stem_avkon_aknenv_obj" | grep -Fq 'HTCLEO_HAK  '
strings -el "$stem_avkon_aknenv_obj" | grep -Fq 'C:\Symbian3\MENULOG.TXT'
strings -el "$stem_avkon_aknenv_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_aknenv_disasm"
stem_avkon_aknenv_home_disasm="$output/stem-avkon-aknenv-homescreen-trace-cdl-reconnect-urel.disasm"
cp "$stem_avkon_aknenv_disasm" "$stem_avkon_aknenv_home_disasm"
grep -q 'HtcleoAknEnvMenuLog' "$stem_avkon_aknenv_home_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_avkon_aknenv_home_disasm"
grep -qi '4d4da01e' "$stem_avkon_aknenv_home_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_aknenv_home_disasm"
stem_avkon_sgc_disasm="$output/stem-avkon-sgc-handlechange-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_avkon_sgc_obj" >"$stem_avkon_sgc_disasm"
grep -q 'HtcleoAknAppUiBaseLog' "$stem_avkon_sgc_disasm"
grep -q 'HtcleoAknSgcMenuLog' "$stem_avkon_sgc_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_avkon_sgc_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$stem_avkon_sgc_disasm"
grep -qi '4d4da100' "$stem_avkon_sgc_disasm"
grep -qi '4d4da132' "$stem_avkon_sgc_disasm"
grep -q '0000c52c' "$stem_avkon_sgc_disasm"
grep -q 'R_ARM_.*CALL.*SetSgcParams' "$stem_avkon_sgc_disasm"
strings "$stem_avkon_sgc_obj" | grep -Fq 'HTCLEO_MENU '
strings "$stem_avkon_sgc_obj" | grep -Fq 'HTCLEO_HSG  '
strings -el "$stem_avkon_sgc_obj" | grep -Fq 'C:\Symbian3\MENULOG.TXT'
strings -el "$stem_avkon_sgc_obj" | grep -Fq 'C:\Symbian3\HSXML.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_sgc_disasm"
stem_avkon_sgc_home_disasm="$output/stem-avkon-sgc-homescreen-trace-akncap-fail-open-urel.disasm"
cp "$stem_avkon_sgc_disasm" "$stem_avkon_sgc_home_disasm"
grep -q 'HtcleoAknSgcMenuLog' "$stem_avkon_sgc_home_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$stem_avkon_sgc_home_disasm"
grep -qi '4d4da133' "$stem_avkon_sgc_home_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_sgc_home_disasm"
stem_avkon_home_focus_disasm="$output/stem-avkon-homescreen-focus-keyblock-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_avkon_viewappui_obj" >"$output/stem-avkon-viewappui-foreground.tmp"
cat "$stem_avkon_disasm" "$stem_avkon_sgc_disasm" \
    "$output/stem-avkon-viewappui-foreground.tmp" \
    >"$stem_avkon_home_focus_disasm"
rm -f "$output/stem-avkon-viewappui-foreground.tmp"
grep -qi '0000c560' "$stem_avkon_home_focus_disasm"
grep -qi '0000c56e' "$stem_avkon_home_focus_disasm"
grep -qi '0000c570' "$stem_avkon_home_focus_disasm"
grep -qi '0000c576' "$stem_avkon_home_focus_disasm"
grep -qi '0000c577' "$stem_avkon_home_focus_disasm"
grep -qi '0000c57f' "$stem_avkon_home_focus_disasm"
grep -qi '0000c580' "$stem_avkon_home_focus_disasm"
grep -qi '0000c593' "$stem_avkon_home_focus_disasm"
grep -qi '0000c598' "$stem_avkon_home_focus_disasm"
grep -qi '0000c59e' "$stem_avkon_home_focus_disasm"
grep -q 'ProcessForegroundEventL' "$stem_avkon_home_focus_disasm"
grep -q 'R_ARM_.*CALL.*SetKeyblockMode' "$stem_avkon_home_focus_disasm"
grep -q 'R_ARM_.*CALL.*IsSystemFaded' "$stem_avkon_home_focus_disasm"
grep -q 'R_ARM_.*CALL.*SetSystemFaded' "$stem_avkon_home_focus_disasm"
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$stem_avkon_home_focus_disasm"
stem_avkon_home_postcoe_sgc_disasm="$output/stem-avkon-aknsgc-homescreen-postcoe-trace-urel.disasm"
cp "$stem_avkon_sgc_disasm" "$stem_avkon_home_postcoe_sgc_disasm"
grep -qi '0000c501' "$stem_avkon_home_postcoe_sgc_disasm"
grep -qi '0000c52c' "$stem_avkon_home_postcoe_sgc_disasm"
stem_avkon_home_setparams_disasm="$output/stem-avkon-aknsgc-homescreen-setparams-defer-urel.disasm"
cp "$stem_avkon_sgc_disasm" "$stem_avkon_home_setparams_disasm"
grep -qi '102750f0' "$stem_avkon_home_setparams_disasm"
grep -qi '0000c529' "$stem_avkon_home_setparams_disasm"
grep -qi '0000c52a' "$stem_avkon_home_setparams_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$stem_avkon_binary" >"$output/stem-avkon-e32-dump.txt"
grep -q 'Secure ID: 100056c6' "$output/stem-avkon-e32-dump.txt"
grep -q 'Vendor ID: 101fb657' "$output/stem-avkon-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/stem-avkon-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 100056c6' \
    "$output/stem-avkon-e32-dump.txt"
grep -q '(4613 entries)' "$output/stem-avkon-e32-dump.txt"
grep -q 'Export Description: Size=063, Type=02' \
    "$output/stem-avkon-e32-dump.txt"
grep -q 'Export Description: Size=062, Type=02' \
    "$output/stem-avkon-stock-473-e32-dump.txt"
sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
if [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-aknenv-809-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-aknenv-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/809-gsapp-aknenv-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-AKNENV-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-sgc-810-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-sgc-local-layout.py" \
        --baseline "$project/Symbian/output/iteration-evidence/810-gsapp-sgc-local-layout/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-SGC-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-appui-811-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-appui-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/811-gsapp-appui-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-APPUI-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-focus-818-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-focus-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/818-gsapp-focus-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-FOCUS-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-sgc-params-812-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-sgc-params-local.py" \
        --baseline "$project/Symbian/output/iteration-evidence/812-gsapp-sgc-params-local/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-SGC-PARAMS-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-sgc-fade-816-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-sgc-fade-local.py" \
        --baseline "$project/Symbian/output/iteration-evidence/816-gsapp-sgc-fade-local/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-SGC-FADE-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-keyblock-819-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-keyblock-local.py" \
        --baseline "$project/Symbian/output/iteration-evidence/819-gsapp-keyblock-local/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-KEYBLOCK-OBJECTS.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-view-transition ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-view-transition-830-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-view-transition.py" \
        --baseline "$project/Symbian/output/iteration-evidence/830-gsapp-view-transition/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-TRANSITION-OBJECTS.json"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknViewAppUi.cpp" "$output/AknViewAppUi-830.cpp"
    cp "$stem_avkon_binary.map" "$output/avkon-view-transition-830.map"
    cp "$stem_avkon_binary.sym" "$output/avkon-view-transition-830.sym"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-lifetime-823-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-lifetime-observer.py" \
        --baseline "$project/Symbian/output/iteration-evidence/823-gsapp-lifetime-observer/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-LIFETIME-OBJECTS.json"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/htcleoclockwatch.inl" "$output/htcleoclockwatch-823.inl"
    cp "$stem_avkon_binary.map" "$output/stem_avkon-lifetime-823.map"
    cp "$stem_avkon_binary.sym" "$output/stem_avkon-lifetime-823.sym"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$stem_avkon_binary" >"$output/avkon-activation-820-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-activation-frontier.py" \
        --baseline "$project/Symbian/output/iteration-evidence/820-gsapp-activation-frontier/BASE-OBJECTS.json" \
        --native "$output" --report "$output/GSAPP-ACTIVATION-OBJECTS.json"
fi
sha256sum "$stem_avkon_obj" >"$output/stem-avkon-object-urel.sha256"
sha256sum "$stem_avkon_obj" \
    >"$output/stem-avkon-aknappui-homescreen-object-urel.sha256"
sha256sum "$stem_avkon_obj" \
    >"$output/stem-avkon-aknappui-homescreen-postcoe-object-urel.sha256"
sha256sum "$stem_avkon_aknenv_obj" \
    >"$output/stem-avkon-aknenv-object-urel.sha256"
sha256sum "$stem_avkon_aknenv_obj" \
    >"$output/stem-avkon-aknenv-homescreen-object-urel.sha256"
sha256sum "$stem_avkon_sgc_obj" \
    >"$output/stem-avkon-sgc-object-urel.sha256"
sha256sum "$stem_avkon_sgc_obj" \
    >"$output/stem-avkon-sgc-homescreen-object-urel.sha256"
sha256sum "$stem_avkon_sgc_obj" \
    >"$output/stem-avkon-aknsgc-homescreen-postcoe-object-urel.sha256"
sha256sum "$stem_avkon_sgc_obj" \
    >"$output/stem-avkon-aknsgc-homescreen-setparams-object-urel.sha256"

# Iteration 474 retains the 473 SetSystem bypass and wraps the same Avkon call
# only to record a synchronous leave before re-leaving with the original code.
if [ "$incremental_eiksrvui_resume" != 1 ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=h \
        --e32input="$eiksrvui_binary" >"$output/eiksrvui-stock-467-e32-dump.txt"
fi
test -s "$output/eiksrvui-stock-467-e32-dump.txt"
grep -q 'Secure ID: 100053d0' "$output/eiksrvui-stock-467-e32-dump.txt"
grep -q 'Vendor ID: 101fb657' "$output/eiksrvui-stock-467-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/eiksrvui-stock-467-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 100053d0' \
    "$output/eiksrvui-stock-467-e32-dump.txt"
sbs_clean -b "$eiksrvui_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$eiksrvui_binary"
then
    rm -f "$eiksrvui_binary"
fi
sbs_build_for "$eiksrvui_binary" -- \
    -b "$eiksrvui_bldinf" -c "$ssm_config" -j 4
test -s "$eiksrvui_binary"
test "$(find "$full_epocroot/epoc32/build/stem-eiksrvui-build" \
    -path '*/stem_eiksrvui_dll/armv5/urel/*' -iname 'eiksrvui.o' \
    -type f | wc -l)" -eq 1
eiksrvui_obj=$(find "$full_epocroot/epoc32/build/stem-eiksrvui-build" \
    -path '*/stem_eiksrvui_dll/armv5/urel/*' -iname 'eiksrvui.o' -type f)
test -s "$eiksrvui_obj"
eiksrvui_disasm="$output/eiksrvui-initialize-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$eiksrvui_obj" >"$eiksrvui_disasm"
grep -q 'HtcleoEikSrvUiLog' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$eiksrvui_disasm"
! grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*CNotifierDialogController.*NewL' "$eiksrvui_disasm"
! grep -q 'R_ARM_.*CALL.*CEikServNotifyServer.*NewL' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*AknsUtils.*InitSkinSupportL' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*CAknAppUiBase.*BaseConstructL' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*RWindowGroup.*Construct' "$eiksrvui_disasm"
grep -q 'R_ARM_.*CALL.*CEikKeySoundServer.*LaunchServer' "$eiksrvui_disasm"
strings "$eiksrvui_obj" | grep -Fq 'HTCLEO_EIKSRV '
strings -el "$eiksrvui_obj" | grep -Fq 'C:\Symbian3\EIKSRV.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$eiksrvui_disasm"
! grep -q 'R_ARM_.*CALL.*StartC32' "$eiksrvui_disasm"
! grep -q 'R_ARM_.*CALL.*CEikServNotifyAlert.*ConstructL' "$eiksrvui_disasm"
! grep -q 'R_ARM_.*CALL.*CEikonEnv.*SetSystem' "$eiksrvui_disasm"
grep -q '42415345' "$eiksrvui_disasm"
grep -qi '4e465953' "$eiksrvui_disasm"
grep -qi '4558544b' "$eiksrvui_disasm"
grep -qi '4b534e44' "$eiksrvui_disasm"
grep -qi '43555253' "$eiksrvui_disasm"
for eiksrvui_entry_word in 0000e7f0 0000e7f1 0000e7f2 0000e7f3 0000e7f4
do
    grep -q "$eiksrvui_entry_word" "$eiksrvui_disasm"
done
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$eiksrvui_binary" >"$output/eiksrvui-e32-dump.txt"
grep -q 'Secure ID: 100053d0' "$output/eiksrvui-e32-dump.txt"
grep -q 'Vendor ID: 101fb657' "$output/eiksrvui-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' "$output/eiksrvui-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 100053d0' \
    "$output/eiksrvui-e32-dump.txt"
test "$(sed -n 's/^Export Description: Size=//p' \
    "$output/eiksrvui-e32-dump.txt")" = \
    "$(sed -n 's/^Export Description: Size=//p' \
    "$output/eiksrvui-stock-467-e32-dump.txt")"
sha256sum "$eiksrvui_binary" >"$output/eiksrvui-urel.sha256"
sha256sum "$eiksrvui_obj" >"$output/eiksrvui-object-urel.sha256"

# Iteration 469 traces both sides of the existing synchronous StartC32
# protocol.  The two outputs are a coupled build unit; no CMI, module, wait,
# property, error, or scheduler policy is changed.
sbs_clean -b "$c32_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    { incremental_wants_binary "$c32root_binary" || \
      incremental_wants_binary "$c32start_binary"; }
then
    rm -f "$c32root_binary" "$c32start_binary"
fi
sbs_build_for "$c32root_binary" "$c32start_binary" -- \
    -b "$c32_bldinf" -c "$ssm_config" -j 4
test -s "$c32root_binary"
test -s "$c32start_binary"
test "$(find "$full_epocroot/epoc32/build/c32-startup-build" \
    -path '*/c32root_dll/armv5/urel/c32root.o' -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/c32-startup-build" \
    -path '*/c32start_exe/armv5/urel/c32start.o' -type f | wc -l)" -eq 1
c32root_obj=$(find "$full_epocroot/epoc32/build/c32-startup-build" \
    -path '*/c32root_dll/armv5/urel/c32root.o' -type f)
c32start_obj=$(find "$full_epocroot/epoc32/build/c32-startup-build" \
    -path '*/c32start_exe/armv5/urel/c32start.o' -type f)
c32root_generated_def=$(find "$full_epocroot/epoc32/build/c32-startup-build" \
    -path '*/c32root_dll/armv5/urel/c32root*.def' -type f)
test -s "$c32root_obj"
test -s "$c32start_obj"
test -s "$c32root_generated_def"
c32root_disasm="$output/c32root-startc32-durable-log-urel.disasm"
c32start_disasm="$output/c32start-configurator-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$c32root_obj" >"$c32root_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$c32start_obj" >"$c32start_disasm"
grep -q 'HtcleoC32RootLog' "$c32root_disasm"
grep -q 'HtcleoC32StartLog' "$c32start_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$c32root_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$c32root_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$c32start_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$c32start_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Create' "$c32root_disasm"
grep -q 'R_ARM_.*CALL.*User.*WaitForRequest' "$c32root_disasm"
grep -q 'R_ARM_.*CALL.*RRootServ.*LoadCpm' "$c32start_disasm"
strings "$c32root_obj" | grep -Fq 'HTCLEO_C32ROOT '
strings -el "$c32root_obj" | grep -Fq 'C:\Symbian3\C32ROOT.TXT'
strings "$c32start_obj" | grep -Fq 'HTCLEO_C32START '
strings -el "$c32start_obj" | grep -Fq 'C:\Symbian3\C32START.TXT'
tr -d '\r' <"$c32_component/eabi/c32rootU.def" | \
    sed 's/[[:space:]]*;.*$//;s/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/c32root-frozen-exports.def"
tr -d '\r' <"$c32root_generated_def" | \
    sed 's/[[:space:]]*;.*$//;s/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/c32root-generated-exports.def"
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/c32root-frozen-exports.def" | wc -l)" -eq 44
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/c32root-generated-exports.def" | wc -l)" -eq 44
diff -u "$output/c32root-frozen-exports.def" \
    "$output/c32root-generated-exports.def"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$c32root_binary" >"$output/c32root-e32-dump.txt"
"$native_epocroot/epoc32/tools/elf2e32" --dump=h \
    --e32input="$c32start_binary" >"$output/c32start-e32-dump.txt"
grep -q 'Secure ID: 101f7484' "$output/c32root-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/c32root-e32-dump.txt"
grep -q 'Secure ID: 101f7988' "$output/c32start-e32-dump.txt"
grep -q 'Vendor ID: 70000001' "$output/c32start-e32-dump.txt"
sha256sum "$c32root_binary" >"$output/c32root-urel.sha256"
sha256sum "$c32start_binary" >"$output/c32start-urel.sha256"
sha256sum "$c32root_obj" >"$output/c32root-object-urel.sha256"
sha256sum "$c32start_obj" >"$output/c32start-object-urel.sha256"

# Iteration 458 proves InitSkinSupportL does not return or leave.  Trace the
# shared AknSkinSrv client/server DLL so one boot identifies whether the client
# blocks in CreateSession, process rendezvous, server construction, or the
# notification IPC.  No startup policy or timeout is changed.
if [ "$incremental_aknskinsrv_resume" != 1 ]; then
    "$native_epocroot/epoc32/tools/elf2e32" --dump=h \
        --e32input="$aknskinsrv_binary" \
        >"$output/aknskinsrv-stock-458-e32-dump.txt"
fi
test -s "$output/aknskinsrv-stock-458-e32-dump.txt"
grep -q 'Secure ID: 10005a35' "$output/aknskinsrv-stock-458-e32-dump.txt"
grep -q 'Vendor ID: 101fb657' "$output/aknskinsrv-stock-458-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/aknskinsrv-stock-458-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 10005a35' \
    "$output/aknskinsrv-stock-458-e32-dump.txt"
sbs_clean -b "$aknskinsrv_bldinf" -c "$ssm_config"
if [ "$build_mode" = incremental ] && \
    incremental_wants_binary "$aknskinsrv_binary"
then
    rm -f "$aknskinsrv_binary"
fi
sbs_build_for "$aknskinsrv_binary" -- \
    -b "$aknskinsrv_bldinf" -c "$ssm_config" -j 4
test -s "$aknskinsrv_binary"
aknskinsrv_generated_def=$(find "$full_epocroot/epoc32/build/aknskinsrv-build" \
    -path '*/aknskinsrv_dll/armv5/urel/AKNSKINSRV*.def' -type f | head -n 1)
test -n "$aknskinsrv_generated_def" && test -s "$aknskinsrv_generated_def"
tr -d '\r' <"$aknskinsrv_frozen_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/aknskinsrv-frozen-exports.def"
tr -d '\r' <"$aknskinsrv_generated_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/aknskinsrv-generated-exports.def"
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/aknskinsrv-frozen-exports.def" | wc -l)" -eq 199
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/aknskinsrv-generated-exports.def" | wc -l)" -eq 199
diff -u "$output/aknskinsrv-frozen-exports.def" \
    "$output/aknskinsrv-generated-exports.def"
test "$(find "$full_epocroot/epoc32/build/aknskinsrv-build" \
    -path '*/aknskinsrv_dll/armv5/urel/*' -iname 'aknssrvclient.o' \
    -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/aknskinsrv-build" \
    -path '*/aknskinsrv_dll/armv5/urel/*' -iname 'aknssrv.o' \
    -type f | wc -l)" -eq 1
aknskinsrv_client_obj=$(find "$full_epocroot/epoc32/build/aknskinsrv-build" \
    -path '*/aknskinsrv_dll/armv5/urel/*' -iname 'aknssrvclient.o' -type f)
aknskinsrv_core_obj=$(find "$full_epocroot/epoc32/build/aknskinsrv-build" \
    -path '*/aknskinsrv_dll/armv5/urel/*' -iname 'aknssrv.o' -type f)
test -s "$aknskinsrv_client_obj"
test -s "$aknskinsrv_core_obj"
aknskinsrv_client_disasm="$output/aknskinsrv-client-durable-log-urel.disasm"
aknskinsrv_core_disasm="$output/aknskinsrv-core-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$aknskinsrv_client_obj" >"$aknskinsrv_client_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$aknskinsrv_core_obj" >"$aknskinsrv_core_disasm"
grep -q 'HtcleoAknSkinLog' "$aknskinsrv_client_disasm"
grep -q 'HtcleoAknSkinLog' "$aknskinsrv_core_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$aknskinsrv_core_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$aknskinsrv_core_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*Rendezvous' "$aknskinsrv_core_disasm"
grep -q 'R_ARM_.*CALL.*User.*WaitForRequest' "$aknskinsrv_core_disasm"
strings "$aknskinsrv_core_obj" | grep -Fq 'HTCLEO_SKIN '
strings -el "$aknskinsrv_core_obj" | grep -Fq 'C:\Symbian3\SKINLOG.TXT'
! grep -q 'e7f000f0\|c6400000\|HalFunction\|User5After' \
    "$aknskinsrv_client_disasm" "$aknskinsrv_core_disasm"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$aknskinsrv_binary" >"$output/aknskinsrv-e32-dump.txt"
grep -q 'Secure ID: 10005a35' "$output/aknskinsrv-e32-dump.txt"
grep -q 'Vendor ID: 101fb657' "$output/aknskinsrv-e32-dump.txt"
grep -q 'Capabilities: 00000000 000ffffe' \
    "$output/aknskinsrv-e32-dump.txt"
grep -q 'Uids:.*10000079 1000008d 10005a35' \
    "$output/aknskinsrv-e32-dump.txt"
grep -q 'Number of exports = 199' "$output/aknskinsrv-e32-dump.txt"
test "$(sed -n 's/^Export Description: Size=//p' \
    "$output/aknskinsrv-e32-dump.txt")" = \
    "$(sed -n 's/^Export Description: Size=//p' \
    "$output/aknskinsrv-stock-458-e32-dump.txt")"
sha256sum "$aknskinsrv_binary" >"$output/aknskinsrv-urel.sha256"
sha256sum "$aknskinsrv_client_obj" \
    >"$output/aknskinsrv-client-object-urel.sha256"
sha256sum "$aknskinsrv_core_obj" \
    >"$output/aknskinsrv-core-object-urel.sha256"

# Rebuild the exact custom-command plug-in only after its AknCapServer client
# dependency is current. The logger is fail-open and preserves both palette
# and StartAknCapserverL result semantics.
sbs_clean -b "$akn_custom_bldinf" -c "$ssm_config"
sbs_build_for "$akn_custom_binary" -- \
    -b "$akn_custom_bldinf" -c "$ssm_config" -j 4
test -s "$akn_custom_binary"
test "$(find "$full_epocroot/epoc32/build/akncustcmds" \
    -path '*/akncustcmds_dll/armv5/urel/akncapserverstart.o' -type f | wc -l)" -eq 1
akn_custom_obj=$(find "$full_epocroot/epoc32/build/akncustcmds" \
    -path '*/akncustcmds_dll/armv5/urel/akncapserverstart.o' -type f)
test -s "$akn_custom_obj"
akn_custom_disasm="$output/akncapserver-custom-command-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$akn_custom_obj" >"$akn_custom_disasm"
grep -q 'HtcleoAknCustomLog' "$akn_custom_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Write' "$akn_custom_disasm"
grep -q 'R_ARM_.*CALL.*RFile.*Flush' "$akn_custom_disasm"
grep -q 'R_ARM_.*CALL.*StartAknCapserverL' "$akn_custom_disasm"
strings "$akn_custom_obj" | grep -Fq 'HTCLEO_CUST '
strings -el "$akn_custom_obj" | grep -Fq 'C:\Symbian3\CUSTLOG.TXT'
! grep -q 'e7f000f0\|c6400000' "$akn_custom_disasm"
sha256sum "$akn_custom_binary" >"$output/akncustcmds-urel.sha256"
sha256sum "$akn_custom_obj" \
    >"$output/akncustcmds-start-object-urel.sha256"

# Rebuild only the NGA Window Server used as sys\bin\ewsrv.exe.  The isolated
# unit avoids unrelated tests/switch binaries; CLEAN keeps the target macro and
# the complete object set coherent.
if [ "$incremental_resource_policy" = gate17-wserv-find-notfound ]; then
    # Critical-service change: independent exact742 reconstruction BEFORE the
    # one-source edit. This CLEAN is scoped to the isolated wserv-only bld.inf.
    test "$wserv_build_bldinf" = "$project/Symbian/hd2/qsd8250-native-bsp/wserv-nga-build/bld.inf"
    "$SBS_HOME/bin/sbs" -b "$wserv_build_bldinf" -c "$ssm_config" CLEAN
fi
sbs_clean -b "$wserv_build_bldinf" -c "$ssm_config"
sbs_build_for "$wserv_binary" -- \
    -b "$wserv_build_bldinf" -c "$ssm_config" -j 4
test -s "$wserv_binary"
wserv_main_obj=$(find "$full_epocroot/epoc32/build/wserv-nga-build" \
    -path '*/wserv_nga_exe/armv5/urel/*' -iname 'wstop.o' -type f | head -n 1)
wserv_plugin_obj=$(find "$full_epocroot/epoc32/build/wserv-nga-build" \
    -path '*/wserv_nga_exe/armv5/urel/*' -iname 'wspluginmanager.o' -type f | head -n 1)
wserv_screen_obj=$(find "$full_epocroot/epoc32/build/wserv-nga-build" \
    -path '*/wserv_nga_exe/armv5/urel/*' -iname 'screen.o' -type f | head -n 1)
wserv_redraw_obj=$(find "$full_epocroot/epoc32/build/wserv-nga-build" \
    -path '*/wserv_nga_exe/armv5/urel/*' -iname 'screenredraw.o' -type f | head -n 1)
wserv_render_manager_obj=$(find "$full_epocroot/epoc32/build/wserv-nga-build" \
    -path '*/wserv_nga_exe/armv5/urel/*' -iname 'renderstagemanager.o' -type f | head -n 1)
test -n "$wserv_main_obj" && test -s "$wserv_main_obj"
test -n "$wserv_plugin_obj" && test -s "$wserv_plugin_obj"
test -n "$wserv_screen_obj" && test -s "$wserv_screen_obj"
test -n "$wserv_redraw_obj" && test -s "$wserv_redraw_obj"
test -n "$wserv_render_manager_obj" && test -s "$wserv_render_manager_obj"
wserv_disasm="$output/wserv-nga-durable-log-urel.disasm"
wserv_plugin_disasm="$output/wserv-nga-plugin-manager-progress-urel.disasm"
wserv_screen_disasm="$output/wserv-nga-screen-construct-progress-urel.disasm"
wserv_redraw_disasm="$output/wserv-nga-screen-redraw-progress-urel.disasm"
wserv_render_manager_disasm="$output/wserv-nga-render-stage-manager-progress-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wserv_main_obj" >"$wserv_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wserv_plugin_obj" >"$wserv_plugin_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wserv_screen_obj" >"$wserv_screen_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wserv_redraw_obj" >"$wserv_redraw_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wserv_render_manager_obj" >"$wserv_render_manager_disasm"
grep -q 'HtcleoWsLog' "$wserv_disasm"
# There are 38 source events. GCCE tail-duplicates the post-debug-path 0x4B
# reporter into both branches, so the UREL object deliberately contains 39
# physical call relocations while each runtime path still emits 0x4B once.
test "$(grep -c 'R_ARM_.*CALL.*HtcleoWsLog' "$wserv_plugin_disasm")" -eq 39
test "$(grep -c 'R_ARM_.*CALL.*HtcleoWsLog' "$wserv_screen_disasm")" -ge 21
test "$(grep -c 'R_ARM_.*CALL.*HtcleoWsLog' "$wserv_redraw_disasm")" -ge 11
test "$(grep -c 'R_ARM_.*CALL.*HtcleoWsLog' "$wserv_render_manager_disasm")" -ge 17
grep -q 'R_ARM_ARM_CALL[[:space:]]*_ZN5RFile5WriteERK6TDesC8\|R_ARM_THM_CALL[[:space:]]*_ZN5RFile5WriteERK6TDesC8' \
    "$wserv_disasm"
grep -q 'R_ARM_ARM_CALL[[:space:]]*_ZN5RFile5FlushEv\|R_ARM_THM_CALL[[:space:]]*_ZN5RFile5FlushEv' \
    "$wserv_disasm"
strings "$wserv_main_obj" | grep -q 'HTCLEO_WS '
strings -el "$wserv_main_obj" | grep -Fq 'C:\Symbian3\WSLOG.TXT'
# 747 is a strict component rollback control, not a new writer implementation.
# Recompile and permit only build-time/header-CRC differences, then reuse the
# original742 artifact so the final comparison is genuinely byte-for-byte.
wserv_742_control="$project/Symbian/output/742-symbian3-full-matrix-unowned-kick-retired-incremental/Symbian3/build/incremental-release-cache/wserv_nga.exe"
test "$(sha256sum "$wserv_742_control" | awk '{print $1}')" = \
    b8a2fb688e3a920923330d12819a1e8b048bca52cbfe2142721ab446889c421b
python3 "$wserv_worker_retirement_transform" "$full_epocroot" \
    --pin-binary "$wserv_binary" "$wserv_742_control"
cmp -s "$wserv_binary" "$wserv_742_control"
printf 'HTCLEO_WSERV_742_BINARY_CONTROL=byte-identical\n'
if [ "$incremental_resource_policy" = gate17-wserv-find-notfound ]; then
    wserv_find_base="$output/wserv-find-notfound-base-802.json"
    python3 "$wserv_find_notfound" "$full_epocroot" --record-base "$wserv_find_base"
    python3 "$wserv_find_notfound" "$full_epocroot"
    sbs_build_for "$wserv_binary" -- -b "$wserv_build_bldinf" -c "$ssm_config" -j 4
    python3 "$wserv_find_notfound" "$full_epocroot" --verify-derived "$wserv_find_base" \
        --report "$output/WSERV-FIND-NOTFOUND-OBJECTS.json"
    wserv_control_policy=derived742-matrix-final-find-notfound
    wserv_find_policy=matrix-final-name-query-native-notfound-no-new-log
fi
if [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    # Binary is restored from801. Replace stale802 debugging metadata only with
    # the independently reconstructed742 symbols pinned by its base certificate.
    python3 "$menu_task_enumeration" "$full_epocroot" --restore-wserv-symbols "$output"
fi
sha256sum "$wserv_binary" >"$output/wserv-nga-urel.sha256"
sha256sum "$wserv_main_obj" >"$output/wserv-nga-wstop-urel.sha256"
sha256sum "$wserv_plugin_obj" >"$output/wserv-nga-plugin-manager-urel.sha256"
sha256sum "$wserv_screen_obj" >"$output/wserv-nga-screen-urel.sha256"
sha256sum "$wserv_redraw_obj" >"$output/wserv-nga-screen-redraw-urel.sha256"
sha256sum "$wserv_render_manager_obj" >"$output/wserv-nga-render-stage-manager-urel.sha256"

# Rebuild the standard OpenWFC engine selected by the ROM.  Iteration 429
# proved that the HTCLEO display channel correctly reports RGB565, while the
# standard target omitted its existing SUPPORT_565_OUTPUT path and therefore
# left with KErrNotSupported.  Enable that upstream conversion/output path.
sbs_clean -b "$wfc_bldinf" -c "$ssm_config"
sbs_build_for "$wfc_binary" -- \
    -b "$wfc_bldinf" -c "$ssm_config" -j 4
test -s "$wfc_binary"
wfc_logger_obj=$(find "$full_epocroot/epoc32/build/openwfc-build" \
    -path '*/libwfc_dll/armv5/urel/*' -iname 'htcleowfclog.o' -type f | head -n 1)
wfc_context_obj=$(find "$full_epocroot/epoc32/build/openwfc-build" \
    -path '*/libwfc_dll/armv5/urel/*' -iname 'wfccontext.o' -type f | head -n 1)
wfc_display_context_obj=$(find "$full_epocroot/epoc32/build/openwfc-build" \
    -path '*/libwfc_dll/armv5/urel/*' -iname 'owfdisplaycontext.o' -type f | head -n 1)
wfc_screen_obj=$(find "$full_epocroot/epoc32/build/openwfc-build" \
    -path '*/libwfc_dll/armv5/urel/*' -iname 'owfscreen_displaychannel.o' -type f | head -n 1)
wfc_stream_obj=$(find "$full_epocroot/epoc32/build/openwfc-build" \
    -path '*/libwfc_dll/armv5/urel/*' -iname 'owfnativestreamstub.o' -type f | head -n 1)
for wfc_obj in "$wfc_logger_obj" "$wfc_context_obj" \
    "$wfc_display_context_obj" "$wfc_screen_obj" "$wfc_stream_obj"
do
    test -n "$wfc_obj" && test -s "$wfc_obj"
done
wfc_logger_disasm="$output/openwfc-context-logger-urel.disasm"
wfc_context_disasm="$output/openwfc-context-progress-urel.disasm"
wfc_display_context_disasm="$output/openwfc-display-context-progress-urel.disasm"
wfc_screen_disasm="$output/openwfc-screen-display-channel-progress-urel.disasm"
wfc_stream_disasm="$output/openwfc-native-stream-progress-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wfc_logger_obj" >"$wfc_logger_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wfc_context_obj" >"$wfc_context_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wfc_display_context_obj" >"$wfc_display_context_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wfc_screen_obj" >"$wfc_screen_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$wfc_stream_obj" >"$wfc_stream_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoWfcLog' "$wfc_context_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoWfcLog' "$wfc_display_context_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoWfcLog' "$wfc_screen_disasm"
grep -qi '00000565' "$wfc_screen_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoWfcLog' "$wfc_stream_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$wfc_logger_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$wfc_logger_disasm"
strings "$wfc_logger_obj" | grep -q 'HTCLEO_WFC '
strings -el "$wfc_logger_obj" | grep -Fq 'C:\Symbian3\WFCLOG.TXT'
sha256sum "$wfc_binary" >"$output/openwfc-engine-urel.sha256"
sha256sum "$wfc_logger_obj" >"$output/openwfc-context-logger-urel.sha256"
sha256sum "$wfc_context_obj" >"$output/openwfc-context-progress-urel.sha256"
sha256sum "$wfc_display_context_obj" >"$output/openwfc-display-context-progress-urel.sha256"
sha256sum "$wfc_screen_obj" >"$output/openwfc-screen-display-channel-progress-urel.sha256"
sha256sum "$wfc_stream_obj" >"$output/openwfc-native-stream-progress-urel.sha256"

# Rebuild the exact standard display/flicker render-stage plug-in referenced by
# WSINI.  It is the sole DSPRLOG writer and preserves all existing leave/error
# semantics while tracing EGL, OpenWFC, SG and DirectGDI construction.
ln -sfn libWFC.dso \
    "$full_epocroot/epoc32/release/armv5/lib/libwfc.dso"
sbs_clean -b "$display_bldinf" -c "$ssm_config"
sbs_build_for "$display_binary" -- \
    -b "$display_bldinf" -c "$ssm_config" -j 4
test -s "$display_binary"
test -s "$display_resource"
display_plugin_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'stdplugin.o' -type f | head -n 1)
display_factory_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'displayrenderstagefactory.o' -type f | head -n 1)
display_stage_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'displayrenderstage.o' -type f | head -n 1)
display_openwfc_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'openwfcwrapper.o' -type f | head -n 1)
display_target_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'rendertarget.o' -type f | head -n 1)
display_policy_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'displaypolicy.o' -type f | head -n 1)
display_fb_factory_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'fbrenderstagefactory.o' -type f | head -n 1)
display_fb_stage_obj=$(find "$full_epocroot/epoc32/build/openwfc" \
    -path '*/10286378_dll/armv5/urel/*' -iname 'fbrenderstage.o' -type f | head -n 1)
for display_obj in "$display_plugin_obj" "$display_factory_obj" \
    "$display_stage_obj" "$display_openwfc_obj" "$display_target_obj" \
    "$display_policy_obj" "$display_fb_factory_obj" "$display_fb_stage_obj"
do
    test -n "$display_obj" && test -s "$display_obj"
done
display_plugin_disasm="$output/display-render-stage-logger-urel.disasm"
display_factory_disasm="$output/display-render-stage-factory-urel.disasm"
display_stage_disasm="$output/display-render-stage-construct-urel.disasm"
display_openwfc_disasm="$output/display-openwfc-wrapper-urel.disasm"
display_target_disasm="$output/display-render-target-urel.disasm"
display_policy_disasm="$output/display-policy-urel.disasm"
display_fb_factory_disasm="$output/flicker-render-stage-factory-urel.disasm"
display_fb_stage_disasm="$output/flicker-render-stage-construct-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_plugin_obj" >"$display_plugin_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_factory_obj" >"$display_factory_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_stage_obj" >"$display_stage_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_openwfc_obj" >"$display_openwfc_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_target_obj" >"$display_target_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_policy_obj" >"$display_policy_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_fb_factory_obj" >"$display_fb_factory_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$display_fb_stage_obj" >"$display_fb_stage_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_factory_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_stage_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_openwfc_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_target_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_policy_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_fb_factory_disasm"
grep -q 'R_ARM_.*CALL.*HtcleoDsprLog' "$display_fb_stage_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$display_plugin_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$display_plugin_disasm"
strings "$display_plugin_obj" | grep -q 'HTCLEO_DSP '
strings -el "$display_plugin_obj" | grep -Fq 'C:\Symbian3\DSPRLOG.TXT'
sha256sum "$display_binary" >"$output/display-render-stage-urel.sha256"
sha256sum "$display_resource" >"$output/display-render-stage-resource.sha256"
sha256sum "$display_plugin_obj" >"$output/display-render-stage-logger-urel.sha256"
sha256sum "$display_factory_obj" >"$output/display-render-stage-factory-urel.sha256"
sha256sum "$display_stage_obj" >"$output/display-render-stage-construct-urel.sha256"
sha256sum "$display_openwfc_obj" >"$output/display-openwfc-wrapper-urel.sha256"
sha256sum "$display_target_obj" >"$output/display-render-target-urel.sha256"
sha256sum "$display_policy_obj" >"$output/display-policy-urel.sha256"
sha256sum "$display_fb_factory_obj" >"$output/flicker-render-stage-factory-urel.sha256"
sha256sum "$display_fb_stage_obj" >"$output/flicker-render-stage-construct-urel.sha256"

# Rebuild the exact ECom implementation selected by WSINI.  The stock Syborg
# stem omitted its registration resource; this build also supplies a separate
# fail-open NVGLOG so ECom load, factory construction and render-stage creation
# can be distinguished without framebuffer probes.
# The PDK was authored for a case-insensitive Windows host.  Its GCCE import
# libraries exist with different case from the MMP spellings, so provide only
# case-compatibility symlinks; the linked exports remain the original PDK DSOs.
ln -sfn NVGDecoder_SW.dso \
    "$full_epocroot/epoc32/release/armv5/lib/nvgdecoder_sw.dso"
ln -sfn libopenvg_sw.dso \
    "$full_epocroot/epoc32/release/armv5/lib/libOpenVG_sw.dso"
ln -sfn libvgi.dso \
    "$full_epocroot/epoc32/release/armv5/lib/libVGI.dso"
sbs_clean -b "$nvg_bldinf" -c "$ssm_config"
sbs_build_for "$nvg_binary" -- \
    -b "$nvg_bldinf" -c "$ssm_config" -j 4
test -s "$nvg_binary"
test -s "$nvg_resource"
nvg_plugin_obj=$(find "$full_epocroot/epoc32/build/nvgrenderstage" \
    -path '*/nvgrenderstage_dll/armv5/urel/*' -iname 'nvgrenderstageplugin.o' \
    -type f | head -n 1)
nvg_factory_obj=$(find "$full_epocroot/epoc32/build/nvgrenderstage" \
    -path '*/nvgrenderstage_dll/armv5/urel/*' -iname 'nvgrenderstagefactory.o' \
    -type f | head -n 1)
nvg_stage_obj=$(find "$full_epocroot/epoc32/build/nvgrenderstage" \
    -path '*/nvgrenderstage_dll/armv5/urel/*' -iname 'nvgrenderstage.o' \
    -type f | head -n 1)
test -n "$nvg_plugin_obj" && test -s "$nvg_plugin_obj"
test -n "$nvg_factory_obj" && test -s "$nvg_factory_obj"
test -n "$nvg_stage_obj" && test -s "$nvg_stage_obj"
nvg_plugin_disasm="$output/nvgrenderstage-plugin-durable-log-urel.disasm"
nvg_factory_disasm="$output/nvgrenderstage-factory-durable-log-urel.disasm"
nvg_stage_disasm="$output/nvgrenderstage-construction-durable-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$nvg_plugin_obj" >"$nvg_plugin_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$nvg_factory_obj" >"$nvg_factory_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$nvg_stage_obj" >"$nvg_stage_disasm"
grep -q 'HtcleoNvgLog' "$nvg_plugin_disasm"
grep -q 'HtcleoNvgLog' "$nvg_factory_disasm"
grep -q 'HtcleoNvgLog' "$nvg_stage_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$nvg_plugin_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$nvg_plugin_disasm"
strings "$nvg_plugin_obj" | grep -q 'HTCLEO_NVG '
strings -el "$nvg_plugin_obj" | grep -Fq 'C:\Symbian3\NVGLOG.TXT'
sha256sum "$nvg_binary" >"$output/nvgrenderstage-urel.sha256"
sha256sum "$nvg_resource" >"$output/nvgrenderstage-resource.sha256"

# Rebuild the ROM-selected ECom server with a dedicated fail-open durable log.
# The trace is interface-gated after request unpacking and keeps the stock
# server completion, RunError, resolver, capability and overflow behaviour.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    test "$(sha256sum "$ecom_server_binary" | awk '{print $1}')" = ecf17482719c2258b2c07a708bfb7560c2231bf528ee09e7b3cbb041de737e90
    python3 "$ecom_server_exception" "$full_epocroot"
    python3 "$home_external_empty" "$full_epocroot"
    python3 "$ecom_font_registry" "$full_epocroot"
    python3 "$ecom_font_getinfo" "$full_epocroot"
    ecom_font_getinfo_policy=FreeType-only-native-Connect-GetInfo-Close-once-RAM-path-fingerprint-no-loader-or-security-policy-change
    ecom_font_registry_policy=FreeType-only-RAM28-registration-index-security-snapshot-in-existing-ECX2-no-new-file-writes
    ecom_server_exception_policy=ECom-main-terminal-ECX2-init-plus-fault-1m-RAM-request10-font7-no-normal-filelog-preserve-panic
    home_external_empty_policy=on859-only-optional-Home-external200286df-and-original-FeatMgr-empty-no-global-change
    #864 is resource-only. Keep the exact863 executable; do not force a relink.
fi
sbs_clean -b "$ecom_server_build_bldinf" -c "$ssm_config"
sbs_build_for "$ecom_server_binary" -- \
    -b "$ecom_server_build_bldinf" -c "$ssm_config" -j 4
test -s "$ecom_server_binary"
ecom_server_logger_obj=$(find "$full_epocroot/epoc32/build/ecom-server-build" \
    -path '*/ecomserver_exe/armv5/urel/*' \
    -iname 'HtcleoEcomServerLog.o' -type f | head -n 1)
ecom_server_session_obj=$(find "$full_epocroot/epoc32/build/ecom-server-build" \
    -path '*/ecomserver_exe/armv5/urel/*' \
    -iname 'EComServerSession.o' -type f | head -n 1)
ecom_server_core_obj=$(find "$full_epocroot/epoc32/build/ecom-server-build" \
    -path '*/ecomserver_exe/armv5/urel/*' \
    -iname 'EComServer.o' -type f | head -n 1)
ecom_server_registry_obj=$(find "$full_epocroot/epoc32/build/ecom-server-build" \
    -path '*/ecomserver_exe/armv5/urel/*' \
    -iname 'RegistryData.o' -type f | head -n 1)
test -n "$ecom_server_logger_obj" && test -s "$ecom_server_logger_obj"
test -n "$ecom_server_session_obj" && test -s "$ecom_server_session_obj"
test -n "$ecom_server_core_obj" && test -s "$ecom_server_core_obj"
test -n "$ecom_server_registry_obj" && test -s "$ecom_server_registry_obj"
ecom_server_logger_disasm="$output/ecom-server-logger-urel.disasm"
ecom_server_session_disasm="$output/ecom-server-session-list-trace-urel.disasm"
ecom_server_core_disasm="$output/ecom-server-core-list-trace-urel.disasm"
ecom_server_registry_disasm="$output/ecom-server-registry-list-trace-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ecom_server_logger_obj" >"$ecom_server_logger_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ecom_server_session_obj" >"$ecom_server_session_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ecom_server_core_obj" >"$ecom_server_core_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ecom_server_registry_obj" >"$ecom_server_registry_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$ecom_server_logger_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$ecom_server_logger_disasm"
grep -q 'HtcleoEcomServerLog' "$ecom_server_session_disasm"
grep -q 'HtcleoEcomServerLog' "$ecom_server_core_disasm"
test "$(grep -c 'HtcleoEcomServerLog' "$ecom_server_session_disasm")" -ge 35
test "$(grep -c 'HtcleoEcomServerLog' "$ecom_server_core_disasm")" -ge 25
test "$(grep -c 'HtcleoEcomServerLog' "$ecom_server_registry_disasm")" -ge 43
for ecom_hsps_stage in 540 541 542 543 544 545 546
do
    grep -qi "0000f${ecom_hsps_stage}" "$ecom_server_core_disasm"
done
grep -qi '200159c7' "$ecom_server_session_disasm"
grep -qi '200159c8' "$ecom_server_core_disasm"
grep -q 'HtcleoEcomHspsLog' "$ecom_server_logger_disasm"
# GCCE materializes F600 as `movs #0xf6; lsls #8`, while F601/F602 remain
# literal-pool words.  Accept that exact equivalent encoding instead of
# requiring a literal 0x0000F600 word that need not exist in the object.
grep -qi 'movs[[:space:]].*#246.*0xf6' "$ecom_server_session_disasm"
grep -qi 'lsls[[:space:]].*#8' "$ecom_server_session_disasm"
grep -qi '0000f601' "$ecom_server_session_disasm"
grep -qi '0000f602' "$ecom_server_session_disasm"
grep -qi '0000f610' "$ecom_server_core_disasm"
grep -qi '0000f620' "$ecom_server_registry_disasm"
test "$(grep -c 'HtcleoEcomHspsLog' \
    "$ecom_server_session_disasm")" -ge 35
test "$(grep -c 'HtcleoEcomHspsLog' \
    "$ecom_server_core_disasm")" -ge 20
grep -qi '0000f60f' "$ecom_server_session_disasm"
grep -qi '0000f617' "$ecom_server_core_disasm"
grep -qi '0000f631' "$ecom_server_session_disasm"
grep -qi '0000f640' "$ecom_server_core_disasm"
strings -el "$ecom_server_logger_obj" | grep -Fq 'C:\Symbian3\HSPSECOM.TXT'
strings "$ecom_server_logger_obj" | grep -q 'HTCLEO_ESRV '
strings -el "$ecom_server_logger_obj" | grep -Fq 'C:\Symbian3\ECOMSRV.TXT'
sha256sum "$ecom_server_binary" >"$output/ecom-server-urel.sha256"
sha256sum "$ecom_server_logger_obj" >"$output/ecom-server-logger-urel.sha256"
sha256sum "$ecom_server_session_obj" >"$output/ecom-server-session-urel.sha256"
sha256sum "$ecom_server_core_obj" >"$output/ecom-server-core-urel.sha256"
sha256sum "$ecom_server_registry_obj" >"$output/ecom-server-registry-urel.sha256"
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    for retained_ec859 in ECOM-EXCEPTION-OBJECTS.json ecomserver-exception-859-full-dump.txt ecomserver-exception-859.map ecomserver-exception-859.sym EComServerStart-859.cpp EComServerSession-859.cpp; do
        cp "$incremental_parent_root/build/$retained_ec859" "$output/$retained_ec859"
    done
    cp "$incremental_parent_root/build/ECOM-EXCEPTION-PARENT-859-ROM.json" "$output/ECOM-EXCEPTION-PARENT-859-ROM.json"
    cp "$incremental_parent_root/build/ECOM-EXCEPTION-PARENT-859-CANONICAL.json" "$output/ECOM-EXCEPTION-PARENT-859-CANONICAL.json"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$ecom_server_binary" >"$output/ecomserver-font-getinfo-863-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-ecom-font-getinfo.py" \
        --native "$output" --report "$output/ECOM-FONT-GETINFO-OBJECTS.json"
    cp "$ecom_server_binary.map" "$output/ecomserver-font-getinfo-863.map"
    cp "$ecom_server_binary.sym" "$output/ecomserver-font-getinfo-863.sym"
    cp "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp" "$output/RegistryData-863.cpp"
    cp "$incremental_parent_root/build/ECOM-FONT-GETINFO-PARENT-863-ROM.json" "$output/ECOM-FONT-GETINFO-PARENT-863-ROM.json"
    cp "$incremental_parent_root/build/ECOM-FONT-GETINFO-PARENT-863-CANONICAL.json" "$output/ECOM-FONT-GETINFO-PARENT-863-CANONICAL.json"
    for retained_font862 in ECOM-FONT-REGISTRY-OBJECTS.json RegistryData-862.cpp ecomserver-font-registry-862-full-dump.txt ecomserver-font-registry-862.map ecomserver-font-registry-862.sym; do
        cp "$incremental_parent_root/build/$retained_font862" "$output/$retained_font862"
    done
    cp "$incremental_parent_root/build/ECOM-FONT-REGISTRY-PARENT-862-ROM.json" "$output/ECOM-FONT-REGISTRY-PARENT-862-ROM.json"
    cp "$incremental_parent_root/build/ECOM-FONT-REGISTRY-PARENT-862-CANONICAL.json" "$output/ECOM-FONT-REGISTRY-PARENT-862-CANONICAL.json"
    for ecfont_source in EComServerStart.cpp Registrar.cpp htcleoecserverexception.inl htcleoecfontregistry.h htcleoecfontregistry.inl; do
        cp "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/$ecfont_source" "$output/$ecfont_source.862"
    done
    for retained_home861 in HOME-EXTERNAL-EMPTY-OBJECTS.json RegistryData-861.cpp ecomserver-home-empty-861-full-dump.txt ecomserver-home-empty-861.map ecomserver-home-empty-861.sym; do
        cp "$incremental_parent_root/build/$retained_home861" "$output/$retained_home861"
    done
    cp "$incremental_parent_root/build/HOME-EXTERNAL-EMPTY-PARENT-861-ROM.json" "$output/HOME-EXTERNAL-EMPTY-PARENT-861-ROM.json"
    cp "$incremental_parent_root/build/HOME-EXTERNAL-EMPTY-PARENT-861-CANONICAL.json" "$output/HOME-EXTERNAL-EMPTY-PARENT-861-CANONICAL.json"
fi

# Rebuild the ECom client library selected by the ROM.  Its UID-attributed
# fail-open log brackets the exact NVG CreateImplementationL request through
# server IPC, RLibrary load, ordinal lookup, proxy table and NewL dispatch.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    # Retain856 source; publish the reviewed898 standalone object/binary later.
    python3 "$font_ecom_reconnect" "$full_epocroot"
    font_ecom_reconnect_policy=font-interface101f7f5d-minus15-one-existing-native-reconnect-real-result-no-failopen
fi
if [ "$incremental_resource_policy" != gate19-filemanager-registration ]; then
    sbs_clean -b "$ecom_build_bldinf" -c "$ssm_config"
    sbs_build_for "$ecom_binary" -- \
        -b "$ecom_build_bldinf" -c "$ssm_config" -j 4
fi
test -s "$ecom_binary"
ecom_session_obj=$(find "$full_epocroot/epoc32/build/ecom-client-build" \
    -path '*/ecom_dll/armv5/urel/*' -iname 'EComSession.o' -type f | head -n 1)
ecom_load_obj=$(find "$full_epocroot/epoc32/build/ecom-client-build" \
    -path '*/ecom_dll/armv5/urel/*' -iname 'LoadManager.o' -type f | head -n 1)
ecom_unload_obj=$(find "$full_epocroot/epoc32/build/ecom-client-build" \
    -path '*/ecom_dll/armv5/urel/*' -iname 'UnloadPolicy.o' -type f | head -n 1)
ecom_logger_obj=$(find "$full_epocroot/epoc32/build/ecom-client-build" \
    -path '*/ecom_dll/armv5/urel/*' -iname 'HtcleoEcomLog.o' -type f | head -n 1)
test -n "$ecom_session_obj" && test -s "$ecom_session_obj"
test -n "$ecom_load_obj" && test -s "$ecom_load_obj"
test -n "$ecom_unload_obj" && test -s "$ecom_unload_obj"
test -n "$ecom_logger_obj" && test -s "$ecom_logger_obj"
ecom_session_disasm="$output/ecom-session-durable-log-urel.disasm"
ecom_load_disasm="$output/ecom-load-manager-durable-log-urel.disasm"
ecom_unload_disasm="$output/ecom-unload-policy-durable-log-urel.disasm"
ecom_logger_disasm="$output/ecom-logger-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ecom_session_obj" >"$ecom_session_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ecom_load_obj" >"$ecom_load_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ecom_unload_obj" >"$ecom_unload_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ecom_logger_obj" >"$ecom_logger_disasm"
grep -q 'HtcleoEcomLog' "$ecom_session_disasm"
grep -q '0000f212' "$ecom_session_disasm"
grep -q '0000f246' "$ecom_session_disasm"
for ecom_matrixmenu_retry_stage in 0311 0312 0313
do
    grep -qi "0000${ecom_matrixmenu_retry_stage}" "$ecom_session_disasm"
done
grep -q 'movs.*#196' "$ecom_session_disasm"
grep -q 'movs.*#197' "$ecom_session_disasm"
grep -q 'R_ARM_.*CALL.*RHandleBase.*Close' "$ecom_session_disasm"
grep -q 'R_ARM_.*CALL.*ConstructL' "$ecom_session_disasm"
grep -q 'HtcleoEcomLog' "$ecom_load_disasm"
grep -q 'HtcleoEcomLog' "$ecom_unload_disasm"
grep -q 'HtcleoEcomHspsClientLog' "$ecom_session_disasm"
grep -q 'HtcleoEcomHspsClientLog' "$ecom_load_disasm"
grep -q 'HtcleoEcomHspsClientLog' "$ecom_unload_disasm"
grep -q 'HtcleoEcomHspsClientLog' "$ecom_logger_disasm"
grep -qi '0000c707' "$ecom_session_disasm"
grep -qi '0000c719' "$ecom_load_disasm"
grep -qi '0000c726' "$ecom_unload_disasm"
grep -qi '0000c738' "$ecom_load_disasm"
grep -q 'R_ARM_.*CALL.*_ZN7RLoader11LoadLibrary' "$ecom_unload_disasm"
test "$(grep -c '4778[[:space:]]*bx[[:space:]]*pc' \
    "$ecom_unload_disasm")" -eq 2
test "$(grep -c 'ef00009f.*svc' "$ecom_unload_disasm")" -eq 1
test "$(grep -c 'ef0000a0.*svc' "$ecom_unload_disasm")" -eq 1
test "$(grep -c 'e12fff1e[[:space:]]*bx[[:space:]]*lr' \
    "$ecom_unload_disasm")" -eq 2
! grep -q 'df9f.*svc\|dfa0.*svc' "$ecom_unload_disasm"
test "$(grep -c 'bl.*HtcleoNvgLibraryAttachExec' \
    "$ecom_unload_disasm")" -eq 7
for bootstrap_phase in 1 2 3 4 5 6
do
    grep -q "420${bootstrap_phase}0100" "$ecom_unload_disasm"
    grep -q "0000b10${bootstrap_phase}" "$ecom_unload_disasm"
    grep -q "0000b20${bootstrap_phase}" "$ecom_unload_disasm"
done
grep -q 'a0b60000' "$ecom_unload_disasm"
grep -q 'HtcleoNvgAttachWatchThread' "$ecom_unload_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*Create' "$ecom_unload_disasm"
grep -q 'R_ARM_.*CALL.*RThread.*SetPriority' "$ecom_unload_disasm"
grep -q 'R_ARM_.*CALL.*RSemaphore.*Wait' "$ecom_unload_disasm"
grep -q 'R_ARM_.*CALL.*RSemaphore.*Signal' "$ecom_unload_disasm"
! grep -q 'R_ARM_.*CALL.*_ZN8RLibrary4InitEv' "$ecom_unload_disasm"
! grep -q 'e7f000f0' "$ecom_unload_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$ecom_logger_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$ecom_logger_disasm"
strings "$ecom_logger_obj" | grep -q 'HTCLEO_ECOM '
strings -el "$ecom_logger_obj" | grep -Fq 'C:\Symbian3\ECOMLOG.TXT'
sha256sum "$ecom_binary" >"$output/ecom-client-urel.sha256"
sha256sum "$ecom_session_obj" >"$output/ecom-session-urel.sha256"
sha256sum "$ecom_load_obj" >"$output/ecom-load-manager-urel.sha256"
sha256sum "$ecom_unload_obj" >"$output/ecom-unload-policy-urel.sha256"
sha256sum "$ecom_logger_obj" >"$output/ecom-logger-urel.sha256"

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    for retained_ecom_file in FONT-ECOM-OBJECTS.json EComSession-856.cpp ecom-font-list-856-full-dump.txt ecom-font-list-856.map ecom-font-list-856.sym; do
        cp "$incremental_parent_root/build/$retained_ecom_file" "$output/$retained_ecom_file"
    done
    cp "$incremental_parent_root/build/FONT-ECOM-PARENT-856-ROM.json" "$output/FONT-ECOM-PARENT-856-ROM.json"
    cp "$incremental_parent_root/build/FONT-ECOM-PARENT-856-CANONICAL.json" "$output/FONT-ECOM-PARENT-856-CANONICAL.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ]; then
    gscreate_evidence="$project/Symbian/output/iteration-evidence/826-gsapp-ecom-create-retry"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$ecom_binary" >"$output/ecom-create-retry-826-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-ecom-create-retry.py" \
        --baseline "$gscreate_evidence/CONTROL-OBJECTS.json" --native "$output" \
        --report "$output/GSAPP-CREATE-RETRY-OBJECTS.json"
    cp "$ecom_session" "$output/EComSession-826.cpp"
    cp "$ecom_binary.map" "$output/ecom-create-retry-826.map"
    cp "$ecom_binary.sym" "$output/ecom-create-retry-826.sym"
    cp "$gscreate_evidence/ecom-native-source-control-825.dll" \
        "$gscreate_evidence/SOURCE-CONTROL.json" "$output/"
fi

# Rebuild PtiEngine only for the MatrixMenu English-keymap fallback.  The
# frozen 1-475 ABI must remain exact; one reviewed GCCE-only const overload is
# appended at 476 and is not consumed by existing callers.
sbs_clean -b "$ptiengine_bldinf" -c "$ssm_config"
sbs_build_for "$ptiengine_binary" -- \
    -b "$ptiengine_bldinf" -c "$ssm_config" -j 4
test -s "$ptiengine_binary"
ptiengine_core_obj=$(find "$full_epocroot/epoc32/build/ptiengine-build" \
    -path '*/ptiengine_dll/armv5/urel/PtiDefaultCore.o' -type f | head -n 1)
ptiengine_generated_def=$(find "$full_epocroot/epoc32/build/ptiengine-build" \
    -path '*/ptiengine_dll/armv5/urel/PtiEngine*.def' -type f | head -n 1)
test -n "$ptiengine_core_obj" && test -s "$ptiengine_core_obj"
test -n "$ptiengine_generated_def" && test -s "$ptiengine_generated_def"
ptiengine_core_disasm="$output/ptiengine-default-core-english-fallback-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$ptiengine_core_obj" >"$ptiengine_core_disasm"
grep -qi '10281897' "$ptiengine_core_disasm"
grep -q 'R_ARM_.*CALL.*RProcess.*SecureId' "$ptiengine_core_disasm"
grep -q 'R_ARM_.*CALL.*CPtiKeyMapDataFactory.*CreateImplementationL' \
    "$ptiengine_core_disasm"
test "$(grep -c ' @ ' "$ptiengine_frozen_def")" -eq 475
grep ' @ ' "$ptiengine_frozen_def" | sed 's/\r$//' \
    >"$output/ptiengine-frozen-exports.def"
sed '/^; NEW:/,$d' "$ptiengine_generated_def" | grep ' @ ' | sed 's/\r$//' \
    >"$output/ptiengine-generated-frozen-prefix.def"
cmp -s "$output/ptiengine-frozen-exports.def" \
    "$output/ptiengine-generated-frozen-prefix.def"
test "$(grep -c '^; NEW:' "$ptiengine_generated_def")" -eq 1
grep -q '_ZNK14CPtiEngineImpl8CoreInfoE19TPtiEngineInputMode @ 476 NONAME' \
    "$ptiengine_generated_def"
"$native_epocroot/epoc32/tools/elf2e32" --dump=hse \
    --e32input="$ptiengine_binary" >"$output/ptiengine-e32-dump.txt"
grep -qi 'Secure ID: 101f8610' "$output/ptiengine-e32-dump.txt"
grep -qi 'Number of exports = 476' "$output/ptiengine-e32-dump.txt"
sha256sum "$ptiengine_binary" >"$output/ptiengine-urel.sha256"
sha256sum "$ptiengine_core_obj" \
    >"$output/ptiengine-default-core-object-urel.sha256"
sha256sum "$ptiengine_stock_657" \
    >"$output/ptiengine-stock-657.sha256"

# Rebuild the exact STEM OpenC backend mapped to sys\bin\backend.dll.  The
# isolated unit avoids unrelated incubator targets; a full CLEAN is required
# because the constructor source and one frozen-export declaration changed.
sbs_clean -b "$stem_backend_bldinf" -c "$ssm_config"
sbs_build_for "$stem_backend_binary" -- \
    -b "$stem_backend_bldinf" -c "$ssm_config" -j 4
test -s "$stem_backend_binary"
stem_backend_obj=$(find "$full_epocroot/epoc32/build/stem-backend-build" \
    -path '*/stem_backend_dll/armv5/urel/localif.o' -type f | head -n 1)
stem_backend_generated_def=$(find "$full_epocroot/epoc32/build/stem-backend-build" \
    -path '*/stem_backend_dll/armv5/urel/stem_backend*.def' -type f | head -n 1)
test -n "$stem_backend_obj" && test -s "$stem_backend_obj"
test -n "$stem_backend_generated_def" && test -s "$stem_backend_generated_def"
stem_backend_disasm="$output/stem-backend-constructor-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$stem_backend_obj" >"$stem_backend_disasm"
grep -q 'HtcleoStemBackendLog' "$stem_backend_disasm"
# GCCE emits both C1 and C2 constructor bodies. Each contains the original 36
# checkpoints plus exact D125 timezone-defer evidence, for 74 direct calls.
test "$(grep -c 'bl.*HtcleoStemBackendLog' "$stem_backend_disasm")" -eq 74
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$stem_backend_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$stem_backend_disasm"
! grep -q 'e7f000f0' "$stem_backend_disasm"
strings "$stem_backend_obj" | grep -q 'HTCLEO_ECOM '
strings -el "$stem_backend_obj" | grep -Fq 'C:\Symbian3\ECOMLOG.TXT'
test "$(grep -E '@[[:space:]]+[0-9]+' "$stem_backend_frozen_def" | wc -l)" -eq 176
test "$(grep -E '@[[:space:]]+[0-9]+' "$stem_backend_generated_def" | wc -l)" -eq 176
tr -d '\r' <"$stem_backend_frozen_def" | sed '/^[[:space:]]*$/d' \
    >"$output/stem-backend-frozen-exports.def"
tr -d '\r' <"$stem_backend_generated_def" | sed '/^[[:space:]]*$/d' \
    >"$output/stem-backend-generated-exports.def"
diff -u "$output/stem-backend-frozen-exports.def" \
    "$output/stem-backend-generated-exports.def"
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$stem_backend_binary" >"$output/stem-backend-e32-dump.txt"
grep -q 'Secure ID: 102828d5' "$output/stem-backend-e32-dump.txt"
grep -q 'Number of exports = 176' "$output/stem-backend-e32-dump.txt"
sha256sum "$stem_backend_binary" >"$output/stem-backend-urel.sha256"
sha256sum "$stem_backend_obj" >"$output/stem-backend-localif-urel.sha256"

# Iteration 437 replaces only Hitchcock with a source-built image whose first
# 2011 frozen exports remain byte-for-byte ordinal compatible.  The linker
# wraps the stock E32 process-attach body so CC00-CC05 can bracket the export
# table and the single GCCE static initializer without touching kernel attach,
# display, loader policy or timing.
# Generate Hitchcock's import-only DSOs here, after the iteration-specific
# AKNSKINSRV.dll has been rebuilt.  This ordering also makes an interrupted
# incremental skin-server build safely resumable when its old release image
# was already removed.
python3 "$hitchcock_import_dso_tool" "$full_epocroot"
sbs_clean --configpath="$hitchcock_config_path" \
    --mo=NOHIDEALL=1 -b "$hitchcock_bldinf" -c "$hitchcock_config"
sbs_build_for "$hitchcock_binary" -- \
    --configpath="$hitchcock_config_path" \
    --mo=NOHIDEALL=1 -b "$hitchcock_bldinf" -c "$hitchcock_config" -j 4
test -s "$hitchcock_binary"
test -s "$hitchcock_sym"
test -s "$hitchcock_map"
test "$(find "$full_epocroot/epoc32/build/hitchcock-build" \
    -path '*/hitchcock_dll/armv5/urel/htcleohitchcockentrytrace.o' \
    -type f | wc -l)" -eq 1
test "$(find "$full_epocroot/epoc32/build/hitchcock-build" \
    -path '*/hitchcock_dll/armv5/urel/hitchcock*.def' \
    -type f | wc -l)" -eq 1
hitchcock_obj=$(find "$full_epocroot/epoc32/build/hitchcock-build" \
    -path '*/hitchcock_dll/armv5/urel/htcleohitchcockentrytrace.o' -type f)
hitchcock_generated_def=$(find "$full_epocroot/epoc32/build/hitchcock-build" \
    -path '*/hitchcock_dll/armv5/urel/hitchcock*.def' -type f)
test -s "$hitchcock_obj"
test -s "$hitchcock_generated_def"
hitchcock_disasm="$output/hitchcock-entrypoint-durable-log-urel.disasm"
hitchcock_obj_nm="$output/hitchcock-entrypoint-durable-log-urel.nm"
hitchcock_image_nm="$output/hitchcock-image-urel.nm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr \
    "$hitchcock_obj" >"$hitchcock_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-nm" -n \
    "$hitchcock_obj" >"$hitchcock_obj_nm"
"$SBS_GCCE441BIN/arm-none-symbianelf-nm" -n \
    "$hitchcock_sym" >"$hitchcock_image_nm"
grep -q '<__wrap__E32Dll_Body>:' "$hitchcock_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5WriteERK6TDesC8' "$hitchcock_disasm"
grep -q 'R_ARM_.*CALL.*_ZN5RFile5FlushEv' "$hitchcock_disasm"
grep -q 'R_ARM_.*CALL.*__DLL_Export_Table__' "$hitchcock_disasm"
grep -q 'R_ARM_.*CALL.*__cpp_initialize__aeabi_' "$hitchcock_disasm"
! grep -q 'HalFunction\|User::After\|User::WaitForRequest\|e7f000f0' \
    "$hitchcock_disasm"
test "$(grep -c ' T __wrap__E32Dll_Body$' "$hitchcock_obj_nm")" -eq 1
test "$(grep -E ' R _ZT[IV]22CHuiFxGenericParameter' \
    "$hitchcock_obj_nm" | wc -l)" -eq 4
grep -q ' t _E32Dll$' "$hitchcock_image_nm"
grep -q ' T __wrap__E32Dll_Body$' "$hitchcock_image_nm"
test "$("$SBS_GCCE441BIN/arm-none-symbianelf-readelf" -r \
    "$hitchcock_sym" | grep -c '__wrap__E32Dll_Body')" -eq 1
hitchcock_init_base=$(awk '$3 == "SHT$$INIT_ARRAY$$Base" {print "0x" $1}' \
    "$hitchcock_image_nm")
hitchcock_init_limit=$(awk '$3 == "SHT$$INIT_ARRAY$$Limit" {print "0x" $1}' \
    "$hitchcock_image_nm")
test $((hitchcock_init_limit - hitchcock_init_base)) -eq 4
tr -d '\r' <"$hitchcock_frozen_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/hitchcock-frozen-exports.def"
tr -d '\r' <"$hitchcock_generated_def" | \
    sed 's/[[:space:]]*$//;/^[[:space:]]*$/d' \
    >"$output/hitchcock-generated-exports.def"
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/hitchcock-frozen-exports.def" | wc -l)" -eq 2011
test "$(grep -E '@[[:space:]]+[0-9]+' \
    "$output/hitchcock-generated-exports.def" | wc -l)" -ge 2011
head -n 2012 "$output/hitchcock-generated-exports.def" \
    >"$output/hitchcock-generated-frozen-prefix.def"
diff -u "$output/hitchcock-frozen-exports.def" \
    "$output/hitchcock-generated-frozen-prefix.def"
test "$(sed -n '2013p' "$output/hitchcock-generated-exports.def")" = '; NEW:'
"$full_epocroot/epoc32/tools/elf2e32" --dump=hseit \
    --e32input="$hitchcock_binary" >"$output/hitchcock-e32-dump.txt"
grep -q 'Secure ID: a48a362e' "$output/hitchcock-e32-dump.txt"
grep -q 'Module Version: 10.0' "$output/hitchcock-e32-dump.txt"
test "$(sed -n 's/^Number of exports = //p' \
    "$output/hitchcock-e32-dump.txt")" -ge 2011
cp "$hitchcock_map" "$output/hitchcock-urel.map"
sha256sum "$hitchcock_binary" >"$output/hitchcock-urel.sha256"
sha256sum "$hitchcock_obj" \
    >"$output/hitchcock-entrypoint-object-urel.sha256"
sha256sum "$hitchcock_map" >"$output/hitchcock-map-urel.sha256"

ssm_main_obj=$(find "$full_epocroot/epoc32/build/ssm" \
    -path '*/sysstatemgr_exe/armv5/urel/main.o' -type f | head -n 1)
ssm_server_obj=$(find "$full_epocroot/epoc32/build/ssm" \
    -path '*/sysstatemgr_exe/armv5/urel/ssmserver.o' -type f | head -n 1)
ssm_engine_obj=$(find "$full_epocroot/epoc32/build/ssm" \
    -path '*/sysstatemgr_exe/armv5/urel/ssmstatetransitionengine.o' -type f | head -n 1)
ssm_cle_obj=$(find "$full_epocroot/epoc32/build/cle" \
    -path '*/ssmclesrv_lib/armv5/urel/cmdlistexecutor.o' -type f | head -n 1)
test -n "$ssm_main_obj" && test -s "$ssm_main_obj"
test -n "$ssm_server_obj" && test -s "$ssm_server_obj"
test -n "$ssm_engine_obj" && test -s "$ssm_engine_obj"
test -n "$ssm_cle_obj" && test -s "$ssm_cle_obj"
ssm_disasm="$output/sysstatemgr-main-rendezvous-urel.disasm"
ssm_server_disasm="$output/sysstatemgr-server-durable-log-urel.disasm"
ssm_engine_disasm="$output/sysstatemgr-engine-durable-log-urel.disasm"
ssm_cle_disasm="$output/sysstatemgr-cle-command-log-urel.disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ssm_main_obj" >"$ssm_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ssm_server_obj" >"$ssm_server_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ssm_engine_obj" >"$ssm_engine_disasm"
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$ssm_cle_obj" >"$ssm_cle_disasm"
grep -q 'Rendezvous' "$ssm_disasm"
grep -q 'HtcleoSsmLog' "$ssm_disasm"
grep -q 'HtcleoSsmLog' "$ssm_server_disasm"
grep -q 'HtcleoSsmLog' "$ssm_engine_disasm"
grep -q 'HtcleoCleLog' "$ssm_cle_disasm"
# GCCE emits this target as Thumb and synthesises the 0x10000000 and
# 0xe0000000 prefixes from smaller immediates.  Validate the exact source
# constants plus the linked call sites instead of requiring those complete
# words to survive literally in the disassembly.
grep -Fq 'HtcleoSsmLog(0x10000000u | (TUint32)iNextAction' \
    "$ssm_component/ssm/src/ssmstatetransitionengine.cpp"
grep -Fq 'HtcleoSsmLog(0x20000005u, htcleoState, KErrNone)' \
    "$ssm_component/ssm/src/ssmstatetransitionengine.cpp"
grep -Fq 'HtcleoSsmLog(0xE0000000u | (TUint32)iNextAction' \
    "$ssm_component/ssm/src/ssmstatetransitionengine.cpp"
test "$(grep -c 'R_ARM_THM_CALL[[:space:]]*_Z12HtcleoSsmLogmmi' "$ssm_disasm")" -eq 4
test "$(grep -c 'R_ARM_THM_CALL[[:space:]]*_Z12HtcleoSsmLogmmi' "$ssm_server_disasm")" -eq 3
test "$(grep -c 'R_ARM_THM_CALL[[:space:]]*_Z12HtcleoSsmLogmmi' "$ssm_engine_disasm")" -eq 3
grep -q 'R_ARM_THM_CALL[[:space:]]*_ZN5RFile5WriteERK6TDesC8' "$ssm_disasm"
grep -q 'R_ARM_THM_CALL[[:space:]]*_ZN5RFile5FlushEv' "$ssm_disasm"
# sysstatemgr.exe is E32-compressed, so GNU strings cannot inspect its payload
# directly.  The just-linked main object is the authoritative uncompressed
# source of the fixed ASCII record prefix and UTF-16 path.
strings "$ssm_main_obj" | grep -q 'HTCLEO_SSM '
strings -el "$ssm_main_obj" | grep -Fq 'C:\Symbian3\SSMLOG.TXT'
grep -q 'R_ARM_THM_CALL[[:space:]]*_ZN5RFile5WriteERK6TDesC8' "$ssm_cle_disasm"
grep -q 'R_ARM_THM_CALL[[:space:]]*_ZN5RFile5FlushEv' "$ssm_cle_disasm"
strings "$ssm_cle_obj" | grep -q 'HTCLEO_CLE '
strings -el "$ssm_cle_obj" | grep -Fq 'C:\Symbian3\CLELOG.TXT'
test "$(grep -c 'HtcleoCleLog' "$ssm_cle_disasm")" -ge 9
sha256sum "$ssm_binary" >"$output/sysstatemgr-urel.sha256"
sha256sum "$ssm_cle_obj" >"$output/sysstatemgr-cle-command-log-urel.sha256"

# Keep the exact742 aifw control while promoting only the already-audited743
# Xn native-focus state machine. The rebuilt source must match immutable743
# apart from E32 creation-time/header CRC bytes before the exact image is used.
ui_742_control="$project/Symbian/output/742-symbian3-full-matrix-unowned-kick-retired-incremental/Symbian3/build/incremental-release-cache"
ui_743_reference="$project/Symbian/output/743-symbian3-full-home-focus-liveness-incremental/Symbian3/build/incremental-release-cache"
if [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$project/Symbian/scripts/apply-htcleo-home-background-priority-ab.py" \
        --report "$output/HOME-PRIORITY-AB-BINARY.json"
    test "$(sha256sum "$homescreen_aifw_binary" | awk '{print $1}')" = \
        eb6e34b8fa929dcd424cf4d6973e5fbdc7fbc77cef904d44f7aa15c95cc25cc7
    echo 'HTCLEO_840_UI_CONTROL=carried-byte-identical-including-priority-retention'
elif incremental_wants_binary "$xn3layout_binary"; then
    python3 "$ui_743_xn_focus_promoter" \
        "$full_epocroot/epoc32/release/armv5/urel" \
        "$ui_742_control" "$ui_743_reference"
elif incremental_wants_binary "$homescreen_aifw_binary"; then
    echo "ERROR: aifw changes require an explicit aifw742/xn743 control policy" >&2
    exit 1
else
    test "$(sha256sum "$homescreen_aifw_binary" | awk '{print $1}')" = \
        eb6e34b8fa929dcd424cf4d6973e5fbdc7fbc77cef904d44f7aa15c95cc25cc7
    test "$(sha256sum "$xn3layout_binary" | awk '{print $1}')" = \
        b9fd5ebf7117d1b8c676d12a4f74ba55dd07b63a1f0bc9cc5fb2d6a7d4d53cb4
    printf 'HTCLEO_742_AIFW_743_XN_CONTROL=carried-byte-identical\n'
fi
if [ "$incremental_resource_policy" = gate17-home-background-priority-ab ]; then
    python3 "$project/Symbian/scripts/inspect-htcleo-home-priority-840.py" >"$output/HOME-PRIORITY-AB-ATTRIBUTION.txt"
    python3 "$project/Symbian/scripts/apply-htcleo-home-background-priority-ab.py" --apply \
        --report "$output/HOME-PRIORITY-AB-BINARY.json"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$xn3layout_binary" >"$output/xn3layoutengine-e32-dump.txt"
fi
sha256sum "$homescreen_aifw_binary" >"$output/aifw-urel.sha256"
sha256sum "$xn3layout_binary" >"$output/xn3layoutengine-urel.sha256"

if [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    if [ "$incremental_resource_policy" = gate17-font-family-binding ]; then
        python3 "$font_family_binding" --apply --report "$output/FONT-FAMILY-BINARY.json"
    else
        python3 "$font_family_binding" --report "$output/FONT-FAMILY-BINARY.json"
    fi
    font_family_binding_policy=FontProvider-three-constdata-families-to-existing-DejaVu-Sans-no-code-fontfile-or-layout-change
    cp "$project/Symbian/output/iteration-evidence/852-font-family-binding/FontProvider-stock-851.dll" "$output/FontProvider-stock-851.dll"
    cp "$project/Symbian/output/iteration-evidence/852-font-family-binding/FontProvider-stock-851.map" "$output/FontProvider-stock-851.map"
    "$native_epocroot/epoc32/tools/elf2e32" --dump=hseit \
        --e32input="$full_epocroot/epoc32/release/armv5/urel/FontProvider.dll" >"$output/fontprovider-family-852-full-dump.txt"
fi

if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$fbs_rom_rasterizer" --report "$output/FBS-ROM-RASTERIZER-BINARY.json"
    cp "$incremental_parent_root/build/FBS-ROM-RASTERIZER-PARENT-857-ROM.json" "$output/FBS-ROM-RASTERIZER-PARENT-857-ROM.json"
    cp "$incremental_parent_root/build/FBS-ROM-RASTERIZER-PARENT-857-CANONICAL.json" "$output/FBS-ROM-RASTERIZER-PARENT-857-CANONICAL.json"
    fbs_rom_rasterizer_policy=FBServ-LoadOpenFontLibraries-native-ROM-only-resolver-r2-false-to-true-one-byte-no-relink
    cp "$project/Symbian/output/iteration-evidence/857-fbs-rom-rasterizer/fbserv-parent856.exe" "$output/fbserv-parent856.exe"
    cp "$project/Symbian/output/iteration-evidence/857-fbs-rom-rasterizer/fbserv-parent856.map" "$output/fbserv-parent856.map"
fi


#886: retain885 observation; FileManager joins the existing zero-handle SGC mode.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_local_evidence="$project/Symbian/output/iteration-evidence/886-filemanager-sgc-local"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-lifetime.py" "$full_epocroot"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-startup.py" "$full_epocroot"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-env.py" "$full_epocroot"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-aknenv.py" "$full_epocroot"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-sgc.py" "$full_epocroot"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-sgc-local.py" "$full_epocroot"
    cp "$fm_local_evidence/avkon-standalone-886.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-sgc-local-886-full-dump.txt"
    # Historical886 proof; the final888 verifier checks the current198 objects.
    cp "$project/Symbian/output/886-symbian3-full-filemanager-sgc-local-incremental/Symbian3/build/FILEMANAGER-SGC-LOCAL-OBJECTS.json" "$output/FILEMANAGER-SGC-LOCAL-OBJECTS.json"
    cp "$fm_local_evidence/avkon-sgc-local-886.map" "$output/avkon-sgc-local-886.map"
    cp "$fm_local_evidence/avkon-sgc-local-886.sym" "$output/avkon-sgc-local-886.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp" "$output/aknsgcc-886.cpp"
    cp "$output/avkon-sgc-local-886-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#887: publish the reviewed two-object CONE FEP observer after all parent layers.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_fep_evidence="$project/Symbian/output/iteration-evidence/887-filemanager-fep-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-fep-frontier.py" "$full_epocroot"
    cp "$fm_fep_evidence/cone-standalone-887.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-fep-887-full-dump.txt"
    # Historical887 proof; final889 checks the current23 CONE objects.
    cp "$project/Symbian/output/887-symbian3-full-filemanager-fep-frontier-incremental/Symbian3/build/FILEMANAGER-FEP-OBJECTS.json" "$output/FILEMANAGER-FEP-OBJECTS.json"
    cp "$fm_fep_evidence/cone-fep-887.map" "$output/cone-fep-887.map"
    cp "$fm_fep_evidence/cone-fep-887.sym" "$output/cone-fep-887.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEFEP.CPP" "$output/COEFEP-887.CPP"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEMAINSECUREFEP.CPP" "$output/COEMAINSECUREFEP-887.CPP"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#888: keep887 CONE/FEP witness and observe only the first FileManager focus.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_focus_evidence="$project/Symbian/output/iteration-evidence/888-filemanager-focus-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-focus-frontier.py" "$full_epocroot"
    cp "$fm_focus_evidence/avkon-standalone-888.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-focus-888-full-dump.txt"
    # Historical888 proof; final890 verifies the current198 Avkon objects.
    cp "$project/Symbian/output/888-symbian3-full-filemanager-focus-frontier-incremental/Symbian3/build/FILEMANAGER-FOCUS-OBJECTS.json" "$output/FILEMANAGER-FOCUS-OBJECTS.json"
    cp "$fm_focus_evidence/avkon-focus-888.map" "$output/avkon-focus-888.map"
    cp "$fm_focus_evidence/avkon-focus-888.sym" "$output/avkon-focus-888.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp" "$output/AknAppUi-888.cpp"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/htcleofmfocus888.inl" "$output/htcleofmfocus888.inl"
    cp "$output/avkon-focus-888-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#889: source-native first-redraw/view boundaries; all888 behavior retained.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_ui_evidence="$project/Symbian/output/iteration-evidence/889-filemanager-ui-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ui-frontier.py" "$full_epocroot"
    cp "$fm_ui_evidence/cone-standalone-889.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-ui-889-full-dump.txt"
    # Historical889 proof; final893 verifies the current23 CONE objects.
    cp "$project/Symbian/output/889-symbian3-full-filemanager-ui-frontier-incremental/Symbian3/build/FILEMANAGER-UI-OBJECTS.json" "$output/FILEMANAGER-UI-OBJECTS.json"
    cp "$fm_ui_evidence/cone-ui-889.map" "$output/cone-ui-889.map"
    cp "$fm_ui_evidence/cone-ui-889.sym" "$output/cone-ui-889.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEPRIV.CPP" "$output/COEPRIV-889.CPP"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/coevwman.cpp" "$output/coevwman-889.cpp"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleofmredraw889.inl" "$output/htcleofmredraw889.inl"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleofmview889.inl" "$output/htcleofmview889.inl"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#890: observe the deferred activation after889's accepted view notification.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_activation_evidence="$project/Symbian/output/iteration-evidence/890-filemanager-activation-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-activation-frontier.py" "$full_epocroot"
    cp "$fm_activation_evidence/avkon-standalone-890.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-activation-890-full-dump.txt"
    # Historical890 proof; final891 verifies the current198 Avkon objects.
    cp "$project/Symbian/output/890-symbian3-full-filemanager-activation-frontier-incremental/Symbian3/build/FILEMANAGER-ACTIVATION-OBJECTS.json" "$output/FILEMANAGER-ACTIVATION-OBJECTS.json"
    cp "$fm_activation_evidence/avkon-activation-890.map" "$output/avkon-activation-890.map"
    cp "$fm_activation_evidence/avkon-activation-890.sym" "$output/avkon-activation-890.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknViewAppUi.cpp" "$output/AknViewAppUi-890.cpp"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/htcleofmactivation890.inl" "$output/htcleofmactivation890.inl"
    cp "$output/avkon-activation-890-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#891: at most16 meaningful FileManager WS callbacks, no dispatch-policy change.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_ws_evidence="$project/Symbian/output/iteration-evidence/891-filemanager-ws-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ws-frontier.py" "$full_epocroot"
    cp "$fm_ws_evidence/avkon-standalone-891.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-ws-891-full-dump.txt"
    # Historical891 proof; final894 verifies the current198 Avkon objects.
    cp "$project/Symbian/output/891-symbian3-full-filemanager-ws-frontier-incremental/Symbian3/build/FILEMANAGER-WS-OBJECTS.json" "$output/FILEMANAGER-WS-OBJECTS.json"
    cp "$fm_ws_evidence/avkon-ws-891.map" "$output/avkon-ws-891.map"
    cp "$fm_ws_evidence/avkon-ws-891.sym" "$output/avkon-ws-891.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp" "$output/AknAppUi-891.cpp"
    cp "$output/avkon-ws-891-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#892: bounded pre-I/O ready candidates at the existing post-Wait hook.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_ready_evidence="$project/Symbian/output/iteration-evidence/892-filemanager-ready-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ready-frontier.py" "$full_epocroot"
    cp "$fm_ready_evidence/cone-standalone-892.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-ready-892-full-dump.txt"
    # Historical892 proof; final893 verifies the current23 CONE objects.
    cp "$project/Symbian/output/892-symbian3-full-filemanager-ready-frontier-incremental/Symbian3/build/FILEMANAGER-READY-OBJECTS.json" "$output/FILEMANAGER-READY-OBJECTS.json"
    cp "$fm_ready_evidence/cone-ready-892.map" "$output/cone-ready-892.map"
    cp "$fm_ready_evidence/cone-ready-892.sym" "$output/cone-ready-892.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp" "$output/htcleoschedulertrace-892.cpp"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#893: identify only exact CIdle/CPeriodic callbacks in the same bounded snapshot.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_callback_evidence="$project/Symbian/output/iteration-evidence/893-filemanager-callback-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-callback-frontier.py" "$full_epocroot"
    cp "$fm_callback_evidence/cone-standalone-893.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-callback-893-full-dump.txt"
    # Historical893 proof; final896 verifies the current23 CONE objects.
    cp "$project/Symbian/output/893-symbian3-full-filemanager-callback-frontier-incremental/Symbian3/build/FILEMANAGER-CALLBACK-OBJECTS.json" "$output/FILEMANAGER-CALLBACK-OBJECTS.json"
    cp "$fm_callback_evidence/cone-callback-893.map" "$output/cone-callback-893.map"
    cp "$fm_callback_evidence/cone-callback-893.sym" "$output/cone-callback-893.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp" "$output/htcleoschedulertrace-893.cpp"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#894: observe the real callback identified in893, without changing dialog policy.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_progress_evidence="$project/Symbian/output/iteration-evidence/894-filemanager-progress-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-progress-frontier.py" "$full_epocroot"
    cp "$fm_progress_evidence/avkon-standalone-894.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-progress-894-full-dump.txt"
    # Historical894 proof; final895 verifies the current198 Avkon objects.
    cp "$project/Symbian/output/894-symbian3-full-filemanager-progress-frontier-incremental/Symbian3/build/FILEMANAGER-PROGRESS-OBJECTS.json" "$output/FILEMANAGER-PROGRESS-OBJECTS.json"
    cp "$fm_progress_evidence/avkon-progress-894.map" "$output/avkon-progress-894.map"
    cp "$fm_progress_evidence/avkon-progress-894.sym" "$output/avkon-progress-894.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/AknProgressDialog.cpp" "$output/AknProgressDialog-894.cpp"
    cp "$output/avkon-progress-894-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#895: pair FileManager's existing local fade getter with a no-session setter.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_systemfade_evidence="$project/Symbian/output/iteration-evidence/895-filemanager-system-fade"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-system-fade.py" "$full_epocroot"
    cp "$fm_systemfade_evidence/avkon-standalone-895.dll" "$stem_avkon_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_avkon_binary" >"$output/avkon-systemfade-895-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-system-fade.py" --native "$output" --report "$output/FILEMANAGER-SYSTEMFADE-OBJECTS.json"
    cp "$fm_systemfade_evidence/avkon-systemfade-895.map" "$output/avkon-systemfade-895.map"
    cp "$fm_systemfade_evidence/avkon-systemfade-895.sym" "$output/avkon-systemfade-895.sym"
    cp "$full_epocroot/sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp" "$output/aknsgcc-895.cpp"
    cp "$output/avkon-systemfade-895-full-dump.txt" "$output/stem-avkon-e32-dump.txt"
    sha256sum "$stem_avkon_binary" >"$output/stem-avkon-urel.sha256"
fi

#896: retire early candidate sampling and observe Wait25-56 at unchanged32-record cap.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_late_evidence="$project/Symbian/output/iteration-evidence/896-filemanager-late-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-late-frontier.py" "$full_epocroot"
    cp "$fm_late_evidence/cone-standalone-896.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-late-896-full-dump.txt"
    # Historical896 proof; final897 verifies the current23 CONE objects.
    cp "$project/Symbian/output/896-symbian3-full-filemanager-late-frontier-incremental/Symbian3/build/FILEMANAGER-LATE-OBJECTS.json" "$output/FILEMANAGER-LATE-OBJECTS.json"
    cp "$fm_late_evidence/cone-late-896.map" "$output/cone-late-896.map"
    cp "$fm_late_evidence/cone-late-896.sym" "$output/cone-late-896.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp" "$output/htcleoschedulertrace-896.cpp"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#897: preserve896 sampling and identify exact CAsyncCallBack objects without dispatch.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_async_evidence="$project/Symbian/output/iteration-evidence/897-filemanager-async-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-async-frontier.py" "$full_epocroot"
    cp "$fm_async_evidence/cone-standalone-897.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-async-897-full-dump.txt"
    # Historical897 CONE receipt; final900 validates the current23 objects.
    cp "$incremental_parent_root/build/FILEMANAGER-ASYNC-OBJECTS.json" "$output/FILEMANAGER-ASYNC-OBJECTS.json"
    cp "$fm_async_evidence/cone-async-897.map" "$output/cone-async-897.map"
    cp "$fm_async_evidence/cone-async-897.sym" "$output/cone-async-897.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp" "$output/htcleoschedulertrace-897.cpp"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

#898: observe native ECom destruction without changing CDL or unloading policy.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_destroy_evidence="$project/Symbian/output/iteration-evidence/898-filemanager-idle-frontier"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-ecom-destroy.py" "$full_epocroot"
    cp "$fm_destroy_evidence/ecom-standalone-898.dll" "$ecom_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$ecom_binary" >"$output/ecom-destroy-898-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-ecom-destroy.py" --native "$output" --report "$output/FILEMANAGER-DESTROY-OBJECTS.json"
    cp "$fm_destroy_evidence/ecom-destroy-898.map" "$output/ecom-destroy-898.map"
    cp "$fm_destroy_evidence/ecom-destroy-898.sym" "$output/ecom-destroy-898.sym"
    cp "$full_epocroot/sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp" "$output/EComSession-898.cpp"
    sha256sum "$ecom_binary" >"$output/ecom-client-urel.sha256"
fi

#899: source-built CDL with bounded native cleanup-tail markers, no unload-policy change.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_cdl_evidence="$project/Symbian/output/iteration-evidence/899-filemanager-cdl-tail"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-cdl-tail.py" "$full_epocroot"
    cp "$fm_cdl_evidence/cdl-standalone-899.dll" "$cdl_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$cdl_binary" >"$output/cdl-tail-899-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-cdl-tail.py" --native "$output" --report "$output/FILEMANAGER-CDL-OBJECTS.json"
    cp "$fm_cdl_evidence/cdl-tail-899.map" "$output/cdl-tail-899.map"
    cp "$fm_cdl_evidence/cdl-tail-899.sym" "$output/cdl-tail-899.sym"
    cp "$full_epocroot/sf/mw/uiresources/layouts/cdl/CdlEngine/src/CdlLibrary.cpp" "$output/CdlLibrary-899.cpp"
    sha256sum "$cdl_binary" >"$output/cdlengine-899-urel.sha256"
fi

#900: bracket existing Flush/base Wait/legacy observer. No scheduler policy change.
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    fm_wait_evidence="$project/Symbian/output/iteration-evidence/900-filemanager-wait-boundary"
    python3 "$project/Symbian/scripts/apply-htcleo-filemanager-wait-boundary.py" "$full_epocroot"
    cp "$fm_wait_evidence/cone-standalone-900.dll" "$stem_cone_binary"
    "$full_epocroot/epoc32/tools/elf2e32" --dump=hseit --e32input="$stem_cone_binary" >"$output/cone-wait-900-full-dump.txt"
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-wait-boundary.py" --native "$output" --report "$output/FILEMANAGER-WAIT-OBJECTS.json"
    cp "$fm_wait_evidence/cone-wait-900.map" "$output/cone-wait-900.map"
    cp "$fm_wait_evidence/cone-wait-900.sym" "$output/cone-wait-900.sym"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/COEMAIN.CPP" "$output/COEMAIN-900.CPP"
    cp "$full_epocroot/sf/mw/classicui/lafagnosticuifoundation/cone/src/htcleoschedulertrace.cpp" "$output/htcleoschedulertrace-900.cpp"
    sha256sum "$stem_cone_binary" >"$output/stem-cone-urel.sha256"
fi

if [ "$build_mode" = incremental ]; then
    : >"$incremental_binary_diff"
    incremental_unexpected=0
    while read -r parent_hash binary_path
    do
        current_hash=$(sha256sum "$binary_path" | awk '{print tolower($1)}')
        if [ "$current_hash" = "$parent_hash" ]; then
            printf 'UNCHANGED\t%s\t%s\n' "$binary_path" "$current_hash" \
                >>"$incremental_binary_diff"
            continue
        fi

        incremental_allowed=0
        for changed_binary in $incremental_changed_binaries
        do
            if [ "$binary_path" = "$changed_binary" ]; then
                incremental_allowed=1
                break
            fi
        done
        if [ "$incremental_allowed" = 1 ]; then
            printf 'CHANGED_ALLOWED\t%s\t%s\t%s\n' \
                "$binary_path" "$parent_hash" "$current_hash" \
                >>"$incremental_binary_diff"
        else
            printf 'CHANGED_UNEXPECTED\t%s\t%s\t%s\n' \
                "$binary_path" "$parent_hash" "$current_hash" \
                >>"$incremental_binary_diff"
            incremental_unexpected=1
        fi
    done <"$incremental_guard_manifest"

    if [ "$incremental_unexpected" -ne 0 ]; then
        echo "ERROR: incremental build changed a non-allowlisted parent binary" >&2
        grep '^CHANGED_UNEXPECTED' "$incremental_binary_diff" >&2
        exit 1
    fi
    for changed_binary in $incremental_changed_binaries
    do
        if [ "$incremental_migration" = 1 ]; then
            awk -F '\t' -v expected="$changed_binary" \
                '($1 == "CHANGED_ALLOWED" || $1 == "UNCHANGED") && $2 == expected { found=1 } END { exit !found }' \
                "$incremental_binary_diff" || {
                    echo "ERROR: migration allowlisted binary is absent: $changed_binary" >&2
                    exit 1
                }
        else
            awk -F '\t' -v expected="$changed_binary" \
                '$1 == "CHANGED_ALLOWED" && $2 == expected { found=1 } END { exit !found }' \
                "$incremental_binary_diff" || {
                    echo "ERROR: allowlisted binary did not change: $changed_binary" >&2
                    exit 1
                }
        fi
    done
    echo "HTCLEO_INCREMENTAL_BINARY_GUARD_OK parent=$incremental_parent changed=$(grep -c '^CHANGED_ALLOWED' "$incremental_binary_diff" || true)"
fi

# Persist the complete release inputs used by ROMBUILD. Starting with this
# iteration, the next incremental run can restore its parent byte-for-byte
# before rebuilding only the explicit allowlist.
mkdir -p "$incremental_release_cache"
find "$incremental_release_cache" -maxdepth 1 -type f -delete
incremental_cache_manifest="$incremental_release_cache/RELEASE-CACHE-MANIFEST.tsv"
: >"$incremental_cache_manifest"
cache_source_manifest="$incremental_parent_release_manifest"
if [ "$build_mode" = full-clean ]; then
    cache_source_manifest="$work/full-clean-release.sha256"
    find "$build_output" "$output" -maxdepth 2 -type f -name '*-urel.sha256' \
        -exec cat {} \; | \
        awk '$2 ~ /^\/root\/.*\/epoc32\/release\// {print tolower($1) "  " $2}' | \
        sort -u >"$cache_source_manifest"
    test -s "$cache_source_manifest"
fi
while read -r _baseline_hash binary_path
do
    cache_name=$(basename "$binary_path")
    if awk -F '\t' -v name="$cache_name" '$3 == name { found=1 } END { exit !found }' \
        "$incremental_cache_manifest"; then
        echo "ERROR: duplicate incremental cache basename: $cache_name" >&2
        exit 1
    fi
    cp "$binary_path" "$incremental_release_cache/$cache_name"
    current_hash=$(sha256sum "$binary_path" | awk '{print $1}')
    printf '%s\t%s\t%s\n' "$current_hash" "$binary_path" "$cache_name" \
        >>"$incremental_cache_manifest"
done <"$cache_source_manifest"
test "$(wc -l <"$incremental_cache_manifest")" = \
    "$(wc -l <"$cache_source_manifest")"
echo "HTCLEO_INCREMENTAL_RELEASE_CACHE_OK files=$(wc -l <"$incremental_cache_manifest")"

if [ "$build_mode" = full-clean ] || [ "$rebuild_native_bsp" = 1 ]; then
    sh "$project/Symbian/scripts/phase4-build-htcleo-native-bsp.sh" urel
else
    echo "HTCLEO_NATIVE_BSP_REUSED parent=$incremental_parent"
fi

test -s "$default_skin_repository_source"
test -s "$default_skin_repository_transform"
python3 "$default_skin_repository_transform" \
    "$default_skin_repository_source" "$default_skin_repository_output"
python3 "$project/Symbian/scripts/prepare-full-rom-oby.py" \
    "$stem" "$full_epocroot" "$prepared"
python3 "$project/Symbian/scripts/prepare-htcleo-native-full-rom-oby.py" \
    "$prepared" "$recipe"
if [ "$incremental_resource_policy" = gate17-font-settings ] || \
   [ "$incremental_resource_policy" = gate17-catalog-observer ] || \
   [ "$incremental_resource_policy" = gate17-settings-only ] || \
   [ "$incremental_resource_policy" = gate17-layout-ipc-trace ] || \
   [ "$incremental_resource_policy" = gate17-settings-ready-781 ] || \
   [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ] || \
   [ "$incremental_resource_policy" = gate17-matrix-list-release ] || \
   [ "$incremental_resource_policy" = gate17-matrix-system-fade ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ] || \
   [ "$incremental_resource_policy" = gate17-menu-action-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-launch-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-request-frontier ] || \
   [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ] || \
   [ "$incremental_resource_policy" = gate17-menu-software-exception ] || \
   [ "$incremental_resource_policy" = gate17-menu-exception-stack ] || \
   [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ] || \
   [ "$incremental_resource_policy" = gate17-mcs-operation-completion ] || \
   [ "$incremental_resource_policy" = gate17-wserv-find-notfound ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration ] || \
   [ "$incremental_resource_policy" = gate17-hsps-header-cache ] || \
   [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    if [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-list-activation ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-view-transition ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ] || \
   [ "$incremental_resource_policy" = gate17-home-view-event ] || \
   [ "$incremental_resource_policy" = gate17-viewcli-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-queue ] || \
   [ "$incremental_resource_policy" = gate17-vws-client-state ] || \
   [ "$incremental_resource_policy" = gate17-viewsrv-source-control ] || \
   [ "$incremental_resource_policy" = gate17-vws-server-event ] || \
   [ "$incremental_resource_policy" = gate17-vws-session-deactivation ] || \
   [ "$incremental_resource_policy" = gate17-home-kernel-watch ] || \
   [ "$incremental_resource_policy" = gate17-home-background-priority-ab ] || \
   [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ] || \
   [ "$incremental_resource_policy" = gate17-gsapp-black-background ] || \
   [ "$incremental_resource_policy" = gate17-avkon-common-geometry ] || \
   [ "$incremental_resource_policy" = gate17-font-family-binding ] || \
   [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
        # The old entry plan pins stock GSApp. Membership/resources stay805;
        # the GSApp-specific verifier owns the exact single-binary exception.
        cmp -s "$gate17_plan" "$incremental_parent_root/build/GATE17-ENTRY-PLAN.json"
        cp "$incremental_parent_root/build/htcleo_symbian3_full_native.oby" "$recipe"
        # Parent recipe already names the extended SPI. The unchanged common
        # SPI pipeline below expects its pre-extension name and rebuilds the
        # same archive; final recipe/resource equality is still mandatory.
        if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
            retained_filtered_spi="$ecom_spi_dir/no-itype-864/ecom-0-0.spi"
            test "$(grep -F "$retained_filtered_spi" "$recipe" | wc -l)" -eq 1
            sed -i "s|$retained_filtered_spi|$ecom_spi_base|" "$recipe"
        else
            test "$(grep -F "$ecom_spi_extended" "$recipe" | wc -l)" -eq 1
            sed -i "s|$ecom_spi_extended|$ecom_spi_base|" "$recipe"
        fi
    else
    python3 "$project/Symbian/scripts/prepare-htcleo-gate17-entry.py" \
        --sdk "$full_epocroot" \
        --parent "$project/Symbian/output/777-symbian3-full-offline-ip-closure-incremental/Symbian3" \
        --plan "$gate17_plan" --apply-recipe "$recipe"
    fi
fi

if [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
    python3 "$project/Symbian/scripts/prepare-htcleo-about-entry.py" \
        --parent "$incremental_parent_root" --plan "$about_entry_plan" --config "$about_entry_config" --apply-recipe "$recipe"
fi

# The stock STEM ECom SPI is a valid 108-entry archive.  Once it is present,
# ECom intentionally does not scan loose Z:\resource\plugins registrations.
# Extend that archive with every HomeScreen registration absent from the stock
# image, using Nokia's PDK spitool rather than changing the ECom discovery path.
mkdir -p "$ecom_spi_dir"
ecom_spi_resources=
ecom_spi_resource_count=0
while IFS= read -r ecom_spi_resource || [ -n "$ecom_spi_resource" ]
do
    ecom_spi_resource=$(printf '%s' "$ecom_spi_resource" | tr -d '\r')
    case "$ecom_spi_resource" in
        ''|'#'*) continue ;;
        *.rsc) ;;
        *)
            echo "ERROR: invalid HomeScreen ECom SPI resource: $ecom_spi_resource" >&2
            exit 1
            ;;
    esac
    case "$ecom_spi_resource" in
        */*|*\\*|*' '*)
            echo "ERROR: non-basename HomeScreen ECom SPI resource: $ecom_spi_resource" >&2
            exit 1
            ;;
    esac
    ecom_spi_source="$full_epocroot/epoc32/data/z/resource/plugins/$ecom_spi_resource"
    test -s "$ecom_spi_source"
    test "$(grep -F "$ecom_spi_source" "$recipe" | \
        grep -Fi "\"resource\\plugins\\$ecom_spi_resource\"" | wc -l)" -eq 1
    ecom_spi_resources="$ecom_spi_resources $ecom_spi_source"
    ecom_spi_resource_count=$((ecom_spi_resource_count + 1))
done <"$ecom_spi_manifest"
test "$ecom_spi_resource_count" -eq "$ecom_spi_additions"
test "$(grep -v '^[[:space:]]*#' "$ecom_spi_manifest" | \
    sed '/^[[:space:]]*$/d;s/\r$//' | sort -u | wc -l)" -eq "$ecom_spi_additions"
test "$(grep -F "$ecom_spi_base" "$recipe" | wc -l)" -eq 1
# All manifest paths are prevalidated basenames without spaces; intentional
# word splitting passes them as separate spitool input files.
# shellcheck disable=SC2086
python3 "$ecom_spi_perl_compat" "$full_epocroot"
PATH="$native_epocroot/epoc32/tools:$PATH" perl "$ecom_spi_tool" \
    -tecom-0-0.spi -d"$ecom_spi_dir/" -i"$ecom_spi_base" \
    $ecom_spi_resources
test -s "$ecom_spi_extended"
python3 "$ecom_spi_audit" "$ecom_spi_base" "$ecom_spi_extended" \
    "$full_epocroot/epoc32/data/z/resource/plugins" \
    "$ecom_spi_manifest" "$ecom_spi_report" --expected-additions "$ecom_spi_additions"
grep -qx 'STATUS=HTCLEO_HOMESCREEN_ECOM_SPI_OK' "$ecom_spi_report"
grep -qx 'BASE_ENTRIES=108' "$ecom_spi_report"
grep -qx "APPENDED_ENTRIES=$ecom_spi_additions" "$ecom_spi_report"
grep -qx "EXTENDED_ENTRIES=$ecom_spi_total" "$ecom_spi_report"
grep -qx 'STOCK_ENTRIES_BYTE_IDENTICAL=1' "$ecom_spi_report"
grep -qx 'APPENDED_PAYLOADS_BYTE_IDENTICAL=1' "$ecom_spi_report"
sed -i "s|$ecom_spi_base|$ecom_spi_extended|" "$recipe"
! grep -Fq "$ecom_spi_base" "$recipe"
test "$(grep -F "$ecom_spi_extended" "$recipe" | \
    grep -Fi '"private\10009d8f\ecom-0-0.spi"' | wc -l)" -eq 1
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    freetype_spi_filtered="$ecom_spi_dir/no-itype-864/ecom-0-0.spi"
    cp "$ecom_spi_report" "$output/HTCLEO-HOMESCREEN-ECOM-SPI-PREFILTER-863.txt"
    python3 "$project/Symbian/scripts/prepare-htcleo-freetype-spi.py" \
        --input "$ecom_spi_extended" --output "$freetype_spi_filtered" \
        --report "$output/FREETYPE-SPI-FILTER.json" --audit "$ecom_spi_report"
    grep -qx 'EXTENDED_ENTRIES=140' "$ecom_spi_report"
    grep -qx 'RETIRED_NAME=ityperast' "$ecom_spi_report"
    grep -qx 'RETAINED_ENTRY_BYTES_IDENTICAL=1' "$ecom_spi_report"
    sed -i "s|$ecom_spi_extended|$freetype_spi_filtered|" "$recipe"
    test "$(grep -F "$freetype_spi_filtered" "$recipe" | wc -l)" -eq 1
fi
if [ "$incremental_resource_policy" = gate17-catalog-observer ]; then
    python3 "$project/Symbian/scripts/prepare-htcleo-rom-registration-version.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --version-file "$work/htcleo-rom-sw.txt" --apply \
        --report "$output/GATE17-ROM-VERSION-RECIPE.json"
fi

python3 "$homescreen_closure_audit" "$full_epocroot" "$recipe" \
    "$homescreen_closure_report"
grep -qx 'STATUS=HTCLEO_HOMESCREEN_IMPORT_CLOSURE_OK' \
    "$homescreen_closure_report"
grep -qx 'ADD_BINARIES=0' "$homescreen_closure_report"
grep -qx 'UNRESOLVED=0' "$homescreen_closure_report"
test "$(grep -F '/root/symbian3-full/epoc32/data/z/private/10207114/import/200259E6/Symbian.skn' \
    "$recipe" | grep -F '"private\10207114\import\200259e6\symbian.skn"' | wc -l)" -eq 1
for homescreen_destination in \
    'sys\bin\ailaunch.exe' \
    'sys\bin\homescreen.exe' \
    'sys\bin\aiutils.dll' \
    'sys\bin\aiidleint.dll' \
    'sys\bin\aifw.dll' \
    'sys\bin\swiutils.dll' \
    'resource\apps\homescreen.rsc' \
    'resource\apps\homescreen.r01' \
    'resource\apps\homescreen_aif.mif' \
    'private\10003a3f\apps\homescreen_reg.rsc'
do
    test "$(grep -Fi "\"$homescreen_destination\"" "$recipe" | wc -l)" -eq 1
done
test "$(grep -F '/root/symbian3-full/epoc32/data/z/resource/skins/200259E6/Symbian.mbm' \
    "$recipe" | grep -F '"resource\skins\200259e6\symbian.mbm"' | wc -l)" -eq 1
test "$(grep -F '/root/symbian3-full/epoc32/data/z/resource/skins/200259E6/Symbian.mif' \
    "$recipe" | grep -F '"resource\skins\200259e6\symbian.mif"' | wc -l)" -eq 1
test "$(grep -F "$default_skin_repository_output" "$recipe" | \
    grep -F '"private\10202be9\101f876f.txt"' | wc -l)" -eq 1
test "$(grep -F "$wserv_binary" "$recipe" | \
    grep -F '"sys\bin\ewsrv.exe"' | wc -l)" -eq 1
test "$(grep -F "$display_binary" "$recipe" | \
    grep -F '"sys\bin\10286378.dll"' | wc -l)" -eq 1
test "$(grep -F "$wfc_binary" "$recipe" | \
    grep -F '"sys\bin\libwfc.dll"' | wc -l)" -eq 1
test "$(grep -F "$nvg_binary" "$recipe" | \
    grep -F '"sys\bin\nvgrenderstage.dll"' | wc -l)" -eq 1
test "$(grep -F "$nvg_resource" "$recipe" | \
    grep -F '"resource\plugins\nvgrenderstage.rsc"' | wc -l)" -eq 1
test "$(grep -F "$ecom_binary" "$recipe" | \
    grep -F '"sys\bin\ecom.dll"' | wc -l)" -eq 1
test "$(grep -F "$ecom_server_binary" "$recipe" | \
    grep -F '"sys\bin\ecomserver.exe"' | wc -l)" -eq 1
test "$(grep -F "$aknskinsrv_binary" "$recipe" | \
    grep -F '"sys\bin\aknskinsrv.dll"' | wc -l)" -eq 1
test "$(grep -F "$stem_backend_binary" "$recipe" | \
    grep -F '"sys\bin\backend.dll"' | wc -l)" -eq 1
test "$(grep -F "$hitchcock_binary" "$recipe" | \
    grep -F '"sys\bin\hitchcock.dll"' | wc -l)" -eq 1
test "$(grep -F "$akncapserver_binary" "$recipe" | \
    grep -F '"sys\bin\akncapserver.exe"' | wc -l)" -eq 1
test "$(grep -F "$matrixmenu_binary" "$recipe" | \
    grep -F '"sys\bin\matrixmenu.exe"' | wc -l)" -eq 1
test "$(grep -F "$eiksrvc_binary" "$recipe" | \
    grep -F '"sys\bin\eiksrvc.dll"' | wc -l)" -eq 1
test "$(grep -F "$eiksrvs_binary" "$recipe" | \
    grep -F '"sys\bin\eiksrvs.exe"' | wc -l)" -eq 1
test "$(grep -F "$eiksrv_binary" "$recipe" | \
    grep -F '"sys\bin\eiksrv.dll"' | wc -l)" -eq 1
test "$(grep -F "$eiksrvui_binary" "$recipe" | \
    grep -F '"sys\bin\eiksrvui.dll"' | wc -l)" -eq 1
test "$(grep -F "$c32root_binary" "$recipe" | \
    grep -F '"sys\bin\c32root.dll"' | wc -l)" -eq 1
test "$(grep -F "$c32start_binary" "$recipe" | \
    grep -F '"sys\bin\c32start.exe"' | wc -l)" -eq 1
test "$(grep -F "$eikcore_binary" "$recipe" | \
    grep -F '"sys\bin\eikcore.dll"' | wc -l)" -eq 1
test "$(grep -F "$featmgr_binary" "$recipe" | \
    grep -F '"sys\bin\featmgr.dll"' | wc -l)" -eq 1
test "$(grep -F "$featmgrserver_binary" "$recipe" | \
    grep -F '"sys\bin\featmgrserver.exe"' | wc -l)" -eq 1
test "$(grep -F "$apparc_aplist_binary" "$recipe" | \
    grep -F '"sys\bin\aplist.dll"' | wc -l)" -eq 1
test "$(grep -F "$apparc_apserv_binary" "$recipe" | \
    grep -F '"sys\bin\apserv.dll"' | wc -l)" -eq 1
test "$(grep -F "$apparc_apsexe_binary" "$recipe" | \
    grep -F '"sys\bin\apsexe.exe"' | wc -l)" -eq 1
test "$(grep -F "$apparc_launch_binary" "$recipe" | \
    grep -F '"sys\bin\akncapserverclient.dll"' | wc -l)" -eq 1
test "$(grep -F "$ssm_custom_binary" "$recipe" | \
    grep -F '"sys\bin\ssmcmd.dll"' | wc -l)" -eq 1
test "$(grep -F "$akn_custom_binary" "$recipe" | \
    grep -F '"sys\bin\akncustcmds.dll"' | wc -l)" -eq 1
test "$(grep -F "$native_epocroot/epoc32/release/armv5/urel/efile.exe" "$recipe" | \
    grep -F '"sys\bin\efile.exe"' | wc -l)" -eq 1
test "$(grep -F 'extension[0x0c0b0001]=' "$recipe" | \
    grep -F '/root/symbian/epoc32/release/armv5/urel/_htcleo_epointer.dll' | \
    grep -F '"sys\bin\epointer.dll"' | wc -l)" -eq 1
test "$(grep -F 'device[0x0c0b0001]=' "$recipe" | \
    grep -F '/root/symbian/epoc32/release/armv5/urel/_htcleo_medint.pdd' | \
    grep -F '"sys\bin\medint.pdd"' | wc -l)" -eq 1
test "$(grep -F 'device[0x0c0b0001]=' "$recipe" | \
    grep -F '/root/symbian/epoc32/release/armv5/urel/_htcleo_ekeyb.dll' | \
    grep -F '"sys\bin\ekeyb.dll"' | wc -l)" -eq 1
python3 "$loader_log_map_tool" --target akncustcmds.dll \
    --log-file AKNLDR.TXT "$recipe" "$loader_log_map"
grep -qx 'STATUS=HTCLEO_LOADER_LOG_MAP_OK' "$loader_log_map"
grep -qx 'TRACE_GATE=top-level-akncustcmds.dll-ELoadLibrary-only' "$loader_log_map"
grep -Fqx 'LOG_PATH=C:\Symbian3\AKNLDR.TXT' "$loader_log_map"

if [ "$incremental_resource_policy" = disable-offline-ip-closure ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-offline-network-bypass.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --report "$output/OFFLINE-NETWORK-BYPASS-RECIPE.json"
fi
if [ "$incremental_resource_policy" = gate17-font-settings ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-gate17-entry.py" \
        --sdk "$full_epocroot" --parent "$incremental_parent_root" \
        --plan "$gate17_plan" --recipe "$recipe" --report "$output/GATE17-ENTRY-RECIPE.json"
fi

rm -f "$work/htcleo_symbian3_full_native.img" \
    "$work/htcleo_symbian3_full_native.log" \
    "$work/htcleo_symbian3_full_native.symbol" \
    "$work/htcleo_symbian3_full_native.dir"

set +e
(cd "$work" && "$rombuild" -no-header -type-safe-link -symbols -S -v \
    "$(basename "$recipe")" >"$log" 2>&1)
rc=$?
set -e

tail -120 "$log"
if [ "$rc" -ne 0 ]; then
    exit "$rc"
fi

test -s "$image"
if [ "$incremental_resource_policy" = disable-offline-ip-closure ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-offline-network-bypass.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" \
        --report "$output/OFFLINE-NETWORK-BYPASS-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-font-settings ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-gate17-entry.py" \
        --sdk "$full_epocroot" --parent "$incremental_parent_root" --plan "$gate17_plan" \
        --recipe "$recipe" --image "$image" --rom-log "$log" \
        --report "$output/GATE17-ENTRY-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-catalog-observer ]; then
    python3 "$project/Symbian/scripts/prepare-htcleo-rom-registration-version.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --version-file "$work/htcleo-rom-sw.txt" --image "$image" --rom-log "$log" \
        --report "$output/GATE17-ROM-VERSION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-settings-only ] || \
   [ "$incremental_resource_policy" = gate17-settings-ready-781 ] || \
   [ "$incremental_resource_policy" = gate17-settings-direct-registration ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-g17-settings.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/G17-SETTINGS-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-layout-ipc-trace ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-packed-layout-trace.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/PACKED-LAYOUT-TRACE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-action-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-action --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MCS-ACTION-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-launch-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-launch --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-LAUNCH-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-attribute-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-attribute --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-ATTRIBUTE-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-request-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-request --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-REQUEST-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-server-exit-watch ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-server-exit --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-SERVER-EXIT-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-software-exception ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-software-exception --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-SOFTWARE-EXCEPTION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-exception-stack ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-exception-stack --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-EXCEPTION-STACK-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-mcs-notifier-stop ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-notifier-stop --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-NOTIFIER-STOP-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-task-lookup-control ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-task-lookup-control --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-TASK-LOOKUP-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-mcs-operation-completion ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-operation-completion --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-OPERATION-COMPLETION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-wserv-find-notfound ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile wserv-find-notfound --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/WSERV-FIND-NOTFOUND-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-task-enumeration ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-task-enumeration --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-TASK-ENUMERATION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-hsps-header-cache ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile hsps-header-cache --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/HSPS-HEADER-CACHE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-menu-task-enumeration-on804 ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile menu-task-enumeration-804 --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MENU-TASK-ENUMERATION-804-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-startup-observer ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-startup --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-STARTUP-OBSERVER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-eikstart-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-eikstart --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-EIKSTART-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-env-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-env --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-ENV-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-aknenv-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-aknenv --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-AKNENV-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-local-layout ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-sgc-local --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-SGC-LOCAL-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-appui-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-appui --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-APPUI-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-focus-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-focus --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-FOCUS-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-params-local ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-sgc-params --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-SGC-PARAMS-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-sgc-fade-local ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-sgc-fade --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-SGC-FADE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-keyblock-local ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-keyblock --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-KEYBLOCK-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-home-background-priority-ab ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile home-priority-ab --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/HOME-PRIORITY-AB-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-home-kernel-watch ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile home-kernel-watch --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/HOME-KERNEL-WATCH-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-vws-session-deactivation ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile vws-session-deactivation --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VWS-SESSION-DEACTIVATION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-vws-server-event ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile vws-server-event --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VWS-SERVER-EVENT-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-viewsrv-source-control ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile viewsrv-control --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VIEWSRV-SOURCE-CONTROL-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-vws-client-state ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile vws-client-state --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VWS-CLIENT-STATE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-vws-client-queue ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile vws-client-queue --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VWS-CLIENT-QUEUE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-viewcli-source-control ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile viewcli-control --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/VIEWCLI-SOURCE-CONTROL-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-home-view-event ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile home-view-event --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/HOME-VIEW-EVENT-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-cone-view-event ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-cone-event --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-CONE-EVENT-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-view-transition ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-transition --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-TRANSITION-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-async-view-event ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-async --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-ASYNC-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-list-activation ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-list --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-LIST-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-child-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-child --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-CHILD-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-create-retry ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-create --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-CREATE-RETRY-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-ecom-notify-guard ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-notify --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-NOTIFY-ROM.json"
fi

if [ "$incremental_resource_policy" = gate17-gsapp-exception-witness ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-exception --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-EXCEPTION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-lifetime-observer ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-lifetime --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-LIFETIME-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-redraw-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-redraw --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-REDRAW-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-plugin-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-plugin --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-PLUGIN-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-activation-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-activation --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-ACTIVATION-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-view-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-view --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-VIEW-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-eikbase-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-eikbase --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-EIKBASE-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-appinfo-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-appinfo --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-APPINFO-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-gsapp-statuspane-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile gsapp-statuspane --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/GSAPP-STATUSPANE-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-matrix-pointer-frontier ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MATRIX-POINTER-FRONTIER-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-matrix-list-release ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile list-release --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MATRIX-LIST-RELEASE-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-matrix-system-fade ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-matrix-pointer-frontier.py" \
        --profile matrix-fade --parent "$incremental_parent_root" --recipe "$recipe" \
        --image "$image" --rom-log "$log" --report "$output/MATRIX-SYSTEM-FADE-ROM.json"
fi
python3 "$rom_space_audit" "$recipe" --image "$image" \
    --window 0x03a00000 >"$rom_space_report"
cat "$rom_space_report"
grep -qx 'ROM_WINDOW=60817408' "$rom_space_report"
grep -q '^ROM_REMAINING=[0-9][0-9]*$' "$rom_space_report"
python3 "$project/Symbian/scripts/create-htcleo-probe-map.py" \
    "$native_epocroot/epoc32/tools/elf2e32" \
    "$native_epocroot/epoc32/release/armv5/urel/e32strt.exe" \
    "$native_epocroot/epoc32/release/armv5/urel/efile.exe" \
    "$native_epocroot/epoc32/release/armv5/urel/elocd.ldd" \
    "$native_epocroot/epoc32/release/armv5/urel/medmmc.pdd" \
    "$native_epocroot/epoc32/release/armv5/urel/efat32.fsy" \
    "$native_epocroot/epoc32/release/armv5/urel/epbussd.dll" \
    "$native_epocroot/epoc32/release/armv5/urel/_htcleo_epbussdiov.dll" \
    "$log" "$recipe" "$probe_map"
cp "$image" "$build_output/htcleo_symbian3_full_native.img"
cp "$recipe" "$build_output/htcleo_symbian3_full_native.oby"
cp "$recipe.removed" "$build_output/htcleo_symbian3_full_native.oby.removed"
cp "$recipe.product-profile.json" \
    "$build_output/htcleo_symbian3_full_native.oby.product-profile.json"
cp "$probe_map" "$build_output/HTCLEO-PROBE-MAP.txt"
cp "$loader_log_map" "$build_output/HTCLEO-LOADER-LOG-MAP.txt"
cp "$rom_space_report" "$build_output/HTCLEO-ROM-SPACE-AUDIT.txt"
cp "$homescreen_closure_report" \
    "$build_output/HOMESCREEN-CLOSURE-AUDIT.txt"
cp "$ecom_spi_extended" "$build_output/ecom-0-0-homescreen-extended.spi"
cp "$ecom_spi_report" \
    "$build_output/HTCLEO-HOMESCREEN-ECOM-SPI-AUDIT.txt"
cp "$prepared.omitted" "$build_output/full-prepared.oby.omitted"
cp "$prepared.fallbacks.tsv" "$build_output/full-prepared.oby.fallbacks.tsv"
cp "$prepared.patchdata-skipped" "$build_output/full-prepared.oby.patchdata-skipped"
for sidecar in \
    "$work/htcleo_symbian3_full_native.log" \
    "$work/htcleo_symbian3_full_native.symbol" \
    "$work/htcleo_symbian3_full_native.dir"
do
    if [ -f "$sidecar" ]; then
        cp "$sidecar" "$build_output/"
    fi
done

size=$(wc -c <"$image")
window=$(( (size + 1048575) / 1048576 * 1048576 ))
ram_start=$((0x12200000 + window))
test "$window" -eq $((0x03a00000))
test "$ram_start" -eq $((0x15c00000))
hash=$(sha256sum "$image" | awk '{print $1}')
cat >"$output/BUILD-RESULT.txt" <<EOF
STATUS=HTCLEO_NATIVE_FULL_ROM_OK
BUILD_MODE=$build_mode
INCREMENTAL_PARENT=$incremental_parent
INCREMENTAL_CHANGED_BINARIES=$incremental_changed_binaries
INCREMENTAL_RESOURCE_POLICY=$incremental_resource_policy
HTCLEO_BLUETOOTH_POLICY=esock-bt-cmi-and-esk-suppressed
HTCLEO_OFFLINE_NETWORK_POLICY=esock-dip-ip-sip-startup-and-protocols-suppressed
HTCLEO_FINAL_ACCEPTANCE=offline-java-gate18-retired-gate20-optional
INCREMENTAL_MIGRATION=$incremental_migration
INCREMENTAL_NATIVE_BSP_REBUILT=$rebuild_native_bsp
IMAGE=$build_output/htcleo_symbian3_full_native.img
SIZE=$size
SHA256=$hash
ROM_LINEAR_BASE=0x12200000
ROM_WINDOW=$(printf '0x%08x' "$window")
RAM_START=$(printf '0x%08x' "$ram_start")
VARID=0x0c0b0001
KERNEL_LIBRARY_ATTACH_PROGRESS=6-bootstrap-plus-10-stage-notify-flush-ack
ECOM_ATTACH_WATCHER=blocked-bootstrap-and-attach-no-polling
ECOM_EXEC_STUB=thumb-entry-arm-swi-interworking
ECOM_FEATMGR_LIST_TRACE=F200-F24D-sid-10205054-interface-10205057
ECOM_SERVER_FEATMGR_LIST_TRACE=F300-F400-exact-arm-interface-10205057-romonly-resolver-10009D92
ECOM_SERVER_REGISTRY_LIST_TRACE=F3E0-F400
ECOM_FEATUREINFO_EMPTY_LIST_COMPAT=interface-10205057-notfound-to-empty
HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY=sid-101f4cd2-keerrserverterminated-reconnect-once-310-314
HTCLEO_ECOM_MATRIXMENU_LIST_RETRY=sid-101f4cd2-reconnect-once-terminated-to-empty-315-31a
HTCLEO_ECOM_HOMESCREEN_LIST_RETRY=sid-102750f0-interface-200286df-one-reconnect-then-empty
HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY=sid-102750f0-interface-20019592-type-action-one-reconnect-then-empty
HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY=sid-102750f0-interface-20019592-types-actions-action-event
HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY=sid-102750f0-interface-20019592-type-menubar-one-reconnect-failclosed
HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY=sid-102750f0-interface-20019592-all-types-one-reconnect-visual-failclosed
HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY=sid-102750f0-shared-one-reconnect-no-normalization
HTCLEO_ECOM_HOMESCREEN_SERVER_TRACE=service6-impl2001952c-session-server-registry-f500-f539
HTCLEO_ECOM_HSPS_DEFINITION_RESOLVE=interface200159c7-to-real-impl200159c8-security-checked
HTCLEO_ECOM_HSPS_PERSISTENT_TRACE=HSPSECOM-1m-f600-f628-append-across-server-restart
HTCLEO_ECOM_HSPS_RESPONSE_TRACE=HSPSECOM-f603-f60f-f617-f631-f634-f640-f642
HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE=HSPSECOM-hcli-c700-c707-c710-c71d-c720-c729-c730-c738
PTIENGINE=source-built-frozen-1-475-plus-reviewed-476
HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK=itut01-10281897-trapped-final-no-fep-gate17
ECOM_SERVER_DURABLE_LOG=ECOMSRV.TXT-capacity-737280-bytes-16384x45-replace-on-exact-request
HTCLEO_HOMESCREEN_ECOM_SPI=stock-108-minus-ityperast-plus-33-140-total-spitool-filter
HTCLEO_HOMESCREEN_ECOM_SPI_AUDIT=all-other-entry-bytes-identical-only-ityperast-retired
STEM_BACKEND=source-built-frozen-176-export-abi
STEM_BACKEND_CONSTRUCTOR_LOG=D101-D124
STEM_BACKEND_TIMEZONE_POLICY=defer-notfound-or-serverterminated
HITCHCOCK=source-built-frozen-prefix-2011
HITCHCOCK_ENTRYPOINT_LOG=CC00-CC05-export-table-static-initializer
AKNCAPSERVER=source-built-uid-10207218
AKNCAPSERVER_STARTUP_LOG=E000-E21B-isolated-eikstart-registration-repair-property-ready-and-lifecycle
AKNCAPSERVER_RENDEZVOUS_COMPAT=explicit-post-construct-ready-signal-no-wait-no-timer
AKNCAPSERVER_PROPERTY_READY=key-7f044302-post-construct-value-1-registered-2-missing
AKNCAPSERVER_OFN_POLICY=htcleo-no-optical-navigation-skip-e102-4f464e00
AKNCAPSERVER_POSTCRITICAL_FILELOG=retired-after-e100-evidence-4e4f494f-no-startup-change
AKNCAPSERVER_POSTCRITICAL_TRACE=property-only-stage16-result16-key-7f044301-no-fat-io
AKNCAPSERVER_E100_RETIREMENT=prearmed-before-e100-property-only-no-fat-io
AKNCAPSERVER_CRITICALITY_POLICY=htcleo-ui-first-skip-thread-system-critical
AKNCAPSERVER_NONLEO_STARTUP_POLICY=skip-product-hal-mmc-password-with-ipc-guard-discreet-popup-alternatefs-ecom-slider-flip-hwrm-slide-builtin-fsw-retained
AKNCAPSERVER_REGISTRATION_LIFETIME=exact-name-self-check-single-reregister-retained-breadcrumb
AKNCAPLOG_CAPACITY=512
EIKSRVC=source-built-uid-100053B1
EIKSRVC_CONNECT_LOG=EIKCONN.TXT-E900-E951-akncap-sid-gated
EIKSRVC_RENDEZVOUS_COMPAT=hardware-ready-restore-stock-wait-no-cancel-no-ntimer
EIKSRVC_READY_RETRY=akncap-only-single-child-64-compact-one-flush-polls-no-timer
EIKCONNLOG_CAPACITY=512
EIKSRVS=source-built-uid-10003A4A
EIKSRVS_STARTUP_LOG=E700-E710-rendezvous-boundary
EIKSRV=source-built-uid-10003A4A
EIKSRV_SERVER_CONSTRUCT_LOG=E720-E757-newl-constructl
EIKSRVLOG_CAPACITY=128
EIKSRVUI=source-built-stem-uid-100053D0
EIKSRVUI_CONSTRUCT_LOG=E776-E79B-frontier-only
EIKSRVUI_INITIALIZE_LOG=E7DC-E7E2-frontier-only
EIKSRVUI_LOG_FLUSH_POLICY=write-close-no-explicit-flush-after-e7db-proof
EIKSRVUI_LOG_SCOPE_POLICY=frontier-only-e7dc-e7e2-and-e776-e79b-after-e7db-hardware-pass
C32_STARTUP_LOG=C32ROOT.TXT-C700-C719-and-C32START.TXT-C800-C879
EIKSRVUI_C32_POLICY=ui-first-fail-open-e7d8-keerrnotsupported-normalized
C32_STARTUP_POLICY=trace-retained-not-invoked-by-eiksrvui
EIKSRVUI_NOTIFY_ALERT_POLICY=ui-first-null-alert-factory-e774-a17f0001
EIKSRVUI_NOTIFIER_SERVER_POLICY=ui-first-defer-newl-and-idle-start-e7dc-e7df-4e465953
EIKSRVUI_OPTIONAL_TAIL_POLICY=ui-first-defer-external-key-keysound-animation-default-sounds-bitmap-cursors
EIKSRVUI_CONSTRUCT_ENTRY_LOG=E7A0-E7F0-E7F4-E7A1-behavior-unchanged
EIKSRVUI_SYSTEM_ATTRIBUTE_POLICY=ui-first-defer-task-end-protection-e7f3-53595301
EIKSRVUI_BASECONSTRUCT_RESULT=E7A3-trap-result-releave-detail-42415345
AKNAPPUI_BASECONSTRUCT_LOG=AKNBASE.TXT-B51C-B520-eiksrv-sid-only-frontier
HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE=HSXML-1m-B500-B520-behavior-neutral
HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_POLICY=diagnostic-only-no-result-branch-timer-layout-or-leave-change
HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE=HSXML-1m-B530-B547-C500-C52C-behavior-neutral
HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_POLICY=diagnostic-only-no-result-branch-timer-layout-sgc-or-leave-change
HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS=fixed-panel-deferred-keerrnotsupported-C529-C52C
HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_POLICY=home-eiksrv-matrixmenu-only-real-ipc-retained-for-other-sids-no-fake-success
AKNAPPUI_SCREEN_CHANGE_POLICY=eiksrv-only-fixed-screen-ui-first-skip-b503-5343524e
AKNAPPUI_SCREEN_SIZE_POLICY=eiksrv-only-fixed-480x800-ui-first-b504-53495a45-b505-01e0-0320
AKNAPPUI_TACTILE_FEEDBACK_POLICY=eiksrv-only-defer-optional-haptics-b506-48415054-b507-null
AKNAPPUI_POSTCOE_LAYOUT_LOG=retired-after-483-hardware-proof
AKNENV_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA000-4D4DA01A
AKNENV_MATRIXMENU_CDL_RECOVERY=notfound-or-terminated-recreate-engine-once
HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT=HSXML-1m-A000-A01E-home-and-matrixmenu-notfound-or-terminated
HTCLEO_AKNENV_HOMESCREEN_POLICY=real-cdl-engine-recreate-once-preserve-other-errors
AKNSGC_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA100-A107-A110-A115-A120-A132
AKNSGC_MATRIXMENU_AKNCAP_POLICY=matrixmenu-only-notfound-or-terminated-fail-open-local-layout-no-fake-handle
HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN=HSXML-1m-A100-A133-real-null-handle-local-layout
HTCLEO_AKNSGC_HOMESCREEN_POLICY=home-and-matrixmenu-notfound-or-terminated-local-layout-no-fake-handle
HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_TRACE=HSXML-1m-C560-C56E-transition-base-keyblock-effects
HTCLEO_AKNSGC_HOMESCREEN_KEYBLOCK_POLICY=handle0-skip-C570-C576-no-fake-session
HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE=HSXML-C560-C59F-enabled-existing-1m
HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE=HSXML-C580-C593-view-C598-C59E-behavior-neutral
HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_HANDLE_COMPAT=handle0-local-state-C577-C57F-real-session-stock
HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_POLICY=home-only-no-session-local-flag-real-session-stock
AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA200-A205-A210-A21C
AKNUI_CONNECT_MATRIXMENU_RETRY_POLICY=one-real-attempt-per-call-discovery-and-fixed-name-retained-no-timer
AKNUI_CONNECT_MATRIXMENU_READY_WAIT=property-subscribe-inflight-child-no-ntimer-bounded-retry-retained
AKNUI_CONNECT_REGISTERED_SERVER=uid-10207218-kernel-name-discovery-bounded-16-fixed-name-fallback
AKNAPPUI_POSTCOE_SCREEN_SIZE_POLICY=eiksrv-only-fixed-480x800-ui-first-b533-46495832
AKNAPPUI_MATRIXMENU_POSTCOE_SCREEN_POLICY=fixed-480x800-b533-b534
AKNAPPUI_SGC_FOREGROUND_POLICY=eiksrv-only-defer-false-c51c-46475244-c51d-0
AKNAPPUI_SGC_PARAMS_POLICY=eiksrv-only-defer-c529-53474350-c52a-keerrnotsupported
AKNAPPUI_MATRIXMENU_SGC_PARAMS_POLICY=defer-c529-c52a-keerrnotsupported
AKNAPPUI_TRANSITION_EFFECTS_POLICY=eiksrv-only-defer-b51b-54524e46-b51e-54524e53
AKNAPPUI_LOG_FLUSH_POLICY=write-close-no-explicit-flush-after-b51a-proof
AKNAPPUI_LOG_SCOPE_POLICY=frontier-only-b51c-b520-after-b51b-hardware-pass
AKNAPPUI_MATRIXMENU_UI_FIRST_POLICY=fixed-480x800-no-screen-change-no-haptics-no-transitions-no-dialler-b500-b520-log
HTCLEO_AKNGRID_CPU_BACKGROUND_PRESERVE=matrixmenu-skip-broken-nvg-unused-area-redraw
MATRIXMENU_INITIAL_STATUSLAYOUT_POLICY=ui-first-defer-startup-usual-layout-0307-53504c59-runtime-switches-retained
MATRIXMENU_DUMMY_GRID_TRACE=retired-after-526-createwindowl-proof
MATRIXMENU_DUMMY_CONTAINER_POLICY=ui-first-null-transition-placeholder-0309-030a-44554d59-main-container-retained
MATRIXMENU_HNENGINE_TRACE=trap-log-releave-030b-no-normalization
MMWIDGETS_DUMMY_GRID_LOG=MMWLOG.TXT-4D570100-4D570168-close-only-matrixmenu
MMWIDGETS_LOG_CAPACITY=1048576-bytes
MMWIDGETS_DEFERRED_AO_TRACE=postprocess-200-215-drawer-220-22f
MMWIDGETS_POSTPROCESS_POLICY=queue-only-real-index-range-stage-216
HNENGINE_CONSTRUCTOR_LOG=HNLOG.TXT-484E0100-484E0128-close-only-matrixmenu
HNENGINE_INITIALIZE_LOG=HNLOG.TXT-484E0200-484E0225-close-only-behavior-unchanged
HNMETADATA_CONSTRUCTOR_LOG=MDLOG.TXT-4D440100-4D44012D-close-only-matrixmenu
HNMETADATA_EVALUATION_LOG=MDLOG.TXT-4D440200-4D44045A-close-only-behavior-unchanged
HNMETADATA_LOG_CAPACITY=1048576-bytes-four-loggers-trace-only
HNMETADATA_SHOWFOLDER_POLICY=ui-first-defer-cenrep-observer-12c-53464f4c
HNMETADATA_NOTIFY_POLICY=matrixmenu-reconnect-once-ready-gated-stock-first-query-no-duplicate-callback-500-514
HNMETADATA_NOTIFY_LIFETIME_TRACE=50a-50c-plus-513-514-callback-object-not-created
HNMETADATA_REDUNDANT_ASYNC_REFRESH=retired-after-ready-property-stock-first-query-proven
MCSMENU=source-built-uid-200113db-exports-82
MCSMENU_UI_FIRST_POLICY=core-menu-apparc-cache-getlist-native-java-retained-persistent-engine-lifetime-nokia-dynamic-services-deferred
MCSMENU_DURABLE_LOG=MCSLOG.TXT-4D430100-4D430135-close-only-server
MCSMENU_APPARC_POLICY=ui-first-scanner-restored-async-queue-notify-requery-reconnect-failopen-128-130
MCSMENU_CORE=source-built-uid-200113dc-exports-35
MCSMENU_CORE_ENGINE_LOG=MCSLOG.TXT-4D450100-4D450515-close-only-behavior-unchanged
MCSMENU_RAM_FALLBACK_POLICY=missing-c-cache-to-real-rom-520-522-524f4d46
MCSMENU_FIRST_CHANGE_POLICY=ram-only-first-changed-operation-notify-flush-530-531
MCSMENU_SERVER_CONTEXT_TRACE=142-150-process-thread-lookup-error-dtor
HTCLEO_MCS_SERVER_LIFETIME=process-persistent-engine-expiry-retained-151-152
MCSMENU_SCANNER_OPTIONAL_CONSTRUCT=160-164-narrow-failopen
MCSMENU_APPARC_BOUNDED_RETRY=165-167-12x250ms-real-scan
MCSMENU_APPARC_RETURNED_RETRY=return-status-before-mutation
MCSMENU_APPARC_SERVER_RESTART=168-16B-apsexe-rendezvous
MCSMENU_HN_READY_GENERATION=menueng-commit-532
MCSMENU_HN_READY_SIGNAL=matrixmenu-owned-alwayspass-commit-generation-query-retry-no-timer
HNMETADATA_QUERY_RETRY=empty-or-transient-once-after-next-commit-460-464
HNMETADATA_GETLIST_EXECUTION=matrixmenu-async-liw-provider-sync-pump-465
HNMETADATA_SYNC_COMPLETION=superseded-by-direct-safe-tail
HNMETADATA_SYNC_RESULT=direct-runl-safe-caller-and-retry-tail-460-466
HTCLEO_HN_SYNC_COMPLETION_SIGNAL=owned-completed-status-wait-before-direct-runl
HNMETADATA_READY_REQUEST_GUARD=no-success-skip-511-success-generation-wait
HNMETADATA_RESULTS_CONSUMPTION_TRACE=query-467-46c-item-470-49a-apparc-ready-gated-bounded-real-count-empty-suite-suppressed
MCSSERVICE=source-built-uid-2001242b-exports-34
MCSSERVICE_GETLIST_SYNC_PUMP=matrixmenu-real-ipc-per-item-icon-failopen-outer-error-raw-result-preserve-sync-result-property-safe-tail
HTCLEO_MCS_NOTIFICATION_CONTRACT=positive-mask-terminal-negative-safe-callback-tail-MCN-1m
MCSMENU_GETLIST_SERVER_COUNT=real-output-list-property-7f4d4302-hn-bounded-30
MCSMENU_GETLIST_SESSION_BUFFER=all-session-size-data-snapshot-real-payload-traced-170-175
MCSMENU_GETLIST_ATOMIC_TRANSFER=matrixmenu-size-plus-real-data-one-ipc-bounded-64k-traced-176-179
AKNSKINSRV=source-built-uid-10005A35
AKNSKINSRV_DURABLE_LOG=SKINLOG.TXT-A800-D8B8-restore-default-settings-boot-drm-defer
AKNSKINLOG_CAPACITY=256
EIKCORE=source-built-frozen-1-594-plus-gcce-595-604
HTCLEO_EIKSTART_HOMESCREEN_TRACE=HSXML-1m-sid-102750f0-commandline-rename-env-factory-execute-48590000-48590012
HTCLEO_EIKSTART_HOMESCREEN_POLICY=diagnostic-only-no-commandline-fallback-no-result-normalization
HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE=HSXML-1m-sid-102750f0-existing-E300-E36A
HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_POLICY=diagnostic-only-no-branch-result-or-timing-change
EIKCOCTL=source-built-stock-abi
EIKCOCTL_MATRIXMENU_APPINFO_LOG=EIKBASE.TXT-B620-B631-close-only
HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_TRACE=HSXML-1m-B620-B631-behavior-neutral
HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_POLICY=diagnostic-only-no-resource-control-wserv-sgc-result-or-leave-change
EIKCOCTL_MATRIXMENU_STATUSPANE_LOG=EIKBASE.TXT-B640-B67B-close-only
EIKCOCTL_MATRIXMENU_STATUSMODEL_LOG=EIKBASE.TXT-B690-B6AC-close-only
HTCLEO_EIKCOCTL_HOMESCREEN_STATUS_TRACE=HSXML-1m-HSP-B640-B713-HSM-B690-B6F5-behavior-neutral
HTCLEO_EIKCOCTL_HOMESCREEN_STATUS_POLICY=diagnostic-only-no-layout-control-wserv-sgc-result-or-leave-change
EIKCOCTL_MATRIXMENU_STATUSLAYOUT_LOG=EIKBASE.TXT-B6B0-B6DB-close-only
EIKCOCTL_MATRIXMENU_STATUSTREE_LAYOUT_LOG=EIKBASE.TXT-B6E0-B6F5-close-only
EIKCOCTL_MATRIXMENU_COMBINED_VISIBILITY_LOG=EIKBASE.TXT-B700-B70D-close-only
EIKCOCTL_MATRIXMENU_FADE_POLICY=handle-zero-not-faded-valid-session-stock-b70e-b70f
HTCLEO_EIKCOCTL_HOMESCREEN_FADE_POLICY=invalid-aknsrv-handle-not-faded-b70e-b70f-valid-session-stock
HTCLEO_MATRIXMENU_CLIENTRECT_SCALE=matrixmenu-direct-logical-360x640-to-480x800-b710-b711
HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE=matrix-contract-client-status-cba-360x640-to-480x800
HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_POLICY=no-applicationrect-800-override-real-cba-final-redraw
HTCLEO_MATRIXMENU_STATUSPANE_SCALE=subpane-logical-360x640-to-480x800-b712-b713
HTCLEO_MATRIXMENU_CBA_INNER_REDRAW=screen-bounding-scale-and-existing-drawnow-matrixmenu-only
HTCLEO_MATRIXMENU_CBA_WRAPPER_REDRAW=actual-window-invalidate-fullrect-drawnow-matrixmenu-only
EIKCOCTL_EIKBASE_CAPACITY=512
EIKCOCTL_STATUSPANE_LEAVE_POLICY=log-and-releave-no-normalization
EIKCORE_PREFACTORY_TRACE=E300-E311-plus-E312-E31E-akncap-sid-gated-property
EIKCORE_POSTPROCESS_GAP_TRACE=E312-E31E-property-only-behavior-unchanged
EIKCORE_BACKGROUND_PRIORITY_POLICY=akncap-only-defer-before-ready-e31b-e31c-stock-other-sids
EIKCORE_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DE300-E311-and-4D4DE400-E425
EIKCORE_CONSTRUCTL_TRACE=E400-E425-akncap-sid-gated-property
EIKCORE_POSTAPPUI_TRACE=E320-E341-sync-E350-E357-async-matrixmenu-durable-behavior-unchanged
EIKCORE_MATRIXMENU_TASKNAME_POLICY=defer-second-refresh-only-if-empty-e342-keerrnotsupported-other-apps-stock
EIKCORE_MATRIXMENU_APPREADY_POLICY=local-ready-retained-late-wserv-publish-deferred-e343-e346-other-apps-stock
EIKCORE_MATRIXMENU_STARTUP_VIEW_AO=pending-setactive-complete-e360-e364-other-apps-stock
EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY=310-one-shot-e365-other-apps-160-stock
EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW=retired-after-real-container-e366-e368-async-other-apps-stock
EIKCORE_MATRIXMENU_VIEW_INIT=retired-empty-avkon-view-e369-e36a-other-apps-stock
STEM_CONE_REDRAW_QUEUE=matrixmenu-pending-setactive-redrawready-other-apps-stock
CONE_EVENT_PUMP_LOG=CONELOG.TXT-1m-scheduler-event-redraw-flush-0100-0403
CONE_READY_AO_TRACE=object-vtable-priority-status-ao100-aof
HTCLEO_CONE_HOMESCREEN_AO_TRACE=HSCONE-1m-scheduler-event-redraw-ready-ao-vtable
HTCLEO_CONE_HOMESCREEN_AO_POLICY=diagnostic-only-sid102750f0-no-dispatch-timing-change
HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE=HSCONE-1m-0500-050f-observers-0520-0524-behavior-neutral
HTCLEO_CONE_HOMESCREEN_FOREGROUND_POLICY=diagnostic-only-no-observer-virtual-focus-branch-or-result-change
HTCLEO_LIW_ECOM_MONITOR_POLICY=negative-notify-retire-success-sync-rearm
EIKAPPUI_BASECONSTRUCT_LOG=EIKBASE.TXT-B600-B615-eiksrv-matrixmenu-close-only
HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE=HSXML-1m-B600-B615-behavior-neutral
HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_POLICY=diagnostic-only-no-result-branch-timer-screen-or-leave-change
HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_TRACE=HSXML-E370-E379-fade-E380-E387-behavior-neutral
HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_POLICY=diagnostic-only-no-focus-fade-resource-stack-window-cursor-result-change
EIKAPPUI_MATRIXMENU_SCREEN_CHANGE_POLICY=defer-final-duplicate-b614-b615-keerrnotsupported
FEATMGR=source-built-frozen-58-export-abi
FEATMGR_AKNCAP_TRACE=E500-E548-akncap-sid-gated-property
FEATMGRSERVER=source-built-registry-before-first-use
FEATMGRSERVER_TRACE=E600-E64F-server-sid-property-deepest-stage-preserved
FEATMGRSERVER_LOADPLUGINS_TRACE=E640-E64F
FEATMGRSERVER_ZERO_PLUGIN_COMPAT=no-interface-to-empty-list
FEATMGRSERVER_UNWIND=E603-fallback-only
WSLOG_CAPACITY=1048576-bytes-ring-128-byte-records
HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT=5s-continuous-0477-request-0462-0465-counters-1m-ring
HTCLEO_HSPSPROVIDER_LOG_RETIREMENT=nonempty-completion-only-no-map-change
HTCLEO_XN_HD2_CLIENT_GEOMETRY=native-panel-contract-no-per-property-ipc-real-cba-inset-first-view-focus
HTCLEO_XN_CLIENT_WINDOW_COMMIT=owning-view-and-background-client-bounds-cached-grass-wallpaper
HTCLEO_HOME_MSK_CENTER=physical480-center-image-and-hit-normal-home-menu-rsk
HTCLEO_HOME_MENU_ARRAY=heap-cbase-zero-init-cleanupstack-no-stack-array
HTCLEO_HOME_MENU_HANDOFF=$home_menu_handoff_policy
HTCLEO_HOME_BACKGROUND_PRIORITY_AB=$home_background_priority_ab_policy
HTCLEO_ABOUT_ENTRY=$about_entry_policy
HTCLEO_GS_LOCAL_BLACK_BACKGROUND=$gsapp_black_background_policy
HTCLEO_GS_STATIC_BACKGROUND=$gsapp_static_background_policy
HTCLEO_GS_ROOT_WINDOW_BACKGROUND=$gsapp_window_background_policy
HTCLEO_GS_ROOT_SKIN_BACKGROUND=$gsapp_root_skin_background_policy
HTCLEO_GS_ROOT_BACKGROUND_OWNER=$gsapp_root_background_owner_policy
HTCLEO_GS_ROOT_PAINT_WITNESS=$gsapp_root_paint_witness_policy
HTCLEO_GS_ROOT_BITMAP_BACKGROUND=$gsapp_root_bitmap_background_policy
HTCLEO_AVKON_COMMON_GEOMETRY=$avkon_common_geometry_policy
HTCLEO_FONT_FAMILY_BINDING=$font_family_binding_policy
HTCLEO_GS_TEXT_WITNESS=$gsapp_text_witness_policy
HTCLEO_GS_FONT_CENSUS=$gsapp_font_census_policy
HTCLEO_GS_FONT_LOAD_BOUNDARY=$gsapp_font_load_boundary_policy
HTCLEO_GS_FONT_SERVER_LIFETIME=$gsapp_font_server_lifetime_policy
HTCLEO_ECOM_SERVER_EXCEPTION=$ecom_server_exception_policy
HTCLEO_ECOM_MISSING_INTERFACE=$ecom_missing_interface_policy
HTCLEO_HOME_EXTERNAL_EMPTY=$home_external_empty_policy
HTCLEO_ECOM_FONT_REGISTRY=$ecom_font_registry_policy
HTCLEO_ECOM_FONT_GETINFO=$ecom_font_getinfo_policy
HTCLEO_FREETYPE_SPI=remove-only-absent-ityperast-duplicate100012a7-101f7f5d-101f7f5e-keep-real-freetype-140-spi-entries
HTCLEO_FILEMANAGER_REGISTRATION=$filemanager_registration_policy
HTCLEO_APPARC_FORCED_NATIVE=$apparc_forced_native_policy
HTCLEO_MCS_NOTIFIER_RECONNECT=$mcs_notifier_reconnect_policy
HTCLEO_APPARC_ENUMERATION_END=$apparc_enumeration_end_policy
HTCLEO_APPARC_TERMINAL_EXCEPTION=$apparc_terminal_exception_policy
HTCLEO_APPARC_EMPTY_ICON_NAME=$apparc_empty_icon_name_policy
HTCLEO_APPARC_PRELOAD_PUBLICATION=$apparc_preload_publication_policy
HTCLEO_FILEMANAGER_LAUNCH_PREP=$filemanager_launch_prep_policy
HTCLEO_FONT_ECOM_LIST_RECONNECT=$font_ecom_reconnect_policy
HTCLEO_FBS_ROM_RASTERIZER=$fbs_rom_rasterizer_policy
HTCLEO_HOME_MENU_DISPATCH=owned-async-after-cba-event-no-inline-ordinal-175d-175e
HTCLEO_HOME_NATIVE_FOCUS_STATE=home-only-wserv-gain-sync-xn-partial-aware-1800-1802-edge1810
HTCLEO_HOME_LIVENESS=retired-exact742-aifw-and-wserv-control
HTCLEO_WSERV_SHELL_HANDOFF_TRACE=retired-exact742-command-reply-and-exit-instrumentation
HTCLEO_WSERV_NONBLOCKING_LOG=retired-exact742-wserv-component-control
HTCLEO_WSERV_742_BINARY_CONTROL=$wserv_control_policy
HTCLEO_WSERV_FIND_NOTFOUND=$wserv_find_policy
HTCLEO_GSAPP_STARTUP_OBSERVER=$gsapp_observer_policy
HTCLEO_GSAPP_EIKSTART_FRONTIER=$gsapp_eikstart_policy
HTCLEO_GSAPP_ENV_FRONTIER=$gsapp_env_policy
HTCLEO_GSAPP_AKNENV_FRONTIER=$gsapp_aknenv_policy
HTCLEO_GSAPP_SGC_LOCAL_LAYOUT=$gsapp_sgc_policy
HTCLEO_GSAPP_APPUI_FRONTIER=$gsapp_appui_policy
HTCLEO_GSAPP_SGC_PARAMS_LOCAL=$gsapp_sgc_params_policy
HTCLEO_GSAPP_SGC_FADE_LOCAL=$gsapp_sgc_fade_policy
HTCLEO_GSAPP_VIEW_FRONTIER=$gsapp_view_policy
HTCLEO_GSAPP_FOCUS_FRONTIER=$gsapp_focus_policy
HTCLEO_GSAPP_KEYBLOCK_LOCAL=$gsapp_keyblock_policy
HTCLEO_GSAPP_ACTIVATION_FRONTIER=$gsapp_activation_policy
HTCLEO_GSAPP_PLUGIN_FRONTIER=$gsapp_plugin_policy
HTCLEO_GSAPP_REDRAW_FRONTIER=$gsapp_redraw_policy
HTCLEO_GSAPP_LIFETIME_OBSERVER=$gsapp_lifetime_policy
HTCLEO_GSAPP_VIEW_TRANSITION=$gsapp_transition_policy
HTCLEO_GSAPP_CONE_VIEW_EVENT=$gsapp_cone_event_policy
HTCLEO_HOME_VIEW_EVENT=$home_view_event_policy
HTCLEO_VIEWCLI_SOURCE_CONTROL=$viewcli_source_control_policy
HTCLEO_VWS_CLIENT_QUEUE=$vws_client_queue_policy
HTCLEO_VWS_CLIENT_STATE=$vws_client_state_policy
HTCLEO_VIEWSRV_SOURCE_CONTROL=$viewsrv_source_control_policy
HTCLEO_VWS_SERVER_EVENT=$vws_server_event_policy
HTCLEO_VWS_SESSION_DEACTIVATION=$vws_session_deactivation_policy
HTCLEO_GSAPP_ASYNC_VIEW_EVENT=$gsapp_async_policy
HTCLEO_GSAPP_INPUT_ACTIVATION=$gsapp_list_policy
HTCLEO_GSAPP_CHILD_FRONTIER=$gsapp_child_policy
HTCLEO_GSAPP_ECOM_CREATE_RETRY=$gsapp_create_policy
HTCLEO_GSAPP_ECOM_NOTIFY_GUARD=$gsapp_notify_policy
HTCLEO_GSAPP_EXCEPTION_WITNESS=$gsapp_exception_policy
HTCLEO_GSAPP_EIKBASE_FRONTIER=$gsapp_eikbase_policy
HTCLEO_GSAPP_APPINFO_FRONTIER=$gsapp_appinfo_policy
HTCLEO_GSAPP_STATUSPANE_FRONTIER=$gsapp_statuspane_policy
HTCLEO_742_UI_CONTROL=$ui_control_policy
HTCLEO_MATRIX_FOCUS_CHROME=retired-749-rejected-return-to-748
HTCLEO_MATRIX_FOCUS_TOUCH_REARM=async-hal10-dfc-owned-d0-00-01-heartbeat-52rrccee
HTCLEO_AVKON_FOCUS_TOUCH_REARM=shared-all-avkon-focusgained-hal10-async-failopen-c594
HTCLEO_CLOCK_WATCH=split-tester-writer-absolute12-highres5s-classic4s-readonly-hal-1m-ring
HTCLEO_TYPE2A_FOCUS_REARM=atomic-request-25-poll-delay-dfc-sole-i2c-functions10-17
HTCLEO_TYPE2A_FOCUS_REARM_DELAY=latest-request-restarts-bounded-25-poll-countdown
HTCLEO_TYPE2A_IRQ_READY_POLL=gpio92-active-low-gates-i2c-read-functions14-15
HTCLEO_TYPE2A_HIGH_LEVEL_FALLBACK=10-high-polls-200ms-real-read-fresh-contact406-error407-functions18-20
HTCLEO_SHELL_POINTER_LOG_POLICY=home-no-per-pointer-files-matrix-5s-entry-grid-edges-heartbeats-commands-focus-retained
HTCLEO_MATRIX_NATIVE_ACTIVATION=stock-apa-empty-message-owned-wg-buffered-ordinal-1450-145f
HTCLEO_MATRIX_SCHEDULER_LOG_RETIREMENT=cone-and-ready-ao-no-file-io-in-matrix-dispatch
HTCLEO_MATRIX_HEARTBEAT=menulog-01fe-arm-01ff-aliv-before-rearm-52rrccee-after-5s-ui-thread-1m-no-frame-property-no-flush
HTCLEO_MATRIX_SKIN_REFRESH=existing-model-resource-invalidation-no-hn-requery-1460-1465
HTCLEO_MATRIX_HOME_HANDOFF=match-outbound-priority-freeze-real-ordinal-restore-144a-144b-1443
HTCLEO_HOME_RESUME_FASTPATH=first-home-stock-repeat-home-no-effects-base-keyblock-focus-retained
HTCLEO_SPARSE_FAT_LOGS=off-764-frozen-763-restored
HTCLEO_MENULOG_SHARED_CAPACITY=1048576-reserve128-five-writers
HTCLEO_EXTERNAL_THREAD_WATCH=$external_thread_watch_policy
HTCLEO_HOME_KERNEL_WATCH=$home_kernel_watch_policy
HTCLEO_THREAD_STATE_HAL=21-readonly-v2-endpoint-readyqueue-timeslice-context
HTCLEO_LOGLESS_LIVENESS=1hz-ntimer-isr-rgb565-mdp-user12-kct2-io-phase
ACTIVE_LOGICAL_DISPLAY_PROBES=1
HTCLEO_KERNEL_FAULT_BADGE=retired-773-core-relink-regression
HTCLEO_CRASH_NOTICE_OBSERVER=btrace-kern4-thread-exit-subject-core772
HTCLEO_DIAGNOSTIC_RETENTION=visible-liveness-and-crash-through-gate21
HTCLEO_MATRIX_STALE_FOCUS=759-frozen-758-original-redraw-finish-restored
HTCLEO_MATRIX_HOME_HANDOFF_ASYNC=standard-casync-after-cba-return-1429-142e-sync-fallback
HTCLEO_HNMETADATA_INITIAL_NOTIFICATION=first-per-subscription-coalesced-no-filelog-later-real-changes-retained
HTCLEO_MCS_STARTUP_LOG_POLICY=144-145-no-file-io-registration-rendezvous-scheduler
HTCLEO_MCS_CLIENT_CONNECT_TRACE=matrix-only-190-193-startserver-return-real-session-results-1m
HTCLEO_MCS_READY_HANDSHAKE=matrix-per-pid-property-500x10ms-no-rendezvous-request-real-createsession
HTCLEO_AKNGRID_EMPTY_CELL_BACKGROUND=matrixmenu-preserve-mmwidgets-wallpaper-stock-other-apps
HTCLEO_MATRIX_WALLPAPER=cached-HOMEBG-full-client-grid-and-empty-cells-no-chrome-change
HTCLEO_MATRIX_NONCELLULAR_RETURN=permanent-direct-home-no-phone-or-video-task-lookup
ECOMLOG_CAPACITY=737280-bytes-16384x45
WSERV_SCREEN_CONSTRUCT_LOG=screen-redraw-renderstage-chain
WSERV_CLIENT_WINDOW_CREATE_TRACE=property-armed-request-0430-0432-0400-0421-behavior-unchanged
WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT=sid-scoped-property-armed-0440-0445-first32-trace-redraw-cleanup-and-optional-errors-skip-fatal-complete
HTCLEO_WSERV_TYPE2A_POINTER_ENABLE=stale-none-to-pointer-only-with-live-type2a-hal-traced-0450-0451
HTCLEO_WSERV_TYPE2A_RAW_PATH_TRACE=bounded-16-receiver-preprocess-process-hittest-0452-0454-0458-0459
HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER=capture-request-plus-5s-continuous-real-event-and-raw-snapshot-045a-0465-0477
HTCLEO_WSERV_RUNL_TRACE_BOUND=first32-real-events-045e
HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK=stock-basearea-root-only-visible-tree-absrect-0466-0467
HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK=root-only-real-property-handle-tree-lookup-0468-0469
HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE=real-construct-pointer-handle-match-visible-lifetime-cleared-046a-046b
HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION=wserv-window-client-mmwidgets-container-appui-reset-gc-046c-046d-0182-1250-1255
HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY=full-16-char-utf16-pairs-046e-0476
HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE=all-mask-log-type-12a0-12a1-repanic
HTCLEO_MATRIXMENU_ABORT_STACK_TRACE=terminate-unexpected-sp-32words-12a2-12cf-repanic
HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT=startup-regression-retired-exception-stack-retained-12a5-12cf
HTCLEO_MATRIXMENU_CALLER_STACK_TRACE=naked-entry-sp-lr-96words-12a5-130f-repanic
HTCLEO_HOMESCREEN_SHELL=stock-active-idle-product-closure-73-seeds-cba-background-target
HTCLEO_HOMESCREEN_CLOSURE=recursive-import-zero-missing-zero-unresolved-controller-rendering-hsps-cps
HTCLEO_STEM_HOMESCREEN_LAUNCH=stock-ailaunch-deferred-monitor-32767
HTCLEO_STEM_HOMESCREEN_LAUNCH_ORDER=critical-post-matrixmenu-wait-deferred-wait
HTCLEO_HOMESCREEN_DURABLE_LOG=HSLOG-1m-startup-ecom-idleuid-launch-heartbeat-5s
HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT=HLD-0c-67-98-only-HSCONE-050f-0207-only-HSLOG-ALIV-retained
HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT=DSPR-stage1000-only-per-frame-fat-writes-retired
HTCLEO_WSERV_TOUCH_ONLY_LOG=WSLOG-045a-0465-touch-046c-0476-fatal-startup-retired
HTCLEO_LOG_RETIREMENT_POLICY=gate16-visual-baseline-preserved-low-rate-heartbeat-and-touch-fatal-only
HTCLEO_HOMESCREEN_CONTROLLER_TRACE=cenrep-ecom-maininterface-array-handlers-0130-0137
HTCLEO_HOMESCREEN_RESTART_POLICY=max-three-crashes-one-second-backoff-preserve-error
HTCLEO_HOMESCREEN_EXIT_CATEGORY_TRACE=HSLOG-1m-0240-0246-024e-utf16-pairs
HTCLEO_HOMESCREEN_EXIT_CATEGORY_POLICY=diagnostic-only-no-restart-count-or-timing-change
AI3XMLUIMAIN=source-built-stock-plugin-uid-2001952a-export-1
HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE=HSXML-1m-eikstart-application-document-appui-xuikon-48580100-48580206
HTCLEO_AI3XMLUIMAIN_BEHAVIOR_POLICY=diagnostic-only-preserve-eikstart-result-and-leave
HTCLEO_AI3XML_ONLINEOFFLINE_POLICY=notfound-or-serverterminated-null-hide-cellular-menu
HTCLEO_AI3XML_ONLINEOFFLINE_TRACE=HSXML-1m-485801A1-A4-real-helper-result
XN3LAYOUTENGINE=source-built-frozen-278-plus-reviewed-279-281
HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE=HSXML-1m-48581000-48581010-behavior-neutral
HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE=HSXML-1m-48581100-48581124-behavior-neutral
HTCLEO_XNVIEWMANAGER_LOADUI_TRACE=HSXML-1m-48581500-0c-10-15-20-2d-30-3e-50-55-60-67
HTCLEO_XNVIEWMANAGER_LOADUI_POLICY=diagnostic-only-real-root-compose-odt-view-widget-path-retained
HTCLEO_XN_ODT_VIEW_LOAD_TRACE=HSXML-1m-48581570-485815A7
HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE=keerrserverterminated-no-persistent-remove
HTCLEO_XNROOT_TRANSIENT_VIEW_POLICY=propagate-transient-other-errors-stock
HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN=homescreen-20019592-actions-action-event-serverterminated-empty
HTCLEO_XN_NONVISUAL_FACTORY_TRACE=HSXML-1m-485815A8-AB
HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE=homescreen-actionshandler-actions-action-event-count0
HTCLEO_XN_ZERO_FACTORY_GENERAL_TRACE=HSXML-1m-48581577-78
HTCLEO_XN_METADATA_FACTORY_FAILOPEN=homescreen-20019592-explicit-nonlayout-metadata-set
HTCLEO_XN_METADATA_FACTORY_POLICY=explicit-nonlayout-no-visual-types
HTCLEO_XN_MENU_GROUP_FACTORY_FAILOPEN=homescreen-20019592-menuitemgrouping-menuitemgroup-serverterminated-empty
HTCLEO_XN_MENU_GROUP_FACTORY_POLICY=qhd-view-complete-metadata-only-no-menubar
HTCLEO_XN3UTILS_STOCK_PIN=pdk304-fc978092e1ae97f2fea7768662f7b2840153942d0e1c51ecb6f9d6cc22f045c2
HTCLEO_XN3LAYOUTENGINE_ABI=exact-frozen-prefix-six-symbol-visibility-promotion
HSPLUGINSETTINGS=source-built-frozen-90-export-abi
HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE=HSXML-1m-48581200-4858123F-behavior-neutral
HTCLEO_HSPLUGINSETTINGS_POLICY=diagnostic-only-no-tls-liw-hsps-result-branch-timer-or-leave-change
HSPSTHEMESERVER=source-built-stock-uid-200159C0
HTCLEO_HSPSTHEMESERVER_FAMILY_COMPAT=480x800-to-qhd_tch-missing-root-retry
HTCLEO_HSPSTHEMESERVER_TRACE=HSPSSRV-1m-48581300-485813F1
HTCLEO_HSPSTHEMESERVER_POLICY=real-rom-manifests-and-installation-retained-no-fabricated-odt
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL=ai3-2001f482-empty-reinstall-once-real-rom
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_TRACE=HSPSSRV-1m-485813e0-485813e4
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_POLICY=exact-corrupt-zero-view-only-no-fabricated-node
HTCLEO_HSPS_INSTALL_SKELETON_TRACE=HSPSSRV-1m-4858135b-5f-90-91-b0-b6-a0-a5-c0-cd-d0-d4-behavior-neutral
HTCLEO_HSPS_INSTALL_SKELETON_POLICY=diagnostic-only-real-dom-resource-localize-repository-path-retained
HTCLEO_HSPS_POSTCOMPLETE_POINTER=guarded-null-after-user-requestcomplete
HTCLEO_HSPS_INSTALLER_ECOM_RECOVERY=xml-parser-and-definition-engine-serverterminated-retry-once
HSPSDEFINITIONENGINE=source-built-stock-uid-200159ba-export-1
HTCLEO_HSPS_DEFINITION_ENGINE_PARSER=lazy-after-outer-ecom-factory-real-parser-retained
HTCLEO_HSPS_DEFINITION_ENGINE_ECOM_RECOVERY=retired-finalclose-after-libxml2-rom-closure
HTCLEO_HSPS_DEFINITION_ENGINE_TRACE=HSDEF-1m-485814e0-eb-f0-fb
HTCLEO_HSPS_LIBXML2_ROM_CLOSURE=stock-dll-resource-spi-impl-101f9783-no-finalclose
HSPSPROVIDER=source-built-stock-uid-200159b7-export-1
HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT=schema-direct-root-list-real-liw-maps
HTCLEO_HSPSPROVIDER_TRACE=HSXML-1m-48581610-48581615
HTCLEO_HSPSPROVIDER_POLICY=real-root-plugin-ids-uids-activation-locking-retained-no-fabrication
HTCLEO_ROM_SPACE_RECLAIM=goal-irrelevant-mp3-test-sample-271890-bytes
HTCLEO_ROM_WINDOW_POLICY=preserve-03a00000-ramstart-15c00000
DISPLAY_RENDER_STAGE_LOG=display-openwfc-render-target
HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT=cpu-frame-loop-rgb565-map-transfer-screeninfo-wsswitchon-1910-1911-1900-1909
HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT=wserv-flicker-target-direct-rgb565-1920-1921
DSPRLOG_CAPACITY=2048
HTCLEO_DISPLAY_FRAME_SIGNATURE=source-1930-destination-1931-sparse-fnv-dspr2048
HTCLEO_DISPLAY_REGION_AWARE_BLIT=dirty-rect-preserve-framebuffer-1932
HTCLEO_UI_FRAME_STAGE_CORRELATION=matrixmenu-eikcore-property-7f4d5702-dspr1933
HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD=matrixmenu-1013-white-legacy360x640-or-scaled1or2rect480x800-retire-1934
HTCLEO_DEFAULT_SKIN_PAYLOAD=symbian-200259e6-stock-skn-mbm-mif
HTCLEO_DEFAULT_SKIN_SELECTION=haze-2000b12d-cenrep-key14-data-only
OPENWFC_CONTEXT_LOG=context-display-surface-scratch-pipeline-thread
WFCLOG_CAPACITY=256
OPENWFC_ENGINE=source-built-standard-not-syborg-alias
OPENWFC_OUTPUT_FORMAT=rgb565-enabled
APPARC_DURABLE_LOG=server-start-list-scan-observer-completion
APPARC_FIRST_SCAN_POLICY=htcleo-synchronous-scan-and-icons-no-timer-later-rescans-stock
APPARC_RESTART_RECOVERY_POLICY=20B-20F-serverterminated-failopen
APPARC_RESTART_RECOGNIZER_POLICY=20D-serverterminated-null-guard
APALOG_CAPACITY=2048-two-module
APPARC_LAUNCH_LOG=apsexe-create-akncap-resume-return-property-signal-retained-and-thread-exit-category
AKNCAPCLIENT_PROPERTY_READY=fire-and-forget-no-request-no-timer-no-poll-property-retained
APASTART_CAPACITY=256
MATRIXMENU=source-built-uid-101f4cd2
MATRIXMENU_STACK_POLICY=htcleo-ui-shell-0x10000-gcce-aknlayoutrect-headroom
MATRIXMENU_LIFECYCLE_LOG=MENULOG.TXT-4D4D0000-4D4D0312-and-4D4D1000-4D4D1012
MATRIXMENU_LOG_CAPACITY=1048576-bytes-own-writer
MATRIXMENU_RUNTIME_EVENT_TRACE=ws-1200-1202-focus-1210-1221-foreground-1230-1241-exit-1290
HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH=visible-foreground-0f-focus-only-touch-rearm-no-ui-redraw
HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION=stale-own-wg-guard-real-wg-uid-tid-pid-stock-handoff-1206-120b
HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE=real-cba-homescreen-apparc-startapp-1400-1449-fixed-uid-bootstrap-only-on-missing-property
MATRIXMENU_STARTUP_FOREGROUND_COMMIT=real-root-task-panes-container-finish-0350-0354
MATRIXMENU_FOREGROUND_EVENT_POLICY=real-wg-ordinal-no-brought-to-foreground-system-event-0355-120a-1291
MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL=skip-when-focus-equals-root-0355-0356
HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT=high-priority-real-cba-refresh-after-grid-0372-0375
HTCLEO_TYPE2A_TOUCH_AUTOSTART=epointer-auto-extension-type2a-only-keys-medint-deferred
HTCLEO_TYPE2A_INPUT_IDENTITY=digitiser-primary-plus-legacy-mouse-hal-compat-480x800
HTCLEO_TYPE2A_RAW_PACKET_SNAPSHOT=current-two-words-points-transitions-functions6-9
HTCLEO_TYPE2A_TOUCH_DIAGNOSTIC=platformspecific2-stage-result-raw-packet-press-latched-samples-events-xy
HTCLEO_TYPE2A_TOUCH_TLMM_POLICY=proccomm-timeout-fixed-boot-mux-fallback-other-errors-failclosed
HTCLEO_TYPE2A_TOUCH_IRQ_READY_POLICY=runtime-gpio92-active-low-data-ready-gates-i2c-read
HTCLEO_TYPE2A_TOUCH_RESET_POLICY=3-bounded-full-power-cycles-gpio-readback-irq500ms-id-authoritative
HTCLEO_TYPE2A_TOUCH_POLL_POLICY=mutating-timer-dfcq0-gpio92-ready-gated-sample-again-fallback-oneshot
HTCLEO_QSD8K_GPT_CLOCK_POLICY=htcleo-divider3-32768hz-match32-periodic-clear-on-match
HTCLEO_QSD8K_VIC_VECTOR_POLICY=scorpion-prime-d0-pending-d4-ack-before-handler-drain-until-none
HTCLEO_TYPE2A_TOUCH_TICK_DIAGNOSTIC=pre-first-sample-vic-enable-irq-raw-gpt-enable-divider-count-nkern-tick
HTCLEO_QSD8K_I2C_POLLING_POLICY=clk-active-6us-write-delay-multibyte-rdfull-failclosed
HTCLEO_QSD8K_I2C_ERROR_POLICY=direct-output-phase8-lines2-status16-controller-stop-flush-recovery
HTCLEO_QSD8K_I2C_ABI=existing-read-write-exports-extended-caller-contract-no-new-symbols
HTCLEO_TYPE2A_TOUCH_I2C_DIAGNOSTIC=direct-output-phase8-lines2-status16
HTCLEO_TYPE2A_TOUCH_I2C_RETRY=init-only-17-attempts-10us-controller-recovery-sample-single
MATRIXMENU_SCHEDULER_ENTRY_KICK=retired-unowned-signal-1013-detail0-stock-scheduler-and-view
MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER=real-suite-direct-container-show-draw-0313-0318
MATRIXMENU_UI_FIRST_CONTAINER_COMPAT=real-widget-statuspane-0320-0333-no-startup-effect
MATRIXMENU_PRECONTAINER_SUITE_INIT_POLICY=defer-hidden-startup-callback-0334-real-sync-container-retained
MATRIXMENU_ROM_PRESENTATION_FALLBACK=foldersuite-first-grid-logical-template-3-0340-0342
MATRIXMENU_FIRST_FRAME_FINISH=post-drawview-wserv-finish-0319-031a-failclosed
MMWIDGETS_GRID_WINDOW_HANDLE=property-101f4cd2-7f4d5701-stage-0144
MATRIXMENU_STARTUP_POLICY=release-equivalent-local-eikstart-deferred-startapp-and-multiplewait-retained
MATRIXMENU_EXTENSION_POLICY=ui-first-defer-030f-4558544e-null-guards
MATRIXMENU_SKIN_SESSION_POLICY=late-haze-connect-after-first-frame-failopen-0310-0360-0362
HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION=post-first-frame-connect-setall-2000b12d-redraw-failopen-0360-0362
HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW=enable-notify-deployed-refresh-draw-finish-0363-0365
HTCLEO_MMWIDGETS_HAZE_BACKGROUND=qsn-bg-screen-existing-haze-item-no-fabricated-pixels
HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND=source-black-52a2a5-32-band-software-draw-0170-0171
HTCLEO_MMWIDGETS_TOUCH_DIAGNOSTIC=hal-172-17a-existing-redraw-snapshots-grid-pointer-180-181-readonly
HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION=real-widget-drawdeferred-fullrect-draw-finish-0370-0371
CUSTOM_COMMAND_LOG=akncustcmds-ordinal1-loader-factory-initialise-execute
CUSTOM_COMMAND_LOAD_SPLIT=connect-loadlibrary-handle-close-init-C100-C108
CUSTOM_COMMAND_INIT_TRACE=libraryattach-bootstrap-kernel-entrypoints-C201-CB26
CUSTOM_COMMAND_EXEC_STUB=thumb-entry-arm-swi-interworking
CUSTLOG_CAPACITY=512-two-module
EFILE_LOADER_TRACE=top-level-akncustcmds.dll
EFILE_LOADER_LOG=AKNLDR.TXT
SSMCMD_ABI=frozen-1-91-plus-private-timer-92-100
SCREEN_PROBE_RENDERERS=retired-hal-function2-and-kernel-exception
GATE11=hardware-pass-430
HARDWARE_FUNCTIONAL_BASELINE=430
SD_DEPLOYED=no
EOF

cat "$output/BUILD-RESULT.txt"

python3 "$project/Symbian/scripts/audit-htcleo-native-full-rom.py" "$output"

# Keep the image before canonical call-site retirement as an explicitly named
# diagnostic sidecar, but make the iteration-419 no-display form the only
# normal package input. Iteration 431 additionally removes both renderer
# implementations, so even the sidecar can no longer draw a probe panel.
# The canonicalizer re-resolves and verifies all fourteen sites against this
# exact build, so future ROM layout changes never reuse stale addresses.
python3 "$canonicalizer" \
    "$build_output/htcleo_symbian3_full_native.img" \
    "$build_output/HTCLEO-PROBE-MAP.txt" \
    "$canonical_image" \
    "$canonical_map"
grep -qx 'STATUS=HTCLEO_CANONICAL_NO_DISPLAY_OK' "$canonical_map"
grep -qx 'CANONICAL_BASELINE_ITERATION=419' "$canonical_map"
grep -qx 'TOTAL_RETIRED_RUNTIME_INSTRUCTIONS=14' "$canonical_map"
grep -qx 'PROGRESS_DISPLAY_CALLS_REMAINING=0' "$canonical_map"
grep -qx 'ROUTINE_FRAMEBUFFER_WRITERS=0' "$canonical_map"
test "$(wc -c <"$canonical_image")" -eq "$size"

canonical_hash=$(sha256sum "$canonical_image" | awk '{print $1}')
test "$(sed -n 's/^CANONICAL_SHA256=//p' "$canonical_map")" = \
    "$canonical_hash"

if [ "$incremental_resource_policy" = gate17-gsapp-black-background ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-gsapp-black-background.py" \
        --profile 850 --native "$output" --image "$canonical_image" --recipe "$recipe" --rom-log "$log" \
        --report "$output/GSAPP-BLACK-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-avkon-common-geometry ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-avkon-common-geometry.py" \
        --native "$output" --image "$canonical_image" --recipe "$recipe" --rom-log "$log" \
        --report "$output/AVKON-GEOMETRY-ROM.json"
fi
if [ "$incremental_resource_policy" = gate17-font-family-binding ]; then
    python3 "$font_family_binding" --image "$canonical_image" --report "$output/FONT-FAMILY-ROM.json"
fi
if [ "$incremental_resource_policy" = gate19-filemanager-registration ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-filemanager-wait-boundary.py" \
        --native "$output" --image "$canonical_image" --recipe "$recipe" --rom-log "$log" \
        --report "$output/FILEMANAGER-WAIT-ROM.json"
fi

#841 compares existing ROM code against the final840 canonical checkpoint.
#The pre-canonical image still has fourteen historical retirement call sites.
#Do not mask them or weaken the core check: run the strict check after the
#unchanged canonicalizer, and again before packaging the sole boot payload.
if [ "$incremental_resource_policy" = gate17-about-entry ] || \
   [ "$incremental_resource_policy" = gate17-about-no-global-rescan ]; then
    python3 "$project/Symbian/scripts/verify-htcleo-about-entry.py" \
        --parent "$incremental_parent_root" --plan "$about_entry_plan" --config "$about_entry_config" --recipe "$recipe" \
        --image "$canonical_image" --rom-log "$log" --report "$output/ABOUT-ENTRY-ROM.json"
fi
cat >"$output/CANONICAL-RESULT.txt" <<EOF
STATUS=HTCLEO_CANONICAL_NO_DISPLAY_OK
BUILD_MODE=$build_mode
INCREMENTAL_PARENT=$incremental_parent
INCREMENTAL_CHANGED_BINARIES=$incremental_changed_binaries
INCREMENTAL_RESOURCE_POLICY=$incremental_resource_policy
HTCLEO_BLUETOOTH_POLICY=esock-bt-cmi-and-esk-suppressed
HTCLEO_OFFLINE_NETWORK_POLICY=esock-dip-ip-sip-startup-and-protocols-suppressed
HTCLEO_FINAL_ACCEPTANCE=offline-java-gate18-retired-gate20-optional
INCREMENTAL_MIGRATION=$incremental_migration
INCREMENTAL_NATIVE_BSP_REBUILT=$rebuild_native_bsp
BASELINE_ITERATION=419
FUNCTIONAL_LINEAGE=430
IMAGE=$canonical_image
SIZE=$size
SHA256=$canonical_hash
ACTIVE_DIAGNOSTIC_IMAGE=$build_output/htcleo_symbian3_full_native.img
ACTIVE_DIAGNOSTIC_SHA256=$hash
PROGRESS_DISPLAY_CALLS_REMAINING=0
KERNEL_LIBRARY_ATTACH_PROGRESS=6-bootstrap-plus-10-stage-notify-flush-ack
ECOM_ATTACH_WATCHER=blocked-bootstrap-and-attach-no-polling
ECOM_EXEC_STUB=thumb-entry-arm-swi-interworking
ECOM_FEATMGR_LIST_TRACE=F200-F24D-sid-10205054-interface-10205057
ECOM_SERVER_FEATMGR_LIST_TRACE=F300-F400-exact-arm-interface-10205057-romonly-resolver-10009D92
ECOM_SERVER_REGISTRY_LIST_TRACE=F3E0-F400
ECOM_FEATUREINFO_EMPTY_LIST_COMPAT=interface-10205057-notfound-to-empty
HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY=sid-101f4cd2-keerrserverterminated-reconnect-once-310-314
HTCLEO_ECOM_MATRIXMENU_LIST_RETRY=sid-101f4cd2-reconnect-once-terminated-to-empty-315-31a
HTCLEO_ECOM_HOMESCREEN_LIST_RETRY=sid-102750f0-interface-200286df-one-reconnect-then-empty
HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY=sid-102750f0-interface-20019592-type-action-one-reconnect-then-empty
HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY=sid-102750f0-interface-20019592-types-actions-action-event
HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY=sid-102750f0-interface-20019592-type-menubar-one-reconnect-failclosed
HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY=sid-102750f0-interface-20019592-all-types-one-reconnect-visual-failclosed
HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY=sid-102750f0-shared-one-reconnect-no-normalization
HTCLEO_ECOM_HOMESCREEN_SERVER_TRACE=service6-impl2001952c-session-server-registry-f500-f539
HTCLEO_ECOM_HSPS_DEFINITION_RESOLVE=interface200159c7-to-real-impl200159c8-security-checked
HTCLEO_ECOM_HSPS_PERSISTENT_TRACE=HSPSECOM-1m-f600-f628-append-across-server-restart
HTCLEO_ECOM_HSPS_RESPONSE_TRACE=HSPSECOM-f603-f60f-f617-f631-f634-f640-f642
HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE=HSPSECOM-hcli-c700-c707-c710-c71d-c720-c729-c730-c738
PTIENGINE=source-built-frozen-1-475-plus-reviewed-476
HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK=itut01-10281897-trapped-final-no-fep-gate17
ECOM_SERVER_DURABLE_LOG=ECOMSRV.TXT-capacity-737280-bytes-16384x45-replace-on-exact-request
HTCLEO_HOMESCREEN_ECOM_SPI=stock-108-minus-ityperast-plus-33-140-total-spitool-filter
HTCLEO_HOMESCREEN_ECOM_SPI_AUDIT=all-other-entry-bytes-identical-only-ityperast-retired
STEM_BACKEND=source-built-frozen-176-export-abi
STEM_BACKEND_CONSTRUCTOR_LOG=D101-D124
STEM_BACKEND_TIMEZONE_POLICY=defer-notfound-or-serverterminated
HITCHCOCK=source-built-frozen-prefix-2011
HITCHCOCK_ENTRYPOINT_LOG=CC00-CC05-export-table-static-initializer
AKNCAPSERVER=source-built-uid-10207218
AKNCAPSERVER_STARTUP_LOG=E000-E21B-isolated-eikstart-registration-repair-property-ready-and-lifecycle
AKNCAPSERVER_RENDEZVOUS_COMPAT=explicit-post-construct-ready-signal-no-wait-no-timer
AKNCAPSERVER_PROPERTY_READY=key-7f044302-post-construct-value-1-registered-2-missing
AKNCAPSERVER_OFN_POLICY=htcleo-no-optical-navigation-skip-e102-4f464e00
AKNCAPSERVER_POSTCRITICAL_FILELOG=retired-after-e100-evidence-4e4f494f-no-startup-change
AKNCAPSERVER_POSTCRITICAL_TRACE=property-only-stage16-result16-key-7f044301-no-fat-io
AKNCAPSERVER_E100_RETIREMENT=prearmed-before-e100-property-only-no-fat-io
AKNCAPSERVER_CRITICALITY_POLICY=htcleo-ui-first-skip-thread-system-critical
AKNCAPSERVER_NONLEO_STARTUP_POLICY=skip-product-hal-mmc-password-with-ipc-guard-discreet-popup-alternatefs-ecom-slider-flip-hwrm-slide-builtin-fsw-retained
AKNCAPSERVER_REGISTRATION_LIFETIME=exact-name-self-check-single-reregister-retained-breadcrumb
AKNCAPLOG_CAPACITY=512
EIKSRVS=source-built-uid-10003A4A
EIKSRVS_STARTUP_LOG=E700-E710-rendezvous-boundary
EIKSRV=source-built-uid-10003A4A
EIKSRV_SERVER_CONSTRUCT_LOG=E720-E757-newl-constructl
EIKSRVLOG_CAPACITY=128
EIKSRVUI=source-built-stem-uid-100053D0
EIKSRVUI_CONSTRUCT_LOG=E776-E79B-frontier-only
EIKSRVUI_INITIALIZE_LOG=E7DC-E7E2-frontier-only
EIKSRVUI_LOG_FLUSH_POLICY=write-close-no-explicit-flush-after-e7db-proof
EIKSRVUI_LOG_SCOPE_POLICY=frontier-only-e7dc-e7e2-and-e776-e79b-after-e7db-hardware-pass
C32_STARTUP_LOG=C32ROOT.TXT-C700-C719-and-C32START.TXT-C800-C879
EIKSRVUI_C32_POLICY=ui-first-fail-open-e7d8-keerrnotsupported-normalized
C32_STARTUP_POLICY=trace-retained-not-invoked-by-eiksrvui
EIKSRVUI_NOTIFY_ALERT_POLICY=ui-first-null-alert-factory-e774-a17f0001
EIKSRVUI_NOTIFIER_SERVER_POLICY=ui-first-defer-newl-and-idle-start-e7dc-e7df-4e465953
EIKSRVUI_OPTIONAL_TAIL_POLICY=ui-first-defer-external-key-keysound-animation-default-sounds-bitmap-cursors
EIKSRVUI_CONSTRUCT_ENTRY_LOG=E7A0-E7F0-E7F4-E7A1-behavior-unchanged
EIKSRVUI_SYSTEM_ATTRIBUTE_POLICY=ui-first-defer-task-end-protection-e7f3-53595301
EIKSRVUI_BASECONSTRUCT_RESULT=E7A3-trap-result-releave-detail-42415345
AKNAPPUI_BASECONSTRUCT_LOG=AKNBASE.TXT-B51C-B520-eiksrv-sid-only-frontier
HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE=HSXML-1m-B500-B520-behavior-neutral
HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_POLICY=diagnostic-only-no-result-branch-timer-layout-or-leave-change
HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE=HSXML-1m-B530-B547-C500-C52C-behavior-neutral
HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_POLICY=diagnostic-only-no-result-branch-timer-layout-sgc-or-leave-change
HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS=fixed-panel-deferred-keerrnotsupported-C529-C52C
HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_POLICY=home-eiksrv-matrixmenu-only-real-ipc-retained-for-other-sids-no-fake-success
AKNAPPUI_SCREEN_CHANGE_POLICY=eiksrv-only-fixed-screen-ui-first-skip-b503-5343524e
AKNAPPUI_SCREEN_SIZE_POLICY=eiksrv-only-fixed-480x800-ui-first-b504-53495a45-b505-01e0-0320
AKNAPPUI_TACTILE_FEEDBACK_POLICY=eiksrv-only-defer-optional-haptics-b506-48415054-b507-null
AKNAPPUI_POSTCOE_LAYOUT_LOG=retired-after-483-hardware-proof
AKNENV_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA000-4D4DA01A
AKNENV_MATRIXMENU_CDL_RECOVERY=notfound-or-terminated-recreate-engine-once
HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT=HSXML-1m-A000-A01E-home-and-matrixmenu-notfound-or-terminated
HTCLEO_AKNENV_HOMESCREEN_POLICY=real-cdl-engine-recreate-once-preserve-other-errors
AKNSGC_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA100-A107-A110-A115-A120-A132
AKNSGC_MATRIXMENU_AKNCAP_POLICY=matrixmenu-only-notfound-or-terminated-fail-open-local-layout-no-fake-handle
HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN=HSXML-1m-A100-A133-real-null-handle-local-layout
HTCLEO_AKNSGC_HOMESCREEN_POLICY=home-and-matrixmenu-notfound-or-terminated-local-layout-no-fake-handle
HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_TRACE=HSXML-1m-C560-C56E-transition-base-keyblock-effects
HTCLEO_AKNSGC_HOMESCREEN_KEYBLOCK_POLICY=handle0-skip-C570-C576-no-fake-session
HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE=HSXML-C560-C59F-enabled-existing-1m
HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE=HSXML-C580-C593-view-C598-C59E-behavior-neutral
HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_HANDLE_COMPAT=handle0-local-state-C577-C57F-real-session-stock
HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_POLICY=home-only-no-session-local-flag-real-session-stock
AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DA200-A205-A210-A21C
AKNUI_CONNECT_MATRIXMENU_RETRY_POLICY=one-real-attempt-per-call-discovery-and-fixed-name-retained-no-timer
AKNUI_CONNECT_MATRIXMENU_READY_WAIT=property-subscribe-inflight-child-no-ntimer-bounded-retry-retained
AKNUI_CONNECT_REGISTERED_SERVER=uid-10207218-kernel-name-discovery-bounded-16-fixed-name-fallback
AKNAPPUI_POSTCOE_SCREEN_SIZE_POLICY=eiksrv-only-fixed-480x800-ui-first-b533-46495832
AKNAPPUI_MATRIXMENU_POSTCOE_SCREEN_POLICY=fixed-480x800-b533-b534
AKNAPPUI_SGC_FOREGROUND_POLICY=eiksrv-only-defer-false-c51c-46475244-c51d-0
AKNAPPUI_SGC_PARAMS_POLICY=eiksrv-only-defer-c529-53474350-c52a-keerrnotsupported
AKNAPPUI_MATRIXMENU_SGC_PARAMS_POLICY=defer-c529-c52a-keerrnotsupported
AKNAPPUI_TRANSITION_EFFECTS_POLICY=eiksrv-only-defer-b51b-54524e46-b51e-54524e53
AKNAPPUI_LOG_FLUSH_POLICY=write-close-no-explicit-flush-after-b51a-proof
AKNAPPUI_LOG_SCOPE_POLICY=frontier-only-b51c-b520-after-b51b-hardware-pass
AKNAPPUI_MATRIXMENU_UI_FIRST_POLICY=fixed-480x800-no-screen-change-no-haptics-no-transitions-no-dialler-b500-b520-log
HTCLEO_AKNGRID_CPU_BACKGROUND_PRESERVE=matrixmenu-skip-broken-nvg-unused-area-redraw
MATRIXMENU_INITIAL_STATUSLAYOUT_POLICY=ui-first-defer-startup-usual-layout-0307-53504c59-runtime-switches-retained
MATRIXMENU_DUMMY_GRID_TRACE=retired-after-526-createwindowl-proof
MATRIXMENU_DUMMY_CONTAINER_POLICY=ui-first-null-transition-placeholder-0309-030a-44554d59-main-container-retained
MATRIXMENU_HNENGINE_TRACE=trap-log-releave-030b-no-normalization
MMWIDGETS_DUMMY_GRID_LOG=MMWLOG.TXT-4D570100-4D570168-close-only-matrixmenu
MMWIDGETS_LOG_CAPACITY=1048576-bytes
MMWIDGETS_DEFERRED_AO_TRACE=postprocess-200-215-drawer-220-22f
MMWIDGETS_POSTPROCESS_POLICY=queue-only-real-index-range-stage-216
HNENGINE_CONSTRUCTOR_LOG=HNLOG.TXT-484E0100-484E0128-close-only-matrixmenu
HNENGINE_INITIALIZE_LOG=HNLOG.TXT-484E0200-484E0225-close-only-behavior-unchanged
HNMETADATA_CONSTRUCTOR_LOG=MDLOG.TXT-4D440100-4D44012D-close-only-matrixmenu
HNMETADATA_EVALUATION_LOG=MDLOG.TXT-4D440200-4D44045A-close-only-behavior-unchanged
HNMETADATA_LOG_CAPACITY=1048576-bytes-four-loggers-trace-only
HNMETADATA_SHOWFOLDER_POLICY=ui-first-defer-cenrep-observer-12c-53464f4c
HNMETADATA_NOTIFY_POLICY=matrixmenu-reconnect-once-ready-gated-stock-first-query-no-duplicate-callback-500-514
HNMETADATA_NOTIFY_LIFETIME_TRACE=50a-50c-plus-513-514-callback-object-not-created
HNMETADATA_REDUNDANT_ASYNC_REFRESH=retired-after-ready-property-stock-first-query-proven
MCSMENU=source-built-uid-200113db-exports-82
MCSMENU_UI_FIRST_POLICY=core-menu-apparc-cache-getlist-native-java-retained-persistent-engine-lifetime-nokia-dynamic-services-deferred
MCSMENU_DURABLE_LOG=MCSLOG.TXT-4D430100-4D430135-close-only-server
MCSMENU_APPARC_POLICY=ui-first-scanner-restored-async-queue-notify-requery-reconnect-failopen-128-130
MCSMENU_CORE=source-built-uid-200113dc-exports-35
MCSMENU_CORE_ENGINE_LOG=MCSLOG.TXT-4D450100-4D450515-close-only-behavior-unchanged
MCSMENU_RAM_FALLBACK_POLICY=missing-c-cache-to-real-rom-520-522-524f4d46
MCSMENU_FIRST_CHANGE_POLICY=ram-only-first-changed-operation-notify-flush-530-531
MCSMENU_SERVER_CONTEXT_TRACE=142-150-process-thread-lookup-error-dtor
HTCLEO_MCS_SERVER_LIFETIME=process-persistent-engine-expiry-retained-151-152
MCSMENU_SCANNER_OPTIONAL_CONSTRUCT=160-164-narrow-failopen
MCSMENU_APPARC_BOUNDED_RETRY=165-167-12x250ms-real-scan
MCSMENU_APPARC_RETURNED_RETRY=return-status-before-mutation
MCSMENU_APPARC_SERVER_RESTART=168-16B-apsexe-rendezvous
MCSMENU_HN_READY_GENERATION=menueng-commit-532
MCSMENU_HN_READY_SIGNAL=matrixmenu-owned-alwayspass-commit-generation-query-retry-no-timer
HNMETADATA_QUERY_RETRY=empty-or-transient-once-after-next-commit-460-464
HNMETADATA_GETLIST_EXECUTION=matrixmenu-async-liw-provider-sync-pump-465
HNMETADATA_SYNC_COMPLETION=superseded-by-direct-safe-tail
HNMETADATA_SYNC_RESULT=direct-runl-safe-caller-and-retry-tail-460-466
HTCLEO_HN_SYNC_COMPLETION_SIGNAL=owned-completed-status-wait-before-direct-runl
HNMETADATA_READY_REQUEST_GUARD=no-success-skip-511-success-generation-wait
HNMETADATA_RESULTS_CONSUMPTION_TRACE=query-467-46c-item-470-49a-apparc-ready-gated-bounded-real-count-empty-suite-suppressed
MCSSERVICE=source-built-uid-2001242b-exports-34
MCSSERVICE_GETLIST_SYNC_PUMP=matrixmenu-real-ipc-per-item-icon-failopen-outer-error-raw-result-preserve-sync-result-property-safe-tail
HTCLEO_MCS_NOTIFICATION_CONTRACT=positive-mask-terminal-negative-safe-callback-tail-MCN-1m
MCSMENU_GETLIST_SERVER_COUNT=real-output-list-property-7f4d4302-hn-bounded-30
MCSMENU_GETLIST_SESSION_BUFFER=all-session-size-data-snapshot-real-payload-traced-170-175
MCSMENU_GETLIST_ATOMIC_TRANSFER=matrixmenu-size-plus-real-data-one-ipc-bounded-64k-traced-176-179
AKNSKINSRV=source-built-uid-10005A35
AKNSKINSRV_DURABLE_LOG=SKINLOG.TXT-A800-D8B8-restore-default-settings-boot-drm-defer
AKNSKINLOG_CAPACITY=256
EIKCORE=source-built-frozen-1-594-plus-gcce-595-604
HTCLEO_EIKSTART_HOMESCREEN_TRACE=HSXML-1m-sid-102750f0-commandline-rename-env-factory-execute-48590000-48590012
HTCLEO_EIKSTART_HOMESCREEN_POLICY=diagnostic-only-no-commandline-fallback-no-result-normalization
HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE=HSXML-1m-sid-102750f0-existing-E300-E36A
HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_POLICY=diagnostic-only-no-branch-result-or-timing-change
EIKCOCTL=source-built-stock-abi
EIKCOCTL_MATRIXMENU_APPINFO_LOG=EIKBASE.TXT-B620-B631-close-only
HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_TRACE=HSXML-1m-B620-B631-behavior-neutral
HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_POLICY=diagnostic-only-no-resource-control-wserv-sgc-result-or-leave-change
EIKCOCTL_MATRIXMENU_STATUSPANE_LOG=EIKBASE.TXT-B640-B67B-close-only
EIKCOCTL_MATRIXMENU_STATUSMODEL_LOG=EIKBASE.TXT-B690-B6AC-close-only
HTCLEO_EIKCOCTL_HOMESCREEN_STATUS_TRACE=HSXML-1m-HSP-B640-B713-HSM-B690-B6F5-behavior-neutral
HTCLEO_EIKCOCTL_HOMESCREEN_STATUS_POLICY=diagnostic-only-no-layout-control-wserv-sgc-result-or-leave-change
EIKCOCTL_MATRIXMENU_STATUSLAYOUT_LOG=EIKBASE.TXT-B6B0-B6DB-close-only
EIKCOCTL_MATRIXMENU_STATUSTREE_LAYOUT_LOG=EIKBASE.TXT-B6E0-B6F5-close-only
EIKCOCTL_MATRIXMENU_COMBINED_VISIBILITY_LOG=EIKBASE.TXT-B700-B70D-close-only
EIKCOCTL_MATRIXMENU_FADE_POLICY=handle-zero-not-faded-valid-session-stock-b70e-b70f
HTCLEO_EIKCOCTL_HOMESCREEN_FADE_POLICY=invalid-aknsrv-handle-not-faded-b70e-b70f-valid-session-stock
HTCLEO_MATRIXMENU_CLIENTRECT_SCALE=matrixmenu-direct-logical-360x640-to-480x800-b710-b711
HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE=matrix-contract-client-status-cba-360x640-to-480x800
HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_POLICY=no-applicationrect-800-override-real-cba-final-redraw
HTCLEO_MATRIXMENU_STATUSPANE_SCALE=subpane-logical-360x640-to-480x800-b712-b713
HTCLEO_MATRIXMENU_CBA_INNER_REDRAW=screen-bounding-scale-and-existing-drawnow-matrixmenu-only
HTCLEO_MATRIXMENU_CBA_WRAPPER_REDRAW=actual-window-invalidate-fullrect-drawnow-matrixmenu-only
EIKCOCTL_EIKBASE_CAPACITY=512
EIKCOCTL_STATUSPANE_LEAVE_POLICY=log-and-releave-no-normalization
EIKCORE_PREFACTORY_TRACE=E300-E311-plus-E312-E31E-akncap-sid-gated-property
EIKCORE_POSTPROCESS_GAP_TRACE=E312-E31E-property-only-behavior-unchanged
EIKCORE_BACKGROUND_PRIORITY_POLICY=akncap-only-defer-before-ready-e31b-e31c-stock-other-sids
EIKCORE_MATRIXMENU_DURABLE_LOG=MENULOG.TXT-4D4DE300-E311-and-4D4DE400-E425
EIKCORE_CONSTRUCTL_TRACE=E400-E425-akncap-sid-gated-property
EIKCORE_POSTAPPUI_TRACE=E320-E341-sync-E350-E357-async-matrixmenu-durable-behavior-unchanged
EIKCORE_MATRIXMENU_TASKNAME_POLICY=defer-second-refresh-only-if-empty-e342-keerrnotsupported-other-apps-stock
EIKCORE_MATRIXMENU_APPREADY_POLICY=local-ready-retained-late-wserv-publish-deferred-e343-e346-other-apps-stock
EIKCORE_MATRIXMENU_STARTUP_VIEW_AO=pending-setactive-complete-e360-e364-other-apps-stock
EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY=310-one-shot-e365-other-apps-160-stock
EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW=retired-after-real-container-e366-e368-async-other-apps-stock
EIKCORE_MATRIXMENU_VIEW_INIT=retired-empty-avkon-view-e369-e36a-other-apps-stock
STEM_CONE_REDRAW_QUEUE=matrixmenu-pending-setactive-redrawready-other-apps-stock
CONE_EVENT_PUMP_LOG=CONELOG.TXT-1m-scheduler-event-redraw-flush-0100-0403
CONE_READY_AO_TRACE=object-vtable-priority-status-ao100-aof
HTCLEO_CONE_HOMESCREEN_AO_TRACE=HSCONE-1m-scheduler-event-redraw-ready-ao-vtable
HTCLEO_CONE_HOMESCREEN_AO_POLICY=diagnostic-only-sid102750f0-no-dispatch-timing-change
HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE=HSCONE-1m-0500-050f-observers-0520-0524-behavior-neutral
HTCLEO_CONE_HOMESCREEN_FOREGROUND_POLICY=diagnostic-only-no-observer-virtual-focus-branch-or-result-change
HTCLEO_LIW_ECOM_MONITOR_POLICY=negative-notify-retire-success-sync-rearm
EIKAPPUI_BASECONSTRUCT_LOG=EIKBASE.TXT-B600-B615-eiksrv-matrixmenu-close-only
HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE=HSXML-1m-B600-B615-behavior-neutral
HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_POLICY=diagnostic-only-no-result-branch-timer-screen-or-leave-change
HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_TRACE=HSXML-E370-E379-fade-E380-E387-behavior-neutral
HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_POLICY=diagnostic-only-no-focus-fade-resource-stack-window-cursor-result-change
EIKAPPUI_MATRIXMENU_SCREEN_CHANGE_POLICY=defer-final-duplicate-b614-b615-keerrnotsupported
FEATMGR=source-built-frozen-58-export-abi
FEATMGR_AKNCAP_TRACE=E500-E548-akncap-sid-gated-property
FEATMGRSERVER=source-built-registry-before-first-use
FEATMGRSERVER_TRACE=E600-E64F-server-sid-property-deepest-stage-preserved
FEATMGRSERVER_LOADPLUGINS_TRACE=E640-E64F
FEATMGRSERVER_ZERO_PLUGIN_COMPAT=no-interface-to-empty-list
FEATMGRSERVER_UNWIND=E603-fallback-only
WSLOG_CAPACITY=1048576-bytes-ring-128-byte-records
HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT=5s-continuous-0477-request-0462-0465-counters-1m-ring
HTCLEO_HSPSPROVIDER_LOG_RETIREMENT=nonempty-completion-only-no-map-change
HTCLEO_XN_HD2_CLIENT_GEOMETRY=native-panel-contract-no-per-property-ipc-real-cba-inset-first-view-focus
HTCLEO_XN_CLIENT_WINDOW_COMMIT=owning-view-and-background-client-bounds-cached-grass-wallpaper
HTCLEO_HOME_MSK_CENTER=physical480-center-image-and-hit-normal-home-menu-rsk
HTCLEO_HOME_MENU_ARRAY=heap-cbase-zero-init-cleanupstack-no-stack-array
HTCLEO_HOME_MENU_HANDOFF=$home_menu_handoff_policy
HTCLEO_HOME_BACKGROUND_PRIORITY_AB=$home_background_priority_ab_policy
HTCLEO_ABOUT_ENTRY=$about_entry_policy
HTCLEO_GS_LOCAL_BLACK_BACKGROUND=$gsapp_black_background_policy
HTCLEO_GS_STATIC_BACKGROUND=$gsapp_static_background_policy
HTCLEO_GS_ROOT_WINDOW_BACKGROUND=$gsapp_window_background_policy
HTCLEO_GS_ROOT_SKIN_BACKGROUND=$gsapp_root_skin_background_policy
HTCLEO_GS_ROOT_BACKGROUND_OWNER=$gsapp_root_background_owner_policy
HTCLEO_GS_ROOT_PAINT_WITNESS=$gsapp_root_paint_witness_policy
HTCLEO_GS_ROOT_BITMAP_BACKGROUND=$gsapp_root_bitmap_background_policy
HTCLEO_AVKON_COMMON_GEOMETRY=$avkon_common_geometry_policy
HTCLEO_FONT_FAMILY_BINDING=$font_family_binding_policy
HTCLEO_GS_TEXT_WITNESS=$gsapp_text_witness_policy
HTCLEO_GS_FONT_CENSUS=$gsapp_font_census_policy
HTCLEO_GS_FONT_LOAD_BOUNDARY=$gsapp_font_load_boundary_policy
HTCLEO_GS_FONT_SERVER_LIFETIME=$gsapp_font_server_lifetime_policy
HTCLEO_ECOM_SERVER_EXCEPTION=$ecom_server_exception_policy
HTCLEO_ECOM_MISSING_INTERFACE=$ecom_missing_interface_policy
HTCLEO_HOME_EXTERNAL_EMPTY=$home_external_empty_policy
HTCLEO_ECOM_FONT_REGISTRY=$ecom_font_registry_policy
HTCLEO_ECOM_FONT_GETINFO=$ecom_font_getinfo_policy
HTCLEO_FREETYPE_SPI=remove-only-absent-ityperast-duplicate100012a7-101f7f5d-101f7f5e-keep-real-freetype-140-spi-entries
HTCLEO_FILEMANAGER_REGISTRATION=$filemanager_registration_policy
HTCLEO_APPARC_FORCED_NATIVE=$apparc_forced_native_policy
HTCLEO_MCS_NOTIFIER_RECONNECT=$mcs_notifier_reconnect_policy
HTCLEO_APPARC_ENUMERATION_END=$apparc_enumeration_end_policy
HTCLEO_APPARC_TERMINAL_EXCEPTION=$apparc_terminal_exception_policy
HTCLEO_APPARC_EMPTY_ICON_NAME=$apparc_empty_icon_name_policy
HTCLEO_APPARC_PRELOAD_PUBLICATION=$apparc_preload_publication_policy
HTCLEO_FILEMANAGER_LAUNCH_PREP=$filemanager_launch_prep_policy
HTCLEO_FONT_ECOM_LIST_RECONNECT=$font_ecom_reconnect_policy
HTCLEO_FBS_ROM_RASTERIZER=$fbs_rom_rasterizer_policy
HTCLEO_HOME_MENU_DISPATCH=owned-async-after-cba-event-no-inline-ordinal-175d-175e
HTCLEO_HOME_NATIVE_FOCUS_STATE=home-only-wserv-gain-sync-xn-partial-aware-1800-1802-edge1810
HTCLEO_HOME_LIVENESS=retired-exact742-aifw-and-wserv-control
HTCLEO_WSERV_SHELL_HANDOFF_TRACE=retired-exact742-command-reply-and-exit-instrumentation
HTCLEO_WSERV_NONBLOCKING_LOG=retired-exact742-wserv-component-control
HTCLEO_WSERV_742_BINARY_CONTROL=$wserv_control_policy
HTCLEO_WSERV_FIND_NOTFOUND=$wserv_find_policy
HTCLEO_GSAPP_STARTUP_OBSERVER=$gsapp_observer_policy
HTCLEO_GSAPP_EIKSTART_FRONTIER=$gsapp_eikstart_policy
HTCLEO_GSAPP_ENV_FRONTIER=$gsapp_env_policy
HTCLEO_GSAPP_AKNENV_FRONTIER=$gsapp_aknenv_policy
HTCLEO_GSAPP_SGC_LOCAL_LAYOUT=$gsapp_sgc_policy
HTCLEO_GSAPP_APPUI_FRONTIER=$gsapp_appui_policy
HTCLEO_GSAPP_SGC_PARAMS_LOCAL=$gsapp_sgc_params_policy
HTCLEO_GSAPP_SGC_FADE_LOCAL=$gsapp_sgc_fade_policy
HTCLEO_GSAPP_VIEW_FRONTIER=$gsapp_view_policy
HTCLEO_GSAPP_FOCUS_FRONTIER=$gsapp_focus_policy
HTCLEO_GSAPP_KEYBLOCK_LOCAL=$gsapp_keyblock_policy
HTCLEO_GSAPP_ACTIVATION_FRONTIER=$gsapp_activation_policy
HTCLEO_GSAPP_PLUGIN_FRONTIER=$gsapp_plugin_policy
HTCLEO_GSAPP_REDRAW_FRONTIER=$gsapp_redraw_policy
HTCLEO_GSAPP_LIFETIME_OBSERVER=$gsapp_lifetime_policy
HTCLEO_GSAPP_VIEW_TRANSITION=$gsapp_transition_policy
HTCLEO_GSAPP_CONE_VIEW_EVENT=$gsapp_cone_event_policy
HTCLEO_HOME_VIEW_EVENT=$home_view_event_policy
HTCLEO_VIEWCLI_SOURCE_CONTROL=$viewcli_source_control_policy
HTCLEO_VWS_CLIENT_QUEUE=$vws_client_queue_policy
HTCLEO_VWS_CLIENT_STATE=$vws_client_state_policy
HTCLEO_VIEWSRV_SOURCE_CONTROL=$viewsrv_source_control_policy
HTCLEO_VWS_SERVER_EVENT=$vws_server_event_policy
HTCLEO_VWS_SESSION_DEACTIVATION=$vws_session_deactivation_policy
HTCLEO_GSAPP_ASYNC_VIEW_EVENT=$gsapp_async_policy
HTCLEO_GSAPP_INPUT_ACTIVATION=$gsapp_list_policy
HTCLEO_GSAPP_CHILD_FRONTIER=$gsapp_child_policy
HTCLEO_GSAPP_ECOM_CREATE_RETRY=$gsapp_create_policy
HTCLEO_GSAPP_ECOM_NOTIFY_GUARD=$gsapp_notify_policy
HTCLEO_GSAPP_EXCEPTION_WITNESS=$gsapp_exception_policy
HTCLEO_GSAPP_EIKBASE_FRONTIER=$gsapp_eikbase_policy
HTCLEO_GSAPP_APPINFO_FRONTIER=$gsapp_appinfo_policy
HTCLEO_GSAPP_STATUSPANE_FRONTIER=$gsapp_statuspane_policy
HTCLEO_742_UI_CONTROL=$ui_control_policy
HTCLEO_MATRIX_FOCUS_CHROME=retired-749-rejected-return-to-748
HTCLEO_MATRIX_FOCUS_TOUCH_REARM=async-hal10-dfc-owned-d0-00-01-heartbeat-52rrccee
HTCLEO_AVKON_FOCUS_TOUCH_REARM=shared-all-avkon-focusgained-hal10-async-failopen-c594
HTCLEO_CLOCK_WATCH=split-tester-writer-absolute12-highres5s-classic4s-readonly-hal-1m-ring
HTCLEO_TYPE2A_FOCUS_REARM=atomic-request-25-poll-delay-dfc-sole-i2c-functions10-17
HTCLEO_TYPE2A_FOCUS_REARM_DELAY=latest-request-restarts-bounded-25-poll-countdown
HTCLEO_TYPE2A_IRQ_READY_POLL=gpio92-active-low-gates-i2c-read-functions14-15
HTCLEO_TYPE2A_HIGH_LEVEL_FALLBACK=10-high-polls-200ms-real-read-fresh-contact406-error407-functions18-20
HTCLEO_SHELL_POINTER_LOG_POLICY=home-no-per-pointer-files-matrix-5s-entry-grid-edges-heartbeats-commands-focus-retained
HTCLEO_MATRIX_NATIVE_ACTIVATION=stock-apa-empty-message-owned-wg-buffered-ordinal-1450-145f
HTCLEO_MATRIX_SCHEDULER_LOG_RETIREMENT=cone-and-ready-ao-no-file-io-in-matrix-dispatch
HTCLEO_MATRIX_HEARTBEAT=menulog-01fe-arm-01ff-aliv-before-rearm-52rrccee-after-5s-ui-thread-1m-no-frame-property-no-flush
HTCLEO_MATRIX_SKIN_REFRESH=existing-model-resource-invalidation-no-hn-requery-1460-1465
HTCLEO_MATRIX_HOME_HANDOFF=match-outbound-priority-freeze-real-ordinal-restore-144a-144b-1443
HTCLEO_HOME_RESUME_FASTPATH=first-home-stock-repeat-home-no-effects-base-keyblock-focus-retained
HTCLEO_SPARSE_FAT_LOGS=off-764-frozen-763-restored
HTCLEO_MENULOG_SHARED_CAPACITY=1048576-reserve128-five-writers
HTCLEO_EXTERNAL_THREAD_WATCH=$external_thread_watch_policy
HTCLEO_HOME_KERNEL_WATCH=$home_kernel_watch_policy
HTCLEO_THREAD_STATE_HAL=21-readonly-v2-endpoint-readyqueue-timeslice-context
HTCLEO_LOGLESS_LIVENESS=1hz-ntimer-isr-rgb565-mdp-user12-kct2-io-phase
ACTIVE_LOGICAL_DISPLAY_PROBES=1
HTCLEO_KERNEL_FAULT_BADGE=retired-773-core-relink-regression
HTCLEO_CRASH_NOTICE_OBSERVER=btrace-kern4-thread-exit-subject-core772
HTCLEO_DIAGNOSTIC_RETENTION=visible-liveness-and-crash-through-gate21
HTCLEO_MATRIX_STALE_FOCUS=759-frozen-758-original-redraw-finish-restored
HTCLEO_MATRIX_HOME_HANDOFF_ASYNC=standard-casync-after-cba-return-1429-142e-sync-fallback
HTCLEO_HNMETADATA_INITIAL_NOTIFICATION=first-per-subscription-coalesced-no-filelog-later-real-changes-retained
HTCLEO_MCS_STARTUP_LOG_POLICY=144-145-no-file-io-registration-rendezvous-scheduler
HTCLEO_MCS_CLIENT_CONNECT_TRACE=matrix-only-190-193-startserver-return-real-session-results-1m
HTCLEO_MCS_READY_HANDSHAKE=matrix-per-pid-property-500x10ms-no-rendezvous-request-real-createsession
HTCLEO_AKNGRID_EMPTY_CELL_BACKGROUND=matrixmenu-preserve-mmwidgets-wallpaper-stock-other-apps
HTCLEO_MATRIX_WALLPAPER=cached-HOMEBG-full-client-grid-and-empty-cells-no-chrome-change
HTCLEO_MATRIX_NONCELLULAR_RETURN=permanent-direct-home-no-phone-or-video-task-lookup
ECOMLOG_CAPACITY=737280-bytes-16384x45
WSERV_SCREEN_CONSTRUCT_LOG=screen-redraw-renderstage-chain
WSERV_CLIENT_WINDOW_CREATE_TRACE=property-armed-request-0430-0432-0400-0421-behavior-unchanged
WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT=sid-scoped-property-armed-0440-0445-first32-trace-redraw-cleanup-and-optional-errors-skip-fatal-complete
HTCLEO_WSERV_TYPE2A_POINTER_ENABLE=stale-none-to-pointer-only-with-live-type2a-hal-traced-0450-0451
HTCLEO_WSERV_TYPE2A_RAW_PATH_TRACE=bounded-16-receiver-preprocess-process-hittest-0452-0454-0458-0459
HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER=capture-request-plus-5s-continuous-real-event-and-raw-snapshot-045a-0465-0477
HTCLEO_WSERV_RUNL_TRACE_BOUND=first32-real-events-045e
HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK=stock-basearea-root-only-visible-tree-absrect-0466-0467
HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK=root-only-real-property-handle-tree-lookup-0468-0469
HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE=real-construct-pointer-handle-match-visible-lifetime-cleared-046a-046b
HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION=wserv-window-client-mmwidgets-container-appui-reset-gc-046c-046d-0182-1250-1255
HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY=full-16-char-utf16-pairs-046e-0476
HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE=all-mask-log-type-12a0-12a1-repanic
HTCLEO_MATRIXMENU_ABORT_STACK_TRACE=terminate-unexpected-sp-32words-12a2-12cf-repanic
HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT=startup-regression-retired-exception-stack-retained-12a5-12cf
HTCLEO_MATRIXMENU_CALLER_STACK_TRACE=naked-entry-sp-lr-96words-12a5-130f-repanic
HTCLEO_HOMESCREEN_SHELL=stock-active-idle-product-closure-73-seeds-cba-background-target
HTCLEO_HOMESCREEN_CLOSURE=recursive-import-zero-missing-zero-unresolved-controller-rendering-hsps-cps
HTCLEO_STEM_HOMESCREEN_LAUNCH=stock-ailaunch-deferred-monitor-32767
HTCLEO_STEM_HOMESCREEN_LAUNCH_ORDER=critical-post-matrixmenu-wait-deferred-wait
HTCLEO_HOMESCREEN_DURABLE_LOG=HSLOG-1m-startup-ecom-idleuid-launch-heartbeat-5s
HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT=HLD-0c-67-98-only-HSCONE-050f-0207-only-HSLOG-ALIV-retained
HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT=DSPR-stage1000-only-per-frame-fat-writes-retired
HTCLEO_WSERV_TOUCH_ONLY_LOG=WSLOG-045a-0465-touch-046c-0476-fatal-startup-retired
HTCLEO_LOG_RETIREMENT_POLICY=gate16-visual-baseline-preserved-low-rate-heartbeat-and-touch-fatal-only
HTCLEO_HOMESCREEN_CONTROLLER_TRACE=cenrep-ecom-maininterface-array-handlers-0130-0137
HTCLEO_HOMESCREEN_RESTART_POLICY=max-three-crashes-one-second-backoff-preserve-error
HTCLEO_HOMESCREEN_EXIT_CATEGORY_TRACE=HSLOG-1m-0240-0246-024e-utf16-pairs
HTCLEO_HOMESCREEN_EXIT_CATEGORY_POLICY=diagnostic-only-no-restart-count-or-timing-change
AI3XMLUIMAIN=source-built-stock-plugin-uid-2001952a-export-1
HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE=HSXML-1m-eikstart-application-document-appui-xuikon-48580100-48580206
HTCLEO_AI3XMLUIMAIN_BEHAVIOR_POLICY=diagnostic-only-preserve-eikstart-result-and-leave
HTCLEO_AI3XML_ONLINEOFFLINE_POLICY=notfound-or-serverterminated-null-hide-cellular-menu
HTCLEO_AI3XML_ONLINEOFFLINE_TRACE=HSXML-1m-485801A1-A4-real-helper-result
XN3LAYOUTENGINE=source-built-frozen-278-plus-reviewed-279-281
HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE=HSXML-1m-48581000-48581010-behavior-neutral
HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE=HSXML-1m-48581100-48581124-behavior-neutral
HTCLEO_XNVIEWMANAGER_LOADUI_TRACE=HSXML-1m-48581500-0c-10-15-20-2d-30-3e-50-55-60-67
HTCLEO_XNVIEWMANAGER_LOADUI_POLICY=diagnostic-only-real-root-compose-odt-view-widget-path-retained
HTCLEO_XN_ODT_VIEW_LOAD_TRACE=HSXML-1m-48581570-485815A7
HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE=keerrserverterminated-no-persistent-remove
HTCLEO_XNROOT_TRANSIENT_VIEW_POLICY=propagate-transient-other-errors-stock
HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN=homescreen-20019592-actions-action-event-serverterminated-empty
HTCLEO_XN_NONVISUAL_FACTORY_TRACE=HSXML-1m-485815A8-AB
HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE=homescreen-actionshandler-actions-action-event-count0
HTCLEO_XN_ZERO_FACTORY_GENERAL_TRACE=HSXML-1m-48581577-78
HTCLEO_XN_METADATA_FACTORY_FAILOPEN=homescreen-20019592-explicit-nonlayout-metadata-set
HTCLEO_XN_METADATA_FACTORY_POLICY=explicit-nonlayout-no-visual-types
HTCLEO_XN_MENU_GROUP_FACTORY_FAILOPEN=homescreen-20019592-menuitemgrouping-menuitemgroup-serverterminated-empty
HTCLEO_XN_MENU_GROUP_FACTORY_POLICY=qhd-view-complete-metadata-only-no-menubar
HTCLEO_XN3UTILS_STOCK_PIN=pdk304-fc978092e1ae97f2fea7768662f7b2840153942d0e1c51ecb6f9d6cc22f045c2
HTCLEO_XN3LAYOUTENGINE_ABI=exact-frozen-prefix-six-symbol-visibility-promotion
HSPLUGINSETTINGS=source-built-frozen-90-export-abi
HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE=HSXML-1m-48581200-4858123F-behavior-neutral
HTCLEO_HSPLUGINSETTINGS_POLICY=diagnostic-only-no-tls-liw-hsps-result-branch-timer-or-leave-change
HSPSTHEMESERVER=source-built-stock-uid-200159C0
HTCLEO_HSPSTHEMESERVER_FAMILY_COMPAT=480x800-to-qhd_tch-missing-root-retry
HTCLEO_HSPSTHEMESERVER_TRACE=HSPSSRV-1m-48581300-485813F1
HTCLEO_HSPSTHEMESERVER_POLICY=real-rom-manifests-and-installation-retained-no-fabricated-odt
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL=ai3-2001f482-empty-reinstall-once-real-rom
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_TRACE=HSPSSRV-1m-485813e0-485813e4
HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_POLICY=exact-corrupt-zero-view-only-no-fabricated-node
HTCLEO_HSPS_INSTALL_SKELETON_TRACE=HSPSSRV-1m-4858135b-5f-90-91-b0-b6-a0-a5-c0-cd-d0-d4-behavior-neutral
HTCLEO_HSPS_INSTALL_SKELETON_POLICY=diagnostic-only-real-dom-resource-localize-repository-path-retained
HTCLEO_HSPS_POSTCOMPLETE_POINTER=guarded-null-after-user-requestcomplete
HTCLEO_HSPS_INSTALLER_ECOM_RECOVERY=xml-parser-and-definition-engine-serverterminated-retry-once
HSPSDEFINITIONENGINE=source-built-stock-uid-200159ba-export-1
HTCLEO_HSPS_DEFINITION_ENGINE_PARSER=lazy-after-outer-ecom-factory-real-parser-retained
HTCLEO_HSPS_DEFINITION_ENGINE_ECOM_RECOVERY=retired-finalclose-after-libxml2-rom-closure
HTCLEO_HSPS_DEFINITION_ENGINE_TRACE=HSDEF-1m-485814e0-eb-f0-fb
HTCLEO_HSPS_LIBXML2_ROM_CLOSURE=stock-dll-resource-spi-impl-101f9783-no-finalclose
HSPSPROVIDER=source-built-stock-uid-200159b7-export-1
HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT=schema-direct-root-list-real-liw-maps
HTCLEO_HSPSPROVIDER_TRACE=HSXML-1m-48581610-48581615
HTCLEO_HSPSPROVIDER_POLICY=real-root-plugin-ids-uids-activation-locking-retained-no-fabrication
HTCLEO_ROM_SPACE_RECLAIM=goal-irrelevant-mp3-test-sample-271890-bytes
HTCLEO_ROM_WINDOW_POLICY=preserve-03a00000-ramstart-15c00000
DISPLAY_RENDER_STAGE_LOG=display-openwfc-render-target
HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT=cpu-frame-loop-rgb565-map-transfer-screeninfo-wsswitchon-1910-1911-1900-1909
HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT=wserv-flicker-target-direct-rgb565-1920-1921
DSPRLOG_CAPACITY=2048
HTCLEO_DISPLAY_FRAME_SIGNATURE=source-1930-destination-1931-sparse-fnv-dspr2048
HTCLEO_DISPLAY_REGION_AWARE_BLIT=dirty-rect-preserve-framebuffer-1932
HTCLEO_UI_FRAME_STAGE_CORRELATION=matrixmenu-eikcore-property-7f4d5702-dspr1933
HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD=matrixmenu-1013-white-legacy360x640-or-scaled1or2rect480x800-retire-1934
HTCLEO_DEFAULT_SKIN_PAYLOAD=symbian-200259e6-stock-skn-mbm-mif
HTCLEO_DEFAULT_SKIN_SELECTION=haze-2000b12d-cenrep-key14-data-only
OPENWFC_CONTEXT_LOG=context-display-surface-scratch-pipeline-thread
WFCLOG_CAPACITY=256
OPENWFC_ENGINE=source-built-standard-not-syborg-alias
OPENWFC_OUTPUT_FORMAT=rgb565-enabled
APPARC_DURABLE_LOG=server-start-list-scan-observer-completion
APPARC_FIRST_SCAN_POLICY=htcleo-synchronous-scan-and-icons-no-timer-later-rescans-stock
APPARC_RESTART_RECOVERY_POLICY=20B-20F-serverterminated-failopen
APPARC_RESTART_RECOGNIZER_POLICY=20D-serverterminated-null-guard
APALOG_CAPACITY=2048-two-module
APPARC_LAUNCH_LOG=apsexe-create-akncap-resume-return-property-signal-retained-and-thread-exit-category
AKNCAPCLIENT_PROPERTY_READY=fire-and-forget-no-request-no-timer-no-poll-property-retained
APASTART_CAPACITY=256
MATRIXMENU=source-built-uid-101f4cd2
MATRIXMENU_STACK_POLICY=htcleo-ui-shell-0x10000-gcce-aknlayoutrect-headroom
MATRIXMENU_LIFECYCLE_LOG=MENULOG.TXT-4D4D0000-4D4D0312-and-4D4D1000-4D4D1012
MATRIXMENU_LOG_CAPACITY=1048576-bytes-own-writer
MATRIXMENU_RUNTIME_EVENT_TRACE=ws-1200-1202-focus-1210-1221-foreground-1230-1241-exit-1290
HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH=visible-foreground-0f-focus-only-touch-rearm-no-ui-redraw
HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION=stale-own-wg-guard-real-wg-uid-tid-pid-stock-handoff-1206-120b
HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE=real-cba-homescreen-apparc-startapp-1400-1449-fixed-uid-bootstrap-only-on-missing-property
MATRIXMENU_STARTUP_FOREGROUND_COMMIT=real-root-task-panes-container-finish-0350-0354
MATRIXMENU_FOREGROUND_EVENT_POLICY=real-wg-ordinal-no-brought-to-foreground-system-event-0355-120a-1291
MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL=skip-when-focus-equals-root-0355-0356
HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT=high-priority-real-cba-refresh-after-grid-0372-0375
HTCLEO_TYPE2A_TOUCH_AUTOSTART=epointer-auto-extension-type2a-only-keys-medint-deferred
HTCLEO_TYPE2A_INPUT_IDENTITY=digitiser-primary-plus-legacy-mouse-hal-compat-480x800
HTCLEO_TYPE2A_RAW_PACKET_SNAPSHOT=current-two-words-points-transitions-functions6-9
HTCLEO_TYPE2A_TOUCH_DIAGNOSTIC=platformspecific2-stage-result-raw-packet-press-latched-samples-events-xy
HTCLEO_TYPE2A_TOUCH_TLMM_POLICY=proccomm-timeout-fixed-boot-mux-fallback-other-errors-failclosed
HTCLEO_TYPE2A_TOUCH_IRQ_READY_POLICY=runtime-gpio92-active-low-data-ready-gates-i2c-read
HTCLEO_TYPE2A_TOUCH_RESET_POLICY=3-bounded-full-power-cycles-gpio-readback-irq500ms-id-authoritative
HTCLEO_TYPE2A_TOUCH_POLL_POLICY=mutating-timer-dfcq0-gpio92-ready-gated-sample-again-fallback-oneshot
HTCLEO_QSD8K_GPT_CLOCK_POLICY=htcleo-divider3-32768hz-match32-periodic-clear-on-match
HTCLEO_QSD8K_VIC_VECTOR_POLICY=scorpion-prime-d0-pending-d4-ack-before-handler-drain-until-none
HTCLEO_TYPE2A_TOUCH_TICK_DIAGNOSTIC=pre-first-sample-vic-enable-irq-raw-gpt-enable-divider-count-nkern-tick
HTCLEO_QSD8K_I2C_POLLING_POLICY=clk-active-6us-write-delay-multibyte-rdfull-failclosed
HTCLEO_QSD8K_I2C_ERROR_POLICY=direct-output-phase8-lines2-status16-controller-stop-flush-recovery
HTCLEO_QSD8K_I2C_ABI=existing-read-write-exports-extended-caller-contract-no-new-symbols
HTCLEO_TYPE2A_TOUCH_I2C_DIAGNOSTIC=direct-output-phase8-lines2-status16
HTCLEO_TYPE2A_TOUCH_I2C_RETRY=init-only-17-attempts-10us-controller-recovery-sample-single
MATRIXMENU_SCHEDULER_ENTRY_KICK=retired-unowned-signal-1013-detail0-stock-scheduler-and-view
MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER=real-suite-direct-container-show-draw-0313-0318
MATRIXMENU_UI_FIRST_CONTAINER_COMPAT=real-widget-statuspane-0320-0333-no-startup-effect
MATRIXMENU_PRECONTAINER_SUITE_INIT_POLICY=defer-hidden-startup-callback-0334-real-sync-container-retained
MATRIXMENU_ROM_PRESENTATION_FALLBACK=foldersuite-first-grid-logical-template-3-0340-0342
MATRIXMENU_FIRST_FRAME_FINISH=post-drawview-wserv-finish-0319-031a-failclosed
MMWIDGETS_GRID_WINDOW_HANDLE=property-101f4cd2-7f4d5701-stage-0144
MATRIXMENU_STARTUP_POLICY=release-equivalent-local-eikstart-deferred-startapp-and-multiplewait-retained
MATRIXMENU_EXTENSION_POLICY=ui-first-defer-030f-4558544e-null-guards
MATRIXMENU_SKIN_SESSION_POLICY=late-haze-connect-after-first-frame-failopen-0310-0360-0362
HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION=post-first-frame-connect-setall-2000b12d-redraw-failopen-0360-0362
HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW=enable-notify-deployed-refresh-draw-finish-0363-0365
HTCLEO_MMWIDGETS_HAZE_BACKGROUND=qsn-bg-screen-existing-haze-item-no-fabricated-pixels
HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND=source-black-52a2a5-32-band-software-draw-0170-0171
HTCLEO_MMWIDGETS_TOUCH_DIAGNOSTIC=hal-172-17a-existing-redraw-snapshots-grid-pointer-180-181-readonly
HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION=real-widget-drawdeferred-fullrect-draw-finish-0370-0371
CUSTOM_COMMAND_LOG=akncustcmds-ordinal1-loader-factory-initialise-execute
CUSTOM_COMMAND_LOAD_SPLIT=connect-loadlibrary-handle-close-init-C100-C108
CUSTOM_COMMAND_INIT_TRACE=libraryattach-bootstrap-kernel-entrypoints-C201-CB26
CUSTOM_COMMAND_EXEC_STUB=thumb-entry-arm-swi-interworking
CUSTLOG_CAPACITY=512-two-module
EFILE_LOADER_TRACE=top-level-akncustcmds.dll
EFILE_LOADER_LOG=AKNLDR.TXT
SSMCMD_ABI=frozen-1-91-plus-private-timer-92-100
SCREEN_PROBE_RENDERERS=retired-hal-function2-and-kernel-exception
GATE11=hardware-pass-430
HARDWARE_FUNCTIONAL_BASELINE=430
SD_DEPLOYED=no
EOF

cat "$output/CANONICAL-RESULT.txt"
