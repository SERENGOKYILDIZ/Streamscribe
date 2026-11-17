#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Metadata Extractor Module
Extracts video and playlist metadata cleanly using yt-dlp.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import yt_dlp

from core.ffmpeg_helper import FFmpegHelper
from services.logger import get_logger

logger = get_logger("metadata")


@dataclass
class VideoFormatOption:
    format_id: str
    resolution: str          # e.g., "1080p", "720p", "audio_only"
    height: int              # e.g., 1080
    ext: str                 # "mp4", "webm", "m4a"
    filesize_approx: int = 0 # in bytes
    has_audio: bool = True
    has_video: bool = True


@dataclass
class MediaItemMetadata:
    url: str
    title: str
    duration_seconds: int = 0
    duration_str: str = "00:00"
    uploader: str = "Bilinmeyen Kanal"
    thumbnail_url: str = ""
    is_playlist: bool = False
    playlist_count: int = 0
    playlist_items: List[Dict[str, Any]] = field(default_factory=list)
    available_qualities: List[str] = field(default_factory=list)
    subtitles: List[str] = field(default_factory=list)
    raw_info: Dict[str, Any] = field(default_factory=dict)
    site_name: str = "Unknown"


class MetadataExtractor:
    """Extracts metadata from YouTube, Udemy, and 1000+ supported sites."""

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalizes Udemy or other specialized URLs."""
        url = url.strip()
        # Udemy lecture URL fix for yt-dlp extractor
        lecture_match = re.match(
            r'https?://(?:[^/]+\.)?udemy\.com/course/([^/?#&]+)/learn/lecture/(\d+)',
            url
        )
        if lecture_match:
            slug, lecture_id = lecture_match.groups()
            return f'https://www.udemy.com/{slug}/learn/v4/t/lecture/{lecture_id}'

        course_match = re.match(r'https?://(?:[^/]+\.)?udemy\.com/course/([^/?#&]+)/?$', url)
        if course_match:
            slug = course_match.group(1)
            return f'https://www.udemy.com/{slug}/'

        return url

    @classmethod
    def format_duration(cls, seconds: int) -> str:
        if not seconds:
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @classmethod
    def extract_info(cls, url: str, cookie_file: Optional[str] = None, 
                     cookies_from_browser: Optional[str] = None) -> MediaItemMetadata:
        """Extracts metadata without downloading media."""
        url = cls.normalize_url(url)
        ffmpeg_bin = FFmpegHelper.get_ffmpeg_path()

        ydl_opts: Dict[str, Any] = {
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_bin,
        }

        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file
        elif cookies_from_browser and cookies_from_browser != "none":
            ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise ValueError("Video veya oynatma listesi bilgisi alınamadı.")

        is_playlist = 'entries' in info and bool(info.get('entries'))
        extractor_key = info.get('extractor_key', 'Generic')

        if is_playlist:
            entries = list(info.get('entries', []))
            first_entry = entries[0] if entries else {}
            title = info.get('title') or "Oynatma Listesi"
            uploader = info.get('uploader') or first_entry.get('uploader') or "Çeşitli"
            thumb = info.get('thumbnails', [{}])[-1].get('url', '') if info.get('thumbnails') else first_entry.get('thumbnail', '')
            
            playlist_items = []
            for idx, entry in enumerate(entries, 1):
                playlist_items.append({
                    'index': idx,
                    'title': entry.get('title', f'Video #{idx}'),
                    'url': entry.get('url') or entry.get('webpage_url', ''),
                    'duration': cls.format_duration(entry.get('duration', 0)),
                    'id': entry.get('id', '')
                })

            return MediaItemMetadata(
                url=url,
                title=title,
                uploader=uploader,
                thumbnail_url=thumb,
                is_playlist=True,
                playlist_count=len(entries),
                playlist_items=playlist_items,
                available_qualities=["En İyi", "1080p", "720p", "480p", "Yalnızca Ses (MP3)"],
                site_name=extractor_key,
                raw_info=info
            )

        # Single video analysis
        title = info.get('title', 'İsimsiz Video')
        duration = info.get('duration', 0)
        uploader = info.get('uploader') or info.get('channel', 'Bilinmeyen Kanal')
        thumb = info.get('thumbnail', '')

        # Qualities
        formats = info.get('formats', [])
        heights = set()
        for f in formats:
            h = f.get('height')
            if h and isinstance(h, int):
                heights.add(h)

        sorted_heights = sorted(list(heights), reverse=True)
        qualities = [f"{h}p" for h in sorted_heights if h >= 144]
        if not qualities:
            qualities = ["En İyi Kalite", "720p", "360p"]
        qualities.append("Yalnızca Ses (MP3)")

        # Subtitles
        subtitles_dict = info.get('subtitles', {}) or {}
        auto_subs = info.get('automatic_captions', {}) or {}
        available_subs = list(set(list(subtitles_dict.keys()) + list(auto_subs.keys())))

        return MediaItemMetadata(
            url=url,
            title=title,
            duration_seconds=duration,
            duration_str=cls.format_duration(duration),
            uploader=uploader,
            thumbnail_url=thumb,
            is_playlist=False,
            playlist_count=1,
            available_qualities=qualities,
            subtitles=available_subs,
            site_name=extractor_key,
            raw_info=info
        )
