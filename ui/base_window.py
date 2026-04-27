from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from ui.theme import THEMES, generate_qss

class BaseWindow(QMainWindow):
    def __init__(self, theme_name="dark"):
        super().__init__()
        self._current_theme = theme_name
        self.colors = THEMES.get(theme_name, THEMES["dark"])
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.refresh_theme(theme_name)

    def refresh_theme(self, theme_name):
        self._current_theme = theme_name
        self.colors = THEMES.get(theme_name, THEMES["dark"])
        
        # Apply to the window
        self.setStyleSheet(generate_qss(self.colors))
        self._rebuild_ui()

    def _rebuild_ui(self):
        # Stop timers if they exist
        if hasattr(self, 'ui_timer'): self.ui_timer.stop()
        if hasattr(self, 'logs_timer'): self.logs_timer.stop()

        # Clear existing layout contents
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # Re-build
        self._build_ui()
        
        # Restart timers
        if hasattr(self, 'ui_timer'): self.ui_timer.start(2000)
        if hasattr(self, 'logs_timer'): self.logs_timer.start(2000)

    def _build_ui(self):
        """To be implemented by subclasses."""
        pass
