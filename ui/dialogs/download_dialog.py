import os
import threading
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DownloadDialog(QDialog):
    def __init__(self, parent, downloader, name, key, target):
        super().__init__(parent)
        self.downloader = downloader
        self.name = name
        self.key = key
        self.target = target
        self.success = False
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Download")
        self.setFixedSize(400, 180)
        layout = QVBoxLayout(self)
        
        lbl = QLabel(f"Downloading {self.name}...")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        layout.addWidget(self.bar)
        
    def exec(self):
        def run():
            self.success = self.downloader.download_and_extract(self.key, self.target)
            self.accept()
            
        threading.Thread(target=run, daemon=True).start()
        return super().exec()
