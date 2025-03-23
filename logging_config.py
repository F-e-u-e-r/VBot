"""
Centralized logging configuration.
This module configures logging for the entire application.
"""
import os
import logging
import logging.config
from logging.handlers import RotatingFileHandler, SMTPHandler

def configure_logging(app):
    """
    Configure application logging based on environment.
    
    Args:
        app: Flask application instance
    """
    # Make sure log directory exists
    logs_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Determine log level from config or default to INFO
    log_level = getattr(logging, app.config.get('LOGGING_LEVEL', 'INFO'))
    
    # Basic configuration for all environments
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': log_level,
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': os.path.join(logs_dir, 'app.log'),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': os.path.join(logs_dir, 'error.log'),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': True,
            },
            'werkzeug': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'sqlalchemy.engine': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False,
            },
            'utils': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'services': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
        }
    }
    
    # Add email handler in production
    if not app.debug and not app.testing:
        mail_handler_config = None
        mail_server = app.config.get('MAIL_SERVER')
        if mail_server:
            mail_handler_config = {
                'level': 'ERROR',
                'class': 'logging.handlers.SMTPHandler',
                'formatter': 'detailed',
                'mailhost': (app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT', 25)),
                'fromaddr': app.config.get('MAIL_DEFAULT_SENDER'),
                'toaddrs': app.config.get('ADMINS', ['admin@example.com']),
                'subject': f'{app.config.get("APP_NAME", "Tracking Tool")} Application Error',
                'credentials': (
                    app.config.get('MAIL_USERNAME'),
                    app.config.get('MAIL_PASSWORD')
                ) if app.config.get('MAIL_USERNAME') else None,
                'secure': app.config.get('MAIL_USE_TLS', False),
            }
            logging_config['handlers']['mail'] = mail_handler_config
            logging_config['loggers']['']['handlers'].append('mail')
    
    # Configure logging
    logging.config.dictConfig(logging_config)
    
    # Capture warnings from Python's warnings module
    logging.captureWarnings(True)
    
    # Log application startup
    app.logger.info(f'Starting {app.config.get("APP_NAME", "Tracking Tool")} in {app.config.get("ENV")} mode')
    
    return app

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: Name for the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name) 