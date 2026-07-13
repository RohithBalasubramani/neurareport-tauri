; Kill running NeuraReport processes before installing new files.
; This prevents "Error opening file for writing: MSVCP140.dll" when
; the backend is still running from a previous session.

!macro NSIS_HOOK_PREINSTALL
  ; Kill the Python backend sidecar
  nsExec::ExecToLog 'taskkill /F /IM neurareport-backend.exe'
  ; Kill the main Tauri app
  nsExec::ExecToLog 'taskkill /F /IM neurareport-desktop.exe'
  ; Brief pause to let file handles release
  Sleep 1000
!macroend

!macro NSIS_HOOK_POSTINSTALL
  ; --- Autostart: run in the system tray on every login ---
  ; Use a STARTUP-FOLDER SHORTCUT, not an HKCU\...\Run entry. A Run entry fires
  ; during early shell initialization — before WebView2 / the desktop is fully
  ; ready — so a WebView2 app launched that way on reboot frequently crashes and
  ; never shows its tray icon (works on install/close but not on restart). A
  ; Startup-folder shortcut launches AFTER the shell is ready and with the
  ; working directory set to the install folder, which is reliable for GUI apps.
  ; (Mirrors the reference agent-tray's Startup-folder shortcut approach.)
  SetShellVarContext current
  SetOutPath "$INSTDIR"                        ; -> shortcut's working directory
  CreateShortcut "$SMSTARTUP\NeuraReport.lnk" "$INSTDIR\neurareport-desktop.exe" "--minimized" "$INSTDIR\neurareport-desktop.exe" 0 SW_SHOWMINIMIZED

  ; Remove any legacy Run-key autostart from older installs (superseded).
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "NeuraReport"

  ; Start it now, minimized to the tray, so it is running immediately after
  ; install (no window, no manual launch needed).
  Exec '"$INSTDIR\neurareport-desktop.exe" --minimized'
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  ; Stop the running app + backend so files can be removed cleanly.
  nsExec::ExecToLog 'taskkill /F /IM neurareport-backend.exe'
  nsExec::ExecToLog 'taskkill /F /IM neurareport-desktop.exe'
  Sleep 500
  ; Remove the autostart shortcut + any legacy Run-key entry.
  SetShellVarContext current
  Delete "$SMSTARTUP\NeuraReport.lnk"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "NeuraReport"
!macroend
