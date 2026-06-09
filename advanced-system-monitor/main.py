"""Main application entry point"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.config import Config
from core.logger import setup_logger
from subsystems.network import NetworkManager
from subsystems.sysstat import SystemStats
from utils.helpers import format_output

logger = setup_logger(__name__)

def main():
    logger.info("Starting application...")
    
    # Display system information
    sys_info = SystemStats.get_system_info()
    format_output("System Information", sys_info)
    
    # Test network connectivity
    network_mgr = NetworkManager("8.8.8.8", 53, timeout=5)
    try:
        is_connected = network_mgr.check_connection()
        format_output("Network Status", f"Connected: {is_connected}")
    except Exception as e:
        logger.error(f"Network test failed: {e}")
        format_output("Network Status", "Connection failed")
    
    logger.info("Application finished successfully!")

if __name__ == "__main__":
    main()
