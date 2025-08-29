#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Optimized Main Module
Enhanced main entry point with improved error handling and performance
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from logger import setup_logging, get_logger, log_error
from error_handler import ErrorHandler, handle_error
from utils import cleanup_resources


def check_dependencies() -> bool:
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    # Check FFmpeg availability
    try:
        from config import config
        ffmpeg_path = config.get_ffmpeg_path()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            pass
        else:
            missing_deps.append("FFmpeg")
            log_error("FFmpeg not found or not accessible")
    except Exception as e:
        missing_deps.append("FFmpeg")
        log_error(f"FFmpeg check error: {e}")
    
    if missing_deps:
        log_error(f"Missing dependencies: {', '.join(missing_deps)}")
        print("❌ Eksik bağımlılıklar tespit edildi:")
        for dep in missing_deps:
            print(f"   - {dep}")
        
        if "FFmpeg" in missing_deps:
            print("\n⚠️ FFmpeg bulunamadı!")
            print("   FFmpeg olmadan video işleme yapılamaz.")
            print("   Lütfen ffmpeg/ klasörünün mevcut olduğundan emin olun.")
        
        print("\n💡 Yükleme için: pip install -r requirements.txt")
        return False
    return True


def launch_gui():
    """Launch the optimized GUI interface"""
    try:
        # Import GUI after dependency check
        from gui import StreamScribeOptimizedGUI
        
        print("🚀 StreamScribe GUI başlatılıyor...")
        app = StreamScribeOptimizedGUI()
        app.run()
        
    except ImportError as e:
        error_msg = f"GUI kütüphaneleri eksik: {e}"
        log_error(error_msg)
        print(f"❌ Hata: {error_msg}")
        print("💡 Yükleme için: pip install -r requirements.txt")
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)
    except Exception as e:
        error_msg = f"GUI başlatma hatası: {str(e)}"
        log_error(error_msg)
        print(f"❌ {error_msg}")
        print(f"Hata detayı: {type(e).__name__}")
        import traceback
        print("\nTam hata detayı:")
        traceback.print_exc()
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)


def launch_legacy_gui():
    """Launch the legacy GUI interface"""
    try:
        from gui import YouTubeDownloaderGUI
        
        print("🚀 StreamScribe Legacy GUI başlatılıyor...")
        app = YouTubeDownloaderGUI()
        app.run()
        
    except ImportError as e:
        error_msg = f"Legacy GUI kütüphaneleri eksik: {e}"
        log_error(error_msg)
        print(f"❌ Hata: {error_msg}")
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Legacy GUI başlatma hatası: {str(e)}"
        log_error(error_msg)
        print(f"❌ {error_msg}")
        print(f"Hata detayı: {type(e).__name__}")
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)


def test_downloader():
    """Test the downloader functionality"""
    try:
        from downloader import OptimizedYouTubeDownloader
        
        # Test with a simple YouTube URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
        
        downloader = OptimizedYouTubeDownloader()
        
        print("🔍 Test video bilgisi alınıyor...")
        info = downloader.get_video_info_fast(test_url)
        
        if 'error' in info:
            print(f"❌ Test başarısız: {info['error']}")
            return False
        else:
            print(f"✅ Test başarılı: {info.get('title', 'Bilinmeyen')}")
            return True
            
    except Exception as e:
        error_msg = f"Downloader test hatası: {str(e)}"
        log_error(error_msg)
        print(f"❌ {error_msg}")
        return False


def show_system_info():
    """Show system information"""
    import platform
    import sys
    
    print("\n📊 Sistem Bilgileri:")
    print(f"   Python: {sys.version}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print(f"   Processor: {platform.processor()}")
    print(f"   StreamScribe: v{config.APP_VERSION}")
    print(f"   Author: {config.APP_AUTHOR}")


def main():
    """Main application entry point"""
    # Setup logging first
    setup_logging(config.LOG_LEVEL)
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description=f"{config.APP_NAME} - YouTube Video İndirici",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
    python main_optimized.py                    # Optimized GUI başlat
    python main_optimized.py --legacy           # Legacy GUI başlat
    python main_optimized.py --check-deps       # Bağımlılıkları kontrol et
    python main_optimized.py --test             # Downloader test et
    python main_optimized.py --info             # Sistem bilgilerini göster

GUI Özellikleri:
    • Modern ve optimize edilmiş arayüz
    • MP4/MP3 format seçimi
    • Tek video veya playlist indirme
    • Kalite seçimi (360p - 4K)
    • Detaylı indirme ilerlemesi takibi
    • Hata yönetimi ve bildirimler
    • Performans optimizasyonları
        """
    )
    
    parser.add_argument(
        "--legacy", 
        action="store_true", 
        help="Legacy GUI arayüzünü başlat"
    )
    
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="Gerekli bağımlılıkları kontrol et"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Downloader fonksiyonalitesini test et"
    )
    
    parser.add_argument(
        "--info", 
        action="store_true",
        help="Sistem bilgilerini göster"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"{config.APP_NAME} v{config.APP_VERSION}"
    )
    
    args = parser.parse_args()
    
    # Show header
    print("="*60)
    print(f"🎬 {config.APP_NAME} - YouTube Video İndirici v{config.APP_VERSION}")
    print("📺 YouTube videolarını MP4/MP3 olarak indir")
    print("🚀 Optimize edilmiş performans ve modern arayüz")
    print("="*60)
    
    try:
        # Handle different commands
        if args.check_deps:
            print("🔍 Bağımlılıklar kontrol ediliyor...")
            if check_dependencies():
                print("✅ Tüm bağımlılıklar mevcut!")
                return 0
            else:
                return 1
        
        if args.test:
            print("🧪 Downloader test ediliyor...")
            if test_downloader():
                print("✅ Test başarılı!")
                return 0
            else:
                return 1
        
        if args.info:
            show_system_info()
            return 0
        
        # Check dependencies before launching GUI
        if not check_dependencies():
            return 1
        
        # Launch appropriate GUI
        if args.legacy:
            launch_legacy_gui()
        else:
            launch_gui()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Kullanıcı tarafından iptal edildi")
        return 0
    except Exception as e:
        error_msg = f"Uygulama hatası: {str(e)}"
        log_error(error_msg)
        print(f"\n❌ {error_msg}")
        print("Lütfen log dosyasını kontrol edin veya uygulamayı yeniden başlatın.")
        return 1
    finally:
        # Cleanup resources
        cleanup_resources()


if __name__ == "__main__":
    sys.exit(main())
