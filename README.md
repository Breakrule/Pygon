# ⚡ Pygon v4.1.0: Professional Development Suite

**Pygon** is a lightweight, portable, and visually stunning local development suite for Windows. Designed for speed, aesthetic excellence, and a premium developer experience, it provides a high-performance alternative to XAMPP and Laragon with a modern, sidebar-driven interface.

## 🌌 The v4.1.0 Overhaul
Pygon v4.1.0 introduces a complete architectural and visual redesign. Transitioning from traditional top-bar navigation to a **modern Sidebar-Workspace model**, the interface now features a premium Slate and Tech Blue palette, high-end Inter typography, and refined service controls.

## 🚀 Key Features

- **Sidebar Architecture**: Sleek navigation with dedicated sections for Dashboard, Shell, Terminal, and Tools.
- **Portable Core**: Single standalone executable. Move your development environment anywhere on a USB drive.
- **Service Mastery**: One-click control for your entire stack with icon-based toggles:
  - **Web Servers**: Apache, Nginx
  - **Languages**: PHP (Seamless version switching), Node.js (Integrated NPM support)
  - **Databases**: MySQL 8.x/9.x, MariaDB
  - **Tools**: Mailpit, HeidiSQL integration
- **Premium Themes**: High-contrast Dark and Clean Light modes with custom SVG assets and smooth interaction states.
- **Auto-Downloader**: Missing a service? Pygon fetches the binaries and sets them up for you instantly.
- **Local SSL**: One-click `mkcert` integration to generate locally-trusted SSL certificates for HTTPS development.
- **VHost Management**: Automatic virtual host generation and host file editing.

## 🛠️ Tech Stack

- **Core Engine**: Python 3.14
- **Interface**: PyQt6 (Premium Slate Theme)
- **Service Logic**: Custom Process Management with automatic orphaned process cleanup.
- **SSL Stack**: mkcert integration

## 📦 Installation & Usage

### The Easy Way (Recommended)
1. Download the latest [Pygon Release v4.1.0](https://github.com/Breakrule/Pygon/releases).
2. Run `Pygon.exe`.

### Running from Source
1. **Clone & Setup**:
   ```bash
   git clone https://github.com/Breakrule/Pygon.git
   cd Pygon
   pip install -r requirements.txt
   ```
2. **Launch**:
   ```bash
   python pygon.py
   ```

## 📂 Structure
- `bin/`: Stores service binaries (e.g., `/apache/2.4.66/`, `/php/8.3.4/`).
- `www/`: Your web projects directory.
- `core/`: High-performance service controllers and system utilities.
- `ui/`: Modern PyQt6 component library with sidebar-based layout.

## 🛡️ Requirements
Pygon requires **Administrative Privileges** to:
- Edit the Windows `hosts` file for custom domains.
- Install the Local CA for SSL certificates.
- Bind services to protected ports (80, 443).

## 📄 License
Distributed under the MIT License.

---
**Developed with ❤️ by [Breakrule](https://github.com/Breakrule)**
