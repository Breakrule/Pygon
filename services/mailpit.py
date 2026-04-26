from services.base import BaseService


class MailpitService(BaseService):
    @property
    def name(self) -> str:
        return "Mail Server (Mailpit)"

    @property
    def icon(self) -> str:
        return "MP"

    @property
    def icon_color(self) -> str:
        return "#00B4D8"

    @property
    def description(self) -> str:
        return "Mailpit SMTP Testing Server"

    @property
    def executable_path(self) -> str:
        return "mailpit/mailpit.exe"

    @property
    def default_port(self) -> int:
        return 1025

    def get_menu_items(self) -> list:
        items = []
        if self.is_running():
            items.append({'label': '🔄 Restart Mailpit', 'action': 'restart'})
        items.extend([
            {'label': '🌐 Open Mailpit UI', 'action': 'open_web_ui'},
            {'label': '📄 Conf File', 'action': 'open_conf'},
            {'label': '📁 Open Folder', 'action': 'open_folder'},
        ])
        return items
