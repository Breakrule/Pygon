# ⚡ Pygon v4.0: Professional Development Suite

**Pygon** is a lightweight, portable, and visually stunning local development suite for Windows. Designed for speed and aesthetic excellence, it provides a high-performance alternative to XAMPP and Laragon with a sleek Cyberpunk-inspired interface.



## 🌌 The Professional Experience
Pygon v4.0 introduces a complete UI overhaul and professional-grade developer tools. Built with **PyQt6**, the interface features an Obsidian-black foundation with vibrant Cyan, Green, and Pink accents, delivering a state-of-the-art developer workspace.

## 🚀 Key Features

- **Portable Core**: Single standalone executable. Move your development environment anywhere on a USB drive.
- **Service Mastery**: One-click control for your entire stack:
  - **Web Servers**: Apache, Nginx
  - **Languages**: PHP (Seamless version switching), Node.js (Integrated NPM support)
  - **Databases**: MySQL 8.x/9.x, MariaDB
  - **Tools**: Mailpit, HeidiSQL integration
- **Smart Pathing**: Automatically resolves service binaries and manages configurations dynamically.
- **Auto-Downloader**: Missing a service? Pygon fetches the binaries and sets them up for you instantly.
- **Local SSL**: One-click `mkcert` integration to generate locally-trusted SSL certificates for HTTPS development.
- **VHost Management**: Automatic virtual host generation and host file editing.

## 🛠️ Tech Stack

- **Core Engine**: Python 3.14
- **Interface**: PyQt6 (Obsidian Neon Theme)
- **Service Logic**: Custom Process Management with automatic orphaned process cleanup.
- **SSL Stack**: mkcert integration

## 📦 Installation & Usage

### The Easy Way (Recommended)
1. Download the latest [Pygon Release](https://github.com/Breakrule/Pygon/releases).
2. Extract the ZIP to your desired folder.
3. Run `Pygon.exe`.

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
- `ui/`: Modern PyQt6 component library.

## 🛡️ Requirements
Pygon requires **Administrative Privileges** to:
- Edit the Windows `hosts` file for custom domains.
- Install the Local CA for SSL certificates.
- Bind services to protected ports (80, 443).

## 📄 License
Distributed under the MIT License.

---
**Developed with ❤️ by [Breakrule](https://github.com/Breakrule)**
