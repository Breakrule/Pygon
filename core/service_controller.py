import os
import threading
from PyQt6.QtWidgets import QMessageBox
from core.constants import BIN_DIR, WWW_DIR

class ServiceController:
    def __init__(self, registry, downloader, host_manager, config, append_console_cb, run_download_ui_cb):
        self.registry = registry
        self.downloader = downloader
        self.host_manager = host_manager
        self.config = config
        self.append_console = append_console_cb
        self.run_download_ui = run_download_ui_cb
        self.is_running = False

    def toggle_all(self):
        if not self.is_running:
            self.start_all()
        else:
            self.stop_all()

    def start_all(self):
        services = [s for s in self.registry.get_all_services() if self.config.get_service_enabled(s.name)]
        
        for s in services:
            if not s.is_installed:
                dl_key = s.get_base_folder()
                if dl_key in self.downloader.URLS:
                    if QMessageBox.question(None, "Download", f"{s.name} is missing. Download?", 
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                        self.run_download_ui(s.name, dl_key, os.path.join(BIN_DIR, dl_key))
        
        # Scaffolding
        for project_dir in os.listdir(WWW_DIR):
            if os.path.isdir(os.path.join(WWW_DIR, project_dir)):
                self.host_manager.generate_vhost_config(project_dir)
                self.host_manager.add_host_entry(f"{project_dir}.test")

        for s in services:
            if s.is_installed:
                s.start()
        
        self.is_running = True
        self.append_console("Console", "[START ALL] All services started.")

    def stop_all(self):
        self.registry.stop_all()
        self.is_running = False
        self.append_console("Console", "[STOP ALL] All services stopped.")

    def toggle_single(self, service):
        if service.is_running():
            service.stop()
            self.append_console("Console", f"[STOP] {service.name}")
        else:
            if not service.is_installed:
                dl_key = service.get_base_folder()
                if dl_key in self.downloader.URLS:
                    if QMessageBox.question(None, "Download", f"{service.name} is missing. Download?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                        if self.run_download_ui(service.name, dl_key, os.path.join(BIN_DIR, dl_key)):
                            service.start()
                            self.append_console("Console", f"[START] {service.name}")
                return
            service.start()
            self.append_console("Console", f"[START] {service.name}")

    def restart_service(self, service):
        self.append_console("Console", f"[RESTART] {service.name}")
        service.stop()
        threading.Timer(0.5, service.start).start()
