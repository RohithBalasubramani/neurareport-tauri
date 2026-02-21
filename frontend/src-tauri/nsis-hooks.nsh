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
