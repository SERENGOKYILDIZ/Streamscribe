#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Optimized GUI Module
Modern, optimized GUI interface with improved performance and user experience
"""

import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from typing import Optional, Dict, Any
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO

from config import config
from logger import get_logger, setup_logging
from downloader import OptimizedYouTubeDownloader

logger = get_logger('gui')


class StreamScribeOptimizedGUI:
    """Optimized StreamScribe GUI with modern design and improved performance"""
    
    def __init__(self):
        # Setup logging
        setup_logging(config.LOG_LEVEL)
        
        # Configure CustomTkinter
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title(f"{config.APP_NAME} - YouTube Video İndirici")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Center window
        self._center_window()
        
        # Set icon
        self._set_window_icon()
        
        # Initialize variables
        self.output_dir = config.DEFAULT_OUTPUT_DIR
        self.downloader: Optional[OptimizedYouTubeDownloader] = None
        self.download_start_time: Optional[float] = None
        
        # Cache for thumbnails and video info
        self._thumbnail_cache: Dict[str, ctk.CTkImage] = {}
        self._video_info_cache: Dict[str, Dict[str, Any]] = {}
        
        # Playlist management
        self.playlist_items: list = []
        self.bulk_download_active = False
        self.current_playlist_info: Optional[Dict[str, Any]] = None
        self.playlist_download_index = 0
        self.playlist_total_videos = 0
        
        # Create UI
        self._create_ui()
        
        # Set fullscreen mode AFTER UI is created
        self.root.after(200, self._set_fullscreen)
        
        # Initialize downloader
        self._setup_downloader()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _set_fullscreen(self):
        """Set window to maximized (zoomed) mode - looks fullscreen but keeps window controls"""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Use zoomed state instead of fullscreen (keeps window controls)
            self.root.state('zoomed')
            
            # Set geometry to screen size
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Store screen dimensions for responsive layout
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.is_fullscreen = True
            
            # Adjust layout for fullscreen
            self._adjust_layout_for_fullscreen()
            
            pass
        except Exception as e:
            pass
            # Fallback to normal window
            try:
                self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
                self._center_window()
            except:
                pass
    
    def _adjust_layout_for_fullscreen(self):
        """Adjust layout elements for maximized mode"""
        try:
            if hasattr(self, 'is_fullscreen') and self.is_fullscreen:
                # Increase font sizes
                self._update_font_sizes(large=True)
                
                # Adjust panel widths for better maximized layout
                self._update_panel_widths()
                
                # Hide debug elements in maximized mode
                self._hide_debug_elements()
                
                pass
        except Exception as e:
            pass
    
    def _update_font_sizes(self, large=False):
        """Update font sizes based on screen mode"""
        try:
            if large:
                # Larger fonts for fullscreen
                self.title_font = ctk.CTkFont(size=32, weight="bold")
                self.header_font = ctk.CTkFont(size=20, weight="bold")
                self.normal_font = ctk.CTkFont(size=16)
                self.small_font = ctk.CTkFont(size=14)
                
                # Update header fonts
                if hasattr(self, 'title_label'):
                    self.title_label.configure(font=ctk.CTkFont(size=32, weight="bold"))
                if hasattr(self, 'subtitle_label'):
                    self.subtitle_label.configure(font=ctk.CTkFont(size=18))
                if hasattr(self, 'version_label'):
                    self.version_label.configure(font=ctk.CTkFont(size=14))
            else:
                # Normal fonts for windowed mode
                self.title_font = ctk.CTkFont(size=24, weight="bold")
                self.header_font = ctk.CTkFont(size=18, weight="bold")
                self.normal_font = ctk.CTkFont(size=14)
                self.small_font = ctk.CTkFont(size=12)
                
                # Update header fonts
                if hasattr(self, 'title_label'):
                    self.title_label.configure(font=ctk.CTkFont(size=24, weight="bold"))
                if hasattr(self, 'subtitle_label'):
                    self.subtitle_label.configure(font=ctk.CTkFont(size=12))
                if hasattr(self, 'version_label'):
                    self.version_label.configure(font=ctk.CTkFont(size=10))
        except Exception as e:
            pass
    
    def _update_panel_widths(self):
        """Update panel widths for fullscreen mode"""
        try:
            if hasattr(self, 'left_panel') and hasattr(self, 'right_panel'):
                if self.is_fullscreen:
                    # Better proportions for fullscreen
                    left_width = int(self.screen_width * 0.45)  # 45% of screen
                    right_width = int(self.screen_width * 0.45)  # 45% of screen
                    spacing = int(self.screen_width * 0.1)      # 10% spacing
                else:
                    # Normal proportions
                    left_width = 420
                    right_width = 380
                    spacing = 16
                
                # Update panel widths
                self.left_panel.configure(width=left_width)
                self.right_panel.configure(width=right_width)
                
                pass
        except Exception as e:
            pass
    
    def _hide_debug_elements(self):
        """Hide debug elements in maximized mode"""
        try:
            # Hide network debug section
            if hasattr(self, 'network_frame'):
                self.network_frame.pack_forget()
            
            # Hide other debug elements
            if hasattr(self, 'debug_label'):
                self.debug_label.pack_forget()
                
        except Exception as e:
            pass
    
    def _set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = Path(__file__).parent / "logo" / "favicon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            pass
    
    def _create_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header
        self._create_header(main_frame)
        
        # Content area
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(8, 0))
        
        # Left panel - Controls (reduced width)
        self.left_panel = ctk.CTkFrame(content_frame, width=420)  # Reduced from 480 to 420
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.left_panel.pack_propagate(False)
        
        # Right panel - Information (increased width)
        self.right_panel = ctk.CTkFrame(content_frame, width=380)  # Increased from 320 to 380
        self.right_panel.pack(side="right", fill="both", padx=(8, 0))
        self.right_panel.pack_propagate(False)
        
        # Create panels
        self._create_control_panel(self.left_panel)
        self._create_info_panel(self.right_panel)
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # F11 to toggle fullscreen
        self.root.bind('<F11>', self._toggle_fullscreen)
        # Escape to exit fullscreen
        self.root.bind('<Escape>', self._exit_fullscreen)
    
    def _toggle_fullscreen(self, event=None):
        """Toggle between maximized and normal window mode"""
        try:
            if self.is_fullscreen:
                # Exit maximized mode
                self.root.state('normal')
                self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
                self._center_window()
                self.is_fullscreen = False
                self._restore_normal_layout()
                pass
            else:
                # Enter maximized mode
                self.root.state('zoomed')
                self.is_fullscreen = True
                self._adjust_layout_for_fullscreen()
                pass
        except Exception as e:
            pass
    
    def _exit_fullscreen(self, event=None):
        """Exit maximized mode"""
        try:
            self.root.state('normal')
            self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
            self._center_window()
            
            # Reset fullscreen flag
            self.is_fullscreen = False
            
            # Restore normal layout
            self._restore_normal_layout()
            
            pass
        except Exception as e:
            pass
    
    def _restore_normal_layout(self):
        """Restore normal layout when exiting maximized mode"""
        try:
            # Restore normal font sizes
            self._update_font_sizes(large=False)
            
            # Restore normal panel widths
            self._update_panel_widths()
            
            # Show debug elements again
            self._show_debug_elements()
            
            pass
        except Exception as e:
            pass
    
    def _show_debug_elements(self):
        """Show debug elements when exiting maximized mode"""
        try:
            # Show network debug section
            if hasattr(self, 'network_frame'):
                self.network_frame.pack(side="bottom", fill="x", padx=8, pady=4)
            
            # Show other debug elements
            if hasattr(self, 'debug_label'):
                self.debug_label.pack(side="bottom", fill="x", padx=8, pady=2)
                
            pass
        except Exception as e:
            pass
    
    def _create_header(self, parent):
        """Create header with title and version"""
        header_frame = ctk.CTkFrame(parent, height=60, fg_color=("#2b2b2b", "#1a1a1a"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=f"🎬 {config.APP_NAME}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#ffffff", "#ffffff")
        )
        self.title_label.pack(side="left", padx=15, pady=15)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="YouTube Video İndirici",
            font=ctk.CTkFont(size=12),
            text_color=("#cccccc", "#cccccc")
        )
        self.subtitle_label.pack(side="left", padx=(0, 15), pady=15)
        
        # Version
        self.version_label = ctk.CTkLabel(
            header_frame,
            text=f"v{config.APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=("#888888", "#888888")
        )
        self.version_label.pack(side="right", padx=15, pady=15)
    
    def _create_control_panel(self, parent):
        """Create main control panel"""
        # URL Input Section
        url_frame = ctk.CTkFrame(parent)
        url_frame.pack(fill="x", padx=15, pady=15)
        
        url_label = ctk.CTkLabel(
            url_frame, 
            text="YouTube URL:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        url_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", padx=15, pady=(0, 8))
        self.url_entry.bind("<KeyRelease>", self._on_url_change)
        self.url_entry.bind("<Control-v>", self._on_paste)
        
        # Analyze button
        self.analyze_btn = ctk.CTkButton(
            url_frame,
            text="🔍 Analiz Et",
            height=30,
            command=self._analyze_video,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.analyze_btn.pack(pady=(0, 15))
        
        # Options Section
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        options_label = ctk.CTkLabel(
            options_frame, 
            text="İndirme Seçenekleri:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        options_label.pack(anchor="w", padx=15, pady=(15, 8))
        
        # Format and Quality Selection - Side by Side
        format_quality_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_quality_container.pack(fill="x", padx=15, pady=(0, 8))
        
        # Format Selection (Left Side)
        format_frame = ctk.CTkFrame(format_quality_container)
        format_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        format_label = ctk.CTkLabel(
            format_frame, 
            text="📁 Format:", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        format_label.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Radio button frame
        radio_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
        radio_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        self.format_var = ctk.StringVar(value="video")
        
        # Video radio button
        video_radio = ctk.CTkRadioButton(
            radio_frame,
            text="🎥 Video (MP4)",
            variable=self.format_var,
            value="video",
            font=ctk.CTkFont(size=11),
            command=self._on_format_change
        )
        video_radio.pack(anchor="w", pady=3)
        
        # Audio radio button
        audio_radio = ctk.CTkRadioButton(
            radio_frame,
            text="🎵 Ses (MP3)",
            variable=self.format_var,
            value="audio",
            font=ctk.CTkFont(size=11),
            command=self._on_format_change
        )
        audio_radio.pack(anchor="w", pady=3)
        
        # Quality Selection (Right Side)
        quality_frame = ctk.CTkFrame(format_quality_container)
        quality_frame.pack(side="right", fill="x", expand=True, padx=(8, 0))
        
        quality_label = ctk.CTkLabel(
            quality_frame, 
            text="⚡ Kalite:", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        quality_label.pack(anchor="w", padx=12, pady=(12, 8))
        
        self.quality_var = ctk.StringVar(value="1080p")
        quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            values=["4K", "1440p", "1080p", "720p", "480p", "360p"],
            variable=self.quality_var,
            height=30,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=10)
        )
        quality_menu.pack(fill="x", padx=12, pady=(0, 12))
        
        # Output directory
        output_frame = ctk.CTkFrame(options_frame)
        output_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        output_label = ctk.CTkLabel(
            output_frame, 
            text="📂 İndirme Klasörü:", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        output_label.pack(anchor="w", padx=12, pady=(12, 8))
        
        dir_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        dir_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        self.output_label = ctk.CTkLabel(
            dir_frame,
            text=self.output_dir,
            font=ctk.CTkFont(size=11),
            anchor="w",
            wraplength=300
        )
        self.output_label.pack(side="left", fill="x", expand=True)
        
        # Browse and Open buttons
        button_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        button_frame.pack(side="right")
        
        browse_btn = ctk.CTkButton(
            button_frame,
            text="📁 Değiştir",
            width=80,
            height=28,
            command=self._browse_output_dir,
            font=ctk.CTkFont(size=10)
        )
        browse_btn.pack(side="left", padx=(5, 0))
        
        open_btn = ctk.CTkButton(
            button_frame,
            text="📂 Aç",
            width=60,
            height=28,
            command=self._open_output_dir,
            font=ctk.CTkFont(size=10)
        )
        open_btn.pack(side="left", padx=(5, 0))
        
        # Progress Section
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        progress_label = ctk.CTkLabel(
            progress_frame, 
            text="İndirme İlerlemesi:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.pack(anchor="w", padx=15, pady=(15, 8))
        
        # Progress bar with percentage
        progress_container = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=15, pady=(0, 8))
        
        self.progress_bar = ctk.CTkProgressBar(progress_container, height=20)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Progress percentage label
        self.progress_percent = ctk.CTkLabel(
            progress_container,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#2b9348", "#2d5016")
        )
        self.progress_percent.pack(anchor="e", pady=(5, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Hazır",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Download Button - moved inside progress frame
        self.download_btn = ctk.CTkButton(
            progress_frame,
            text="⬇️ İNDİR",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_download,
            fg_color=("#2b9348", "#2d5016"),
            hover_color=("#1e6b32", "#1f3a0f"),
            state="disabled"
        )
        self.download_btn.pack(fill="x", padx=15, pady=(0, 15))
    
    def _create_info_panel(self, parent):
        """Create information panel"""
        # Info header
        info_header = ctk.CTkFrame(parent, height=40, fg_color=("#2b2b2b", "#1a1a1a"))
        info_header.pack(fill="x", padx=8, pady=(8, 0))
        info_header.pack_propagate(False)
        
        self.info_title = ctk.CTkLabel(
            info_header,
            text="📋 Video Bilgileri",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.info_title.pack(pady=12)
        
        # Scrollable info area
        self.info_frame = ctk.CTkScrollableFrame(parent, height=320)
        self.info_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Thumbnail
        self.thumbnail_label = ctk.CTkLabel(
            self.info_frame,
            text="🎥\nThumbnail",
            width=350,
            height=200,
            fg_color=("#3b3b3b", "#2b2b2b"),
            corner_radius=8
        )
        self.thumbnail_label.pack(pady=8)
        
        # Video info
        self.video_title = ctk.CTkLabel(
            self.info_frame,
            text="Video başlığı burada görünecek",
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=350,
            anchor="center",
            justify="center"
        )
        self.video_title.pack(fill="x", pady=(8, 5))
        
        # Info details
        self.info_details = ctk.CTkTextbox(
            self.info_frame,
            height=100,
            font=ctk.CTkFont(size=10)
        )
        self.info_details.pack(fill="x", pady=8)
        self.info_details.insert("1.0", "Video analiz edilmedi.\n\nBir YouTube URL'si girin ve 'Analiz Et' butonuna tıklayın.")
        self.info_details.configure(state="disabled")
        
        # Playlist videos list (initially hidden) - Improved layout
        self.playlist_frame = ctk.CTkFrame(self.info_frame)
        self.playlist_frame.pack(fill="both", expand=True, pady=10)
        
        playlist_label = ctk.CTkLabel(
            self.playlist_frame,
            text="📋 Playlist Videoları:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        playlist_label.pack(anchor="w", padx=18, pady=(18, 10))
        
        # Scrollable playlist with increased height and better spacing
        self.playlist_listbox = ctk.CTkScrollableFrame(
            self.playlist_frame,
            height=200,  # Increased from 120 to 200
            fg_color="transparent"
        )
        self.playlist_listbox.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        
        # Initially hide playlist frame
        self.playlist_frame.pack_forget()
    
    def _setup_downloader(self):
        """Initialize downloader with callbacks"""
        try:
            self.downloader = OptimizedYouTubeDownloader(self.output_dir)
            self.downloader.set_progress_callback(self._progress_callback)
            self.downloader.set_status_callback(self._status_callback)
            self.downloader.set_error_callback(self._error_callback)
            pass
        except Exception as e:
            logger.error(f"Downloader setup error: {e}")
            messagebox.showerror("Hata", f"Downloader başlatılamadı: {e}")
    
    def _on_url_change(self, event=None):
        """Handle URL entry changes"""
        url = self.url_entry.get().strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            self.analyze_btn.configure(state="normal")
        else:
            self.analyze_btn.configure(state="disabled")
            self.download_btn.configure(state="disabled")
    
    def _on_paste(self, event=None):
        """Handle paste event"""
        self.root.after(100, self._on_url_change)
    
    def _analyze_video(self):
        """Analyze video and show info"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin!")
            return
        
        # Reset progress bar and status for new analysis (but preserve if bulk download is active)
        if not hasattr(self, 'bulk_download_active') or not self.bulk_download_active:
            self.progress_bar.set(0)
            self.progress_percent.configure(text="0%")
        self.status_label.configure(text="Video bilgileri alınıyor...")
        
        self.analyze_btn.configure(state="disabled", text="🔄 Analiz Ediliyor...")
        
        def analyze_worker():
            try:
                info = self.downloader.get_video_info_fast(url)
                self.root.after(0, lambda: self._display_video_info(info))
            except Exception as e:
                logger.error(f"Video analysis error: {e}")
                self.root.after(0, lambda: self._show_error(f"Analiz hatası: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.analyze_btn.configure(
                    state="normal", text="🔍 Analiz Et"
                ))
        
        threading.Thread(target=analyze_worker, daemon=True).start()
    
    def _display_video_info(self, info: Dict[str, Any]):
        """Display video information in info panel"""
        if 'error' in info:
            self._show_error(info['error'])
            return
        
        # Update title
        title = info.get('title', 'Bilinmeyen Video')
        self.video_title.configure(text=title)
        
        # Update details
        self.info_details.configure(state="normal")
        self.info_details.delete("1.0", "end")
        
        details = f"📺 Başlık: {title}\n\n"
        details += f"🔗 Video ID: {info.get('video_id', 'N/A')}\n\n"
        details += f"📋 Tür: {'Playlist' if info.get('is_playlist', False) else 'Tek Video'}\n\n"
        details += f"⚡ Yöntem: {info.get('method', 'yt-dlp').title()}\n\n"
        
        if info.get('is_playlist', False):
            count = info.get('playlist_count', 0)
            details += f"📊 Video Sayısı: {count}\n\n"
            details += "✅ Playlist analizi tamamlandı.\nAşağıdaki listeden tek tek video indirebilirsiniz."
            
            # Update title to show it's a playlist
            self.info_title.configure(text="📋 Oynatma Listesi Bilgileri")
            
            # Store playlist info for download tracking
            self.current_playlist_info = info
            self.playlist_total_videos = count
            
            # Show playlist videos
            self._show_playlist_videos(info)
        else:
            details += "✅ Video analizi tamamlandı.\nİndirme için ayarları yapın ve 'İNDİR' butonuna tıklayın."
            
            # Update title to show it's a single video
            self.info_title.configure(text="📋 Video Bilgileri")
            
            # Hide playlist frame for single videos
            self.playlist_frame.pack_forget()
            # Clear playlist info for single videos
            self.current_playlist_info = None
        
        self.info_details.insert("1.0", details)
        self.info_details.configure(state="disabled")
        
        # Load thumbnail
        if 'thumbnail' in info:
            self._load_thumbnail(info['thumbnail'])
        
        # Enable download button and set dynamic text based on content type
        if info.get('is_playlist', False):
            # For playlists, change button text to "Tüm Playlist'i İndir"
            self.download_btn.configure(state="normal", text="🚀 Tüm Playlist'i İndir")
            # Change button command to bulk download
            self.download_btn.configure(command=self._start_bulk_download)
        else:
            # For single videos, use normal "İndir" text
            self.download_btn.configure(state="normal", text="⬇️ İNDİR")
            # Restore normal download command
            self.download_btn.configure(command=self._start_download)
        
        self.status_label.configure(text="Video analizi tamamlandı - İndirmeye hazır")
        
        pass
    
    def _load_thumbnail(self, url: str):
        """Load and display thumbnail with caching"""
        if not url:
            return
        
        # Check cache first
        if url in self._thumbnail_cache:
            self.thumbnail_label.configure(image=self._thumbnail_cache[url], text="")
            return
        
        def load_worker():
            try:
                response = requests.get(url, timeout=config.TIMEOUT_FAST)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    image = image.resize((350, 200), Image.Resampling.LANCZOS)
                    
                    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(350, 200))
                    
                    # Cache the image
                    self._thumbnail_cache[url] = ctk_image
                    
                    # Limit cache size
                    if len(self._thumbnail_cache) > config.THUMBNAIL_CACHE_SIZE:
                        oldest_key = next(iter(self._thumbnail_cache))
                        del self._thumbnail_cache[oldest_key]
                    
                    self.root.after(0, lambda: self.thumbnail_label.configure(
                        image=ctk_image, text=""
                    ))
                    
            except Exception as e:
                pass
        
        threading.Thread(target=load_worker, daemon=True).start()
    
    def _show_playlist_videos(self, info: Dict[str, Any]):
        """Show playlist videos in the list"""
        # Clear existing playlist items
        for widget in self.playlist_listbox.winfo_children():
            widget.destroy()
        
        # Show playlist frame
        self.playlist_frame.pack(fill="both", expand=True, pady=8)
        
        # Get playlist entries
        playlist_url = self.url_entry.get().strip()
        if not playlist_url:
            return
        
        def load_playlist_worker():
            try:
                entries = self.downloader.get_playlist_entries(playlist_url)
                
                self.root.after(0, lambda: self._populate_playlist_list(entries))
                
            except Exception as e:
                logger.error(f"Playlist loading error: {e}")
                self.root.after(0, lambda: self._show_error(f"Playlist yükleme hatası: {str(e)}"))
        
        threading.Thread(target=load_playlist_worker, daemon=True).start()
    
    def _populate_playlist_list(self, entries: list):
        """Populate the playlist list with video entries"""
        if not entries:
            no_videos_label = ctk.CTkLabel(
                self.playlist_listbox,
                text="❌ Playlist videoları yüklenemedi",
                font=ctk.CTkFont(size=10),
                text_color=("#ff6b6b", "#ff6b6b")
            )
            no_videos_label.pack(pady=5)
            return
        
        # Store playlist entries for tracking
        self.playlist_entries = entries[:20]  # Limit to first 20 videos
        self.playlist_download_status = {}  # Track download status for each video
        
        for i, entry in enumerate(self.playlist_entries):
            # Create a more structured video frame
            video_frame = ctk.CTkFrame(self.playlist_listbox, fg_color=("#f0f0f0", "#2b2b2b"))
            video_frame.pack(fill="x", padx=5, pady=3)
            
            # Video info
            title = entry.get('title', f'Video {i+1}')
            video_id = entry.get('id', '')
            url = entry.get('url', '')
            
            # Truncate long titles with better display
            display_title = title[:65] + "..." if len(title) > 65 else title
            
            # Create a horizontal layout container
            content_frame = ctk.CTkFrame(video_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=5)
            
            # Status indicator (initially hidden)
            status_label = ctk.CTkLabel(
                content_frame,
                text="⏳",
                font=ctk.CTkFont(size=14),
                text_color=("#ffa500", "#ffa500"),  # Orange for pending
                width=20
            )
            status_label.pack(side="left", padx=(5, 8), pady=5)
            
            # Video title label with better formatting and more space
            title_label = ctk.CTkLabel(
                content_frame,
                text=f"{i+1:2d}. {display_title}",
                font=ctk.CTkFont(size=11),
                anchor="center",
                justify="center"
            )
            title_label.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=5)
            
            # Progress label (initially hidden)
            progress_label = ctk.CTkLabel(
                content_frame,
                text="",
                font=ctk.CTkFont(size=10),
                text_color=("#888888", "#888888"),
                width=60
            )
            progress_label.pack(side="right", padx=(8, 5), pady=5)
            
            # Download button for this video with better styling
            download_btn = ctk.CTkButton(
                content_frame,
                text="⬇️",
                width=35,
                height=28,
                font=ctk.CTkFont(size=12),
                command=lambda u=url, t=title, idx=i+1: self._download_playlist_video(u, t, idx)
            )
            download_btn.pack(side="right", padx=(8, 10), pady=5)
            
            # Store references for status updates
            self.playlist_download_status[i] = {
                'frame': video_frame,
                'status_label': status_label,
                'progress_label': progress_label,
                'download_btn': download_btn,
                'title': title,
                'url': url,
                'index': i+1
            }
        
        # Bulk download button removed - now handled by dynamic main button
        
        if len(entries) > 20:
            more_label = ctk.CTkLabel(
                self.playlist_listbox,
                text=f"📋 ... ve {len(entries) - 20} video daha",
                font=ctk.CTkFont(size=10),
                text_color=("#888888", "#888888")
            )
            more_label.pack(pady=8)
    
    def _download_single_video(self, url: str, title: str):
        """Download a single video from playlist"""
        if not url:
            self._show_error("Geçersiz video URL'si")
            return
        
        # Update URL entry with the selected video URL
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        
        # Update status
        self.status_label.configure(text=f"Seçilen video: {title[:30]}...")
        
        # Auto-analyze the video
        self._analyze_video()
        
        pass
    
    def _download_playlist_video(self, url: str, title: str, video_index: int):
        """Download a single video from playlist with progress tracking"""
        if not url:
            self._show_error("Geçersiz video URL'si")
            return
        
        # Update progress tracking
        self.playlist_download_index = video_index
        
        # Update status with playlist info
        playlist_title = self.current_playlist_info.get('title', 'Playlist') if self.current_playlist_info else 'Playlist'
        playlist_name = playlist_title.split(' (')[0]  # Remove video count from title
        status_text = f"{playlist_name} - {video_index}/{self.playlist_total_videos} videosu indiriliyor"
        self.status_label.configure(text=status_text)
        
        # Reset progress bar
        self.progress_bar.set(0)
        self.progress_percent.configure(text="0%")
        self.download_start_time = time.time()
        
        # Get options
        audio_only = self.format_var.get() == "audio"
        max_height = config.get_quality_value(self.quality_var.get())
        
        # Create playlist-specific output directory
        playlist_output_dir = self._get_playlist_output_dir(playlist_name)
        
        def download_worker():
            try:
                # Temporarily update downloader output directory
                original_output_dir = self.downloader.output_dir
                self.downloader.output_dir = playlist_output_dir
                
                success = self.downloader.download(
                    url=url,
                    audio_only=audio_only,
                    max_height=max_height,
                    prefer_mp4=True,
                    no_playlist=True,
                    include_subs=False
                )
                
                # Restore original output directory
                self.downloader.output_dir = original_output_dir
                
                if success:
                    self.root.after(0, lambda: self.progress_bar.set(1.0))
                    self.root.after(0, lambda: self.progress_percent.configure(text="100%"))
                    self.root.after(0, lambda: self.status_label.configure(
                        text=f"✅ {playlist_name} - {video_index}/{self.playlist_total_videos} videosu tamamlandı"
                    ))
                    pass
                else:
                    self.root.after(0, lambda: self.status_label.configure(
                        text=f"❌ {playlist_name} - {video_index}/{self.playlist_total_videos} videosu başarısız"
                    ))
                    logger.error(f"Playlist video download failed: {title}")
                    
            except Exception as e:
                logger.error(f"Playlist video download error: {e}")
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"❌ Hata: {str(e)[:50]}..."
                ))
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _start_bulk_download(self):
        """Start bulk download of all playlist videos"""
        if not hasattr(self, 'playlist_entries') or not self.playlist_entries:
            self._show_error("Playlist videoları bulunamadı!")
            return
        
        if self.bulk_download_active:
            self._show_error("Zaten bir toplu indirme işlemi devam ediyor!")
            return
        
        # Confirm bulk download
        playlist_title = self.current_playlist_info.get('title', 'Playlist') if self.current_playlist_info else 'Playlist'
        playlist_name = playlist_title.split(' (')[0]  # Remove video count from title
        
        result = messagebox.askyesno(
            "Toplu İndirme Onayı",
            f"'{playlist_name}' playlist'indeki tüm videoları indirmek istiyor musunuz?\n\n"
            f"Toplam: {len(self.playlist_entries)} video\n"
            f"Bu işlem uzun sürebilir."
        )
        
        if not result:
            return
        
        # Get playlist output directory
        playlist_output_dir = self._get_playlist_output_dir(playlist_name)
        
        # Verify directory was created
        if not os.path.exists(playlist_output_dir):
            logger.error(f"Failed to create playlist directory: {playlist_output_dir}")
            self._show_error(f"Playlist klasörü oluşturulamadı: {playlist_output_dir}")
            return
        
        pass
        
        # Store playlist output directory for use in download functions
        self.current_playlist_output_dir = playlist_output_dir
        
        # Start bulk download
        self.bulk_download_active = True
        self.bulk_download_index = 0
        self.bulk_download_total = len(self.playlist_entries)
        
        # Reset progress bar for bulk download
        self.progress_bar.set(0)
        self.progress_percent.configure(text="0%")
        
        # Store initial progress state
        self.initial_progress = 0
        
        # Update status with folder information
        folder_name = os.path.basename(playlist_output_dir)
        self.status_label.configure(text=f"🚀 {playlist_name} - Toplu indirme başlatılıyor...\n📁 Klasör: {folder_name}")
        
        # Start first video download
        self._download_next_playlist_video()
    
    def _download_next_playlist_video(self):
        """Download next video in playlist sequence"""
        if not self.bulk_download_active or self.bulk_download_index >= self.bulk_download_total:
            self._finish_bulk_download()
            return
        
        # Get current video info
        current_video = self.playlist_entries[self.bulk_download_index]
        url = current_video.get('url', '')
        title = current_video.get('title', f'Video {self.bulk_download_index + 1}')
        
        # Update status for current video
        playlist_title = self.current_playlist_info.get('title', 'Playlist') if self.current_playlist_info else 'Playlist'
        playlist_name = playlist_title.split(' (')[0]
        
        # Calculate current progress percentage for bulk download
        current_progress = int(((self.bulk_download_index + 1) / self.bulk_download_total) * 100)
        status_text = f"🚀 {playlist_name} - [{self.bulk_download_index + 1}/{self.bulk_download_total}] videosu indiriliyor | 📊 Progress: {current_progress}%"
        self.status_label.configure(text=status_text)
        
        # Update video status in playlist
        self._update_playlist_video_status(self.bulk_download_index, "downloading", "0%")
        
        # Get options
        audio_only = self.format_var.get() == "audio"
        max_height = config.get_quality_value(self.quality_var.get())
        
        # Use the playlist output directory created in _start_bulk_download
        playlist_output_dir = getattr(self, 'current_playlist_output_dir', None)
        if not playlist_output_dir:
            logger.error("Playlist output directory not found!")
            self._show_error("Playlist klasörü bulunamadı!")
            return
        
        def download_worker():
            try:
                # Temporarily update downloader output directory
                original_output_dir = self.downloader.output_dir
                self.downloader.output_dir = playlist_output_dir
                
                success = self.downloader.download(
                    url=url,
                    audio_only=audio_only,
                    max_height=max_height,
                    prefer_mp4=True,
                    no_playlist=True,
                    include_subs=False
                )
                
                # Restore original output directory
                self.downloader.output_dir = original_output_dir
                
                if success:
                    # Update video status to completed
                    self.root.after(0, lambda: self._update_playlist_video_status(
                        self.bulk_download_index, "completed", "100%"
                    ))
                    
                    # Update overall progress - each video adds 1/total to progress
                    # For 10 videos: 1st video = 10%, 2nd video = 20%, ..., 10th video = 100%
                    progress = (self.bulk_download_index + 1) / self.bulk_download_total
                    
                    # Ensure progress is between 0 and 1
                    progress = max(0.0, min(1.0, progress))
                    
                    # Update progress bar (0.0 to 1.0) - BULK DOWNLOAD PROGRESS
                    self.root.after(0, lambda: self.progress_bar.set(progress))
                    
                    # Update percentage text (0% to 100%) - BULK DOWNLOAD PERCENTAGE
                    percentage = int(progress * 100)
                    self.root.after(0, lambda: self.progress_percent.configure(
                        text=f"📋 Playlist[{self.bulk_download_index + 1}/{self.bulk_download_total}] {percentage}%"
                    ))
                    
                    pass
                else:
                    # Update video status to failed
                    self.root.after(0, lambda: self._update_playlist_video_status(
                        self.bulk_download_index, "failed", "❌"
                    ))
                    
                    logger.error(f"Bulk download video failed: {title}")
                
                # Move to next video
                self.bulk_download_index += 1
                
                # Download next video after a short delay
                self.root.after(1000, self._download_next_playlist_video)
                    
            except Exception as e:
                logger.error(f"Bulk download error: {e}")
                self.root.after(0, lambda: self._update_playlist_video_status(
                    self.bulk_download_index, "failed", "❌"
                ))
                
                # Move to next video even if failed
                self.bulk_download_index += 1
                self.root.after(1000, self._download_next_playlist_video)
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _finish_bulk_download(self):
        """Finish bulk download process"""
        self.bulk_download_active = False
        
        # Update final status
        playlist_title = self.current_playlist_info.get('title', 'Playlist') if self.current_playlist_info else 'Playlist'
        playlist_name = playlist_title.split(' (')[0]
        
        completed_count = sum(1 for status in self.playlist_download_status.values() 
                            if status.get('status') == 'completed')
        
        # Use the playlist output directory created in _start_bulk_download
        playlist_output_dir = getattr(self, 'current_playlist_output_dir', None)
        if not playlist_output_dir:
            logger.error("Playlist output directory not found in finish!")
            return
        folder_name = os.path.basename(playlist_output_dir)
        
        if completed_count == self.bulk_download_total:
            self.status_label.configure(text=f"✅ {playlist_name} - Tüm videolar başarıyla indirildi! (100%)\n📁 Klasör: {folder_name}")
            self.progress_bar.set(1.0)
            self.progress_percent.configure(text="📋 Playlist[10/10] 100% (Tüm videolar tamamlandı)")
            
            # Ask user if they want to open the folder
            self.root.after(1000, lambda: self._ask_open_playlist_folder(playlist_output_dir, playlist_name))
        else:
            failed_count = self.bulk_download_total - completed_count
            final_progress = int((completed_count / self.bulk_download_total) * 100)
            self.status_label.configure(text=f"⚠️ {playlist_name} - {completed_count} video indirildi, {failed_count} video başarısız ({final_progress}%)\n📁 Klasör: {folder_name}")
            # Update progress bar to show final state
            final_progress_bar = completed_count / self.bulk_download_total
            self.progress_bar.set(final_progress_bar)
            self.progress_percent.configure(text=f"📋 Playlist[{completed_count}/{self.bulk_download_total}] {final_progress}%")
        
        pass
    
    def _ask_open_playlist_folder(self, folder_path: str, playlist_name: str):
        """Ask user if they want to open the playlist folder"""
        try:
            result = messagebox.askyesno(
                "Klasör Açma",
                f"'{playlist_name}' playlist'indeki tüm videolar indirildi!\n\n"
                f"Klasörü açmak istiyor musunuz?\n"
                f"📁 {os.path.basename(folder_path)}"
            )
            
            if result:
                self._open_playlist_folder(folder_path)
                
        except Exception as e:
            pass
    
    def _open_playlist_folder(self, folder_path: str):
        """Open the playlist folder in file explorer"""
        try:
            from utils import open_directory_safely
            
            if open_directory_safely(folder_path):
                pass
            else:
                raise Exception("Tüm yöntemler başarısız oldu")
                
        except Exception as e:
            logger.error(f"Error opening playlist folder: {e}")
            # Show alternative ways to open the folder
            error_msg = f"Klasör açılamadı: {folder_path}\n\nAlternatif çözümler:\n1. Windows Explorer'ı açın\n2. Adres çubuğuna şunu yazın:\n{folder_path}\n\n3. Veya şu komutu çalıştırın:\ncmd /c start explorer \"{folder_path}\""
            messagebox.showerror("Klasör Açılamadı", error_msg)
    
    def _update_playlist_video_status(self, video_index: int, status: str, progress_text: str):
        """Update status of a specific playlist video"""
        if video_index not in self.playlist_download_status:
            return
        
        video_status = self.playlist_download_status[video_index]
        status_label = video_status['status_label']
        progress_label = video_status['progress_label']
        download_btn = video_status['download_btn']
        
        if status == "downloading":
            status_label.configure(text="⏳", text_color=("#ffa500", "#ffa500"))  # Orange
            progress_label.configure(text=progress_text)
            download_btn.configure(state="disabled", text="⏳")
            # Store status for completion tracking
            video_status['status'] = 'downloading'
            
        elif status == "completed":
            status_label.configure(text="✅", text_color=("#4CAF50", "#4CAF50"))  # Green
            progress_label.configure(text="✅")
            download_btn.configure(state="disabled", text="✅", fg_color=("#4CAF50", "#4CAF50"))
            # Store status for completion tracking
            video_status['status'] = 'completed'
            
        elif status == "failed":
            status_label.configure(text="❌", text_color=("#f44336", "#f44336"))  # Red
            progress_label.configure(text="❌")
            download_btn.configure(state="disabled", text="❌")
            # Store status for completion tracking
            video_status['status'] = 'failed'
    
    def _get_playlist_output_dir(self, playlist_name: str) -> str:
        """Get playlist-specific output directory with date and better naming"""
        import re
        from datetime import datetime
        
        # Clean playlist name for folder name
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', playlist_name)
        clean_name = clean_name.strip()[:40]  # Limit length
        
        # Add current date and time for better organization
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Create folder name: PlaylistName_YYYY-MM-DD_HH-MM
        folder_name = f"{clean_name}_{current_datetime}"
        
        playlist_dir = os.path.join(self.output_dir, folder_name)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(playlist_dir, exist_ok=True)
            
            # Verify directory was created
            if os.path.exists(playlist_dir):
                pass
            else:
                logger.error(f"Failed to create directory: {playlist_dir}")
                
        except Exception as e:
            logger.error(f"Error creating playlist directory: {e}")
            raise
        
        return playlist_dir
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.output_label.configure(text=directory)
            if self.downloader:
                self.downloader.output_dir = directory
            pass
    
    def _open_output_dir(self):
        """Open output directory in file explorer"""
        try:
            from utils import open_directory_safely
            
            if open_directory_safely(self.output_dir):
                pass
            else:
                raise Exception("Tüm yöntemler başarısız oldu")
                
        except Exception as e:
            logger.error(f"Error opening directory: {e}")
            # Daha kullanıcı dostu hata mesajı ve alternatif çözümler
            error_msg = f"Klasör açılamadı: {self.output_dir}\n\nAlternatif çözümler:\n1. Windows Explorer'ı açın\n2. Adres çubuğuna şunu yazın:\n{self.output_dir}\n\n3. Veya şu komutu çalıştırın:\ncmd /c start explorer \"{self.output_dir}\""
            messagebox.showerror("Klasör Açılamadı", error_msg)
    
    def _on_format_change(self):
        """Handle format change"""
        format_type = self.format_var.get()
        pass
        
        # Update quality options based on format
        if format_type == "audio":
            # For audio, we don't need video quality options
            pass
        else:
            # For video, ensure quality is set
            pass
    
    def _start_download(self):
        """Start download process"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin!")
            return
        
        # Update UI
        self.download_btn.configure(state="disabled", text="📡 İNDİRİLİYOR...")
        
        # Only reset progress bar if not in bulk download mode
        if not hasattr(self, 'bulk_download_active') or not self.bulk_download_active:
            self.progress_bar.set(0)
            self.progress_percent.configure(text="0%")
        
        self.status_label.configure(text="İndirme başlatılıyor...")
        self.download_start_time = time.time()
        
        # Reset playlist download tracking for single video downloads
        if not self.current_playlist_info:
            self.playlist_download_index = 0
            self.playlist_total_videos = 0
        
        # If we're in a playlist context, create playlist folder for single video downloads
        playlist_output_dir = None
        if self.current_playlist_info:
            playlist_title = self.current_playlist_info.get('title', 'Playlist')
            playlist_name = playlist_title.split(' (')[0]
            try:
                playlist_output_dir = self._get_playlist_output_dir(playlist_name)
                pass
            except Exception as e:
                logger.error(f"Failed to create playlist folder for single video: {e}")
        
        # Get options
        audio_only = self.format_var.get() == "audio"
        max_height = config.get_quality_value(self.quality_var.get())
        
        def download_worker():
            try:
                success = self.downloader.download(
                    url=url,
                    audio_only=audio_only,
                    max_height=max_height,
                    prefer_mp4=True,
                    no_playlist=True,
                    include_subs=False
                )
                
                if success:
                    self.root.after(0, lambda: self.status_label.configure(
                        text="🎉 İndirme başarıyla tamamlandı!"
                    ))
                    self.root.after(0, lambda: self.progress_bar.set(1.0))
                    self.root.after(0, lambda: self.progress_percent.configure(text="100%"))
                    pass
                else:
                    self.root.after(0, lambda: self.status_label.configure(
                        text="❌ İndirme başarısız"
                    ))
                    logger.error("Download failed")
                    
            except Exception as e:
                logger.error(f"Download error: {e}")
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"❌ Hata: {str(e)[:50]}..."
                ))
            finally:
                self.root.after(0, lambda: self.download_btn.configure(
                    state="normal", text="⬇️ İNDİR"
                ))
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _progress_callback(self, data: Dict[str, Any]):
        """Handle download progress updates"""
        if not hasattr(self, 'download_start_time') or not self.download_start_time:
            self.download_start_time = time.time()
        
        try:
            if data['status'] == 'downloading':
                # Extract percentage with multiple fallback methods
                percent = 0.0
                
                # Method 1: Try _percent_str first
                if '_percent_str' in data and data['_percent_str']:
                    try:
                        percent_str = data['_percent_str'].replace('%', '').strip()
                        if percent_str and percent_str != 'N/A':
                            percent = float(percent_str) / 100.0
                    except (ValueError, TypeError):
                        pass
                
                # Method 2: Calculate from downloaded/total bytes
                if percent == 0.0 and 'downloaded_bytes' in data and 'total_bytes' in data:
                    downloaded = data.get('downloaded_bytes', 0)
                    total = data.get('total_bytes', 0) or data.get('total_bytes_estimate', 0)
                    if total > 0 and downloaded > 0:
                        percent = min(downloaded / total, 1.0)
                
                # Method 3: Calculate from downloaded/total bytes estimate
                if percent == 0.0 and 'downloaded_bytes' in data and 'total_bytes_estimate' in data:
                    downloaded = data.get('downloaded_bytes', 0)
                    total_estimate = data.get('total_bytes_estimate', 0)
                    if total_estimate > 0 and downloaded > 0:
                        percent = min(downloaded / total_estimate, 1.0)
                
                # Ensure percent is valid
                if not isinstance(percent, (int, float)) or percent < 0:
                    percent = 0.0
                elif percent > 1.0:
                    percent = 1.0
                
                # Update progress bar and percentage (use after_idle for better performance)
                # But don't update if we're in bulk download mode (let bulk download handle progress)
                if not hasattr(self, 'bulk_download_active') or not self.bulk_download_active:
                    self.root.after_idle(lambda p=percent: self.progress_bar.set(p))
                    self.root.after_idle(lambda p=percent: self.progress_percent.configure(text=f"{p*100:.1f}%"))
                
                # Format speed
                speed = data.get('speed', 0)
                if isinstance(speed, (int, float)) and speed > 0:
                    if speed > 1024*1024:  # MB/s
                        speed_str = f"{speed/(1024*1024):.1f} MB/s"
                    elif speed > 1024:  # KB/s
                        speed_str = f"{speed/1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed:.0f} B/s"
                else:
                    speed_str = "Hesaplanıyor..."
                
                # Format ETA
                eta = data.get('eta', 0)
                if isinstance(eta, (int, float)) and eta > 0:
                    if eta > 60:
                        eta_str = f"{int(eta//60)}dk {int(eta%60)}s"
                    else:
                        eta_str = f"{int(eta)}s"
                else:
                    eta_str = "Hesaplanıyor..."
                
                # Calculate elapsed time
                elapsed = time.time() - self.download_start_time
                if elapsed > 60:
                    elapsed_str = f"{int(elapsed//60)}dk {int(elapsed%60)}s"
                else:
                    elapsed_str = f"{int(elapsed)}s"
                
                # Format file size information
                downloaded_size = data.get('downloaded_bytes', 0)
                total_size = data.get('total_bytes', 0) or data.get('total_bytes_estimate', 0)
                
                if downloaded_size > 0 and total_size > 0:
                    downloaded_mb = downloaded_size / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    size_info = f"📁 {downloaded_mb:.1f}MB / {total_mb:.1f}MB"
                elif downloaded_size > 0:
                    downloaded_mb = downloaded_size / (1024 * 1024)
                    size_info = f"📁 {downloaded_mb:.1f}MB"
                else:
                    size_info = "📁 Hesaplanıyor..."
                
                # Update status with playlist info if available
                if self.current_playlist_info and self.playlist_download_index > 0:
                    playlist_title = self.current_playlist_info.get('title', 'Playlist')
                    playlist_name = playlist_title.split(' (')[0]  # Remove video count from title
                    status_text = f"📋 {playlist_name} - [{self.playlist_download_index}/{self.playlist_total_videos}] videosu | ⬇️ {percent*100:.1f}% | {size_info} | 🚀 {speed_str} | ⏱️ Kalan: {eta_str}"
                else:
                    status_text = f"⬇️ {percent*100:.1f}% | {size_info} | 🚀 {speed_str} | ⏱️ Kalan: {eta_str} | 🕑 Geçen: {elapsed_str}"
                
                self.root.after_idle(lambda text=status_text: self.status_label.configure(text=text))
                
            elif data['status'] == 'finished':
                self.root.after_idle(lambda: self.progress_bar.set(1.0))
                self.root.after_idle(lambda: self.progress_percent.configure(text="100%"))
                pass
                
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
            logger.error(f"Progress data: {data}")
    
    def _status_callback(self, message: str):
        """Handle status updates"""
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def _error_callback(self, error: str):
        """Handle errors"""
        self.root.after(0, lambda: self._show_error(error))
    
    def _show_error(self, error: str):
        """Show error message"""
        self.status_label.configure(text=f"❌ {error}")
        messagebox.showerror("Hata", error)
        pass
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"GUI runtime error: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        try:
            if self.downloader:
                self.downloader.cleanup()
            pass
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


if __name__ == "__main__":
    app = StreamScribeOptimizedGUI()
    app.run()
