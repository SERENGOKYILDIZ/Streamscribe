# Oturum Doğrulama ve Çerez Rehberi (Udemy vb.)

StreamScribe, Udemy ve üyelik gerektiren diğer platformlardan kayıtlı olduğunuz kursları ve videoları indirebilmeniz için gelişmiş çerez (cookie) ve oturum yöntemleri sunar.

---

## 🎯 1. Yöntem: DevTools Cookie Header (En Kararlı ve Önerilen Yöntem)

Windows 11/10 üzerinde Chrome ve Edge tarayıcılarının yeni "App-Bound Encryption" koruması, harici uygulamaların tarayıcı veritabanından doğrudan çerez şifresi çözmesini engelleyebilir. Bu sebeple **DevTools Cookie Header** yöntemi %100 kararlı çalışan en güvenilir çözümdür.

### Adım Adım Nasıl Alınır?

1. Tarayıcınızdan (Chrome, Edge, Firefox, Brave) [Udemy](https://www.udemy.com)'ye normal şekilde giriş yapın.
2. Klavyeden **F12** tuşuna basarak (veya sayfaya sağ tıklayıp *İncele* diyerek) Geliştirici Araçları'nı (DevTools) açın.
3. Üstteki **Network (Ağ)** sekmesine geçin.
4. Sayfayı yenileyin (**F5**).
5. İstek listesindeki ilk `udemy.com` isteğine tıklayın.
6. Sağ taraftaki **Headers (Başlıklar)** panelinde **Request Headers (İstek Başlıkları)** altına inin.
7. `Cookie:` satırının karşısındaki tüm metni kopyalayın (`client_id=...; access_token=...; dj_session_id=...`).
8. StreamScribe **Ayarlar** sekmesine gelin, *"Giriş Gerektiren Siteler (Udemy vb.)"* kutucuğuna yapıştırıp **"Çerez Başlığını Doğrula & Uygula"** butonuna basın.

> 🔒 **Gizlilik:** Çerezler sadece yerel oturumunuzda geçici bir Netscape dosyasında tutulur, hiçbir yere gönderilmez ve şifreleriniz asla kaydedilmez.

---

## 🌐 2. Yöntem: Canlı Tarayıcı Çerezleri

StreamScribe, bilgisayarınızda yüklü tarayıcıların oturum çerezlerini doğrudan okuyabilir:
- **Desteklenen Tarayıcılar:** Chrome, Firefox, Edge, Brave.
- **Kullanım:** Ayarlar sekmesindeki "Veya Tarayıcı Çerezi" dropdown menüsünden kullandığınız tarayıcıyı seçin.
- ⚠️ **Önemli Not:** Tarayıcıdan çerez okunurken veritabanı kilitlenmelerini önlemek için ilgili tarayıcının tamamen kapalı olması önerilir.

---

## ⚠️ DRM Korumalı İçerikler Hakkında

- StreamScribe bir **DRM kırma aracı değildir**.
- Platformlar tarafından DRM (Widevine) ile şifrelenmiş içerikler `yt-dlp` tarafından yasal olarak reddedilir.
- Bu aracı yalnızca kayıtlı olduğunuz kursları kişisel çevrimdışı arşiviniz için indirmek amacıyla kullanınız.
