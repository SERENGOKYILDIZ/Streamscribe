import moviepy.editor as mp
import whisper

# 1. Videodan ses çıkar
video_path = "video.mp4"
audio_path = "audio.wav"

video = mp.VideoFileClip(video_path)
video.audio.write_audiofile(audio_path)

# 2. Whisper modelini yükle
model = whisper.load_model("small")  # tiny, base, small, medium, large
# not: "large" daha doğru çevirir ama daha yavaştır

# 3. Türkçe altyazı için çeviri yap
result = model.transcribe(audio_path, task="translate")  # İngilizceyi Türkçeye çevirir

# 4. SRT dosyası yaz
def write_srt(transcription, filename="subtitle_tr.srt"):
    with open(filename, "w", encoding="utf-8") as f:
        for i, segment in enumerate(transcription["segments"], start=1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            f.write(f"{i}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

write_srt(result, "subtitle_tr.srt")
print("Türkçe altyazı dosyası oluşturuldu: subtitle_tr.srt")
