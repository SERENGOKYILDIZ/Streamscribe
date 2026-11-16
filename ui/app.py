#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Main Application Window
PySide6-powered responsive, modern desktop interface.
"""

import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSize
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

logger = get_logger("app")


class MainWindow(QMainWindow):
    """Main application window with modern navigation sidebar and stacked views."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config_service.settings.app_name} v{config_service.settings.app_version}")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 640)

        # Set Application Icon
        self._set_app_icon()

        # Build UI layout
        self._setup_ui()
        self._connect_signals()

    def _set_app_icon(self):
        project_root = Path(__file__).resolve().parent.parent
        candidates = [
            project_root / "logo" / "icon.ico",
            project_root / "logo" / "logo.png",
        ]
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
        title_lbl = QLabel(config_service.settings.app_name)
        title_lbl.setObjectName("AppLogoTitle")
        ver_lbl = QLabel(f"v{config_service.settings.app_version}")
        ver_lbl.setObjectName("AppVersionLabel")
        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(ver_lbl)
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
        footer_lbl = QLabel("© 2026 Semi Eren Gökyıldız\nModern Video & Audio Engine")
        footer_lbl.setStyleSheet("color: #475569; font-size: 10px; line-height: 1.4;")
        sidebar_layout.addWidget(footer_lbl)

        main_layout.addWidget(sidebar)

        # 2. Right Stacked Content
        self.stack = QStackedWidget()

        self.downloader_view = DownloaderView()
        self.downloader_view.navigate_to_queue.connect(lambda: self._switch_view(1))
        self.stack.addWidget(self.downloader_view)

        self.queue_view = QueueView()
        self.stack.addWidget(self.queue_view)

        self.history_view = HistoryView()
        self.stack.addWidget(self.history_view)

        self.settings_view = SettingsView()
        self.stack.addWidget(self.settings_view)

        main_layout.addWidget(self.stack, stretch=1)

        # Activate initial view
        self._switch_view(0)

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
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            if i == index:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh history when switching to history view
        if index == 2:
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
