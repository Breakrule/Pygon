from services.base import BaseService


class PhpService(BaseService):
    @property
    def name(self) -> str:
        return "PHP Version"

    @property
    def icon(self) -> str:
        return "PP"

    @property
    def icon_color(self) -> str:
        return "#777BB4"

    @property
    def description(self) -> str:
        return "PHP-CGI FastCGI Processor"

    @property
    def executable_path(self) -> str:
        return "php/php-cgi.exe"

    @property
    def default_port(self) -> int:
        return 9000

    def get_start_args(self) -> list:
        return ["-b", f"127.0.0.1:{self.current_port}"]

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart PHP', 'action': 'restart'})
        items.extend([
            {'label': '📄 php.ini', 'action': 'open_conf'},
            {'label': '🧩 PHP Extensions', 'action': 'php_extensions'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': 'ℹ️ phpinfo()', 'action': 'phpinfo'},
            {'label': '📁 Open Folder', 'action': 'open_folder'},
        ])
        return items
