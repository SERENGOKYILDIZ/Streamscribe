#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Whisper Transcriber Module
Transcribes audio/video to SRT, VTT, and TXT files using Whisper.
"""

import os
import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from core.ffmpeg_helper import FFmpegHelper
from services.logger import get_logger

logger = get_logger("transcriber")


class WhisperTranscriber:
    """Manages audio transcription and subtitle generation via Whisper."""

    def __init__(self, model_size: str = "base", device: str = "auto"):
        self.model_size = model_size
        self.device = device
        self._model = None
        self.is_cancelled = False

    def is_available(self) -> bool:
        """Check if whisper and torch dependencies are functional."""
        try:
            import whisper
            import torch
            return True
        except ImportError:
            return False

    def _load_model(self):
        if self._model is not None:
            return self._model
            
        import whisper
        import torch

        if self.device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = self.device

        logger.info(f"Loading Whisper model '{self.model_size}' on device '{device}'...")
        self._model = whisper.load_model(self.model_size, device=device)
        return self._model

    def cancel(self):
        self.is_cancelled = True

    @staticmethod
    def _format_timestamp(seconds: float, srt: bool = True) -> str:
        """Converts float seconds into SRT (00:00:00,000) or VTT (00:00:00.000) timestamp."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        delim = "," if srt else "."
        return f"{hours:02d}:{minutes:02d}:{secs:02d}{delim}{millis:03d}"

    def write_srt(self, segments: List[Dict[str, Any]], output_path: str):
        """Writes Whisper segments into standard SRT format."""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, start=1):
                start = self._format_timestamp(seg["start"], srt=True)
                end = self._format_timestamp(seg["end"], srt=True)
                text = seg["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def write_txt(self, text: str, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

    def transcribe(self, media_path: str, output_formats: Optional[List[str]] = None,
                   language: Optional[str] = None,
                   progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, str]:
        """
        Transcribes the media file and saves output in requested formats (.srt, .txt).
        Returns a dictionary of generated file paths: {"srt": path, "txt": path}.
        """
        self.is_cancelled = False
        if output_formats is None:
            output_formats = ["srt", "txt"]

        if not self.is_available():
            raise RuntimeError("Whisper or PyTorch is not installed in the environment.")

        if progress_callback:
            progress_callback("Whisper modeli yükleniyor...")

        model = self._load_model()

        if self.is_cancelled:
            raise RuntimeError("Transcription cancelled by user.")

        if progress_callback:
            progress_callback("Ses çözümleniyor (Transkripsiyon sürüyor)...")

        options = {}
        if language and language != "auto":
            options["language"] = language

        result = model.transcribe(media_path, **options)

        base_path, _ = os.path.splitext(media_path)
        generated_files = {}

        if "srt" in output_formats:
            srt_path = f"{base_path}.srt"
            self.write_srt(result["segments"], srt_path)
            generated_files["srt"] = srt_path

        if "txt" in output_formats:
            txt_path = f"{base_path}.txt"
            self.write_txt(result["text"], txt_path)
            generated_files["txt"] = txt_path

        if progress_callback:
            progress_callback("Transkripsiyon tamamlandı!")

        return generated_files
