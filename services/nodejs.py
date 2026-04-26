from services.base import BaseService


class NodejsService(BaseService):
    @property
    def name(self) -> str:
        return "Node.js Service"

    @property
    def icon(self) -> str:
        return "NJ"

    @property
    def icon_color(self) -> str:
        return "#68A063"

    @property
    def description(self) -> str:
        return "Node.js Runtime"

    @property
    def executable_path(self) -> str:
        return "node/node.exe"

    @property
    def default_port(self) -> int:
        return 3000

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart Node', 'action': 'restart'})
        items.extend([
            {'label': '💻 Node Console', 'action': 'open_console'},
            {'label': '📦 npm install', 'action': 'npm_install'},
            {'label': '📁 Open Folder', 'action': 'open_folder'},
        ])
        return items
