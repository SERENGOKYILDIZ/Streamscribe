#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Download Engine
Modern yt-dlp wrapper supporting cancel, progress streaming and format conversion.
"""

import os
import re
import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
import yt_dlp

from core.ffmpeg_helper import FFmpegHelper
from core.metadata import MetadataExtractor
from services.logger import get_logger

logger = get_logger("engine")


class DownloadCancelledException(Exception):
    """Raised when user cancels a running download."""
    pass


class DownloadEngine:
    """Core video and audio download engine built on yt-dlp."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.is_cancelled = False
        self._current_filename: Optional[str] = None
        self._downloaded_bytes: int = 0
        self._total_bytes: int = 0

    def cancel(self):
        """Signals the active download to abort."""
        self.is_cancelled = True
        logger.info("Cancellation requested for current download task.")

    def _progress_hook(self, d: Dict[str, Any], progress_cb: Optional[Callable[[Dict[str, Any]], None]]):
        if self.is_cancelled:
            raise DownloadCancelledException("Download cancelled by user.")

        status = d.get('status')
        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            speed = d.get('speed') or 0
            eta = d.get('eta') or 0
            percent = (downloaded / total * 100) if total > 0 else 0.0

            if progress_cb:
                progress_cb({
                    'status': 'downloading',
                    'percent': percent,
                    'downloaded_bytes': downloaded,
                    'total_bytes': total,
                    'speed': speed,
                    'eta': eta,
                    'filename': d.get('filename')
                })

        elif status == 'finished':
            self._current_filename = d.get('filename')
            if progress_cb:
                progress_cb({
                    'status': 'processing',
                    'percent': 100.0,
                    'filename': self._current_filename
                })

    def download(self, url: str, quality: str = "1080p", audio_only: bool = False,
                 embed_subs: bool = False, sub_langs: str = "en,tr",
                 cookie_file: Optional[str] = None, cookies_from_browser: Optional[str] = None,
                 progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
        """Executes download for a single video or audio file."""
        self.is_cancelled = False
        url = MetadataExtractor.normalize_url(url)
        ffmpeg_bin = FFmpegHelper.get_ffmpeg_path()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        out_template = os.path.join(self.output_dir, "%(title).180s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            'outtmpl': out_template,
            'ffmpeg_location': ffmpeg_bin,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 5,
            'fragment_retries': 3,
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback)],
            'postprocessor_hooks': [lambda d: None],
        }

        if cookie_file and os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file
        elif cookies_from_browser and cookies_from_browser != "none":
            ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)

        if audio_only or quality == "Yalnızca Ses (MP3)":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {'key': 'FFmpegMetadata'},
                ],
            })
        else:
            # Universal Compatibility: Prefer H.264 (AVC) + AAC so Windows Media Player / Movies & TV can play directly
            height_match = re.search(r'(\d+)p', quality)
            max_height = int(height_match.group(1)) if height_match else None

            if max_height:
                format_spec = (
                    f"bestvideo[height<={max_height}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
                    f"bestvideo[height<={max_height}][vcodec^=avc1]+bestaudio[ext=m4a]/"
                    f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/"
                    f"bestvideo[height<={max_height}]+bestaudio/"
                    f"best[height<={max_height}]/best"
                )
            else:
                format_spec = (
                    "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
                    "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/"
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo+bestaudio/best"
                )

            ydl_opts.update({
                'format': format_spec,
                'format_sort': ['vcodec:h264', 'res', 'fps', 'acodec:m4a'],
                'merge_output_format': 'mp4',
                'postprocessors': [{'key': 'FFmpegMetadata'}],
            })

            # Subtitle options with automatic format conversion for MP4 container compatibility
            if embed_subs:
                langs = [l.strip() for l in sub_langs.split(",") if l.strip()]
                ydl_opts.update({
                    'writesubtitles': True,
                    'writeautomaticsub': False,  # Avoid aggressive YouTube 429 rate limits on auto-captions
                    'subtitleslangs': langs,
                })
                ydl_opts['postprocessors'].extend([
                    {'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'},
                    {'key': 'FFmpegEmbedSubtitle'},
                ])

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Identify true final file path on disk (resolving merges)
                final_filename = ydl.prepare_filename(info)
                if 'requested_downloads' in info and info['requested_downloads']:
                    final_filename = info['requested_downloads'][0].get('filepath') or final_filename

                base, ext = os.path.splitext(final_filename)
                
                # Check for audio conversion extension change
                if audio_only or quality == "Yalnızca Ses (MP3)":
                    mp3_path = f"{base}.mp3"
                    if os.path.exists(mp3_path):
                        return mp3_path
                else:
                    mp4_path = f"{base}.mp4"
                    if os.path.exists(mp4_path):
                        return mp4_path
                        
                return final_filename
        except DownloadCancelledException:
            logger.info("Download explicitly cancelled by user.")
            raise
        except Exception as e:
            err_str = str(e)
            # If download failed due to subtitles (429 Too Many Requests, unavailable subs, etc.), fallback to clean video download
            if embed_subs and ("subtitles" in err_str.lower() or "429" in err_str):
                logger.warning(
                    f"Altyazı indirilemedi ({err_str[:80]}...). Video altyazısız olarak indirilmeye devam ediliyor."
                )
                return self.download(
                    url=url,
                    quality=quality,
                    audio_only=audio_only,
                    embed_subs=False,
                    sub_langs=sub_langs,
                    cookie_file=cookie_file,
                    cookies_from_browser=cookies_from_browser,
                    progress_callback=progress_callback
                )

            logger.error(f"Download failed: {str(e)}")
            raise
