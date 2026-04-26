import os
import urllib.request
import zipfile
import logging
import shutil
import socket


class AutoDownloader:
    """
    Downloads and extracts required binaries if they are missing.
    """

    # Download URLs for all services (Windows x64)
    URLS = {
        "apache":   "https://www.apachelounge.com/download/VS18/binaries/httpd-2.4.66-260223-Win64-VS18.zip",
        "mysql":    "https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.3-winx64.zip",
        "php":      "https://windows.php.net/downloads/releases/php-8.4.4-nts-Win32-vs17-x64.zip",
        "node":     "https://nodejs.org/dist/v20.20.0/node-v20.20.0-win-x64.zip",
    }

    # MySQL blocks standard browser User-Agents, but allows standard command line tools like curl.
    USER_AGENT = "curl/8.4.0"

    def __init__(self, bin_dir: str):
        self.bin_dir = bin_dir

    def _download_file(self, url: str, dest_path: str, progress_callback=None):
        """Downloads a file with a proper User-Agent header and progress reporting."""
        # Build headers — Apache Lounge requires Referer to serve the zip
        from urllib.parse import urlparse
        parsed = urlparse(url)
        referer = f"{parsed.scheme}://{parsed.netloc}/"
        req = urllib.request.Request(url, headers={
            "User-Agent": self.USER_AGENT,
            "Referer": referer,
            "Accept": "*/*",
        })
        response = urllib.request.urlopen(req, timeout=60)
        total_size = int(response.headers.get("Content-Length", 0))
        block_size = 8192
        downloaded = 0
        block_num = 0

        with open(dest_path, "wb") as f:
            while True:
                chunk = response.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                block_num += 1
                if progress_callback and total_size:
                    progress_callback(block_num, block_size, total_size)

    def download_and_extract(self, service_name: str, target_folder: str, progress_callback=None, status_callback=None) -> bool:
        """
        Downloads a zip file from URLS[service_name] and extracts it to target_folder.
        target_folder should be an absolute path to the service directory (e.g. bin/apache).
        """
        if service_name not in self.URLS:
            logging.error(f"No download URL configured for {service_name}")
            return False

        url = self.URLS[service_name]
        zip_path = os.path.join(self.bin_dir, f"{service_name}_download.zip")

        # If target_folder is relative, join with bin_dir; if absolute, use as-is
        if os.path.isabs(target_folder):
            extract_path = target_folder
        else:
            extract_path = os.path.join(self.bin_dir, target_folder)

        os.makedirs(extract_path, exist_ok=True)

        try:
            if status_callback:
                status_callback("Connecting to download server...")

            logging.info(f"Downloading {service_name} from {url}...")

            self._download_file(url, zip_path, progress_callback=progress_callback)

            if status_callback:
                status_callback("Extracting files...")
            logging.info(f"Extracting {service_name} to {extract_path}...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Clean up zip
            if os.path.exists(zip_path):
                os.remove(zip_path)

            # Post-extraction: flatten nested folders
            self._flatten_extracted(service_name, extract_path)

            # Service-specific post-install patching
            if service_name == "apache":
                self._patch_apache_config(extract_path)

            logging.info(f"Successfully installed {service_name}")
            return True

        except Exception as e:
            if status_callback:
                status_callback(f"Download failed: {str(e)}")
            logging.error(f"Failed to install {service_name}: {e}")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass
            return False

    def _flatten_extracted(self, service_name: str, extract_path: str):
        """
        Many zip files contain a single root folder (e.g. nginx-1.28.0/, mysql-8.4.3-winx64/).
        This moves the contents up one level so executables are in the expected locations.
        """
        # Map of service_name -> expected nested folder prefix patterns
        # We look for any single subfolder that matches and flatten it
        prefix_patterns = {
            "apache":  "Apache24",
            "mysql":   "mysql-",
            "php":     "php-",
            "node":    "node-",
        }

        prefix = prefix_patterns.get(service_name)
        if prefix is None:
            return

        # Find matching subfolder
        try:
            items = os.listdir(extract_path)
        except Exception:
            return

        for item in items:
            item_path = os.path.join(extract_path, item)
            if os.path.isdir(item_path) and item.startswith(prefix):
                # Move all contents up one level
                self._move_contents_up(item_path, extract_path)
                # Remove the now-empty folder
                try:
                    shutil.rmtree(item_path, ignore_errors=True)
                except Exception:
                    pass
                break

    @staticmethod
    def _move_contents_up(source_dir: str, dest_dir: str):
        """Moves all files and folders from source_dir into dest_dir."""
        for item in os.listdir(source_dir):
            src = os.path.join(source_dir, item)
            dst = os.path.join(dest_dir, item)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                else:
                    os.remove(dst)
            shutil.move(src, dst)

    def _patch_apache_config(self, extract_path: str):
        """Patches Apache's httpd.conf to use Pygon's actual paths instead of the hardcoded c:/Apache24."""
        conf_file = os.path.join(extract_path, 'conf', 'httpd.conf')
        if not os.path.exists(conf_file):
            return

        # Get absolute path with forward slashes for Apache conf
        abs_path = os.path.abspath(extract_path).replace('\\', '/')
        
        try:
            with open(conf_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Update ServerRoot
            content = content.replace('Define SRVROOT "c:/Apache24"', f'Define SRVROOT "{abs_path}"')
            content = content.replace('Define SRVROOT "C:/Apache24"', f'Define SRVROOT "{abs_path}"')
            
            # 2. Update DocumentRoot to point to Pygon's www directory
            # Base directory is one level up from bin_dir
            base_dir = os.path.dirname(os.path.abspath(self.bin_dir)).replace('\\', '/')
            www_dir = f"{base_dir}/www"
            
            content = content.replace('DocumentRoot "${SRVROOT}/htdocs"', f'DocumentRoot "{www_dir}"')
            content = content.replace('<Directory "${SRVROOT}/htdocs">', f'<Directory "{www_dir}">')
            
            # 3. Add ServerName to suppress warnings if it's commented out
            if '#ServerName www.example.com:80' in content:
                content = content.replace('#ServerName www.example.com:80', 'ServerName localhost:80')

            with open(conf_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info("Successfully patched Apache httpd.conf paths")
        except Exception as e:
            logging.error(f"Failed to patch Apache config: {e}")

