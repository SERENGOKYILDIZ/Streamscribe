#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe History View
Displays downloaded media history stored in SQLite.
"""

import os
import time
import subprocess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QMessageBox
)
import qtawesome as qta

from services.history_service import history_service, HistoryItem


class HistoryItemWidget(QFrame):
    """Row widget for each historical download item."""

    def __init__(self, item: HistoryItem, on_delete=None, parent=None):
        super().__init__(parent)
        self.item = item
        self.on_delete = on_delete
        self.setProperty("class", "SubCardFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon_name = "fa5s.music" if self.item.format_type == "audio" else "fa5s.video"
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color="#60A5FA").pixmap(24, 24))
        layout.addWidget(icon_lbl)

        # Title & Meta Info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title_lbl = QLabel(self.item.title)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #FFFFFF;")
        text_layout.addWidget(title_lbl)

        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.item.download_date))
        size_mb = self.item.file_size_bytes / (1024 * 1024)
        info_str = f"Tarih: {date_str}  •  Kalite: {self.item.quality or 'Bilinmiyor'}  •  Boyut: {size_mb:.1f} MB"
        info_lbl = QLabel(info_str)
        info_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        text_layout.addWidget(info_lbl)
        layout.addLayout(text_layout, stretch=1)

        # Status badge
        status_lbl = QLabel(self.item.status.upper())
        badge_style = "background-color: #064E3B; color: #34D399;" if self.item.status == "completed" else "background-color: #7F1D1D; color: #F87171;"
        status_lbl.setStyleSheet(f"{badge_style} border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold;")
        layout.addWidget(status_lbl)

        # Open folder button
        if self.item.file_path and os.path.exists(self.item.file_path):
            open_btn = QPushButton()
            open_btn.setIcon(qta.icon("fa5s.folder-open", color="#94A3B8"))
            open_btn.setToolTip("Dosyayı Klasörde Göster")
            open_btn.setProperty("class", "SecondaryButton")
            open_btn.setFixedSize(30, 30)
            open_btn.clicked.connect(self._open_file_folder)
            layout.addWidget(open_btn)

        # Delete from history button
        del_btn = QPushButton()
        del_btn.setIcon(qta.icon("fa5s.trash", color="#F87171"))
        del_btn.setToolTip("Geçmişten Sil")
        del_btn.setProperty("class", "SecondaryButton")
        del_btn.setFixedSize(30, 30)
        del_btn.clicked.connect(self._delete_self)
        layout.addWidget(del_btn)

    def _open_file_folder(self):
        if self.item.file_path and os.path.exists(self.item.file_path):
            folder = os.path.dirname(self.item.file_path)
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])

    def _delete_self(self):
        if self.item.id:
            history_service.delete_item(self.item.id)
            if self.on_delete:
                self.on_delete(self)


class HistoryView(QWidget):
    """View presenting download history with search and cleanup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Row
        header_row = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_lbl = QLabel("İndirme Geçmişi")
        header_lbl.setObjectName("ViewHeaderLabel")
        sub_lbl = QLabel("Daha önce tamamlanan veya indirilen tüm videolar.")
        sub_lbl.setObjectName("ViewSubHeaderLabel")
        header_text_layout.addWidget(header_lbl)
        header_text_layout.addWidget(sub_lbl)
        header_row.addLayout(header_text_layout, stretch=1)

        self.clear_btn = QPushButton(" Geçmişi Temizle")
        self.clear_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"))
        self.clear_btn.setProperty("class", "DangerButton")
        self.clear_btn.clicked.connect(self._clear_all)
        header_row.addWidget(self.clear_btn)

        main_layout.addLayout(header_row)

        # Search Bar
        search_card = QFrame()
        search_card.setProperty("class", "CardFrame")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(12, 10, 12, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Geçmişte ara (video adı veya URL)...")
        self.search_input.textChanged.connect(self._filter_items)
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_card)

        # Scrollable History List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 8, 0, 8)
        self.list_layout.setSpacing(8)

        self.empty_label = QLabel("Henüz bir indirme geçmişi bulunmuyor.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #64748B; font-size: 14px; padding: 60px;")
        self.list_layout.addWidget(self.empty_label)

        self.list_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

        self.widgets = []
        self.refresh_history()

    def refresh_history(self):
        for w in self.widgets:
            w.deleteLater()
        self.widgets.clear()

        items = history_service.get_items(limit=200)
        if not items:
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)
        for item in items:
            w = HistoryItemWidget(item, on_delete=self._on_item_deleted, parent=self.scroll_content)
            self.list_layout.insertWidget(self.list_layout.count() - 1, w)
            self.widgets.append(w)

    def _on_item_deleted(self, widget: HistoryItemWidget):
        if widget in self.widgets:
            self.widgets.remove(widget)
        widget.deleteLater()
        if not self.widgets:
            self.empty_label.setVisible(True)

    def _filter_items(self, text: str):
        query = text.strip().lower()
        visible_count = 0
        for w in self.widgets:
            matches = query in w.item.title.lower() or query in w.item.url.lower()
            w.setVisible(matches)
            if matches:
                visible_count += 1
        self.empty_label.setVisible(visible_count == 0)

    def _clear_all(self):
        if not self.widgets:
            return
        reply = QMessageBox.question(
            self, "Onay", "Tüm indirme geçmişini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history_service.clear_history()
            self.refresh_history()
