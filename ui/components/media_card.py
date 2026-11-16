#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Media Card Component
Spacious, modern card displaying thumbnail, title, quality selector, and actions.
"""

import threading
import requests
from io import BytesIO
from typing import Optional
from PIL import Image

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap, QImage, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QFrame, QSizePolicy
)
import qtawesome as qta

from core.metadata import MediaItemMetadata
from services.logger import get_logger

logger = get_logger("media_card")


class ImageSignals(QObject):
    loaded = Signal(QPixmap)


class MediaCard(QFrame):
    """Modern card displaying video preview and spacious configuration controls."""

    download_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.metadata: Optional[MediaItemMetadata] = None
        self.image_signals = ImageSignals()
        self.image_signals.loaded.connect(self._set_thumbnail_pixmap)

        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # 1. Top Section: Thumbnail + Title & Meta Info
        top_section = QHBoxLayout()
        top_section.setSpacing(20)

        # Thumbnail Container
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(260, 146)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("background-color: #0E1626; border-radius: 8px;")
        top_section.addWidget(self.thumb_label)

        # Info Layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        self.title_label = QLabel("Video Başlığı Yükleniyor...")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 17px; font-weight: bold; color: #FFFFFF; line-height: 1.4;")
        info_layout.addWidget(self.title_label)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(14)

        self.uploader_label = QLabel("👤 Kanal")
        self.uploader_label.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 500;")
        meta_row.addWidget(self.uploader_label)

        self.duration_label = QLabel("⏱️ 00:00")
        self.duration_label.setStyleSheet("color: #38BDF8; font-weight: 600; font-size: 13px;")
        meta_row.addWidget(self.duration_label)

        self.platform_badge = QLabel("YOUTUBE")
        self.platform_badge.setStyleSheet(
            "background-color: #1E3A8A; color: #60A5FA; border-radius: 4px; padding: 3px 10px; font-weight: bold; font-size: 11px;"
        )
        meta_row.addWidget(self.platform_badge)
        meta_row.addStretch()
        info_layout.addLayout(meta_row)

        info_layout.addStretch()
        top_section.addLayout(info_layout, stretch=1)
        main_layout.addLayout(top_section)

        # Separator Line
        separator = QFrame()
        separator.setProperty("class", "SeparatorLine")
        main_layout.addWidget(separator)

        # 2. Bottom Section: Controls & Actions (Spacious Layout)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(24)

        # Quality Selection Box
        qual_box = QVBoxLayout()
        qual_box.setSpacing(4)
        qual_lbl = QLabel("İndirme Kalitesi:")
        qual_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        self.quality_combo = QComboBox()
        self.quality_combo.setMinimumWidth(180)
        qual_box.addWidget(qual_lbl)
        qual_box.addWidget(self.quality_combo)
        bottom_row.addLayout(qual_box)

        # Options Box (Checkboxes)
        options_box = QVBoxLayout()
        options_box.setSpacing(6)
        self.sub_check = QCheckBox("Altyazı Göm (Varsa)")
        self.sub_check.setChecked(True)

        self.transcribe_check = QCheckBox("🎙️ Whisper ile Metne / Altyazıya Dönüştür")
        self.transcribe_check.setToolTip("Video indirildikten sonra yerel yapay zeka ile otomatik altyazı (.srt) üretir.")
        
        options_box.addWidget(self.sub_check)
        options_box.addWidget(self.transcribe_check)
        bottom_row.addLayout(options_box)

        bottom_row.addStretch()

        # Add to Queue Button
        self.download_btn = QPushButton(" Kuyruğa Ekle")
        self.download_btn.setIcon(qta.icon("fa5s.download", color="white"))
        self.download_btn.setProperty("class", "PrimaryButton")
        self.download_btn.setFixedHeight(46)
        self.download_btn.setMinimumWidth(170)
        self.download_btn.clicked.connect(self._on_download_clicked)
        bottom_row.addWidget(self.download_btn)

        main_layout.addLayout(bottom_row)

    def set_metadata(self, meta: MediaItemMetadata):
        self.metadata = meta
        self.title_label.setText(meta.title)
        self.uploader_label.setText(f"👤 {meta.uploader}")
        self.duration_label.setText(f"⏱️ {meta.duration_str}")
        self.platform_badge.setText(meta.site_name.upper())

        # Populate qualities
        self.quality_combo.clear()
        for q in meta.available_qualities:
            self.quality_combo.addItem(q)

        # Load Thumbnail in background thread
        self.thumb_label.setText("Yükleniyor...")
        if meta.thumbnail_url:
            threading.Thread(target=self._fetch_thumbnail, args=(meta.thumbnail_url,), daemon=True).start()
        else:
            self.thumb_label.setText("Görsel Yok")

        self.setVisible(True)

    def _fetch_thumbnail(self, url: str):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content)).convert("RGBA")
                img = img.resize((260, 146), Image.Resampling.LANCZOS)
                
                # Convert PIL to QPixmap with rounded corners
                qim = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGBA8888)
                pix = QPixmap.fromImage(qim)

                # Draw rounded rectangle
                rounded = QPixmap(pix.size())
                rounded.fill(Qt.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addRoundedRect(0, 0, pix.width(), pix.height(), 8, 8)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pix)
                painter.end()

                self.image_signals.loaded.emit(rounded)
        except Exception as e:
            logger.warning(f"Could not load thumbnail: {e}")

    def _set_thumbnail_pixmap(self, pixmap: QPixmap):
        self.thumb_label.setPixmap(pixmap)

    def _on_download_clicked(self):
        if not self.metadata:
            return

        selected_quality = self.quality_combo.currentText()
        audio_only = "Ses" in selected_quality or "MP3" in selected_quality

        params = {
            'url': self.metadata.url,
            'title': self.metadata.title,
            'uploader': self.metadata.uploader,
            'duration_str': self.metadata.duration_str,
            'thumbnail_url': self.metadata.thumbnail_url,
            'quality': selected_quality,
            'audio_only': audio_only,
            'embed_subs': self.sub_check.isChecked(),
            'transcribe_after_download': self.transcribe_check.isChecked(),
        }
        self.download_requested.emit(params)
