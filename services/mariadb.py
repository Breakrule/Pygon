import os
import subprocess
import logging
import shutil
from services.base import BaseService

class MariadbService(BaseService):
    @property
    def name(self) -> str:
        return "MariaDB Database"

    @property
    def icon(self) -> str:
        return "🦭"

    @property
    def icon_color(self) -> str:
        return "#003545"

    @property
    def description(self) -> str:
        return "MariaDB Relational Database"

    @property
    def executable_path(self) -> str:
        # MariaDB usually uses mariadbd.exe but falls back to mysqld.exe
        return "bin/mariadbd.exe"

    @property
    def default_port(self) -> int:
        return 3306

    def get_actual_executable_path(self) -> str:
        path = super().get_actual_executable_path()
        if not os.path.exists(path):
            # Fallback to mysqld.exe
            alt_path = path.replace("mariadbd.exe", "mysqld.exe")
            if os.path.exists(alt_path):
                return alt_path
        return path

    def get_start_args(self) -> list:
        base_dir = self._get_base_dir()
        ini_path = os.path.join(base_dir, "my.ini")
        return [f"--defaults-file={ini_path}", "--console"]

    def _get_base_dir(self) -> str:
        exe_path = self.get_actual_executable_path()
        # bin/mariadbd.exe -> bin -> base
        return os.path.dirname(os.path.dirname(exe_path))

    def pre_start(self) -> bool:
        base_dir = self._get_base_dir()
        data_dir = os.path.join(base_dir, "data")
        ini_path = os.path.join(base_dir, "my.ini")

        # 0. Clean up any background processes
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'mariadbd.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(['taskkill', '/F', '/IM', 'mysqld.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass

        # 1. Update/Generate my.ini
        safe_base = base_dir.replace('\\', '/')
        safe_data = data_dir.replace('\\', '/')
        
        config_body = f"""
port={self.current_port}
basedir="{safe_base}"
datadir="{safe_data}"
bind-address=127.0.0.1
max_connections=100
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
"""
        content = f"[mariadb]{config_body}\n[mysqld]{config_body}"
        try:
            with open(ini_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to write MariaDB my.ini: {e}")
            return False

        # 2. Initialize Data Directory
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            logging.info("Initializing MariaDB data directory...")
            init_exe = os.path.join(base_dir, "bin", "mariadb-install-db.exe")
            if not os.path.exists(init_exe):
                init_exe = os.path.join(base_dir, "bin", "mysql_install_db.exe")
            
            if not os.path.exists(init_exe):
                logging.error("MariaDB initialization tool not found.")
                return False

            try:
                # MariaDB initialization is usually fast and stable
                cmd = [init_exe, f"--datadir={data_dir}", f"--basedir={base_dir}", "--force"]
                subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                logging.info("MariaDB data directory initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize MariaDB: {e}")
                return False

        return True

    def start(self) -> bool:
        if not self.pre_start():
            return False
        return super().start()

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart MariaDB', 'action': 'restart'})
        items.extend([
            {'label': '📄 my.ini', 'action': 'open_conf'},
            {'label': '🗄️ Database Manager', 'action': 'open_db_manager'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': '📁 Data Directory', 'action': 'open_folder'},
        ])
        return items
