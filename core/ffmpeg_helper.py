#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe FFmpeg Helper Module
Discovers and manages FFmpeg binaries and common media operations.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List
from services.logger import get_logger

logger = get_logger("ffmpeg_helper")


class FFmpegHelper:
    """Manages FFmpeg location and invocation."""
    
    _cached_ffmpeg_path: Optional[str] = None

    @classmethod
    def get_ffmpeg_path(cls) -> Optional[str]:
        """Locate FFmpeg executable: local project bundle or system PATH."""
        if cls._cached_ffmpeg_path and os.path.exists(cls._cached_ffmpeg_path):
            return cls._cached_ffmpeg_path

        # 1. Project local ffmpeg folder
        project_root = Path(__file__).resolve().parent.parent
        candidates = [
            project_root / "ffmpeg" / "bin" / "ffmpeg.exe",
            project_root / "ffmpeg" / "ffmpeg.exe",
            project_root / "bin" / "ffmpeg.exe",
        ]
        for candidate in candidates:
            if candidate.exists() and os.access(candidate, os.X_OK):
                cls._cached_ffmpeg_path = str(candidate)
                logger.info(f"Using bundled FFmpeg: {cls._cached_ffmpeg_path}")
                return cls._cached_ffmpeg_path

        # 2. System PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            cls._cached_ffmpeg_path = system_ffmpeg
            logger.info(f"Using system FFmpeg: {system_ffmpeg}")
            return system_ffmpeg

        logger.warning("FFmpeg not found in bundle or system PATH.")
        return None

    @classmethod
    def is_available(cls) -> bool:
        return cls.get_ffmpeg_path() is not None

    @classmethod
    def extract_audio(cls, video_path: str, output_path: str, audio_format: str = "mp3", bitrate: str = "192k") -> bool:
        """Extract audio track from video to mp3/wav."""
        ffmpeg_bin = cls.get_ffmpeg_path()
        if not ffmpeg_bin:
            logger.error("Cannot extract audio: FFmpeg not found.")
            return False

        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame" if audio_format == "mp3" else "pcm_s16le",
            "-b:a", bitrate,
            output_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg audio extraction failed: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
