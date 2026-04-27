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

    @staticmethod
    def get_process_metrics(pid: int):
        """Returns (cpu_usage, memory_bytes) for a process and all its children."""
        try:
            parent = psutil.Process(pid)
            processes = [parent] + parent.children(recursive=True)
            
            total_cpu = 0.0
            total_mem = 0
            
            for p in processes:
                try:
                    # Note: cpu_percent(interval=None) is better for recurring polling
                    total_cpu += p.cpu_percent()
                    total_mem += p.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return total_cpu, total_mem
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return 0.0, 0

    @staticmethod
    def launch_pygon_shell(registry):
        """Launches a shell with binaries of active services in the PATH."""
        import subprocess
        env = os.environ.copy()
        paths = []
        
        for svc in registry.get_all_services():
            exe = svc.get_actual_executable_path()
            if os.path.exists(exe):
                bin_dir = os.path.abspath(os.path.dirname(exe))
                if bin_dir not in paths:
                    paths.append(bin_dir)
        
        if paths:
            new_path = os.pathsep.join(paths) + os.pathsep + env.get("PATH", "")
            env["PATH"] = new_path
        
        subprocess.Popen(["cmd.exe", "/K", "echo Pygon Dev Shell Initialized! & echo Active paths: " + str(paths) + " & prompt Pygon$G "], 
                        env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)
