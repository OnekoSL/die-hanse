#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use reqwest::blocking::Client;
use std::fs::{create_dir_all, OpenOptions};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use tauri::{AppHandle, Manager, RunEvent};

const API_HOST: &str = "127.0.0.1";
const API_PORT: u16 = 18522;
const HEALTH_TIMEOUT: Duration = Duration::from_secs(30);

#[cfg(windows)]
struct ProcessJob(windows_sys::Win32::Foundation::HANDLE);
#[cfg(windows)]
unsafe impl Send for ProcessJob {}
#[cfg(windows)]
impl Drop for ProcessJob {
    fn drop(&mut self) {
        unsafe {
            windows_sys::Win32::Foundation::CloseHandle(self.0);
        }
    }
}
#[cfg(windows)]
fn own_process_tree(child: &Child) -> Result<ProcessJob, Box<dyn std::error::Error>> {
    use std::os::windows::io::AsRawHandle;
    use windows_sys::Win32::System::JobObjects::*;
    unsafe {
        let handle = CreateJobObjectW(std::ptr::null(), std::ptr::null());
        if handle.is_null() {
            return Err(std::io::Error::last_os_error().into());
        }
        let job = ProcessJob(handle);
        let mut limits: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if SetInformationJobObject(
            handle,
            JobObjectExtendedLimitInformation,
            &limits as *const _ as *const _,
            std::mem::size_of_val(&limits) as u32,
        ) == 0
            || AssignProcessToJobObject(handle, child.as_raw_handle()) == 0
        {
            return Err(std::io::Error::last_os_error().into());
        }
        Ok(job)
    }
}

struct OwnedBackend {
    child: Child,
    #[cfg(windows)]
    _job: ProcessJob,
}
impl Drop for OwnedBackend {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}
struct AppState {
    backend: Mutex<Option<OwnedBackend>>,
}

fn main() {
    let result = tauri::Builder::default()
        .manage(AppState {
            backend: Mutex::new(None),
        })
        .setup(|app| {
            // Tauri runs setup inside its event loop and panics on returned errors.
            // Display our own diagnostic after start_backend has cleaned up its child.
            if let Err(error) = start_backend(app.handle()) {
                show_error(&format!("Die Hanse konnte nicht starten.\n\n{error}"));
                app.handle().exit(1);
            }
            Ok(())
        })
        .build(tauri::generate_context!());
    match result {
        Ok(app) => app.run(|handle, event| {
            if matches!(event, RunEvent::ExitRequested { .. } | RunEvent::Exit) {
                if let Ok(mut backend) = handle.state::<AppState>().backend.lock() {
                    backend.take();
                }
            }
        }),
        Err(error) => show_error(&format!("Die Hanse konnte nicht starten.\n\n{error}")),
    }
}

fn show_error(message: &str) {
    #[cfg(windows)]
    unsafe {
        use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};
        let body: Vec<u16> = message.encode_utf16().chain(Some(0)).collect();
        let title: Vec<u16> = "Die Hanse".encode_utf16().chain(Some(0)).collect();
        MessageBoxW(
            std::ptr::null_mut(),
            body.as_ptr(),
            title.as_ptr(),
            MB_OK | MB_ICONERROR,
        );
    }
    #[cfg(not(windows))]
    eprintln!("{message}");
}

fn start_backend(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    // No pid files and no killing/attaching to a process that we did not start.
    std::net::TcpListener::bind((API_HOST, API_PORT)).map_err(|_| {
        format!("Port {API_PORT} ist belegt. Die Hanse läuft möglicherweise bereits. Bitte das andere Fenster schließen.")
    })?;
    let app_data = app.path().app_data_dir()?;
    let data_dir = app_data.join("data");
    let log_dir = app_data.join("logs");
    create_dir_all(&data_dir)?;
    create_dir_all(&log_dir)?;
    let backend_path = resolve_backend_executable(app)?;
    let mut command = Command::new(&backend_path);
    command
        .env("HANSE_API_HOST", API_HOST)
        .env("HANSE_API_PORT", API_PORT.to_string())
        .env("HANSE_DB_PATH", data_dir.join("hanse.db"))
        .env("HANSE_SCENARIO_DIR", resolve_scenario_dir(app)?)
        .env(
            "HANSE_ALLOWED_ORIGINS",
            "tauri://localhost,http://tauri.localhost,https://tauri.localhost",
        )
        .stdin(Stdio::null())
        .stdout(Stdio::from(
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(log_dir.join("backend.stdout.log"))?,
        ))
        .stderr(Stdio::from(
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(log_dir.join("backend.stderr.log"))?,
        ));
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000); // CREATE_NO_WINDOW
    }
    let mut child = command.spawn()?;
    #[cfg(windows)]
    let job = match own_process_tree(&child) {
        Ok(job) => job,
        Err(error) => {
            let _ = child.kill();
            let _ = child.wait();
            return Err(error);
        }
    };
    let mut owned = OwnedBackend {
        child,
        #[cfg(windows)]
        _job: job,
    };
    // RAII kills the owned process even if readiness fails before storage in AppState.
    wait_for_health(&mut owned.child)?;
    *app.state::<AppState>()
        .backend
        .lock()
        .map_err(|_| "Backendzustand gesperrt")? = Some(owned);
    Ok(())
}

fn wait_for_health(child: &mut Child) -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::builder().timeout(Duration::from_secs(2)).build()?;
    let deadline = Instant::now() + HEALTH_TIMEOUT;
    while Instant::now() < deadline {
        if child.try_wait()?.is_some() {
            return Err(
                "Backend vorzeitig beendet. Details stehen im Anwendungsdatenordner unter logs."
                    .into(),
            );
        }
        if let Ok(response) = client
            .get(format!("http://{API_HOST}:{API_PORT}/api/v1/health"))
            .send()
        {
            if response.status().is_success() {
                let body = response.text()?;
                if body.contains("die-hanse") && child.try_wait()?.is_none() {
                    return Ok(());
                }
            }
        }
        thread::sleep(Duration::from_millis(100));
    }
    Err("Das Backend antwortet nicht. Der gestartete Prozess wurde beendet.".into())
}

fn resolve_backend_executable(app: &AppHandle) -> Result<PathBuf, Box<dyn std::error::Error>> {
    if let Ok(explicit) = std::env::var("HANSE_BACKEND_BIN") {
        let path = PathBuf::from(explicit);
        if path.exists() {
            return Ok(path);
        }
    }

    let exe_name = if cfg!(target_os = "windows") {
        "hanse-backend.exe"
    } else {
        "hanse-backend"
    };

    let mut candidates: Vec<PathBuf> = Vec::new();
    if let Ok(resource_dir) = app.path().resource_dir() {
        candidates.push(
            resource_dir
                .join("backend-dist")
                .join("hanse-backend")
                .join(exe_name),
        );
        candidates.push(
            resource_dir
                .join("_up_")
                .join("backend-dist")
                .join("hanse-backend")
                .join(exe_name),
        );
    }
    if let Ok(current_exe) = std::env::current_exe() {
        if let Some(exe_dir) = current_exe.parent() {
            candidates.push(
                exe_dir
                    .join("backend-dist")
                    .join("hanse-backend")
                    .join(exe_name),
            );
            candidates.push(
                exe_dir
                    .join("_up_")
                    .join("backend-dist")
                    .join("hanse-backend")
                    .join(exe_name),
            );
        }
    }

    for candidate in &candidates {
        if candidate.exists() {
            return Ok(candidate.clone());
        }
    }

    let searched = candidates
        .iter()
        .map(|path| path.display().to_string())
        .collect::<Vec<_>>()
        .join(", ");
    Err(format!("Backend-Binary nicht gefunden. Gesucht in: {searched}").into())
}

fn resolve_scenario_dir(app: &AppHandle) -> Result<PathBuf, Box<dyn std::error::Error>> {
    if let Ok(explicit) = std::env::var("HANSE_SCENARIO_DIR") {
        return Ok(PathBuf::from(explicit));
    }

    let mut candidates: Vec<PathBuf> = Vec::new();
    if let Ok(resource_dir) = app.path().resource_dir() {
        candidates.push(
            resource_dir
                .join("backend-dist")
                .join("data")
                .join("scenarios"),
        );
        candidates.push(
            resource_dir
                .join("_up_")
                .join("backend-dist")
                .join("data")
                .join("scenarios"),
        );
    }
    if let Ok(current_exe) = std::env::current_exe() {
        if let Some(exe_dir) = current_exe.parent() {
            candidates.push(exe_dir.join("backend-dist").join("data").join("scenarios"));
            candidates.push(
                exe_dir
                    .join("_up_")
                    .join("backend-dist")
                    .join("data")
                    .join("scenarios"),
            );
        }
    }

    for candidate in &candidates {
        if candidate.exists() {
            return Ok(candidate.clone());
        }
    }

    Err("Szenario-Daten nicht gefunden".into())
}
