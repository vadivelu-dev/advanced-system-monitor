"""Network operations"""
import socket
from core.logger import setup_logger
from core.exceptions import NetworkError

logger = setup_logger(__name__)

class NetworkManager:
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
    
    def check_connection(self):
        """Check if host is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                logger.info(f"✓ Connection to {self.host}:{self.port} successful")
                return True
            else:
                logger.warning(f"✗ Connection to {self.host}:{self.port} failed")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"Failed to connect: {e}")
    
    def get_hostname(self):
        """Get hostname from IP or vice versa"""
        try:
            hostname = socket.gethostbyaddr(self.host)[0]
            logger.info(f"Hostname: {hostname}")
            return hostname
        except Exception as e:
            logger.error(f"Failed to get hostname: {e}")
            return None
