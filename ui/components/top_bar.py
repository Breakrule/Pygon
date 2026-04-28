from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class TopBar(QWidget):
    def __init__(self, parent, colors, app_name, on_open_settings, on_open_shell, on_open_console, on_profile_change, on_add_profile):
        super().__init__(parent)
        self.colors = colors
        self.on_open_settings = on_open_settings
        self.on_open_shell = on_open_shell
        self.on_open_console = on_open_console
        self.on_profile_change = on_profile_change
        self.on_add_profile = on_add_profile
        
        self.setFixedHeight(70)
        self.setObjectName("TopBar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 0, 25, 0)
        layout.setSpacing(15)
        
        # Left — Title
        self.title_lbl = QLabel(app_name)
        self.title_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {colors['accent']}; letter-spacing: 1.2px;")
        layout.addWidget(self.title_lbl)
        
        layout.addStretch()

        # Profile Selector
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(160)
        self.profile_combo.setFixedHeight(36)
        self.profile_combo.setToolTip("Switch between service profiles")
        self.profile_combo.addItem("Default Profile")
        self.profile_combo.currentTextChanged.connect(self.on_profile_change)
        layout.addWidget(self.profile_combo)
        
        self.add_profile_btn = QPushButton("+")
        self.add_profile_btn.setFixedSize(30, 36)
        self.add_profile_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.add_profile_btn.setToolTip("Create new profile from current state")
        self.add_profile_btn.clicked.connect(self._on_add_profile_clicked)
        layout.addWidget(self.add_profile_btn)
        
        # Shell Button
        self.shell_btn = QPushButton("💻  Shell")
        self.shell_btn.setMinimumWidth(120)
        self.shell_btn.setFixedHeight(40)
        self.shell_btn.setToolTip("Open Pygon Shell with active binaries in PATH")
        self.shell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shell_btn.clicked.connect(self.on_open_shell)
        layout.addWidget(self.shell_btn)

        # Terminal Button
        self.terminal_btn = QPushButton("📟  Terminal")
        self.terminal_btn.setMinimumWidth(120)
        self.terminal_btn.setFixedHeight(40)
        self.terminal_btn.setToolTip("Open Console, Logs, and Errors")
        self.terminal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.terminal_btn.clicked.connect(self.on_open_console)
        layout.addWidget(self.terminal_btn)
        
        # Right — Settings
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFont(QFont("Segoe UI Emoji", 16))
        self.settings_btn.setFixedSize(50, 45)
        self.settings_btn.setToolTip("Open Preferences and Port settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.on_open_settings)
        self.settings_btn.setStyleSheet("padding: 0px; text-align: center;")
        layout.addWidget(self.settings_btn)

    def _on_add_profile_clicked(self):
        if self.on_add_profile:
            self.on_add_profile()