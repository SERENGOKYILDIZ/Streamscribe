import os
import threading
import re
import requests
import json
from typing import Callable, Optional
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    """YouTube video/playlist downloader class"""
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = output_dir
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        self._is_downloading = False
        
        # Set FFmpeg path to local directory
        self.ffmpeg_path = self._get_ffmpeg_path()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_ffmpeg_path(self) -> str:
        """Get FFmpeg executable path from local directory"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(script_dir, "ffmpeg", "bin", "ffmpeg.exe")
        
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
        else:
            # Fallback to system FFmpeg if local not found
            return "ffmpeg"
    
    def set_progress_callback(self, callback: Callable):
        """Set callback function for download progress updates"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def set_error_callback(self, callback: Callable):
        """Set callback function for error handling"""
        self.error_callback = callback
    
    def _progress_hook(self, d):
        """Internal progress hook for yt-dlp"""
        if self.progress_callback:
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('eta', 0)
                self.progress_callback({
                    'status': 'downloading',
                    'percent': percent,
                    'speed': speed,
                    'eta': eta
                })
            elif d['status'] == 'finished':
                if self.status_callback:
                    self.status_callback("İşleniyor...")
                self.progress_callback({
                    'status': 'finished',
                    'percent': '100%',
                    'speed': '',
                    'eta': 0
                })
    
    def _build_format(self, max_height: int, prefer_mp4: bool) -> str:
        """Build format string for video quality"""
        v = f"bestvideo[height<={max_height}]"
        if prefer_mp4:
            v += "[ext=mp4]"
            a = "bestaudio[ext=m4a]/bestaudio"
            combo = f"{v}+{a}/best[ext=mp4]/best"
        else:
            a = "bestaudio"
            combo = f"{v}+{a}/best"
        return combo

    def download(self, url: str, 
                 audio_only: bool = False,
                 max_height: int = 1080,
                 prefer_mp4: bool = True,
                 no_playlist: bool = False,
                 include_subs: bool = False,
                 sub_langs: str = "tr,en",
                 auto_subs: bool = False) -> bool:
        """Download video/playlist with specified options"""
        
        if self._is_downloading:
            if self.error_callback:
                self.error_callback("Zaten bir indirme işlemi devam ediyor!")
            return False
        
        try:
            self._is_downloading = True
            
            if self.status_callback:
                self.status_callback("İndirme başlatılıyor...")
            
            # Configure yt-dlp options
            ydl_opts = {
                "outtmpl": os.path.join(self.output_dir, "%(title).200s [%(id)s].%(ext)s"),
                "merge_output_format": "mp4" if prefer_mp4 else None,
                "progress_hooks": [self._progress_hook],
                "noplaylist": no_playlist,
                "quiet": True,
                "concurrent_fragment_downloads": 4,
                "retries": 10,
                "ffmpeg_location": self.ffmpeg_path,  # Use local FFmpeg
            }
            
            if audio_only:
                # Download audio and convert to MP3
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
                        {"key": "FFmpegMetadata"},
                    ],
                })
            else:
                ydl_opts["format"] = self._build_format(max_height, prefer_mp4)
                # Video post-processing
                ydl_opts.setdefault("postprocessors", [])
                ydl_opts["postprocessors"].append({"key": "FFmpegVideoRemuxer", "preferedformat": "mp4" if prefer_mp4 else "mkv"})
                ydl_opts["postprocessors"].append({"key": "FFmpegMetadata"})
            
            if include_subs:
                # Subtitle download and embedding
                langs = [s.strip() for s in sub_langs.split(",") if s.strip()]
                ydl_opts.update({
                    "writesubtitles": True,
                    "writeautomaticsub": auto_subs,
                    "subtitleslangs": langs,
                    "subtitlesformat": "srt",
                    "embedsubtitles": True,
                })
            
            # Start download
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if self.status_callback:
                self.status_callback("İndirme tamamlandı!")
            
            return True
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"İndirme hatası: {str(e)}")
            return False
        finally:
            self._is_downloading = False
    
    def download_async(self, *args, **kwargs):
        """Start download in a separate thread"""
        thread = threading.Thread(target=self.download, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    
    def is_downloading(self) -> bool:
        """Check if download is in progress"""
        return self._is_downloading
    
    def get_video_info_fast(self, url: str) -> dict:
        """Get video info using web scraping - much faster than yt-dlp"""
        try:
            # Check if it's a playlist first
            if 'list=' in url:
                return self._get_playlist_info(url)
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return {'error': 'Geçersiz YouTube URL'}
            
            # Get video page with faster timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(f'https://www.youtube.com/watch?v={video_id}', 
                                  headers=headers, timeout=1.5)  # Reduced timeout from 3s to 1.5s
            
            if response.status_code != 200:
                return {'error': 'Video sayfası erişilemez'}
            
            html = response.text
            
            # Extract title using multiple methods
            title = self._extract_title_from_html(html)
            
            if not title or title == 'Bilinmeyen Video':
                # Fallback to page title if JSON extraction fails
                title_match = re.search(r'<title>([^<]+)</title>', html)
                if title_match:
                    title = title_match.group(1).replace(' - YouTube', '').strip()
                else:
                    title = 'Bilinmeyen Video'
            
            # Get thumbnail URL - use medium quality by default for speed
            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'  # Changed from hqdefault to mqdefault
            
            # Try to get higher quality thumbnail with faster timeout
            maxres_thumb = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            try:
                thumb_check = requests.head(maxres_thumb, timeout=0.8)  # Reduced from 2s to 0.8s
                if thumb_check.status_code == 200:
                    thumbnail_url = maxres_thumb
            except:
                pass  # Use default quality
            
            return {
                'title': self._clean_title(title),
                'thumbnail': thumbnail_url,
                'video_id': video_id,
                'is_playlist': False,
                'method': 'webscraping'
            }
            
        except requests.RequestException:
            return {'error': 'İnternet bağlantısı sorunu'}
        except Exception as e:
            return {'error': f'Web scraping hatası: {str(e)[:30]}...'}
    
    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/.*[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''
    
    def _extract_title_from_html(self, html: str) -> str:
        """Extract video title from HTML using multiple methods"""
        
        # Method 1: Try to extract from ytInitialPlayerResponse JSON
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
        
        # Method 2: Try ytInitialData JSON
        json_pattern2 = r'var ytInitialData = (\{.*?\});'
        json_match2 = re.search(json_pattern2, html)
        if json_match2:
            try:
                json_data = json.loads(json_match2.group(1))
                # Navigate through the complex JSON structure
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
        
        # Method 3: Simple regex patterns as fallback
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
    
    def _get_playlist_info(self, url: str) -> dict:
        """Get playlist info using optimized web scraping - much faster and more reliable"""
        try:
            # Extract playlist ID from URL
            playlist_id = self._extract_playlist_id(url)
            if not playlist_id:
                return {'error': 'Geçersiz playlist URL'}
            
            # Use optimized headers for faster response
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Fast request with minimal timeout
            response = requests.get(url, headers=headers, timeout=2.0)  # Reduced to 2s
            
            if response.status_code != 200:
                return {'error': 'Playlist sayfası erişilemez'}
            
            html = response.text
            
            # Extract playlist title using optimized method
            title = self._extract_playlist_title_optimized(html)
            if not title:
                title = 'Playlist'
            
            # Count videos using optimized regex
            video_count = self._count_playlist_videos_optimized(html)
            
            # Get thumbnail - try to get actual first video thumbnail first
            thumbnail_url = ''
            first_video_id = self._extract_first_video_id(html)
            if first_video_id:
                thumbnail_url = f'https://img.youtube.com/vi/{first_video_id}/mqdefault.jpg'
            else:
                # Fallback to a default playlist thumbnail
                thumbnail_url = 'https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg'  # Default thumbnail
            
            return {
                'title': f"{self._clean_title(title)} ({video_count} video)",
                'thumbnail': thumbnail_url,
                'is_playlist': True,
                'playlist_count': video_count,
                'playlist_id': playlist_id,
                'method': 'optimized_webscraping'
            }
            
        except requests.RequestException as e:
            return {'error': f'İnternet bağlantısı sorunu: {str(e)[:30]}...'}
        except Exception as e:
            return {'error': f'Playlist bilgisi alınamadı: {str(e)[:30]}...'}
    
    def _extract_playlist_id(self, url: str) -> str:
        """Extract YouTube playlist ID from URL with multiple patterns"""
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
    
    def _extract_playlist_title_optimized(self, html: str) -> str:
        """Extract playlist title using optimized JSON parsing"""
        
        # Method 1: Try ytInitialData JSON (most reliable)
        json_pattern = r'var ytInitialData = (\{.*?\});'
        json_match = re.search(json_pattern, html)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                
                # Navigate to playlist title in JSON structure
                metadata = json_data.get('metadata', {}).get('playlistMetadataRenderer', {})
                title = metadata.get('title', '')
                if title:
                    return title
                
                # Alternative path: header section
                header = json_data.get('header', {}).get('playlistHeaderRenderer', {})
                title_obj = header.get('title', {})
                if isinstance(title_obj, dict):
                    title = title_obj.get('simpleText', '')
                    if title:
                        return title
                
                # Another alternative path
                contents = json_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
                for tab in contents:
                    if isinstance(tab, dict):
                        tab_content = tab.get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {})
                        if tab_content:
                            sections = tab_content.get('contents', [])
                            for section in sections:
                                if isinstance(section, dict):
                                    playlist_info = section.get('itemSectionRenderer', {}).get('contents', [])
                                    for item in playlist_info:
                                        if isinstance(item, dict):
                                            playlist_header = item.get('playlistHeaderRenderer', {})
                                            if playlist_header:
                                                title_obj = playlist_header.get('title', {})
                                                if isinstance(title_obj, dict):
                                                    title = title_obj.get('simpleText', '')
                                                    if title:
                                                        return title
                                                        
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"JSON parsing error in ytInitialData: {e}")
                pass
        
        # Method 2: Try ytInitialPlayerResponse JSON
        json_pattern2 = r'var ytInitialPlayerResponse = (\{.*?\});'
        json_match2 = re.search(json_pattern2, html)
        if json_match2:
            try:
                json_data = json.loads(json_match2.group(1))
                playlist_info = json_data.get('playlistInfo', {})
                title = playlist_info.get('title', '')
                if title:
                    return title
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"JSON parsing error in ytInitialPlayerResponse: {e}")
                pass
        
        # Method 3: Fast regex fallback patterns
        patterns = [
            r'"playlistTitle":"([^"]+)"',
            r'"title":"([^"]+)".*"playlistRenderer"',
            r'<title>([^<]+)</title>',
            r'"title":"([^"]+)".*"videoOwnerRenderer"',
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
            except Exception as e:
                print(f"Regex pattern error: {e}")
                continue
        
        return ''
    
    def _count_playlist_videos_optimized(self, html: str) -> int:
        """Count videos in playlist using optimized method"""
        try:
            # Method 1: Count videoId patterns (fastest)
            video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            unique_videos = len(set(video_matches))
            
            if unique_videos > 0:
                return unique_videos
            
            # Method 2: Count playlist items
            item_matches = re.findall(r'"playlistItemRenderer"', html)
            if item_matches:
                return len(item_matches)
            
            # Method 3: Look for video count in JSON
            json_pattern = r'var ytInitialData = (\{.*?\});'
            json_match = re.search(json_pattern, html)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    # Try to find video count in various JSON paths
                    metadata = json_data.get('metadata', {}).get('playlistMetadataRenderer', {})
                    if metadata:
                        stats = metadata.get('stats', [])
                        for stat in stats:
                            if isinstance(stat, dict) and stat.get('runs'):
                                for run in stat.get('runs', []):
                                    if isinstance(run, dict) and 'video' in run.get('text', '').lower():
                                        count_text = run.get('text', '')
                                        count_match = re.search(r'(\d+)', count_text)
                                        if count_match:
                                            return int(count_match.group(1))
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"JSON parsing error in video count: {e}")
                    pass
            
            # Method 4: Simple regex fallback
            try:
                # Look for "X videos" pattern
                video_count_pattern = r'(\d+)\s*video'
                count_match = re.search(video_count_pattern, html, re.IGNORECASE)
                if count_match:
                    return int(count_match.group(1))
            except Exception as e:
                print(f"Regex video count error: {e}")
                pass
            
            return 0
            
        except Exception as e:
            print(f"Video count extraction error: {e}")
            return 0
    
    def _extract_first_video_id(self, html: str) -> str:
        """Extract first video ID from playlist for thumbnail"""
        try:
            # Look for first videoId in playlist
            video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if video_matches:
                return video_matches[0]
            
            # Alternative: look for playlist items
            item_pattern = r'"playlistItemRenderer".*?"videoId":"([a-zA-Z0-9_-]{11})"'
            item_match = re.search(item_pattern, html)
            if item_match:
                return item_match.group(1)
            
            return ''
            
        except Exception:
            return ''
    
    def _clean_title(self, title: str) -> str:
        """Clean and decode title text with enhanced Turkish character support"""
        if not title:
            return 'Bilinmeyen Video'
        
        import html
        import json
        import codecs
        
        # Ensure we're working with a string
        if isinstance(title, bytes):
            try:
                title = title.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    title = title.decode('latin-1')
                except UnicodeDecodeError:
                    title = title.decode('utf-8', errors='ignore')
        
        # Handle JSON-escaped strings with better error handling
        try:
            # If title is JSON-escaped, decode it
            if '\\u' in title or r'\u' in title:
                # Try to decode JSON escape sequences
                title = codecs.decode(title, 'unicode_escape')
        except (UnicodeDecodeError, UnicodeEncodeError):
            try:
                # Alternative JSON decoding
                if '\\u' in title:
                    title = json.loads(f'"{title}"')
            except (json.JSONDecodeError, ValueError):
                pass  # Keep original if decoding fails
        
        # Handle HTML entities first
        title = html.unescape(title)
        
        # Enhanced Unicode escape handling for Turkish characters
        turkish_unicode_map = {
            '\\u00e7': 'ç', '\\u00c7': 'Ç',  # ç/Ç
            '\\u00f6': 'ö', '\\u00d6': 'Ö',  # ö/Ö
            '\\u00fc': 'ü', '\\u00DC': 'Ü',  # ü/Ü
            '\\u011f': 'ğ', '\\u011E': 'Ğ',  # ğ/Ğ
            '\\u0131': 'ı', '\\u0130': 'İ',  # ı/İ
            '\\u015f': 'ş', '\\u015E': 'Ş',  # ş/Ş
            # Without backslash too
            '\u00e7': 'ç', '\u00c7': 'Ç',
            '\u00f6': 'ö', '\u00d6': 'Ö',
            '\u00fc': 'ü', '\u00DC': 'Ü',
            '\u011f': 'ğ', '\u011E': 'Ğ',
            '\u0131': 'ı', '\u0130': 'İ',
            '\u015f': 'ş', '\u015E': 'Ş',
        }
        
        for escaped, char in turkish_unicode_map.items():
            title = title.replace(escaped, char)
        
        # Handle other common entities and escapes
        entity_replacements = {
            '&amp;': '&', '&quot;': '"', '&apos;': "'", '&lt;': '<', '&gt;': '>',
            '&#39;': "'", '&#34;': '"', '&#x27;': "'", '&#x22;': '"',
            '\\u0026': '&', '\\u003d': '=', '\\u0027': "'", '\\u0022': '"',
            '\\/': '/', '\\\\': '\\', '\\n': ' ', '\\t': ' ',
            # Additional Unicode sequences
            '\u0026': '&', '\u003d': '=', '\u0027': "'", '\u0022': '"',
        }
        
        for old, new in entity_replacements.items():
            title = title.replace(old, new)
        
        # Remove common YouTube suffixes
        youtube_suffixes = [
            ' - YouTube', ' - YouTube Music', ' (Official Video)', 
            ' (Official Audio)', ' [Official Video]', ' [Official Audio]',
            ' (Lyrics)', ' [Lyrics]', ' (HD)', ' [HD]'
        ]
        
        for suffix in youtube_suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)]
        
        # Final normalization - ensure proper UTF-8 encoding
        try:
            # Normalize and ensure UTF-8
            title = title.encode('utf-8').decode('utf-8')
            # Additional normalization for Turkish characters
            import unicodedata
            title = unicodedata.normalize('NFC', title)
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If encoding fails, try to clean problematic characters
            title = ''.join(char for char in title if ord(char) < 65536)
        
        # Clean up excessive whitespace
        title = ' '.join(title.split())
        
        # Return cleaned title or fallback
        return title.strip() if title.strip() else 'Bilinmeyen Video'
    
    def get_video_info(self, url: str) -> dict:
        """Get video information - tries web scraping first, then yt-dlp fallback"""
        # First try fast web scraping
        info = self.get_video_info_fast(url)
        
        # If web scraping failed, try yt-dlp as fallback
        if 'error' in info:
            return self.get_video_info_ytdlp(url)
        
        return info
    
    def get_video_info_ytdlp(self, url: str) -> dict:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'no_check_certificate': True,
                'extract_flat': False,
                'ignoreerrors': True,
                'socket_timeout': 8,  # Reduced timeout
                'retries': 2,  # Fewer retries
                'fragment_retries': 1,
                'no_call_home': True,
                'simulate': True,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'writethumbnail': False,  # Don't download thumbnail
                'youtube_include_dash_manifest': False,  # Skip DASH
                'format': 'worst',  # Don't analyze all formats
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'error': 'Video bilgisi alınamadı'}
                
                # Playlist kontrolü
                is_playlist = 'entries' in info and info['entries']
                
                if is_playlist:
                    # Playlist ise ilk video bilgisini al
                    first_entry = info['entries'][0] if info['entries'] else {}
                    playlist_count = len(info['entries'])
                    return {
                        'title': f"{info.get('title', 'Playlist')} ({playlist_count} video)",
                        'thumbnail': first_entry.get('thumbnail', ''),
                        'is_playlist': True,
                        'playlist_count': playlist_count
                    }
                else:
                    # Tek video - sadece temel bilgiler
                    return {
                        'title': info.get('title', 'Bilinmiyor'),
                        'thumbnail': info.get('thumbnail', ''),
                        'is_playlist': False
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


if __name__ == "__main__":
    # Command line interface for backward compatibility
    import argparse
    
    def progress_hook(data):
        if data['status'] == 'downloading':
            print(f"\rİndiriliyor: {data['percent']} | Hız: {data['speed']} | ETA: {data['eta']}s", end="", flush=True)
        elif data['status'] == 'finished':
            print("\nİndirme tamamlandı!")
    
    def status_hook(message):
        print(f"\n{message}")
    
    def error_hook(message):
        print(f"\nHATA: {message}")
    
    ap = argparse.ArgumentParser(description="YouTube video/playlist indirici")
    ap.add_argument("url", help="Video veya playlist URL'si")
    ap.add_argument("-o", "--output", default="downloads",
                    help="Çıkış klasörü (varsayılan: downloads)")
    ap.add_argument("--audio-only", action="store_true",
                    help="Sadece ses indir ve MP3'e dönüştür")
    ap.add_argument("--max-height", type=int, default=1080,
                    help="Maks. çözünürlük yüksekliği (örn: 720/1080/2160)")
    ap.add_argument("--mp4", action="store_true",
                    help="Mümkünse MP4 tercih et")
    ap.add_argument("--no-playlist", action="store_true",
                    help="Sadece tek video indir (playlist ise bile)")
    ap.add_argument("--subs", action="store_true",
                    help="Altyazıları indir (mevcutsa/otomatik) ve göm")
    ap.add_argument("--sub-langs", default="tr,en",
                    help="Altyazı dilleri virgüllü (örn: tr,en)")
    ap.add_argument("--auto-subs", action="store_true",
                    help="Otomatik oluşturulan altyazıları da dene")
    args = ap.parse_args()
    
    # Create downloader instance
    downloader = YouTubeDownloader(args.output)
    downloader.set_progress_callback(progress_hook)
    downloader.set_status_callback(status_hook)
    downloader.set_error_callback(error_hook)
    
    # Start download
    downloader.download(
        url=args.url,
        audio_only=args.audio_only,
        max_height=args.max_height,
        prefer_mp4=args.mp4,
        no_playlist=args.no_playlist,
        include_subs=args.subs,
        sub_langs=args.sub_langs,
        auto_subs=args.auto_subs
    )