import customtkinter as ctk
import os
import sys
import threading
import time
import ctypes
import psutil
from tkinter import messagebox
from services.registry import ServiceRegistry
from core.port_monitor import PortMonitor
from core.host_manager import HostManager
from core.tray import TrayManager
from core.mkcert_manager import MkcertManager
from core.downloader import AutoDownloader
from core.config_manager import ConfigManager

# Application Configuration
APP_NAME = "Pygon"
APP_VERSION = "1.0.0"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BIN_DIR = os.path.join(BASE_DIR, "bin")
WWW_DIR = os.path.join(BASE_DIR, "www")
VHOST_CONF_DIR = os.path.join(BIN_DIR, "apache", "conf", "vhosts")

for directory in [BIN_DIR, WWW_DIR, VHOST_CONF_DIR]:
    os.makedirs(directory, exist_ok=True)

# ── Theme System ────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#0B0F17",
        "surface": "#121826",
        "card": "#1E2533",
        "card_hover": "#2A3347",
        "border": "#2D3748",
        "text": "#F8FAFC",
        "text_dim": "#94A3B8",
        "accent": "#10B981",
        "accent_hover": "#059669",
        "danger": "#EF4444",
        "danger_hover": "#DC2626",
        "warning": "#F59E0B",
        "console_bg": "#030712",
        "status_bar": "#0B0F17"
    },
    "light": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "card": "#F1F5F9",
        "card_hover": "#E2E8F0",
        "border": "#CBD5E1",
        "text": "#0F172A",
        "text_dim": "#64748B",
        "accent": "#059669",
        "accent_hover": "#047857",
        "danger": "#DC2626",
        "danger_hover": "#B91C1C",
        "warning": "#D97706",
        "console_bg": "#F8FAFC",
        "status_bar": "#F1F5F9"
    }
}

class PygonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = ConfigManager(os.path.join(BASE_DIR, "config.yaml"))
        self._current_theme = self.config.get_theme()
        self.colors = THEMES[self._current_theme]

        self.title(f"{APP_NAME} v2.0")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        ctk.set_appearance_mode("Dark" if self._current_theme == "dark" else "Light")
        self.configure(fg_color=self.colors["bg"])

        # Core logic
        self.registry = ServiceRegistry(bin_dir=BIN_DIR, config_manager=self.config)
        self.host_manager = HostManager(vhost_conf_dir=VHOST_CONF_DIR, document_root=WWW_DIR)
        self.mkcert_manager = MkcertManager(bin_dir=BIN_DIR)
        self.downloader = AutoDownloader(bin_dir=BIN_DIR)

        self.is_running = False
        self.service_ui_map = {}
        
        self._build_ui()

        # System tray
        self.tray = TrayManager(self)
        self.tray.start_tray()
        
        # New Close Behavior
        self.protocol("WM_DELETE_WINDOW", self._on_close_request)

        # Start periodic updates
        self.update_status()
        self._update_system_info()
        self._update_console_logs()

    # ─────────────────────── Window Management ───────────────────────
    def _on_close_request(self):
        behavior = self.config.get_close_behavior()
        if behavior == "tray":
            self.withdraw()
        elif behavior == "exit":
            self.exit_app()
        else:
            # Ask the user
            dialog = ctk.CTkToplevel(self)
            dialog.title("Close Pygon")
            dialog.geometry("350x200")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(fg_color=self.colors["bg"])

            ctk.CTkLabel(dialog, text="Choose close behavior:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 10))
            
            remember_var = ctk.BooleanVar(value=False)
            
            def handle_choice(choice):
                if remember_var.get():
                    self.config.set_close_behavior(choice)
                if choice == "tray":
                    self.withdraw()
                    dialog.destroy()
                else:
                    self.exit_app()

            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)

            ctk.CTkButton(btn_frame, text="Minimize to Tray", command=lambda: handle_choice("tray"), fg_color=self.colors["card"], text_color=self.colors["text"]).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="Exit & Kill Services", command=lambda: handle_choice("exit"), fg_color=self.colors["danger"]).pack(side="left", padx=5)
            
            ctk.CTkCheckBox(dialog, text="Remember my choice", variable=remember_var, font=ctk.CTkFont(size=11)).pack(pady=10)

    def exit_app(self):
        self.stop_services()
        if hasattr(self, 'tray') and self.tray.icon:
            self.tray.icon.stop()
        self.destroy()
        sys.exit(0)

    # ─────────────────────── UI Build ────────────────────────────────
    def _build_ui(self):
        # Configure grid: top bar, main body, bottom bar
        self.grid_rowconfigure(0, weight=0)  # Top bar
        self.grid_rowconfigure(1, weight=1)  # Main body
        self.grid_rowconfigure(2, weight=0)  # Status bar
        self.grid_columnconfigure(0, weight=1)

        self._build_top_bar()
        self._build_main_body()
        self._build_status_bar()

    # ── Top Bar ──────────────────────────────────────────────────────
    def _build_top_bar(self):
        top = ctk.CTkFrame(self, fg_color=self.colors["surface"], height=52, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        # Left — Title
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, padx=20, pady=8, sticky="w")

        ctk.CTkLabel(
            left, text=f"⚡ {APP_NAME}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(side="left")

        # Right — Theme Toggle + Settings
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.grid(row=0, column=1, padx=15, pady=8, sticky="e")

        theme_icon = "☀" if self._current_theme == "dark" else "🌙"
        self.theme_btn = ctk.CTkButton(
            right, text=theme_icon,
            font=ctk.CTkFont(size=16),
            width=36, height=36, corner_radius=8,
            fg_color="transparent", hover_color=self.colors["card"],
            text_color=self.colors["text"],
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="right", padx=(8, 0))

        settings_btn = ctk.CTkButton(
            right, text="⚙ Settings",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100, height=36, corner_radius=8,
            fg_color=self.colors["card"], hover_color=self.colors["card_hover"],
            text_color=self.colors["text"],
            command=self._open_settings
        )
        settings_btn.pack(side="right")


    # ── Main Body ────────────────────────────────────────────────────
    def _build_main_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 4))
        body.grid_columnconfigure(0, weight=55)
        body.grid_columnconfigure(1, weight=45)
        body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    # ── Left Panel — Services + System Info ──────────
    def _build_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(4, 4))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header row — "Services" + START ALL
        header = ctk.CTkFrame(left, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Services",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text"]
        ).grid(row=0, column=0, sticky="w")

        self.start_all_btn = ctk.CTkButton(
            header, text="▶  START ALL",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=130, height=34,
            corner_radius=10,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self.toggle_services
        )
        self.start_all_btn.grid(row=0, column=1, sticky="e")

        # Scrollable service list
        svc_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["text_dim"]
        )
        svc_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10))
        svc_scroll.grid_columnconfigure(0, weight=1)

        all_services = self.registry.get_all_services()
        services = [s for s in all_services if self.config.get_service_enabled(s.name)]
        if not services:
            ctk.CTkLabel(svc_scroll, text="No services enabled.", text_color=self.colors["text_dim"]).grid(row=0, column=0, pady=40)
        else:
            for idx, service in enumerate(services):
                self._build_service_card(svc_scroll, service, idx)

        # System Info
        self._build_system_info(left)

    def _build_service_card(self, parent, service, idx):
        card = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=10, height=60)
        card.grid(row=idx, column=0, sticky="ew", pady=4, padx=4)
        card.grid_propagate(False)
        card.grid_columnconfigure(2, weight=1)

        # Icon
        icon_frame = ctk.CTkFrame(card, fg_color=getattr(service, 'icon_color', self.colors["accent"]), corner_radius=8, width=36, height=36)
        icon_frame.grid(row=0, column=0, padx=(12, 8), pady=12)
        icon_frame.grid_propagate(False)
        ctk.CTkLabel(icon_frame, text=getattr(service, 'icon', 'SV'), font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

        # Name & Status Info
        name_frame = ctk.CTkFrame(card, fg_color="transparent")
        name_frame.grid(row=0, column=1, sticky="w")
        
        name_lbl = ctk.CTkLabel(name_frame, text=service.name, font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text"], anchor="w")
        name_lbl.pack(anchor="w")
        
        port_lbl = ctk.CTkLabel(name_frame, text=f"Port: {service.current_port}", font=ctk.CTkFont(size=11), text_color=self.colors["text_dim"], anchor="w")
        port_lbl.pack(anchor="w")

        # Version Dropdown
        versions = service.get_available_versions()
        version_dropdown = None
        if versions:
            def on_ver(choice, s=service):
                s.set_active_version(choice)
                self._append_console("Console", f"[VERSION] {s.name} changed to {choice}")
            
            # Convert folder names to display names if service supports it
            display_versions = [service.get_version_display(v) for v in versions]
            ver_map = {service.get_version_display(v): v for v in versions}
            
            version_dropdown = ctk.CTkOptionMenu(
                card, values=display_versions,
                command=lambda c: on_ver(ver_map[c]),
                font=ctk.CTkFont(size=11),
                width=80, height=28,
                corner_radius=6,
                fg_color=self.colors["card_hover"],
                button_color=self.colors["border"],
                button_hover_color=self.colors["text_dim"]
            )
            version_dropdown.set(service.get_version_display(service.active_version))
            version_dropdown.grid(row=0, column=3, padx=10)

        # Start/Stop Button
        toggle_btn = ctk.CTkButton(
            card, text="START",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=70, height=30,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=lambda s=service: self._toggle_single_service(s)
        )
        toggle_btn.grid(row=0, column=4, padx=(0, 15))

        self.service_ui_map[service.name] = {
            "toggle_btn": toggle_btn,
            "port_lbl": port_lbl,
            "service": service,
            "card": card,
            "dropdown": version_dropdown
        }

    def _toggle_single_service(self, service):
        if service.is_running():
            self._stop_single_service(service)
        else:
            self._start_single_service(service)

    # ── System Info ──────────────────────────────────────────────────
    def _build_system_info(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._sys_bars = {}
        metrics = [("CPU", "cpu"), ("RAM", "mem"), ("DISK", "disk")]

        for i, (label, key) in enumerate(metrics):
            m_frame = ctk.CTkFrame(frame, fg_color=self.colors["card"], corner_radius=10, height=60)
            m_frame.grid(row=0, column=i, padx=5, sticky="ew")
            m_frame.grid_propagate(False)
            
            ctk.CTkLabel(m_frame, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color=self.colors["text_dim"]).pack(pady=(8, 0))
            
            val_lbl = ctk.CTkLabel(m_frame, text="0%", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text"])
            val_lbl.pack()
            
            bar = ctk.CTkProgressBar(m_frame, height=4, width=80, progress_color=self.colors["accent"], fg_color=self.colors["border"])
            bar.pack(pady=4)
            bar.set(0)
            
            self._sys_bars[key] = (bar, val_lbl)

    # ── Right Panel — Console / Logs / Errors ────────────────────────
    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 4))
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(
            right, corner_radius=10,
            fg_color=self.colors["bg"],
            segmented_button_fg_color=self.colors["surface"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
            segmented_button_unselected_color=self.colors["surface"],
            segmented_button_unselected_hover_color=self.colors["card_hover"]
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        self._console_tabs = {}
        for tab_name in ["Console", "Logs", "Errors"]:
            tab = self.tabview.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

            textbox = ctk.CTkTextbox(
                tab,
                font=ctk.CTkFont(size=12, family="Consolas"),
                fg_color=self.colors["console_bg"],
                text_color="#A8D8A0" if tab_name == "Console" else (
                    self.colors["text_dim"] if tab_name == "Logs" else "#FF6B6B"
                ),
                corner_radius=8,
                wrap="word",
                state="disabled"
            )
            textbox.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
            self._console_tabs[tab_name] = textbox

        # Clear button
        clear_frame = ctk.CTkFrame(right, fg_color="transparent")
        clear_frame.grid(row=1, column=0, sticky="e", padx=15, pady=(0, 15))

        ctk.CTkButton(
            clear_frame, text="🗑  Clear",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90, height=30,
            corner_radius=8,
            fg_color=self.colors["card"],
            hover_color=self.colors["danger"],
            text_color=self.colors["text"],
            command=self._clear_console
        ).pack(side="right")

    # ── Bottom Status Bar ────────────────────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=self.colors["status_bar"], height=32, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        self._status_bar_inner = ctk.CTkFrame(bar, fg_color="transparent")
        self._status_bar_inner.pack(fill="x", padx=20, pady=4)

    def _refresh_status_bar(self):
        """Rebuilds the status bar text based on current service states."""
        for widget in self._status_bar_inner.winfo_children():
            widget.destroy()

        services = self.registry.get_all_services()
        for service in services:
            running = service.is_running()
            color = self.colors["accent"] if running else self.colors["text_dim"]
            status = "Online" if running else "Offline"
            text = f"● {service.name.split()[0]}: {status}"

            ctk.CTkLabel(
                self._status_bar_inner, text=text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=color
            ).pack(side="left", padx=(0, 20))

    # ─────────────────────── Service Controls ────────────────────────
    def toggle_services(self):
        if not self.is_running:
            self.start_services()
        else:
            self.stop_services()

    def _start_single_service(self, service):
        if not service.is_installed:
            dl_key = service.get_base_folder()
            if dl_key in self.downloader.URLS:
                if messagebox.askyesno("Missing Binary", f"{service.name} is not installed.\nDownload automatically?"):
                    target = os.path.join(BIN_DIR, service.get_base_folder())
                    if self._run_download_with_ui(service.name, dl_key, target):
                        service.start()
                        self._append_console("Console", f"[START] {service.name}")
            return

        if PortMonitor.is_port_in_use(service.current_port):
            messagebox.showwarning("Port Conflict", f"Port {service.current_port} is in use.")
            return

        service.start()
        self._append_console("Console", f"[START] {service.name}")

    def _stop_single_service(self, service):
        service.stop()
        self._append_console("Console", f"[STOP] {service.name}")

    def start_services(self):
        self.start_all_btn.configure(text="⏳ STARTING...", state="disabled")
        self.update()

        services = [s for s in self.registry.get_all_services() if self.config.get_service_enabled(s.name)]
        
        # Check if binaries exist
        for s in services:
            if not s.is_installed:
                dl_key = s.get_base_folder()
                if dl_key in self.downloader.URLS:
                    if messagebox.askyesno("Download", f"{s.name} is missing. Download?"):
                        self._run_download_with_ui(s.name, dl_key, os.path.join(BIN_DIR, dl_key))
        
        # Apache VHost scaffolding
        for project_dir in os.listdir(WWW_DIR):
            proj_path = os.path.join(WWW_DIR, project_dir)
            if os.path.isdir(proj_path):
                self.host_manager.generate_vhost_config(project_dir)
                self.host_manager.add_host_entry(f"{project_dir}.test")

        for s in services:
            if s.is_installed:
                s.start()
        
        self.is_running = True
        self.start_all_btn.configure(text="■  STOP ALL", fg_color=self.colors["danger"], hover_color=self.colors["danger_hover"], state="normal")
        self._append_console("Console", "[START ALL] All services started.")

    def stop_services(self):
        self.start_all_btn.configure(text="⏳ STOPPING...", state="disabled")
        self.update()
        self.registry.stop_all()
        self.is_running = False
        self.start_all_btn.configure(text="▶  START ALL", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"], state="normal")
        self._append_console("Console", "[STOP ALL] All services stopped.")

    # ─────────────────────── Console / Logs ──────────────────────────
    def _append_console(self, tab_name, text):
        tb = self._console_tabs.get(tab_name)
        if not tb: return
        tb.configure(state="normal")
        tb.insert("end", f"[{time.strftime('%H:%M:%S')}] {text}\n")
        tb.see("end")
        tb.configure(state="disabled")

    def _clear_console(self):
        for tb in self._console_tabs.values():
            tb.configure(state="normal")
            tb.delete("1.0", "end")
            tb.configure(state="disabled")
        self._append_console("Console", "Console cleared.")

    def _update_console_logs(self):
        for ui in self.service_ui_map.values():
            svc = ui["service"]
            for line in svc.get_logs(): self._append_console("Logs", f"[{svc.name}] {line}")
            for line in svc.get_errors(): self._append_console("Errors", f"[{svc.name}] {line}")
        self.after(2000, self._update_console_logs)

    def _update_system_info(self):
        try:
            cpu = psutil.cpu_percent() / 100.0
            mem = psutil.virtual_memory().percent / 100.0
            disk = psutil.disk_usage(BASE_DIR).percent / 100.0
            for key, val, bar_lbl in [("cpu", cpu, self._sys_bars["cpu"]), ("mem", mem, self._sys_bars["mem"]), ("disk", disk, self._sys_bars["disk"])]:
                bar, lbl = bar_lbl
                bar.set(val)
                lbl.configure(text=f"{int(val*100)}%")
                color = self.colors["danger"] if val > 0.85 else (self.colors["warning"] if val > 0.65 else self.colors["accent"])
                bar.configure(progress_color=color)
        except: pass
        self.after(3000, self._update_system_info)

    def _toggle_theme(self):
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self._current_theme = new_theme
        self.colors = THEMES[new_theme]
        self.config.set_theme(new_theme)
        
        ctk.set_appearance_mode(new_theme.title())
        self.configure(fg_color=self.colors["bg"])
        
        # Smooth refresh: just rebuild everything
        for widget in self.winfo_children():
            widget.destroy()
        
        self.theme_btn = None
        self._build_ui()
        self._refresh_status_bar()

    # ── Service Context Menu ────────────────────────────────────
    def _show_service_menu(self, service, anchor_widget):
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0,
                       bg=self.colors["card"], fg=self.colors["text"],
                       activebackground=self.colors["accent"], activeforeground="#ffffff",
                       font=("Segoe UI", 10), relief="flat", bd=1)

        items = service.get_menu_items()
        for item in items:
            if item.get('children'):
                submenu = tk.Menu(menu, tearoff=0,
                                  bg=self.colors["card"], fg=self.colors["text"],
                                  activebackground=self.colors["accent"], activeforeground="#ffffff",
                                  font=("Segoe UI", 10), relief="flat", bd=1)
                for child in item['children']:
                    submenu.add_command(label=child['label'], command=lambda a=child['action'], s=service: self._handle_menu_action(a, s))
                menu.add_cascade(label=item['label'], menu=submenu)
            else:
                menu.add_command(label=item['label'], command=lambda a=item['action'], s=service: self._handle_menu_action(a, s))

        x = anchor_widget.winfo_rootx() + anchor_widget.winfo_width()
        y = anchor_widget.winfo_rooty()
        menu.tk_popup(x, y)

    def _handle_menu_action(self, action, service):
        if action == 'restart':
            self._append_console("Console", f"[RESTART] {service.name}")
            service.stop()
            self.after(500, service.start)
        elif action == 'open_folder':
            folder = os.path.join(BIN_DIR, service.get_base_folder())
            if os.path.exists(folder): os.startfile(folder)
        elif action == 'open_docroot':
            os.startfile(WWW_DIR)
        elif action == 'open_conf':
            paths = self._get_conf_paths(service)
            for p in paths:
                if os.path.exists(p): os.startfile(p); return
        elif action == 'open_error_log':
            paths = self._get_log_paths(service, 'error')
            for p in paths:
                if os.path.exists(p): os.startfile(p); return
        elif action == 'open_console':
            exe_map = {'mysql': 'mysql/bin/mysql.exe', 'node': 'node/node.exe'}
            exe = os.path.join(BIN_DIR, exe_map.get(service.get_base_folder(), ""))
            if os.path.exists(exe): os.startfile(exe)
        elif action == 'set_node_project':
            from tkinter import filedialog
            path = filedialog.askdirectory(title="Select Node.js Project Folder")
            if path:
                self.config.set_general("node_project_path", path)
                self._append_console("Console", f"[NODE] Project path set to: {path}")
        else:
            self._placeholder_action(action)

    def _get_conf_paths(self, service) -> list:
        base = os.path.join(BIN_DIR, service.get_base_folder())
        ver = service.active_version
        name = service.get_base_folder()
        if name == 'apache': return [os.path.join(base, 'conf', 'httpd.conf')]
        if name == 'mysql': return [os.path.join(base, ver, 'my.ini') if ver else os.path.join(base, 'my.ini')]
        if name == 'php': return [os.path.join(base, ver, 'php.ini') if ver else os.path.join(base, 'php.ini')]
        return []

    def _get_log_paths(self, service, log_type='error') -> list:
        base = os.path.join(BIN_DIR, service.get_base_folder())
        name = service.get_base_folder()
        if name == 'apache': return [os.path.join(base, 'logs', f'{log_type}.log')]
        if name == 'mysql': return [os.path.join(base, 'data', f'{log_type}.log')]
        return []

    # ─────────────────────── Menu Actions ────────────────────────────
    def _placeholder_action(self, label=""):
        messagebox.showinfo("Coming Soon", f'"{label}" will be available in a future update.')

    def _open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Preferences")
        win.geometry("500x400")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        win.configure(fg_color=self.colors["bg"])

        tabs = ctk.CTkTabview(win, fg_color=self.colors["surface"], corner_radius=10,
                              segmented_button_selected_color=self.colors["accent"])
        tabs.pack(fill="both", expand=True, padx=15, pady=15)

        gen = tabs.add("General")
        
        # Startup
        startup_var = ctk.BooleanVar(value=self.config.get_general("run_on_startup", False))
        def _toggle_startup():
            self.config.set_general("run_on_startup", startup_var.get())
            self._apply_startup_setting(startup_var.get())
            
        ctk.CTkCheckBox(gen, text="Run Pygon when Windows starts", variable=startup_var, command=_toggle_startup).pack(anchor="w", padx=20, pady=15)

        # Services
        svc_tab = tabs.add("Services")
        svc_scroll = ctk.CTkScrollableFrame(svc_tab, fg_color="transparent")
        svc_scroll.pack(fill="both", expand=True)

        for svc in self.registry.get_all_services():
            f = ctk.CTkFrame(svc_scroll, fg_color="transparent")
            f.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar(value=self.config.get_service_enabled(svc.name))
            def _toggle_svc(s=svc.name, v=var):
                self.config.set_service_enabled(s, v.get())
                self._rebuild_service_list()
            
            ctk.CTkCheckBox(f, text=svc.name, variable=var, command=_toggle_svc).pack(side="left", padx=10)

        # Footer
        footer = ctk.CTkFrame(win, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=15, pady=15)
        ctk.CTkButton(footer, text="Close", width=100, command=win.destroy).pack(side="right")

    def _apply_startup_setting(self, enabled: bool):
        """Add/remove Pygon from Windows startup registry."""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_SET_VALUE)
            if enabled:
                exe = sys.executable
                if getattr(sys, 'frozen', False):
                    cmd = f'"{exe}"'
                else:
                    cmd = f'"{exe}" "{os.path.abspath(__file__)}"'
                winreg.SetValueEx(key, "Pygon", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "Pygon")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def _rebuild_service_list(self):
        """Rebuild the service card list to reflect enabled/disabled changes."""
        # Find the scrollable frame and rebuild
        self._build_ui()

    def _toggle_theme(self):
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self._current_theme = new_theme
        self.colors = THEMES[new_theme]
        self.config.set_theme(new_theme)
        ctk.set_appearance_mode(new_theme.title())
        self.configure(fg_color=self.colors["bg"])
        for widget in self.winfo_children():
            widget.destroy()
        self.service_ui_map = {}
        self._build_ui()
        self._refresh_status_bar()

    def _open_hosts_file(self):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            os.startfile(hosts_path)
        except:
            import subprocess
            subprocess.Popen(["notepad.exe", hosts_path])

    def _open_web(self):
        import webbrowser
        webbrowser.open("http://127.0.0.1")

    def _open_database(self):
        mysql_exe = os.path.join(BIN_DIR, "mysql", "bin", "mysql.exe")
        if os.path.exists(mysql_exe):
            import subprocess
            subprocess.Popen(["cmd", "/k", mysql_exe, "-u", "root"], creationflags=0x10)
        else:
            messagebox.showinfo("Database", "MySQL client not found.")

    def _open_terminal(self):
        import subprocess
        subprocess.Popen(["cmd", "/k", f"cd /d {WWW_DIR}"], creationflags=0x10)

    def update_status(self):
        any_running = False
        for name, ui in self.service_ui_map.items():
            service = ui["service"]
            running = service.is_running()
            if running:
                any_running = True
                ui["toggle_btn"].configure(text="STOP", fg_color=self.colors["danger"], hover_color=self.colors["danger_hover"])
            else:
                ui["toggle_btn"].configure(text="START", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"])
            ui["port_lbl"].configure(text=f"Port: {service.current_port}")

        if any_running:
            self.start_all_btn.configure(text="■  STOP ALL", fg_color=self.colors["danger"], hover_color=self.colors["danger_hover"])
            self.is_running = True
        else:
            self.start_all_btn.configure(text="▶  START ALL", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"])
            self.is_running = False

        self._refresh_status_bar()
        self.after(2000, self.update_status)

    def _run_download_with_ui(self, service_display_name, dl_key, target_folder):
        popup = ctk.CTkToplevel(self)
        popup.title("Downloading Service")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        popup.configure(fg_color=self.colors["bg"])

        lbl = ctk.CTkLabel(popup, text=f"Downloading {service_display_name}...", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=(25, 10))

        progress = ctk.CTkProgressBar(popup, width=300, progress_color=self.colors["accent"])
        progress.pack(pady=5)
        progress.set(0)

        status_lbl = ctk.CTkLabel(popup, text="Preparing...", text_color=self.colors["text_dim"])
        status_lbl.pack(pady=5)

        res = [False]
        def thread_func():
            success = self.downloader.download_and_extract(dl_key, target_folder, 
                status_callback=lambda m: popup.after(0, lambda: status_lbl.configure(text=m)))
            res[0] = success
            popup.after(500, popup.destroy)

        threading.Thread(target=thread_func, daemon=True).start()
        self.wait_window(popup)
        return res[0]


if __name__ == "__main__":
    # Prevent multiple instances using a Windows Mutex
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Pygon_SingleInstance_Mutex")
    last_error = ctypes.windll.kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Pygon Already Running",
            "An instance of Pygon is already running.\nCheck your system tray or taskbar."
        )
        sys.exit(0)

    app = PygonApp()
    app.mainloop()
