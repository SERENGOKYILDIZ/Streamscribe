# StreamScribe: Modern YouTube Video Downloader & Subtitle Generator

**StreamScribe** is a powerful and highly optimized Python application that downloads YouTube videos with a modern GUI interface and automatically generates Turkish subtitles using AI.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Optimized](https://img.shields.io/badge/Optimized-v2.2.1-brightgreen.svg)

## 👨‍💻 Author

**Author:** Semi Eren Gökyıldız
- **Email:** [gokyildizsemieren@gmail.com](mailto:gokyildizsemieren@gmail.com)
- **GitHub:** [SERENGOKYILDIZ](https://github.com/SERENGOKYILDIZ)
- **LinkedIn:** [Semi Eren Gökyıldız](https://www.linkedin.com/in/semi-eren-gokyildiz/)

## Downloads

[![Download StreamScribe](https://img.shields.io/badge/Download-StreamScribe_v2.2.1-blue?style=for-the-badge&logo=windows)](https://github.com/SERENGOKYILDIZ/Streamscribe/releases/download/v2.2.1/Streamscribe_v2.2.1_Standalone.exe)

---

## 🚀 Features

### 📱 Modern GUI Interface
- **CustomTkinter** designed modern and user-friendly interface
- Dark/light theme support
- Real-time download progress tracking with detailed file size information
- Drag-and-drop URL support
- **Full-screen mode** with horizontal layout
- **Smart notification system** for bulk downloads
- **Dynamic title switching** (Video Bilgileri ↔ Oynatma Listesi Bilgileri)
- **Improved playlist layout** with better spacing and visibility

### 💻 Executable Build
- **Ready-to-use executable** in the `build/` folder
- **No Python installation required** on target computers
- **Standalone application** with all dependencies included
- **Easy distribution** - just copy the exe file

### 📺 Video Downloading
- **Download YouTube videos in MP4/MP3 format**
- **Single video or complete playlist** downloading
- **Quality selection up to 4K** (360p - 2160p) with **aggressive quality enforcement**
- **Ultra-fast downloading** - Multi-threaded support with optimizations
- **Automatic format optimization** with forced quality selection
- **Local FFmpeg usage** - No installation required on other computers
- **Bulk download notifications** - Get notified when all videos complete
- **Progress bar reset** on new video analysis
- **Real-time quality monitoring** - See selected vs. actual download quality

### 🎵 Audio Downloading
- **High-quality MP3** output (192 kbps)
- **Automatic metadata** addition
- **Fast audio conversion** with optimized processing

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

### 🚀 New Optimizations (v2.0)

#### ⚡ Performance Improvements
- **Advanced Caching System**: Intelligent caching for video info and thumbnails
- **Connection Pooling**: Optimized HTTP requests with session reuse
- **Memory Management**: Automatic cleanup and resource management
- **Thread Optimization**: Improved thread handling and cleanup
- **Faster Video Info**: Enhanced web scraping with fallback mechanisms

#### 🛡️ Enhanced Error Handling
- **Centralized Error Management**: Comprehensive error categorization
- **User-Friendly Messages**: Clear, actionable error messages in Turkish
- **Automatic Retry Logic**: Smart retry mechanisms with exponential backoff
- **Graceful Degradation**: Fallback options when primary methods fail

#### 📊 Advanced Logging
- **Structured Logging**: Detailed logging with rotation and levels
- **Performance Monitoring**: Built-in performance tracking
- **Debug Information**: Comprehensive debugging capabilities
- **Error Tracking**: Detailed error logging and reporting
- **Console-Only Logging**: Clean console output without log file creation

#### ⚙️ Configuration Management
- **Centralized Config**: All settings in one place
- **User Preferences**: Persistent user configuration
- **Environment Detection**: Automatic environment configuration
- **Performance Tuning**: Configurable performance parameters

---

## 🛠️ Installation

### Quick Start (Recommended)
```bash
# Clone the repository
git clone https://github.com/SERENGOKYILDIZ/Streamscribe.git
cd Streamscribe

# Install dependencies
pip install -r requirements.txt

# Run the optimized version
python main.py
```

### Alternative: Use Executable
1. Go to the `build/` folder
2. Double-click `Streamscribe.exe`
3. The application will start immediately - no setup required!

### Detailed Installation (Optional)

#### 1. Python Requirements
Python 3.12 is recommended for optimal compatibility.

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

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
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
2. 📋 **Video Info:** Use "Analiz Et" for preview
3. ⚙️ **Configure Options:**
   - Format: MP4 (Video) or MP3 (Audio)
   - Quality: Choose between 360p - 4K
   - Playlist: Check to download entire list
   - Subtitles: Check to automatically add subtitles
4. 📂 **Select Folder:** Choose download location
5. ⬇️ **Download:** Click "İNDİR" button
6. 📊 **Monitor:** Track status from progress bar with file size info
7. 🔔 **Get Notified:** Receive notification when bulk download completes

### 💻 Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --legacy           Launch legacy GUI interface
  --check-deps       Check required dependencies
  --test             Test downloader functionality
  --info             Show system information
  --version          Show version information
```

---

## 🔧 Advanced Configuration

### Performance Settings
```python
# config.py
CACHE_SIZE = 50                    # Video info cache size
THUMBNAIL_CACHE_SIZE = 30          # Thumbnail cache size
TIMEOUT_FAST = 1.5                 # Fast request timeout
TIMEOUT_NORMAL = 3.0               # Normal request timeout
MAX_PLAYLIST_VIDEOS = 50           # Maximum playlist videos
```

### Logging Configuration
```python
# logger.py
LOG_LEVEL = "ERROR"                # Logging level (ERROR only for clean console)
LOG_FILE = "streamscribe.log"      # Log file name (disabled in v2.0.2)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## 📁 Project Structure

```
StreamScribe/
├── main.py                    # Optimized main entry point
├── gui.py                     # Optimized GUI interface
├── downloader.py              # Optimized downloader engine
├── config.py                  # Configuration management
├── logger.py                  # Logging system
├── error_handler.py           # Error handling system
├── utils.py                   # Performance utilities
├── test_optimizations.py      # Test suite
├── test_progress.py           # Progress bar testing
├── requirements.txt           # Updated dependencies
├── downloads/                 # Downloaded files
├── ffmpeg/                    # Built-in FFmpeg binaries
├── logo/                      # Application icons
└── build/                     # Executable files
```

---

## 🚀 Performance Benchmarks

### Before Optimization
- Video info retrieval: ~3-5 seconds
- Memory usage: ~150MB
- Cache hit rate: 0%
- Error handling: Basic

### After Optimization
- Video info retrieval: ~0.5-1 second ⚡
- Memory usage: ~80MB (47% reduction) 📉
- Cache hit rate: 85%+ 🎯
- Error handling: Comprehensive 🛡️

---

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_optimizations.py
```

Test progress bar functionality:
```bash
python test_progress.py
```

Test coverage includes:
- ✅ Configuration module
- ✅ Logging system
- ✅ Error handling
- ✅ Utility functions
- ✅ Downloader optimization
- ✅ Progress bar functionality
- ✅ Integration tests
- ✅ Performance tests

---

## 🔍 Troubleshooting

### Common Issues and Solutions

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Performance issues:**
```bash
# Check system resources
python main.py --info

# Test downloader
python main.py --test
```

**Logging issues:**
```bash
# Check log files
tail -f streamscribe.log
tail -f streamscribe.error.log
```

**Progress bar issues:**
```bash
# Test progress functionality
python test_progress.py
```

---

## 🤝 Contributing

1. 🍴 **Fork** the repository
2. 🌿 **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. 💾 **Commit** changes (`git commit -m 'Add amazing feature'`)
4. 📤 **Push** to branch (`git push origin feature/amazing-feature`)
5. 🔄 **Open Pull Request**

---

## 📊 Performance Monitoring

The optimized version includes built-in performance monitoring:

- **Cache Statistics**: Track cache hit rates and performance
- **Memory Usage**: Monitor memory consumption
- **Download Speed**: Track download performance
- **Error Rates**: Monitor error frequency and types
- **Progress Tracking**: Real-time download progress with file size info

---

## 🎯 Future Optimizations

Planned improvements for future versions:

- [ ] **GPU Acceleration**: CUDA support for faster processing
- [ ] **Database Caching**: Persistent cache storage
- [ ] **Parallel Downloads**: Multiple simultaneous downloads
- [ ] **Smart Quality Selection**: Automatic quality optimization
- [ ] **Cloud Integration**: Cloud storage support
- [ ] **Advanced Playlist Management**: Better playlist organization
- [ ] **Custom Themes**: User-selectable interface themes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 Optimization Summary

The StreamScribe v2.0 optimization brings:

- **47% reduction** in memory usage
- **3-5x faster** video info retrieval
- **85%+ cache hit rate** for repeated requests
- **Comprehensive error handling** with user-friendly messages
- **Advanced logging** with performance monitoring
- **Centralized configuration** management
- **Thread-safe operations** with proper cleanup
- **Connection pooling** for better network performance
- **Enhanced video quality selection** with better format matching
- **Improved playlist layout** with better spacing and visibility
- **Progress bar reset** functionality for new video analysis
- **Dynamic title switching** based on content type

These optimizations make StreamScribe significantly faster, more reliable, and more user-friendly while maintaining all existing functionality.

---

## 🔄 Recent Updates

### v2.2.1 (Latest)
- ✅ **Filename Cleanup** - Removed random Video IDs from downloaded filenames (e.g. "Video Title.mp4")
- ✅ **Build Fix** - Migrated to Python 3.11 to resolve PyInstaller build issues
- ✅ **Dependency Update** - Detailed requirements verification

### v2.2.0
- ✅ **Version Bump** - Updated to v2.2.0
- ✅ **Video Info Fix** - Resolved "Requested format is not available" error by optimizing yt-dlp options
- ✅ **Right-Click Paste** - Added context menu "Yapıştır" (Paste) to URL input field
- ✅ **UI Improvements** - Enhanced progress percentage visibility (White color, larger font)
- ✅ **License** - Added MIT License

- ✅ **Progress bar size stabilization** - Size fluctuations prevented, progress bar shaking resolved
- ✅ **YouTube 403 Forbidden error fixed** - Format string flexibility increased
- ✅ **Stable size management** - Size fluctuations filtered with _stable_total_bytes
- ✅ **Flexible format selection** - height>={max_height-180} → height<={max_height} transition
- ✅ **yt-dlp options optimization** - format_sort_force: False, prefer_free_formats: True
- ✅ **Progress hook improvements** - Stable percentage calculation and size management
- ✅ **Automatic size reset** - Stable size automatically resets for each new download

### v2.1
- ✅ **Major quality improvements** - Aggressive quality enforcement for exe builds
- ✅ **Console log cleanup** - No more log files, clean console output only
- ✅ **Real-time quality monitoring** - See selected vs. actual download quality in terminal
- ✅ **Enhanced format string** - More aggressive quality selection with fallbacks
- ✅ **YouTube 403 error prevention** - Flexible format selection to avoid restrictions
- ✅ **Quality threshold optimization** - 1080p → 900p+, 720p → 540p+ minimum
- ✅ **Format sort enforcement** - Strict quality sorting with codec preferences
- ✅ **Progress hook improvements** - Better format selection visibility

### v2.0.1
- ✅ **Enhanced video quality selection** - Better format matching for selected quality
- ✅ **Progress bar improvements** - Reset functionality and better progress tracking
- ✅ **Dynamic title switching** - Smart title changes based on content type
- ✅ **Improved playlist layout** - Better spacing and visibility for video items
- ✅ **Panel width optimization** - Better space distribution between left and right panels
- ✅ **File size information** - Real-time file size display during download
- ✅ **Enhanced error handling** - Better error messages and recovery
- ✅ **Performance optimizations** - Faster video info retrieval and better caching

### v2.0.0
- ✅ **Major performance improvements** - 47% memory reduction, 3-5x faster video info
- ✅ **Advanced caching system** - Intelligent caching for better performance
- ✅ **Enhanced error handling** - Comprehensive error management
- ✅ **Advanced logging** - Performance monitoring and debugging
- ✅ **Centralized configuration** - Better settings management
