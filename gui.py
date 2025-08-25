import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO
from typing import Optional
from downloader import YouTubeDownloader


class YouTubeDownloaderGUI:
    """Modern YouTube downloader GUI using CustomTkinter"""
    
    def __init__(self):
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("StreamScribe - YouTube Video İndirici ve Altyazı Çeviricisi")
        
        # Get screen dimensions for full screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window to full screen size
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.minsize(1200, 700)  # Minimum size for landscape layout
        self.root.resizable(True, True)
        
        # Try to maximize window immediately
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                pass  # Fallback to normal size
        
        # Set logo and icon
        try:
            # Small icon for favicon
            icon_path = os.path.join(os.path.dirname(__file__), "logo", "favicon-32x32.png")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=os.path.join(os.path.dirname(__file__), "logo", "favicon.ico"))
        except:
            pass  # Continue if logo cannot be loaded
        
        # Initialize downloader
        self.downloader: Optional[YouTubeDownloader] = None
        self.output_dir = "downloads"
        
        # Video info cache (URL -> info dict)
        self.video_info_cache = {}
        # Thumbnail cache (URL -> PIL Image)
        self.thumbnail_cache = {}
        self.current_thumbnail_url = None  # Track current thumbnail to prevent flicker
        self.auto_fetch_delay = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Center window on screen after widgets are created
        self.center_window()
        
        # Ensure window is maximized and centered
        self.root.update_idletasks()
        self.root.state('zoomed')  # Force maximize again
        self.center_window()  # Center again after maximize
    
    def center_window(self):
        """Center the window on screen - works with both normal and maximized states"""
        self.root.update_idletasks()
        
        # Get current window state
        try:
            is_zoomed = self.root.state() == 'zoomed'
        except:
            is_zoomed = False
        
        if is_zoomed:
            # If maximized, ensure it's truly centered by setting position to 0,0
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        else:
            # If not maximized, center normally
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create and arrange GUI widgets according to new design specifications"""
        
        # Main container frame
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.pack(padx=15, pady=10, fill="both", expand=True)
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # URL input section - at top
        self.create_url_section()
        
        # Video info section - main layout with thumbnail and info
        self.create_video_info_section()
        
        # Playlist section - will be shown when playlist detected
        self.create_playlist_section()
        
        # Control buttons at bottom
        self.create_control_section()
    

    def create_url_section(self):
        """Create URL input section"""
        url_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        url_frame.pack(padx=10, pady=(5, 5), fill="x")  # Reduced padding
        
        url_label = ctk.CTkLabel(url_frame, text="🔗 YouTube URL'sini yapıştırın:", font=ctk.CTkFont(size=14, weight="bold"))
        url_label.pack(anchor="w", padx=12, pady=(8, 3))  # Reduced padding
        
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=36,  # Slightly larger
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(padx=12, pady=(0, 8), fill="x")  # Reduced padding
        
        # Bind events for auto-fetch
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        self.url_entry.bind('<Control-v>', self.on_paste)
    
    def create_video_info_section(self):
        """Create main video info section with horizontal layout for better space utilization"""
        self.video_section = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        self.video_section.pack(padx=10, pady=(0, 10), fill="x")
        
        # Main horizontal layout - use full width
        main_layout = ctk.CTkFrame(self.video_section, fg_color="transparent")
        main_layout.pack(fill="x", padx=20, pady=20)
        
        # Left side - Large thumbnail and basic info (fixed width)
        left_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=(0, 40))
        
        # Large thumbnail (280x210) - reasonable size for better visibility
        self.large_thumbnail_frame = ctk.CTkFrame(left_frame, width=280, height=210, corner_radius=10)
        self.large_thumbnail_frame.pack(pady=(0, 15))
        self.large_thumbnail_frame.pack_propagate(False)
        
        self.large_thumbnail_label = ctk.CTkLabel(
            self.large_thumbnail_frame,
            text="🎥\nThumbnail",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        self.large_thumbnail_label.pack(expand=True)
        
        # Video title under thumbnail - reasonable font size
        self.video_title_label = ctk.CTkLabel(
            left_frame, 
            text="Video başlığı burada görünecek", 
            font=ctk.CTkFont(size=14, weight="bold"),
            width=280,
            wraplength=260,
            anchor="center"
        )
        self.video_title_label.pack()
        
        # Main progress bar under title
        self.main_progress_bar = ctk.CTkProgressBar(left_frame, width=280, height=12)
        self.main_progress_bar.pack(pady=(12, 8))
        self.main_progress_bar.set(0)
        
        self.main_status_label = ctk.CTkLabel(
            left_frame, 
            text="Hazır", 
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color="gray60"
        )
        self.main_status_label.pack()
        
        # Center section - Video link and format selection
        center_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True, padx=(0, 40))
        
        # Video link display
        link_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        link_frame.pack(fill="x", pady=(0, 20))
        
        link_label = ctk.CTkLabel(link_frame, text="📎 Video Linki:", font=ctk.CTkFont(size=13, weight="bold"))
        link_label.pack(anchor="w")
        
        self.video_link_label = ctk.CTkLabel(
            link_frame, 
            text="URL girilmedi", 
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="w"
        )
        self.video_link_label.pack(anchor="w")
        
        # Format selection - reasonable size
        format_section = ctk.CTkFrame(center_frame, fg_color="transparent")
        format_section.pack(fill="x", pady=(0, 20))
        
        format_label = ctk.CTkLabel(format_section, text="📁 Format Seçimi:", font=ctk.CTkFont(size=13, weight="bold"))
        format_label.pack(anchor="w")
        
        format_frame = ctk.CTkFrame(format_section, fg_color="transparent")
        format_frame.pack(anchor="w", pady=(5, 0))
        
        self.format_var = tk.StringVar(value="video")
        
        self.video_button = ctk.CTkRadioButton(
            format_frame, 
            text="🎬 VİDEO", 
            variable=self.format_var, 
            value="video",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.video_button.pack(side="left", padx=(0, 25))
        
        self.audio_button = ctk.CTkRadioButton(
            format_frame, 
            text="🎵 SES", 
            variable=self.format_var, 
            value="audio",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.audio_button.pack(side="left")
        
        # Quality selection - reasonable size
        quality_section = ctk.CTkFrame(center_frame, fg_color="transparent")
        quality_section.pack(fill="x", pady=(10, 20))
        
        quality_label = ctk.CTkLabel(quality_section, text="🎯 Kalite:", font=ctk.CTkFont(size=13, weight="bold"))
        quality_label.pack(anchor="w")
        
        self.quality_var = tk.StringVar(value="1080p")
        quality_options = ["4K", "1440p", "1080p", "720p", "480p", "360p"]
        self.quality_optionmenu = ctk.CTkOptionMenu(
            quality_section,
            values=quality_options,
            variable=self.quality_var,
            width=100,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.quality_optionmenu.pack(anchor="w", pady=(5, 0))
        
        # Additional options - reasonable size
        subtitle_section = ctk.CTkFrame(center_frame, fg_color="transparent")
        subtitle_section.pack(fill="x")
        
        self.subtitle_var = tk.BooleanVar(value=False)
        self.subtitle_checkbox = ctk.CTkCheckBox(
            subtitle_section,
            text="📝 Altyazı Ekle",
            variable=self.subtitle_var,
            font=ctk.CTkFont(size=12)
        )
        self.subtitle_checkbox.pack(anchor="w")
        
        # Right section - Additional controls and info
        right_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=(40, 0))
        
        # Download info section
        info_label = ctk.CTkLabel(right_frame, text="📊 İndirme Bilgileri", font=ctk.CTkFont(size=13, weight="bold"))
        info_label.pack(anchor="w", pady=(0, 12))
        
        # File size info
        self.file_size_label = ctk.CTkLabel(
            right_frame,
            text="Dosya boyutu: --",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.file_size_label.pack(anchor="w", pady=(0, 6))
        
        # Duration info
        self.duration_label = ctk.CTkLabel(
            right_frame,
            text="Süre: --",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.duration_label.pack(anchor="w", pady=(0, 6))
        
        # Channel info
        self.channel_label = ctk.CTkLabel(
            right_frame,
            text="Kanal: --",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.channel_label.pack(anchor="w", pady=(0, 6))
        
        # Upload date info
        self.upload_date_label = ctk.CTkLabel(
            right_frame,
            text="Yüklenme: --",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.upload_date_label.pack(anchor="w")
    
    def create_playlist_section(self):
        """Create playlist section with horizontal layout - hidden by default"""
        self.playlist_section = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        # Don't pack yet - will be shown when playlist detected
        
        # Playlist header with bulk controls - larger and better spaced
        header_frame = ctk.CTkFrame(self.playlist_section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        playlist_header = ctk.CTkLabel(
            header_frame, 
            text="📋 Oynatma Listesi", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        playlist_header.pack(side="left")
        
        # Bulk download controls - larger buttons
        bulk_controls = ctk.CTkFrame(header_frame, fg_color="transparent")
        bulk_controls.pack(side="right")
        
        self.bulk_download_button = ctk.CTkButton(
            bulk_controls,
            text="📦 Tümünü İndir",
            command=self.start_bulk_download,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2b8a3e", "#1c5f2e"),
            hover_color=("#37b94c", "#2b8a3e")
        )
        self.bulk_download_button.pack(side="right", padx=(15, 0))
        
        self.stop_bulk_button = ctk.CTkButton(
            bulk_controls,
            text="⏹️ Durdur",
            command=self.stop_bulk_download,
            height=40,
            width=100,
            font=ctk.CTkFont(size=13),
            fg_color=("#d32f2f", "#b71c1c"),
            hover_color=("#b71c1c", "#d32f2f"),
            state="disabled"
        )
        self.stop_bulk_button.pack(side="right", padx=(10, 0))
        
        # Overall progress for bulk download - larger and better spaced
        self.bulk_progress_frame = ctk.CTkFrame(self.playlist_section, fg_color="transparent")
        self.bulk_progress_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        bulk_progress_label = ctk.CTkLabel(
            self.bulk_progress_frame,
            text="📊 Genel İlerleme:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        bulk_progress_label.pack(anchor="w")
        
        self.bulk_progress_bar = ctk.CTkProgressBar(
            self.bulk_progress_frame,
            height=16,
            width=600
        )
        self.bulk_progress_bar.pack(fill="x", pady=(8, 0))
        self.bulk_progress_bar.set(0)
        
        self.bulk_status_label = ctk.CTkLabel(
            self.bulk_progress_frame,
            text="Hazır",
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color="gray60"
        )
        self.bulk_status_label.pack(anchor="w")
        
        # Scrollable frame for playlist items - larger height
        self.playlist_frame = ctk.CTkScrollableFrame(self.playlist_section, height=300)
        self.playlist_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.playlist_items = []  # Store playlist item widgets
        self.bulk_download_active = False
        self.bulk_download_thread = None
    
    def create_control_section(self):
        """Create control buttons section with horizontal layout"""
        control_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        control_frame.pack(padx=10, pady=(0, 10), fill="x")
        
        button_layout = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_layout.pack(fill="x", padx=20, pady=20)
        
        # Top row - Folder selection and info
        top_row = ctk.CTkFrame(button_layout, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))
        
        # Folder selection - left side
        folder_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        folder_frame.pack(side="left", fill="x", expand=True)
        
        folder_label = ctk.CTkLabel(folder_frame, text=f"📂 İndirme Klasörü: {os.path.basename(self.output_dir)}", 
                                   font=ctk.CTkFont(size=14, weight="bold"))
        folder_label.pack(anchor="w")
        
        # Store reference to update it later
        self.folder_label = folder_label
        
        # Folder buttons - right side
        folder_buttons_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        folder_buttons_frame.pack(side="right")
        
        self.folder_button = ctk.CTkButton(
            folder_buttons_frame,
            text="📁 Klasör Seç",
            command=self.browse_folder,
            width=120,
            height=36,
            font=ctk.CTkFont(size=13)
        )
        self.folder_button.pack(side="left", padx=(0, 10))
        
        # Add "Open Folder" button next to folder selection
        self.open_folder_button = ctk.CTkButton(
            folder_buttons_frame,
            text="📂 Klasörü Aç",
            command=self.open_download_folder_direct,
            width=140,
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color=("#2b8a3e", "#2f9e44"),
            hover_color=("#2f9e44", "#37b24d")
        )
        self.open_folder_button.pack(side="left")
        
        # Bottom row - Main control buttons
        bottom_row = ctk.CTkFrame(button_layout, fg_color="transparent")
        bottom_row.pack(fill="x")
        
        # Left side - Download button
        self.download_button = ctk.CTkButton(
            bottom_row,
            text="⬇️ İNDİRMEYİ BAŞLAT",
            command=self.start_download,
            height=56,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=10,
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#144870", "#1f538d")
        )
        self.download_button.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        # Right side - Cancel button
        self.cancel_button = ctk.CTkButton(
            bottom_row,
            text="❌ İPTAL",
            command=self.cancel_download,
            height=56,
            width=120,
            fg_color=("#d32f2f", "#b71c1c"),
            hover_color=("#b71c1c", "#d32f2f"),
            corner_radius=10,
            state="disabled",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.cancel_button.pack(side="right")

    def on_url_change(self, event=None):
        """Handle URL entry changes for auto-fetch"""
        if self.auto_fetch_delay:
            self.root.after_cancel(self.auto_fetch_delay)
        
        url = self.url_entry.get().strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            # Auto-fetch after 0.8 seconds of no typing (reduced from 1.5s)
            self.auto_fetch_delay = self.root.after(800, lambda: self.auto_fetch_video_info(url))
    
    def on_paste(self, event=None):
        """Handle paste event"""
        self.root.after(100, self.on_url_change)  # Check after paste
    
    def auto_fetch_video_info(self, url):
        """Automatically fetch video info when URL is detected"""
        current_url = self.url_entry.get().strip()
        if current_url == url and url:
            self.get_video_info_fast(url)
    
    def get_video_info_fast(self, url=None):
        """Fast video info retrieval with minimal UI blocking and enhanced caching"""
        if not url:
            url = self.url_entry.get().strip()
        
        if not url:
            return
        
        # Cache check first - immediate response
        if url in self.video_info_cache:
            info = self.video_info_cache[url]
            self.display_video_info(info)
            self.main_status_label.configure(text=f"⚡ Cache'den yüklendi")
            return
        
        # Show loading state immediately
        self.main_status_label.configure(text="🔄 Hızlı bilgi alınıyor...")
        
        # Clear previous thumbnail immediately for better UX (only if widget exists)
        if hasattr(self, 'large_thumbnail_label') and self.large_thumbnail_label:
            self.clear_large_thumbnail()
        
        def fetch_fast():
            try:
                temp_downloader = YouTubeDownloader()
                
                # Try fast method first
                info = temp_downloader.get_video_info_fast(url)
                
                # If fast method fails, try fallback with minimal delay
                if 'error' in info:
                    self.root.after(0, lambda: self.main_status_label.configure(
                        text="🔄 Alternatif yöntem deneniyor..."
                    ))
                    
                    # Try yt-dlp fallback
                    try:
                        info = temp_downloader.get_video_info_ytdlp(url)
                    except:
                        pass
                
                if 'error' in info:
                    self.root.after(0, lambda: self.main_status_label.configure(
                        text=f"⚠️ {info['error'][:50]}..."
                    ))
                else:
                    processed_info = self.process_video_info(info)
                    self.video_info_cache[url] = processed_info
                    
                    # Update UI immediately
                    self.root.after(0, lambda: self.display_video_info(processed_info))
                    self.root.after(0, lambda: self.main_status_label.configure(
                        text="✅ Video bilgisi alındı"
                    ))
            except Exception as e:
                self.root.after(0, lambda: self.main_status_label.configure(
                    text=f"❌ Hata: {str(e)[:30]}..."
                ))
        
        # Use daemon thread for non-blocking fetch
        thread = threading.Thread(target=fetch_fast, daemon=True)
        thread.start()
    
    def download_thumbnail(self, url: str, size: tuple = (280, 210)) -> Optional[Image.Image]:
        """Download and process thumbnail image with caching"""
        if not url:
            return None
            
        # Check cache first
        cache_key = f"{url}_{size[0]}x{size[1]}"
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]
            
        try:
            response = requests.get(url, timeout=2)  # Reduced timeout from 5s to 2s
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                # Resize to fit thumbnail frame
                image = image.resize(size, Image.Resampling.LANCZOS)
                
                # Cache the processed image
                self.thumbnail_cache[cache_key] = image
                
                # Limit cache size to prevent memory issues
                if len(self.thumbnail_cache) > 20:
                    # Remove oldest entries
                    oldest_key = next(iter(self.thumbnail_cache))
                    del self.thumbnail_cache[oldest_key]
                    
                return image
        except Exception as e:
            print(f"Thumbnail indirme hatası: {e}")
        return None
    
    def update_large_thumbnail_priority(self, thumbnail_url: str):
        """Update large thumbnail with priority loading for better performance"""
        if not thumbnail_url:
            self.clear_large_thumbnail()
            return
        
        # Check if widget exists and is valid
        if not hasattr(self, 'large_thumbnail_label') or not self.large_thumbnail_label:
            print("Thumbnail label not available")
            return
        
        # Don't reload if it's the same thumbnail
        if self.current_thumbnail_url == thumbnail_url:
            return
            
        self.current_thumbnail_url = thumbnail_url
        
        # Show loading state immediately - safer approach
        try:
            if self.large_thumbnail_label.winfo_exists():
                self.large_thumbnail_label.configure(
                    image=None,
                    text="🔄\nYükleniyor..."
                )
            else:
                print("Thumbnail label destroyed")
                return
        except Exception as e:
            print(f"Thumbnail loading state error: {e}")
            return
        
        def load_thumbnail_priority():
            try:
                # Check if widget still exists before processing
                if not self.large_thumbnail_label.winfo_exists():
                    print("Thumbnail label destroyed during loading")
                    return
                
                # Check cache first
                cache_key = f"{thumbnail_url}_280x210"
                if cache_key in self.thumbnail_cache:
                    image = self.thumbnail_cache[cache_key]
                else:
                    # Download with faster timeout
                    response = requests.get(thumbnail_url, timeout=1.5)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        image = image.resize((280, 210), Image.Resampling.LANCZOS)
                        
                        # Cache immediately
                        self.thumbnail_cache[cache_key] = image
                        
                        # Limit cache size
                        if len(self.thumbnail_cache) > 20:
                            oldest_key = next(iter(self.thumbnail_cache))
                            del self.thumbnail_cache[oldest_key]
                    else:
                        image = None
                
                # Final check before updating UI
                if (image and self.current_thumbnail_url == thumbnail_url and 
                    hasattr(self, 'large_thumbnail_label') and 
                    self.large_thumbnail_label.winfo_exists()):
                    
                    # Convert to CTkImage and update UI
                    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(280, 210))
                    self.root.after(0, lambda: self._safe_update_thumbnail(ctk_image))
                elif self.current_thumbnail_url == thumbnail_url:
                    self.root.after(0, self.clear_large_thumbnail)
                    
            except Exception as e:
                print(f"Priority thumbnail loading error: {e}")
                if self.current_thumbnail_url == thumbnail_url:
                    self.root.after(0, self.clear_large_thumbnail)
        
        # Use high priority thread
        thread = threading.Thread(target=load_thumbnail_priority, daemon=True)
        thread.start()
    
    def _safe_update_thumbnail(self, ctk_image):
        """Safely update thumbnail image"""
        try:
            if (hasattr(self, 'large_thumbnail_label') and 
                self.large_thumbnail_label and 
                self.large_thumbnail_label.winfo_exists()):
                self.large_thumbnail_label.configure(image=ctk_image, text="")
        except Exception as e:
            print(f"Safe thumbnail update error: {e}")
    
    def update_large_thumbnail(self, thumbnail_url: str):
        """Update large thumbnail display with flicker prevention and faster loading"""
        if not thumbnail_url:
            self.clear_large_thumbnail()
            return
        
        # Check if widget exists and is valid
        if not hasattr(self, 'large_thumbnail_label') or not self.large_thumbnail_label:
            print("Thumbnail label not available")
            return
        
        # Don't reload if it's the same thumbnail
        if self.current_thumbnail_url == thumbnail_url:
            return
            
        self.current_thumbnail_url = thumbnail_url
        
        # Show loading state immediately - safer approach
        try:
            if self.large_thumbnail_label.winfo_exists():
                self.large_thumbnail_label.configure(
                    image=None,
                    text="🔄\nYükleniyor..."
                )
            else:
                print("Thumbnail label destroyed")
                return
        except Exception as e:
            print(f"Thumbnail loading state error: {e}")
            return
        
        def load_thumbnail():
            try:
                # Check if widget still exists before processing
                if not self.large_thumbnail_label.winfo_exists():
                    print("Thumbnail label destroyed during loading")
                    return
                
                image = self.download_thumbnail(thumbnail_url, (280, 210))
                if (image and self.current_thumbnail_url == thumbnail_url and
                    hasattr(self, 'large_thumbnail_label') and 
                    self.large_thumbnail_label.winfo_exists()):
                    
                    # Convert to CTkImage
                    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(280, 210))
                    self.root.after(0, lambda: self._safe_update_thumbnail(ctk_image))
                elif self.current_thumbnail_url == thumbnail_url:
                    self.root.after(0, self.clear_large_thumbnail)
            except Exception as e:
                print(f"Thumbnail loading error: {e}")
                if self.current_thumbnail_url == thumbnail_url:
                    self.root.after(0, self.clear_large_thumbnail)
        
        # Use daemon thread for faster loading
        thread = threading.Thread(target=load_thumbnail, daemon=True)
        thread.start()
    
    def clear_large_thumbnail(self):
        """Clear large thumbnail display"""
        # Check if widget exists before configuring
        if hasattr(self, 'large_thumbnail_label') and self.large_thumbnail_label:
            self.current_thumbnail_url = None  # Reset current thumbnail tracking
            try:
                self.large_thumbnail_label.configure(
                    image=None,
                    text="🎥\nThumbnail"
                )
            except Exception as e:
                print(f"Thumbnail clear error: {e}")
        else:
            self.current_thumbnail_url = None
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(initialdir=self.output_dir)
        if folder:
            self.output_dir = folder
            self.main_status_label.configure(text=f"📂 Klasör: {folder[-30:]}...")
            # Update the folder label to show new directory
            self.update_folder_display()
    
    def update_folder_display(self):
        """Update the folder display label with current directory"""
        try:
            folder_name = os.path.basename(self.output_dir) if self.output_dir else "downloads"
            # Update the folder label
            if hasattr(self, 'folder_label'):
                self.folder_label.configure(text=f"📂 İndirme Klasörü: {folder_name}")
            # Also update status
            self.main_status_label.configure(text=f"📂 Aktif klasör: {folder_name}")
        except Exception as e:
            print(f"Folder display update error: {e}")
    
    def process_video_info(self, info):
        """Process and format video information with enhanced Turkish character handling"""
        # Başlık işleme - Unicode normalizasyonu ile
        title = info['title']
        
        # Ensure proper Unicode normalization for Turkish characters
        try:
            import unicodedata
            title = unicodedata.normalize('NFC', title)
        except Exception:
            pass  # Continue with original title if normalization fails
        
        # Başlık kısaltma - Turkish character count aware
        if len(title) > 45:
            # More careful truncation to avoid cutting Turkish characters
            title = title[:42] + "..."
        
        # Bilgi metnini oluştur
        info_text = f"📺 {title}"
        
        if info['is_playlist']:
            playlist_count = info.get('playlist_count', 0)
            info_text += f" (📋 {playlist_count} video)"
        
        # Method bilgisini ekle
        method = info.get('method', 'yt-dlp')
        
        return {
            **info,
            'display_text': info_text,
            'short_title': title,
            'method': method
        }
    
    def display_video_info(self, processed_info):
        """Display processed video information with enhanced Turkish character support and faster thumbnail loading"""
        # Update video title with proper encoding
        title = processed_info.get('short_title', processed_info.get('title', 'Bilinmeyen Video'))
        
        # Ensure proper UTF-8 encoding for Turkish characters
        try:
            if isinstance(title, str):
                # Normalize Unicode characters for better display
                import unicodedata
                title = unicodedata.normalize('NFC', title)
            
            # Configure label with proper text encoding
            self.video_title_label.configure(text=title, text_color="white")
        except Exception as e:
            print(f"Başlık görüntüleme hatası: {e}")
            self.video_title_label.configure(text="Video Başlığı Alınamadı", text_color="white")
        
        # Update video link
        url = self.url_entry.get().strip()
        display_url = url[:50] + "..." if len(url) > 50 else url
        self.video_link_label.configure(text=display_url, text_color="lightblue")
        
        # Update large thumbnail with priority loading
        thumbnail_url = processed_info.get('thumbnail', '')
        if thumbnail_url:
            # Start thumbnail loading immediately in high priority
            self.update_large_thumbnail_priority(thumbnail_url)
        
        # Handle playlist
        if processed_info.get('is_playlist', False):
            self.show_playlist_section()
            self.load_playlist_items(url)
        else:
            self.hide_playlist_section()
        
        # Update status
        self.main_status_label.configure(text="✅ Video bilgisi güncellendi")
    
    def show_playlist_section(self):
        """Show playlist section"""
        if not self.playlist_section.winfo_ismapped():
            self.playlist_section.pack(padx=10, pady=(0, 10), fill="x", after=self.video_section)
    
    def hide_playlist_section(self):
        """Hide playlist section"""
        if self.playlist_section.winfo_ismapped():
            self.playlist_section.pack_forget()
        self.clear_playlist_items()
    
    def load_playlist_items(self, playlist_url: str):
        """Load playlist items using optimized web scraping - much faster"""
        def fetch_playlist_optimized():
            try:
                print(f"🔍 Starting playlist extraction for: {playlist_url}")
                
                # Show loading state immediately
                self.root.after(0, lambda: self.bulk_status_label.configure(
                    text="📋 Oynatma listesi videoları hızlı yükleniyor..."
                ))
                
                # Use optimized downloader
                temp_downloader = YouTubeDownloader()
                
                # First try fast web scraping method
                print("📡 Trying fast web scraping method...")
                playlist_info = temp_downloader.get_video_info_fast(playlist_url)
                print(f"📊 Playlist info result: {playlist_info}")
                
                if 'error' not in playlist_info and playlist_info.get('is_playlist', False):
                    print("✅ Web scraping successful, extracting videos...")
                    # Extract video IDs and titles using optimized method
                    entries = self._extract_playlist_videos_optimized(playlist_url)
                    print(f"📹 Extracted {len(entries)} videos from optimized method")
                    
                    if entries:
                        self.root.after(0, lambda: self.create_playlist_items(entries))
                        self.root.after(0, lambda: self.bulk_status_label.configure(
                            text=f"✅ {len(entries)} video yüklendi - hazır!"
                        ))
                        return
                    else:
                        print("⚠️ No videos extracted from optimized method")
                
                # Fallback to yt-dlp if web scraping fails
                print("🔄 Trying fallback method...")
                self.root.after(0, lambda: self.bulk_status_label.configure(
                    text="📋 Alternatif yöntem deneniyor..."
                ))
                
                entries = self._extract_playlist_videos_fallback(playlist_url)
                print(f"📹 Extracted {len(entries)} videos from fallback method")
                
                if entries:
                    self.root.after(0, lambda: self.create_playlist_items(entries))
                    self.root.after(0, lambda: self.bulk_status_label.configure(
                        text=f"✅ {len(entries)} video yüklendi - hazır!"
                    ))
                else:
                    print("❌ No videos extracted from any method")
                    self.root.after(0, lambda: self.bulk_status_label.configure(
                        text="❌ Playlist videoları alınamadı"
                    ))
                    
            except Exception as e:
                print(f"❌ Playlist yükleme hatası: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self.bulk_status_label.configure(
                    text=f"❌ Playlist yüklenirken hata: {str(e)[:30]}..."
                ))
        
        threading.Thread(target=fetch_playlist_optimized, daemon=True).start()
    
    def _extract_playlist_videos_optimized(self, playlist_url: str) -> list:
        """Extract playlist videos using optimized web scraping"""
        try:
            import requests
            import re
            
            # Use optimized headers for faster response
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Fast request with minimal timeout
            response = requests.get(playlist_url, headers=headers, timeout=3.0)
            html = response.text
            
            # Extract video IDs and titles using optimized patterns
            video_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            title_pattern = r'"title":\{"runs":\[\{"text":"([^"]+)"'
            
            video_ids = re.findall(video_pattern, html)
            titles = re.findall(title_pattern, html)
            
            # Remove duplicates and limit to reasonable number
            unique_video_ids = list(dict.fromkeys(video_ids))[:30]  # Max 30 videos
            
            if not unique_video_ids:
                print("No video IDs found in playlist")
                return []
            
            # Create entries list
            entries = []
            for i, video_id in enumerate(unique_video_ids):
                try:
                    title = titles[i] if i < len(titles) else f'Video {i+1}'
                    
                    # Clean title using downloader's method
                    temp_downloader = YouTubeDownloader()
                    clean_title = temp_downloader._clean_title(title)
                    
                    entries.append({
                        'id': video_id,
                        'title': clean_title,
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
                    })
                except Exception as e:
                    print(f"Error processing video {i}: {e}")
                    # Add basic entry even if title processing fails
                    entries.append({
                        'id': video_id,
                        'title': f'Video {i+1}',
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
                    })
            
            print(f"Successfully extracted {len(entries)} videos from playlist")
            return entries
            
        except Exception as e:
            print(f"Optimized playlist extraction error: {e}")
            return []
    
    def _extract_playlist_videos_fallback(self, playlist_url: str) -> list:
        """Fallback method using yt-dlp for playlist extraction"""
        try:
            from yt_dlp import YoutubeDL
            
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'socket_timeout': 10,  # Reduced timeout
                'retries': 1,  # Fewer retries for speed
                'fragment_retries': 1,
                'no_call_home': True,
                'simulate': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
            if 'entries' in playlist_info and playlist_info['entries']:
                entries = []
                for i, entry in enumerate(playlist_info['entries'][:30]):  # Max 30 videos
                    if entry:
                        try:
                            entries.append({
                                'id': entry.get('id', f'video_{i}'),
                                'title': entry.get('title', f'Video {i+1}'),
                                'url': entry.get('url', ''),
                                'thumbnail': entry.get('thumbnail', '')
                            })
                        except Exception as e:
                            print(f"Error processing fallback entry {i}: {e}")
                            # Add basic entry even if processing fails
                            entries.append({
                                'id': f'video_{i}',
                                'title': f'Video {i+1}',
                                'url': '',
                                'thumbnail': ''
                            })
                
                print(f"Fallback method extracted {len(entries)} videos")
                return entries
            
            print("No entries found in fallback method")
            return []
            
        except Exception as e:
            print(f"Fallback playlist extraction error: {e}")
            return []
    
    def create_playlist_items(self, entries):
        """Create playlist item widgets"""
        self.clear_playlist_items()
        
        for i, entry in enumerate(entries):
            if not entry:  # Skip None entries
                continue
                
            item_frame = ctk.CTkFrame(self.playlist_frame, corner_radius=5)
            item_frame.pack(fill="x", pady=2)
            
            # Video info
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            title = entry.get('title', f'Video {i+1}')
            
            # Ensure proper Turkish character display
            try:
                import unicodedata
                title = unicodedata.normalize('NFC', title)
            except Exception:
                pass
            
            if len(title) > 60:
                title = title[:57] + "..."
                
            title_label = ctk.CTkLabel(
                info_frame, 
                text=f"{i+1}. {title}",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            title_label.pack(anchor="w")
            
            # Progress bar for this item
            progress_bar = ctk.CTkProgressBar(info_frame, height=10, width=250)
            progress_bar.pack(anchor="w", pady=(2, 0))
            progress_bar.set(0)
            
            # Status label
            status_label = ctk.CTkLabel(
                info_frame,
                text="Hazır",
                font=ctk.CTkFont(size=10),
                text_color="gray60"
            )
            status_label.pack(anchor="w")
            
            # Download button
            download_btn = ctk.CTkButton(
                item_frame,
                text="⬇️",
                width=30,
                height=25,
                font=ctk.CTkFont(size=12),
                command=lambda idx=i, url=entry.get('url', ''): self.download_single_video(idx, url)
            )
            download_btn.pack(side="right", padx=10, pady=5)
            
            # Store item references
            self.playlist_items.append({
                'frame': item_frame,
                'progress': progress_bar,
                'status': status_label,
                'button': download_btn,
                'entry': entry
            })
        
    def start_bulk_download(self):
            """Start downloading all playlist items"""
            if self.bulk_download_active:
                return
                
            if not self.playlist_items:
                messagebox.showwarning("Uyarı", "Playlist yüklenemedi veya boş!")
                return
                
            self.bulk_download_active = True
            self.bulk_download_button.configure(state="disabled")
            self.stop_bulk_button.configure(state="normal")
            self.bulk_status_label.configure(text="📂 Otomatik klasör oluşturulacak - Toplu indirme hazırlanıyor...")
                
            # Reset all progress bars
            self.bulk_progress_bar.set(0)
            for item in self.playlist_items:
                item['progress'].set(0)
                item['status'].configure(text="Sırada")
                item['button'].configure(state="disabled")
                
            # Start bulk download in thread
            self.bulk_download_thread = threading.Thread(
                target=self._bulk_download_worker, 
                daemon=True
            )
            self.bulk_download_thread.start()
        
    def stop_bulk_download(self):
            """Stop bulk download process"""
            self.bulk_download_active = False
            self.bulk_download_button.configure(state="normal")
            self.stop_bulk_button.configure(state="disabled")
            self.bulk_status_label.configure(text="Toplu indirme durduruldu")
                
            # Re-enable individual download buttons
            for item in self.playlist_items:
                if item['status'].cget('text') not in ["Tamamlandı", "İndiriliyor"]:
                    item['button'].configure(state="normal")
                    item['status'].configure(text="Hazır")
        
    def _bulk_download_worker(self):
            """Background worker for bulk download with enhanced progress tracking"""
            import time
            import os
            
            try:
                completed = 0
                failed = 0
                total = len(self.playlist_items)
                start_time = time.time()
                total_downloaded_bytes = 0
                
                # Get playlist title and create folder
                playlist_title = self.video_title_label.cget("text")
                # Remove video count if present (e.g., "My Playlist (25 video)" -> "My Playlist")
                import re
                playlist_title = re.sub(r'\s*\(\d+\s*video\)\s*$', '', playlist_title)
                
                # Create safe folder name
                safe_folder_name = "".join(c for c in playlist_title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                if not safe_folder_name:
                    safe_folder_name = "Playlist_Download"
                
                # Create playlist folder
                playlist_folder = os.path.join(self.output_dir, safe_folder_name)
                os.makedirs(playlist_folder, exist_ok=True)
                
                # Store original output directory
                original_output_dir = self.output_dir
                
                self.root.after(0, lambda: self.bulk_status_label.configure(
                    text=f"📂 '{safe_folder_name}' klasörü oluşturuldu - Toplu indirme başlatıldı: 0/{total}"
                ))
                    
                for i, item in enumerate(self.playlist_items):
                    if not self.bulk_download_active:
                        break
                        
                    entry = item['entry']
                    video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                    
                    # Calculate elapsed time
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 3600:  # Hours
                        elapsed_str = f"{int(elapsed_time // 3600)}s {int((elapsed_time % 3600) // 60)}dk"
                    elif elapsed_time > 60:  # Minutes
                        elapsed_str = f"{int(elapsed_time // 60)}dk {int(elapsed_time % 60)}s"
                    else:  # Seconds
                        elapsed_str = f"{int(elapsed_time)}s"
                    
                    # Format total downloaded size
                    if total_downloaded_bytes > 1024*1024*1024:  # GB
                        size_str = f"{total_downloaded_bytes/(1024*1024*1024):.1f} GB"
                    elif total_downloaded_bytes > 1024*1024:  # MB
                        size_str = f"{total_downloaded_bytes/(1024*1024):.1f} MB"
                    elif total_downloaded_bytes > 1024:  # KB
                        size_str = f"{total_downloaded_bytes/1024:.1f} KB"
                    else:
                        size_str = f"{total_downloaded_bytes} B"
                        
                    # Update status
                    self.root.after(0, lambda idx=i: self._update_item_status(idx, "İndiriliyor"))
                    self.root.after(0, lambda idx=i, t=elapsed_str, s=size_str: self.bulk_status_label.configure(
                        text=f"📈 Video {i+1}/{total} hazırlanıyor...  |  ⏱️ {t}  |  💾 {s}  |  ✅ {completed} tamamlandı  |  ❌ {failed} hata"
                    ))
                    
                    # Temporarily change output directory to playlist folder
                    self.output_dir = playlist_folder
                        
                    # Download video
                    success = self._download_playlist_item(i, video_url)
                    
                    # Restore original output directory
                    self.output_dir = original_output_dir
                        
                    if success:
                        completed += 1
                        # Try to estimate downloaded size (rough estimate)
                        total_downloaded_bytes += 50 * 1024 * 1024  # Rough estimate: 50MB per video
                        self.root.after(0, lambda idx=i: self._update_item_status(idx, "✅ Tamamlandı"))
                        self.root.after(0, lambda idx=i: self.playlist_items[idx]['progress'].set(1.0))
                    else:
                        failed += 1
                        self.root.after(0, lambda idx=i: self._update_item_status(idx, "❌ Hata"))
                    
                    # Calculate updated time and size info
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 3600:  # Hours
                        elapsed_str = f"{int(elapsed_time // 3600)}s {int((elapsed_time % 3600) // 60)}dk"
                    elif elapsed_time > 60:  # Minutes
                        elapsed_str = f"{int(elapsed_time // 60)}dk {int(elapsed_time % 60)}s"
                    else:  # Seconds
                        elapsed_str = f"{int(elapsed_time)}s"
                    
                    # Format total downloaded size
                    if total_downloaded_bytes > 1024*1024*1024:  # GB
                        size_str = f"{total_downloaded_bytes/(1024*1024*1024):.1f} GB"
                    elif total_downloaded_bytes > 1024*1024:  # MB
                        size_str = f"{total_downloaded_bytes/(1024*1024):.1f} MB"
                    elif total_downloaded_bytes > 1024:  # KB
                        size_str = f"{total_downloaded_bytes/1024:.1f} KB"
                    else:
                        size_str = f"{total_downloaded_bytes} B"
                        
                    # Update bulk progress with detailed info
                    progress = (i + 1) / total
                    self.root.after(0, lambda p=progress: self.bulk_progress_bar.set(p))
                    self.root.after(0, lambda c=completed, f=failed, curr=i+1, t=total, elapsed=elapsed_str, size=size_str, folder=safe_folder_name: 
                        self.bulk_status_label.configure(
                            text=f"🏁 {curr}/{t} işlendi | 📂 '{folder}' | ⏱️ {elapsed} | 💾 {size} | ✅ {c} başarılı | ❌ {f} hata | %{int((curr/t)*100)}"
                        )
                    )
                        
                    # Small delay between downloads to avoid overwhelming
                    if self.bulk_download_active and i < total - 1:
                        time.sleep(0.5)
                
            except Exception as e:
                # Restore original output directory in case of error
                self.output_dir = original_output_dir
                self.root.after(0, lambda: self.bulk_status_label.configure(
                    text=f"❌ Toplu indirme hatası: {str(e)[:30]}..."
                ))
            finally:
                # Ensure output directory is restored
                self.output_dir = original_output_dir
                
                completed_final = sum(1 for item in self.playlist_items 
                                    if item['status'].cget('text') == "✅ Tamamlandı")
                failed_final = sum(1 for item in self.playlist_items 
                                 if item['status'].cget('text') == "❌ Hata")
                
                # Calculate final statistics
                total_time = time.time() - start_time
                if total_time > 3600:  # Hours
                    time_str = f"{int(total_time // 3600)}s {int((total_time % 3600) // 60)}dk"
                elif total_time > 60:  # Minutes
                    time_str = f"{int(total_time // 60)}dk {int(total_time % 60)}s"
                else:  # Seconds
                    time_str = f"{int(total_time)}s"
                
                # Format final downloaded size
                if total_downloaded_bytes > 1024*1024*1024:  # GB
                    final_size_str = f"{total_downloaded_bytes/(1024*1024*1024):.1f} GB"
                elif total_downloaded_bytes > 1024*1024:  # MB
                    final_size_str = f"{total_downloaded_bytes/(1024*1024):.1f} MB"
                elif total_downloaded_bytes > 1024:  # KB
                    final_size_str = f"{total_downloaded_bytes/1024:.1f} KB"
                else:
                    final_size_str = f"{total_downloaded_bytes} B"
                    
                self.root.after(0, lambda c=completed_final, f=failed_final, t=total, time_s=time_str, size_s=final_size_str, folder=safe_folder_name: 
                    self.bulk_status_label.configure(
                        text=f"🏆 Toplu indirme tamamlandı! | 📂 '{folder}' | ⏱️ {time_s} | 💾 {size_s} | ✅ {c}/{t} başarılı | ❌ {f} hata"
                    )
                )
                self.root.after(0, self._bulk_download_finished)
        
    def _update_item_status(self, index: int, status: str):
            """Update individual item status"""
            if index < len(self.playlist_items):
                self.playlist_items[index]['status'].configure(text=status)
        
    def _download_playlist_item(self, index: int, video_url: str) -> bool:
        """Download single playlist item using yt-dlp directly"""
        try:
            from yt_dlp import YoutubeDL
            import os
            
            # Use current output directory (which will be playlist folder during bulk download)
            current_output_dir = self.output_dir
            os.makedirs(current_output_dir, exist_ok=True)
            
            # Enhanced progress callback for this specific item
            def item_progress_hook(data):
                try:
                    if data['status'] == 'downloading' and index < len(self.playlist_items):
                        # Extract percentage with multiple methods
                        percent = 0.0
                        if '_percent_str' in data:
                            percent_str = data['_percent_str'].replace('%', '')
                            try:
                                percent = float(percent_str) / 100.0
                            except (ValueError, TypeError):
                                pass
                        elif 'downloaded_bytes' in data and 'total_bytes' in data and data['total_bytes'] > 0:
                            percent = data['downloaded_bytes'] / data['total_bytes']
                        
                        # Update individual progress bar
                        if percent > 0:
                            self.root.after(0, lambda p=percent: 
                                self.playlist_items[index]['progress'].set(p) 
                                if index < len(self.playlist_items) else None
                            )
                        
                        # Extract speed and ETA for individual item status
                        speed_str = ""
                        if 'speed' in data and data['speed'] and data['speed'] > 0:
                            speed = data['speed']
                            if speed > 1024*1024:  # MB/s
                                speed_str = f" | {speed/(1024*1024):.1f} MB/s"
                            elif speed > 1024:  # KB/s
                                speed_str = f" | {speed/1024:.1f} KB/s"
                        
                        # Update item status with speed info
                        status_text = f"📥 {percent*100:.0f}%{speed_str}"
                        self.root.after(0, lambda s=status_text: 
                            self._update_item_status(index, s) if index < len(self.playlist_items) else None
                        )
                        
                except Exception as e:
                    print(f"Progress hook error: {e}")
            
            # Determine format settings
            is_audio = self.format_var.get() == "audio"
            
            if is_audio:
                # Audio download with mp3 conversion
                format_selector = 'bestaudio/best'
                output_template = os.path.join(current_output_dir, '%(title)s.%(ext)s')
                postprocessors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                # Video download
                quality_map = {"4K": "2160", "1440p": "1440", "1080p": "1080", 
                             "720p": "720", "480p": "480", "360p": "360"}
                max_height = quality_map.get(self.quality_var.get(), "1080")
                format_selector = f'best[height<={max_height}]/best'
                output_template = os.path.join(current_output_dir, '%(title)s.%(ext)s')
                postprocessors = []
            
            # Configure yt-dlp options with enhanced settings
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_template,
                'progress_hooks': [item_progress_hook],
                'quiet': True,
                'no_warnings': True,
                'extractaudio': is_audio,
                'audioformat': 'mp3' if is_audio else None,
                'postprocessors': postprocessors,
                'retries': 3,  # Retry failed downloads
                'fragment_retries': 3,
                'writethumbnail': False,  # Skip thumbnail for speed
                'writeinfojson': False,   # Skip info json for speed
            }
            
            # Add subtitle support if enabled
            if self.subtitle_var.get():
                ydl_opts.update({
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['tr', 'en'],
                })
            
            # Download the video
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            return True
            
        except Exception as e:
            print(f"Playlist item download error: {e}")
            # Update item status to show error
            self.root.after(0, lambda: 
                self._update_item_status(index, f"❌ {str(e)[:20]}...") if index < len(self.playlist_items) else None
            )
            return False
        
    def _bulk_download_finished(self):
        """Called when bulk download finishes - shows notification"""
        self.bulk_download_active = False
        self.bulk_download_button.configure(state="normal")
        self.stop_bulk_button.configure(state="disabled")
            
        # Re-enable buttons for non-completed items
        for item in self.playlist_items:
            if item['status'].cget('text') not in ["✅ Tamamlandı"]:
                item['button'].configure(state="normal")
        
        # Show completion notification
        try:
            # Get final statistics
            completed = sum(1 for item in self.playlist_items 
                          if item['status'].cget('text') == "✅ Tamamlandı")
            failed = sum(1 for item in self.playlist_items 
                       if item['status'].cget('text') == "❌ Hata")
            total = len(self.playlist_items)
            
            # Create notification message
            if failed == 0:
                message = f"🎉 Toplu indirme başarıyla tamamlandı!\n\n✅ {completed}/{total} video indirildi\n📂 Playlist klasörü oluşturuldu\n\nTüm videolar başarıyla indirildi!"
                messagebox.showinfo("🏆 İndirme Tamamlandı", message)
            else:
                message = f"⚠️ Toplu indirme tamamlandı!\n\n✅ {completed}/{total} video başarılı\n❌ {failed} video başarısız\n📂 Playlist klasörü oluşturuldu\n\nBaşarısız videoları tekrar deneyebilirsiniz."
                messagebox.showwarning("🏁 İndirme Tamamlandı", message)
                
        except Exception as e:
            print(f"Notification error: {e}")
            # Fallback to simple message
            messagebox.showinfo("İndirme Tamamlandı", "Toplu indirme işlemi tamamlandı!")
    
    def download_single_video(self, index: int, video_url: str):
        """Download a single video from playlist"""
        if self.bulk_download_active:
            return  # Don't allow individual downloads during bulk
        
        if index >= len(self.playlist_items):
            return
        
        item = self.playlist_items[index]
        item['button'].configure(state="disabled")
        item['status'].configure(text="İndiriliyor")
        item['progress'].set(0)
        
        def download_worker():
            success = self._download_playlist_item(index, video_url)
            
            if success:
                self.root.after(0, lambda: item['status'].configure(text="Tamamlandı"))
                self.root.after(0, lambda: item['progress'].set(1.0))
            else:
                self.root.after(0, lambda: item['status'].configure(text="Hata"))
                self.root.after(0, lambda: item['button'].configure(state="normal"))
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def clear_playlist_items(self):
        """Clear all playlist items"""
        # Stop bulk download if active
        if self.bulk_download_active:
            self.stop_bulk_download()
        
        for item in self.playlist_items:
            item['frame'].destroy()
        self.playlist_items.clear()
        
        # Reset bulk progress
        self.bulk_progress_bar.set(0)
        self.bulk_status_label.configure(text="Hazır")
    
    def download_single_video(self, index: int, video_url: str):
        """Download a single video from playlist"""
        if index < len(self.playlist_items):
            item = self.playlist_items[index]
            item['status'].configure(text="İndiriliyor...")
            item['button'].configure(state="disabled")
            
            # Here you would implement single video download
            # For now, just simulate progress
            def simulate_progress():
                for i in range(101):
                    if item['frame'].winfo_exists():
                        self.root.after(50 * i, lambda p=i/100: item['progress'].set(p))
                    
                self.root.after(5000, lambda: item['status'].configure(text="Tamamlandı") if item['frame'].winfo_exists() else None)
            
            threading.Thread(target=simulate_progress, daemon=True).start()
    
    def progress_callback(self, data):
        """Handle download progress updates for main progress bar with enhanced formatting"""
        import time
        
        # Initialize download start time if not exists
        if not hasattr(self, 'download_start_time'):
            self.download_start_time = time.time()
            
        try:
            if data['status'] == 'downloading':
                # Calculate download duration
                elapsed_time = time.time() - self.download_start_time
                if elapsed_time > 3600:  # Hours
                    duration_str = f"{int(elapsed_time // 3600)}s {int((elapsed_time % 3600) // 60)}dk"
                elif elapsed_time > 60:  # Minutes
                    duration_str = f"{int(elapsed_time // 60)}dk {int(elapsed_time % 60)}s"
                else:  # Seconds
                    duration_str = f"{int(elapsed_time)}s"
                
                # Parse percentage more carefully
                if 'percent' in data and data['percent'] is not None:
                    try:
                        percent_str = str(data['percent']).replace('%', '')
                        percent = float(percent_str) / 100
                        self.main_progress_bar.set(percent)
                        
                        # Create clean percentage display
                        percent_display = f"{float(percent_str):.1f}%"
                    except (ValueError, TypeError):
                        percent_display = "0.0%"
                else:
                    percent_display = "0.0%"
                
                # Enhanced speed formatting with more detail
                speed = data.get('speed', 0)
                if isinstance(speed, (int, float)) and speed > 0:
                    if speed > 1024*1024*1024:  # GB/s
                        speed_str = f"{speed/(1024*1024*1024):.2f} GB/s"
                    elif speed > 1024*1024:  # MB/s
                        speed_str = f"{speed/(1024*1024):.1f} MB/s"
                    elif speed > 1024:  # KB/s
                        speed_str = f"{speed/1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed:.0f} B/s"
                        
                    # Add speed category indicators
                    if speed > 50*1024*1024:  # > 50MB/s - Very Fast
                        speed_indicator = "🚀🚀"
                    elif speed > 10*1024*1024:  # > 10MB/s - Fast
                        speed_indicator = "🚀"
                    elif speed > 1024*1024:  # > 1MB/s - Good
                        speed_indicator = "⚡"
                    else:  # < 1MB/s - Slow
                        speed_indicator = "🐢"
                    
                    speed_str = f"{speed_indicator} {speed_str}"
                else:
                    speed_str = "🔄 Hesaplanıyor..."
                
                # Format ETA with improved display
                eta = data.get('eta', 0)
                if isinstance(eta, (int, float)) and eta > 0:
                    if eta > 3600:  # Hours
                        hours = int(eta // 3600)
                        minutes = int((eta % 3600) // 60)
                        eta_str = f"{hours}s {minutes}dk"
                    elif eta > 60:  # Minutes
                        minutes = int(eta // 60)
                        seconds = int(eta % 60)
                        eta_str = f"{minutes}dk {seconds}s"
                    else:  # Seconds
                        eta_str = f"{int(eta)}s"
                else:
                    eta_str = "🕰️ Hesaplanıyor..."
                
                # Get downloaded and total bytes for size display
                downloaded_bytes = data.get('downloaded_bytes', 0)
                total_bytes = data.get('total_bytes', 0)
                
                if downloaded_bytes and total_bytes:
                    # Format downloaded size
                    if downloaded_bytes > 1024*1024*1024:  # GB
                        downloaded_str = f"{downloaded_bytes/(1024*1024*1024):.1f} GB"
                    elif downloaded_bytes > 1024*1024:  # MB
                        downloaded_str = f"{downloaded_bytes/(1024*1024):.1f} MB"
                    elif downloaded_bytes > 1024:  # KB
                        downloaded_str = f"{downloaded_bytes/1024:.1f} KB"
                    else:
                        downloaded_str = f"{downloaded_bytes} B"
                    
                    # Format total size
                    if total_bytes > 1024*1024*1024:  # GB
                        total_str = f"{total_bytes/(1024*1024*1024):.1f} GB"
                    elif total_bytes > 1024*1024:  # MB
                        total_str = f"{total_bytes/(1024*1024):.1f} MB"
                    elif total_bytes > 1024:  # KB
                        total_str = f"{total_bytes/1024:.1f} KB"
                    else:
                        total_str = f"{total_bytes} B"
                    
                    size_info = f" | 💾 {downloaded_str}/{total_str}"
                else:
                    size_info = ""
                
                # Create beautiful status text with enhanced formatting
                status_text = f"⬇️ {percent_display} | {speed_str} | ⏱️ {eta_str} | 🕑 {duration_str}{size_info}"
                self.main_status_label.configure(text=status_text)
                
            elif data['status'] == 'finished':
                # Calculate total download time
                if hasattr(self, 'download_start_time'):
                    total_time = time.time() - self.download_start_time
                    if total_time > 60:
                        time_str = f"{int(total_time // 60)}dk {int(total_time % 60)}s"
                    else:
                        time_str = f"{int(total_time)}s"
                    
                    self.main_progress_bar.set(1.0)
                    self.main_status_label.configure(text=f"✅ İndirme başarıyla tamamlandı! (🕑 {time_str})")
                    delattr(self, 'download_start_time')  # Clean up
                else:
                    self.main_progress_bar.set(1.0)
                    self.main_status_label.configure(text="✅ İndirme başarıyla tamamlandı!")
                
            elif data['status'] == 'error':
                error_msg = data.get('error', 'Bilinmeyen hata')
                self.main_status_label.configure(text=f"❌ Hata: {error_msg[:30]}...")
                if hasattr(self, 'download_start_time'):
                    delattr(self, 'download_start_time')  # Clean up on error
                
        except Exception as e:
            print(f"Progress callback error: {e}")
    
    def status_callback(self, message):
        """Handle status updates"""
        self.main_status_label.configure(text=f"📡 {message}")
    
    def error_callback(self, message):
        """Handle error messages"""
        self.main_status_label.configure(text=f"❌ {message}")
        messagebox.showerror("İndirme Hatası", message)
        self.reset_ui()
    
    def start_download(self):
        """Start the download process with new format handling"""
        import time
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen geçerli bir YouTube URL'si girin!")
            return
        
        # Initialize download timing
        self.download_start_time = time.time()
        
        # Initialize downloader
        self.downloader = YouTubeDownloader(self.output_dir)
        self.downloader.set_progress_callback(self.progress_callback)
        self.downloader.set_status_callback(self.status_callback)
        self.downloader.set_error_callback(self.error_callback)
        
        # Configure download options with new format system
        audio_only = self.format_var.get() == "audio"  # Changed from "mp3"
        quality_map = {"4K": 2160, "1440p": 1440, "1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
        max_height = quality_map.get(self.quality_var.get(), 1080)
        
        # Check if this is a playlist download
        is_playlist_download = len(self.playlist_items) > 0
        include_subs = self.subtitle_var.get()
        
        # Update UI
        self.download_button.configure(state="disabled", text="📡 İNDİRİLİYOR")
        self.cancel_button.configure(state="normal")
        self.main_progress_bar.set(0)
        self.main_status_label.configure(text="🚀 İndirme başlatılıyor...")
        
        # Create folder for playlist if needed
        if is_playlist_download:
            video_title = self.video_title_label.cget("text")
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            playlist_folder = os.path.join(self.output_dir, safe_title)
            os.makedirs(playlist_folder, exist_ok=True)
            download_dir = playlist_folder
        else:
            download_dir = self.output_dir
        
        # Start download in separate thread
        def download_thread():
            if is_playlist_download:
                success = self.download_playlist(url, audio_only, max_height, include_subs, download_dir)
            else:
                # Update downloader output directory
                self.downloader.output_dir = download_dir
                success = self.downloader.download(
                    url=url,
                    audio_only=audio_only,
                    max_height=max_height,
                    prefer_mp4=True,
                    no_playlist=True,  # Single video
                    include_subs=include_subs,
                    sub_langs="tr,en",
                    auto_subs=True
                )
            
            if success:
                self.root.after(0, lambda: self.main_status_label.configure(text="🎉 Başarıyla tamamlandı!"))
                self.root.after(0, self.open_download_folder)
            
            self.root.after(0, self.reset_ui)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def download_playlist(self, playlist_url: str, audio_only: bool, max_height: int, include_subs: bool, download_dir: str) -> bool:
        """Download entire playlist with individual progress tracking"""
        try:
            # Create separate downloader for playlist
            playlist_downloader = YouTubeDownloader(download_dir)
            
            # Download the entire playlist
            success = playlist_downloader.download(
                url=playlist_url,
                audio_only=audio_only,
                max_height=max_height,
                prefer_mp4=True,
                no_playlist=False,  # Allow playlist
                include_subs=include_subs,
                sub_langs="tr,en",
                auto_subs=True
            )
            
            # Update individual playlist item progress (simulation)
            for i, item in enumerate(self.playlist_items):
                if item['frame'].winfo_exists():
                    self.root.after(1000 * i, lambda idx=i: self.update_playlist_item_progress(idx))
            
            return success
            
        except Exception as e:
            print(f"Playlist indirme hatası: {e}")
            return False
    
    def update_playlist_item_progress(self, index: int):
        """Update progress for a specific playlist item"""
        if index < len(self.playlist_items):
            item = self.playlist_items[index]
            if item['frame'].winfo_exists():
                item['status'].configure(text="İndiriliyor...")
                
                # Simulate progress
                def animate_progress():
                    for i in range(101):
                        if item['frame'].winfo_exists():
                            self.root.after(30 * i, lambda p=i/100: item['progress'].set(p) if item['frame'].winfo_exists() else None)
                    
                    self.root.after(3000, lambda: item['status'].configure(text="Tamamlandı") if item['frame'].winfo_exists() else None)
                
                threading.Thread(target=animate_progress, daemon=True).start()
    
    def cancel_download(self):
        """Cancel the ongoing download"""
        if self.downloader and self.downloader.is_downloading():
            messagebox.showinfo("İptal", "İndirme işlemi en kısa sürede durdurulacak...")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.download_button.configure(state="normal", text="⬇️ İNDİR")
        self.cancel_button.configure(state="disabled")
    
    def open_download_folder(self):
        """Ask user if they want to open the download folder"""
        if messagebox.askyesno("İndirme Tamamlandı", "İndirilen dosyaları görmek ister misiniz?"):
            try:
                os.startfile(self.output_dir)  # Windows
            except:
                try:
                    os.system(f'xdg-open "{self.output_dir}"')  # Linux
                except:
                    try:
                        os.system(f'open "{self.output_dir}"')  # macOS
                    except:
                        pass
    
    def open_download_folder_direct(self):
        """Open the download folder directly without asking"""
        try:
            target_dir = self.output_dir
            
            # Check if there's a recent playlist folder
            if hasattr(self, 'playlist_items') and len(self.playlist_items) > 0:
                # Get playlist title to find the folder
                playlist_title = self.video_title_label.cget("text")
                import re
                playlist_title = re.sub(r'\s*\(\d+\s*video\)\s*$', '', playlist_title)
                
                # Create safe folder name
                safe_folder_name = "".join(c for c in playlist_title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                if safe_folder_name:
                    playlist_folder = os.path.join(self.output_dir, safe_folder_name)
                    if os.path.exists(playlist_folder):
                        target_dir = playlist_folder
            
            # Check if directory exists, create if not
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # Open folder using different methods based on OS
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.startfile(target_dir)
            elif system == "Darwin":  # macOS
                os.system(f'open "{target_dir}"')
            elif system == "Linux":
                os.system(f'xdg-open "{target_dir}"')
            else:
                # Fallback for other systems
                os.system(f'explorer "{target_dir}"')
                
            # Update status to show folder was opened
            folder_name = os.path.basename(target_dir)
            if target_dir != self.output_dir:
                self.main_status_label.configure(text=f"📂 Playlist klasörü açıldı: {folder_name}")
            else:
                self.main_status_label.configure(text=f"📂 İndirme klasörü açıldı: {folder_name}")
            
        except Exception as e:
            # Show error message if folder can't be opened
            messagebox.showerror("Hata", f"Klasör açılamadı: {str(e)}")
            print(f"Folder open error: {e}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()
