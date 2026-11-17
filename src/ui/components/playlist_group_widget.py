#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Playlist Group Widget
Groups download queue items belonging to the same playlist into a collapsible card.
"""

import os
import subprocess
from typing import Dict, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QFrame
)
import qtawesome as qta

from core.queue_manager import QueueTask, queue_manager
from ui.components.queue_item_widget import QueueItemWidget


class PlaylistGroupWidget(QFrame):
    """Card grouping multiple queue tasks from the same playlist."""

    cancel_playlist_requested = Signal(str)

    def __init__(self, playlist_id: str, playlist_title: str, total_count: int, parent=None):
        super().__init__(parent)
        self.playlist_id = playlist_id
        self.playlist_title = playlist_title
        self.total_count = total_count
        self.tasks: Dict[str, QueueTask] = {}
        self.item_widgets: Dict[str, QueueItemWidget] = {}
        self._is_collapsed = False

        self.setProperty("class", "CardFrame")
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(18, 16, 18, 16)
        self.main_layout.setSpacing(12)

        # 1. Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.folder", color="#38BDF8").pixmap(22, 22))
        header_row.addWidget(icon_lbl)

        # Title
        self.title_label = QLabel(f"Oynatma Listesi: {self.playlist_title}")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        header_row.addWidget(self.title_label, stretch=1)

        # Progress / Count Badge
        self.status_badge = QLabel(f"0 / {self.total_count} Tamamlandı")
        self.status_badge.setStyleSheet(
            "background-color: #1E3A8A; color: #60A5FA; border-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px;"
        )
        header_row.addWidget(self.status_badge)

        # Collapse / Expand Button
        self.toggle_btn = QPushButton(" Gizle")
        self.toggle_btn.setIcon(qta.icon("fa5s.chevron-up", color="#94A3B8"))
        self.toggle_btn.setProperty("class", "SecondaryButton")
        self.toggle_btn.setFixedHeight(32)
        self.toggle_btn.clicked.connect(self._toggle_collapse)
        header_row.addWidget(self.toggle_btn)

        # Open Playlist Folder Button
        self.folder_btn = QPushButton()
        self.folder_btn.setIcon(qta.icon("fa5s.folder-open", color="#60A5FA"))
        self.folder_btn.setToolTip("Oynatma Listesi Klasörünü Aç")
        self.folder_btn.setProperty("class", "SecondaryButton")
        self.folder_btn.setFixedSize(32, 32)
        self.folder_btn.clicked.connect(self._open_playlist_folder)
        header_row.addWidget(self.folder_btn)

        # Cancel Playlist Button
        self.cancel_btn = QPushButton()
        self.cancel_btn.setIcon(qta.icon("fa5s.times", color="#F87171"))
        self.cancel_btn.setToolTip("Tüm Listeyi İptal Et")
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.setFixedSize(32, 32)
        self.cancel_btn.clicked.connect(self._cancel_all_in_playlist)
        header_row.addWidget(self.cancel_btn)

        self.main_layout.addLayout(header_row)

        # 2. Overall Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.main_layout.addWidget(self.progress_bar)

        # 3. Items Container (Collapsible)
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(8, 6, 8, 6)
        self.items_layout.setSpacing(8)
        self.main_layout.addWidget(self.items_container)

    def add_task_widget(self, task: QueueTask, widget: QueueItemWidget):
        self.tasks[task.task_id] = task
        self.item_widgets[task.task_id] = widget
        self.items_layout.addWidget(widget)
        self.update_task(task)

    def update_task(self, task: QueueTask):
        self.tasks[task.task_id] = task
        widget = self.item_widgets.get(task.task_id)
        if widget:
            widget.update_task(task)

        # Calculate overall group progress
        completed_count = sum(1 for t in self.tasks.values() if t.status == "completed")
        total_items = max(len(self.tasks), self.total_count)
        
        # Overall average percentage
        avg_percent = sum(t.percent for t in self.tasks.values()) / max(total_items, 1)
        self.progress_bar.setValue(int(avg_percent))

        if completed_count == total_items:
            self.status_badge.setText(f"Tamamlandı ({completed_count}/{total_items})")
            self.status_badge.setStyleSheet(
                "background-color: #064E3B; color: #34D399; border-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px;"
            )
            self.cancel_btn.setVisible(False)
        else:
            self.status_badge.setText(f"{completed_count} / {total_items} İndi (%{int(avg_percent)})")

    def _toggle_collapse(self):
        self._is_collapsed = not self._is_collapsed
        self.items_container.setVisible(not self._is_collapsed)
        if self._is_collapsed:
            self.toggle_btn.setText(" Göster")
            self.toggle_btn.setIcon(qta.icon("fa5s.chevron-down", color="#94A3B8"))
        else:
            self.toggle_btn.setText(" Gizle")
            self.toggle_btn.setIcon(qta.icon("fa5s.chevron-up", color="#94A3B8"))

    def _cancel_all_in_playlist(self):
        for task_id in list(self.tasks.keys()):
            queue_manager.cancel_task(task_id)

    def _open_playlist_folder(self):
        folder = None
        for t in self.tasks.values():
            if t.output_dir and os.path.exists(t.output_dir):
                folder = t.output_dir
                break
            if t.final_filepath and os.path.exists(os.path.dirname(t.final_filepath)):
                folder = os.path.dirname(t.final_filepath)
                break

        if not folder:
            import re
            from services.config_service import config_service
            safe = re.sub(r'[\\/*?:"<>|]', '', self.playlist_title).strip() or "Oynatma_Listesi"
            folder = os.path.join(config_service.settings.download_dir, safe)

        if os.path.exists(folder):
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])
