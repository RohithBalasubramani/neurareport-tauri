use std::fs::OpenOptions;
use std::io::Write;
use std::sync::Mutex;
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::Manager;

struct BackendState {
    port: u16,
    child: Option<std::process::Child>,
    error: Option<String>,
}

impl Drop for BackendState {
    fn drop(&mut self) {
        if let Some(ref mut child) = self.child {
            let _ = child.kill();
        }
    }
}

fn log_file_path() -> std::path::PathBuf {
    let dir = dirs::data_dir()
        .unwrap_or_else(|| std::path::PathBuf::from("."))
        .join("com.neurareport.desktop");
    let _ = std::fs::create_dir_all(&dir);
    dir.join("neurareport.log")
}

fn log(msg: &str) {
    let path = log_file_path();
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&path) {
        let ts = chrono::Local::now().format("%Y-%m-%d %H:%M:%S");
        let _ = writeln!(f, "[{}] {}", ts, msg);
    }
    println!("{}", msg);
}

#[tauri::command]
fn get_backend_port(state: tauri::State<'_, Mutex<BackendState>>) -> u16 {
    state.lock().unwrap().port
}

#[tauri::command]
fn get_backend_url(state: tauri::State<'_, Mutex<BackendState>>) -> String {
    let port = state.lock().unwrap().port;
    format!("http://127.0.0.1:{}", port)
}

#[tauri::command]
fn get_startup_error(state: tauri::State<'_, Mutex<BackendState>>) -> Option<String> {
    state.lock().unwrap().error.clone()
}

/// Check if the backend is reachable via TCP.  Called from the frontend
/// health-check loop so the request never touches browser CORS / CSP.
#[tauri::command]
async fn check_backend_health(state: tauri::State<'_, Mutex<BackendState>>) -> Result<bool, String> {
    let port = state.lock().map_err(|e| e.to_string())?.port;
    match tokio::net::TcpStream::connect(format!("127.0.0.1:{}", port)).await {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

/// Find the backend executable inside the bundled resources folder.
///
/// The `tauri.conf.json` resources config `"neurareport-backend": "./"` copies
/// the PyInstaller output directory's *contents* into the resource root, so
/// the binary is at `<resource_dir>/neurareport-backend` (not in a subdirectory).
fn find_backend_exe(app: &tauri::App) -> Result<std::path::PathBuf, String> {
    let resource_dir = app
        .path()
        .resource_dir()
        .map_err(|e| format!("Cannot resolve resource dir: {}", e))?;

    #[cfg(target_os = "windows")]
    let exe_name = "neurareport-backend.exe";
    #[cfg(not(target_os = "windows"))]
    let exe_name = "neurareport-backend";

    // Primary: resource root (matches resource map config)
    let exe_path = resource_dir.join(exe_name);
    if exe_path.exists() {
        return Ok(exe_path);
    }

    // Fallback: nested subdirectory (for alternative resource configs)
    let nested = resource_dir.join("neurareport-backend").join(exe_name);
    if nested.exists() {
        return Ok(nested);
    }

    Err(format!(
        "Backend exe not found at {:?} or {:?}",
        exe_path, nested
    ))
}

/// Show + focus the main window (from a tray click or the tray menu).
fn show_main_window(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.show();
        let _ = w.unminimize();
        let _ = w.set_focus();
    }
}

/// Kill the spawned backend before a real quit (from the tray "Quit" item).
fn kill_backend(app: &tauri::AppHandle) {
    if let Some(state) = app.try_state::<Mutex<BackendState>>() {
        if let Ok(mut s) = state.lock() {
            if let Some(ref mut child) = s.child {
                log("[tauri] Killing backend process (quit)");
                let _ = child.kill();
            }
        }
    }
}

pub fn run() {
    tauri::Builder::default()
        // Single-instance must be the FIRST plugin. If a second copy is
        // launched (double-clicking the icon while it's already in the tray,
        // or the login autostart firing while it's running), we surface the
        // existing window instead of starting a second backend + scheduler
        // (which would double-send emails).
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            show_main_window(app);
        }))
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            log("[tauri] NeuraReport desktop starting...");

            // --- System tray ---------------------------------------------
            // Keeps the app (and its child backend + report scheduler) alive
            // in the background when the window is closed, so scheduled reports
            // and Run Now keep working without the window open. A real quit
            // happens only via the tray "Quit" item.
            let open_i =
                MenuItem::with_id(app, "open", "Open NeuraReport", true, None::<&str>)?;
            let quit_i =
                MenuItem::with_id(app, "quit", "Quit NeuraReport", true, None::<&str>)?;
            let tray_menu = Menu::with_items(app, &[&open_i, &quit_i])?;
            let mut tray_builder = TrayIconBuilder::with_id("main-tray")
                .tooltip("NeuraReport")
                .menu(&tray_menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "open" => show_main_window(app),
                    "quit" => {
                        kill_backend(app);
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        show_main_window(tray.app_handle());
                    }
                });
            if let Some(icon) = app.default_window_icon() {
                tray_builder = tray_builder.icon(icon.clone());
            }
            let _tray = tray_builder.build(app)?;

            // Autostart is registered by the NSIS installer (a HKCU\...\Run
            // "NeuraReport" entry that launches the app with --minimized), so
            // there's nothing to self-register here.

            // The main window is created hidden (visible:false in config).
            // Show it on a normal launch; keep it tray-only when auto-started
            // at login (--minimized) — avoids a window flash on every boot.
            let autostarted = std::env::args().any(|a| a == "--minimized");
            if let Some(w) = app.get_webview_window("main") {
                if autostarted {
                    let _ = w.hide();
                } else {
                    let _ = w.show();
                    let _ = w.set_focus();
                }
            }

            let port = portpicker::pick_unused_port().unwrap_or(9070);
            log(&format!("[tauri] Selected port {} for backend", port));

            #[cfg(debug_assertions)]
            {
                let dev_port: u16 = std::env::var("NEURA_DEV_PORT")
                    .unwrap_or_else(|_| "9070".to_string())
                    .parse()
                    .unwrap_or(9070);
                log(&format!(
                    "[tauri] Dev mode — expecting backend on port {} (set NEURA_DEV_PORT to override)",
                    dev_port
                ));
                app.manage(Mutex::new(BackendState {
                    port: dev_port,
                    child: None,
                    error: None,
                }));
                return Ok(());
            }

            #[cfg(not(debug_assertions))]
            {
                // Production: launch backend from resources folder
                let backend_exe = match find_backend_exe(app) {
                    Ok(path) => {
                        log(&format!("[tauri] Found backend at {:?}", path));
                        path
                    }
                    Err(e) => {
                        log(&format!("[tauri] ERROR: {}", e));
                        app.manage(Mutex::new(BackendState {
                            port,
                            child: None,
                            error: Some(e),
                        }));
                        return Ok(());
                    }
                };

                // Set execute permission on Linux/macOS
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let _ = std::fs::set_permissions(
                        &backend_exe,
                        std::fs::Permissions::from_mode(0o755),
                    );
                }

                use std::process::{Command, Stdio};

                let mut cmd = Command::new(&backend_exe);
                cmd.args(["--port", &port.to_string()])
                    .env("PYTHONUNBUFFERED", "1")
                    // Desktop app is always a local/trusted environment
                    .env("NEURA_DEBUG", "true")
                    .env("NEURA_ALLOWED_HOSTS_ALL", "true")
                    .env("NEURA_JWT_SECRET", "neurareport-desktop-local")
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped());

                // Hide the console window on Windows
                #[cfg(target_os = "windows")]
                {
                    use std::os::windows::process::CommandExt;
                    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
                }

                match cmd.spawn()
                {
                    Ok(mut child) => {
                        log("[tauri] Backend process spawned successfully");

                        // Capture stdout in background thread
                        if let Some(stdout) = child.stdout.take() {
                            std::thread::spawn(move || {
                                use std::io::BufRead;
                                let reader = std::io::BufReader::new(stdout);
                                for line in reader.lines() {
                                    if let Ok(line) = line {
                                        log(&format!("[backend] {}", line));
                                    }
                                }
                            });
                        }

                        // Capture stderr in background thread
                        if let Some(stderr) = child.stderr.take() {
                            std::thread::spawn(move || {
                                use std::io::BufRead;
                                let reader = std::io::BufReader::new(stderr);
                                for line in reader.lines() {
                                    if let Ok(line) = line {
                                        log(&format!("[backend:err] {}", line));
                                    }
                                }
                            });
                        }

                        app.manage(Mutex::new(BackendState {
                            port,
                            child: Some(child),
                            error: None,
                        }));

                        // Health-check: wait for backend to be ready
                        let health_port = port;
                        tauri::async_runtime::spawn(async move {
                            for i in 0..60 {
                                tokio::time::sleep(std::time::Duration::from_millis(500)).await;
                                match tokio::net::TcpStream::connect(format!(
                                    "127.0.0.1:{}",
                                    health_port
                                ))
                                .await
                                {
                                    Ok(_) => {
                                        log(&format!(
                                            "[tauri] Backend ready on port {} (after {}ms)",
                                            health_port,
                                            (i + 1) * 500
                                        ));
                                        return;
                                    }
                                    Err(_) => continue,
                                }
                            }
                            log("[tauri] WARNING: Backend did not start within 30 seconds");
                        });
                    }
                    Err(e) => {
                        let msg = format!("Failed to spawn backend: {}", e);
                        log(&format!("[tauri] ERROR: {}", msg));
                        app.manage(Mutex::new(BackendState {
                            port,
                            child: None,
                            error: Some(msg),
                        }));
                    }
                }

                Ok(())
            }
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                // Close-to-tray: hide the window instead of quitting so the
                // backend + report scheduler keep running in the background.
                // The backend is only stopped on a real quit (tray "Quit").
                log("[tauri] Window close -> hiding to tray (backend stays alive)");
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![
            get_backend_port,
            get_backend_url,
            get_startup_error,
            check_backend_health
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
