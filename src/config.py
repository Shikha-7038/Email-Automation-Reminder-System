"""
Configuration management for Email Automation System
Loads environment variables and system settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailConfig:
    """Email server configuration"""
    
    # SMTP Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    
    # System Configuration
    DRY_RUN = os.getenv('DRY_RUN', 'False').lower() == 'true'
    
    @classmethod
    def is_configured(cls):
        """Check if email configuration is complete"""
        return bool(cls.SENDER_EMAIL and cls.SENDER_PASSWORD)
    
    @classmethod
    def get_config_summary(cls):
        """Return configuration summary (hides sensitive data)"""
        return {
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'sender_email': cls.SENDER_EMAIL if cls.SENDER_EMAIL else 'Not set',
            'dry_run': cls.DRY_RUN,
            'configured': cls.is_configured()
        }