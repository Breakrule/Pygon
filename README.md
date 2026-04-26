# ⚡ Pygon

**Pygon** is a lightweight, modern, and high-performance local development environment manager for Windows. Built with Python and CustomTkinter, it serves as a powerful alternative to XAMPP or Laragon, providing a seamless GUI to manage your web development stack.

![Pygon Preview](https://via.placeholder.com/1200x600?text=Pygon+Local+Development+Environment)

## 🚀 Features

- **Dynamic VHosts**: Automatically detects directories in your `www/` root and generates Nginx/Apache virtual host configurations.
- **Local SSL**: Integrated `mkcert` support to generate locally-trusted SSL certificates for `.test` domains.
- **Service Management**: One-click control for:
  - **Web Servers**: Nginx, Apache
  - **Languages**: PHP (multi-version support), Node.js
  - **Databases**: MySQL, PostgreSQL
  - **Tools**: Redis, Mailpit
- **Auto-Downloader**: Missing service binaries are automatically fetched and configured on demand.
- **System Monitoring**: Real-time CPU, RAM, and Disk usage tracking.
- **Portable Design**: Designed to be portable and lightweight.

## 🛠️ Tech Stack

- **Core**: Python 3.x
- **UI**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Utilities**: `psutil`, `jinja2`, `pyyaml`
- **SSL**: `mkcert`

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Breakrule/Pygon.git
   cd Pygon
   ```

2. **Set up the environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Initialize Configuration**:
   Copy the example config to create your local settings:
   ```powershell
   copy config.yaml.example config.yaml
   ```

4. **Launch Pygon**:
   ```bash
   python pygon.py
   ```

## 📂 Project Structure

- `pygon.py`: Main application entry point.
- `core/`: Internal logic for host management, SSL, and process control.
- `services/`: Service-specific definitions and wrappers.
- `www/`: Your local web projects go here.
- `bin/`: (Ignored by Git) Where service binaries are downloaded.

## 🛡️ Security Note

Pygon requires **Administrative Privileges** to:
- Edit the Windows `hosts` file.
- Install the Local CA for SSL.
- Bind services to protected ports (e.g., 80, 443).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
**Developed with ❤️ by Breakrule**
