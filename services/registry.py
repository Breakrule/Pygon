import os
import sys
import importlib
import inspect
from services.base import BaseService

class ServiceRegistry:
    """
    Scans the 'services' folder and automatically loads any class inheriting from BaseService.
    """
    def __init__(self, bin_dir: str, config_manager=None):
        self.bin_dir = bin_dir
        self.config_manager = config_manager
        self.services = [] # List of instantiated BaseService objects
        self.load_services()

    def load_services(self):
        """Dynamically loads and instantiates all services in the services package."""
        self.services.clear()
        
        if getattr(sys, 'frozen', False):
            # If running as a PyInstaller bundle, use _MEIPASS
            base_path = sys._MEIPASS
        else:
            # If running from source
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        services_dir = os.path.join(base_path, "services")
        
        if not os.path.exists(services_dir):
            print(f"Directory missing: {services_dir}")
            return
            
        # Iterate through all .py files in the services folder
        for filename in os.listdir(services_dir):
            if filename.endswith(".py") and filename not in ["__init__.py", "base.py", "registry.py"]:
                module_name = f"services.{filename[:-3]}"
                
                try:
                    # Import the module dynamically
                    module = importlib.import_module(module_name)
                    
                    # Find any classes inside the module that inherit from BaseService
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseService) and obj is not BaseService:
                            # Instantiate the service and add it to our registry
                            service_instance = obj(bin_dir=self.bin_dir, config_manager=self.config_manager)
                            self.services.append(service_instance)
                            
                except Exception as e:
                    print(f"Failed to load service module {module_name}: {e}")

    def get_all_services(self) -> list:
        return self.services

    def start_all(self):
        for service in self.services:
            service.start()

    def stop_all(self):
        for service in self.services:
            service.stop()
