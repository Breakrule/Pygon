from abc import ABC, abstractmethod
import os
import subprocess
import logging
import threading
import collections


class BaseService(ABC):
    """
    Abstract Base Class for all Pygon Services (Servers, Databases, etc).
    """

    def __init__(self, bin_dir: str, config_manager=None):
        self.bin_dir = bin_dir
        self.config = config_manager
        self.process = None
        # Log buffer for console output capture (thread-safe deque)
        self._log_buffer = collections.deque(maxlen=500)
        self._error_buffer = collections.deque(maxlen=200)
        self._reader_threads = []

    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the service (e.g., 'Nginx Web Server')"""
        pass

    @property
    @abstractmethod
    def executable_path(self) -> str:
        """The relative path to the executable within bin_dir (e.g., 'nginx/nginx.exe')"""
        pass

    @property
    @abstractmethod
    def default_port(self) -> int:
        """The primary port this service listens on."""
        pass

    @property
    def icon(self) -> str:
        """Short text label for UI icon badge. Override in subclass."""
        return "SV"

    @property
    def icon_color(self) -> str:
        """Color for the icon badge. Override in subclass."""
        return "#6B7280"

    @property
    def description(self) -> str:
        """Short description for UI display. Override in subclass."""
        return self.name

    @property
    def current_port(self) -> int:
        """Returns the custom port if set, otherwise the default port."""
        if self.config:
            custom = self.config.get_service_port(self.name)
            if custom is not None:
                return custom
        return self.default_port

    def set_custom_port(self, port: int):
        """Saves a custom port override."""
        if self.config:
            self.config.set_service_port(self.name, port)

    def get_menu_items(self) -> list:
        """Returns a list of context menu items for this service.
        Each item is a dict: {'label': str, 'action': str, 'children': [...]}
        'action' is a string key that the UI will map to a callback.
        'children' is optional for submenus.
        Override in subclasses to provide service-specific menus.
        """
        items = []
        if self.is_running():
            items.append({'label': f'Restart {self.name.split()[0]}', 'action': 'restart'})
        items.append({'label': 'Open Folder', 'action': 'open_folder'})
        return items

    @property
    def is_installed(self) -> bool:
        """Checks if the executable exists in the expected location."""
        # Must check for the actual executable file
        exe = self.get_actual_executable_path()
        if os.path.isfile(exe):
            return True
        return False

    def get_base_folder(self) -> str:
        """Gets the root folder for this service type (e.g. 'nginx'). Extracted from executable_path."""
        return self.executable_path.split("/")[0] if "/" in self.executable_path else self.executable_path.split("\\")[0]

    # Directories that are NOT version folders (internal service structure)
    _EXCLUDE_DIRS = {'bin', 'conf', 'data', 'docs', 'etc', 'html', 'include',
                     'lib', 'lib64', 'libexec', 'logs', 'man', 'modules',
                     'sbin', 'share', 'ssl', 'temp', 'tmp', 'var', 'vhosts',
                     'scripts', 'support', '__pycache__'}

    def get_available_versions(self) -> list:
        """Scans the bin/service_name/ directory for subfolders that look like versions."""
        base_folder = os.path.join(self.bin_dir, self.get_base_folder())
        versions = []

        if os.path.exists(base_folder):
            for item in os.listdir(base_folder):
                item_path = os.path.join(base_folder, item)
                # Must be a directory, not an excluded name, and should look like a version (contains a digit)
                if (os.path.isdir(item_path)
                        and item.lower() not in self._EXCLUDE_DIRS
                        and any(c.isdigit() for c in item)):
                    versions.append(item)

        return sorted(versions, reverse=True)

    @property
    def active_version(self) -> str:
        """Gets the currently selected version from config, or defaults to the first available."""
        saved_ver = self.config.get_service_version(self.name) if self.config else None
        avail = self.get_available_versions()
        
        if saved_ver and saved_ver in avail:
            return saved_ver
        if avail:
            return avail[0]
        return ""
        
    def set_active_version(self, version: str):
        """Saves the selected version."""
        if self.config:
            self.config.set_service_version(self.name, version)
            
    def get_actual_executable_path(self) -> str:
        """Resolves the real executable path considering versions."""
        std_path = os.path.join(self.bin_dir, self.executable_path)
        if os.path.isfile(std_path) and not self.active_version:
            return std_path
            
        exe_name = os.path.basename(self.executable_path)
        base = self.get_base_folder()
        version_folder = self.active_version
        
        if version_folder:
            vers_path = os.path.join(self.bin_dir, base, version_folder, exe_name)
            if os.path.exists(vers_path):
                return vers_path
                
        return std_path

    def get_start_args(self) -> list:
        """Override to provide custom startup arguments."""
        return []

    def get_working_dir(self) -> str:
        """Override to provide a specific working directory."""
        return os.path.dirname(self.get_actual_executable_path())

    def _stream_reader(self, stream, buffer):
        """Background thread to read from a subprocess stream into a buffer."""
        try:
            for line in iter(stream.readline, b''):
                try:
                    text = line.decode('utf-8', errors='replace').rstrip('\r\n')
                    if text:
                        buffer.append(text)
                except Exception:
                    pass
        except Exception:
            pass

    def start(self) -> bool:
        """Starts the service subprocess."""
        if not self.is_installed:
            logging.error(f"{self.name} is not installed.")
            return False

        if self.is_running():
            logging.info(f"{self.name} is already running.")
            return True

        exe_path = self.get_actual_executable_path()

        if not os.path.isfile(exe_path):
            logging.error(f"{self.name}: executable not found at {exe_path}")
            self._error_buffer.append(f"Executable not found: {exe_path}")
            return False
        
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            cmd = [exe_path] + self.get_start_args()
            self.process = subprocess.Popen(
                cmd,
                cwd=self.get_working_dir(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )

            # Start reader threads to capture stdout/stderr
            stdout_thread = threading.Thread(
                target=self._stream_reader,
                args=(self.process.stdout, self._log_buffer),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._stream_reader,
                args=(self.process.stderr, self._error_buffer),
                daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()
            self._reader_threads = [stdout_thread, stderr_thread]

            logging.info(f"Started {self.name} (PID: {self.process.pid})")
            return True
        except Exception as e:
            logging.error(f"Failed to start {self.name}: {e}")
            self._error_buffer.append(f"Failed to start: {e}")
            return False

    def stop(self) -> bool:
        """Stops the service subprocess."""
        if not self.process:
            return True
            
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            self._reader_threads.clear()
            logging.info(f"Stopped {self.name}")
            return True
        except subprocess.TimeoutExpired:
            logging.warning(f"{self.name} did not terminate gracefully. Killing...")
            self.process.kill()
            self.process = None
            self._reader_threads.clear()
            return True
        except Exception as e:
            logging.error(f"Error stopping {self.name}: {e}")
            return False

    def is_running(self) -> bool:
        """Checks if the subprocess is currently active."""
        if not self.process:
            return False
        return self.process.poll() is None

    def get_logs(self) -> list:
        """Returns recent log lines from stdout."""
        return list(self._log_buffer)

    def get_errors(self) -> list:
        """Returns recent error lines from stderr."""
        return list(self._error_buffer)

    def clear_logs(self):
        """Clears both log and error buffers."""
        self._log_buffer.clear()
        self._error_buffer.clear()
