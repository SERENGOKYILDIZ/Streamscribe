# Streamscribe: Video Downloader & Auto Subtitle Translator

Streamscribe allows you to:
- Download videos (or audio) from YouTube and other platforms.
- Automatically generate **Turkish subtitles** from English audio using [OpenAI Whisper](https://github.com/openai/whisper).
- Embed the subtitles into the video using FFmpeg.
- Expandable for more video/audio processing features in the future.

---

## Requirements

### 1. Python packages
Install the dependencies:
```bash
pip install yt-dlp moviepy openai-whisper torch
```

⚠️ Note: Whisper requires **PyTorch**. Make sure you have a compatible version installed for your system and GPU/CPU.

### 2. FFmpeg
FFmpeg is required for merging video/audio and embedding subtitles.

- **Windows:**  
  1. Go to the official FFmpeg download page: [ffmpeg.org/download.html](https://ffmpeg.org/download.html).  
  2. Easier method: download from [gyan.dev ffmpeg builds](https://www.gyan.dev/ffmpeg/builds/).  
  3. Download the file **`ffmpeg-git-full.7z`**.  
  4. Extract it and add the `bin/` folder (where `ffmpeg.exe` is located) to your PATH.

- **Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install ffmpeg
```

- **macOS (Homebrew):**
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

---

## Usage

### 1. Download a YouTube video
Run the downloader script:
```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --mp4
```

Options:
- `--audio-only` → Download as MP3.
- `--subs --auto-subs` → Download available/auto-generated subtitles and embed them.
- `--max-height 1080` → Limit resolution.

### 2. Generate Turkish subtitles
Use the subtitle script:
```bash
python auto_subtitles.py video.mp4
```

This will:
- Extract audio from the video.
- Use Whisper to transcribe and translate English → Turkish.
- Save subtitles as `subtitle_tr.srt`.

### 3. Embed subtitles into the video
```bash
ffmpeg -i video.mp4 -vf subtitles=subtitle_tr.srt output_tr.mp4
```

---

## File Structure
```
Streamscribe/
│── youtube_downloader.py   # Downloads video/audio from YouTube or other platforms
│── auto_subtitles.py       # Creates Turkish subtitles using Whisper
│── requirements.txt        # Dependencies list
│── README.md               # Project documentation
```

---

## Example Workflow
```bash
# Step 1: Download the video
python youtube_downloader.py "https://www.youtube.com/watch?v=abcd1234" --mp4

# Step 2: Generate Turkish subtitles
python auto_subtitles.py "video.mp4"

# Step 3: Embed the subtitles into the video
ffmpeg -i video.mp4 -vf subtitles=subtitle_tr.srt video_tr.mp4
```

---

## Notes
- Ensure you have a good microphone/audio quality for best transcription.
- Whisper `small` model is default, you can switch to `medium` or `large` for higher accuracy:
  ```python
  model = whisper.load_model("large")
  ```
- Use only for videos you have the rights to download and process.
- Streamscribe is expandable: you can add more video/audio processing features in the future.
