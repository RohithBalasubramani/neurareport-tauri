use std::fs::OpenOptions;
use std::io::Write;
use std::sync::Mutex;
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

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            log("[tauri] NeuraReport desktop starting...");

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
            if let tauri::WindowEvent::Destroyed = event {
                let managed: tauri::State<'_, Mutex<BackendState>> = window.state();
                let mut state = managed.lock().unwrap();
                if let Some(ref mut child) = state.child {
                    log("[tauri] Killing backend process");
                    let _ = child.kill();
                }
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
