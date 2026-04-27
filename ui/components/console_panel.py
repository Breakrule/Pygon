from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

class ConsolePanel(QFrame):
    def __init__(self, parent, colors, on_clear):
        super().__init__(parent)
        self.colors = colors
        self.on_clear = on_clear
        self.tabs = {}
        
        self.setObjectName("SurfacePanel")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self._build_ui()

    def _build_ui(self):
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        for tab_name in ["Console", "Logs", "Errors"]:
            editor = QPlainTextEdit()
            editor.setReadOnly(True)
            editor.setFont(QFont("Consolas", 10))
            
            # Text color based on tab
            color = self.colors["console_text"] if tab_name == "Console" else (self.colors["text_dim"] if tab_name == "Logs" else "#FF6B6B")
            editor.setStyleSheet(f"color: {color};")
            
            self.tab_widget.addTab(editor, tab_name)
            self.tabs[tab_name] = editor
            
        # Footer with Clear button
        footer = QHBoxLayout()
        footer.addStretch()
        
        clear_btn = QPushButton("🗑  Clear")
        clear_btn.setFixedSize(90, 30)
        clear_btn.clicked.connect(self.on_clear)
        footer.addWidget(clear_btn)
        
        self.layout.addLayout(footer)

    def append(self, tab_name, text):
        try:
            editor = self.tabs.get(tab_name)
            if not editor: return
            
            timestamp = QTime.currentTime().toString("HH:mm:ss")
            editor.appendPlainText(f"[{timestamp}] {text}")
            
            # Scroll to bottom
            scrollbar = editor.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except RuntimeError:
            pass # UI is closing

    def clear(self):
        for editor in self.tabs.values():
            editor.clear()
