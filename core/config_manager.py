import os
import yaml


class ConfigManager:
    """
    Manages loading and saving user preferences to a config.yaml file.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.settings = self.load_config()

    def load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {"versions": {}, "ports": {}, "autostart": {}, "general": {}, "services_enabled": {}, "services_ssl": {}}

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f) or {}
                for key in ("versions", "ports", "autostart", "general", "services_enabled", "services_ssl"):
                    data.setdefault(key, {})
                return data
        except Exception:
            return {"versions": {}, "ports": {}, "autostart": {}, "general": {}, "services_enabled": {}, "services_ssl": {}}

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    # ── Service Version ──────────────────────────────────────────────
    def get_service_version(self, service_name: str) -> str:
        """Returns the saved version for a service, or None."""
        return self.settings.setdefault("versions", {}).get(service_name)

    def set_service_version(self, service_name: str, version: str):
        """Saves the selected version for a service."""
        self.settings.setdefault("versions", {})[service_name] = version
        self.save_config()

    # ── Service Port ─────────────────────────────────────────────────
    def get_service_port(self, service_name: str) -> int:
        """Returns the saved custom port for a service, or None."""
        return self.settings.setdefault("ports", {}).get(service_name)

    def set_service_port(self, service_name: str, port: int):
        """Saves a custom port for a service."""
        self.settings.setdefault("ports", {})[service_name] = port
        self.save_config()

    # ── Service Autostart (Start All checkbox) ───────────────────────
    def get_service_autostart(self, service_name: str) -> bool:
        """Returns the saved autostart check state for a service. True by default."""
        return self.settings.setdefault("autostart", {}).get(service_name, True)

    def set_service_autostart(self, service_name: str, autostart: bool):
        """Saves the autostart check state for a service."""
        self.settings.setdefault("autostart", {})[service_name] = autostart
        self.save_config()

    # ── Service Enabled (show/hide in main UI) ───────────────────────
    def get_service_enabled(self, service_name: str) -> bool:
        """Returns whether a service is enabled (shown in main UI). True by default."""
        return self.settings.setdefault("services_enabled", {}).get(service_name, True)

    def set_service_enabled(self, service_name: str, enabled: bool):
        """Saves whether a service is enabled."""
        self.settings.setdefault("services_enabled", {})[service_name] = enabled
        self.save_config()

    # ── Service SSL ──────────────────────────────────────────────────
    def get_service_ssl(self, service_name: str) -> bool:
        """Returns whether SSL is enabled for a service. False by default."""
        return self.settings.setdefault("services_ssl", {}).get(service_name, False)

    def set_service_ssl(self, service_name: str, ssl: bool):
        """Saves SSL state for a service."""
        self.settings.setdefault("services_ssl", {})[service_name] = ssl
        self.save_config()

    # ── General Settings ─────────────────────────────────────────────
    def get_general(self, key: str, default=None):
        """Returns a general setting value."""
        return self.settings.setdefault("general", {}).get(key, default)

    def set_general(self, key: str, value):
        """Saves a general setting value."""
        self.settings.setdefault("general", {})[key] = value
        self.save_config()

    # ── Theme ────────────────────────────────────────────────────────
    def get_theme(self) -> str:
        """Returns the saved theme ('dark' or 'light'). Defaults to 'dark'."""
        return self.get_general("theme", "dark")

    def set_theme(self, theme: str):
        """Saves the theme preference."""
        self.set_general("theme", theme)

    # ── Close Behavior ───────────────────────────────────────────────
    def get_close_behavior(self) -> str:
        """Returns the saved close behavior ('tray', 'exit', or 'ask'). Defaults to 'ask'."""
        return self.get_general("close_behavior", "ask")

    def set_close_behavior(self, behavior: str):
        """Saves the close behavior preference."""
        self.set_general("close_behavior", behavior)
