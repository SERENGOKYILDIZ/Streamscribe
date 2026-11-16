#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Downloader View
URL analysis, metadata presentation and queue submission.
"""

import threading
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QApplication, QMessageBox
)
import qtawesome as qta

from core.metadata import MetadataExtractor, MediaItemMetadata
from core.queue_manager import QueueTask, queue_manager
from ui.components.media_card import MediaCard
from ui.components.playlist_card import PlaylistCard
from services.config_service import config_service
from services.logger import get_logger

logger = get_logger("downloader_view")


class AnalysisSignals(QObject):
    success = Signal(object)
    failed = Signal(str)


class DownloaderView(QWidget):
    """Main view for entering URLs and previewing video/playlist options."""

    navigate_to_queue = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = AnalysisSignals()
        self.signals.success.connect(self._on_analysis_success)
        self.signals.failed.connect(self._on_analysis_failed)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Titles
        header_lbl = QLabel("Video & Oynatma Listesi İndirici")
        header_lbl.setObjectName("ViewHeaderLabel")
        sub_lbl = QLabel("YouTube, Udemy ve 1000'den fazla siteden video veya ses indirin, Whisper ile altyazı çıkarın.")
        sub_lbl.setObjectName("ViewSubHeaderLabel")
        main_layout.addWidget(header_lbl)
        main_layout.addWidget(sub_lbl)

        # URL Input Bar Card
        input_card = QFrame()
        input_card.setProperty("class", "CardFrame")
        input_layout = QHBoxLayout(input_card)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(14)

        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setFixedHeight(44)
        self.url_input.setPlaceholderText("Video veya oynatma listesi bağlantısını buraya yapıştırın (https://...)")
        self.url_input.returnPressed.connect(self.start_analysis)
        input_layout.addWidget(self.url_input, stretch=1)

        # Paste Button
        self.paste_btn = QPushButton(" Panodan Yapıştır")
        self.paste_btn.setFixedHeight(44)
        self.paste_btn.setIcon(qta.icon("fa5s.paste", color="#94A3B8"))
        self.paste_btn.setProperty("class", "SecondaryButton")
        self.paste_btn.clicked.connect(self._paste_clipboard)
        input_layout.addWidget(self.paste_btn)

        # Analyze Button
        self.analyze_btn = QPushButton(" Analiz Et")
        self.analyze_btn.setFixedHeight(44)
        self.analyze_btn.setIcon(qta.icon("fa5s.search", color="white"))
        self.analyze_btn.setProperty("class", "PrimaryButton")
        self.analyze_btn.clicked.connect(self.start_analysis)
        input_layout.addWidget(self.analyze_btn)

        main_layout.addWidget(input_card)

        # Loading / Status Label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #38BDF8; font-size: 13px; font-weight: 500;")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)

        # Scrollable Area for Result Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.cards_layout = QVBoxLayout(content)
        self.cards_layout.setContentsMargins(0, 8, 0, 8)
        self.cards_layout.setSpacing(16)

        # Media Card (Single Video)
        self.media_card = MediaCard()
        self.media_card.download_requested.connect(self._on_single_download_requested)
        self.cards_layout.addWidget(self.media_card)

        # Playlist Card
        self.playlist_card = PlaylistCard()
        self.playlist_card.bulk_download_requested.connect(self._on_bulk_download_requested)
        self.cards_layout.addWidget(self.playlist_card)

        self.cards_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _paste_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self.start_analysis()

    def start_analysis(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir video veya oynatma listesi URL'si girin.")
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText(" İnceleniyor...")
        self.status_label.setText("🔄 Video ve akış bilgileri alınıyor, lütfen bekleyin...")
        self.status_label.setVisible(True)
        self.media_card.setVisible(False)
        self.playlist_card.setVisible(False)

        settings = config_service.settings
        threading.Thread(
            target=self._async_analyze,
            args=(url, settings.custom_cookie_file, settings.cookie_browser),
            daemon=True
        ).start()

    def _async_analyze(self, url: str, cookie_file: str, cookie_browser: str):
        try:
            meta = MetadataExtractor.extract_info(
                url=url,
                cookie_file=cookie_file or None,
                cookies_from_browser=cookie_browser if cookie_browser != "none" else None
            )
            self.signals.success.emit(meta)
        except Exception as e:
            self.signals.failed.emit(str(e))

    def _on_analysis_success(self, meta: MediaItemMetadata):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText(" Analiz Et")
        self.status_label.setVisible(False)

        if meta.is_playlist:
            self.playlist_card.set_metadata(meta)
            self.media_card.setVisible(False)
        else:
            self.media_card.set_metadata(meta)
            self.playlist_card.setVisible(False)

    def _on_analysis_failed(self, error_msg: str):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText(" Analiz Et")
        self.status_label.setText(f"❌ Bilgi alınamadı: {error_msg}")
        self.status_label.setStyleSheet("color: #F87171; font-size: 13px;")
        QMessageBox.critical(self, "Analiz Hatası", f"Video bilgileri alınırken hata oluştu:\n\n{error_msg}")

    def _on_single_download_requested(self, params: dict):
        task = QueueTask(
            url=params['url'],
            title=params['title'],
            uploader=params.get('uploader', ''),
            thumbnail_url=params.get('thumbnail_url', ''),
            duration_str=params.get('duration_str', ''),
            quality=params['quality'],
            audio_only=params['audio_only'],
            embed_subs=params.get('embed_subs', True),
            transcribe_after_download=params.get('transcribe_after_download', False)
        )
        queue_manager.add_task(task)
        self.navigate_to_queue.emit()

    def _on_bulk_download_requested(self, items: list, options: dict):
        for item in items:
            task = QueueTask(
                url=item.get('url', ''),
                title=item.get('title', 'Video'),
                duration_str=item.get('duration', ''),
                quality=options['quality'],
                audio_only=options['audio_only'],
                embed_subs=options['embed_subs'],
                transcribe_after_download=options['transcribe_after_download']
            )
            queue_manager.add_task(task)

        self.navigate_to_queue.emit()
