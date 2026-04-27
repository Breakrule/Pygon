# Pygon v4.0 — Professional Developer Tools & Architectural Scaling

## Goal Description
Transition Pygon from a simple local server manager to a professional, scalable development suite. This involves adding advanced developer tools (Pygon Shell, Project-Based Versioning, Profiles), deep system integration (Tray Actions, Service Metrics), and a dynamic Extension System for community plugins.

## Proposed Changes

### 1. Per-Service Resource Monitoring
**Description**: Display real-time RAM and CPU usage per service to help identify bottlenecks.
**Implementation**:
- **`core/system_utils.py`**: Add `get_process_metrics(pid: int)` using `psutil`. Iterate through children of the PID to sum up memory and CPU %.
- **`ui/components/service_card.py`**: Add a small `QLabel` for metrics (e.g., "RAM: 45MB | CPU: 2%").
- **`pygon.py`**: Add a `QTimer` (`_metrics_timer`) running every 3 seconds. It iterates over `self.registry.get_all_services()`. For running services, it calls `get_process_metrics(service.process.pid)` and updates the card.

### 2. Pygon Shell Integration
**Description**: Launch a terminal with environment variables pre-configured for the active service versions (PHP, Node, MySQL).
**Implementation**:
- **`core/system_utils.py`**: Add `launch_pygon_shell(registry, config)`. 
  - Collect `get_actual_executable_path()` directories for all active services.
  - Prepend these directories to a copy of `os.environ['PATH']`.
  - Use `subprocess.Popen(['cmd.exe', '/K', 'echo Pygon Shell Initialized & prompt Pygon$G '], env=custom_env, creationflags=subprocess.CREATE_NEW_CONSOLE)`
- **`ui/components/top_bar.py`**: Add a "💻 Shell" button.
- **`pygon.py`**: Connect the shell button to `SystemUtils.launch_pygon_shell`.

### 3. Project-Based Version Mapping
**Description**: Assign different PHP versions to specific directories in `www/`.
**Implementation**:
- **`core/config_manager.py`**: Add `get_project_version(project_name)` and `set_project_version(project_name, version)`.
- **`core/host_manager.py`**: Modify the VirtualHost generator. Instead of using the global PHP FastCGI port, look up the project in config. If a specific version is set, generate a block pointing to that version's specific FastCGI port. 
- **`services/php.py`**: Modify to allow spawning multiple `php-cgi.exe` instances on different ports if multiple versions are required simultaneously by different projects.
- **UI Integration**: Add a context menu to the Modern Dashboard (see #6) to manage these mappings.

### 4. Tray Quick-Actions
**Description**: Full control of services directly from the Windows system tray.
**Implementation**:
- **`core/tray.py`**: Inject `ServiceController` into the tray manager.
- Build a dynamic `QMenu` for the `QSystemTrayIcon`.
- Add "Start All", "Stop All" actions.
- Add a separator, then dynamically add a submenu for each registered service (e.g., `Apache ▾ -> [Start, Stop, Restart]`).
- Ensure UI state stays in sync by emitting signals or relying on the existing `_update_ui_state` timer.

### 5. Service Profiles (Workspaces)
**Description**: Group configurations to quickly switch between stacks (e.g., "Laravel Stack", "Node Stack").
**Implementation**:
- **`core/config_manager.py`**: Add `profiles` dictionary. Add `save_profile(name)` and `load_profile(name)`.
- **`ui/components/top_bar.py`**: Add a `QComboBox` for Profile selection.
- **`pygon.py`**: On profile change, prompt user, call `controller.stop_all()`, load new config state, and `controller.start_all()`. Update UI dropdowns to match the loaded config.

### 6. Modern Dashboard
**Description**: A beautiful landing page for `localhost` listing all projects.
**Implementation**:
- **`core/dashboard_generator.py`**: Create a script that scans the `www/` directory and generates a static `index.html`.
- The HTML will use CSS matching Pygon's Neon Dark Mode and list all project folders as clickable cards.
- Links will point to `http://folder.test` (if mkcert virtual hosts are enabled) or `http://localhost/folder`.
- Hook this generator into the Apache/Nginx service start sequence or add a "Refresh Dashboard" button in the UI.

### 7. Extension System
**Description**: Allow drop-in community plugins without modifying core code.
**Implementation**:
- **How it works**: A new `plugins/` directory will be created. Users can drop a `.py` file containing a class that inherits from `BaseService`.
- **`services/registry.py`**: Update `load_services()` to scan both the internal `services/` directory and the external `plugins/` directory.
- Use `importlib.util.spec_from_file_location` to dynamically load external `.py` files safely.
- This allows the community to build support for PostgreSQL, MongoDB, Redis, etc., without waiting for official Pygon releases.

---

## Verification Plan

### Automated / Manual Tests
1. **Metrics**: Start MySQL. Open Windows Task Manager. Compare Pygon UI CPU/RAM values to Task Manager. They should closely align.
2. **Pygon Shell**: Click the Shell button. Type `php -v` and `node -v`. Ensure the output matches the versions currently selected in the Pygon UI, not the global Windows system PATH.
3. **Projects Mapping**: Set `project_a` to PHP 8.2 and `project_b` to PHP 8.4. Create an `info.php` in both folders. Access both via browser and verify the `PHP Version` output is different and matches the configuration.
4. **Tray Menu**: Right-click the system tray icon, select Apache -> Stop. Verify the main UI immediately reflects the offline status.
5. **Profiles**: Create a "Frontend Stack" (Disables Apache/PHP/MySQL, enables Node). Switch to this profile. Verify Apache stops and Node starts automatically.
6. **Dashboard**: Navigate to `http://localhost`. Verify the new Neon UI appears with an accurate list of folders in `www/`.
7. **Extensions**: Drop a dummy `redis_service.py` into the `plugins/` folder. Restart Pygon. Verify a "Redis" card automatically appears in the UI and functions correctly.
