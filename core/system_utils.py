import sys
import os
import psutil
from core.constants import BASE_DIR

class SystemUtils:
    @staticmethod
    def apply_startup_setting(enabled: bool):
        """Add/remove Pygon from Windows startup registry."""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_SET_VALUE)
            if enabled:
                exe = sys.executable
                if getattr(sys, 'frozen', False):
                    cmd = f'"{exe}"'
                else:
                    # Pointing to the main pygon.py in the root
                    script_path = os.path.join(BASE_DIR, "pygon.py")
                    cmd = f'"{exe}" "{script_path}"'
                winreg.SetValueEx(key, "Pygon", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "Pygon")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    @staticmethod
    def get_system_metrics():
        """Returns CPU, RAM, and DISK usage percentages."""
        try:
            cpu = psutil.cpu_percent() / 100.0
            mem = psutil.virtual_memory().percent / 100.0
            disk = psutil.disk_usage(BASE_DIR).percent / 100.0
            return cpu, mem, disk
        except:
            return 0.0, 0.0, 0.0
