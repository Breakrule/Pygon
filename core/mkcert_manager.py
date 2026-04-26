import os
import subprocess
import urllib.request
import logging

class MkcertManager:
    """
    Downloads and manages mkcert for automatic local SSL generation.
    """
    MKCERT_URL = "https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-windows-amd64.exe"
    
    def __init__(self, bin_dir: str):
        self.bin_dir = os.path.join(bin_dir, "mkcert")
        self.exe_path = os.path.join(self.bin_dir, "mkcert.exe")
        os.makedirs(self.bin_dir, exist_ok=True)

    def is_installed(self) -> bool:
        return os.path.exists(self.exe_path)

    def download_mkcert(self):
        """Downloads the mkcert executable if it doesn't exist."""
        if self.is_installed():
            return True
            
        logging.info("Downloading mkcert for local SSL support...")
        try:
            urllib.request.urlretrieve(self.MKCERT_URL, self.exe_path)
            logging.info("mkcert downloaded successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to download mkcert: {e}")
            return False

    def install_local_ca(self):
        """Uses mkcert -install to create a local Certificate Authority."""
        if not self.is_installed():
            self.download_mkcert()
            
        try:
            # -install requires Administrator privileges to add to the system trust store on Windows
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run([self.exe_path, "-install"], creationflags=creationflags, check=True)
            logging.info("mkcert local CA installed and trusted.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install local CA: {e}")
            return False

    def generate_cert(self, domain: str, output_dir: str) -> bool:
        """Generates a site-specific certificate."""
        if not self.is_installed():
            return False

        try:
            cert_file = os.path.join(output_dir, f"{domain}.crt")
            key_file = os.path.join(output_dir, f"{domain}.key")
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            subprocess.run([
                self.exe_path,
                "-cert-file", cert_file,
                "-key-file", key_file,
                domain
            ], creationflags=creationflags, check=True)
            
            logging.info(f"Generated SSL certificate for {domain}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to generate certificate for {domain}: {e}")
            return False
