from services.base import BaseService


class RedisService(BaseService):
    @property
    def name(self) -> str:
        return "Redis Cache"

    @property
    def icon(self) -> str:
        return "RD"

    @property
    def icon_color(self) -> str:
        return "#DC382D"

    @property
    def description(self) -> str:
        return "Redis In-Memory Cache"

    @property
    def executable_path(self) -> str:
        return "redis/redis-server.exe"

    @property
    def default_port(self) -> int:
        return 6379

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart Redis', 'action': 'restart'})
        items.extend([
            {'label': '📄 redis.conf', 'action': 'open_conf'},
            {'label': '💻 Redis CLI', 'action': 'open_console'},
            {'label': '📋 redis.log', 'action': 'open_error_log'},
            {'label': '📁 Open Folder', 'action': 'open_folder'},
        ])
        return items
