#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Configuration Service
Centralized and persistent configuration management.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from config import Config, load_version_from_ini


@dataclass
class AppSettings:
    # General
    app_name: str = Config.APP_NAME
    app_version: str = field(default_factory=load_version_from_ini)
    app_author: str = Config.APP_AUTHOR
    theme_mode: str = "dark"           # "dark", "light", "system"
    theme_color: str = "blue"          # "blue", "purple", "emerald"
    download_dir: str = field(default_factory=lambda: str(Path.home() / "Downloads" / "StreamScribe"))
    
    # Download Preferences
    default_format: str = "mp4"        # "mp4", "mkv", "mp3", "wav"
    default_quality: str = "1080p"     # "best", "2160p", "1440p", "1080p", "720p", "480p", "audio_only"
    max_concurrent_downloads: int = 2  # 1 to 5
    embed_subtitles: bool = True
    subtitle_langs: str = "en,tr"      # comma separated
    auto_subtitles: bool = True
    
    # Authentication (Udemy, etc.)
    cookie_browser: str = "none"       # "none", "chrome", "firefox", "edge", "brave"
    custom_cookie_file: str = ""
    
    # Whisper / Transcription Settings
    whisper_model: str = "base"        # "tiny", "base", "small", "medium", "large"
    whisper_device: str = "auto"       # "auto", "cpu", "cuda"
    auto_transcribe_on_download: bool = False
    transcribe_output_formats: list = field(default_factory=lambda: ["srt", "txt"])
    
    # Network & Performance
    chunk_size_mb: int = 10
    socket_timeout: int = 15
    retries: int = 5


class ConfigService:
    """Manages application settings with persistent JSON storage."""
    
    CONFIG_FILENAME = "streamscribe_settings.json"
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Store config in user's home directory under .streamscribe
            self.config_dir = Path.home() / ".streamscribe"
        else:
            self.config_dir = config_dir
            
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self.settings: AppSettings = self.load_settings()
        
        # Ensure download directory exists
        Path(self.settings.download_dir).mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> AppSettings:
        """Load settings from JSON file, falling back to defaults."""
        if not self.config_file.exists():
            default_settings = AppSettings()
            self.save_settings(default_settings)
            return default_settings
            
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Filter valid fields for AppSettings and enforce latest version & static author
            live_version = load_version_from_ini()
            valid_keys = AppSettings.__dataclass_fields__.keys()
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            needs_sync = (
                filtered_data.get("app_version") != live_version
                or filtered_data.get("app_author") != Config.APP_AUTHOR
            )
            filtered_data["app_version"] = live_version
            filtered_data["app_author"] = Config.APP_AUTHOR
            settings = AppSettings(**filtered_data)
            if needs_sync:
                self.save_settings(settings)
            return settings
        except Exception:
            return AppSettings()

    def save_settings(self, settings: Optional[AppSettings] = None) -> bool:
        """Save settings to disk."""
        if settings is not None:
            self.settings = settings
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.settings), f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def update(self, **kwargs) -> bool:
        """Update specific setting attributes and save."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        return self.save_settings()


# Global Singleton Instance
config_service = ConfigService()
