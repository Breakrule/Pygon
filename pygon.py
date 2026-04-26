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
NGINX_CONF_DIR = os.path.join(BIN_DIR, "nginx", "conf", "vhosts")

for directory in [BIN_DIR, WWW_DIR, NGINX_CONF_DIR]:
    os.makedirs(directory, exist_ok=True)

# ── Theme Palettes ───────────────────────────────────────────────────────
DARK_THEME = {
    "bg": "#080C14", "surface": "#0F1520", "card": "#1A2332",
    "card_hover": "#253344", "border": "#2D3B4E",
    "text": "#E8ECF1", "text_dim": "#7B8794",
    "accent": "#10B981", "accent_hover": "#059669",
    "danger": "#EF4444", "danger_hover": "#DC2626",
    "warning": "#F59E0B", "tab_bg": "#0F1520",
    "console_bg": "#030712", "status_bar": "#080C14",
}
LIGHT_THEME = {
    "bg": "#F1F5F9", "surface": "#FFFFFF", "card": "#E2E8F0",
    "card_hover": "#CBD5E1", "border": "#94A3B8",
    "text": "#1E293B", "text_dim": "#64748B",
    "accent": "#059669", "accent_hover": "#047857",
    "danger": "#DC2626", "danger_hover": "#B91C1C",
    "warning": "#D97706", "tab_bg": "#FFFFFF",
    "console_bg": "#F8FAFC", "status_bar": "#E2E8F0",
}

def get_theme_colors(theme_name="dark"):
    t = DARK_THEME if theme_name == "dark" else LIGHT_THEME
    return t

# Active theme (set on startup from config)
_t = DARK_THEME
COL_BG          = _t["bg"]
COL_SURFACE     = _t["surface"]
COL_CARD        = _t["card"]
COL_CARD_HOVER  = _t["card_hover"]
COL_BORDER      = _t["border"]
COL_TEXT        = _t["text"]
COL_TEXT_DIM    = _t["text_dim"]
COL_ACCENT      = _t["accent"]
COL_ACCENT_HOVER= _t["accent_hover"]
COL_DANGER      = _t["danger"]
COL_DANGER_HOVER= _t["danger_hover"]
COL_WARNING     = _t["warning"]
COL_TAB_BG      = _t["tab_bg"]
COL_TAB_SEL     = _t["card_hover"]
COL_CONSOLE_BG  = _t["console_bg"]
COL_STATUS_BAR  = _t["status_bar"]


class PygonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} - Local Development Environment")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.resizable(True, True)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Apply saved theme
        saved_theme = ConfigManager(os.path.join(BASE_DIR, "config.yaml")).get_theme()
        if saved_theme == "light":
            t = LIGHT_THEME
        else:
            t = DARK_THEME
        # Update globals
        global COL_BG, COL_SURFACE, COL_CARD, COL_CARD_HOVER, COL_BORDER
        global COL_TEXT, COL_TEXT_DIM, COL_ACCENT, COL_ACCENT_HOVER
        global COL_DANGER, COL_DANGER_HOVER, COL_WARNING
        global COL_TAB_BG, COL_TAB_SEL, COL_CONSOLE_BG, COL_STATUS_BAR
        COL_BG = t["bg"]; COL_SURFACE = t["surface"]; COL_CARD = t["card"]
        COL_CARD_HOVER = t["card_hover"]; COL_BORDER = t["border"]
        COL_TEXT = t["text"]; COL_TEXT_DIM = t["text_dim"]
        COL_ACCENT = t["accent"]; COL_ACCENT_HOVER = t["accent_hover"]
        COL_DANGER = t["danger"]; COL_DANGER_HOVER = t["danger_hover"]
        COL_WARNING = t["warning"]; COL_TAB_BG = t["tab_bg"]
        COL_TAB_SEL = t["card_hover"]; COL_CONSOLE_BG = t["console_bg"]
        COL_STATUS_BAR = t["status_bar"]
        if saved_theme == "light":
            ctk.set_appearance_mode("Light")

        self.configure(fg_color=COL_BG)

        # Core logic
        self.config = ConfigManager(os.path.join(BASE_DIR, "config.yaml"))
        self.registry = ServiceRegistry(bin_dir=BIN_DIR, config_manager=self.config)
        self.host_manager = HostManager(nginx_conf_dir=NGINX_CONF_DIR, document_root=WWW_DIR)
        self.mkcert_manager = MkcertManager(bin_dir=BIN_DIR)
        self.downloader = AutoDownloader(bin_dir=BIN_DIR)

        self.is_running = False
        self.service_ui_map = {}
        self._console_line_count = 0

        # Auto-create service directories
        for service in self.registry.get_all_services():
            svc_dir = os.path.join(BIN_DIR, os.path.dirname(service.executable_path))
            os.makedirs(svc_dir, exist_ok=True)

        self._build_ui()

        # System tray
        self.tray = TrayManager(self)
        self.tray.start_tray()
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # Start periodic updates
        self.update_status()
        self._update_system_info()
        self._update_console_logs()

    # ─────────────────────── Window Management ───────────────────────
    def hide_to_tray(self):
        self.withdraw()

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
        top = ctk.CTkFrame(self, fg_color=COL_SURFACE, height=52, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        # Left — Title + Version
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkLabel(
            left, text=f"⚡ {APP_NAME}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COL_ACCENT
        ).pack(side="left")

        ctk.CTkLabel(
            left, text=f"  v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=COL_TEXT_DIM
        ).pack(side="left", padx=(4, 0))

        # Right — Theme Toggle + Hosts + Settings
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.grid(row=0, column=1, padx=12, pady=8, sticky="e")

        # Theme toggle button
        self._current_theme = self.config.get_theme()
        theme_icon = "☀" if self._current_theme == "dark" else "🌙"
        self.theme_btn = ctk.CTkButton(
            right, text=theme_icon,
            font=ctk.CTkFont(size=16),
            width=32, height=32, corner_radius=6,
            fg_color="transparent", hover_color=COL_CARD,
            text_color=COL_TEXT,
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="right", padx=(4, 0))

        settings_btn = ctk.CTkButton(
            right, text="⚙ Settings",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=90, height=32, corner_radius=6,
            fg_color="transparent", hover_color=COL_CARD,
            text_color=COL_TEXT,
            command=self._show_top_settings_menu
        )
        settings_btn.pack(side="right")
        self.settings_btn = settings_btn

        # Hosts file edit button
        hosts_btn = ctk.CTkButton(
            right, text="📋 Hosts",
            font=ctk.CTkFont(size=12),
            width=80, height=32, corner_radius=6,
            fg_color="transparent", hover_color=COL_CARD,
            text_color=COL_TEXT,
            command=self._open_hosts_file
        )
        hosts_btn.pack(side="right", padx=(0, 4))

    def _show_top_settings_menu(self):
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0, bg=COL_CARD, fg=COL_TEXT,
                       activebackground=COL_ACCENT, activeforeground="#ffffff",
                       relief="flat", borderwidth=1, font=("Segoe UI", 10))

        menu.add_command(label="📦 Modules", command=lambda: self._placeholder_action("Modules"))
        menu.add_command(label="💻 Terminal", command=lambda: self._placeholder_action("Terminal"))
        menu.add_command(label="⏱️ Cron Jobs", command=lambda: self._placeholder_action("Cron Jobs"))
        menu.add_command(label="📝 WordPress", command=lambda: self._placeholder_action("WordPress"))
        menu.add_command(label="🎨 Webpage Designer", command=lambda: self._placeholder_action("Designer"))
        menu.add_separator()
        menu.add_command(label="⚙️ Preferences...", command=self._open_settings)

        # Position menu beneath the settings button
        x = self.settings_btn.winfo_rootx()
        y = self.settings_btn.winfo_rooty() + self.settings_btn.winfo_height()
        menu.tk_popup(x, y)

    # ── Main Body ────────────────────────────────────────────────────
    def _build_main_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 4))
        body.grid_columnconfigure(0, weight=55)
        body.grid_columnconfigure(1, weight=45)
        body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    # ── Left Panel — Services + System Info + Quick Actions ──────────
    def _build_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color=COL_SURFACE, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(4, 4))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header row — "Services" + START ALL
        header = ctk.CTkFrame(left, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Services",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COL_TEXT
        ).grid(row=0, column=0, sticky="w")

        self.start_all_btn = ctk.CTkButton(
            header, text="▶  START ALL",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120, height=32,
            corner_radius=8,
            fg_color=COL_ACCENT,
            hover_color=COL_ACCENT_HOVER,
            command=self.toggle_services
        )
        self.start_all_btn.grid(row=0, column=1, sticky="e")

        # Scrollable service list
        svc_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=COL_BORDER,
            scrollbar_button_hover_color=COL_TEXT_DIM
        )
        svc_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 4))
        svc_scroll.grid_columnconfigure(0, weight=1)

        all_services = self.registry.get_all_services()
        # Filter by enabled status from Preferences
        services = [s for s in all_services if self.config.get_service_enabled(s.name)]
        if not services:
            ctk.CTkLabel(
                svc_scroll, text="No services enabled. Check Preferences.",
                text_color=COL_TEXT_DIM
            ).grid(row=0, column=0, pady=30)
        else:
            for idx, service in enumerate(services):
                self._build_service_card(svc_scroll, service, idx)

        # Bottom section — System Info + Quick Actions
        bottom = ctk.CTkFrame(left, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 10))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        self._build_system_info(bottom)
        self._build_quick_actions(bottom)

    def _build_service_card(self, parent, service, idx):
        card = ctk.CTkFrame(
            parent, fg_color=COL_CARD,
            corner_radius=8, height=54
        )
        card.grid(row=idx, column=0, sticky="ew", pady=3, padx=4)
        card.grid_propagate(False)
        card.grid_columnconfigure(2, weight=1)

        # Autostart Checkbox
        auto_var = ctk.BooleanVar(value=self.config.get_service_autostart(service.name))
        def _on_auto_change(s=service, v=auto_var):
            self.config.set_service_autostart(s.name, v.get())
        
        auto_chk = ctk.CTkCheckBox(
            card, text="", variable=auto_var,
            width=24, checkbox_width=20, checkbox_height=20,
            corner_radius=4,
            fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER,
            command=_on_auto_change
        )
        auto_chk.grid(row=0, column=0, padx=(12, 0), pady=17)

        # Icon badge (colored square with text)
        icon_frame = ctk.CTkFrame(
            card, fg_color=getattr(service, 'icon_color', '#6B7280'),
            corner_radius=6, width=32, height=32
        )
        icon_frame.grid(row=0, column=1, padx=(6, 4))
        icon_frame.grid_propagate(False)
        ctk.CTkLabel(
            icon_frame, text=getattr(service, 'icon', 'SV'),
            font=ctk.CTkFont(size=11, weight="bold", family="Consolas"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5, anchor="center")

        name_lbl = ctk.CTkLabel(
            card, text=service.name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COL_TEXT, anchor="w"
        )
        name_lbl.grid(row=0, column=2, sticky="w", padx=4)

        # Editable Port Entry
        port_var = ctk.StringVar(value=str(service.current_port))

        port_entry = ctk.CTkEntry(
            card, textvariable=port_var,
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color=COL_TEXT_DIM,
            fg_color=COL_CARD,
            border_color=COL_BORDER,
            border_width=1,
            width=54, height=26,
            corner_radius=4,
            justify="center"
        )
        port_entry.grid(row=0, column=3, padx=4)

        def _save_port(event=None, s=service, pv=port_var, pe=port_entry):
            try:
                new_port = int(pv.get())
                if 1 <= new_port <= 65535:
                    s.set_custom_port(new_port)
                    pe.configure(border_color=COL_ACCENT)
                    self.after(1500, lambda: pe.configure(border_color=COL_BORDER))
                    self._append_console("Console", f"[PORT] {s.name} port changed to {new_port}")
                else:
                    pv.set(str(s.current_port))
            except ValueError:
                pv.set(str(s.current_port))

        port_entry.bind("<Return>", _save_port)
        port_entry.bind("<FocusOut>", _save_port)

        # Version dropdown (if applicable)
        versions = service.get_available_versions()
        version_dropdown = None
        if versions:
            def on_ver(choice, s=service):
                s.set_active_version(choice)
                self.config.set_service_version(s.name, choice)
                # Ensure the display updates to the new version
                self._append_console("Console", f"[VERSION] {s.name} version changed to {choice}")

            version_dropdown = ctk.CTkOptionMenu(
                card, values=versions,
                command=on_ver,
                font=ctk.CTkFont(size=11),
                width=96, height=26,
                corner_radius=6,
                fg_color=COL_CARD_HOVER,
                button_color=COL_BORDER,
                button_hover_color=COL_TEXT_DIM
            )
            version_dropdown.set(service.active_version)
            version_dropdown.grid(row=0, column=4, padx=4)

        # Toggle switch
        switch_var = ctk.BooleanVar(value=False)

        def on_toggle(s=service, sv=switch_var):
            if sv.get():
                self._start_single_service(s)
            else:
                self._stop_single_service(s)

        switch = ctk.CTkSwitch(
            card, text="",
            variable=switch_var,
            command=on_toggle,
            width=44, height=22,
            switch_width=40, switch_height=20,
            progress_color=COL_ACCENT,
            button_color=COL_TEXT,
            fg_color=COL_BORDER,
            button_hover_color="#ffffff"
        )
        switch.grid(row=0, column=5, padx=(4, 6))

        # Status indicator dot
        status_lbl = ctk.CTkLabel(
            card, text="●",
            font=ctk.CTkFont(size=10),
            text_color=COL_TEXT_DIM, width=16
        )
        status_lbl.grid(row=0, column=6, padx=(0, 2))

        # Menu button (⋮ kebab)
        menu_btn = ctk.CTkButton(
            card, text="⋮",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=28, height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COL_CARD_HOVER,
            text_color=COL_TEXT_DIM,
            command=lambda s=service, b=card: self._show_service_menu(s, b)
        )
        menu_btn.grid(row=0, column=7, padx=(0, 10))

        self.service_ui_map[service.name] = {
            "autostart_var": auto_var,
            "label": status_lbl,
            "switch": switch,
            "switch_var": switch_var,
            "dropdown": version_dropdown,
            "port_entry": port_entry,
            "port_var": port_var,
            "service": service,
            "card": card,
            "name_lbl": name_lbl,
        }

    # ── System Info ──────────────────────────────────────────────────
    def _build_system_info(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COL_CARD, corner_radius=8)
        frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="System Info",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COL_TEXT
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self._sys_bars = {}
        metrics = [
            ("CPU", "cpu"),
            ("Memory", "mem"),
            ("Disk", "disk"),
            ("Network", "net"),
        ]

        for i, (label, key) in enumerate(metrics):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.grid(row=i + 1, column=0, sticky="ew", padx=12, pady=2)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont(size=10),
                text_color=COL_TEXT_DIM, width=55, anchor="w"
            ).grid(row=0, column=0, sticky="w")

            bar = ctk.CTkProgressBar(
                row, height=8, corner_radius=4,
                progress_color=COL_ACCENT,
                fg_color=COL_BORDER
            )
            bar.grid(row=0, column=1, sticky="ew", padx=(4, 4))
            bar.set(0)

            val_lbl = ctk.CTkLabel(
                row, text="0%",
                font=ctk.CTkFont(size=10, family="Consolas"),
                text_color=COL_TEXT_DIM, width=38, anchor="e"
            )
            val_lbl.grid(row=0, column=2, sticky="e")

            self._sys_bars[key] = (bar, val_lbl)

        # Bottom padding
        ctk.CTkFrame(frame, fg_color="transparent", height=8).grid(
            row=len(metrics) + 1, column=0
        )

    # ── Quick Actions ────────────────────────────────────────────────
    def _build_quick_actions(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COL_CARD, corner_radius=8)
        frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="Quick Actions",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COL_TEXT
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        actions = [
            ("🌐 Open Web", 0, 0, self._open_web),
            ("🗄 Database", 0, 1, self._open_database),
            ("💻 Terminal", 1, 0, self._open_terminal),
            ("🔺 Laravel", 1, 1, lambda: self._placeholder_action("Laravel App")),
        ]

        for label, r, c, cmd in actions:
            btn = ctk.CTkButton(
                frame, text=label,
                font=ctk.CTkFont(size=11),
                height=32, corner_radius=6,
                fg_color=COL_CARD_HOVER,
                hover_color=COL_BORDER,
                text_color=COL_TEXT,
                command=cmd
            )
            btn.grid(row=r + 1, column=c, padx=6, pady=3, sticky="ew")

        ctk.CTkFrame(frame, fg_color="transparent", height=8).grid(
            row=3, column=0, columnspan=2
        )

    # ── Right Panel — Console / Logs / Errors ────────────────────────
    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color=COL_SURFACE, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 4))
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(
            right, corner_radius=8,
            fg_color=COL_TAB_BG,
            segmented_button_fg_color=COL_CARD,
            segmented_button_selected_color=COL_ACCENT,
            segmented_button_selected_hover_color=COL_ACCENT_HOVER,
            segmented_button_unselected_color=COL_CARD,
            segmented_button_unselected_hover_color=COL_CARD_HOVER
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))

        self._console_tabs = {}
        for tab_name in ["Console", "Logs", "Errors"]:
            tab = self.tabview.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

            textbox = ctk.CTkTextbox(
                tab,
                font=ctk.CTkFont(size=12, family="Consolas"),
                fg_color=COL_CONSOLE_BG,
                text_color="#a8d8a0" if tab_name == "Console" else (
                    COL_TEXT_DIM if tab_name == "Logs" else "#ff6b6b"
                ),
                corner_radius=6,
                wrap="word",
                state="disabled"
            )
            textbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
            self._console_tabs[tab_name] = textbox

        # Clear button
        clear_frame = ctk.CTkFrame(right, fg_color="transparent")
        clear_frame.grid(row=1, column=0, sticky="e", padx=12, pady=(0, 10))

        ctk.CTkButton(
            clear_frame, text="🗑  Clear",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=80, height=28,
            corner_radius=6,
            fg_color=COL_CARD,
            hover_color=COL_DANGER,
            text_color=COL_TEXT,
            command=self._clear_console
        ).pack(side="right")

    # ── Bottom Status Bar ────────────────────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=COL_STATUS_BAR, height=32, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        self._status_bar_inner = ctk.CTkFrame(bar, fg_color="transparent")
        self._status_bar_inner.pack(fill="x", padx=16, pady=4)

        self._status_labels = {}

    def _refresh_status_bar(self):
        """Rebuilds the status bar text based on current service states."""
        # Clear old labels
        for widget in self._status_bar_inner.winfo_children():
            widget.destroy()

        services = self.registry.get_all_services()
        for service in services:
            running = service.is_running()
            color = COL_ACCENT if running else COL_TEXT_DIM
            status = "Running" if running else "Stopped"
            text = f"● {service.name.split()[0]}: {status}"

            lbl = ctk.CTkLabel(
                self._status_bar_inner, text=text,
                font=ctk.CTkFont(size=10),
                text_color=color
            )
            lbl.pack(side="left", padx=(0, 16))

        # PHP version at the end
        for service in services:
            if "PHP" in service.name:
                ver = service.active_version or "N/A"
                ctk.CTkLabel(
                    self._status_bar_inner, text=f"PHP: {ver}",
                    font=ctk.CTkFont(size=10, family="Consolas"),
                    text_color=COL_WARNING
                ).pack(side="right")
                break

    # ─────────────────────── Service Controls ────────────────────────
    def toggle_services(self):
        if not self.is_running:
            self.start_services()
        else:
            self.stop_services()

    def _start_single_service(self, service):
        """Start a single service via its toggle switch."""
        if not service.is_installed:
            dl_key = service.get_base_folder()
            if dl_key in self.downloader.URLS:
                if messagebox.askyesno(
                    "Missing Binary",
                    f"{service.name} is not installed.\nDownload automatically?"
                ):
                    target = os.path.join(BIN_DIR, service.get_base_folder())
                    success = self._run_download_with_ui(service.name, dl_key, target)
                    if not success:
                        messagebox.showerror("Error", f"Failed to download {service.name}.")
                        ui = self.service_ui_map.get(service.name)
                        if ui:
                            ui["switch_var"].set(False)
                        return
                else:
                    ui = self.service_ui_map.get(service.name)
                    if ui:
                        ui["switch_var"].set(False)
                    return
            else:
                messagebox.showinfo(
                    "Not Installed",
                    f"{service.name} binary not found at:\n{service.executable_path}\n\nPlease install it manually."
                )
                ui = self.service_ui_map.get(service.name)
                if ui:
                    ui["switch_var"].set(False)
                return

        if PortMonitor.is_port_in_use(service.current_port):
            proc_info = PortMonitor.get_process_using_port(service.current_port)
            proc_name = proc_info['name'] if proc_info else 'Unknown'
            messagebox.showwarning(
                "Port Conflict",
                f"Port {service.current_port} is in use by: {proc_name}"
            )
            ui = self.service_ui_map.get(service.name)
            if ui:
                ui["switch_var"].set(False)
            return

        service.start()
        self._append_console("Console", f"[START] {service.name} on port {service.current_port}")

    def _stop_single_service(self, service):
        """Stop a single service via its toggle switch."""
        service.stop()
        self._append_console("Console", f"[STOP] {service.name}")

    def start_services(self):
        self.start_all_btn.configure(text="⏳ STARTING...", state="disabled")
        self.update()

        all_services = self.registry.get_all_services()
        # Only process services that have the checkbox ticked
        services = [s for s in all_services if self.config.get_service_autostart(s.name)]

        if not services:
            messagebox.showinfo("No Selection", "Please check the box next to at least one service to start.")
            self.start_all_btn.configure(text="▶  START ALL", state="normal")
            return

        installed_services = []
        skipped = []

        for service in services:
            if service.is_installed:
                installed_services.append(service)
            else:
                dl_key = service.get_base_folder()
                if dl_key in self.downloader.URLS:
                    if messagebox.askyesno(
                        "Missing Binary",
                        f"{service.name} is not installed. Download?"
                    ):
                        target = os.path.join(BIN_DIR, service.get_base_folder())
                        success = self._run_download_with_ui(service.name, dl_key, target)
                        if success:
                            installed_services.append(service)
                        else:
                            skipped.append(service.name)
                    else:
                        skipped.append(service.name)
                else:
                    skipped.append(service.name)

        if not installed_services:
            messagebox.showinfo("No Services", "No installed services found to start.")
            self.start_all_btn.configure(text="▶  START ALL", state="normal")
            return

        # Port check (only for installed services)
        for service in installed_services:
            if PortMonitor.is_port_in_use(service.current_port):
                proc_info = PortMonitor.get_process_using_port(service.current_port)
                proc_name = proc_info['name'] if proc_info else 'Unknown'
                messagebox.showwarning(
                    "Port Conflict",
                    f"Port {service.current_port} for {service.name} in use by: {proc_name}"
                )
                self.start_all_btn.configure(text="▶  START ALL", state="normal")
                return

        # SSL / VHost scaffolding
        if not self.mkcert_manager.is_installed():
            self.start_all_btn.configure(text="⏳ MKCERT...", state="disabled")
            self.update()
            self.mkcert_manager.install_local_ca()

        ssl_out_dir = os.path.join(NGINX_CONF_DIR, "ssl")
        os.makedirs(ssl_out_dir, exist_ok=True)

        for project_dir in os.listdir(WWW_DIR):
            if os.path.isdir(os.path.join(WWW_DIR, project_dir)):
                domain = f"{project_dir}.test"
                self.mkcert_manager.generate_cert(domain, ssl_out_dir)
                cert_file = os.path.join(ssl_out_dir, f"{domain}.crt")
                key_file = os.path.join(ssl_out_dir, f"{domain}.key")
                self.host_manager.generate_nginx_config(project_dir, ssl_cert=cert_file, ssl_key=key_file)
                self.host_manager.add_host_entry(domain)

        # Start only installed services
        for service in installed_services:
            service.start()

        # Flip switches for installed services only
        for svc_name, ui in self.service_ui_map.items():
            service = ui["service"]
            if service in installed_services:
                ui["switch_var"].set(True)

        self.is_running = True
        self.start_all_btn.configure(
            text="■  STOP ALL",
            fg_color=COL_DANGER,
            hover_color=COL_DANGER_HOVER,
            state="normal"
        )
        self._append_console("Console", "[START ALL] All services started.")

    def stop_services(self):
        self.start_all_btn.configure(text="⏳ STOPPING...", state="disabled")
        self.update()

        self.registry.stop_all()

        for svc_name, ui in self.service_ui_map.items():
            ui["switch_var"].set(False)

        self.is_running = False
        self.start_all_btn.configure(
            text="▶  START ALL",
            fg_color=COL_ACCENT,
            hover_color=COL_ACCENT_HOVER,
            state="normal"
        )
        self._append_console("Console", "[STOP ALL] All services stopped.")

    # ─────────────────────── Console / Logs ──────────────────────────
    def _append_console(self, tab_name, text):
        """Append a line of text to a console tab."""
        tb = self._console_tabs.get(tab_name)
        if not tb:
            return
        tb.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        tb.insert("end", f"[{timestamp}] {text}\n")
        tb.see("end")
        tb.configure(state="disabled")

    def _clear_console(self):
        """Clear all console tabs and service log buffers."""
        for name, tb in self._console_tabs.items():
            tb.configure(state="normal")
            tb.delete("1.0", "end")
            tb.configure(state="disabled")

        for svc_name, ui in self.service_ui_map.items():
            ui["service"].clear_logs()

        self._append_console("Console", "Console cleared.")

    def _update_console_logs(self):
        """Periodically pull logs from services into the console tabs."""
        for svc_name, ui in self.service_ui_map.items():
            service = ui["service"]

            # Pull stdout logs
            logs = service.get_logs()
            if logs:
                for line in logs:
                    self._append_console("Logs", f"[{svc_name}] {line}")
                service._log_buffer.clear()

            # Pull stderr errors
            errors = service.get_errors()
            if errors:
                for line in errors:
                    self._append_console("Errors", f"[{svc_name}] {line}")
                service._error_buffer.clear()

        self.after(2000, self._update_console_logs)

    # ─────────────────────── Status Updates ──────────────────────────
    def update_status(self):
        """Periodically polls the ServiceRegistry to update GUI status indicators."""
        for service_name, ui in self.service_ui_map.items():
            service = ui["service"]
            status_lbl = ui["label"]
            switch_var = ui["switch_var"]
            card = ui["card"]

            if service.is_running():
                status_lbl.configure(text_color=COL_ACCENT)
                card.configure(fg_color=COL_CARD)
                if ui.get("dropdown"):
                    ui["dropdown"].configure(state="disabled")
                # Sync switch state
                if not switch_var.get():
                    switch_var.set(True)
            else:
                status_lbl.configure(text_color=COL_TEXT_DIM)
                card.configure(fg_color=COL_CARD)
                if ui.get("dropdown"):
                    ui["dropdown"].configure(state="normal")
                if switch_var.get() and not self.is_running:
                    switch_var.set(False)

            # Check for newly added versions
            dropdown = ui.get("dropdown")
            if dropdown and not service.is_running():
                current_values = dropdown._values
                latest_versions = service.get_available_versions()
                if current_values != latest_versions and latest_versions:
                    dropdown.configure(values=latest_versions)
                    if service.active_version not in latest_versions:
                        service.set_active_version(latest_versions[0])
                    dropdown.set(service.active_version)

        self._refresh_status_bar()
        self.after(2000, self.update_status)

    # ─────────────────────── System Info ──────────────────────────────
    def _update_system_info(self):
        """Updates system resource bars using psutil."""
        try:
            cpu = psutil.cpu_percent(interval=0) / 100.0
            mem = psutil.virtual_memory().percent / 100.0
            disk = psutil.disk_usage('/').percent / 100.0

            net = psutil.net_io_counters()
            # Normalize network to a 0-1 scale (rough heuristic: cap at 100MB/s)
            net_bytes = (net.bytes_sent + net.bytes_recv) % (100 * 1024 * 1024)
            net_val = min(net_bytes / (100 * 1024 * 1024), 1.0)

            updates = {
                "cpu": cpu,
                "mem": mem,
                "disk": disk,
                "net": net_val
            }

            for key, val in updates.items():
                if key in self._sys_bars:
                    bar, lbl = self._sys_bars[key]
                    bar.set(val)
                    lbl.configure(text=f"{int(val * 100)}%")

                    # Color coding
                    if val > 0.85:
                        bar.configure(progress_color=COL_DANGER)
                    elif val > 0.65:
                        bar.configure(progress_color=COL_WARNING)
                    else:
                        bar.configure(progress_color=COL_ACCENT)
        except Exception:
            pass

        self.after(3000, self._update_system_info)

    # ─────────────────────── Service Context Menu ────────────────────
    def _show_service_menu(self, service, anchor_widget):
        """Shows a context menu popup for a service using tkinter Menu."""
        import tkinter as tk

        menu = tk.Menu(self, tearoff=0,
                       bg="#2a2a50", fg="#e8e8f0",
                       activebackground="#2fa572", activeforeground="white",
                       font=("Segoe UI", 10),
                       relief="flat", bd=0)

        items = service.get_menu_items()
        for item in items:
            if item.get('children'):
                submenu = tk.Menu(menu, tearoff=0,
                                  bg="#2a2a50", fg="#e8e8f0",
                                  activebackground="#2fa572", activeforeground="white",
                                  font=("Segoe UI", 10),
                                  relief="flat", bd=0)
                for child in item['children']:
                    submenu.add_command(
                        label=child['label'],
                        command=lambda a=child['action'], s=service: self._handle_menu_action(a, s)
                    )
                menu.add_cascade(label=item['label'], menu=submenu)
            elif item.get('action') == 'separator':
                menu.add_separator()
            else:
                menu.add_command(
                    label=item['label'],
                    command=lambda a=item['action'], s=service: self._handle_menu_action(a, s)
                )

        x = anchor_widget.winfo_rootx() + anchor_widget.winfo_width()
        y = anchor_widget.winfo_rooty()
        menu.tk_popup(x, y)

    def _handle_menu_action(self, action, service):
        """Dispatches a context menu action for a service."""
        if action == 'restart':
            self._append_console("Console", f"[RESTART] {service.name}")
            service.stop()
            self.after(500, service.start)

        elif action == 'open_folder':
            folder = os.path.join(BIN_DIR, service.get_base_folder())
            if os.path.exists(folder):
                os.startfile(folder)
            else:
                messagebox.showinfo("Not Found", f"Folder not found:\n{folder}")

        elif action == 'open_docroot':
            os.startfile(WWW_DIR)

        elif action == 'open_conf':
            conf_paths = self._get_conf_paths(service)
            opened = False
            for p in conf_paths:
                if os.path.exists(p):
                    os.startfile(p)
                    opened = True
                    break
            if not opened:
                messagebox.showinfo("Not Found", f"Config file not found for {service.name}.")

        elif action == 'open_error_log':
            log_paths = self._get_log_paths(service, 'error')
            opened = False
            for p in log_paths:
                if os.path.exists(p):
                    os.startfile(p)
                    opened = True
                    break
            if not opened:
                messagebox.showinfo("Not Found", f"Error log not found for {service.name}.")

        elif action == 'open_access_log':
            log_paths = self._get_log_paths(service, 'access')
            opened = False
            for p in log_paths:
                if os.path.exists(p):
                    os.startfile(p)
                    opened = True
                    break
            if not opened:
                messagebox.showinfo("Not Found", f"Access log not found for {service.name}.")

        elif action == 'open_vhosts':
            if os.path.exists(NGINX_CONF_DIR):
                os.startfile(NGINX_CONF_DIR)
            else:
                messagebox.showinfo("Not Found", "vhosts directory not found.")

        elif action == 'ssl_manage':
            ssl_dir = os.path.join(NGINX_CONF_DIR, "ssl")
            if os.path.exists(ssl_dir):
                os.startfile(ssl_dir)
            else:
                messagebox.showinfo("SSL", f"SSL directory not found at:\n{ssl_dir}")

        elif action == 'open_console':
            base = service.get_base_folder()
            console_map = {
                'mysql': os.path.join(BIN_DIR, 'mysql', 'bin', 'mysql.exe'),
                'redis': os.path.join(BIN_DIR, 'redis', 'redis-cli.exe'),
                'pgsql': os.path.join(BIN_DIR, 'pgsql', 'bin', 'psql.exe'),
                'node': os.path.join(BIN_DIR, 'node', 'node.exe'),
            }
            exe = console_map.get(base)
            if exe and os.path.exists(exe):
                os.startfile(exe)
            else:
                messagebox.showinfo("Console", f"Console executable not found for {service.name}.")

        elif action == 'open_web_ui':
            import webbrowser
            webbrowser.open("http://localhost:8025")

        elif action in ('php_extensions', 'php_conf', 'phpinfo', 'php_version',
                        'npm_install'):
            self._placeholder_action(action.replace('_', ' ').title())

        else:
            self._placeholder_action(action or 'Unknown')

    def _get_conf_paths(self, service) -> list:
        """Returns a list of possible config file paths for a service."""
        base = os.path.join(BIN_DIR, service.get_base_folder())
        ver = service.active_version
        name = service.get_base_folder()
        paths = []

        if name == 'apache':
            paths = [
                os.path.join(base, ver, 'conf', 'httpd.conf') if ver else '',
                os.path.join(base, 'conf', 'httpd.conf'),
            ]
        elif name == 'nginx':
            paths = [
                os.path.join(base, ver, 'conf', 'nginx.conf') if ver else '',
                os.path.join(base, 'conf', 'nginx.conf'),
            ]
        elif name == 'mysql':
            paths = [
                os.path.join(base, ver, 'my.ini') if ver else '',
                os.path.join(base, 'my.ini'),
                os.path.join(base, ver, 'my.cnf') if ver else '',
                os.path.join(base, 'my.cnf'),
            ]
        elif name == 'php':
            paths = [
                os.path.join(base, ver, 'php.ini') if ver else '',
                os.path.join(base, 'php.ini'),
            ]
        elif name == 'redis':
            paths = [
                os.path.join(base, 'redis.conf'),
                os.path.join(base, 'redis.windows.conf'),
            ]
        elif name == 'pgsql':
            paths = [os.path.join(base, 'data', 'postgresql.conf')]
        elif name == 'mailpit':
            paths = [os.path.join(base, 'mailpit.conf')]

        return [p for p in paths if p]

    def _get_log_paths(self, service, log_type='error') -> list:
        """Returns a list of possible log file paths for a service."""
        base = os.path.join(BIN_DIR, service.get_base_folder())
        ver = service.active_version
        name = service.get_base_folder()
        paths = []

        if name in ('apache', 'nginx'):
            paths = [
                os.path.join(base, ver, 'logs', f'{log_type}.log') if ver else '',
                os.path.join(base, 'logs', f'{log_type}.log'),
            ]
        elif name == 'mysql':
            data_dir = os.path.join(base, ver, 'data') if ver else os.path.join(base, 'data')
            paths = [
                os.path.join(data_dir, f'{log_type}.log'),
                os.path.join(base, f'{log_type}.log'),
            ]
        elif name == 'php':
            paths = [
                os.path.join(base, ver, 'logs', f'{log_type}.log') if ver else '',
                os.path.join(base, 'logs', f'php_{log_type}.log'),
            ]
        elif name == 'redis':
            paths = [os.path.join(base, 'redis.log')]
        elif name == 'pgsql':
            paths = [os.path.join(base, 'data', 'pg_log')]

        return [p for p in paths if p]

    # ─────────────────────── Menu Actions ────────────────────────────
    def _placeholder_action(self, label=""):
        messagebox.showinfo("Coming Soon", f'"{label}" will be available in a future update.')

    def _open_settings(self, label=""):
        """Opens the full Preferences window with General + Services tabs."""
        win = ctk.CTkToplevel(self)
        win.title("Pygon Preferences")
        win.geometry("600x500")
        win.resizable(False, True)
        win.transient(self)
        win.grab_set()
        win.configure(fg_color=COL_BG)

        tabs = ctk.CTkTabview(win, fg_color=COL_SURFACE, corner_radius=8,
                              segmented_button_fg_color=COL_CARD,
                              segmented_button_selected_color=COL_ACCENT,
                              segmented_button_unselected_color=COL_CARD)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)

        # ── General Tab ──
        gen = tabs.add("General")
        gen.grid_columnconfigure(1, weight=1)
        row = 0

        general_settings = [
            ("run_on_startup", "Run Pygon when Windows starts", False),
            ("run_minimized", "Run minimized to tray", False),
            ("auto_start_all", "Start All services automatically", False),
            ("auto_vhost", "Auto-create Virtual Hosts ({name}.test)", True),
            ("auto_update", "Check for updates on startup", False),
        ]
        gen_vars = {}
        for key, label_text, default in general_settings:
            var = ctk.BooleanVar(value=self.config.get_general(key, default))
            gen_vars[key] = var
            ctk.CTkCheckBox(
                gen, text=label_text, variable=var,
                font=ctk.CTkFont(size=12),
                fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER,
                text_color=COL_TEXT
            ).grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=6)
            row += 1

        # Document Root
        ctk.CTkLabel(gen, text="Document Root:", font=ctk.CTkFont(size=12),
                     text_color=COL_TEXT).grid(row=row, column=0, sticky="w", padx=20, pady=(12, 4))
        docroot_var = ctk.StringVar(value=self.config.get_general("document_root", WWW_DIR))
        ctk.CTkEntry(gen, textvariable=docroot_var, font=ctk.CTkFont(size=11),
                     fg_color=COL_CARD, border_color=COL_BORDER, text_color=COL_TEXT
                     ).grid(row=row, column=1, sticky="ew", padx=(4, 20), pady=(12, 4))
        row += 1

        # Data Directory
        ctk.CTkLabel(gen, text="Data Directory:", font=ctk.CTkFont(size=12),
                     text_color=COL_TEXT).grid(row=row, column=0, sticky="w", padx=20, pady=4)
        datadir_var = ctk.StringVar(value=self.config.get_general("data_dir", BIN_DIR))
        ctk.CTkEntry(gen, textvariable=datadir_var, font=ctk.CTkFont(size=11),
                     fg_color=COL_CARD, border_color=COL_BORDER, text_color=COL_TEXT
                     ).grid(row=row, column=1, sticky="ew", padx=(4, 20), pady=4)
        row += 1

        # ── Services & Ports Tab ──
        svc_tab = tabs.add("Services & Ports")
        svc_tab.grid_columnconfigure(0, weight=1)
        svc_tab.grid_rowconfigure(0, weight=1)

        svc_scroll = ctk.CTkScrollableFrame(svc_tab, fg_color="transparent")
        svc_scroll.grid(row=0, column=0, sticky="nsew")
        svc_scroll.grid_columnconfigure(1, weight=1)

        # Header row
        for ci, txt in enumerate(["Enable", "Service", "Port", "SSL"]):
            ctk.CTkLabel(
                svc_scroll, text=txt, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COL_TEXT_DIM
            ).grid(row=0, column=ci, padx=8, pady=(4, 8), sticky="w")

        svc_vars = []
        services = self.registry.get_all_services()
        for i, svc in enumerate(services):
            svc_row = i + 1
            enabled_var = ctk.BooleanVar(value=self.config.get_service_enabled(svc.name))
            ssl_var = ctk.BooleanVar(value=self.config.get_service_ssl(svc.name))
            port_var = ctk.StringVar(value=str(svc.current_port))

            ctk.CTkCheckBox(svc_scroll, text="", variable=enabled_var, width=24,
                            fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER
                            ).grid(row=svc_row, column=0, padx=8, pady=3)
            ctk.CTkLabel(svc_scroll, text=svc.name, font=ctk.CTkFont(size=12),
                         text_color=COL_TEXT).grid(row=svc_row, column=1, sticky="w", padx=4, pady=3)
            ctk.CTkEntry(svc_scroll, textvariable=port_var, width=70, height=26,
                         font=ctk.CTkFont(size=11, family="Consolas"),
                         fg_color=COL_CARD, border_color=COL_BORDER, text_color=COL_TEXT,
                         justify="center").grid(row=svc_row, column=2, padx=8, pady=3)
            ctk.CTkCheckBox(svc_scroll, text="", variable=ssl_var, width=24,
                            fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER
                            ).grid(row=svc_row, column=3, padx=8, pady=3)

            svc_vars.append((svc, enabled_var, port_var, ssl_var))

        # Save / Cancel buttons
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        def _save_prefs():
            for key, var in gen_vars.items():
                self.config.set_general(key, var.get())
            self.config.set_general("document_root", docroot_var.get())
            self.config.set_general("data_dir", datadir_var.get())
            for svc, en_var, p_var, ssl_var in svc_vars:
                self.config.set_service_enabled(svc.name, en_var.get())
                self.config.set_service_ssl(svc.name, ssl_var.get())
                try:
                    port = int(p_var.get())
                    if 1 <= port <= 65535:
                        svc.set_custom_port(port)
                except ValueError:
                    pass
            # Apply Windows startup registry
            self._apply_startup_setting(gen_vars["run_on_startup"].get())
            self._rebuild_service_list()
            win.destroy()

        ctk.CTkButton(btn_frame, text="Save", width=100, fg_color=COL_ACCENT,
                      hover_color=COL_ACCENT_HOVER, command=_save_prefs
                      ).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color=COL_CARD,
                      hover_color=COL_CARD_HOVER, text_color=COL_TEXT,
                      command=win.destroy).pack(side="right", padx=4)

    def _apply_startup_setting(self, enabled: bool):
        """Add/remove Pygon from Windows startup registry."""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_SET_VALUE)
            if enabled:
                exe = sys.executable if not getattr(sys, 'frozen', False) else sys.executable
                winreg.SetValueEx(key, "Pygon", 0, winreg.REG_SZ, f'"{exe}" "{os.path.abspath(__file__)}"')
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
        """Toggle between dark and light themes."""
        global COL_BG, COL_SURFACE, COL_CARD, COL_CARD_HOVER, COL_BORDER
        global COL_TEXT, COL_TEXT_DIM, COL_ACCENT, COL_ACCENT_HOVER
        global COL_DANGER, COL_DANGER_HOVER, COL_WARNING
        global COL_TAB_BG, COL_TAB_SEL, COL_CONSOLE_BG, COL_STATUS_BAR

        new_theme = "light" if self._current_theme == "dark" else "dark"
        self._current_theme = new_theme
        self.config.set_theme(new_theme)

        t = get_theme_colors(new_theme)
        COL_BG = t["bg"]; COL_SURFACE = t["surface"]; COL_CARD = t["card"]
        COL_CARD_HOVER = t["card_hover"]; COL_BORDER = t["border"]
        COL_TEXT = t["text"]; COL_TEXT_DIM = t["text_dim"]
        COL_ACCENT = t["accent"]; COL_ACCENT_HOVER = t["accent_hover"]
        COL_DANGER = t["danger"]; COL_DANGER_HOVER = t["danger_hover"]
        COL_WARNING = t["warning"]; COL_TAB_BG = t["tab_bg"]
        COL_TAB_SEL = t["card_hover"]; COL_CONSOLE_BG = t["console_bg"]
        COL_STATUS_BAR = t["status_bar"]

        ctk.set_appearance_mode("Dark" if new_theme == "dark" else "Light")
        self.theme_btn.configure(text="☀" if new_theme == "dark" else "🌙")

        # Rebuild UI with new colors
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=COL_BG)
        self.service_ui_map = {}
        self._build_ui()
        self.update_status()
        self._update_system_info()
        self._update_console_logs()

    def _open_hosts_file(self):
        """Opens the Windows hosts file in Notepad."""
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            os.startfile(hosts_path)
        except Exception:
            import subprocess
            subprocess.Popen(["notepad.exe", hosts_path])

    def _open_web(self):
        """Opens the default web browser to 127.0.0.1."""
        import webbrowser
        webbrowser.open("http://127.0.0.1")

    def _open_database(self):
        """Opens MySQL CLI or falls back to a message."""
        mysql_exe = os.path.join(BIN_DIR, "mysql", "bin", "mysql.exe")
        if os.path.exists(mysql_exe):
            import subprocess
            subprocess.Popen(["cmd", "/k", mysql_exe, "-u", "root"], creationflags=0x10)
        else:
            messagebox.showinfo("Database", "MySQL client not found.\nInstall MySQL first.")

    def _open_terminal(self):
        """Opens a terminal in the WWW_DIR directory."""
        import subprocess
        subprocess.Popen(["cmd", "/k", f"cd /d {WWW_DIR}"], creationflags=0x10)

    def open_document_root(self):
        os.startfile(WWW_DIR)

    # ─────────────────────── Download UI ─────────────────────────────
    def _run_download_with_ui(self, service_display_name: str, dl_key: str, target_folder: str) -> bool:
        """Shows a progress bar popup while downloading a service."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Downloading {service_display_name}")
        popup.geometry("420x200")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        popup.configure(fg_color=COL_SURFACE)

        lbl = ctk.CTkLabel(
            popup, text=f"Downloading {service_display_name}...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COL_TEXT
        )
        lbl.pack(pady=(25, 10))

        progress = ctk.CTkProgressBar(
            popup, width=340,
            progress_color=COL_ACCENT,
            fg_color=COL_BORDER
        )
        progress.pack(pady=5)
        progress.set(0)

        status_lbl = ctk.CTkLabel(
            popup, text="Starting download...",
            text_color=COL_TEXT_DIM,
            font=ctk.CTkFont(size=12)
        )
        status_lbl.pack(pady=5)

        download_result = [False]

        popup.after(0, lambda: progress.configure(mode="indeterminate"))
        popup.after(0, progress.start)

        def status_callback(msg: str):
            popup.after(0, lambda: status_lbl.configure(text=msg))

        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            mb_downloaded = downloaded / (1024 * 1024)

            if total_size > 0:
                percent = downloaded / total_size
                popup.after(0, lambda p=percent: progress.set(min(1.0, p)))
                mb_total = total_size / (1024 * 1024)
                popup.after(0, lambda md=mb_downloaded, mt=mb_total:
                            status_lbl.configure(text=f"{md:.1f} MB / {mt:.1f} MB"))
            else:
                popup.after(0, lambda md=mb_downloaded:
                            status_lbl.configure(text=f"{md:.1f} MB downloaded..."))

        def download_thread():
            popup.after(0, lambda: lbl.configure(text=f"Downloading {service_display_name}..."))
            success = self.downloader.download_and_extract(
                dl_key, target_folder,
                progress_callback=reporthook,
                status_callback=status_callback
            )
            popup.after(0, lambda: lbl.configure(text=f"Extracting... (Please wait)"))

            if success:
                popup.after(0, progress.stop)
                popup.after(0, lambda: progress.configure(mode="determinate"))
                popup.after(0, lambda: progress.set(1.0))
                popup.after(0, lambda: status_lbl.configure(text="Complete!", text_color=COL_ACCENT))
            else:
                popup.after(0, progress.stop)
                popup.after(0, lambda: progress.configure(mode="determinate", progress_color=COL_DANGER))
                popup.after(0, lambda: progress.set(1.0))

            download_result[0] = success
            popup.after(2500 if not success else 1000, popup.destroy)

        popup.update()
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        self.wait_window(popup)
        return download_result[0]


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
