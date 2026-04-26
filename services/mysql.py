from services.base import BaseService


class MysqlService(BaseService):
    @property
    def name(self) -> str:
        return "MySQL Database"

    @property
    def icon(self) -> str:
        return "MY"

    @property
    def icon_color(self) -> str:
        return "#4479A1"

    @property
    def description(self) -> str:
        return "MySQL Relational Database"

    @property
    def executable_path(self) -> str:
        return "mysql/bin/mysqld.exe"

    @property
    def default_port(self) -> int:
        return 3306

    def get_start_args(self) -> list:
        return ["--console"]

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart MySQL', 'action': 'restart'})
        items.extend([
            {'label': '📄 my.ini', 'action': 'open_conf'},
            {'label': '💻 MySQL Console', 'action': 'open_console'},
            {'label': '📋 error.log', 'action': 'open_error_log'},
            {'label': '📁 Data Directory', 'action': 'open_folder'},
        ])
        return items
