#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Logger Service
Rotating structured logger.
"""

import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_INITIALIZED = False


def setup_logger(log_dir: Path = None, level: int = logging.INFO) -> logging.Logger:
    global _INITIALIZED
    logger = logging.getLogger("streamscribe")
    
    if _INITIALIZED:
        return logger
        
    logger.setLevel(level)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # File Handler
    if log_dir is None:
        log_dir = Path.home() / ".streamscribe" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "streamscribe.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    _INITIALIZED = True
    return logger


def get_logger(module_name: str) -> logging.Logger:
    """Returns a child logger for the given module name."""
    if not _INITIALIZED:
        setup_logger()
    return logging.getLogger(f"streamscribe.{module_name}")
