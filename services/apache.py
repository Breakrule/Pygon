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
