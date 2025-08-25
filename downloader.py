import argparse
import os
from yt_dlp import YoutubeDL

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '').strip()
        s = d.get('_speed_str', '').strip()
        eta = d.get('eta')
        print(f"\rİndiriliyor: {p} | Hız: {s} | ETA: {eta}s", end="", flush=True)
    elif d['status'] == 'finished':
        print("\nBirleştirme/işleme yapılıyor...")

def build_format(max_height: int, prefer_mp4: bool):
    # Örn: 1080p sınır, mp4 tercih
    v = f"bestvideo[height<={max_height}]"
    if prefer_mp4:
        v += "[ext=mp4]"
        a = "bestaudio[ext=m4a]/bestaudio"
        combo = f"{v}+{a}/best[ext=mp4]/best"
    else:
        a = "bestaudio"
        combo = f"{v}+{a}/best"
    return combo

def main():
    ap = argparse.ArgumentParser(description="YouTube video/playlist indirici")
    ap.add_argument("url", help="Video veya playlist URL’si")
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

    os.makedirs(args.output, exist_ok=True)

    ydl_opts = {
        "outtmpl": os.path.join(args.output, "%(title).200s [%(id)s].%(ext)s"),
        "merge_output_format": "mp4" if args.mp4 else None,
        "progress_hooks": [progress_hook],
        "noplaylist": args.no_playlist,
        "quiet": False,
        "concurrent_fragment_downloads": 4,
        "retries": 10,
    }

    if args.audio_only:
        # En iyi sesi indir, MP3'e dönüştür
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
                {"key": "FFmpegMetadata"},
            ],
        })
    else:
        ydl_opts["format"] = build_format(args.max_height, args.mp4)
        # Video indirme sonrası birleştirme ve metadata
        ydl_opts.setdefault("postprocessors", [])
        ydl_opts["postprocessors"].append({"key": "FFmpegVideoRemuxer", "preferedformat": "mp4" if args.mp4 else "mkv"})
        ydl_opts["postprocessors"].append({"key": "FFmpegMetadata"})

    if args.subs:
        # Altyazı indirme ve gömme (FFmpeg gerekir)
        langs = [s.strip() for s in args.sub_langs.split(",") if s.strip()]
        ydl_opts.update({
            "writesubtitles": True,
            "writeautomaticsub": args.auto_subs,
            "subtitleslangs": langs,
            "subtitlesformat": "srt",
            "embedsubtitles": True,
        })

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([args.url])

if __name__ == "__main__":
    main()
