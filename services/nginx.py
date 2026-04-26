from services.base import BaseService


class NginxService(BaseService):
    @property
    def name(self) -> str:
        return "Nginx Web Server"

    @property
    def icon(self) -> str:
        return "NX"

    @property
    def icon_color(self) -> str:
        return "#009639"

    @property
    def description(self) -> str:
        return "Nginx HTTP & Reverse Proxy"

    @property
    def executable_path(self) -> str:
        return "nginx/nginx.exe"

    @property
    def default_port(self) -> int:
        return 8080

    def get_menu_items(self) -> list:
        items = [
            {'label': '📁 Web Root', 'action': 'open_docroot'},
        ]
        if self.is_running():
            items.append({'label': '🔄 Restart Nginx', 'action': 'restart'})
        items.extend([
            {'label': '📄 nginx.conf', 'action': 'open_conf'},
            {'label': '📂 vhosts', 'action': 'open_vhosts'},
            {'label': '🔒 SSL', 'action': 'ssl_manage'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': '📋 access.log', 'action': 'open_access_log'},
        ])
        return items
