import pystray
from PIL import Image, ImageDraw
import threading
import logging

class TrayManager:
    def __init__(self, app_instance):
        """
        :param app_instance: Reference to the main PygonApp window.
        """
        self.app = app_instance
        self.icon = None
        
    def create_image(self):
        """Generate a simple default icon (a blue circle for Pygon)."""
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        d = ImageDraw.Draw(image)
        d.ellipse((8, 8, 56, 56), fill=(47, 165, 114)) # Pygon Green
        return image

    def start_tray(self):
        """Runs the tray icon in a separate thread so it doesn't block the GUI."""
        def setup(icon):
            self.icon = icon
            
        # Build dynamic menu items based on registered services
        menu_items = [
            pystray.MenuItem('Show Dashboard', self.on_show),
            pystray.Menu.SEPARATOR
        ]
        
        # Add a sub-menu or just info for each service
        for service in self.app.registry.get_all_services():
            # For now, just listing them. In the future we could add individual start/stop here.
            menu_items.append(pystray.MenuItem(f'{service.name} (Port {service.default_port})', lambda *args: None, enabled=False))
            
        menu_items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Start All', self.on_start_all),
            pystray.MenuItem('Stop All', self.on_stop_all),
            pystray.MenuItem('Open Web Root', self.on_open_www),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit Pygon', self.on_quit)
        ])
        
        menu = pystray.Menu(*menu_items)
        
        icon = pystray.Icon("Pygon", self.create_image(), "Pygon Local Server", menu)
        threading.Thread(target=icon.run, args=(setup,), daemon=True).start()

    def on_show(self, icon, item):
        self.app.deiconify() # Restore the window
        self.app.lift()

    def on_start_all(self, icon, item):
        self.app.start_services()

    def on_stop_all(self, icon, item):
        self.app.stop_services()
        
    def on_open_www(self, icon, item):
        self.app.open_document_root()

    def on_quit(self, icon, item):
        # Route the quit hook safely to the main Tkinter thread
        self.app.after(0, self.app.exit_app)
