"""
Application configuration settings.
This module contains configuration classes for different environments.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Enable CSRF protection by default
    WTF_CSRF_ENABLED = True
    
    # File upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    
    # Flask-Limiter configuration
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # CORS settings
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Ensure upload folder exists
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Set absolute paths for static files if in production
        if not app.debug and not app.testing:
            app.static_folder = os.path.join(os.getcwd(), 'static')
            app.template_folder = os.path.join(os.getcwd(), 'templates')

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.getcwd(), 'instance', 'dev.sqlite')
    
    # Expanded logging for development
    LOGGING_LEVEL = 'DEBUG'
    
    # More lenient rate limits for development
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour"
    
    # Enable full error reporting
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True
    
    # CORS settings for development
    CORS_ORIGINS = "*"

class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    DEBUG = True
    
    # Use a separate database for testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.getcwd(), 'instance', 'testing.sqlite')
    
    # Disable CSRF for testing API endpoints
    WTF_CSRF_ENABLED = False
    
    # Use a test upload folder
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'uploads')
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Shorter session lifetime for testing
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    
    # Testing URL
    SERVER_NAME = "testing.vbot.autos"
    
    # Disable email sending in testing
    MAIL_SUPPRESS_SEND = True
    
    # Testing-specific configuration
    TESTING_BANNER = True

class ProductionConfig(Config):
    """Configuration for production environment."""
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost/tracking_tool'
    
    # Production security settings
    WTF_CSRF_ENABLED = True
    CORS_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '').split(',')
    
    # Set strict content security policy
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' 'unsafe-inline'",  # Allow inline styles for Bootstrap
        'img-src': "'self' data:",  # Allow data: URLs for images
        'font-src': "'self'",
    }
    
    # Extended session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging configuration
    LOGGING_LEVEL = 'INFO'
    
    # File storage settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/var/www/tracking-tool/uploads'
    
    @staticmethod
    def init_app(app):
        """Initialize application with production settings."""
        Config.init_app(app)
        
        # Set up production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        handler = RotatingFileHandler('app.log', maxBytes=10485760, backupCount=10)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        
        # Apply security headers
        @app.after_request
        def add_security_headers(response):
            # Content Security Policy
            if app.config.get('CONTENT_SECURITY_POLICY'):
                csp = app.config['CONTENT_SECURITY_POLICY']
                csp_str = '; '.join(f"{key} {value}" for key, value in csp.items())
                response.headers['Content-Security-Policy'] = csp_str
            
            # Other security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            return response

class DockerConfig(ProductionConfig):
    """Configuration for Docker deployment."""
    # Use environment variables from Docker
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Docker-specific paths
    UPLOAD_FOLDER = '/app/uploads'
    
    # Allow Docker internal network
    CORS_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:80').split(',')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}
