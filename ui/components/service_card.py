from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction

class ServiceCard(QFrame):
    def __init__(self, parent, service, colors, on_toggle, on_menu, on_db_manager=None):
        super().__init__(parent)
        self.service = service
        self.colors = colors
        self.on_toggle = on_toggle
        self.on_menu = on_menu
        self.on_db_manager = on_db_manager
        
        self.setObjectName("ServiceCard")
        self.setMinimumHeight(85)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 8, 15, 8)
        self.layout.setSpacing(12)
        
        self._build_card()

    def _get_service_badge(self):
        """Returns a 2-letter badge based on service name."""
        name = self.service.name.lower()
        if "mysql" in name: return "My"
        if "mariadb" in name: return "Md"
        if "apache" in name: return "Ap"
        if "nginx" in name: return "Nx"
        if "php" in name: return "Ph"
        if "node" in name: return "Nd"
        if "redis" in name: return "Rd"
        if "pgsql" in name: return "Pg"
        if "mailpit" in name: return "Mp"
        return "SV"

    def _build_card(self):
        # Icon Frame (Badge)
        icon_color = getattr(self.service, 'icon_color', self.colors["accent"])
        self.icon_frame = QFrame()
        self.icon_frame.setFixedSize(46, 46)
        self.icon_frame.setStyleSheet(f"background-color: {icon_color}; border-radius: 23px;") # Circle
        
        icon_layout = QVBoxLayout(self.icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_lbl = QLabel(self._get_service_badge())
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.icon_lbl.setStyleSheet("color: white; background: transparent;")
        icon_layout.addWidget(self.icon_lbl)
        
        self.layout.addWidget(self.icon_frame)
        
        # Name & Port
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        self.name_lbl = QLabel(self.service.name)
        self.name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.name_lbl)
        
        self.port_lbl = QLabel(f"Port: {self.service.current_port}")
        self.port_lbl.setObjectName("DimText")
        self.port_lbl.setFont(QFont("Segoe UI", 10))
        info_layout.addWidget(self.port_lbl)
        
        self.metrics_lbl = QLabel("")
        self.metrics_lbl.setObjectName("DimText")
        self.metrics_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.metrics_lbl.setStyleSheet(f"color: {self.colors['accent']};")
        info_layout.addWidget(self.metrics_lbl)
        
        self.layout.addLayout(info_layout)
        self.layout.addStretch()
        
        # Version Dropdown
        versions = self.service.get_available_versions()
        if versions:
            self.dropdown = QComboBox()
            self.dropdown.setMinimumWidth(110)
            self.dropdown.setFixedHeight(32)
            self.dropdown.setToolTip("Switch between installed versions")
            
            display_versions = [self.service.get_version_display(v) for v in versions]
            self.ver_map = {self.service.get_version_display(v): v for v in versions}
            self.dropdown.addItems(display_versions)
            self.dropdown.setCurrentText(self.service.get_version_display(self.service.active_version))
            
            self.dropdown.currentTextChanged.connect(self._on_version_changed)
            self.layout.addWidget(self.dropdown)
        else:
            self.dropdown = None

        # Toggle Button
        self.toggle_btn = QPushButton("START")
        self.toggle_btn.setObjectName("AccentButton")
        self.toggle_btn.setMinimumWidth(100)
        self.toggle_btn.setFixedHeight(40)
        self.toggle_btn.setToolTip("Start or Stop this service")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(lambda: self.on_toggle(self.service))
        self.layout.addWidget(self.toggle_btn)
        
        # Menu Button
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setObjectName("MenuButton")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setToolTip("Service actions and configurations")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(lambda: self.on_menu(self.service, self.menu_btn))
        self.layout.addWidget(self.menu_btn)

    def _on_version_changed(self, text):
        if text in self.ver_map:
            self.service.set_active_version(self.ver_map[text])

    def update_status(self):
        running = self.service.is_running()
        if running:
            self.toggle_btn.setText("STOP")
            self.toggle_btn.setObjectName("DangerButton")
            if self.dropdown: self.dropdown.setEnabled(False)
        else:
            self.toggle_btn.setText("START")
            self.toggle_btn.setObjectName("AccentButton")
            if self.dropdown: self.dropdown.setEnabled(True)
        
        # Force stylesheet refresh to update colors based on object name
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
        
        self.port_lbl.setText(f"Port: {self.service.current_port}")

    def contextMenuEvent(self, event):
        self.on_menu(self.service, self)

    def update_metrics(self, cpu_val, mem_val):
        if cpu_val == 0 and mem_val == 0:
            self.metrics_lbl.setText("")
        else:
            # Convert bytes to MB
            mem_mb = mem_val / (1024 * 1024)
            self.metrics_lbl.setText(f"CPU: {cpu_val:.1f}% | RAM: {mem_mb:.1f}MB")
