import os
from services.base import BaseService


class NodejsService(BaseService):
    @property
    def name(self) -> str:
        return "Node.js Service"

    @property
    def icon(self) -> str:
        return "⬡"

    @property
    def icon_color(self) -> str:
        return "#68A063"

    @property
    def description(self) -> str:
        return "Node.js Runtime"

    @property
    def executable_path(self) -> str:
        return "node.exe"

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
            {'label': '📂 Set Project Path', 'action': 'set_node_project'},
        ])
        return items

    def get_version_display(self, version: str) -> str:
        """Parses version from folder name (e.g., 'node-v20.20.0-win-x64' -> 'v20')."""
        if not version: return "Default"
        import re
        match = re.search(r'node-v(\d+)', version)
        if match:
            return "v" + match.group(1)
        return version

    def get_actual_executable_path(self) -> str:
        """Resolves node.exe inside version subfolders."""
        base_exe = "node.exe"
        if self.active_version:
            path = os.path.join(self.bin_dir, "node", self.active_version, base_exe)
            if os.path.exists(path):
                return path
        return super().get_actual_executable_path()

    def get_working_dir(self) -> str:
        """Returns the user-selected project path if set, otherwise default."""
        if self.config:
            project_path = self.config.get_general("node_project_path")
            if project_path and os.path.exists(project_path):
                return project_path
        return super().get_working_dir()

    def get_start_args(self) -> list:
        """If a project is set, returns npm args."""
        working_dir = self.get_working_dir()
        if os.path.exists(os.path.join(working_dir, "package.json")):
            npm_path = os.path.join(os.path.dirname(self.get_actual_executable_path()), "npm.cmd")
            if os.path.exists(npm_path):
                return ["/c", npm_path, "run", "dev"]
            return ["/c", "npm", "run", "dev"]
        return []

    def get_command_line(self) -> list:
        """If a project is set, run 'npm run dev' via cmd /c."""
        args = self.get_start_args()
        if args and args[0] == "/c":
            return ["cmd"] + args
        return [self.get_actual_executable_path()] + args
