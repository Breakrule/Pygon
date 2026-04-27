# Pygon v3.1 — UI/UX Overhaul, Port Management & Version Updates

## Background

Pygon v3.0 successfully migrated from CustomTkinter to PyQt6. However, several
visual and functional issues remain:

- **Light theme is broken** — text and buttons disappear or become invisible
  against the background due to insufficient contrast in the light color palette
- **Right-click context menu** renders with wrong styling and clipped content
- **Settings dialog** is minimal — just a few checkboxes, no port editing
- **Icons** use plain Unicode emoji which render inconsistently across systems
- **No way to change service ports** without manually editing `config.yaml`
- **MySQL** only ships 8.0.36; users need access to the latest 9.x series
- **No version check mechanism** — users can't tell if newer binaries are available

## Scope

> [!IMPORTANT]
> This issue targets **UI/UX improvements and new features only**. The `services/`
> layer and `core/` business logic remain untouched except for adding MySQL 9.6.0
> download URL and a version-check utility.

---

## Proposed Changes

### 1. Fix Light/Dark Theme Contrast

**Problem**: In light mode, buttons use `card` color (`#F1F5F9`) as background
which is nearly identical to the `surface` (`#FFFFFF`) and `bg` (`#F8FAFC`).
The `DimText` color (`#64748B`) doesn't have enough contrast on light cards.
Context menu text inherits wrong colors.

#### [MODIFY] [theme.py](file:///d:/Developers/Projects/Pygon/ui/theme.py)

**Light palette fixes:**
| Token | Current | Fixed | Rationale |
|---|---|---|---|
| `card` | `#F1F5F9` | `#FFFFFF` | White cards on light gray bg for clear separation |
| `card_hover` | `#E2E8F0` | `#F1F5F9` | Subtle hover on white |
| `surface` | `#FFFFFF` | `#F1F5F9` | Swap — surface is the panel, card sits on top |
| `text_dim` | `#64748B` | `#475569` | Darker dim text for readability |
| `console_bg` | `#F8FAFC` | `#FFFFFF` | Brighter console for contrast with text |

**QSS additions for both themes:**
- Add explicit `QMenu::item` padding and text color
- Add `QComboBox::drop-down` border styling
- Add `QScrollBar` styling (currently uses ugly system default)
- Add `QPushButton#DatabaseButton` style — a distinct blue variant
- Add `QDialog` background rule to prevent transparent dialogs
- Add `QSpinBox` styling for the new port editor

---

### 2. Fix Right-Click Context Menu

**Problem**: `contextMenuEvent` on `ServiceCard` calls `self.on_menu(self.service, self)`
passing the card frame as anchor. `_show_service_menu` then calls
`anchor.mapToGlobal(anchor.rect().bottomLeft())` which positions the menu at the
bottom of the entire card — often offscreen. The menu itself has no padding or
separator support.

#### [MODIFY] [service_card.py](file:///d:/Developers/Projects/Pygon/ui/components/service_card.py)
- Pass `event.globalPos()` from `contextMenuEvent` instead of `self`
- Override `contextMenuEvent(self, event)` to use `event.globalPos()`

#### [MODIFY] [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py) — `_show_service_menu`
- Accept `QPoint` or `QPushButton` as anchor
- Add separator between action groups (restart | config files | tools)
- Add icons to menu items using `QIcon` with colored pixmaps

---

### 3. Redesign Main App Layout

**Current layout**: Two-column with left services panel + right console, no visual
hierarchy between the top bar, services, and system info.

**New layout**: Clean single-pane layout with collapsible console.

#### [MODIFY] [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py) — `_build_ui`

```
┌─────────────────────────────────────────────────┐
│  ⚡ Pygon               [🔍 Check Updates] [⚙] [☀]│  ← TopBar
├─────────────────────────────────────────────────┤
│  Services                        [▶ START ALL] │  ← Section Header
│  ┌─────────────────────────────────────────┐    │
│  │ 🐬 MySQL Database    8.0.36 ▾ [DB][START]│    │  ← ServiceCard
│  │ 🦭 MariaDB Database  11.4.2 ▾ [DB][START]│    │
│  │ 🌐 Apache Web Server 2.4.66 ▾    [START]│    │
│  │ ⬢  Node.js Service   20.20 ▾     [START]│    │
│  │ 🐘 PHP Version       8.4.4 ▾     [START]│    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐                      │  ← System Info
│  │ CPU │ │ RAM │ │ DISK│                       │
│  │ 23% │ │ 67% │ │ 45% │                      │
│  └─────┘ └─────┘ └─────┘                      │
├─────────────────────────────────────────────────┤
│  Console  Logs  Errors              [🗑 Clear] │  ← ConsolePanel (bottom)
│  [00:15:32] Started MySQL Database (PID: 1234) │
│  [00:15:33] Started Apache Web Server...       │
└─────────────────────────────────────────────────┘
│ ● MySQL: Online  ● Apache: Offline  ● PHP: ... │  ← StatusBar
└─────────────────────────────────────────────────┘
```

Key changes:
- Full-width layout (no side-by-side columns) — more room for service cards
- Console moves to bottom panel with `QSplitter` (user-resizable)
- Service cards are wider, cleaner
- "Check Updates" button in top bar

---

### 4. Redesign Settings Dialog

**Current**: Minimal — 2 tabs (General with 1 checkbox, Services with enable/disable)

#### [MODIFY] [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py) — `_open_settings`

New settings dialog with 3 tabs:

**Tab 1: General**
- Run on startup (checkbox)
- Close behavior (radio: Ask / Minimize to Tray / Exit)
- Document root path (text + browse button)
- Auto-start services on launch (checkbox)

**Tab 2: Services**
- For each service: row with `[Enable ✓] [Name] [Port: ___] [Version: ▾]`
- Port is editable via `QSpinBox` (range 1–65535)
- Changes save immediately to `config.yaml` via `config.set_service_port()`
- Warning label: "Port changes take effect on next service restart"

**Tab 3: About**
- App name + version
- Links: GitHub, Documentation
- System info: Python version, Qt version, OS

---

### 5. Improve Icons

**Problem**: Unicode emoji render differently across Windows versions and font
settings. Some (like ⚡, ⚙, ☀, 🌙) may appear as black boxes or squares.

#### [MODIFY] [top_bar.py](file:///d:/Developers/Projects/Pygon/ui/components/top_bar.py)
- Replace emoji with SVG-style `QIcon` generated from `QPainter` on `QPixmap`
- Theme toggle: draw sun/moon as simple geometric shapes
- Settings: draw gear icon

#### [MODIFY] [service_card.py](file:///d:/Developers/Projects/Pygon/ui/components/service_card.py)
- Replace emoji icon labels with 2-letter text badges rendered on colored circles
  (e.g., "My" for MySQL, "Md" for MariaDB, "Ap" for Apache, "Nd" for Node, "Ph" for PHP)
- This guarantees consistent rendering across all Windows versions

#### Icon Mapping
| Service | Badge | Color |
|---|---|---|
| MySQL Database | My | `#4479A1` |
| MariaDB Database | Md | `#003545` |
| Apache Web Server | Ap | `#D22128` |
| Node.js Service | Nd | `#339933` |
| PHP Version | Ph | `#777BB4` |
| Nginx Web Server | Nx | `#009639` |
| Redis Cache | Rd | `#DC382D` |
| PostgreSQL Database | Pg | `#336791` |
| Mail Server | Mp | `#4A90D9` |

---

### 6. Port Management in Settings

#### [MODIFY] [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py) — `_open_settings` (Services tab)
- Each service row gets a `QSpinBox` for port (pre-filled from `config.get_service_port()`)
- On value change → `config.set_service_port(service.name, new_port)`
- Service card's `port_lbl` auto-updates on next UI tick

#### No changes needed to:
- `config_manager.py` — `get_service_port` / `set_service_port` already exist
- `services/base.py` — `current_port` property already reads from config

---

### 7. Add MySQL 9.6.0

#### [MODIFY] [downloader.py](file:///d:/Developers/Projects/Pygon/core/downloader.py)
- Add second URL entry: `"mysql-9.6"` → `https://dev.mysql.com/get/Downloads/MySQL-9.0/mysql-9.6.0-winx64.zip`
- The downloader's versioned folder logic will place it in `bin/mysql/9.6.0/`
- User can then switch between 8.0.36 and 9.6.0 via the dropdown

> [!WARNING]
> MySQL 9.x uses `caching_sha2_password` by default. The `my.ini` generator in
> `services/mysql.py` should NOT include `default_authentication_plugin=mysql_native_password`
> for version 9.x, as it is fully removed. A version check should conditionally
> include this directive.

#### [MODIFY] [mysql.py](file:///d:/Developers/Projects/Pygon/services/mysql.py) — `pre_start`
- Detect version from `active_version` string
- If version starts with `8.`: include `default_authentication_plugin=mysql_native_password`
- If version starts with `9.`: omit it

---

### 8. Check Services Latest Version Button

#### [NEW] `core/version_checker.py`
- `VersionChecker` class with static method `check_latest(service_name: str) -> dict`
- Returns `{"current": "8.0.36", "latest": "8.0.40", "update_available": True}`
- Sources:
  - **MySQL**: scrape `https://dev.mysql.com/downloads/mysql/` for latest version string
  - **PHP**: scrape `https://www.php.net/downloads.php`
  - **Node.js**: fetch `https://nodejs.org/dist/index.json` (JSON API)
  - **Apache**: scrape `https://www.apachelounge.com/download/`
  - **MariaDB**: fetch `https://downloads.mariadb.org/rest-api/mariadb/`

#### [MODIFY] [top_bar.py](file:///d:/Developers/Projects/Pygon/ui/components/top_bar.py)
- Add "🔄 Check Updates" button between stretch and settings button

#### [MODIFY] [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py)
- Add `_check_updates` callback
- Run version checks in background thread
- Show results in a `QDialog` table:
  `| Service | Installed | Latest | Status |`
  `| MySQL   | 8.0.36    | 8.0.40 | ⚠ Update |`
  `| PHP     | 8.4.4     | 8.4.4  | ✅ Latest |`
- "Download" button per row to trigger `download_and_extract` for the new version

---

## Files Summary

| File | Action | Description |
|---|---|---|
| [theme.py](file:///d:/Developers/Projects/Pygon/ui/theme.py) | MODIFY | Fix light palette, add QMenu/QScrollBar/QSpinBox/QDialog styles |
| [base_window.py](file:///d:/Developers/Projects/Pygon/ui/base_window.py) | MODIFY | No structural change, minor cleanup |
| [top_bar.py](file:///d:/Developers/Projects/Pygon/ui/components/top_bar.py) | MODIFY | QPainter icons, add Check Updates button |
| [service_card.py](file:///d:/Developers/Projects/Pygon/ui/components/service_card.py) | MODIFY | Text badges, fix contextMenuEvent, wider layout |
| [system_info.py](file:///d:/Developers/Projects/Pygon/ui/components/system_info.py) | MODIFY | Minor style tweaks for consistency |
| [console_panel.py](file:///d:/Developers/Projects/Pygon/ui/components/console_panel.py) | MODIFY | Ensure text color works in both themes |
| [pygon.py](file:///d:/Developers/Projects/Pygon/pygon.py) | MODIFY | New layout, settings redesign, menu fixes, version check UI |
| [downloader.py](file:///d:/Developers/Projects/Pygon/core/downloader.py) | MODIFY | Add MySQL 9.6.0 URL |
| [mysql.py](file:///d:/Developers/Projects/Pygon/services/mysql.py) | MODIFY | Conditional auth plugin based on version |
| [version_checker.py](file:///d:/Developers/Projects/Pygon/core/version_checker.py) | NEW | Latest version detection for all services |

---

## Verification Plan

### Visual Audit
- Toggle dark ↔ light theme: all text readable, all buttons visible, no clipping
- Right-click any service card: menu appears at cursor position
- Settings dialog: port spinboxes accept valid input, reject < 1 or > 65535
- Screenshot comparison at 100%, 125%, 150% DPI

### Functional Test
- Change MySQL port in settings → restart → verify `my.ini` reflects new port
- Download MySQL 9.6.0 → switch version in dropdown → start → confirm `ready for connections`
- Click "Check Updates" → background fetch completes → dialog shows results
- Close dialog without crash

### Regression
- All existing services (Apache, PHP, Node, MySQL 8.0, MariaDB) start/stop correctly
- HeidiSQL auto-connect still works with changed ports
- Config.yaml preserves all settings after modification
