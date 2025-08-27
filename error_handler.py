#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Error Handler Module
Centralized error handling and user-friendly error messages
"""

import traceback
import sys
from typing import Optional, Dict, Any, Callable
from enum import Enum
from logger import get_logger

logger = get_logger('error_handler')


class ErrorType(Enum):
    """Error types for categorization"""
    NETWORK = "network"
    DOWNLOAD = "download"
    GUI = "gui"
    CONFIG = "config"
    FILE = "file"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class StreamScribeError(Exception):
    """Base exception class for StreamScribe"""
    
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN, 
                 original_error: Optional[Exception] = None, user_message: Optional[str] = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error
        self.user_message = user_message or message
        self.traceback = traceback.format_exc()


class NetworkError(StreamScribeError):
    """Network-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.NETWORK, 
            original_error,
            "İnternet bağlantısı sorunu. Lütfen bağlantınızı kontrol edin."
        )


class DownloadError(StreamScribeError):
    """Download-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.DOWNLOAD, 
            original_error,
            "Video indirme hatası. Lütfen URL'yi kontrol edin ve tekrar deneyin."
        )


class GUIError(StreamScribeError):
    """GUI-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.GUI, 
            original_error,
            "Arayüz hatası. Lütfen uygulamayı yeniden başlatın."
        )


class ConfigError(StreamScribeError):
    """Configuration-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.CONFIG, 
            original_error,
            "Konfigürasyon hatası. Lütfen ayarları kontrol edin."
        )


class FileError(StreamScribeError):
    """File-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.FILE, 
            original_error,
            "Dosya işleme hatası. Lütfen dosya izinlerini kontrol edin."
        )


class PermissionError(StreamScribeError):
    """Permission-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            ErrorType.PERMISSION, 
            original_error,
            "İzin hatası. Lütfen yönetici olarak çalıştırmayı deneyin."
        )


class ErrorHandler:
    """Centralized error handler for StreamScribe"""
    
    def __init__(self):
        self.error_callbacks: Dict[ErrorType, Callable] = {}
        self.general_error_callback: Optional[Callable] = None
    
    def set_error_callback(self, error_type: ErrorType, callback: Callable):
        """Set error callback for specific error type"""
        self.error_callbacks[error_type] = callback
    
    def set_general_error_callback(self, callback: Callable):
        """Set general error callback for all errors"""
        self.general_error_callback = callback
    
    def handle_error(self, error: Exception, context: str = "") -> str:
        """Handle error and return user-friendly message"""
        try:
            # Log the error
            logger.error(f"Error in {context}: {error}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            
            # Determine error type and create appropriate exception
            streamscribe_error = self._categorize_error(error)
            
            # Call specific error callback if available
            if streamscribe_error.error_type in self.error_callbacks:
                self.error_callbacks[streamscribe_error.error_type](streamscribe_error)
            
            # Call general error callback if available
            if self.general_error_callback:
                self.general_error_callback(streamscribe_error)
            
            return streamscribe_error.user_message
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return "Beklenmeyen bir hata oluştu. Lütfen uygulamayı yeniden başlatın."
    
    def _categorize_error(self, error: Exception) -> StreamScribeError:
        """Categorize error and create appropriate StreamScribeError"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network errors
        if any(keyword in error_str for keyword in ['connection', 'timeout', 'network', 'dns', 'ssl']):
            return NetworkError(str(error), error)
        
        # Download errors
        if any(keyword in error_str for keyword in ['download', 'extract', 'format', 'video', 'youtube']):
            return DownloadError(str(error), error)
        
        # File errors
        if any(keyword in error_str for keyword in ['file', 'directory', 'path', 'not found']):
            return FileError(str(error), error)
        
        # Permission errors
        if any(keyword in error_str for keyword in ['permission', 'access', 'denied', 'forbidden']):
            return PermissionError(str(error), error)
        
        # GUI errors
        if any(keyword in error_type for keyword in ['tkinter', 'gui', 'widget']):
            return GUIError(str(error), error)
        
        # Config errors
        if any(keyword in error_str for keyword in ['config', 'setting', 'option']):
            return ConfigError(str(error), error)
        
        # Default to unknown error
        return StreamScribeError(str(error), ErrorType.UNKNOWN, error)
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return self.handle_error(e, f"Function: {func.__name__}")
    
    def safe_thread_execute(self, func: Callable, callback: Callable, *args, **kwargs):
        """Safely execute a function in a thread with error handling"""
        import threading
        
        def thread_worker():
            try:
                result = func(*args, **kwargs)
                callback(result)
            except Exception as e:
                error_msg = self.handle_error(e, f"Thread function: {func.__name__}")
                callback(None, error_msg)
        
        thread = threading.Thread(target=thread_worker, daemon=True)
        thread.start()
        return thread


# Global error handler instance
error_handler = ErrorHandler()


def handle_error(error: Exception, context: str = "") -> str:
    """Convenience function to handle errors"""
    return error_handler.handle_error(error, context)


def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """Convenience function to safely execute functions"""
    return error_handler.safe_execute(func, *args, **kwargs)


def safe_thread_execute(func: Callable, callback: Callable, *args, **kwargs):
    """Convenience function to safely execute functions in threads"""
    return error_handler.safe_thread_execute(func, callback, *args, **kwargs)


# Error message templates
ERROR_MESSAGES = {
    ErrorType.NETWORK: {
        'timeout': 'Bağlantı zaman aşımı. İnternet bağlantınızı kontrol edin.',
        'connection': 'İnternet bağlantısı sorunu. Lütfen bağlantınızı kontrol edin.',
        'dns': 'DNS çözümleme hatası. İnternet bağlantınızı kontrol edin.',
        'ssl': 'SSL sertifika hatası. Güvenlik ayarlarınızı kontrol edin.'
    },
    ErrorType.DOWNLOAD: {
        'video_not_found': 'Video bulunamadı. URL\'yi kontrol edin.',
        'private_video': 'Video özel veya kısıtlı. Bu videoyu indiremezsiniz.',
        'age_restricted': 'Yaş kısıtlamalı video. Bu videoyu indiremezsiniz.',
        'format_not_available': 'İstenen format mevcut değil. Farklı bir kalite seçin.',
        'playlist_empty': 'Playlist boş veya erişilemez.',
        'quota_exceeded': 'YouTube API kotası aşıldı. Lütfen daha sonra tekrar deneyin.'
    },
    ErrorType.FILE: {
        'not_found': 'Dosya bulunamadı.',
        'permission_denied': 'Dosya izni reddedildi.',
        'disk_full': 'Disk alanı dolu. Lütfen alan açın.',
        'invalid_path': 'Geçersiz dosya yolu.',
        'file_in_use': 'Dosya kullanımda. Lütfen diğer programları kapatın.'
    },
    ErrorType.GUI: {
        'widget_destroyed': 'Arayüz bileşeni yok edildi.',
        'thread_error': 'Arayüz thread hatası.',
        'display_error': 'Görüntüleme hatası.',
        'event_error': 'Olay işleme hatası.'
    },
    ErrorType.CONFIG: {
        'invalid_setting': 'Geçersiz ayar değeri.',
        'config_not_found': 'Konfigürasyon dosyası bulunamadı.',
        'config_corrupt': 'Konfigürasyon dosyası bozuk.',
        'setting_not_found': 'Ayar bulunamadı.'
    }
}


def get_user_friendly_message(error_type: ErrorType, error_key: str) -> str:
    """Get user-friendly error message"""
    if error_type in ERROR_MESSAGES and error_key in ERROR_MESSAGES[error_type]:
        return ERROR_MESSAGES[error_type][error_key]
    return "Beklenmeyen bir hata oluştu."
