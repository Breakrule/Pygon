import os
import re
import logging
from services.base import BaseService


class ApacheService(BaseService):
    @property
    def name(self) -> str:
        return "Apache Web Server"

    @property
    def icon(self) -> str:
        return "🌐"

    @property
    def icon_color(self) -> str:
        return "#E45735"

    @property
    def description(self) -> str:
        return "Apache HTTP Server"

    @property
    def executable_path(self) -> str:
        return "bin/httpd.exe"

    @property
    def default_port(self) -> int:
        return 80

    def get_menu_items(self) -> list:
        items = [
            {'label': '📁 public_html', 'action': 'open_docroot'},
        ]
        if self.is_running():
            items.append({'label': '🔄 Restart Apache', 'action': 'restart'})
        items.extend([
            {'label': '📄 Conf File', 'action': 'open_conf'},
            {'label': '🐘 PHP', 'action': None, 'children': [
                {'label': 'PHP Extensions', 'action': 'php_extensions'},
                {'label': 'PHP Conf', 'action': 'php_conf'},
            ]},
            {'label': '🔒 SSL', 'action': 'ssl_manage'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': '🐘 PHP Version', 'action': 'php_version'},
        ])
        return items

    def start(self) -> bool:
        """Prepare config before starting."""
        self._prepare_config()
        return super().start()

    def _prepare_config(self):
        """Patches httpd.conf for ServerRoot and PHP module paths."""
        if not self.config: return
        
        # 1. Paths
        exe_path = self.get_actual_executable_path()
        apache_version_dir = os.path.dirname(os.path.dirname(exe_path))
        apache_type_dir = os.path.dirname(apache_version_dir)
        bin_root = os.path.dirname(apache_type_dir)
        
        conf_path = os.path.join(apache_version_dir, "conf", "httpd.conf")
        if not os.path.exists(conf_path): return
        
        try:
            with open(conf_path, "r") as f:
                content = f.read()
            
            # 2. Patch ServerRoot (SRVROOT)
            safe_root = apache_version_dir.replace("\\", "/")
            # Match 'Define SRVROOT "..."' or 'ServerRoot "..."'
            if 'Define SRVROOT' in content:
                content = re.sub(r'Define SRVROOT ".*"', f'Define SRVROOT "{safe_root}"', content)
            elif 'ServerRoot' in content:
                content = re.sub(r'ServerRoot ".*"', f'ServerRoot "{safe_root}"', content)

            # 3. Patch PHP (if version selected)
            php_ver = self.config.get_service_version("PHP Version")
            if php_ver:
                php_dir = os.path.join(bin_root, "php", php_ver)
                php_dll = ""
                if os.path.exists(php_dir):
                    for f in os.listdir(php_dir):
                        if f.startswith("php") and f.endswith("apache2_4.dll"):
                            php_dll = os.path.join(php_dir, f).replace("\\", "/")
                            break
                
                if php_dll:
                    module_line = f'LoadModule php_module "{php_dll}"'
                    if 'LoadModule php_module' in content:
                        content = re.sub(r'LoadModule php_module ".*"', module_line, content)
                    else:
                        content += f"\n{module_line}\nAddHandler application/x-httpd-php .php\nPHPIniDir \"{php_dir.replace('\\', '/')}\"\n"
            
            with os.fdopen(os.open(conf_path, os.O_WRONLY | os.O_TRUNC | os.O_CREAT), 'w') as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to prepare Apache config: {e}")
