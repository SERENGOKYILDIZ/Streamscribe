#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Optimized Downloader Module
Enhanced YouTube downloader with improved performance and error handling
"""

import os
import threading
import re
import time
import tempfile
from typing import Callable, Optional, Dict, Any, List
from pathlib import Path
import requests
from yt_dlp import YoutubeDL

from config import config
from logger import get_logger

logger = get_logger('downloader')


class _YdlErrorCapture:
    """Minimal yt-dlp logger that captures warning/error messages instead of
    printing them to the console, so the real failure reason (e.g. why a
    login silently failed) can be surfaced to the user instead of a generic
    "video unavailable" message. Never receives passwords - yt-dlp/site
    extractors do not echo credentials back through their loggers."""

    def __init__(self):
        self.messages: List[str] = []

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        self.messages.append(str(msg))

    def error(self, msg):
        self.messages.append(str(msg))


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

        # Optional: browser to pull cookies from, for sites that require login
        # (e.g. Udemy). None means no cookies are used.
        self.cookies_from_browser: Optional[str] = None

        # Optional: path to a Netscape-format cookies.txt file, as an alternative
        # to live browser cookie extraction (which can fail on Windows due to
        # Chrome/Brave/Edge's "App-Bound Encryption" - see yt-dlp#10927).
        # Takes priority over cookies_from_browser when set.
        self.cookie_file: Optional[str] = None

        # Tracks a cookies.txt file we generated ourselves (e.g. from a pasted
        # cookie header via set_raw_cookie_header), so it can be cleaned up.
        self._temp_cookie_file: Optional[str] = None

        # Optional: direct username/password login (e.g. for Udemy), used by
        # sites yt-dlp supports logging into directly. Kept only in memory,
        # never written to disk or logged.
        self.login_username: Optional[str] = None
        self.login_password: Optional[str] = None

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

    def set_cookies_from_browser(self, browser: Optional[str]):
        """Set the browser to pull login cookies from (e.g. 'chrome', 'firefox',
        'edge', 'brave'). Needed for sites that require authentication, such as
        Udemy. Pass None to disable."""
        self.cookies_from_browser = browser or None

    def set_cookie_file(self, path: Optional[str]):
        """Set a Netscape-format cookies.txt file to use for login instead of
        live browser extraction. Pass None to disable."""
        self.cookie_file = path or None

    def set_login_credentials(self, username: Optional[str], password: Optional[str]):
        """Set a username/password to log in directly (e.g. for Udemy), bypassing
        browser cookie extraction entirely. Pass (None, None) to disable."""
        self.login_username = username or None
        self.login_password = password or None

    def set_raw_cookie_header(self, header: Optional[str]) -> int:
        """Parse a raw 'Cookie: name1=value1; name2=value2' request header
        (copied by hand from a browser's DevTools Network tab, after logging
        in normally in that browser) and write it to a temporary Netscape
        cookies.txt file used via cookie_file. This reuses a session a real
        person already authenticated in their own browser - no automated
        login attempt, no browser-database reading (so it also sidesteps the
        DPAPI/App-Bound Encryption issue), no extension required.
        Pass None/empty to clear. Returns the number of cookies parsed."""
        # Clean up any previous temp file
        old_temp = getattr(self, '_temp_cookie_file', None)
        if old_temp:
            try:
                os.remove(old_temp)
            except OSError:
                pass
            self._temp_cookie_file = None

        if not header or not header.strip():
            self.cookie_file = None
            return 0

        pairs = []
        for part in header.split(';'):
            part = part.strip()
            if '=' not in part:
                continue
            name, _, value = part.partition('=')
            name = name.strip()
            value = value.strip()
            if name:
                pairs.append((name, value))

        if not pairs:
            raise ValueError(
                "Geçerli çerez bulunamadı. 'isim=değer; isim2=değer2' formatında olmalı."
            )

        expiry = int(time.time()) + 365 * 24 * 3600
        lines = ["# Netscape HTTP Cookie File"]
        for name, value in pairs:
            lines.append(f".udemy.com\tTRUE\t/\tTRUE\t{expiry}\t{name}\t{value}")

        fd, path = tempfile.mkstemp(prefix="streamscribe_cookies_", suffix=".txt")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

        self.cookie_file = path
        self._temp_cookie_file = path
        return len(pairs)

    def _auth_error_message(self, text: str) -> Optional[str]:
        """Turn a raw yt-dlp error/warning string into a friendly Turkish message
        for known authentication failure modes (CAPTCHA, bad login, cookie
        extraction). Returns None if the text doesn't match any of these, so
        the caller can fall back to its own generic categorization."""
        lower = text.lower()
        if "captcha" in lower:
            return (
                "Udemy bir CAPTCHA doğrulaması istiyor. Bu durumda kullanıcı adı/şifre ile "
                "otomatik giriş yapılamaz - lütfen tarayıcınızdan Udemy'ye normal şekilde giriş yapıp "
                "CAPTCHA'yı çözün, sonra tarayıcı çerezi veya çerez dosyası yöntemini deneyin."
            )
        if "unable to login" in lower:
            return "Udemy girişi başarısız. Kullanıcı adı/e-posta ve şifreyi kontrol edip tekrar deneyin."
        if "cookie" in lower:
            browser_name = self.cookies_from_browser or "seçili tarayıcı"
            return (
                f"{browser_name} çerezleri okunamadı. Olası nedenler: "
                f"(1) {browser_name} hâlâ çalışıyor (arka planda/sistem tepsisinde de olabilir) - "
                f"tamamen kapatıp tekrar deneyin. "
                f"(2) Chrome/Brave'in yeni 'App-Bound Encryption' koruması nedeniyle çerez şifresi "
                f"çözülemiyor olabilir (bilinen bir yt-dlp sınırlaması) - bu durumda Edge veya Firefox "
                f"seçmeyi deneyin."
            )
        return None

    def _normalize_udemy_url(self, url: str) -> str:
        """yt-dlp's Udemy extractor regex expects `<course-slug>/learn/v4/t/lecture/<id>`
        (or `<course-slug>/` for a whole course) directly after the domain, but
        Udemy's current site uses `/course/<course-slug>/...` - the extra
        `course/` segment makes yt-dlp misparse the course slug as literally
        "course", which then 403s. Rewrite the URL into the shape yt-dlp expects."""
        lecture_match = re.match(
            r'https?://(?:[^/]+\.)?udemy\.com/course/([^/?#&]+)/learn/lecture/(\d+)',
            url
        )
        if lecture_match:
            slug, lecture_id = lecture_match.groups()
            rewritten = f'https://www.udemy.com/{slug}/learn/v4/t/lecture/{lecture_id}'
            logger.info(f"Rewriting Udemy lecture URL for extractor compatibility: {rewritten}")
            return rewritten

        course_match = re.match(r'https?://(?:[^/]+\.)?udemy\.com/course/([^/?#&]+)/?$', url)
        if course_match:
            slug = course_match.group(1)
            rewritten = f'https://www.udemy.com/{slug}/'
            logger.info(f"Rewriting Udemy course URL for extractor compatibility: {rewritten}")
            return rewritten

        return url

    def _progress_hook(self, d: Dict[str, Any]):
        """Optimized progress hook for yt-dlp with stable size handling"""
        try:
            if not self.progress_callback:
                return
            
            status = d.get('status', '')
            
            if status == 'downloading':
                # Get current progress data
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 0)
                total_bytes_estimate = d.get('total_bytes_estimate', 0)
                
                # Stabilize total size - use the largest stable value
                if not hasattr(self, '_stable_total_bytes'):
                    self._stable_total_bytes = 0
                
                # Update stable total bytes only if we get a larger, more reliable value
                current_total = max(total_bytes, total_bytes_estimate)
                if current_total > self._stable_total_bytes and current_total > 0:
                    # Only update if the new value is significantly larger (prevents small fluctuations)
                    if current_total > self._stable_total_bytes * 1.1 or self._stable_total_bytes == 0:
                        self._stable_total_bytes = current_total
                
                # Use stable total bytes for progress calculation
                final_total = self._stable_total_bytes if self._stable_total_bytes > 0 else current_total
                
                # Calculate stable percentage
                if final_total > 0:
                    percent = min(100, (downloaded_bytes / final_total) * 100)
                    percent_str = f"{percent:.1f}%"
                else:
                    percent_str = d.get('_percent_str', '0%')
                
                # Extract progress data with stable size
                progress_data = {
                    'status': 'downloading',
                    '_percent_str': percent_str,
                    'speed': d.get('speed', 0),
                    'eta': d.get('eta', 0),
                    'downloaded_bytes': downloaded_bytes,
                    'total_bytes': final_total,  # Use stable total
                    'total_bytes_estimate': final_total  # Use stable total
                }
                
                # Log progress data for debugging
                logger.debug(f"Progress data: {progress_data}")
                
                self.progress_callback(progress_data)
                
            elif status == 'finished':
                if self.status_callback:
                    self.status_callback("İşleniyor...")
                
                # Reset stable total bytes for next download
                if hasattr(self, '_stable_total_bytes'):
                    self._stable_total_bytes = 0
                
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
                    print(f"Format Selection: {info_msg}")
                elif 'downloading' in info_msg.lower():
                    print(f"Downloading: {info_msg}")
                
        except Exception as e:
            logger.error(f"Progress hook error: {e}")
    
    def _build_format_string(self, max_height: int, prefer_mp4: bool) -> str:
        """Build flexible format string for video quality with audio"""
        try:
            # More flexible approach to avoid 403 errors
            if prefer_mp4:
                # Flexible format selection with fallbacks
                format_string = f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}][ext=mp4]+bestaudio/best[height<={max_height}]+bestaudio/best+bestaudio"
            else:
                # Flexible format selection with fallbacks
                format_string = f"bestvideo[height<={max_height}]+bestaudio/bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]+bestaudio/best+bestaudio"
            
            print(f"Generated Format String: {format_string}")
            return format_string
            
        except Exception as e:
            logger.error(f"Format string building error: {e}")
            # Fallback to best format that includes audio - CRITICAL FOR AUDIO
            fallback = f"best[height<={max_height}]+bestaudio/best+bestaudio"
            print(f"Fallback Format String: {fallback}")
            return fallback
    
    def _get_optimized_ydl_options(self, audio_only: bool, max_height: int, 
                                 prefer_mp4: bool, no_playlist: bool, 
                                 include_subs: bool, sub_langs: str, 
                                 auto_subs: bool) -> Dict[str, Any]:
        """Get optimized yt-dlp options"""
        try:
            options = {
                "outtmpl": os.path.join(self.output_dir, "%(title).200s.%(ext)s"),
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
                # Size stabilization options
                "buffersize": 1024,  # Smaller buffer for more stable progress
                "sleep_interval": 0.1,  # Faster progress updates
                "merge_output_format": "mp4" if prefer_mp4 else "mkv",
                # Quality optimization settings - flexible approach
                "format_sort": ["res", "fps", "codec:h264", "codec:vp9", "codec:av1"],
                "format_sort_force": False,  # More flexible sorting
                "prefer_free_formats": True,  # Prefer free formats to avoid 403
                "check_formats": False,  # Disable format checking to avoid 403
            }

            if self.cookie_file:
                options["cookiefile"] = self.cookie_file
            elif self.cookies_from_browser:
                options["cookiesfrombrowser"] = (self.cookies_from_browser,)

            if self.login_username and self.login_password:
                options["username"] = self.login_username
                options["password"] = self.login_password

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
                options["format"] = self._build_format_string(max_height, prefer_mp4)
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
                # Quality enforcement - force higher quality (overrides the more
                # flexible top-level defaults, which stay in effect for audio_only)
                options["format_sort"] = ["res", "fps", "codec:h264", "codec:vp9", "codec:av1"]
                options["format_sort_force"] = True  # Force strict sorting
                options["prefer_free_formats"] = False  # Don't prefer free formats
                options["check_formats"] = True  # Enable format checking
            
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
            url = self._normalize_udemy_url(url)
            if self.status_callback:
                self.status_callback("İndirme başlatılıyor...")

            # Get optimized options
            ydl_opts = self._get_optimized_ydl_options(
                audio_only, max_height, prefer_mp4, no_playlist, 
                include_subs, sub_langs, auto_subs
            )
            
            # Print quality selection info
            print(f"Selected Quality: {max_height}p")
            print(f"Format String: {ydl_opts.get('format', 'N/A')}")
            print(f"Format Sort: {ydl_opts.get('format_sort', 'N/A')}")
            
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
            auth_msg = self._auth_error_message(error_str)
            if auth_msg:
                error_msg = auth_msg
            elif "Private video" in error_str:
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
    
    def get_video_info_fast(self, url: str) -> Dict[str, Any]:
        """Get video info using yt-dlp (reliable method) with retry"""
        try:
            # Check cache first
            if url in self._video_info_cache:
                cached = self._video_info_cache[url]
                if 'error' not in cached:
                    return cached
            
            # Use yt-dlp directly for reliability with retry
            last_error = None
            for attempt in range(3):
                try:
                    result = self.get_video_info_ytdlp(url, attempt=attempt)
                    if 'error' not in result:
                        # Cache successful results
                        self._video_info_cache[url] = result
                        return result
                    last_error = result.get('error', 'Bilinmeyen hata')
                    logger.warning(f"Video info attempt {attempt + 1}/3 failed: {last_error}")
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Video info attempt {attempt + 1}/3 exception: {e}")
                
                # Wait before retry with exponential backoff
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
            
            return {'error': last_error or 'Video bilgisi alınamadı. Lütfen URL\'yi kontrol edin.'}
            
        except Exception as e:
            logger.error(f"Error in get_video_info_fast: {e}")
            return {'error': f'Video bilgisi alınamadı: {str(e)[:80]}'}
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information - delegates to get_video_info_fast which includes retry"""
        return self.get_video_info_fast(url)
    def get_video_info_ytdlp(self, url: str, attempt: int = 0) -> Dict[str, Any]:
        """Get video info using yt-dlp with progressive fallback strategies"""
        try:
            # Handle Mix Playlists (RD...) by stripping the list parameter
            # This forces yt-dlp to treat it as a single video
            if "list=RD" in url:
                logger.info("Mix Playlist detected (RD...), stripping list parameter")
                url = re.sub(r'[?&]list=RD[^&]*', '', url)

            url = self._normalize_udemy_url(url)

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'no_check_certificate': True,
                'extract_flat': False,
                'ignoreerrors': True,
                'socket_timeout': config.TIMEOUT_LONG + (attempt * 5),
                'retries': 3,
                'fragment_retries': 2,
                'extractor_retries': 3,
                'no_call_home': True,
                'simulate': True,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'writethumbnail': False,
                'youtube_include_dash_manifest': False,
                # Use embedded client to bypass throttling
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android', 'ios'],
                    }
                },
            }

            # Explicit user-selected cookie source (e.g. for login-required
            # sites like Udemy) takes priority over the automatic retry logic below
            if self.cookie_file:
                ydl_opts['cookiefile'] = self.cookie_file
            elif self.cookies_from_browser:
                ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)

            if self.login_username and self.login_password:
                ydl_opts['username'] = self.login_username
                ydl_opts['password'] = self.login_password

            # On retry attempts, try progressively more aggressive options
            if (attempt >= 1 and not self.cookies_from_browser and not self.cookie_file
                    and not (self.login_username and self.login_password)):
                # Try with browser cookies for authentication
                for browser in ['chrome', 'firefox', 'edge', 'brave']:
                    try:
                        ydl_opts['cookiesfrombrowser'] = (browser,)
                        logger.info(f"Attempting with {browser} cookies (attempt {attempt + 1})")
                        break
                    except Exception:
                        continue
            
            if attempt >= 2:
                # Most permissive settings on final attempt
                ydl_opts['socket_timeout'] = 30
                ydl_opts['retries'] = 5
                ydl_opts['extractor_args'] = {
                    'youtube': {
                        'player_client': ['web', 'mweb', 'android', 'ios'],
                    }
                }
                logger.info(f"Final attempt with extended timeout and all player clients")

            # Capture yt-dlp's internal warning/error messages instead of letting
            # them go to the console, so we can explain *why* extraction failed
            # even when it fails silently (returns None) rather than raising -
            # this commonly happens with a failed Udemy login under ignoreerrors.
            error_capture = _YdlErrorCapture()
            ydl_opts['logger'] = error_capture

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    captured = ' | '.join(error_capture.messages)
                    logger.warning(f"yt-dlp returned None for URL: {url} (captured: {captured})")
                    auth_msg = self._auth_error_message(captured) if captured else None
                    if auth_msg:
                        return {'error': auth_msg}
                    if captured:
                        return {'error': f'Video bilgisi alınamadı: {captured[:200]}'}
                    return {'error': 'Video bilgisi alınamadı. Video silinmiş veya kısıtlı olabilir.'}
                
                # Check if it's a playlist
                is_playlist = 'entries' in info and info['entries']
                
                if is_playlist:
                    entries = [e for e in info['entries'] if e is not None]
                    first_entry = entries[0] if entries else {}
                    playlist_count = len(entries)
                    result = {
                        'title': f"{info.get('title', 'Playlist')} ({playlist_count} video)",
                        'thumbnail': first_entry.get('thumbnail', ''),
                        'is_playlist': True,
                        'playlist_count': playlist_count,
                        'method': 'yt-dlp'
                    }
                    logger.info(f"Playlist info retrieved: {result['title']}")
                    return result
                else:
                    result = {
                        'title': info.get('title', 'Bilinmiyor'),
                        'thumbnail': info.get('thumbnail', ''),
                        'video_id': info.get('id', ''),
                        'is_playlist': False,
                        'method': 'yt-dlp'
                    }
                    logger.info(f"Video info retrieved: {result['title']}")
                    return result
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"get_video_info_ytdlp error (attempt {attempt + 1}): {error_msg}")
            
            auth_msg = self._auth_error_message(error_msg)
            if auth_msg:
                return {'error': auth_msg}
            elif "timeout" in error_msg.lower():
                return {'error': 'Bağlantı zaman aşımı. İnternet bağlantınızı kontrol edin.'}
            elif "not available" in error_msg.lower() or "unavailable" in error_msg.lower():
                return {'error': 'Video bulunamadı veya kaldırılmış.'}
            elif "private" in error_msg.lower():
                return {'error': 'Video özel veya kısıtlı.'}
            elif "sign in" in error_msg.lower() or "login" in error_msg.lower():
                return {'error': 'Bu video için giriş yapılması gerekiyor.'}
            elif "geo" in error_msg.lower() or "country" in error_msg.lower():
                return {'error': 'Bu video bölgenizde kullanılamıyor.'}
            elif "copyright" in error_msg.lower() or "blocked" in error_msg.lower():
                return {'error': 'Video telif hakkı nedeniyle engellenmiş.'}
            elif "429" in error_msg or "too many" in error_msg.lower():
                return {'error': 'Çok fazla istek gönderildi. Lütfen biraz bekleyin.'}
            else:
                return {'error': f'Video bilgisi alınamadı: {error_msg[:80]}'}
    
    def get_playlist_entries(self, url: str) -> List[Dict[str, Any]]:
        """Get detailed playlist entries for selection"""
        try:
            url = self._normalize_udemy_url(url)
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': True,
                'ignoreerrors': True,
                'socket_timeout': config.TIMEOUT_LONG + 5,
                'retries': 3,
                'extractor_retries': 3,
                'no_call_home': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android', 'ios'],
                    }
                },
            }

            if self.cookie_file:
                ydl_opts['cookiefile'] = self.cookie_file
            elif self.cookies_from_browser:
                ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)

            if self.login_username and self.login_password:
                ydl_opts['username'] = self.login_username
                ydl_opts['password'] = self.login_password

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

            # Remove any temporary cookie file we generated ourselves
            temp_cookie_file = getattr(self, '_temp_cookie_file', None)
            if temp_cookie_file:
                try:
                    os.remove(temp_cookie_file)
                except OSError:
                    pass
                self._temp_cookie_file = None

            pass
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Backward compatibility
YouTubeDownloader = OptimizedYouTubeDownloader
