import requests
import re
import logging

class VersionChecker:
    """
    Utility to check the latest available versions of services.
    """
    
    @staticmethod
    def get_latest_mysql() -> str:
        try:
            # Scrape MySQL downloads page for latest GA version
            response = requests.get("https://dev.mysql.com/downloads/mysql/", timeout=5)
            match = re.search(r'MySQL Community Server (\d+\.\d+\.\d+)', response.text)
            return match.group(1) if match else "Unknown"
        except Exception as e:
            logging.error(f"Failed to check MySQL version: {e}")
            return "Error"

    @staticmethod
    def get_latest_php() -> str:
        try:
            # PHP versions are listed on windows.php.net
            response = requests.get("https://windows.php.net/download/", timeout=5)
            # Find the first 8.4.x or 8.x.x version
            match = re.search(r'PHP (\d+\.\d+\.\d+)', response.text)
            return match.group(1) if match else "Unknown"
        except Exception as e:
            logging.error(f"Failed to check PHP version: {e}")
            return "Error"

    @staticmethod
    def get_latest_node() -> str:
        try:
            # Node.js has a clean JSON API
            response = requests.get("https://nodejs.org/dist/index.json", timeout=5)
            data = response.json()
            # Return the latest version (first in list)
            return data[0]['version'].lstrip('v')
        except Exception as e:
            logging.error(f"Failed to check Node.js version: {e}")
            return "Error"

    @staticmethod
    def check_all(services: list) -> dict:
        """Checks versions for all requested services."""
        results = {}
        for svc in services:
            name = svc.lower()
            if "mysql" in name: results[svc] = VersionChecker.get_latest_mysql()
            elif "php" in name: results[svc] = VersionChecker.get_latest_php()
            elif "node" in name: results[svc] = VersionChecker.get_latest_node()
            else: results[svc] = "N/A"
        return results
