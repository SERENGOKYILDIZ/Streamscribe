#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Configuration Module
Centralized configuration management for the application
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Config:
    """Application configuration class"""
    
    # Application Info
    APP_NAME = "StreamScribe"
    APP_VERSION = "2.1"
    APP_AUTHOR = "Semi Eren Gökyıldız"
    
    # Performance Settings
    CACHE_SIZE = 50
    THUMBNAIL_CACHE_SIZE = 30
    MAX_PLAYLIST_VIDEOS = 50
    
    # Timeout Settings
    TIMEOUT_FAST = 1.5
    TIMEOUT_NORMAL = 3.0
    TIMEOUT_LONG = 10.0
    
    # Download Settings
    DEFAULT_QUALITY = "1080p"
    DEFAULT_FORMAT = "video"
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Quality Mapping
    QUALITY_MAP = {
        "4K": 2160,
        "1440p": 1440,
        "1080p": 1080,
        "720p": 720,
        "480p": 480,
        "360p": 360
    }
    
    # FFmpeg Settings
    FFMPEG_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")
    
    # GUI Settings
    WINDOW_WIDTH = 1050  # Increased from 1000 to accommodate wider panels
    WINDOW_HEIGHT = 680  # Increased from 620
    MIN_WINDOW_WIDTH = 900  # Increased from 850
    MIN_WINDOW_HEIGHT = 580  # Increased from 520
    
    # Theme Settings
    THEME_MODE = "dark"
    COLOR_THEME = "blue"
    
    # Logging Settings
    LOG_LEVEL = "ERROR"
    LOG_FILE = "streamscribe.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # User Agent for requests
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Request Headers
    REQUEST_HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    @classmethod
    def get_quality_value(cls, quality: str) -> int:
        """Get numeric quality value from string"""
        return cls.QUALITY_MAP.get(quality, 1080)
    
    @classmethod
    def get_ffmpeg_path(cls) -> str:
        """Get FFmpeg executable path"""
        if os.path.exists(cls.FFMPEG_LOCAL_PATH):
            return cls.FFMPEG_LOCAL_PATH
        return "ffmpeg"
    
    @classmethod
    def load_user_config(cls, config_file: str = "user_config.json") -> Dict[str, Any]:
        """Load user configuration from file"""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
        return {}
    
    @classmethod
    def save_user_config(cls, config: Dict[str, Any], config_file: str = "user_config.json") -> bool:
        """Save user configuration to file"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False


# Global configuration instance
config = Config()
