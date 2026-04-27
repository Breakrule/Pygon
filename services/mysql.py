import os
import subprocess
import logging
import shutil
from services.base import BaseService

class MysqlService(BaseService):
    @property
    def name(self) -> str:
        return "MySQL Database"

    @property
    def icon(self) -> str:
        return "🐬"

    @property
    def icon_color(self) -> str:
        return "#4479A1"

    @property
    def description(self) -> str:
        return "MySQL Relational Database"

    @property
    def executable_path(self) -> str:
        return "bin/mysqld.exe"

    @property
    def default_port(self) -> int:
        return 3306

    def get_start_args(self) -> list:
        base_dir = self._get_mysql_base()
        ini_path = os.path.join(base_dir, "my.ini")
        return [f"--defaults-file={ini_path}", "--console"]

    def _get_mysql_base(self) -> str:
        """Helper to find the real MySQL base directory (containing share/errmsg.sys)."""
        exe_path = self.get_actual_executable_path()
        # Start from the executable's directory and go up
        current = os.path.dirname(exe_path) # bin/
        
        # Check if we are in a 'bin' folder
        if os.path.basename(current).lower() == 'bin':
            parent = os.path.dirname(current)
            if os.path.exists(os.path.join(parent, "share")):
                return parent
            return parent
        return current

    def pre_start(self) -> bool:
        """Initialize data directory and my.ini if missing."""
        exe_path = self.get_actual_executable_path()
        mysql_base = self._get_mysql_base()
        
        # 0. Clean up any orphaned mysqld processes that might lock files
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'mysqld.exe'], 
                             capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass

        # We put data and my.ini in the mysql_base folder
        data_dir = os.path.join(mysql_base, "data")
        ini_path = os.path.join(mysql_base, "my.ini")

        # 1. Always ensure my.ini is up to date with correct paths and port
        logging.info(f"Generating/Updating my.ini at {ini_path}...")
        safe_base = mysql_base.replace('\\', '/')
        safe_data = data_dir.replace('\\', '/')
        
        # MySQL 8.x vs 9.x compatibility
        auth_plugin = ""
        if self.active_version and self.active_version.startswith("8"):
            auth_plugin = "# Authentication\ndefault_authentication_plugin=mysql_native_password"
        
        content = f"""[mysqld]
port={self.current_port}
basedir="{safe_base}"
datadir="{safe_data}"
bind-address=127.0.0.1
max_connections=100
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES

# InnoDB Paths
innodb_data_home_dir="{safe_data}"
innodb_log_group_home_dir="{safe_data}"
innodb_data_file_path=ibdata1:10M:autoextend

# Windows Compatibility Fixes
innodb_use_native_aio=0
innodb_flush_method=normal
{auth_plugin}

# Path to error messages
lc-messages-dir="{safe_base}/share"
lc-messages=en_US
"""
        try:
            with open(ini_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to write my.ini: {e}")
            return False

        # 2. Ensure data directory exists and is initialized
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            logging.info(f"Initializing MySQL data directory...")
            if os.path.exists(data_dir):
                try: shutil.rmtree(data_dir)
                except: pass
            os.makedirs(data_dir, exist_ok=True)
            
            try:
                # --initialize-insecure creates 'root' user with no password
                cmd = [exe_path, "--no-defaults", "--initialize-insecure", f"--basedir={mysql_base}", f"--datadir={data_dir}"]
                logging.info(f"Running: {' '.join(cmd)}")
                # Use DEVNULL to prevent Windows subprocess buffer deadlocks during heavy init
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                
                if result.returncode != 0:
                    logging.error(f"MySQL Init Failed with return code {result.returncode}. Check data directory for .err logs.")
                    return False
                logging.info("MySQL data directory initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize MySQL: {e}")
                return False

        return True

    def start(self) -> bool:
        if not self.pre_start():
            return False
        return super().start()

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart MySQL', 'action': 'restart'})
        items.extend([
            {'label': '📄 my.ini', 'action': 'open_conf'},
            {'label': '🗄️ Database Manager', 'action': 'open_db_manager'},
            {'label': '💻 MySQL Console', 'action': 'open_console'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': '📁 Data Directory', 'action': 'open_folder'},
        ])
        return items
