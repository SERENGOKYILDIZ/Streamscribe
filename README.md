# StreamScribe: Modern YouTube Video Downloader & Subtitle Generator

**StreamScribe** is a powerful Python application that downloads YouTube videos with a modern GUI interface and automatically generates Turkish subtitles using AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 👨‍💻 Author

**Author:** Semi Eren Gökyıldız
- **Email:** [gokyildizsemieren@gmail.com](mailto:gokyildizsemieren@gmail.com)
- **GitHub:** [SERENGOKYILDIZ](https://github.com/SERENGOKYILDIZ)
- **LinkedIn:** [Semi Eren Gökyıldız](https://www.linkedin.com/in/semi-eren-gokyildiz/)

---

## 🚀 Features

### 📱 Modern GUI Interface
- **CustomTkinter** designed modern and user-friendly interface
- Dark/light theme support
- Real-time download progress tracking
- Drag-and-drop URL support
- **Full-screen mode** with horizontal layout
- **Smart notification system** for bulk downloads

### 📺 Video Downloading
- **Download YouTube videos in MP4/MP3 format**
- **Single video or complete playlist** downloading
- **Quality selection up to 4K** (360p - 2160p)
- **Fast downloading** - Multi-threaded support
- **Automatic format optimization**
- **Local FFmpeg usage** - No installation required on other computers
- **Bulk download notifications** - Get notified when all videos complete

### 🎵 Audio Downloading
- **High-quality MP3** output (192 kbps)
- **Automatic metadata** addition
- **Fast audio conversion**

### 📝 Subtitle Processing
- **OpenAI Whisper** for automatic transcription
- **Automatic translation from English to Turkish**
- **SRT format** subtitle files
- **Embed subtitles in video** (using FFmpeg)
- **Multi-language support**

### ⚡ Advanced Features
- **Error tolerance** - Automatic retry on connection issues
- **Smart file naming** - Safe character conversion
- **Folder selection** - Download to your preferred location
- **Ultra-fast video info** - Web scraping + yt-dlp fallback
- **Thumbnail preview** - Visual information with video image
- **Download history** - Track recently downloaded files
- **Local FFmpeg** - No system installation required
- **Automatic URL recognition** - Get info automatically when pasting URL
- **Optimized playlist extraction** - Fast playlist information loading
- **Horizontal UI layout** - Better element distribution

---

## 🛠️ Installation

### 1. Python Requirements
Python 3.8 or newer is required.

**Check Python version:**
```bash
python --version
# or
python3 --version
```

**If Python is not installed:**
- **Windows:** Download from [python.org](https://www.python.org/downloads/) and check "Add to PATH"
- **Linux:** `sudo apt install python3 python3-pip` (Ubuntu/Debian) or `sudo dnf install python3 python3-pip` (Fedora)
- **macOS:** `brew install python3` or download from [python.org](https://www.python.org/downloads/)

### 2. Clone or Download Project

**Option A: Clone with Git (Recommended)**
```bash
git clone https://github.com/SERENGOKYILDIZ/Streamscribe.git
cd Streamscribe
```

**Option B: Download ZIP**
1. Click "Code" → "Download ZIP" on GitHub
2. Extract the ZIP file
3. Open terminal/command prompt in the extracted folder

### 3. Create Virtual Environment (Recommended)

**Windows:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify activation (you should see (.venv) in prompt)
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in prompt)
```

### 4. Install Dependencies

**With activated virtual environment:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**If you encounter permission errors:**
```bash
# Windows (run as Administrator)
pip install -r requirements.txt

# Linux/macOS
pip install --user -r requirements.txt
```

**Required packages:**
- `yt-dlp` - YouTube video downloading
- `customtkinter` - Modern GUI interface
- `Pillow` - Image processing
- `moviepy` - Video processing
- `openai-whisper` - Speech recognition and translation
- `torch` - AI model
- `requests` - HTTP requests for fast web scraping

### 5. Verify Installation

**Check if packages are installed:**
```bash
pip list
```

**Test basic functionality:**
```bash
python -c "import customtkinter; print('CustomTkinter OK')"
python -c "import yt_dlp; print('yt-dlp OK')"
python -c "import whisper; print('Whisper OK')"
```

### 6. FFmpeg Setup

**FFmpeg is included in the project!** No additional installation needed.

**Verify FFmpeg:**
```bash
# Windows (from project directory)
ffmpeg\bin\ffmpeg.exe -version

# Linux/macOS (if you want system-wide installation)
ffmpeg -version
```

**Optional system-wide FFmpeg installation:**

**Windows:**
1. Download from [FFmpeg Download Page](https://ffmpeg.org/download.html) or [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Download `ffmpeg-git-full.7z` file
3. Extract using 7-Zip or WinRAR
4. Copy `bin` folder to `C:\ffmpeg\`
5. Add `C:\ffmpeg\bin` to System Environment Variables → Path
6. Restart command prompt and test: `ffmpeg -version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
ffmpeg -version
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
ffmpeg -version
```

**macOS (MacPorts):**
```bash
sudo port install ffmpeg
ffmpeg -version
```

### 7. Test Installation

**Launch the application:**
```bash
python main.py
```

**Expected behavior:**
- GUI window should open in full-screen mode
- No error messages in terminal
- All buttons and elements should be visible

**If GUI doesn't open:**
```bash
# Try alternative launch
python gui.py

# Check for errors
python -c "import customtkinter; print('CustomTkinter version:', customtkinter.__version__)"
```

### 8. First Run Setup

**When you first run the application:**
1. **Select output folder:** Click "Klasör Seç" and choose where to save downloads
2. **Test with a simple YouTube URL:** Paste a short video URL to test functionality
3. **Check video info:** Click "Video Bilgisi Al" to verify connection
4. **Test download:** Try downloading a short video to verify everything works

### 9. Troubleshooting Common Issues

**"Module not found" errors:**
```bash
# Reinstall packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**FFmpeg not found:**
```bash
# Windows: Check if ffmpeg\bin\ffmpeg.exe exists in project folder
# Linux/macOS: Install system-wide FFmpeg (see step 6)
```

**GUI won't open:**
```bash
# Update CustomTkinter
pip install --upgrade customtkinter

# Check Python version compatibility
python --version
```

**Slow performance:**
```bash
# Install PyTorch with CUDA support (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 10. Development Setup (Optional)

**For developers who want to contribute:**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/
```

---

## 📖 Usage

### 🖥️ GUI Interface (Recommended)

**Launch the application:**
```bash
python main.py
```

**GUI usage steps:**
1. 🔗 **Enter URL:** Paste YouTube video/playlist link
2. 📋 **Video Info:** Use "Get Video Info" for preview
3. ⚙️ **Configure Options:**
   - Format: MP4 (Video) or MP3 (Audio)
   - Quality: Choose between 360p - 4K
   - Playlist: Check to download entire list
   - Subtitles: Check to automatically add subtitles
4. 📂 **Select Folder:** Choose download location
5. ⬇️ **Download:** Click "Start Download" button
6. 📊 **Monitor:** Track status from progress bar
7. 🔔 **Get Notified:** Receive notification when bulk download completes

### 💻 Command Line

**Video download:**
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --mp4
```

**Audio download:**
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

**Playlist download:**
```bash
python downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --mp4
```

**Download with subtitles:**
```bash
python downloader.py "URL" --mp4 --subs --auto-subs
```

**Generate Turkish subtitles:**
```bash
python main.py --subtitle video.mp4
```

### 🎯 Command Line Options

```bash
python downloader.py [URL] [OPTIONS]

Options:
  --audio-only          Download audio only (MP3)
  --mp4                 Prefer MP4 format
  --max-height 1080     Maximum resolution (360/720/1080/1440/2160)
  --no-playlist         Download only single video from playlist
  --subs                Download and embed subtitles
  --auto-subs           Also try automatically generated subtitles
  --sub-langs "tr,en"   Subtitle languages (comma-separated)
  -o, --output DIR      Output folder (default: downloads)
```

---

## 📁 Project Structure

```
StreamScribe/
├── main.py              # Main application and subtitle functionality
├── gui.py               # Modern GUI interface (CustomTkinter)
├── downloader.py        # YouTube downloader class
├── requirements.txt     # Python dependencies
├── downloads/          # Downloaded files (auto-created)
├── ffmpeg/             # Built-in FFmpeg binaries
│   └── bin/           # FFmpeg executables
├── logo/               # Application icons and logos
├── README.md           # Project documentation
└── .gitignore          # Git ignore rules
```

---

## 🔧 Advanced Usage

### 📋 Dependency Check
```bash
python main.py --check-deps
```

### 🎬 Video Processing Workflow
```bash
# 1. Download video
python main.py --gui

# 2. Generate Turkish subtitles
python main.py --subtitle "downloads/video.mp4"

# 3. Embed subtitles in video
ffmpeg -i "downloads/video.mp4" -vf subtitles="video_tr.srt" "video_with_subs.mp4"
```

### ⚙️ Customization

**Video Info Speed:**
- **Ultra-fast mode (default)** - Web scraping in ~0.5-1 second ⚡
- **Reliable mode** - yt-dlp fallback in ~2-3 seconds 🔍
- **Instant loading** - Cache system for immediate loading 💾
- **Thumbnail preview** - Visual confirmation with video image 🖼️

**Whisper Model Selection:**
- `tiny` - Fastest, lower accuracy
- `small` - Balanced (default)
- `medium` - More accurate, slower
- `large` - Most accurate, slowest

**Resolution Options:**
- `360p` - For mobile devices
- `720p` - HD quality
- `1080p` - Full HD (default)
- `1440p` - 2K quality
- `2160p` - 4K Ultra HD

---

## 🚨 Important Notes

- ⚖️ **Copyright:** Only download videos you have permission for
- 🌐 **Internet:** Stable internet connection required
- 💾 **Disk Space:** Ensure sufficient disk space for 4K videos
- 🔊 **Audio Quality:** Better audio quality provides better transcription
- 🎯 **GPU:** CUDA-enabled GPU usage recommended for Whisper
- 🔔 **Notifications:** Bulk download completion notifications are enabled by default

---

## 🆘 Troubleshooting

### Common Errors and Solutions

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**FFmpeg not found:**
- Windows: Add FFmpeg to PATH
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

**Slow downloading:**
- Check your internet connection
- Choose lower resolution
- Try closing VPN if using one

**Cannot generate subtitles:**
- Ensure PyTorch is installed correctly
- Check video audio quality
- Try smaller Whisper model (`tiny` or `small`)

**GUI won't open:**
```bash
pip install --upgrade customtkinter
```

**Thumbnail loading issues:**
- Check internet connection
- Verify URL validity
- Try refreshing video info

---

## 🤝 Contributing

1. 🍴 **Fork** the repository
2. 🌿 **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. 💾 **Commit** changes (`git commit -m 'Add amazing feature'`)
4. 📤 **Push** to branch (`git push origin feature/amazing-feature`)
5. 🔄 **Open Pull Request**
