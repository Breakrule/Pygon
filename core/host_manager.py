import os
import ctypes
import logging
from jinja2 import Environment, FileSystemLoader, Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HostManager:
    HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"
    
    def __init__(self, nginx_conf_dir: str, document_root: str):
        self.nginx_conf_dir = nginx_conf_dir
        self.document_root = document_root
        
        # Simple Jinja2 template for Nginx Auto-Vhosts
        self.template_str = r"""
server {
    listen 80;
    {% if ssl_cert and ssl_key %}
    listen 443 ssl;
    ssl_certificate "{{ ssl_cert }}";
    ssl_certificate_key "{{ ssl_key }}";
    {% endif %}
    
    server_name {{ project_name }}.test;
    root "{{ project_path }}";
    index index.html index.htm index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
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

    def generate_nginx_config(self, project_name: str, ssl_cert: str = None, ssl_key: str = None) -> bool:
        """Generates an Nginx config file for a project in the www root."""
        try:
            template = Template(self.template_str)
            
            project_path = os.path.join(self.document_root, project_name)
            project_path = project_path.replace("\\", "/") # Nginx uses forward slashes
            
            # Format SSL paths for Nginx
            if ssl_cert: ssl_cert = ssl_cert.replace("\\", "/")
            if ssl_key: ssl_key = ssl_key.replace("\\", "/")
            
            config_content = template.render(
                project_name=project_name, 
                project_path=project_path,
                ssl_cert=ssl_cert,
                ssl_key=ssl_key
            )
            
            conf_filename = os.path.join(self.nginx_conf_dir, f"auto.{project_name}.test.conf")
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(conf_filename), exist_ok=True)
            
            with open(conf_filename, 'w') as f:
                f.write(config_content)
                
            logging.info(f"Generated Nginx config for {project_name}.test")
            return True
            
        except Exception as e:
            logging.error(f"Failed to generate Nginx config: {e}")
            return False
