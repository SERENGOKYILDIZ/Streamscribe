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
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = Path(config.LOG_FILE)
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_file.with_suffix('.error.log'),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self._logger.addHandler(error_handler)
    
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
