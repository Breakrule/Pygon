import subprocess
import os
import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ServiceManager:
    """
    Manages starting, stopping, and monitoring of background services (Nginx, PHP, MySQL, etc.)
    """
    
    def __init__(self, bin_dir: str):
        """
        :param bin_dir: The absolute path to the directory containing service executables.
        """
        self.bin_dir = bin_dir
        self.processes = {} # map service name to subprocess.Popen object

    def start_service(self, name: str, executable: str, args: list = None, cwd: str = None) -> bool:
        """
        Starts a service.
        :param name: Friendly name (e.g., 'nginx')
        :param executable: Path relative to bin_dir or absolute path (e.g., 'nginx/nginx.exe')
        :param args: List of arguments
        :param cwd: Working directory for the process
        """
        if self.is_service_running(name):
            logging.info(f"Service {name} is already running.")
            return True

        exe_path = os.path.join(self.bin_dir, executable)
        if not os.path.exists(exe_path):
            logging.error(f"Executable not found: {exe_path}")
            return False

        if args is None:
            args = []

        try:
            work_dir = cwd if cwd else os.path.dirname(exe_path)
            # Create a detached process (on Windows, CREATE_NO_WINDOW prevents a console window)
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            cmd = [exe_path] + args
            process = subprocess.Popen(
                cmd,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
            self.processes[name] = process
            logging.info(f"Started service: {name} (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Failed to start service {name}: {e}")
            return False

    def stop_service(self, name: str) -> bool:
        """Stops a tracked service."""
        if name not in self.processes:
            logging.warning(f"Service {name} is not being tracked by ServiceManager.")
            return False
            
        process = self.processes[name]
        try:
            # Simple kill for now. More complex services might need graceful shutdown args.
            process.terminate()
            process.wait(timeout=5)
            del self.processes[name]
            logging.info(f"Stopped service: {name}")
            return True
        except subprocess.TimeoutExpired:
            logging.warning(f"Service {name} did not terminate gracefully. Killing...")
            process.kill()
            del self.processes[name]
            return True
        except Exception as e:
            logging.error(f"Error stopping service {name}: {e}")
            return False

    def is_service_running(self, name: str) -> bool:
        """Checks if a tracked service is still running."""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        return process.poll() is None # If poll() is None, the process is still running

    def stop_all(self):
        """Stops all tracked services."""
        services = list(self.processes.keys())
        for service in services:
            self.stop_service(service)
