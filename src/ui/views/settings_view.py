#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Settings View
Configuration management for paths, concurrency, Whisper, and Udemy authentication.
"""

import os
import time
import tempfile
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QCheckBox, QFrame,
    QScrollArea, QFileDialog, QMessageBox, QTextEdit
)
import qtawesome as qta

from services.config_service import config_service, AppSettings
from config import Config, load_version_from_ini


class SettingsView(QWidget):
    """View managing persistent user preferences and credentials."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Row
        header_row = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_lbl = QLabel("Uygulama Ayarları")
        header_lbl.setObjectName("ViewHeaderLabel")
        sub_lbl = QLabel("İndirme yolları, eşzamanlılık, Whisper ve Udemy oturum ayarları.")
        sub_lbl.setObjectName("ViewSubHeaderLabel")
        header_text_layout.addWidget(header_lbl)
        header_text_layout.addWidget(sub_lbl)
        header_row.addLayout(header_text_layout, stretch=1)

        self.save_btn = QPushButton(" Değişiklikleri Kaydet")
        self.save_btn.setIcon(qta.icon("fa5s.save", color="white"))
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.clicked.connect(self.save_settings)
        header_row.addWidget(self.save_btn)

        main_layout.addLayout(header_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form_layout = QVBoxLayout(content)
        form_layout.setContentsMargins(0, 8, 0, 8)
        form_layout.setSpacing(16)

        # 1. Download Path Card
        path_card = QFrame()
        path_card.setProperty("class", "CardFrame")
        path_layout = QVBoxLayout(path_card)
        path_layout.setSpacing(8)

        card_title = QLabel("📁 İndirme Dizini")
        card_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        path_layout.addWidget(card_title)

        picker_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        picker_row.addWidget(self.path_input, stretch=1)

        browse_btn = QPushButton(" Gözat...")
        browse_btn.setIcon(qta.icon("fa5s.folder", color="#94A3B8"))
        browse_btn.setProperty("class", "SecondaryButton")
        browse_btn.clicked.connect(self._browse_directory)
        picker_row.addWidget(browse_btn)
        path_layout.addLayout(picker_row)
        form_layout.addWidget(path_card)

        # 2. Concurrency & Format Card
        perf_card = QFrame()
        perf_card.setProperty("class", "CardFrame")
        perf_layout = QVBoxLayout(perf_card)
        perf_layout.setSpacing(12)

        perf_title = QLabel("⚡ Performans & İndirme Seçenekleri")
        perf_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        perf_layout.addWidget(perf_title)

        row1 = QHBoxLayout()
        c_label = QLabel("Aynı Anda İndirme Sınırı (Eşzamanlılık):")
        c_label.setStyleSheet("color: #CBD5E1;")
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 5)
        self.concurrent_spin.setValue(2)
        row1.addWidget(c_label)
        row1.addWidget(self.concurrent_spin)
        row1.addStretch()
        perf_layout.addLayout(row1)

        row2 = QHBoxLayout()
        q_label = QLabel("Varsayılan Video Kalitesi:")
        q_label.setStyleSheet("color: #CBD5E1;")
        self.default_quality_combo = QComboBox()
        self.default_quality_combo.addItems(["En İyi", "1080p", "720p", "480p", "Yalnızca Ses (MP3)"])
        row2.addWidget(q_label)
        row2.addWidget(self.default_quality_combo)
        row2.addStretch()
        perf_layout.addLayout(row2)

        form_layout.addWidget(perf_card)

        # 3. Whisper / Altyazı Card
        whisper_card = QFrame()
        whisper_card.setProperty("class", "CardFrame")
        w_layout = QVBoxLayout(whisper_card)
        w_layout.setSpacing(10)

        w_title = QLabel("🎙️ Whisper Yapay Zeka Transkripsiyon")
        w_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        w_layout.addWidget(w_title)

        w_desc = QLabel("Videolardan konuşmayı metne dökmek ve altyazı (.srt) üretmek için yerel Whisper modeli.")
        w_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        w_layout.addWidget(w_desc)

        w_row = QHBoxLayout()
        model_lbl = QLabel("Model Boyutu:")
        model_lbl.setStyleSheet("color: #CBD5E1;")
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems(["tiny", "base", "small", "medium"])
        w_row.addWidget(model_lbl)
        w_row.addWidget(self.whisper_model_combo)
        w_row.addStretch()
        w_layout.addLayout(w_row)

        form_layout.addWidget(whisper_card)

        # 4. Authentication & Udemy Card
        auth_card = QFrame()
        auth_card.setProperty("class", "CardFrame")
        auth_layout = QVBoxLayout(auth_card)
        auth_layout.setSpacing(10)

        auth_title = QLabel("🎓 Giriş Gerektiren Siteler (Udemy vb.)")
        auth_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        auth_layout.addWidget(auth_title)

        auth_desc = QLabel(
            "Udemy gibi oturum isteyen siteler için en güvenilir yöntem: Tarayıcınızdan DevTools (F12) "
            "Network sekmesindeki 'Cookie' istek başlığını kopyalayıp buraya yapıştırmaktır."
        )
        auth_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        auth_desc.setWordWrap(True)
        auth_layout.addWidget(auth_desc)

        self.cookie_header_input = QTextEdit()
        self.cookie_header_input.setPlaceholderText("Örn: client_id=...; access_token=...; dj_session_id=...")
        self.cookie_header_input.setFixedHeight(75)
        auth_layout.addWidget(self.cookie_header_input)

        cookie_btn_row = QHBoxLayout()
        self.apply_cookie_btn = QPushButton(" Çerez Başlığını Doğrula & Uygula")
        self.apply_cookie_btn.setIcon(qta.icon("fa5s.check", color="white"))
        self.apply_cookie_btn.setProperty("class", "SecondaryButton")
        self.apply_cookie_btn.clicked.connect(self._apply_raw_cookie_header)
        cookie_btn_row.addWidget(self.apply_cookie_btn)

        cookie_btn_row.addStretch()

        b_lbl = QLabel("Veya Tarayıcı Çerezi:")
        b_lbl.setStyleSheet("color: #CBD5E1;")
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["none", "chrome", "firefox", "edge", "brave"])
        cookie_btn_row.addWidget(b_lbl)
        cookie_btn_row.addWidget(self.browser_combo)
        auth_layout.addLayout(cookie_btn_row)

        form_layout.addWidget(auth_card)

        # 5. About / Version Card
        about_card = QFrame()
        about_card.setProperty("class", "CardFrame")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(18, 14, 18, 14)
        about_layout.setSpacing(6)

        live_ver = load_version_from_ini()
        about_title = QLabel(f"ℹ️ {Config.APP_NAME} — v{live_ver}")
        about_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #38BDF8;")
        about_layout.addWidget(about_title)

        about_dev = QLabel(f"Geliştirici: {Config.APP_AUTHOR}  •  Motor: yt-dlp + faster-whisper (CTranslate2)")
        about_dev.setStyleSheet("color: #94A3B8; font-size: 12px;")
        about_layout.addWidget(about_dev)

        form_layout.addWidget(about_card)

        form_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def load_settings(self):
        s = config_service.settings
        self.path_input.setText(s.download_dir)
        self.concurrent_spin.setValue(s.max_concurrent_downloads)
        
        idx = self.default_quality_combo.findText(s.default_quality)
        if idx >= 0:
            self.default_quality_combo.setCurrentIndex(idx)

        w_idx = self.whisper_model_combo.findText(s.whisper_model)
        if w_idx >= 0:
            self.whisper_model_combo.setCurrentIndex(w_idx)

        b_idx = self.browser_combo.findText(s.cookie_browser)
        if b_idx >= 0:
            self.browser_combo.setCurrentIndex(b_idx)

    def _browse_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "İndirme Klasörü Seç", self.path_input.text())
        if folder:
            self.path_input.setText(folder)

    def _apply_raw_cookie_header(self):
        raw = self.cookie_header_input.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir çerez başlığı yapıştırın.")
            return

        pairs = []
        for part in raw.split(';'):
            part = part.strip()
            if '=' in part:
                name, _, val = part.partition('=')
                if name.strip():
                    pairs.append((name.strip(), val.strip()))

        if not pairs:
            QMessageBox.warning(self, "Geçersiz Format", "Geçerli çerez çifti bulunamadı.")
            return

        # Write to temporary cookies.txt
        expiry = int(time.time()) + 365 * 24 * 3600
        lines = ["# Netscape HTTP Cookie File"]
        for name, value in pairs:
            lines.append(f".udemy.com\tTRUE\t/\tTRUE\t{expiry}\t{name}\t{value}")

        fd, path = tempfile.mkstemp(prefix="streamscribe_cookies_", suffix=".txt")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

        config_service.update(custom_cookie_file=path)
        QMessageBox.information(self, "Başarılı", f"{len(pairs)} adet çerez başarıyla işlendi ve kaydedildi!")

    def save_settings(self):
        config_service.update(
            download_dir=self.path_input.text(),
            max_concurrent_downloads=self.concurrent_spin.value(),
            default_quality=self.default_quality_combo.currentText(),
            whisper_model=self.whisper_model_combo.currentText(),
            cookie_browser=self.browser_combo.currentText()
        )
        QMessageBox.information(self, "Bilgi", "Ayarlar başarıyla kaydedildi!")
