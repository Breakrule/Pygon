from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class TopBar(QWidget):
    def __init__(self, parent, colors, app_name, on_open_settings, on_check_updates):
        super().__init__(parent)
        self.colors = colors
        self.on_open_settings = on_open_settings
        self.on_check_updates = on_check_updates
        
        self.setFixedHeight(60)
        self.setObjectName("TopBar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)
        
        # Left — Title
        self.title_lbl = QLabel(app_name)
        self.title_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {colors['accent']}; letter-spacing: 1px;")
        layout.addWidget(self.title_lbl)
        
        layout.addStretch()
        
        # Check Updates
        self.update_btn = QPushButton("🔄  Check Updates")
        self.update_btn.setFixedSize(150, 40)
        self.update_btn.setToolTip("Check for new versions of MySQL, PHP, and Node.js")
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.clicked.connect(self.on_check_updates)
        layout.addWidget(self.update_btn)
        
        # Right — Settings
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFont(QFont("Segoe UI Emoji", 14))
        self.settings_btn.setFixedSize(48, 44)
        self.settings_btn.setToolTip("Open Preferences and Port settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.on_open_settings)
        self.settings_btn.setStyleSheet("padding: 0px; text-align: center;")
        layout.addWidget(self.settings_btn)
