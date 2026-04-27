import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QCheckBox, QLineEdit, QFileDialog, 
    QScrollArea, QFrame, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from core.constants import APP_NAME, WWW_DIR, BIN_DIR, BASE_DIR
from core.system_utils import SystemUtils

class SettingsDialog(QDialog):
    def __init__(self, parent, config, registry, colors, rebuild_ui_cb):
        super().__init__(parent)
        self.config = config
        self.registry = registry
        self.colors = colors
        self.rebuild_ui = rebuild_ui_cb
        
        self.setWindowTitle("Preferences")
        self.setMinimumSize(750, 650)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self._setup_general_tab()
        self._setup_services_tab()
        self._setup_about_tab()
        
        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Done")
        close_btn.setObjectName("AccentButton")
        close_btn.setFixedSize(100, 36)
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        layout.addLayout(footer)

    def _setup_general_tab(self):
        gen = QWidget()
        gen_layout = QVBoxLayout(gen)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        gen_layout.setSpacing(15)
        
        # Startup Settings
        gen_layout.addWidget(QLabel("Startup & Behavior"))
        h_startup = QVBoxLayout()
        h_startup.setSpacing(10)
        
        startup_check = QCheckBox("Run Pygon on Windows startup")
        startup_check.setChecked(self.config.get_general("run_on_startup", False))
        startup_check.toggled.connect(lambda v: (self.config.set_general("run_on_startup", v), SystemUtils.apply_startup_setting(v)))
        h_startup.addWidget(startup_check)
        
        min_check = QCheckBox("Run Minimized to Tray")
        min_check.setChecked(self.config.get_general("run_minimized", False))
        min_check.toggled.connect(lambda v: self.config.set_general("run_minimized", v))
        h_startup.addWidget(min_check)
        
        auto_check = QCheckBox("Start All Services Automatically on Launch")
        auto_check.setChecked(self.config.get_general("autostart_all", False))
        auto_check.toggled.connect(lambda v: self.config.set_general("autostart_all", v))
        h_startup.addWidget(auto_check)
        gen_layout.addLayout(h_startup)

        gen_layout.addSpacing(10)

        # Document Root
        doc_root_layout = QHBoxLayout()
        doc_root_layout.addWidget(QLabel("Web Root (www):"), 2)
        self.doc_root_edit = QLineEdit(self.config.get_general("document_root", WWW_DIR))
        self.doc_root_edit.setReadOnly(True)
        self.doc_root_edit.setFixedHeight(32)
        doc_root_layout.addWidget(self.doc_root_edit, 5)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedSize(100, 32)
        browse_btn.clicked.connect(self._on_browse_docroot)
        doc_root_layout.addWidget(browse_btn)
        gen_layout.addLayout(doc_root_layout)

        # Data Directory
        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(QLabel("Data Directory:"), 2)
        self.data_dir_edit = QLineEdit(self.config.get_general("data_dir", os.path.join(BASE_DIR, "data")))
        self.data_dir_edit.setReadOnly(True)
        self.data_dir_edit.setFixedHeight(32)
        data_dir_layout.addWidget(self.data_dir_edit, 5)
        browse_data_btn = QPushButton("Browse")
        browse_data_btn.setFixedSize(100, 32)
        browse_data_btn.clicked.connect(self._on_browse_datadir)
        data_dir_layout.addWidget(browse_data_btn)
        gen_layout.addLayout(data_dir_layout)

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

        # Theme Settings
        gen_layout.addSpacing(10)
        gen_layout.addWidget(QLabel("Interface Theme:"))
        theme_bg = QButtonGroup(gen)
        current_theme = self.config.get_theme()
        for i, (label, val) in enumerate([("Dark Mode (Neon)", "dark"), ("Light Mode (Clean)", "light")]):
            rb = QRadioButton(label)
            if current_theme == val: rb.setChecked(True)
            rb.toggled.connect(lambda v, x=val: v and (self.config.set_theme(x), self.rebuild_ui(x)))
            gen_layout.addWidget(rb)
            theme_bg.addButton(rb, i)

        gen_layout.addStretch()
        self.tabs.addTab(gen, "General")

    def _setup_services_tab(self):
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
            row.setStyleSheet(f"border: 1px solid {self.colors['border']}; border-radius: 8px; padding: 12px;")
            h = QHBoxLayout(row)
            h.setContentsMargins(15, 10, 15, 10)
            
            enable_check = QCheckBox(svc.name)
            enable_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            enable_check.setChecked(self.config.get_service_enabled(svc.name))
            enable_check.toggled.connect(lambda v, s=svc.name: (self.config.set_service_enabled(s, v), self.rebuild_ui()))
            h.addWidget(enable_check, 2)

            h.addStretch(1)
            
            if "apache" in svc.name.lower():
                ssl_check = QCheckBox("SSL")
                ssl_check.setFont(QFont("Segoe UI", 10))
                ssl_check.setChecked(self.config.get_service_ssl(svc.name))
                ssl_check.toggled.connect(lambda v, s=svc.name: self.config.set_service_ssl(s, v))
                h.addWidget(ssl_check)
                h.addSpacing(15)

            h.addWidget(QLabel("Port:"), 0)
            port_spin = QSpinBox()
            port_spin.setMinimumWidth(120)
            port_spin.setFixedHeight(36)
            port_spin.setRange(1, 65535)
            port_spin.setValue(svc.current_port)
            port_spin.valueChanged.connect(lambda v, s=svc.name: self.config.set_service_port(s, v))
            h.addWidget(port_spin, 0)

            svc_layout.addWidget(row)

        svc_layout.addStretch()
        svc_scroll.setWidget(svc_content)
        svc_tab_layout = QVBoxLayout(svc_tab)
        svc_tab_layout.addWidget(svc_scroll)
        self.tabs.addTab(svc_tab, "Services")

    def _setup_about_tab(self):
        about = QWidget()
        about_layout = QVBoxLayout(about)
        about_layout.setContentsMargins(40, 40, 40, 40)
        about_layout.setSpacing(10)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "logo.png")
        if os.path.exists(logo_path):
            about_logo = QLabel()
            about_logo.setPixmap(QPixmap(logo_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            about_layout.addWidget(about_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            logo_lbl = QLabel("⚡")
            logo_lbl.setFont(QFont("Segoe UI", 48))
            about_layout.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel(f"{APP_NAME}")
        title_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {self.colors['accent']}; margin-top: 10px;")
        about_layout.addWidget(title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        ver_lbl = QLabel("v4.0 Professional Suite")
        ver_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        ver_lbl.setStyleSheet(f"color: {self.colors['text_dim']};")
        about_layout.addWidget(ver_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        badge = QLabel("STABLE RELEASE")
        badge.setFixedSize(120, 24)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background-color: {self.colors['success']}; color: black; border-radius: 12px; font-weight: bold; font-size: 10px;")
        about_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        
        about_layout.addSpacing(20)
        
        desc_lbl = QLabel("A high-performance, modular development environment for Windows.\nDesigned for speed, beauty, and portability.")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setStyleSheet("line-height: 150%;")
        about_layout.addWidget(desc_lbl)
        
        about_layout.addStretch()
        
        credits_lbl = QLabel("Developed by Breakrule & Pygon Community")
        credits_lbl.setObjectName("DimText")
        credits_lbl.setFont(QFont("Segoe UI", 9))
        about_layout.addWidget(credits_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.tabs.addTab(about, "About")

    def _on_browse_docroot(self):
        p = QFileDialog.getExistingDirectory(self, "Select Document Root")
        if p:
            self.config.set_general("document_root", p)
            self.doc_root_edit.setText(p)

    def _on_browse_datadir(self):
        p = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if p:
            self.config.set_general("data_dir", p)
            self.data_dir_edit.setText(p)
