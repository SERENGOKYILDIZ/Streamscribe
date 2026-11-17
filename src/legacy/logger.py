#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Logging Module
Centralized logging configuration and utilities
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from config import config


class StreamScribeLogger:
    """Centralized logging manager for StreamScribe"""
    
    _instance: Optional['StreamScribeLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'StreamScribeLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup the main logger with file and console handlers"""
        self._logger = logging.getLogger('StreamScribe')
        self._logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler
        try:
            log_file = config.LOG_FILE
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file handler: {e}")
        
        # Set level for both handlers
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        console_handler.setLevel(log_level)
        if 'file_handler' in locals():
            file_handler.setLevel(log_level)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'StreamScribe.{name}')
        return self._logger
    
    def set_level(self, level: str):
        """Set logging level"""
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(getattr(logging, level.upper(), logging.INFO))


# Global logger instance
logger_manager = StreamScribeLogger()


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance"""
    return logger_manager.get_logger(name)


def setup_logging(level: str = "INFO"):
    """Setup logging for the application"""
    logger_manager.set_level(level)


# Convenience functions
def log_info(message: str, logger_name: str = None):
    """Log info message"""
    get_logger(logger_name).info(message)


def log_warning(message: str, logger_name: str = None):
    """Log warning message"""
    get_logger(logger_name).warning(message)


def log_error(message: str, logger_name: str = None):
    """Log error message"""
    get_logger(logger_name).error(message)


def log_debug(message: str, logger_name: str = None):
    """Log debug message"""
    get_logger(logger_name).debug(message)


def log_exception(message: str, logger_name: str = None):
    """Log exception with traceback"""
    get_logger(logger_name).exception(message)


def export_latest_log():
    """Export current log file content to latest_log.txt, overwriting previous version.
    Called on application shutdown to preserve the last session's logs."""
    try:
        log_file = config.LOG_FILE
        latest_log_file = os.path.join(os.path.dirname(os.path.abspath(log_file)), "latest_log.txt")
        
        if os.path.exists(log_file):
            import shutil
            shutil.copy2(log_file, latest_log_file)
            get_logger().info(f"Latest log exported to: {latest_log_file}")
        else:
            # If no log file exists, write current session info
            with open(latest_log_file, 'w', encoding='utf-8') as f:
                import datetime
                f.write(f"StreamScribe v{config.APP_VERSION} - Session Log\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("No log entries recorded during this session.\n")
    except Exception as e:
        print(f"Failed to export latest log: {e}")
