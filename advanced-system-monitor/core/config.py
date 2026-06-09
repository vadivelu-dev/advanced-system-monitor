"""Configuration management"""

class Config:
    DEBUG = True
    HOST = "localhost"
    PORT = 5000
    TIMEOUT = 10
    LOG_LEVEL = "INFO"

    @staticmethod
    def get_db_url():
        return f"sqlite:///app.db"
