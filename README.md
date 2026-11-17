<div align="center">

# 🎬 StreamScribe
### Ultra-Hızlı Modern Video İndirici & Whisper Yapay Zeka Transkripsiyonu

[![En Son Sürümü İndir](https://img.shields.io/github/v/release/SERENGOKYILDIZ/Streamscribe?label=⬇️%20En%20Son%20Sürümü%20İndir%20(Setup%20%2F%20Portable)&style=for-the-badge&logo=windows&logoColor=white&color=2563EB)](https://github.com/SERENGOKYILDIZ/Streamscribe/releases/latest)
[![Tüm Sürümler](https://img.shields.io/badge/📦_Tüm_Sürümler-GitHub_Releases-1E293B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SERENGOKYILDIZ/Streamscribe/releases)

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-v3.2-brightgreen.svg)

</div>

---

**StreamScribe**, [yt-dlp](https://github.com/yt-dlp/yt-dlp), [PySide6 (Qt)](https://doc.qt.io/qtforpython/) ve [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) üzerine inşa edilmiş, modern, şık ve yüksek performanslı bir masaüstü video indirme ve yapay zeka altyazı/transkripsiyon uygulamasıdır.

> 💡 **Kurulum veya Python gerekmez:** Yukarıdaki butona tıklayarak en son sürümün Setup kurulum sihirbazını (`Streamscribe_v3.2_Setup.exe`) veya taşınabilir arşivini (`Portable.zip`) indirebilirsiniz. Dahili FFmpeg ve tüm bağımlılıklar pakete dahildir; 0.3 saniyede anında açılır.

---

## 👨‍💻 Yazar (Author)

**Geliştirici:** Semi Eren Gökyıldız
- **E-posta:** [gokyildizsemieren@gmail.com](mailto:gokyildizsemieren@gmail.com)
- **GitHub:** [@SERENGOKYILDIZ](https://github.com/SERENGOKYILDIZ)
- **LinkedIn:** [Semi Eren Gökyıldız](https://www.linkedin.com/in/semi-eren-gokyildiz/)

---

## 🚀 Öne Çıkan Özellikler (v3.2)

### 🎨 Modern & Ferah PySide6 (Qt) Arayüzü
- **Sıfırdan Yenilenen Mimari:** Eski hantal arayüz yerine, akıcı ve duyarlı PySide6 (Qt) mimarisi.
- **Koyu Tema (Slate 900):** Göz yormayan, pürüzsüz kartlar ve dikişsiz şeffaf tipografi.
- **Sol Kenar Çubuğu (Sidebar):** İndirici, Canlı Kuyruk, Geçmiş ve Ayarlar sekmeleri arasında tek tıkla geçiş.
- **High-DPI Desteği:** 4K, 2K ve farklı ölçeklendirme oranlarına sahip ekranlarda pürüzsüz görüntü.

### 📥 Çoklu İndirme Kuyruğu & Playlist Gruplama
- **Otomatik Playlist Gruplama:** Oynatma listelerinden eklenen videolar kuyrukta tek bir derli toplu grup kartı altında toplanır. Katlanabilir liste ve toplu ilerleme yüzdesi sunar.
- **Eşzamanlı İndirme Havuzu:** Arka planda birden fazla videoyu aynı anda indirebilme (1-5 arası ayarlanabilir).
- **Canlı Takip:** Anlık indirme hızı (MB/s), kalan süre (ETA), indirilen boyut ve ilerleme çubuğu.
- **Gerçek İptal (Cancel) Desteği:** İstenen indirmeyi donma olmadan anında durdurabilme veya tümünü tek tıkla iptal etme.
- **Klasörde Aç:** İndirme tamamlandığında dosyayı doğrudan Windows Gezgini'nde açabilme.

### 🎬 Evrensel Video & Ses Uyumluluğu (H.264 + AAC)
- **Windows Oynatıcı Garantisi:** YouTube'un sunduğu ve standart Windows oynatıcılarının açamadığı AV1/VP9 codec'leri yerine, **H.264 (AVC) + AAC** format önceliği. İndirilen videolar Windows Media Player, Filmler ve TV, telefonlar ve televizyonlarda çift tıklandığında doğrudan açılır.
- **Hata Toleranslı Altyazı Fallback'i:** Altyazı indirilirken YouTube 429 Too Many Requests verirse veya altyazı yoksa video indirmesi iptal edilmez; motor otomatik olarak altyazısız indirmeye devam eder.
- **Kalite Seçimi:** 4K (2160p), 1440p, 1080p, 720p, 480p veya Yalnızca Ses (192 kbps MP3).
- **Altyazı Gömme:** Kaynakta mevcut olan altyazıları otomatik indirip MP4 içine uyumlu şekilde gömme (`FFmpegSubtitlesConvertor`).

### 🎙️ Whisper Yapay Zeka Transkripsiyonu
- **Yerel Altyazı & Metin Çıkarma:** İndirilen video veya seslerden yerel OpenAI Whisper modeli ile otomatik altyazı (`.srt`) ve düz metin (`.txt`) üretme.
- **Model Seçimi:** `tiny`, `base`, `small`, `medium` modelleri arasından ihtiyaca göre seçim.
- **GPU / CPU Desteği:** CUDA destekli ekran kartı varsa otomatik olarak GPU üzerinde yüksek hızda çalışır.

### 🎓 Udemy ve Oturum Gerektiren Siteler
- **DevTools Cookie Header:** Tarayıcı DevTools (F12) Network sekmesinden kopyalanan `Cookie` başlığını tek tıkla yapıştırma (Windows App-Bound Encryption ve 403 engellerini aşmanın en güvenilir yöntemi).
- **Tarayıcı Çerezleri:** Chrome, Firefox, Edge ve Brave tarayıcılarından çerez okuma desteği.
- **Otomatik URL Normalizasyonu:** Güncel Udemy ders linklerini yt-dlp uyumlu formata otomatik dönüştürür.

### 📜 SQLite İndirme Geçmişi
- İndirilen veya transkribe edilen tüm videolar yerel SQLite veritabanında saklanır.
- Başlık veya URL ile anında arama yapabilme, dosyanın bulunduğu klasöre gitme ve geçmişi temizleme.

---

## 📚 Dokümantasyon

Detaylı teknik kılavuzlar için `docs/` dizinini inceleyebilirsiniz:
- [🏛️ Mimari ve Tasarım Kılavuzu](docs/ARCHITECTURE.md)
- [🔑 Oturum ve Çerez Yönetimi (Udemy)](docs/AUTHENTICATION.md)
- [🏗️ Standalone EXE Derleme Rehberi](docs/BUILD_GUIDE.md)

---

## 📁 Proje Klasör Mimarisi

```text
Streamscribe/
├── src/                        # Tüm uygulama kaynak kodları
│   ├── core/                   # İş mantığı, yt-dlp ve Whisper motoru
│   │   ├── engine.py           # yt-dlp indirme motoru ve H.264/AAC format kontrolü
│   │   ├── metadata.py         # Video/oynatma listesi metadata analiz motoru
│   │   ├── queue_manager.py    # Thread-pool eşzamanlı kuyruk yöneticisi & Qt Signals
│   │   ├── transcriber.py      # Whisper yerel transkripsiyon motoru
│   │   └── ffmpeg_helper.py    # Yerel ve sistem FFmpeg tespiti ve yardımcıları
│   ├── services/               # Servisler ve kalıcı veri katmanı
│   │   ├── config_service.py   # JSON tabanlı kalıcı ayarlar (~/.streamscribe/streamscribe_settings.json)
│   │   ├── history_service.py  # SQLite tabanlı indirme geçmişi (~/.streamscribe/history.db)
│   │   └── logger.py           # Yapılandırılmış ve döngüsel loglama servisi
│   ├── ui/                     # PySide6 (Qt) arayüz katmanı
│   │   ├── app.py              # Ana pencere ve navigasyon sidebar'ı
│   │   ├── styles.py           # Modern Dark Theme QSS (Slate 900 paleti)
│   │   ├── components/         # MediaCard, PlaylistCard, QueueItemWidget, PlaylistGroupWidget
│   │   └── views/              # DownloaderView, QueueView, HistoryView, SettingsView
│   ├── config.py               # Uygulama sabitleri ve yapılandırma
│   └── legacy/                 # Eski sürümlerden arşivlenen modüller
├── docs/                       # Geliştirici ve kullanıcı dokümantasyonu
├── ffmpeg/                     # Taşınabilir yerel FFmpeg ikilileri
├── logo/                       # İkon ve görseller
├── releases/                   # Derlenmiş hazır EXE sürümleri
├── main.py                     # Temiz PySide6 giriş noktası
├── requirements.txt            # Bağımlılık listesi
├── Streamscribe.spec           # PyInstaller derleme profili
└── build.py                    # Tek tıkla EXE derleme betiği
```

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.11 veya üzeri
- Windows 10/11, macOS veya Linux

### Adım Adım Kurulum

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/SERENGOKYILDIZ/Streamscribe.git
   cd Streamscribe
   ```

2. **Sanal Ortam Oluşturun ve Aktif Edin:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı Başlatın:**
   ```bash
   python main.py
   ```

---

## 📦 Dağıtım, Kurulum Sihirbazı & Derleme (Build)

Uygulama sürümü kök dizindeki [`version.ini`](version.ini) dosyasından tek merkezden yönetilir (Geliştirici bilgisi statik olarak **Semi Eren Gökyıldız** şeklindedir).

- **Sadece Uygulama & Portable Arşiv Derlemek İçin:**
  ```powershell
  python build.py
  ```
  Çıktılar `releases/v3.2/` altında (`Streamscribe_v3.2/` ve `Streamscribe_v3.2_Portable.zip`) oluşturulur.

- **Hem Derleme Yapıp Hem de Inno Setup Kurulum Sihirbazı (`Setup.exe`) Üretmek İçin:**
  ```powershell
  .\setup.cmd
  ```
  Kurulum dosyası `release_setup/Streamscribe_v3.2_Setup.exe` dizininde oluşturulur.

---

## ⚖️ Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
