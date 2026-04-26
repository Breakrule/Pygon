# Pygon v2.0 — Major Refactor & UI Redesign [COMPLETED]

The major v2.0 refactor is now complete. The project has been stripped to 4 core services, the UI/UX has been modernized with a new theme system, and all requested behavioral fixes (tray, close dialog, version switching, node runtime) have been implemented.

## User Review Required

> [!IMPORTANT]
> **Service Removal**: The following service files will be **permanently deleted** from the project:
> - `services/nginx.py`
> - `services/postgresql.py`
> - `services/redis.py`
> - `services/mailpit.py`
>
> The dynamic `ServiceRegistry` pattern is preserved, so re-adding them later is just dropping a new `.py` file into `services/`.

> [!WARNING]
> **Breaking Change — Close Button Behavior**: Currently, clicking `X` hides to tray silently. The new behavior will present a dialog asking the user to choose between "Minimize to Tray" or "Exit & Kill All Services". This is a deliberate UX change per your request. The dialog can be suppressed via a "Remember my choice" checkbox in Preferences.

## Open Questions

1. **Version Download Strategy**: For multi-version support (e.g., PHP 8.1, 8.2, 8.3, 8.4), should the `AutoDownloader` be updated with URLs for each version, or should users manually place version folders into `bin/php/`?
2. **Apache + PHP Integration**: When the user switches PHP version, should Pygon automatically patch the Apache `httpd.conf` to load the correct `php_module` DLL from the selected PHP version folder? This is the Laragon-style behavior.
3. **Node.js Usage Pattern**: Node.js doesn't run as a persistent "server" like Apache/MySQL. Currently it just launches `node.exe`. Should it instead serve as a "managed runtime" (user points it at a project and Pygon runs `npm run dev`)?

---

## Proposed Changes

### Phase 1: Service Layer Cleanup
Strip the project to 4 core services. Remove dead code and the unused legacy `ServiceManager`.
- **DELETE**: `services/nginx.py`, `services/postgresql.py`, `services/redis.py`, `services/mailpit.py`.
- **DELETE**: `core/service_manager.py` (Superseded by `BaseService`).
- **MODIFY**: `downloader.py` (Trim URLs, remove Nginx patching).

### Phase 2: Version Switching System
- **MODIFY**: `base.py` (Add restart-on-version-change logic).
- **MODIFY**: `php.py`, `nodejs.py` (Implement version display parsing).

### Phase 3: UI/UX Redesign
- **RETHEME**: Overhaul colors (HSL-based), refine dark/light modes.
- **REDESIGN**: Service cards with prominent version dropdowns.
- **STREAMLINE**: Remove clutter (excessive panels, placeholder menus).

### Phase 4: Close/Tray Behavior Fix
- **NEW**: Close dialog with "Minimize to Tray" vs "Exit & Kill Services".
- **MODIFY**: `tray.py` (Simplified menu).
- **FIX**: Ensure `exit_app()` kills all background processes reliably.

### Phase 5: Cleanup & Lightweight Optimization
- **OPTIMIZE**: Remove all dead references to deleted services.
- **VHOST**: Switch Nginx vhost template to Apache.
