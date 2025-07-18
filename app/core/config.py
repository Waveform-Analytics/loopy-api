from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # MongoDB connection (from environment variables)
    mongodb_username: str
    mongodb_pw: str  
    mongodb_uri_template: str  # Template with placeholders like mongodb+srv://{username}:{password}@...
    mongodb_database: str = "myCGMitc"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Authentication
    api_key: str = secrets.token_urlsafe(32)  # Generate random key if not provided
    
    # CORS settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def mongodb_uri(self) -> str:
        """Build the complete MongoDB URI from template and credentials."""
        return self.mongodb_uri_template.format(
            username=self.mongodb_username,
            password=self.mongodb_pw
        )


settings = Settings()

# Set MONGODB_URI for loopy-basic package
os.environ["MONGODB_URI"] = settings.mongodb_uri