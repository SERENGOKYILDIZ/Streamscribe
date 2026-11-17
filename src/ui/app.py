#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Main Application Window
PySide6-powered responsive, modern desktop interface.
"""

import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame
)
import qtawesome as qta

from ui.styles import DARK_THEME_QSS
from ui.views import DownloaderView, QueueView, HistoryView, SettingsView
from core.queue_manager import queue_manager, QueueTask
from services.config_service import config_service
from services.logger import get_logger
from config import Config, load_version_from_ini

logger = get_logger("app")


class MainWindow(QMainWindow):
    """Main application window with modern navigation sidebar and stacked views."""

    def __init__(self):
        super().__init__()
        self.app_version = load_version_from_ini()
        config_service.settings.app_version = self.app_version
        self.setWindowTitle(f"{Config.APP_NAME} v{self.app_version}")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 640)

        # Set Application Icon
        self._set_app_icon()

        # Build UI layout
        self._setup_ui()
        self._connect_signals()

    def _set_app_icon(self):
        meipass = getattr(sys, "_MEIPASS", None)
        candidates = []
        if meipass:
            candidates.extend([
                Path(meipass) / "logo" / "favicon.ico",
                Path(meipass) / "logo" / "logo.png",
            ])
        candidates.extend([
            Path.cwd() / "logo" / "favicon.ico",
            Path.cwd() / "logo" / "logo.png",
            Path(__file__).resolve().parent.parent.parent / "logo" / "favicon.ico",
            Path(__file__).resolve().parent.parent.parent / "logo" / "logo.png",
            Path(__file__).resolve().parent.parent / "logo" / "favicon.ico",
        ])
        for c in candidates:
            if c.exists():
                self.setWindowIcon(QIcon(str(c)))
                break

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 20, 14, 20)
        sidebar_layout.setSpacing(8)

        # Logo / Branding
        logo_row = QHBoxLayout()
        logo_row.setSpacing(8)
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon("fa5s.bolt", color="#38BDF8").pixmap(24, 24))
        logo_row.addWidget(logo_icon)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(0)
        title_lbl = QLabel(Config.APP_NAME)
        title_lbl.setObjectName("AppLogoTitle")
        self.ver_lbl = QLabel(f"v{self.app_version}")
        self.ver_lbl.setObjectName("AppVersionLabel")
        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(self.ver_lbl)
        logo_row.addLayout(title_vbox)
        logo_row.addStretch()
        sidebar_layout.addLayout(logo_row)

        sidebar_layout.addSpacing(24)

        # Navigation Buttons
        self.nav_buttons = []

        self.btn_downloader = self._create_nav_button(" İndirici", "fa5s.download", 0)
        sidebar_layout.addWidget(self.btn_downloader)

        self.btn_queue = self._create_nav_button(" Kuyruk", "fa5s.tasks", 1)
        sidebar_layout.addWidget(self.btn_queue)

        self.btn_history = self._create_nav_button(" Geçmiş", "fa5s.history", 2)
        sidebar_layout.addWidget(self.btn_history)

        self.btn_settings = self._create_nav_button(" Ayarlar", "fa5s.cog", 3)
        sidebar_layout.addWidget(self.btn_settings)

        sidebar_layout.addStretch()

        # Footer info
        footer_lbl = QLabel(f"© 2026 {Config.APP_AUTHOR}\n{Config.APP_NAME} v{self.app_version}")
        footer_lbl.setStyleSheet("color: #475569; font-size: 10px; line-height: 1.4;")
        sidebar_layout.addWidget(footer_lbl)

        main_layout.addWidget(sidebar)

        # 2. Right Stacked Content
        self.stack = QStackedWidget()

        # Primary view loaded immediately for instant startup
        self.downloader_view = DownloaderView()
        self.downloader_view.navigate_to_queue.connect(lambda: self._switch_view(1))
        self.stack.addWidget(self.downloader_view)

        # Placeholders for lazy-loaded views
        self.queue_view = None
        self.history_view = None
        self.settings_view = None

        main_layout.addWidget(self.stack, stretch=1)

        # Activate initial view
        self._switch_view(0)

        # Defer background initialization of secondary views for instant window display
        QTimer.singleShot(60, self._init_deferred_views)

    def _init_deferred_views(self):
        """Preload secondary views in background after window is already displayed."""
        if self.queue_view is None:
            self._get_or_create_view(1)
        if self.history_view is None:
            self._get_or_create_view(2)
        if self.settings_view is None:
            self._get_or_create_view(3)

    def _get_or_create_view(self, index: int):
        if index == 1:
            if self.queue_view is None:
                self.queue_view = QueueView()
                self.stack.addWidget(self.queue_view)
            return self.queue_view
        elif index == 2:
            if self.history_view is None:
                self.history_view = HistoryView()
                self.stack.addWidget(self.history_view)
            return self.history_view
        elif index == 3:
            if self.settings_view is None:
                self.settings_view = SettingsView()
                self.stack.addWidget(self.settings_view)
            return self.settings_view
        return self.downloader_view

    def _create_nav_button(self, text: str, icon_name: str, index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color="#94A3B8"))
        btn.setIconSize(QSize(18, 18))
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self._switch_view(index))
        self.nav_buttons.append(btn)
        return btn

    def _switch_view(self, index: int):
        target_widget = self._get_or_create_view(index)
        self.stack.setCurrentWidget(target_widget)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            if i == index:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh history when switching to history view
        if index == 2 and self.history_view:
            self.history_view.refresh_history()

    def _connect_signals(self):
        signals = queue_manager.signals
        signals.task_added.connect(self._on_task_count_changed)
        signals.task_completed.connect(self._on_task_count_changed)
        signals.task_failed.connect(self._on_task_count_changed)
        signals.task_cancelled.connect(self._on_task_count_changed)

    def _on_task_count_changed(self, task: QueueTask):
        active_count = sum(1 for t in queue_manager.get_all_tasks() if t.status in ("queued", "downloading", "transcribing"))
        if active_count > 0:
            self.btn_queue.setText(f" Kuyruk ({active_count})")
        else:
            self.btn_queue.setText(" Kuyruk")
