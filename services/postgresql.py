from services.base import BaseService


class PostgresqlService(BaseService):
    @property
    def name(self) -> str:
        return "PostgreSQL Database"

    @property
    def icon(self) -> str:
        return "PG"

    @property
    def icon_color(self) -> str:
        return "#336791"

    @property
    def description(self) -> str:
        return "PostgreSQL Relational Database"

    @property
    def executable_path(self) -> str:
        return "pgsql/bin/pg_ctl.exe"

    @property
    def default_port(self) -> int:
        return 5432

    def get_start_args(self) -> list:
        return ["start", "-D", "data"]

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart PostgreSQL', 'action': 'restart'})
        items.extend([
            {'label': '📄 postgresql.conf', 'action': 'open_conf'},
            {'label': '💻 psql Console', 'action': 'open_console'},
            {'label': '📋 pg_log', 'action': 'open_error_log'},
            {'label': '📁 Data Directory', 'action': 'open_folder'},
        ])
        return items
