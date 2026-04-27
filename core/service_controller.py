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
        
        # Generate initial dashboard
        from core.dashboard_generator import DashboardGenerator
        DashboardGenerator(self.www_dir).generate()

    def toggle_all(self):
        if not self.is_running:
            self.start_all()
        else:
            self.stop_all()

    @property
    def www_dir(self):
        return self.config.get_general("document_root", WWW_DIR)

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
        from core.dashboard_generator import DashboardGenerator
        dg = DashboardGenerator(self.www_dir)
        
        if os.path.exists(self.www_dir):
            for project_dir in os.listdir(self.www_dir):
                if os.path.isdir(os.path.join(self.www_dir, project_dir)):
                    self.host_manager.generate_vhost_config(project_dir, self.config)
                    self.host_manager.add_host_entry(f"{project_dir}.pygon")
        
        dg.generate()

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
            
            # Scaffolding & Dashboard update on single start
            if "apache" in service.name.lower() or "nginx" in service.name.lower():
                from core.dashboard_generator import DashboardGenerator
                DashboardGenerator(self.www_dir).generate()
                if os.path.exists(self.www_dir):
                    for project_dir in os.listdir(self.www_dir):
                        if os.path.isdir(os.path.join(self.www_dir, project_dir)):
                            self.host_manager.generate_vhost_config(project_dir, self.config)

            service.start()
            self.append_console("Console", f"[START] {service.name}")

    def restart_service(self, service):
        self.append_console("Console", f"[RESTART] {service.name}")
        service.stop()
        threading.Timer(0.5, service.start).start()
