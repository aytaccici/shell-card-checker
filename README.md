# 🚗 Shell Kart Bakiye Kontrol Scripti

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

> Shell Türkiye kart bakiyesini otomatik olarak kontrol eden Python scripti. CAPTCHA'yı OCR ile otomatik çözer ve bakiye değişikliklerinde bildirim gönderir.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Yapılandırma](#-yapılandırma)
- [Bildirimler](#-bildirimler)
- [Cron Job](#-cron-job)
- [Sorun Giderme](#-sorun-giderme)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

## ✨ Özellikler

- 🤖 **Otomatik CAPTCHA Çözme** - OCR teknolojisi ile %90+ başarı oranı
- 📊 **Bakiye Değişikliği Takibi** - Sadece değişiklik olduğunda bildirim
- 📨 **Çoklu Bildirim Desteği** - Telegram, Email, WhatsApp
- 💾 **Otomatik Kayıt** - Son bakiyeyi JSON dosyasında saklar
- ⚙️ **Kolay Yapılandırma** - `.env` dosyası ile basit kurulum
- 🔄 **Cron Job Desteği** - Otomatik periyodik kontrol
- 🐧 **Raspberry Pi Uyumlu** - Düşük kaynak kullanımı
- 📝 **Detaylı Loglama** - Tüm işlemler loglanır

## 🖼️ Ekran Görüntüleri

### Terminal Çıktısı
```
============================================================
🚗 SHELL KART BAKİYE KONTROL
============================================================
⏰ Zaman: 2025-11-15 00:00:00
============================================================

📄 Sayfa yükleniyor...
✅ Sayfa yüklendi
🤖 CAPTCHA otomatik çözülüyor (OCR)...
✅ CAPTCHA otomatik çözüldü: ABC123

📊 BAKİYE SONUÇLARI
============================================================
💳 Kart Numarası: 2400030848
📋 Kart Tipi: PARTNERCARD
💰 Bakiye: 4,500.00 TL
✅ Durum: Aktif
============================================================
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- Tesseract OCR
- İnternet bağlantısı

### Hızlı Kurulum

#### Linux / macOS

```bash
# Repository'yi klonlayın
git clone https://github.com/kullaniciadi/shell-balance-checker.git
cd shell-balance-checker

# Tesseract OCR kurulumu
# Ubuntu/Debian:
sudo apt install tesseract-ocr

# macOS:
brew install tesseract

# Python paketlerini kurun
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Raspberry Pi (Otomatik)

```bash
# Repository'yi klonlayın
git clone https://github.com/kullaniciadi/shell-balance-checker.git
cd shell-balance-checker

# Otomatik kurulum script'ini çalıştırın
chmod +x install.sh
./install.sh
```

Detaylı Raspberry Pi kurulumu için [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) dosyasına bakın.

### Yapılandırma

1. `.env` dosyasını oluşturun:
```bash
cp .env.example .env
nano .env
```

2. En azından şu ayarları yapın:
```env
CARD_NUMBER=2400030848
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

3. Test edin:
```bash
python3 shell_auto_checker.py
```

## 💻 Kullanım

### Manuel Çalıştırma

```bash
# Sanal ortamı aktifleştirin
source venv/bin/activate

# .env dosyasından kart numarasını kullan
python3 shell_auto_checker.py

# Veya komut satırından kart numarası belirtin
python3 shell_auto_checker.py 2400030848
```

### Otomatik Çalıştırma (Cron Job)

Her 30 dakikada bir otomatik kontrol için:

```bash
# Crontab'ı düzenleyin
crontab -e

# Şu satırı ekleyin (yolu kendi dizininize göre değiştirin)
*/30 * * * * /home/pi/shell-balance-checker/run_check.sh
```

Detaylı cron job kurulumu için [CRON_SETUP.md](CRON_SETUP.md) dosyasına bakın.

## ⚙️ Yapılandırma

### .env Dosyası Ayarları

```env
# Kart numarası (zorunlu)
CARD_NUMBER=2400030848

# Telegram bildirimleri
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email bildirimleri
EMAIL_ENABLED=false
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_PASSWORD=your_app_password

# WhatsApp bildirimleri (Twilio)
WHATSAPP_ENABLED=false
WHATSAPP_TWILIO_ACCOUNT_SID=your_account_sid
WHATSAPP_TWILIO_AUTH_TOKEN=your_auth_token
WHATSAPP_TWILIO_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+905551234567
```

### Kart Numarası Öncelik Sırası

1. `.env` dosyasından (`CARD_NUMBER`)
2. Komut satırı argümanı
3. Kullanıcı inputu (interaktif mod)
4. Varsayılan değer (`2400030848`)

## 📨 Bildirimler

### Telegram (Önerilen) 🤖

1. [@BotFather](https://t.me/BotFather)'a Telegram'da mesaj gönderin
2. `/newbot` komutu ile yeni bot oluşturun
3. Bot token'ınızı alın
4. Chat ID'nizi alın:
   ```bash
   python3 get_chat_id.py
   ```
   Veya botunuza mesaj gönderip şu komutu çalıştırın:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getUpdates | grep -o '"id":[0-9]*' | head -1
   ```
5. `.env` dosyasına ekleyin

### Email 📧

**Gmail için:**
1. Google Hesabınız > Güvenlik > 2 Adımlı Doğrulama
2. Uygulama şifreleri > Yeni uygulama şifresi oluştur
3. Oluşturulan şifreyi `.env` dosyasına ekleyin

**Diğer Email Sağlayıcıları:**
- SMTP sunucu ve port bilgilerini `.env` dosyasına ekleyin

### WhatsApp (Twilio) 📱

1. [Twilio](https://www.twilio.com) hesabı oluşturun
2. WhatsApp API'yi aktifleştirin
3. Twilio bilgilerinizi `.env` dosyasına ekleyin
4. Twilio kütüphanesini kurun:
   ```bash
   pip install twilio
   ```

## 📊 Bakiye Takibi

Script her çalıştırmada:

1. ✅ Son bakiyeyi `balance_{kart_numarası}.json` dosyasından okur
2. 🔍 Yeni bakiyeyle karşılaştırır
3. 📨 **Değişiklik varsa:** Bildirim gönderir (Telegram/Email/WhatsApp)
4. 📝 **Değişiklik yoksa:** Sadece console'a log yazar

### Bakiye Dosyası Formatı

```json
{
  "card_number": "2400030848",
  "balance": 4500.0,
  "card_type": "PARTNERCARD",
  "status": "Aktif",
  "last_check": "2025-11-15 00:00:00",
  "timestamp": 1734212700.0
}
```

## 🔄 Cron Job

### Zamanlama Örnekleri

```cron
# Her 30 dakikada bir (önerilen)
*/30 * * * * /path/to/run_check.sh

# Her 15 dakikada bir
*/15 * * * * /path/to/run_check.sh

# Her saat başı
0 * * * * /path/to/run_check.sh

# Her gün belirli saatlerde (09:00, 12:00, 18:00)
0 9,12,18 * * * /path/to/run_check.sh

# Sadece hafta içi
*/30 * * * 1-5 /path/to/run_check.sh
```

### Log Dosyaları

```bash
# Son logları görüntüle
tail -f cron.log

# Son 100 satırı görüntüle
tail -n 100 cron.log

# Belirli bir tarihteki logları görüntüle
grep "2025-11-15" cron.log
```

## 🐛 Sorun Giderme

### CAPTCHA Çözülemiyor

```bash
# Tesseract'ın kurulu olduğunu kontrol edin
tesseract --version

# OCR kütüphanelerini kontrol edin
pip list | grep -E "(pytesseract|Pillow)"

# Test edin
python3 -c "import pytesseract; from PIL import Image; print('OK')"
```

### Bildirimler Çalışmıyor

- ✅ `.env` dosyasındaki ayarları kontrol edin
- ✅ API key'lerin doğru olduğundan emin olun
- ✅ Bildirim servislerinin aktif olduğunu kontrol edin
- ✅ Log dosyalarını kontrol edin

### Cron Job Çalışmıyor

```bash
# Cron servisinin çalıştığını kontrol edin
sudo systemctl status cron

# Cron loglarını kontrol edin
grep CRON /var/log/syslog | tail -20

# Yolların mutlak (absolute) olduğundan emin olun
which python3  # Sanal ortam içinde
```

### Python Modülleri Bulunamıyor

```bash
# Sanal ortamı aktifleştirin
source venv/bin/activate

# Paketleri yeniden kurun
pip install -r requirements.txt
```

## 📁 Proje Yapısı

```
shell-balance-checker/
├── shell_auto_checker.py      # Ana script
├── run_check.sh               # Cron job wrapper script
├── install.sh                 # Otomatik kurulum scripti
├── get_chat_id.py             # Telegram Chat ID alıcı
├── requirements.txt           # Python paket bağımlılıkları
├── .env.example               # Örnek yapılandırma dosyası
├── .gitignore                 # Git ignore kuralları
├── README.md                  # Bu dosya
├── RASPBERRY_PI_SETUP.md      # Raspberry Pi kurulum rehberi
└── CRON_SETUP.md              # Cron job kurulum rehberi
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### Katkı Kuralları

- Kod standartlarına uyun (PEP 8)
- Yeni özellikler için test ekleyin
- Dokümantasyonu güncelleyin
- Commit mesajlarını açıklayıcı yazın

## 📝 Changelog

### v1.0.0 (2025-11-15)
- ✨ İlk sürüm
- 🤖 Otomatik CAPTCHA çözme
- 📨 Çoklu bildirim desteği
- 📊 Bakiye değişikliği takibi
- 🔄 Cron job desteği

## 🔒 Güvenlik

- ⚠️ `.env` dosyasını **asla** Git'e commit etmeyin
- 🔑 API key'leri güvenli tutun
- 📝 `.gitignore` dosyası hassas dosyaları otomatik olarak hariç tutar
- 🔐 Production ortamında `.env` dosyasına uygun izinler verin:
  ```bash
  chmod 600 .env
  ```

## ⚠️ Yasal Uyarı

Bu script Shell Türkiye'nin resmi API'si değildir. Kullanım sorumluluğu size aittir. Script'i kullanarak Shell Türkiye'nin kullanım şartlarını ihlal etmemeye dikkat edin.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👤 Yazar

**Aytaç Cici**

- GitHub: [@kullaniciadi](https://github.com/kullaniciadi)
- Email: your-email@example.com

## 🙏 Teşekkürler

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - CAPTCHA çözme için
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing için
- [Requests](https://requests.readthedocs.io/) - HTTP istekleri için

## ⭐ Yıldız Verin

Bu projeyi beğendiyseniz, yıldız vermeyi unutmayın! ⭐

---

**Not:** Bu proje aktif olarak geliştirilmektedir. Sorun bildirimi ve öneriler için issue açabilirsiniz.
