#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Modern Entry Point
Powered by PySide6 & yt-dlp & Whisper.
"""

import sys
import os
from pathlib import Path

# Add project root and src directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from services.config_service import config_service
from services.logger import setup_logger, get_logger
from core.ffmpeg_helper import FFmpegHelper
from ui.app import MainWindow
from ui.styles import DARK_THEME_QSS

logger = get_logger("main")


def main():
    setup_logger()
    logger.info("Initializing StreamScribe Modern...")

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(config_service.settings.app_name)
    app.setApplicationVersion(config_service.settings.app_version)

    # Apply modern dark theme stylesheet
    app.setStyleSheet(DARK_THEME_QSS)

    # Check FFmpeg
    if not FFmpegHelper.is_available():
        logger.warning("FFmpeg executable could not be detected. Merging and audio conversions may be limited.")

    # Create and display main window
    window = MainWindow()
    window.show()

    logger.info("StreamScribe window loaded successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
