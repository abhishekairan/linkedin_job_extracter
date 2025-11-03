"""
Configuration management module for LinkedIn Job Scraper.
Handles environment variables and configuration validation.
"""
import os
import platform
from pathlib import Path
from dotenv import load_dotenv


# Load .env file from project root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Centralized configuration class for LinkedIn Job Scraper."""
    
    # LinkedIn credentials
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    
    # Chrome/ChromeDriver paths
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    CHROME_BINARY_PATH = os.getenv('CHROME_BINARY_PATH', '/usr/bin/chromium-browser')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    IMPLICIT_WAIT = int(os.getenv('WAIT_TIME', '10'))
    
    # Platform detection
    PLATFORM = platform.system()  # Returns 'Linux', 'Windows', or 'Darwin'
    
    @classmethod
    def validate(cls):
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If required credentials are missing
            FileNotFoundError: If ChromeDriver path doesn't exist
        
        Returns:
            bool: True if all validations pass
        """
        # Check if credentials exist
        if not cls.LINKEDIN_EMAIL or not cls.LINKEDIN_PASSWORD:
            raise ValueError(
                "Missing LinkedIn credentials. "
                "Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file"
            )
        
        # Verify ChromeDriver path exists
        chromedriver_path = Path(cls.CHROMEDRIVER_PATH)
        if not chromedriver_path.exists():
            raise FileNotFoundError(
                f"ChromeDriver not found at: {cls.CHROMEDRIVER_PATH}. "
                "Please set CHROMEDRIVER_PATH in .env file"
            )
        
        return True

