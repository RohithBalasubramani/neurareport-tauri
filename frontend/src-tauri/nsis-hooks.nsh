; Kill running NeuraReport processes before installing new files.
; This prevents "Error opening file for writing: MSVCP140.dll" when
; the backend is still running from a previous session.

!macro NSIS_HOOK_PREINSTALL
  ; Kill the Python backend sidecar
  nsExec::ExecToLog 'taskkill /F /IM neurareport-backend.exe'
  ; Kill the main Tauri app
  nsExec::ExecToLog 'taskkill /F /IM NeuraReport.exe'
  ; Brief pause to let file handles release
  Sleep 1000
!macroend

!macro NSIS_HOOK_POSTINSTALL
  ; --- Autostart: run in the system tray on every login ---
  ; The app is registered to launch minimized (no window) at login, so the
  ; report scheduler keeps working without the user ever opening the app.
  ; The value name "NeuraReport" matches the app's own autostart plugin on
  ; other OSes, and the Rust side skips self-registration on Windows, so
  ; there is exactly ONE Run entry (no double-launch).
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "NeuraReport" '"$INSTDIR\NeuraReport.exe" --minimized'

  ; Start it now, minimized to the tray, so it is running immediately after
  ; install (no window, no manual launch needed).
  Exec '"$INSTDIR\NeuraReport.exe" --minimized'
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  ; Stop the running app + backend so files can be removed cleanly.
  nsExec::ExecToLog 'taskkill /F /IM neurareport-backend.exe'
  nsExec::ExecToLog 'taskkill /F /IM NeuraReport.exe'
  Sleep 500
  ; Remove the autostart entry.
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "NeuraReport"
!macroend
