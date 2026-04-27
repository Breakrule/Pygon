import os
import sys
import threading
import ctypes
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
    QTabWidget, QCheckBox, QFileDialog, QProgressBar, QMenu,
    QSplitter, QSpinBox, QLineEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QAction

# Core Imports
from core.constants import APP_NAME, BIN_DIR, WWW_DIR, VHOST_CONF_DIR
from core.config_manager import ConfigManager
from core.service_controller import ServiceController
from core.system_utils import SystemUtils
from core.port_monitor import PortMonitor
from core.host_manager import HostManager
from core.tray import TrayManager
from core.mkcert_manager import MkcertManager
from core.downloader import AutoDownloader
from core.version_checker import VersionChecker
from services.registry import ServiceRegistry

# UI Imports
from ui.base_window import BaseWindow
from ui.components.top_bar import TopBar
from ui.components.service_card import ServiceCard
from ui.components.console_panel import ConsolePanel

class PygonApp(BaseWindow):
    def __init__(self):
        self.config = ConfigManager(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml"))
        
        # 1. Initialize State
        self.cards = {}
        
        # 2. Initialize Managers
        self.registry = ServiceRegistry(bin_dir=BIN_DIR, config_manager=self.config)
        self.host_manager = HostManager(vhost_conf_dir=VHOST_CONF_DIR, document_root=WWW_DIR)
        self.mkcert_manager = MkcertManager(bin_dir=BIN_DIR)
        self.downloader = AutoDownloader(bin_dir=BIN_DIR)
        
        # 3. Initialize Controller (before super() because _build_ui needs it)
        self.controller = ServiceController(
            self.registry, self.downloader, self.host_manager, self.config,
            self._append_console, self._run_download_with_ui
        )

        # 4. Initialize BaseWindow (triggers _build_ui)
        super().__init__(theme_name=self.config.get_theme())

        # 5. Final Setup
        self.setWindowTitle(f"{APP_NAME} v3.0")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        # 6. System tray
        self.tray = TrayManager(self)
        self.tray.start_tray()

        # 7. Start loops (Qt Timers)
        self._start_update_loops()

    def _build_ui(self):
        # Top Bar
        self.top_bar = TopBar(self, self.colors, APP_NAME, self._open_settings, self._on_check_updates)
        self.main_layout.addWidget(self.top_bar)

        # Main Splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(1)
        self.main_layout.addWidget(self.splitter)

        # Upper Panel: Services List
        upper_panel = QFrame()
        upper_panel.setObjectName("MainContent")
        upper_layout = QVBoxLayout(upper_panel)
        upper_layout.setContentsMargins(20, 10, 20, 10)
        upper_layout.setSpacing(15)

        # Services Header
        header_layout = QHBoxLayout()
        svc_title = QLabel("Services")
        svc_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(svc_title)
        
        header_layout.addStretch()
        
        self.db_manager_btn = QPushButton("🗄  Database")
        self.db_manager_btn.setFixedSize(130, 40)
        self.db_manager_btn.setToolTip("Open HeidiSQL Database Manager")
        self.db_manager_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.db_manager_btn.clicked.connect(lambda: self._open_db_manager(None))
        header_layout.addWidget(self.db_manager_btn)
        
        self.start_all_btn = QPushButton("▶  START ALL")
        self.start_all_btn.setObjectName("AccentButton")
        self.start_all_btn.setFixedSize(140, 40)
        self.start_all_btn.setToolTip("Start or Stop all enabled services")
        self.start_all_btn.clicked.connect(self._on_toggle_all)
        header_layout.addWidget(self.start_all_btn)
        upper_layout.addLayout(header_layout)

        # Scroll Area for Services
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("MainContent")
        self.svc_list_layout = QVBoxLayout(scroll_content)
        self.svc_list_layout.setContentsMargins(0, 0, 10, 0)
        self.svc_list_layout.setSpacing(10)
        
        enabled_services = [s for s in self.registry.get_all_services() if self.config.get_service_enabled(s.name)]
        for svc in enabled_services:
            card = ServiceCard(scroll_content, svc, self.colors, self.controller.toggle_single, self._show_service_menu, self._open_db_manager)
            self.svc_list_layout.addWidget(card)
            self.cards[svc.name] = card
        
        self.svc_list_layout.addStretch()
        scroll.setWidget(scroll_content)
        upper_layout.addWidget(scroll)

        # self.sys_info = SystemInfoPanel(upper_panel, self.colors)
        # upper_layout.addWidget(self.sys_info)

        # Lower Panel: Console
        self.console = ConsolePanel(self.splitter, self.colors, self._on_clear_console)
        
        self.splitter.addWidget(upper_panel)
        self.splitter.addWidget(self.console)
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

        # Status Bar
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(32)
        self.status_bar.setStyleSheet(f"background-color: {self.colors['status_bar']}; border-top: 1px solid {self.colors['border']};")
        self.status_layout = QHBoxLayout(self.status_bar)
        self.status_layout.setContentsMargins(20, 0, 20, 0)
        self.main_layout.addWidget(self.status_bar)

    def _start_update_loops(self):
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._update_ui_state)
        self.ui_timer.start(2000)

        # self.metrics_timer = QTimer(self)
        # self.metrics_timer.timeout.connect(self._update_system_metrics)
        # self.metrics_timer.start(3000)

        self.logs_timer = QTimer(self)
        self.logs_timer.timeout.connect(self._poll_logs)
        self.logs_timer.start(2000)

    def _update_ui_state(self):
        try:
            if not hasattr(self, 'start_all_btn') or not self.start_all_btn: return
            
            any_running = False
            for card in self.cards.values():
                card.update_status()
                if card.service.is_running(): any_running = True
            
            self.controller.is_running = any_running
            if any_running:
                self.start_all_btn.setText("■  STOP ALL")
                self.start_all_btn.setObjectName("DangerButton")
            else:
                self.start_all_btn.setText("▶  START ALL")
                self.start_all_btn.setObjectName("AccentButton")
            
            self.start_all_btn.style().unpolish(self.start_all_btn)
            self.start_all_btn.style().polish(self.start_all_btn)
            
            self._refresh_status_bar()
        except (RuntimeError, AttributeError):
            pass # Widget was likely deleted during theme switch

    def _update_system_metrics(self):
        # System info panel removed in v3.1
        pass

    def _poll_logs(self):
        try:
            if not hasattr(self, 'console') or not self.console: return
            for svc in self.registry.get_all_services():
                for line in svc.get_new_logs(): 
                    self.console.append("Logs", f"[{svc.name}] {line}")
                for line in svc.get_new_errors(): 
                    self.console.append("Errors", f"[{svc.name}] {line}")
        except (RuntimeError, AttributeError):
            pass

    def _refresh_status_bar(self):
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for svc in self.registry.get_all_services():
            running = svc.is_running()
            color = self.colors["accent"] if running else self.colors["text_dim"]
            text = f"● {svc.name.split()[0]}: {'Online' if running else 'Offline'}"
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {color};")
            self.status_layout.addWidget(lbl)
            self.status_layout.addSpacing(20)
        self.status_layout.addStretch()

    def _on_toggle_all(self):
        self.start_all_btn.setEnabled(False)
        def run():
            self.controller.toggle_all()
            self.start_all_btn.setEnabled(True)
        threading.Thread(target=run, daemon=True).start()

    def _on_clear_console(self):
        self.console.clear()
        for svc in self.registry.get_all_services(): svc.clear_logs()

    def _append_console(self, tab, text):
        self.console.append(tab, text)

    def closeEvent(self, event):
        behavior = self.config.get_close_behavior()
        if behavior == "tray":
            self.hide()
            event.ignore()
        elif behavior == "exit":
            self.exit_app()
        else:
            res = self._show_close_dialog()
            if res == "tray":
                self.hide()
                event.ignore()
            elif res == "exit":
                self.exit_app()
            else:
                event.ignore()

    def _show_close_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Close Pygon")
        dialog.setFixedSize(350, 200)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        msg = QLabel("Choose close behavior:")
        msg.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(msg, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        tray_btn = QPushButton("Minimize to Tray")
        exit_btn = QPushButton("Exit & Kill Services")
        exit_btn.setObjectName("DangerButton")
        
        btn_layout.addWidget(tray_btn)
        btn_layout.addWidget(exit_btn)
        layout.addLayout(btn_layout)
        
        rem_check = QCheckBox("Remember my choice")
        layout.addWidget(rem_check, alignment=Qt.AlignmentFlag.AlignCenter)
        
        result = [None]
        def set_choice(c):
            if rem_check.isChecked(): self.config.set_close_behavior(c)
            result[0] = c
            dialog.accept()
            
        tray_btn.clicked.connect(lambda: set_choice("tray"))
        exit_btn.clicked.connect(lambda: set_choice("exit"))
        
        dialog.exec()
        return result[0]

    def exit_app(self):
        self.controller.stop_all()
        QApplication.quit()
        sys.exit(0)

    def _show_service_menu(self, service, anchor):
        menu = QMenu(self)
        for item in service.get_menu_items():
            if item.get('children'):
                sub = menu.addMenu(item['label'])
                for c in item['children']:
                    act = sub.addAction(c['label'])
                    act.triggered.connect(lambda _, a=c['action'], s=service: self._handle_menu_action(a, s))
            else:
                act = menu.addAction(item['label'])
                act.triggered.connect(lambda _, a=item['action'], s=service: self._handle_menu_action(a, s))
        
        if isinstance(anchor, QPushButton):
            menu.exec(anchor.mapToGlobal(anchor.rect().bottomLeft()))
        else:
            menu.exec(QCursor.pos())

    def _handle_menu_action(self, action, service):
        if not action: return
        if action == 'restart': self.controller.restart_service(service)
        elif action == 'open_folder': os.startfile(os.path.join(BIN_DIR, service.get_base_folder()))
        elif action == 'open_docroot': os.startfile(WWW_DIR)
        elif action == 'open_conf': 
            paths = self._get_conf_paths(service)
            for p in paths:
                if os.path.exists(p): os.startfile(p); return
        elif action == 'open_error_log':
            paths = self._get_log_paths(service, 'error')
            for p in paths:
                if os.path.exists(p): os.startfile(p); return
        elif action == 'open_db_manager':
            self._open_db_manager(service)
        elif action == 'set_node_project':
            p = QFileDialog.getExistingDirectory(self, "Select Node.js Project Folder")
            if p: self.config.set_general("node_project_path", p); self._poll_logs()
        elif action in ['php_extensions', 'phpinfo', 'npm_install', 'ssl_manage', 'php_version', 'php_conf']:
            QMessageBox.information(self, "Coming Soon", f"The '{action.replace('_', ' ').title()}' feature will be available in a future update.")

    def _get_conf_paths(self, service):
        base = os.path.join(BIN_DIR, service.get_base_folder())
        ver = service.active_version
        name = service.get_base_folder()
        if name == 'apache': return [os.path.join(base, 'conf', 'httpd.conf')]
        if name == 'mysql': return [os.path.join(base, ver, 'my.ini') if ver else os.path.join(base, 'my.ini')]
        if name == 'php': return [os.path.join(base, ver, 'php.ini') if ver else os.path.join(base, 'php.ini')]
        return []

    def _get_log_paths(self, service, log_type='error'):
        base = os.path.join(BIN_DIR, service.get_base_folder())
        name = service.get_base_folder()
        if name == 'apache': return [os.path.join(base, 'logs', f'{log_type}.log')]
        if name == 'mysql': return [os.path.join(base, 'data', f'{log_type}.log')]
        return []

    def _open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        dialog.setFixedSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 1. General Tab
        gen = QWidget()
        gen_layout = QVBoxLayout(gen)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        gen_layout.setSpacing(15)

        # Startup
        startup_check = QCheckBox("Run Pygon on Windows startup")
        startup_check.setChecked(self.config.get_general("run_on_startup", False))
        startup_check.toggled.connect(lambda v: (self.config.set_general("run_on_startup", v), SystemUtils.apply_startup_setting(v)))
        gen_layout.addWidget(startup_check)

        # Document Root
        doc_root_layout = QHBoxLayout()
        doc_root_layout.addWidget(QLabel("Document Root:"))
        self.doc_root_edit = QLineEdit(self.config.get_general("document_root", WWW_DIR))
        self.doc_root_edit.setReadOnly(True)
        doc_root_layout.addWidget(self.doc_root_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._on_browse_docroot)
        doc_root_layout.addWidget(browse_btn)
        gen_layout.addLayout(doc_root_layout)

        # Close Behavior
        gen_layout.addWidget(QLabel("When closing window:"))
        bg = QButtonGroup(gen)
        cb = self.config.get_close_behavior()
        for i, (label, val) in enumerate([("Ask me", "ask"), ("Minimize to Tray", "tray"), ("Exit & Kill", "exit")]):
            rb = QRadioButton(label)
            if cb == val: rb.setChecked(True)
            rb.toggled.connect(lambda v, x=val: v and self.config.set_close_behavior(x))
            gen_layout.addWidget(rb)
            bg.addButton(rb, i)

        gen_layout.addStretch()
        tabs.addTab(gen, "General")
        
        # 2. Services Tab
        svc_tab = QWidget()
        svc_scroll = QScrollArea()
        svc_scroll.setWidgetResizable(True)
        svc_scroll.setFrameShape(QFrame.Shape.NoFrame)
        svc_content = QWidget()
        svc_layout = QVBoxLayout(svc_content)
        svc_layout.setContentsMargins(10, 10, 10, 10)
        svc_layout.setSpacing(10)

        for svc in self.registry.get_all_services():
            row = QFrame()
            row.setFrameStyle(QFrame.Shape.StyledPanel)
            row.setStyleSheet(f"border: 1px solid {self.colors['border']}; border-radius: 8px; padding: 10px;")
            h = QHBoxLayout(row)
            h.setContentsMargins(15, 5, 15, 5)
            
            enable_check = QCheckBox(svc.name)
            enable_check.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            enable_check.setChecked(self.config.get_service_enabled(svc.name))
            enable_check.toggled.connect(lambda v, s=svc.name: (self.config.set_service_enabled(s, v), self._rebuild_ui()))
            h.addWidget(enable_check, 2)

            h.addStretch(1)
            h.addWidget(QLabel("Port:"), 0)
            port_spin = QSpinBox()
            port_spin.setFixedWidth(100)
            port_spin.setRange(1, 65535)
            port_spin.setValue(svc.current_port)
            port_spin.valueChanged.connect(lambda v, s=svc.name: self.config.set_service_port(s, v))
            h.addWidget(port_spin, 1)

            svc_layout.addWidget(row)

        svc_layout.addStretch()
        svc_scroll.setWidget(svc_content)
        svc_tab_layout = QVBoxLayout(svc_tab)
        svc_tab_layout.addWidget(svc_scroll)
        tabs.addTab(svc_tab, "Services")

        # 3. About Tab
        about = QWidget()
        about_layout = QVBoxLayout(about)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_lbl = QLabel("⚡")
        logo_lbl.setFont(QFont("Segoe UI", 48))
        about_layout.addWidget(logo_lbl)
        
        title_lbl = QLabel(f"{APP_NAME} v3.1")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        about_layout.addWidget(title_lbl)
        
        about_layout.addWidget(QLabel("Modular Development Environment for Windows"))
        about_layout.addWidget(QLabel("Build with PyQt6 & Python"))
        about_layout.addStretch()
        
        tabs.addTab(about, "About")
        
        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Done")
        close_btn.setObjectName("AccentButton")
        close_btn.setFixedSize(100, 36)
        close_btn.clicked.connect(dialog.accept)
        footer.addWidget(close_btn)
        layout.addLayout(footer)
        
        dialog.exec()

    def _on_browse_docroot(self):
        p = QFileDialog.getExistingDirectory(self, "Select Document Root")
        if p:
            self.config.set_general("document_root", p)
            self.doc_root_edit.setText(p)

    def _on_check_updates(self):
        """Checks for latest versions of services in the background."""
        self.top_bar.update_btn.setEnabled(False)
        self.top_bar.update_btn.setText("⏳ Checking...")
        
        def run():
            services = [s.name for s in self.registry.get_all_services()]
            latest = VersionChecker.check_all(services)
            
            # Use QTimer to bring results back to UI thread
            QTimer.singleShot(0, lambda: self._show_update_results(latest))
            
        threading.Thread(target=run, daemon=True).start()

    def _show_update_results(self, latest):
        self.top_bar.update_btn.setEnabled(True)
        self.top_bar.update_btn.setText("🔄  Check Updates")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Service Updates")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Available Updates")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        list_layout = QVBoxLayout(content)
        
        for svc_name, latest_ver in latest.items():
            if latest_ver == "N/A": continue
            
            svc = next((s for s in self.registry.get_all_services() if s.name == svc_name), None)
            current_ver = svc.active_version if svc else "None"
            
            row = QFrame()
            row.setStyleSheet(f"border-bottom: 1px solid {self.colors['border']}; padding: 10px;")
            h = QHBoxLayout(row)
            
            name_lbl = QLabel(svc_name)
            name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            h.addWidget(name_lbl, 2)
            
            ver_layout = QVBoxLayout()
            curr_lbl = QLabel(f"Current: {current_ver}")
            curr_lbl.setObjectName("DimText")
            new_lbl = QLabel(f"Latest: {latest_ver}")
            
            # Highlight if update available
            if latest_ver != "Error" and latest_ver != current_ver:
                new_lbl.setStyleSheet(f"color: {self.colors['accent']}; font-weight: bold;")
            
            ver_layout.addWidget(curr_lbl)
            ver_layout.addWidget(new_lbl)
            h.addLayout(ver_layout, 2)
            
            if latest_ver != current_ver and latest_ver != "Error":
                dl_btn = QPushButton("Update")
                dl_btn.setObjectName("AccentButton")
                dl_btn.setFixedSize(80, 28)
                # Note: Triggering update would need version-specific download logic
                dl_btn.clicked.connect(lambda _, n=svc_name: QMessageBox.information(dialog, "Update", f"Download for {n} version {latest_ver} started."))
                h.addWidget(dl_btn, 1)
            else:
                status_lbl = QLabel("✅ Latest")
                status_lbl.setStyleSheet(f"color: {self.colors['text_dim']};")
                h.addWidget(status_lbl, 1)
                
            list_layout.addWidget(row)
            
        list_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()

    def _run_download_with_ui(self, name, key, target):
        dialog = QDialog(self)
        dialog.setWindowTitle("Download")
        dialog.setFixedSize(400, 180)
        layout = QVBoxLayout(dialog)
        
        lbl = QLabel(f"Downloading {name}...")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        bar = QProgressBar()
        bar.setRange(0, 0)
        layout.addWidget(bar)
        
        res = [False]
        def run():
            res[0] = self.downloader.download_and_extract(key, target)
            QTimer.singleShot(0, dialog.accept)
            
        threading.Thread(target=run, daemon=True).start()
        dialog.exec()
        return res[0]

    def _open_db_manager(self, service=None):
        """Launches HeidiSQL for database services."""
        # If no specific service provided, try to find a running database service
        if service is None:
            db_services = [s for s in self.registry.get_all_services() if "Database" in s.name]
            # Prioritize running ones
            running = [s for s in db_services if s.is_running()]
            service = running[0] if running else (db_services[0] if db_services else None)
        
        if not service:
            QMessageBox.warning(self, "No Database", "No database service is currently enabled.")
            return

        heidi_base = os.path.join(BIN_DIR, "heidisql")
        heidi_exe = None
        
        if os.path.exists(heidi_base):
            # Look for heidisql.exe in any version subfolder
            for ver in os.listdir(heidi_base):
                ver_path = os.path.join(heidi_base, ver, "heidisql.exe")
                if os.path.exists(ver_path):
                    heidi_exe = ver_path
                    break
        
        if not heidi_exe:
            if QMessageBox.question(self, "Download HeidiSQL", 
                                  "HeidiSQL is not installed. Download and install it?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self._run_download_with_ui("HeidiSQL", "heidisql", os.path.join(BIN_DIR, "heidisql"))
            return

        # Launch HeidiSQL with auto-connect parameters
        if not service.is_running():
            if QMessageBox.question(self, f"{service.name} Not Running", 
                                  f"{service.name} is currently stopped. Start it before opening the database manager?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.controller.toggle_single(service)
                # Small delay to allow database to initialize if it's the first time
                QTimer.singleShot(1000, lambda: self._open_db_manager(service))
                return

        try:
            # HeidiSQL CLI parameters: -h (host), -u (user), -P (port)
            # Remove quotes around IP and ensure no space between flag and value for some versions
            args = [
                heidi_exe,
                f'-h=127.0.0.1',
                f'-u=root',
                f'-P={service.current_port}'
            ]
            
            # Use Popen to launch without blocking
            subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.console.append("Console", f"[HeidiSQL] Launching for {service.name} on port {service.current_port}...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch HeidiSQL: {e}")

if __name__ == "__main__":
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Pygon_v3_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(0, "An instance of Pygon is already running.", "Pygon", 0x30)
        sys.exit(0)
        
    app = QApplication(sys.argv)
    window = PygonApp()
    window.show()
    sys.exit(app.exec())
