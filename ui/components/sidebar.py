from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class Sidebar(QWidget):
    def __init__(self, parent, colors, app_name, on_open_settings, on_open_shell, on_open_console, on_open_db, on_profile_change, on_add_profile):
        super().__init__(parent)
        self.colors = colors
        self.on_open_settings = on_open_settings
        self.on_open_shell = on_open_shell
        self.on_open_console = on_open_console
        self.on_open_db = on_open_db
        self.on_profile_change = on_profile_change
        self.on_add_profile = on_add_profile
        
        self.setFixedWidth(260)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            QWidget#Sidebar {{
                background-color: {colors['surface']};
                border-right: 1px solid {colors['border']};
            }}
            QPushButton#NavButton {{
                background-color: transparent;
                color: {colors['text_dim']};
                border: none;
                text-align: left;
                padding: 12px 20px;
                font-size: 11pt;
                font-weight: 500;
                border-radius: 8px;
            }}
            QPushButton#NavButton:hover {{
                background-color: {colors['card_hover']};
                color: {colors['accent']};
            }}
            QPushButton#NavButton[active="true"] {{
                background-color: {colors['accent']}20;
                color: {colors['accent']};
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 30, 15, 20)
        layout.setSpacing(10)
        
        # 1. Logo / Title
        self.title_lbl = QLabel(app_name)
        self.title_lbl.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {colors['accent']}; margin-bottom: 20px; padding-left: 10px;")
        layout.addWidget(self.title_lbl)
        
        layout.addSpacing(10)
        
        # 2. Navigation Section
        layout.addWidget(self._create_section_label("GENERAL"))
        
        self.dash_btn = self._create_nav_btn("📊  Dashboard", None)
        self.dash_btn.setProperty("active", "true")
        layout.addWidget(self.dash_btn)
        
        self.shell_btn = self._create_nav_btn("💻  Shell", self.on_open_shell)
        layout.addWidget(self.shell_btn)
        
        self.terminal_btn = self._create_nav_btn("📟  Terminal", self.on_open_console)
        layout.addWidget(self.terminal_btn)
        
        layout.addSpacing(15)
        layout.addWidget(self._create_section_label("TOOLS"))
        
        self.db_btn = self._create_nav_btn("🗄  Database", lambda: self.on_open_db())
        layout.addWidget(self.db_btn)
        
        self.settings_btn = self._create_nav_btn("⚙️  Settings", self.on_open_settings)
        layout.addWidget(self.settings_btn)
        
        layout.addStretch()
        
        # 3. Profile Section (At the bottom)
        layout.addWidget(self._create_section_label("PROFILE"))
        
        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(8)
        
        self.profile_combo = QComboBox()
        self.profile_combo.setFixedHeight(40)
        self.profile_combo.setToolTip("Switch between service profiles")
        self.profile_combo.currentTextChanged.connect(self.on_profile_change)
        profile_layout.addWidget(self.profile_combo)
        
        self.add_profile_btn = QPushButton("＋ Create New Profile")
        self.add_profile_btn.setFixedHeight(36)
        self.add_profile_btn.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        self.add_profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_profile_btn.clicked.connect(self.on_add_profile)
        self.add_profile_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors['accent']};
                border: 1px solid {colors['accent']}40;
                border-radius: 6px;
                padding: 0 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']}15;
                border: 1px solid {colors['accent']};
            }}
        """)
        profile_layout.addWidget(self.add_profile_btn)
        
        layout.addLayout(profile_layout)

    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {self.colors['text_dim']}; margin-top: 10px; margin-bottom: 5px; padding-left: 10px;")
        return lbl

    def _create_nav_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setFixedHeight(45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if callback:
            btn.clicked.connect(callback)
        return btn
