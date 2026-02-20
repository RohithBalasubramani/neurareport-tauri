use std::sync::Mutex;
use tauri::Manager;

struct BackendState {
    port: u16,
    #[allow(dead_code)]
    child: Option<tauri_plugin_shell::process::CommandChild>,
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

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            let port = portpicker::pick_unused_port().expect("No free port available");
            println!("[tauri] Selected port {} for backend", port);

            #[cfg(debug_assertions)]
            {
                // Dev mode: backend is started manually, Vite proxy handles routing.
                // Just store the port (default 8000) for reference.
                let dev_port: u16 = std::env::var("NEURA_DEV_PORT")
                    .unwrap_or_else(|_| "8000".to_string())
                    .parse()
                    .unwrap_or(8000);
                println!(
                    "[tauri] Dev mode — expecting backend on port {} (set NEURA_DEV_PORT to override)",
                    dev_port
                );
                app.manage(Mutex::new(BackendState {
                    port: dev_port,
                    child: None,
                }));
                return Ok(());
            }

            #[cfg(not(debug_assertions))]
            {
                use tauri_plugin_shell::ShellExt;

                // Production: spawn the PyInstaller-bundled backend sidecar
                let sidecar = app
                    .shell()
                    .sidecar("binaries/neurareport-backend")
                    .expect("Failed to create sidecar command")
                    .args(["--port", &port.to_string()]);

                let (mut rx, child) = sidecar.spawn().expect("Failed to spawn backend sidecar");

                // Log sidecar output
                tauri::async_runtime::spawn(async move {
                    use tauri_plugin_shell::process::CommandEvent;
                    while let Some(event) = rx.recv().await {
                        match event {
                            CommandEvent::Stdout(line) => {
                                println!("[backend] {}", String::from_utf8_lossy(&line));
                            }
                            CommandEvent::Stderr(line) => {
                                eprintln!("[backend] {}", String::from_utf8_lossy(&line));
                            }
                            CommandEvent::Terminated(status) => {
                                eprintln!("[backend] Process terminated: {:?}", status);
                            }
                            _ => {}
                        }
                    }
                });

                app.manage(Mutex::new(BackendState {
                    port,
                    child: Some(child),
                }));

                // Health-check: wait for backend to be ready
                let health_port = port;
                tauri::async_runtime::spawn(async move {
                    let url = format!("http://127.0.0.1:{}/health", health_port);
                    for i in 0..60 {
                        tokio::time::sleep(std::time::Duration::from_millis(500)).await;
                        match tokio::net::TcpStream::connect(format!("127.0.0.1:{}", health_port))
                            .await
                        {
                            Ok(_) => {
                                println!(
                                    "[tauri] Backend ready on port {} (after {}ms)",
                                    health_port,
                                    (i + 1) * 500
                                );
                                return;
                            }
                            Err(_) => continue,
                        }
                    }
                    eprintln!("[tauri] WARNING: Backend did not start within 30 seconds");
                });

                Ok(())
            }
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                let managed = window.state::<Mutex<BackendState>>();
                let child = managed.lock().ok().and_then(|mut s| s.child.take());
                if let Some(child) = child {
                    println!("[tauri] Killing backend process");
                    let _ = child.kill();
                }
            }
        })
        .invoke_handler(tauri::generate_handler![get_backend_port, get_backend_url])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
