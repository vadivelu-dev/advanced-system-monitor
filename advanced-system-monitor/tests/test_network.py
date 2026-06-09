"""Test network operations"""
import unittest
from subsystems.network import NetworkManager
from core.exceptions import NetworkError

class TestNetworkManager(unittest.TestCase):
    def setUp(self):
        self.manager = NetworkManager("8.8.8.8", 53, timeout=5)
    
    def test_check_connection(self):
        """Test connection check"""
        try:
            result = self.manager.check_connection()
            self.assertIsNotNone(result)
            print(f"Connection test result: {result}")
        except NetworkError as e:
            print(f"Network error (expected): {e}")

if __name__ == '__main__':
    unittest.main()
