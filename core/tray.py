from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

class TrayManager:
    def __init__(self, app_instance):
        """
        :param app_instance: Reference to the main PygonApp (QMainWindow).
        """
        self.app = app_instance
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setToolTip("Pygon Local Server")
        
    def create_icon(self):
        """Generate a simple default icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#10B981")) # Pygon Green
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()
        
        return QIcon(pixmap)

    def start_tray(self):
        """Initializes and shows the system tray icon."""
        self.tray_icon.setIcon(self.create_icon())
        
        self.menu = QMenu()
        self.menu.aboutToShow.connect(self._rebuild_menu)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_activated)
        self.tray_icon.show()

    def _rebuild_menu(self):
        """Dynamic menu generation based on current service states."""
        self.menu.clear()
        
        show_action = self.menu.addAction("Show Dashboard")
        show_action.triggered.connect(self.on_show)
        
        self.menu.addSeparator()
        
        # ── Service Control Submenus ──────────────────────────────────
        for service in self.app.registry.get_all_services():
            is_running = service.is_running()
            status_dot = "●" if is_running else "○"
            svc_menu = self.menu.addMenu(f"{status_dot} {service.name}")
            
            toggle_text = "Stop Service" if is_running else "Start Service"
            toggle_act = svc_menu.addAction(toggle_text)
            toggle_act.triggered.connect(lambda checked, s=service: self.app.controller.toggle_single(s))
            
            if is_running:
                restart_act = svc_menu.addAction("Restart Service")
                restart_act.triggered.connect(lambda checked, s=service: self.app.controller.restart_service(s))
            
            svc_menu.addSeparator()
            
            # Config & Logs
            log_act = svc_menu.addAction("View Logs")
            log_act.triggered.connect(lambda checked, s=service: s.open_error_log())
            
            conf_act = svc_menu.addAction("Edit Config")
            conf_act.triggered.connect(lambda checked, s=service: s.open_conf())

        self.menu.addSeparator()
        
        start_all = self.menu.addAction("▶  Start All Services")
        start_all.triggered.connect(self.on_start_all)
        
        stop_all = self.menu.addAction("⏹  Stop All Services")
        stop_all.triggered.connect(self.on_stop_all)
        
        self.menu.addSeparator()
        
        open_www = self.menu.addAction("📁  Open Web Root (www)")
        open_www.triggered.connect(self.on_open_www)
        
        self.menu.addSeparator()
        
        quit_action = self.menu.addAction("Exit Pygon")
        quit_action.triggered.connect(self.on_quit)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.on_show()

    def on_show(self):
        self.app.show()
        self.app.raise_()
        self.app.activateWindow()

    def on_start_all(self):
        self.app._on_toggle_all()

    def on_stop_all(self):
        self.app.controller.stop_all()
        
    def on_open_www(self):
        import os
        from core.constants import WWW_DIR
        os.startfile(WWW_DIR)

    def on_quit(self):
        self.app.exit_app()
