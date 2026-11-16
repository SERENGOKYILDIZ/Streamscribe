#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Playlist Card Component
Displays playlist item selections and bulk download actions.
"""

from typing import List, Dict, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QScrollArea, QComboBox
)
import qtawesome as qta

from core.metadata import MediaItemMetadata


class PlaylistItemRow(QFrame):
    """Row widget for each video inside the playlist selector."""
    
    def __init__(self, item: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.item_data = item
        self.setProperty("class", "SubCardFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self.check_box = QCheckBox()
        self.check_box.setChecked(True)
        layout.addWidget(self.check_box)

        index_lbl = QLabel(f"#{self.item_data.get('index', 1)}")
        index_lbl.setStyleSheet("color: #64748B; font-weight: bold; min-width: 30px;")
        layout.addWidget(index_lbl)

        title_lbl = QLabel(self.item_data.get('title', 'Video'))
        title_lbl.setStyleSheet("color: #F8FAFC; font-weight: 500;")
        layout.addWidget(title_lbl, stretch=1)

        dur_lbl = QLabel(self.item_data.get('duration', '00:00'))
        dur_lbl.setStyleSheet("color: #38BDF8; font-size: 11px;")
        layout.addWidget(dur_lbl)

    def is_selected(self) -> bool:
        return self.check_box.isChecked()

    def set_selected(self, val: bool):
        self.check_box.setChecked(val)


class PlaylistCard(QFrame):
    """Card containing playlist overview and scrollable video selection list."""

    bulk_download_requested = Signal(list, dict)  # Emits (selected_items, options)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.metadata = None
        self.row_widgets: List[PlaylistItemRow] = []
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header: Playlist Title and Total Count
        header_row = QHBoxLayout()
        self.title_label = QLabel("Oynatma Listesi")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        header_row.addWidget(self.title_label, stretch=1)

        self.count_badge = QLabel("0 Video")
        self.count_badge.setStyleSheet(
            "background-color: #1E3A8A; color: #60A5FA; border-radius: 4px; padding: 2px 8px; font-weight: bold; font-size: 12px;"
        )
        header_row.addWidget(self.count_badge)
        main_layout.addLayout(header_row)

        # Controls Row (Select All, Deselect All, Quality ComboBox, Options)
        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)

        self.select_all_btn = QPushButton("Tümünü Seç")
        self.select_all_btn.setProperty("class", "SecondaryButton")
        self.select_all_btn.clicked.connect(lambda: self._set_all_selected(True))
        controls_row.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Seçimi Kaldır")
        self.deselect_all_btn.setProperty("class", "SecondaryButton")
        self.deselect_all_btn.clicked.connect(lambda: self._set_all_selected(False))
        controls_row.addWidget(self.deselect_all_btn)

        controls_row.addStretch()

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["En İyi", "1080p", "720p", "480p", "Yalnızca Ses (MP3)"])
        controls_row.addWidget(self.quality_combo)

        self.transcribe_check = QCheckBox("Whisper ile Altyazı/Metin Çıkar")
        controls_row.addWidget(self.transcribe_check)

        self.add_all_btn = QPushButton(" Seçilenleri Kuyruğa Ekle")
        self.add_all_btn.setIcon(qta.icon("fa5s.download", color="white"))
        self.add_all_btn.setProperty("class", "PrimaryButton")
        self.add_all_btn.setFixedHeight(36)
        self.add_all_btn.clicked.connect(self._on_bulk_add_clicked)
        controls_row.addWidget(self.add_all_btn)

        main_layout.addLayout(controls_row)

        # Scrollable list for videos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(260)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def set_metadata(self, meta: MediaItemMetadata):
        self.metadata = meta
        self.title_label.setText(meta.title)
        self.count_badge.setText(f"{meta.playlist_count} Video")

        # Clear existing rows
        for row in self.row_widgets:
            row.deleteLater()
        self.row_widgets.clear()

        # Add new rows
        for item in meta.playlist_items:
            row = PlaylistItemRow(item, self.scroll_content)
            self.scroll_layout.addWidget(row)
            self.row_widgets.append(row)

        self.setVisible(True)

    def _set_all_selected(self, val: bool):
        for row in self.row_widgets:
            row.set_selected(val)

    def _on_bulk_add_clicked(self):
        selected_items = [r.item_data for r in self.row_widgets if r.is_selected()]
        if not selected_items:
            return

        quality = self.quality_combo.currentText()
        options = {
            'quality': quality,
            'audio_only': "Ses" in quality or "MP3" in quality,
            'embed_subs': True,
            'transcribe_after_download': self.transcribe_check.isChecked(),
        }
        self.bulk_download_requested.emit(selected_items, options)
