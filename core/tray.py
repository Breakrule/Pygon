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
        
        # Menu
        menu = QMenu()
        
        show_action = menu.addAction("Show Dashboard")
        show_action.triggered.connect(self.on_show)
        
        menu.addSeparator()
        
        # List services (read-only info)
        for service in self.app.registry.get_all_services():
            item = menu.addAction(f"{service.name} (Port {service.default_port})")
            item.setEnabled(False)
            
        menu.addSeparator()
        
        start_all = menu.addAction("Start All")
        start_all.triggered.connect(self.on_start_all)
        
        stop_all = menu.addAction("Stop All")
        stop_all.triggered.connect(self.on_stop_all)
        
        open_www = menu.addAction("Open Web Root")
        open_www.triggered.connect(self.on_open_www)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit Pygon")
        quit_action.triggered.connect(self.on_quit)
        
        self.tray_icon.setContextMenu(menu)
        
        # Double click to show
        self.tray_icon.activated.connect(self._on_activated)
        
        self.tray_icon.show()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.on_show()

    def on_show(self):
        self.app.show()
        self.app.setWindowState(self.app.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
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
