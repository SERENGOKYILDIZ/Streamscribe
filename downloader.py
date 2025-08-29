#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Optimized Downloader Module
Enhanced YouTube downloader with improved performance and error handling
"""

import os
import threading
import re
import json
import time
from typing import Callable, Optional, Dict, Any, List
from pathlib import Path
import requests
from yt_dlp import YoutubeDL

from config import config
from logger import get_logger

logger = get_logger('downloader')


class OptimizedYouTubeDownloader:
    """Optimized YouTube video/playlist downloader class"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.DEFAULT_OUTPUT_DIR
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        self._is_downloading = False
        self._download_thread: Optional[threading.Thread] = None
        
        # Performance optimizations
        self._session = requests.Session()
        self._session.headers.update(config.REQUEST_HEADERS)
        
        # Cache for video info
        self._video_info_cache: Dict[str, Dict[str, Any]] = {}
        self._thumbnail_cache: Dict[str, bytes] = {}
        
        # Set FFmpeg path
        self.ffmpeg_path = config.get_ffmpeg_path()
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        pass
    
    def set_progress_callback(self, callback: Callable):
        """Set callback function for download progress updates"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def set_error_callback(self, callback: Callable):
        """Set callback function for error handling"""
        self.error_callback = callback
    
    def _progress_hook(self, d: Dict[str, Any]):
        """Optimized progress hook for yt-dlp"""
        try:
            if not self.progress_callback:
                return
            
            status = d.get('status', '')
            
            if status == 'downloading':
                # Extract progress data efficiently with better fallbacks
                progress_data = {
                    'status': 'downloading',
                    '_percent_str': d.get('_percent_str', '0%'),
                    'speed': d.get('speed', 0),
                    'eta': d.get('eta', 0),
                    'downloaded_bytes': d.get('downloaded_bytes', 0),
                    'total_bytes': d.get('total_bytes', 0),
                    'total_bytes_estimate': d.get('total_bytes_estimate', 0)
                }
                
                # Log progress data for debugging
                logger.debug(f"Progress data: {progress_data}")
                
                self.progress_callback(progress_data)
                
            elif status == 'finished':
                if self.status_callback:
                    self.status_callback("İşleniyor...")
                
                self.progress_callback({
                    'status': 'finished',
                    'percent': '100%',
                    '_percent_str': '100%',
                    'speed': 0,
                    'eta': 0
                })
                
            elif status == 'info':
                # Log format selection and quality information
                info_msg = d.get('message', '')
                if 'format' in info_msg.lower() or 'resolution' in info_msg.lower():
                    print(f"🎬 Format Seçimi: {info_msg}")
                elif 'downloading' in info_msg.lower():
                    print(f"📥 İndiriliyor: {info_msg}")
                
        except Exception as e:
            logger.error(f"Progress hook error: {e}")
    
    def _build_format_string(self, max_height: int, prefer_mp4: bool) -> str:
        """Build optimized format string for video quality with audio"""
        try:
            if prefer_mp4:
                # Force higher quality - more aggressive selection
                format_string = f"bestvideo[height>={max_height-180}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>={max_height-180}]+bestaudio/best[height>={max_height-180}][ext=mp4]+bestaudio/best[height>={max_height-180}]+bestaudio/best+bestaudio"
            else:
                # Force higher quality - more aggressive selection
                format_string = f"bestvideo[height>={max_height-180}]+bestaudio/bestvideo[height>={max_height-180}]+bestaudio/best[height>={max_height-180}]+bestaudio/best+bestaudio"
            
            print(f"🔍 Oluşturulan Format String: {format_string}")
            return format_string
            
        except Exception as e:
            logger.error(f"Format string building error: {e}")
            # Fallback to best format that includes audio - CRITICAL FOR AUDIO
            fallback = f"best[height>={max_height-180}]+bestaudio/best+bestaudio"
            print(f"⚠️ Fallback Format String: {fallback}")
            return fallback
    
    def _get_optimized_ydl_options(self, audio_only: bool, max_height: int, 
                                 prefer_mp4: bool, no_playlist: bool, 
                                 include_subs: bool, sub_langs: str, 
                                 auto_subs: bool) -> Dict[str, Any]:
        """Get optimized yt-dlp options"""
        try:
            options = {
                "outtmpl": os.path.join(self.output_dir, "%(title).200s [%(id)s].%(ext)s"),
                "progress_hooks": [self._progress_hook],
                "noplaylist": no_playlist,
                "quiet": False,
                "no_warnings": False,
                "concurrent_fragment_downloads": 4,
                "retries": 10,
                "ffmpeg_location": self.ffmpeg_path,
                "socket_timeout": config.TIMEOUT_LONG,
                "fragment_retries": 3,
                "extractor_retries": 3,
                "http_chunk_size": 10485760,  # 10MB chunks
                "merge_output_format": "mp4" if prefer_mp4 else "mkv",
                # Quality optimization settings - force higher quality
                "format_sort": ["res", "fps", "codec:h264", "codec:vp9", "codec:av1"],
                "format_sort_force": True,  # Force strict sorting
                "prefer_free_formats": False,  # Don't prefer free formats
                "check_formats": True,  # Enable format checking
            }
            
            if audio_only:
                options.update({
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio", 
                            "preferredcodec": "mp3", 
                            "preferredquality": "192"
                        },
                        {"key": "FFmpegMetadata"},
                    ],
                })
            else:
                # For video downloads, use enhanced format string with audio guarantee
                format_string = self._build_format_string(max_height, prefer_mp4)
                pass
                
                # Add fallback format to ensure audio is always included
                fallback_format = f"best[height<={max_height}]+bestaudio/best+bestaudio"
                pass
                
                # Use the generated format string
                options["format"] = format_string
                # For video downloads, ensure audio is preserved and merged properly
                options.setdefault("postprocessors", []).extend([
                    # Use FFmpegVideoConvertor to ensure video+audio merge
                    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4" if prefer_mp4 else "mkv"},
                    {"key": "FFmpegMetadata"}
                ])
                # Critical audio preservation settings
                options["keepvideo"] = False  # Don't keep separate video file
                options["keepaudio"] = False  # Don't keep separate audio file
                options["audioformat"] = "best"  # Best audio quality
                options["audioquality"] = "0"  # Best audio quality (0 = best)
                options["extractaudio"] = False  # Don't extract audio separately
                options["prefer_ffmpeg"] = True  # Prefer FFmpeg for processing
                # Force audio stream inclusion
                options["audio_multistreams"] = True  # Allow multiple audio streams
                options["audio_preference"] = "best"  # Prefer best audio
                # Additional audio preservation for single video downloads
                options["audio_only"] = False  # Ensure we're downloading video+audio
                options["extract_flat"] = False  # Don't extract flat (keeps audio)
                options["ignore_no_formats_error"] = True  # Ignore format errors
                # Ensure video+audio merge
                options["merge_output_format"] = "mp4" if prefer_mp4 else "mkv"
                options["prefer_ffmpeg"] = True  # Prefer FFmpeg for processing
                # Quality enforcement - force higher quality
                options["format_sort"] = ["res", "fps", "codec:h264", "codec:vp9", "codec:av1"]
                options["format_sort_force"] = True  # Force strict sorting
                options["prefer_free_formats"] = False  # Don't prefer free formats
                options["check_formats"] = True  # Enable format checking
                options["format_sort_force"] = True  # Force quality selection
            
            if include_subs:
                langs = [s.strip() for s in sub_langs.split(",") if s.strip()]
                options.update({
                    "writesubtitles": True,
                    "writeautomaticsub": auto_subs,
                    "subtitleslangs": langs,
                    "subtitlesformat": "srt",
                    "embedsubtitles": True,
                })
            
            return options
            
        except Exception as e:
            logger.error(f"Options building error: {e}")
            return {"format": "best"}
    
    def download(self, url: str, 
                 audio_only: bool = False,
                 max_height: int = 1080,
                 prefer_mp4: bool = True,
                 no_playlist: bool = False,
                 include_subs: bool = False,
                 sub_langs: str = "tr,en",
                 auto_subs: bool = False) -> bool:
        """Download video/playlist with optimized options"""
        
        if self._is_downloading:
            error_msg = "Zaten bir indirme işlemi devam ediyor!"
            logger.warning(error_msg)
            if self.error_callback:
                self.error_callback(error_msg)
            return False
        
        try:
            self._is_downloading = True
            if self.status_callback:
                self.status_callback("İndirme başlatılıyor...")
            
            # Get optimized options
            ydl_opts = self._get_optimized_ydl_options(
                audio_only, max_height, prefer_mp4, no_playlist, 
                include_subs, sub_langs, auto_subs
            )
            
            # Print quality selection info
            print(f"🎯 Seçilen Kalite: {max_height}p")
            print(f"📹 Format String: {ydl_opts.get('format', 'N/A')}")
            print(f"🔧 Format Sort: {ydl_opts.get('format_sort', 'N/A')}")
            
            # Start download
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if self.status_callback:
                self.status_callback("İndirme tamamlandı!")
            
            return True
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Download error: {e}")
            
            # Categorize and provide user-friendly error messages
            if "Private video" in error_str:
                error_msg = "Bu video özel/gizli. İndirilemez."
            elif "Video unavailable" in error_str:
                error_msg = "Video mevcut değil veya kaldırılmış."
            elif "Sign in" in error_str:
                error_msg = "Bu video için giriş yapmanız gerekiyor."
            elif "Copyright" in error_str or "blocked" in error_str:
                error_msg = "Video telif hakkı nedeniyle engellenmiş."
            elif "Network" in error_str or "Connection" in error_str:
                error_msg = "Ağ bağlantı hatası. İnternet bağlantınızı kontrol edin."
            elif "timeout" in error_str.lower():
                error_msg = "Bağlantı zaman aşımı. Tekrar deneyin."
            else:
                error_msg = f"İndirme hatası: {error_str[:100]}..."
            
            if self.error_callback:
                self.error_callback(error_msg)
            return False
        finally:
            self._is_downloading = False
    
    def download_async(self, *args, **kwargs) -> threading.Thread:
        """Start download in a separate thread with proper cleanup"""
        if self._download_thread and self._download_thread.is_alive():
            pass
            return self._download_thread
        
        self._download_thread = threading.Thread(
            target=self.download, 
            args=args, 
            kwargs=kwargs,
            daemon=True,
            name="DownloadThread"
        )
        self._download_thread.start()
        return self._download_thread
    
    def is_downloading(self) -> bool:
        """Check if download is in progress"""
        return self._is_downloading
    
    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL with optimized patterns"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/.*[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''
    
    def _extract_playlist_id(self, url: str) -> str:
        """Extract YouTube playlist ID from URL"""
        patterns = [
            r'list=([a-zA-Z0-9_-]+)',
            r'playlist\?list=([a-zA-Z0-9_-]+)',
            r'&list=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''
    
    def _clean_title(self, title: str) -> str:
        """Clean and decode title text with enhanced Turkish character support"""
        if not title:
            return 'Bilinmeyen Video'
        
        try:
            import html
            import unicodedata
            
            # Handle JSON-escaped strings
            if '\\u' in title:
                title = title.encode().decode('unicode_escape')
            
            # Handle HTML entities
            title = html.unescape(title)
            
            # Normalize Unicode
            title = unicodedata.normalize('NFC', title)
            
            # Clean up excessive whitespace
            title = ' '.join(title.split())
            
            return title.strip() if title.strip() else 'Bilinmeyen Video'
            
        except Exception as e:
            pass
            return 'Bilinmeyen Video'
    
    def get_video_info_fast(self, url: str) -> Dict[str, Any]:
        """Get video info using yt-dlp (reliable method)"""
        try:
            # Check cache first
            if url in self._video_info_cache:
                return self._video_info_cache[url]
            
            # Use yt-dlp directly for reliability
            return self.get_video_info_ytdlp(url)
            
        except Exception as e:
            logger.error(f"Error in get_video_info_fast: {e}")
            return {'error': 'Video bilgisi alınamadı. Lütfen URL\'yi kontrol edin.'}
    
    def _extract_title_from_html_optimized(self, html: str) -> str:
        """Extract video title using optimized JSON parsing"""
        try:
            # Method 1: ytInitialPlayerResponse JSON
            json_pattern = r'var ytInitialPlayerResponse = (\{.*?\});'
            json_match = re.search(json_pattern, html)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    title = json_data.get('videoDetails', {}).get('title', '')
                    if title:
                        return title
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Method 2: ytInitialData JSON
            json_pattern2 = r'var ytInitialData = (\{.*?\});'
            json_match2 = re.search(json_pattern2, html)
            if json_match2:
                try:
                    json_data = json.loads(json_match2.group(1))
                    contents = json_data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {}).get('contents', [])
                    for content in contents:
                        video_primary = content.get('videoPrimaryInfoRenderer', {})
                        if video_primary:
                            title_runs = video_primary.get('title', {}).get('runs', [])
                            if title_runs and len(title_runs) > 0:
                                title = title_runs[0].get('text', '')
                                if title:
                                    return title
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Method 3: Simple regex fallback
            patterns = [
                r'"title":"([^"]+)"',
                r'"title":\{"runs":\[\{"text":"([^"]+)"',
                r'<title>([^<]+)</title>'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    title = match.group(1)
                    if title and title != 'YouTube':
                        return title.replace(' - YouTube', '').strip()
            
            return 'Bilinmeyen Video'
            
        except Exception as e:
            pass
            return 'Bilinmeyen Video'
    
    def _get_playlist_info_optimized(self, url: str) -> Dict[str, Any]:
        """Get playlist info using optimized web scraping"""
        try:
            playlist_id = self._extract_playlist_id(url)
            if not playlist_id:
                return {'error': 'Geçersiz playlist URL'}
            
            response = self._session.get(url, timeout=config.TIMEOUT_NORMAL)
            
            if response.status_code != 200:
                return {'error': 'Playlist sayfası erişilemez'}
            
            html = response.text
            
            # Extract playlist title
            title = self._extract_playlist_title_optimized(html)
            if not title:
                title = 'Playlist'
            
            # Count videos
            video_count = self._count_playlist_videos_optimized(html)
            
            # Get thumbnail
            thumbnail_url = ''
            first_video_id = self._extract_first_video_id(html)
            if first_video_id:
                thumbnail_url = f'https://img.youtube.com/vi/{first_video_id}/mqdefault.jpg'
            else:
                thumbnail_url = 'https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg'
            
            result = {
                'title': f"{self._clean_title(title)} ({video_count} video)",
                'thumbnail': thumbnail_url,
                'is_playlist': True,
                'playlist_count': video_count,
                'playlist_id': playlist_id,
                'method': 'optimized_webscraping'
            }
            
            # Cache the result
            self._video_info_cache[url] = result
            
            pass
            return result
            
        except requests.RequestException as e:
            logger.error(f"Request error in playlist info: {e}")
            return {'error': f'İnternet bağlantısı sorunu: {str(e)[:30]}...'}
        except Exception as e:
            logger.error(f"Error in playlist info: {e}")
            return {'error': f'Playlist bilgisi alınamadı: {str(e)[:30]}...'}
    
    def _extract_playlist_title_optimized(self, html: str) -> str:
        """Extract playlist title using optimized JSON parsing"""
        try:
            # Try ytInitialData JSON
            json_pattern = r'var ytInitialData = (\{.*?\});'
            json_match = re.search(json_pattern, html)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    
                    # Navigate to playlist title
                    metadata = json_data.get('metadata', {}).get('playlistMetadataRenderer', {})
                    title = metadata.get('title', '')
                    if title:
                        return title
                    
                    # Alternative path
                    header = json_data.get('header', {}).get('playlistHeaderRenderer', {})
                    title_obj = header.get('title', {})
                    if isinstance(title_obj, dict):
                        title = title_obj.get('simpleText', '')
                        if title:
                            return title
                            
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
            
            # Fallback patterns
            patterns = [
                r'"playlistTitle":"([^"]+)"',
                r'"title":"([^"]+)".*"playlistRenderer"',
                r'<title>([^<]+)</title>',
            ]
            
            for pattern in patterns:
                try:
                    match = re.search(pattern, html)
                    if match:
                        title = match.group(1)
                        if title and 'YouTube' not in title and len(title) > 3:
                            clean_title = title.replace(' - YouTube', '').replace(' | YouTube', '').strip()
                            if clean_title:
                                return clean_title
                except Exception:
                    continue
            
            return ''
            
        except Exception as e:
            pass
            return ''
    
    def _count_playlist_videos_optimized(self, html: str) -> int:
        """Count videos in playlist using optimized method"""
        try:
            # Count videoId patterns
            video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            unique_videos = len(set(video_matches))
            
            if unique_videos > 0:
                return min(unique_videos, config.MAX_PLAYLIST_VIDEOS)
            
            # Count playlist items
            item_matches = re.findall(r'"playlistItemRenderer"', html)
            if item_matches:
                return min(len(item_matches), config.MAX_PLAYLIST_VIDEOS)
            
            return 0
            
        except Exception as e:
            pass
            return 0
    
    def _extract_first_video_id(self, html: str) -> str:
        """Extract first video ID from playlist for thumbnail"""
        try:
            video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if video_matches:
                return video_matches[0]
            
            item_pattern = r'"playlistItemRenderer".*?"videoId":"([a-zA-Z0-9_-]{11})"'
            item_match = re.search(item_pattern, html)
            if item_match:
                return item_match.group(1)
            
            return ''
            
        except Exception:
            return ''
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information with fallback"""
        # Try fast method first
        info = self.get_video_info_fast(url)
        
        # If fast method failed, try yt-dlp fallback
        if 'error' in info:
            pass
            return self.get_video_info_ytdlp(url)
        
        return info
    
    def get_video_info_ytdlp(self, url: str) -> Dict[str, Any]:
        """Get video info using yt-dlp as fallback"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'no_check_certificate': True,
                'extract_flat': False,
                'ignoreerrors': True,
                'socket_timeout': config.TIMEOUT_LONG,
                'retries': 2,
                'fragment_retries': 1,
                'no_call_home': True,
                'simulate': True,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'writethumbnail': False,
                'youtube_include_dash_manifest': False,
                'format': 'worst',
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'error': 'Video bilgisi alınamadı'}
                
                # Check if it's a playlist
                is_playlist = 'entries' in info and info['entries']
                
                if is_playlist:
                    first_entry = info['entries'][0] if info['entries'] else {}
                    playlist_count = len(info['entries'])
                    return {
                        'title': f"{info.get('title', 'Playlist')} ({playlist_count} video)",
                        'thumbnail': first_entry.get('thumbnail', ''),
                        'is_playlist': True,
                        'playlist_count': playlist_count,
                        'method': 'yt-dlp'
                    }
                else:
                    return {
                        'title': info.get('title', 'Bilinmiyor'),
                        'thumbnail': info.get('thumbnail', ''),
                        'is_playlist': False,
                        'method': 'yt-dlp'
                    }
                    
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return {'error': 'Bağlantı zaman aşımı'}
            elif "not available" in error_msg.lower():
                return {'error': 'Video bulunamadı'}
            elif "private" in error_msg.lower():
                return {'error': 'Video özel veya kısıtlı'}
            else:
                return {'error': f'Hata: {error_msg[:50]}...'}
    
    def get_playlist_entries(self, url: str) -> List[Dict[str, Any]]:
        """Get detailed playlist entries for selection"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': True,
                'ignoreerrors': True,
                'socket_timeout': config.TIMEOUT_LONG,
                'retries': 2,
                'no_call_home': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or 'entries' not in info:
                    return []
                
                entries = []
                for i, entry in enumerate(info['entries'][:config.MAX_PLAYLIST_VIDEOS]):
                    if entry:
                        entries.append({
                            'index': i + 1,
                            'id': entry.get('id', ''),
                            'title': entry.get('title', f'Video {i+1}'),
                            'url': entry.get('url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                            'duration': entry.get('duration', 0),
                            'thumbnail': f"https://img.youtube.com/vi/{entry.get('id', '')}/mqdefault.jpg"
                        })
                
            return entries
                
        except Exception as e:
            logger.error(f"Playlist entries error: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, '_session'):
                self._session.close()
            
            # Clear caches
            self._video_info_cache.clear()
            self._thumbnail_cache.clear()
            
            pass
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Backward compatibility
YouTubeDownloader = OptimizedYouTubeDownloader
