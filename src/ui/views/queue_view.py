#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Queue View
Live download queue list with support for standalone items and grouped playlists.
"""

from typing import Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox
)
import qtawesome as qta

from core.queue_manager import queue_manager, QueueTask
from ui.components.queue_item_widget import QueueItemWidget
from ui.components.playlist_group_widget import PlaylistGroupWidget


class QueueView(QWidget):
    """View displaying active, queued, and finished download tasks with playlist grouping."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_widgets: Dict[str, QueueItemWidget] = {}
        self.playlist_groups: Dict[str, PlaylistGroupWidget] = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Row
        header_row = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_lbl = QLabel("İndirme Kuyruğu")
        header_lbl.setObjectName("ViewHeaderLabel")
        sub_lbl = QLabel("Devam eden ve sıradaki indirme/transkripsiyon görevleri.")
        sub_lbl.setObjectName("ViewSubHeaderLabel")
        header_text_layout.addWidget(header_lbl)
        header_text_layout.addWidget(sub_lbl)
        header_row.addLayout(header_text_layout, stretch=1)

        # Action Buttons
        self.clear_btn = QPushButton(" Tamamlananları Temizle")
        self.clear_btn.setIcon(qta.icon("fa5s.check-circle", color="#94A3B8"))
        self.clear_btn.setProperty("class", "SecondaryButton")
        self.clear_btn.clicked.connect(self._clear_finished)
        header_row.addWidget(self.clear_btn)

        self.cancel_all_btn = QPushButton(" Tümünü İptal Et")
        self.cancel_all_btn.setIcon(qta.icon("fa5s.stop", color="white"))
        self.cancel_all_btn.setProperty("class", "DangerButton")
        self.cancel_all_btn.clicked.connect(self._cancel_all)
        header_row.addWidget(self.cancel_all_btn)

        main_layout.addLayout(header_row)

        # Scrollable Task Container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.tasks_layout = QVBoxLayout(self.scroll_content)
        self.tasks_layout.setContentsMargins(0, 8, 0, 8)
        self.tasks_layout.setSpacing(14)

        # Empty Queue Placeholder
        self.empty_label = QLabel("Şu anda kuyrukta bekleyen bir indirme yok.\nİndirici sekmesinden video ekleyebilirsiniz.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #64748B; font-size: 14px; padding: 60px;")
        self.tasks_layout.addWidget(self.empty_label)

        self.tasks_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

    def _connect_signals(self):
        signals = queue_manager.signals
        signals.task_added.connect(self._on_task_added)
        signals.task_updated.connect(self._on_task_updated)
        signals.task_completed.connect(self._on_task_updated)
        signals.task_failed.connect(self._on_task_updated)
        signals.task_cancelled.connect(self._on_task_updated)

    def _on_task_added(self, task: QueueTask):
        self.empty_label.setVisible(False)

        # 1. Grouped Playlist Task
        if task.playlist_id:
            group = self.playlist_groups.get(task.playlist_id)
            if not group:
                group = PlaylistGroupWidget(
                    playlist_id=task.playlist_id,
                    playlist_title=task.playlist_title or "Oynatma Listesi",
                    total_count=task.playlist_total,
                    parent=self.scroll_content
                )
                self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, group)
                self.playlist_groups[task.playlist_id] = group

            widget = QueueItemWidget(task, parent=group.items_container)
            widget.cancel_clicked.connect(self._on_task_cancel_requested)
            group.add_task_widget(task, widget)
            self.item_widgets[task.task_id] = widget

        # 2. Standalone Single Video Task
        else:
            widget = QueueItemWidget(task, parent=self.scroll_content)
            widget.cancel_clicked.connect(self._on_task_cancel_requested)
            self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, widget)
            self.item_widgets[task.task_id] = widget

    def _on_task_updated(self, task: QueueTask):
        if task.playlist_id and task.playlist_id in self.playlist_groups:
            self.playlist_groups[task.playlist_id].update_task(task)
        else:
            widget = self.item_widgets.get(task.task_id)
            if widget:
                widget.update_task(task)

    def _on_task_cancel_requested(self, task_id: str):
        queue_manager.cancel_task(task_id)

    def _cancel_all(self):
        if not self.item_widgets:
            return
        reply = QMessageBox.question(
            self, "Onay", "Kuyruktaki tüm indirmeleri iptal etmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            queue_manager.cancel_all()

    def _clear_finished(self):
        to_remove_tasks = []
        for task_id, widget in self.item_widgets.items():
            task = queue_manager.get_task(task_id)
            if task and task.status in ("completed", "cancelled", "failed"):
                if not task.playlist_id:
                    widget.deleteLater()
                    to_remove_tasks.append(task_id)

        for tid in to_remove_tasks:
            del self.item_widgets[tid]

        # Check completed playlist groups
        to_remove_groups = []
        for pid, group in self.playlist_groups.items():
            all_done = all(t.status in ("completed", "cancelled", "failed") for t in group.tasks.values())
            if all_done:
                group.deleteLater()
                to_remove_groups.append(pid)

        for pid in to_remove_groups:
            del self.playlist_groups[pid]

        if not self.item_widgets and not self.playlist_groups:
            self.empty_label.setVisible(True)
