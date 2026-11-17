#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Queue Item Widget
Interactive card displaying live download/transcription progress, speed, ETA, and actions.
"""

import os
import subprocess
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QFrame
)
import qtawesome as qta

from core.queue_manager import QueueTask, queue_manager


class QueueItemWidget(QFrame):
    """Visual representation of a single task in the download queue."""

    cancel_clicked = Signal(str)

    def __init__(self, task: QueueTask, parent=None):
        super().__init__(parent)
        self.task_id = task.task_id
        self.setProperty("class", "CardFrame")
        self._setup_ui(task)
        self.update_task(task)

    def _setup_ui(self, task: QueueTask):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Header: Title + Status Badge + Actions
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.title_label = QLabel(task.title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #FFFFFF; line-height: 1.3;")
        top_row.addWidget(self.title_label, stretch=1)

        self.status_badge = QLabel("Kuyrukta")
        self.status_badge.setStyleSheet(
            "background-color: #243144; color: #CBD5E1; border-radius: 4px; padding: 4px 10px; font-size: 11px; font-weight: bold;"
        )
        top_row.addWidget(self.status_badge)

        # Action Buttons
        self.folder_btn = QPushButton()
        self.folder_btn.setIcon(qta.icon("fa5s.folder-open", color="#60A5FA"))
        self.folder_btn.setToolTip("İndirilen Dosyayı Aç")
        self.folder_btn.setProperty("class", "SecondaryButton")
        self.folder_btn.setFixedSize(34, 34)
        self.folder_btn.setVisible(False)
        self.folder_btn.clicked.connect(self._open_folder)
        top_row.addWidget(self.folder_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setIcon(qta.icon("fa5s.times", color="#F87171"))
        self.cancel_btn.setToolTip("İptal Et")
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.setFixedSize(34, 34)
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.task_id))
        top_row.addWidget(self.cancel_btn)

        layout.addLayout(top_row)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Bottom info row: Speed, ETA, Size
        bottom_row = QHBoxLayout()
        self.speed_label = QLabel("Hız: --")
        self.speed_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        bottom_row.addWidget(self.speed_label)

        self.eta_label = QLabel("Kalan Süre: --")
        self.eta_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        bottom_row.addWidget(self.eta_label)

        bottom_row.addStretch()

        self.size_label = QLabel("0 MB / 0 MB")
        self.size_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        bottom_row.addWidget(self.size_label)

        layout.addLayout(bottom_row)

    def update_task(self, task: QueueTask):
        self.title_label.setText(task.title)
        self.progress_bar.setValue(int(task.percent))

        # Size formatting
        downloaded_mb = task.downloaded_bytes / (1024 * 1024)
        total_mb = task.total_bytes / (1024 * 1024)
        if total_mb > 0:
            self.size_label.setText(f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB ({task.percent:.1f}%)")

        # Speed formatting
        speed_mb = task.speed_bytes_sec / (1024 * 1024)
        if speed_mb > 0:
            self.speed_label.setText(f"Hız: {speed_mb:.2f} MB/s")

        # ETA formatting
        if task.eta_seconds > 0:
            m, s = divmod(task.eta_seconds, 60)
            self.eta_label.setText(f"Kalan: {m:02d}:{s:02d}")

        # Status badge update
        if task.status == "downloading":
            self.status_badge.setText(f"İndiriliyor %{int(task.percent)}")
            self.status_badge.setStyleSheet(
                "background-color: #1E3A8A; color: #60A5FA; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 11px;"
            )
        elif task.status == "transcribing":
            self.status_badge.setText("🎙️ Transkripsiyon (Whisper)...")
            self.status_badge.setStyleSheet(
                "background-color: #581C87; color: #C084FC; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 11px;"
            )
            self.speed_label.setText("Yapay Zeka Altyazı Üretiyor")
            self.eta_label.setText("")
        elif task.status == "completed":
            self.status_badge.setText("Tamamlandı")
            self.status_badge.setStyleSheet(
                "background-color: #064E3B; color: #34D399; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 11px;"
            )
            self.cancel_btn.setVisible(False)
            self.folder_btn.setVisible(True)
            self.speed_label.setText("İndirme bitti")
            self.eta_label.setText("")
        elif task.status == "cancelled":
            self.status_badge.setText("İptal Edildi")
            self.status_badge.setStyleSheet(
                "background-color: #7F1D1D; color: #FCA5A5; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 11px;"
            )
            self.cancel_btn.setVisible(False)
        elif task.status == "failed":
            self.status_badge.setText("Başarısız")
            self.status_badge.setStyleSheet(
                "background-color: #7F1D1D; color: #F87171; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 11px;"
            )
            self.cancel_btn.setVisible(False)
            if task.error_message:
                self.speed_label.setText(f"Hata: {task.error_message[:40]}...")

    def _open_folder(self):
        task = queue_manager.get_task(self.task_id)
        if not task or not task.final_filepath:
            return
        folder = os.path.dirname(task.final_filepath)
        if os.path.exists(folder):
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])
