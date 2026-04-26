from services.base import BaseService


class ApacheService(BaseService):
    @property
    def name(self) -> str:
        return "Apache Web Server"

    @property
    def icon(self) -> str:
        return "AP"

    @property
    def icon_color(self) -> str:
        return "#E45735"

    @property
    def description(self) -> str:
        return "Apache HTTP Server"

    @property
    def executable_path(self) -> str:
        return "apache/bin/httpd.exe"

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
        """Patch PHP config before starting."""
        self._patch_php_config()
        return super().start()

    def _patch_php_config(self):
        """Patches httpd.conf to load the correct PHP module DLL."""
        if not self.config: return
        
        php_ver = self.config.get_service_version("PHP Version")
        if not php_ver: return
        
        import os
        bin_dir = os.path.dirname(os.path.dirname(self.get_actual_executable_path()))
        conf_path = os.path.join(bin_dir, "conf", "httpd.conf")
        
        if not os.path.exists(conf_path): return
        
        # Determine PHP module path
        php_dir = os.path.join(os.path.dirname(bin_dir), "php", php_ver)
        # Look for php8apache2_4.dll or similar
        php_dll = ""
        for f in os.listdir(php_dir):
            if f.startswith("php") and f.endswith("apache2_4.dll"):
                php_dll = os.path.join(php_dir, f).replace("\\", "/")
                break
        
        if not php_dll: return
        
        try:
            with open(conf_path, "r") as f:
                content = f.read()
            
            import re
            # Update LoadModule
            module_line = f'LoadModule php_module "{php_dll}"'
            if 'LoadModule php_module' in content:
                content = re.sub(r'LoadModule php_module ".*"', module_line, content)
            else:
                content += f"\n{module_line}\nAddHandler application/x-httpd-php .php\nPHPIniDir \"{php_dir.replace('\\', '/')}\"\n"
            
            with open(conf_path, "w") as f:
                f.write(content)
        except Exception:
            pass
