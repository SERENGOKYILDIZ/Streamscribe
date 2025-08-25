#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe - YouTube Video İndirici ve Altyazı Çeviricisi

Bu uygulama şunları yapabilir:
- YouTube videolarını MP4/MP3 formatında indir
- Tek video veya oynatma listesi indir
- Modern GUI arayüzü ile kolay kullanım
- Otomatik Türkçe altyazı oluşturma (Whisper ile)
- Altyazıları videoya gömme

Kullanım:
    python main.py              # GUI arayüzünü başlat
    python main.py --gui         # GUI arayüzünü başlat
    python main.py --subtitle <video_file>  # Video için Türkçe altyazı oluştur
    python main.py --help        # Yardım göster
"""

import sys
import os
import argparse
from pathlib import Path


def create_subtitle(video_path: str) -> bool:
    """
    Video dosyası için Türkçe altyazı oluştur
    
    Args:
        video_path (str): Video dosyasının yolu
        
    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        import moviepy.editor as mp
        import whisper
        
        if not os.path.exists(video_path):
            print(f"❌ Hata: Video dosyası bulunamadı: {video_path}")
            return False
        
        # Get FFmpeg path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(script_dir, "ffmpeg", "bin", "ffmpeg.exe")
        
        # Set FFmpeg path for moviepy if local version exists
        if os.path.exists(ffmpeg_path):
            mp.config.FFMPEG_BINARY = ffmpeg_path
            print(f"🔧 Yerel FFmpeg kullanılıyor: {ffmpeg_path}")
        
        print(f"🎬 Video işleniyor: {video_path}")
        
        # Video dosyasından ses çıkar
        video_name = Path(video_path).stem
        audio_path = f"{video_name}_temp_audio.wav"
        
        print("🔊 Ses dosyası çıkarılıyor...")
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        
        # Whisper modelini yükle
        print("🤖 Whisper modeli yükleniyor...")
        model = whisper.load_model("small")  # tiny, base, small, medium, large
        
        # Türkçe altyazı için çeviri yap
        print("🔤 Altyazı oluşturuluyor ve Türkçeye çevriliyor...")
        result = model.transcribe(audio_path, task="translate")
        
        # SRT dosyası oluştur
        subtitle_path = f"{video_name}_tr.srt"
        
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        with open(subtitle_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()
                
                f.write(f"{i}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
        
        # Geçici ses dosyasını sil
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        print(f"✅ Türkçe altyazı dosyası oluşturuldu: {subtitle_path}")
        print(f"💡 Altyazıyı videoya gömmek için:")
        if os.path.exists(ffmpeg_path):
            print(f"   \"{ffmpeg_path}\" -i \"{video_path}\" -vf subtitles=\"{subtitle_path}\" \"{video_name}_tr.mp4\"")
        else:
            print(f"   ffmpeg -i \"{video_path}\" -vf subtitles=\"{subtitle_path}\" \"{video_name}_tr.mp4\"")
        
        return True
        
    except ImportError as e:
        print(f"❌ Hata: Gerekli kütüphaneler eksik. requirements.txt dosyasını kontrol edin.")
        print(f"   Eksik: {e}")
        return False
    except Exception as e:
        print(f"❌ Altyazı oluşturma hatası: {str(e)}")
        return False
    finally:
        # Geçici dosyaları temizle
        if 'audio_path' in locals() and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass


def launch_gui():
    """
    GUI arayüzünü başlat
    """
    try:
        from gui import YouTubeDownloaderGUI
        
        print("🚀 StreamScribe GUI başlatılıyor...")
        app = YouTubeDownloaderGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Hata: GUI kütüphaneleri eksik. requirements.txt dosyasını kontrol edin.")
        print(f"   Eksik: {e}")
        print("\n💡 Yükleme için: pip install -r requirements.txt")
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ GUI başlatma hatası: {str(e)}")
        print(f"Hata detayı: {type(e).__name__}")
        import traceback
        print("\nTam hata detayı:")
        traceback.print_exc()
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)


def check_dependencies():
    """
    Gerekli bağımlılıkları kontrol et
    """
    missing_deps = []
    
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    if missing_deps:
        print("❌ Eksik bağımlılıklar tespit edildi:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Yükleme için: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """
    Ana uygulama giriş noktası
    """
    parser = argparse.ArgumentParser(
        description="StreamScribe - YouTube Video İndirici ve Altyazı Çeviricisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
    python main.py                          # GUI arayüzünü başlat
    python main.py --gui                    # GUI arayüzünü başlat
    python main.py --subtitle video.mp4    # Video için Türkçe altyazı oluştur
    python main.py --check-deps             # Bağımlılıkları kontrol et

GUI Özellikleri:
    • Modern ve kullanıcı dostu arayüz
    • MP4/MP3 format seçimi
    • Tek video veya playlist indirme
    • Kalite seçimi (360p - 4K)
    • Altyazı indirme ve gömme
    • İndirme ilerlemesi takibi
    • Hata yönetimi ve bildirimler

Altyazı Özellikleri:
    • OpenAI Whisper ile otomatik transkripsiyon
    • İngilizce'den Türkçe'ye çeviri
    • SRT format altyazı dosyası
    • FFmpeg ile video gömme desteği
        """
    )
    
    parser.add_argument(
        "--gui", 
        action="store_true", 
        help="GUI arayüzünü başlat (varsayılan)"
    )
    
    parser.add_argument(
        "--subtitle", 
        metavar="VIDEO_FILE",
        help="Belirtilen video dosyası için Türkçe altyazı oluştur"
    )
    
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="Gerekli bağımlılıkları kontrol et"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="StreamScribe v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Başlık göster
    print("="*60)
    print("🎬 StreamScribe - YouTube Video İndirici v1.0.0")
    print("📺 YouTube videolarını MP4/MP3 olarak indir")
    print("🔤 Otomatik Türkçe altyazı oluştur")
    print("="*60)
    
    # Bağımlılık kontrolü
    if args.check_deps:
        print("🔍 Bağımlılıklar kontrol ediliyor...")
        if check_dependencies():
            print("✅ Tüm bağımlılıklar mevcut!")
        return
    
    # Altyazı oluşturma
    if args.subtitle:
        if not check_dependencies():
            sys.exit(1)
        
        success = create_subtitle(args.subtitle)
        sys.exit(0 if success else 1)
    
    # GUI başlatma (varsayılan)
    if not check_dependencies():
        sys.exit(1)
    
    launch_gui()


if __name__ == "__main__":
    main()
