"""
Test Procedure Management System - Configuration
Flask application configuration
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "instance" / "test_procedures.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    EXPORT_FOLDER = BASE_DIR / 'exports'
    BACKUP_FOLDER = BASE_DIR / 'backups'

    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'txt'}

    # Pagination
    PROCEDURES_PER_PAGE = 20
    RESULTS_PER_PAGE = 50

    # Languages
    LANGUAGES = ['tr', 'en']
    DEFAULT_LANGUAGE = 'en'

    # Backup
    AUTO_BACKUP_ENABLED = True
    AUTO_BACKUP_INTERVAL_DAYS = 7
    MAX_BACKUP_FILES = 10

    # Session
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Timezone
    TIMEZONE = 'Europe/Istanbul'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
