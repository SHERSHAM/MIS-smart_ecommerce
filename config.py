"""
VIVA - LIVE BETTER | Smart E-Commerce Decision Support System
Configuration Module
"""

import os
from dotenv import load_dotenv

# Ensure .env is loaded from the exact project directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'viva-secret-key-2026-elevate-your-everyday-sedss')

    # MySQL Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Shersha123')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'smart_ecommerce_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_CURSORCLASS = 'DictCursor'

    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')

    # Shipping
    FREE_SHIPPING_THRESHOLD = 999  # Free shipping on orders above ₹999
    SHIPPING_FEE = 49  # ₹49 shipping for orders below threshold

    # Pagination
    PRODUCTS_PER_PAGE = 12


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
