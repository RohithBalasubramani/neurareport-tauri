use std::fs::OpenOptions;
use std::io::Write;
use std::sync::Mutex;
use tauri::Manager;

struct BackendState {
    port: u16,
    #[allow(dead_code)]
    child: Option<tauri_plugin_shell::process::CommandChild>,
    error: Option<String>,
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
                    .unwrap_or_else(|_| "8000".to_string())
                    .parse()
                    .unwrap_or(8000);
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
                use tauri_plugin_shell::ShellExt;

                // Production: spawn the PyInstaller-bundled backend sidecar
                let sidecar_result = app
                    .shell()
                    .sidecar("binaries/neurareport-backend")
                    .map(|cmd| cmd.args(["--port", &port.to_string()]));

                match sidecar_result {
                    Ok(sidecar) => {
                        match sidecar.spawn() {
                            Ok((mut rx, child)) => {
                                log("[tauri] Backend sidecar spawned successfully");

                                // Log sidecar output to file
                                tauri::async_runtime::spawn(async move {
                                    use tauri_plugin_shell::process::CommandEvent;
                                    while let Some(event) = rx.recv().await {
                                        match event {
                                            CommandEvent::Stdout(line) => {
                                                log(&format!(
                                                    "[backend] {}",
                                                    String::from_utf8_lossy(&line)
                                                ));
                                            }
                                            CommandEvent::Stderr(line) => {
                                                log(&format!(
                                                    "[backend:err] {}",
                                                    String::from_utf8_lossy(&line)
                                                ));
                                            }
                                            CommandEvent::Terminated(status) => {
                                                log(&format!(
                                                    "[backend] Process terminated: {:?}",
                                                    status
                                                ));
                                            }
                                            _ => {}
                                        }
                                    }
                                });

                                app.manage(Mutex::new(BackendState {
                                    port,
                                    child: Some(child),
                                    error: None,
                                }));

                                // Health-check: wait for backend to be ready
                                let health_port = port;
                                tauri::async_runtime::spawn(async move {
                                    for i in 0..60 {
                                        tokio::time::sleep(std::time::Duration::from_millis(500))
                                            .await;
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
                                let msg = format!("Failed to spawn backend sidecar: {}", e);
                                log(&format!("[tauri] ERROR: {}", msg));
                                app.manage(Mutex::new(BackendState {
                                    port,
                                    child: None,
                                    error: Some(msg),
                                }));
                            }
                        }
                    }
                    Err(e) => {
                        let msg = format!("Failed to create sidecar command: {}", e);
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
                let managed = window.state::<Mutex<BackendState>>();
                let child = managed.lock().ok().and_then(|mut s| s.child.take());
                if let Some(child) = child {
                    log("[tauri] Killing backend process");
                    let _ = child.kill();
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            get_backend_port,
            get_backend_url,
            get_startup_error
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
