import os
import ctypes
import logging
from jinja2 import Environment, FileSystemLoader, Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HostManager:
    HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"
    
    def __init__(self, vhost_conf_dir: str, document_root: str):
        self.vhost_conf_dir = vhost_conf_dir
        self.document_root = document_root
        
        # Apache VirtualHost Template
        self.template_str = """
<VirtualHost *:80>
    ServerName {{ project_name }}.test
    DocumentRoot "{{ project_path }}"
    <Directory "{{ project_path }}">
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"""

    def is_admin(self) -> bool:
        """Check if running as administrator (required to rewrite hosts)."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def add_host_entry(self, domain: str, ip: str = "127.0.0.1") -> bool:
        """Add a domain to the Windows hosts file."""
        if not self.is_admin():
            logging.error("Administrator privileges required to edit hosts file.")
            return False
            
        entry = f"{ip} {domain}"
        try:
            with open(self.HOSTS_FILE, 'r') as f:
                content = f.read()
                
            if entry in content:
                return True # Already exists
                
            with open(self.HOSTS_FILE, 'a') as f:
                f.write(f"\n{entry}\n")
            logging.info(f"Added {domain} to hosts file.")
            return True
        except Exception as e:
            logging.error(f"Failed to edit hosts file: {e}")
            return False

    def generate_vhost_config(self, project_name: str) -> bool:
        """Generates an Apache VirtualHost config file."""
        try:
            template = Template(self.template_str)
            project_path = os.path.join(self.document_root, project_name).replace("\\", "/")
            
            config_content = template.render(
                project_name=project_name, 
                project_path=project_path
            )
            
            conf_filename = os.path.join(self.vhost_conf_dir, f"vhost-{project_name}.conf")
            os.makedirs(os.path.dirname(conf_filename), exist_ok=True)
            
            with open(conf_filename, 'w') as f:
                f.write(config_content)
            logging.info(f"Generated VirtualHost config for {project_name}.test")
            return True
        except Exception as e:
            logging.error(f"Failed to generate VirtualHost config: {e}")
            return False
