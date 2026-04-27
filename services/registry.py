import os
import sys
import importlib
import importlib.util
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
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # 1. Load Internal Services
        services_dir = os.path.join(base_path, "services")
        self._scan_and_load(services_dir, "services")
        
        # 2. Load External Plugins
        # Plugins always sit next to the main entry point (not inside _MEIPASS if frozen)
        if getattr(sys, 'frozen', False):
            # In frozen app, plugins are in the same folder as the EXE
            plugins_dir = os.path.join(os.path.dirname(sys.executable), "plugins")
        else:
            plugins_dir = os.path.join(base_path, "plugins")
            
        if not os.path.exists(plugins_dir):
            try: os.makedirs(plugins_dir, exist_ok=True)
            except: pass
            
        self._scan_and_load(plugins_dir, "plugins", external=True)

    def _scan_and_load(self, directory: str, package_prefix: str, external=False):
        if not os.path.exists(directory): return
        
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename not in ["__init__.py", "base.py", "registry.py"]:
                module_path = os.path.join(directory, filename)
                module_name = f"{package_prefix}.{filename[:-3]}"
                
                try:
                    if not external:
                        # Use standard import for internal services
                        module = importlib.import_module(module_name)
                    else:
                        # Use file location for external plugins
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        # Add the directory to sys.path so plugins can import services.base
                        if directory not in sys.path:
                            sys.path.insert(0, directory)
                        spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseService) and obj is not BaseService:
                            # Avoid duplicate instances of the same class
                            if any(isinstance(s, obj) for s in self.services): continue
                            
                            service_instance = obj(bin_dir=self.bin_dir, config_manager=self.config_manager)
                            self.services.append(service_instance)
                            
                except Exception as e:
                    print(f"Failed to load {package_prefix} module {module_name}: {e}")

    def get_all_services(self) -> list:
        return self.services

    def start_all(self):
        for service in self.services:
            service.start()

    def stop_all(self):
        for service in self.services:
            service.stop()
