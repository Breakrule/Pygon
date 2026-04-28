from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from ui.components.console_panel import ConsolePanel

class ConsoleWindow(QDialog):
    def __init__(self, parent, colors, on_clear):
        super().__init__(parent)
        self.setWindowTitle("Console & Logs")
        self.resize(800, 500)
        
        # Make it a proper window that doesn't block the main one
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Use existing ConsolePanel
        self.console_panel = ConsolePanel(self, colors, on_clear)
        self.layout.addWidget(self.console_panel)
        
    def append(self, tab, text):
        """Proxy to ConsolePanel.append"""
        self.console_panel.append(tab, text)
        
    def clear(self):
        """Proxy to ConsolePanel.clear"""
        self.console_panel.clear()

    def closeEvent(self, event):
        """Hide instead of closing to preserve logs if needed, 
        but QDialog handles visibility fine with .show() / .hide()"""
        super().closeEvent(event)
