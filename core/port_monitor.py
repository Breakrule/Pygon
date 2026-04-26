import socket
import psutil
import logging

class PortMonitor:
    @staticmethod
    def is_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
        """Check if a specific port is in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0

    @staticmethod
    def get_process_using_port(port: int):
        """Finds the process ID and name using the specified port."""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'name': process.name()
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {'pid': conn.pid, 'name': 'Unknown'}
        except Exception as e:
            logging.error(f"Error checking ports (requires admin for some): {e}")
            
        return None
