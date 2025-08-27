#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Utilities Module
Performance optimizations and utility functions
"""

import os
import time
import hashlib
import threading
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from functools import wraps, lru_cache
import requests
from PIL import Image
from io import BytesIO

from config import config
from logger import get_logger

logger = get_logger('utils')


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_lock = threading.Lock()
        self._session_pool: Dict[str, requests.Session] = {}
    
    def get_cached_result(self, key: str, max_age: float = 300) -> Optional[Any]:
        """Get cached result if not expired"""
        with self._cache_lock:
            if key in self._cache:
                if time.time() - self._cache_timestamps[key] < max_age:
                    return self._cache[key]
                else:
                    # Remove expired cache
                    del self._cache[key]
                    del self._cache_timestamps[key]
            return None
    
    def set_cached_result(self, key: str, value: Any):
        """Set cached result with timestamp"""
        with self._cache_lock:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
            
            # Limit cache size
            if len(self._cache) > config.CACHE_SIZE:
                oldest_key = min(self._cache_timestamps.keys(), 
                               key=lambda k: self._cache_timestamps[k])
                del self._cache[oldest_key]
                del self._cache_timestamps[oldest_key]
    
    def get_session(self, name: str = "default") -> requests.Session:
        """Get or create a requests session with connection pooling"""
        if name not in self._session_pool:
            session = requests.Session()
            session.headers.update(config.REQUEST_HEADERS)
            # Configure connection pooling
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=3
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            self._session_pool[name] = session
        return self._session_pool[name]
    
    def cleanup(self):
        """Cleanup resources"""
        for session in self._session_pool.values():
            session.close()
        self._session_pool.clear()
        with self._cache_lock:
            self._cache.clear()
            self._cache_timestamps.clear()


# Global performance optimizer
perf_optimizer = PerformanceOptimizer()


def cache_result(max_age: float = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache first
            result = perf_optimizer.get_cached_result(key, max_age)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            perf_optimizer.set_cached_result(key, result)
            return result
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


def measure_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.3f} seconds")
        return result
    return wrapper


class ImageProcessor:
    """Optimized image processing utilities"""
    
    @staticmethod
    @cache_result(max_age=3600)  # Cache for 1 hour
    def download_and_resize_image(url: str, size: tuple = (280, 160)) -> Optional[Image.Image]:
        """Download and resize image with caching"""
        try:
            session = perf_optimizer.get_session("image")
            response = session.get(url, timeout=config.TIMEOUT_FAST)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                # Resize with high quality
                image = image.resize(size, Image.Resampling.LANCZOS)
                return image
        except Exception as e:
            logger.error(f"Image processing error: {e}")
        return None
    
    @staticmethod
    def create_ctk_image(image: Image.Image, size: tuple) -> Any:
        """Create CTkImage from PIL Image"""
        try:
            import customtkinter as ctk
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception as e:
            logger.error(f"CTkImage creation error: {e}")
            return None


class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def safe_filename(filename: str, max_length: int = 200) -> str:
        """Create safe filename by removing invalid characters"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove multiple underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Trim to max length
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        
        return filename.strip('_')
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Directory creation error: {e}")
            return False
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception:
            return 0.0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


class ThreadManager:
    """Thread management utilities"""
    
    def __init__(self):
        self._threads: List[threading.Thread] = []
        self._thread_lock = threading.Lock()
    
    def start_thread(self, target: Callable, name: str = None, daemon: bool = True, *args, **kwargs) -> threading.Thread:
        """Start a new thread and track it"""
        thread = threading.Thread(
            target=target,
            name=name or f"Thread-{len(self._threads)}",
            daemon=daemon,
            *args, **kwargs
        )
        
        with self._thread_lock:
            self._threads.append(thread)
        
        thread.start()
        return thread
    
    def cleanup_finished_threads(self):
        """Remove finished threads from tracking"""
        with self._thread_lock:
            self._threads = [t for t in self._threads if t.is_alive()]
    
    def wait_for_all_threads(self, timeout: float = None):
        """Wait for all tracked threads to complete"""
        with self._thread_lock:
            threads = self._threads.copy()
        
        for thread in threads:
            thread.join(timeout)
    
    def get_active_thread_count(self) -> int:
        """Get count of active threads"""
        with self._thread_lock:
            return sum(1 for t in self._threads if t.is_alive())


# Global thread manager
thread_manager = ThreadManager()


class URLValidator:
    """URL validation utilities"""
    
    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'm.youtube.com',
            'music.youtube.com'
        ]
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower() in youtube_domains
        except Exception:
            return False
    
    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Check if URL is a YouTube playlist URL"""
        return 'list=' in url or 'playlist' in url
    
    @staticmethod
    def normalize_youtube_url(url: str) -> str:
        """Normalize YouTube URL"""
        if 'youtu.be/' in url:
            # Convert youtu.be to youtube.com
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            return f"https://www.youtube.com/watch?v={video_id}"
        return url


class ProgressTracker:
    """Progress tracking utilities"""
    
    def __init__(self):
        self._progress_data: Dict[str, Dict[str, Any]] = {}
        self._progress_lock = threading.Lock()
    
    def update_progress(self, task_id: str, progress: float, status: str = "", **kwargs):
        """Update progress for a task"""
        with self._progress_lock:
            self._progress_data[task_id] = {
                'progress': progress,
                'status': status,
                'timestamp': time.time(),
                **kwargs
            }
    
    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for a task"""
        with self._progress_lock:
            return self._progress_data.get(task_id)
    
    def remove_progress(self, task_id: str):
        """Remove progress tracking for a task"""
        with self._progress_lock:
            self._progress_data.pop(task_id, None)
    
    def cleanup_old_progress(self, max_age: float = 3600):
        """Remove old progress data"""
        current_time = time.time()
        with self._progress_lock:
            to_remove = [
                task_id for task_id, data in self._progress_data.items()
                if current_time - data.get('timestamp', 0) > max_age
            ]
            for task_id in to_remove:
                del self._progress_data[task_id]


# Global progress tracker
progress_tracker = ProgressTracker()


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_speed(bytes_per_second: float) -> str:
    """Format speed in human readable format"""
    if bytes_per_second < 1024:
        return f"{bytes_per_second:.0f} B/s"
    elif bytes_per_second < 1024 * 1024:
        return f"{bytes_per_second / 1024:.1f} KB/s"
    elif bytes_per_second < 1024 * 1024 * 1024:
        return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
    else:
        return f"{bytes_per_second / (1024 * 1024 * 1024):.1f} GB/s"


def open_directory_safely(directory_path: str) -> bool:
    """Safely open directory in file explorer with multiple fallback methods"""
    import os
    import subprocess
    import platform
    
    try:
        if platform.system() == "Windows":
            # Windows için birden fazla yöntem dene
            methods = [
                # Yöntem 1: os.startfile (en güvenilir)
                lambda: os.startfile(directory_path),
                # Yöntem 2: explorer komutu (shell=True ile)
                lambda: subprocess.run(f'explorer "{directory_path}"', shell=True, check=True),
                # Yöntem 3: explorer komutu (path ile)
                lambda: subprocess.run(["explorer", directory_path], check=True),
                # Yöntem 4: cmd ile
                lambda: subprocess.run(f'cmd /c start "" "{directory_path}"', shell=True, check=True)
            ]
            
            for i, method in enumerate(methods):
                try:
                    method()
                    return True
                except Exception as e:
                    if i == len(methods) - 1:  # Son yöntem başarısız
                        raise e
                    continue
                        
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", directory_path], check=True)
            return True
        else:  # Linux
            subprocess.run(["xdg-open", directory_path], check=True)
            return True
            
    except Exception as e:
        logger.error(f"Failed to open directory {directory_path}: {e}")
        return False


def cleanup_resources():
    """Cleanup all resources"""
    perf_optimizer.cleanup()
    thread_manager.cleanup_finished_threads()
    progress_tracker.cleanup_old_progress()
    logger.info("Resource cleanup completed")
