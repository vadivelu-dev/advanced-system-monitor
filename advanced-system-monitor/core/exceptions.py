"""Custom exceptions"""

class AppException(Exception):
    """Base application exception"""
    pass

class ConnectionError(AppException):
    """Connection-related errors"""
    pass

class ConfigError(AppException):
    """Configuration-related errors"""
    pass

class NetworkError(AppException):
    """Network-related errors"""
    pass
