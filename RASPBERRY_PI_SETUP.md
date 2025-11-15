# Raspberry Pi Kurulum Rehberi - Shell Kart Bakiye Kontrol

Bu rehber Raspberry Pi'ye Shell kart bakiye kontrol scriptini kurmak için adım adım talimatlar içerir.

## 📋 Gereksinimler

- Raspberry Pi (herhangi bir model)
- Raspbian OS veya Raspberry Pi OS
- İnternet bağlantısı
- Python 3.x

## 🔧 Kurulum Adımları

### 1. Sistem Güncellemesi

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Python ve Gerekli Paketlerin Kurulumu

```bash
# Python 3 ve pip zaten kurulu olmalı, kontrol edin
python3 --version
pip3 --version

# Gerekli sistem paketleri
sudo apt install -y python3-pip python3-venv tesseract-ocr libtesseract-dev libjpeg-dev zlib1g-dev

# Tesseract OCR kurulumu (CAPTCHA çözme için)
sudo apt install -y tesseract-ocr
```

### 3. Proje Klasörü Oluşturma

```bash
# Proje klasörü oluştur
mkdir -p ~/shell-balance-checker
cd ~/shell-balance-checker

# Dosyaları buraya kopyalayın (scp, git clone veya manuel)
```

### 4. Python Sanal Ortamı Oluşturma

```bash
# Sanal ortam oluştur
python3 -m venv venv

# Sanal ortamı aktifleştir
source venv/bin/activate

# Python paketlerini kur
pip install --upgrade pip
pip install requests beautifulsoup4 pytesseract pillow python-dotenv
```

### 5. Dosyaları Kopyalama

Dosyaları Raspberry Pi'ye kopyalayın:

**Yöntem 1: SCP ile (Mac/Linux'tan)**
```bash
scp shell_auto_checker.py pi@raspberrypi.local:~/shell-balance-checker/
scp .env.example pi@raspberrypi.local:~/shell-balance-checker/
```

**Yöntem 2: Git ile**
```bash
cd ~/shell-balance-checker
# Git repo'ya push edip pull edin
```

**Yöntem 3: USB ile**
- USB bellek kullanarak dosyaları kopyalayın

### 6. .env Dosyasını Yapılandırma

```bash
cd ~/shell-balance-checker
cp .env.example .env
nano .env
```

`.env` dosyasını düzenleyin:

```env
# Kart numarası
CARD_NUMBER=2400030848

# Telegram bildirim ayarları
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email bildirim ayarları (opsiyonel)
EMAIL_ENABLED=false
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_PASSWORD=your_app_password

# WhatsApp bildirim ayarları (opsiyonel - Twilio gerekli)
WHATSAPP_ENABLED=false
WHATSAPP_TWILIO_ACCOUNT_SID=
WHATSAPP_TWILIO_AUTH_TOKEN=
WHATSAPP_TWILIO_FROM=
WHATSAPP_TO=
```

**Önemli:** `.env` dosyasını düzenledikten sonra kaydedin (Ctrl+O, Enter, Ctrl+X)

### 7. Script'i Çalıştırılabilir Yapma

```bash
chmod +x shell_auto_checker.py
```

### 8. İlk Test

```bash
# Sanal ortam aktifken
source venv/bin/activate

# Script'i test edin
python3 shell_auto_checker.py
```

Eğer her şey çalışıyorsa, bakiye bilgilerini göreceksiniz.

## 🔄 Cron Job Kurulumu

### Yöntem 1: Her 30 Dakikada Bir (Önerilen)

```bash
# Crontab'ı düzenle
crontab -e
```

Aşağıdaki satırı ekleyin:

```cron
*/30 * * * * cd /home/pi/shell-balance-checker && /home/pi/shell-balance-checker/venv/bin/python3 /home/pi/shell-balance-checker/shell_auto_checker.py >> /home/pi/shell-balance-checker/cron.log 2>&1
```

**Açıklama:**
- `*/30 * * * *` - Her 30 dakikada bir
- `cd /home/pi/shell-balance-checker` - Çalışma dizinine git
- `/home/pi/shell-balance-checker/venv/bin/python3` - Sanal ortamdaki Python'u kullan
- `>> /home/pi/shell-balance-checker/cron.log 2>&1` - Log dosyasına yaz

### Yönt 2: Shell Script ile (Daha Temiz)

Önce bir wrapper script oluşturun:

```bash
nano ~/shell-balance-checker/run_check.sh
```

İçeriği:

```bash
#!/bin/bash
cd /home/pi/shell-balance-checker
source venv/bin/activate
python3 shell_auto_checker.py
deactivate
```

Çalıştırılabilir yapın:

```bash
chmod +x ~/shell-balance-checker/run_check.sh
```

Crontab'a ekleyin:

```cron
*/30 * * * * /home/pi/shell-balance-checker/run_check.sh >> /home/pi/shell-balance-checker/cron.log 2>&1
```

### Cron Zamanlama Örnekleri

```cron
# Her 30 dakikada bir
*/30 * * * * ...

# Her saat başı
0 * * * * ...

# Her gün saat 09:00'da
0 9 * * * ...

# Her gün saat 09:00 ve 18:00'da
0 9,18 * * * ...

# Her 15 dakikada bir
*/15 * * * * ...
```

## 📊 Log Dosyaları

Log dosyaları otomatik olarak oluşturulur:

- `cron.log` - Cron job çıktıları
- `balance_{kart_numarası}.json` - Son bakiye bilgileri

Log dosyalarını görüntülemek için:

```bash
# Son logları görüntüle
tail -f ~/shell-balance-checker/cron.log

# Son 50 satırı görüntüle
tail -n 50 ~/shell-balance-checker/cron.log
```

## 🔍 Sorun Giderme

### Cron Job Çalışmıyor

1. **Cron servisinin çalıştığını kontrol edin:**
   ```bash
   sudo systemctl status cron
   ```

2. **Cron loglarını kontrol edin:**
   ```bash
   grep CRON /var/log/syslog
   ```

3. **Manuel test edin:**
   ```bash
   cd ~/shell-balance-checker
   source venv/bin/activate
   python3 shell_auto_checker.py
   ```

4. **Yol sorunlarını kontrol edin:**
   - Crontab'daki tüm yolların mutlak (absolute) olduğundan emin olun
   - Sanal ortam yolunu kontrol edin: `which python3` (venv içinde)

### CAPTCHA Çözülemiyor

```bash
# Tesseract'ın kurulu olduğunu kontrol edin
tesseract --version

# Test edin
tesseract test_image.png stdout
```

### Python Modülleri Bulunamıyor

```bash
# Sanal ortamı aktifleştirin
source venv/bin/activate

# Paketleri yeniden kurun
pip install -r requirements.txt
```

### İnternet Bağlantısı Sorunları

```bash
# İnternet bağlantısını test edin
ping -c 3 google.com

# DNS çözümlemesini test edin
nslookup sfs.turkiyeshell.com
```

## 📝 Bakım

### Log Dosyalarını Temizleme

Log dosyaları büyüyebilir, düzenli temizleyin:

```bash
# Eski logları temizle (30 günden eski)
find ~/shell-balance-checker -name "*.log" -mtime +30 -delete
```

### Disk Kullanımını Kontrol Etme

```bash
# Disk kullanımını kontrol edin
df -h

# Proje klasörünün boyutunu kontrol edin
du -sh ~/shell-balance-checker
```

### Bakiye Dosyalarını Yedekleme

```bash
# Bakiye dosyalarını yedekle
cp ~/shell-balance-checker/balance_*.json ~/backup/
```

## 🔐 Güvenlik Notları

1. **`.env` dosyasını koruyun:**
   ```bash
   chmod 600 ~/shell-balance-checker/.env
   ```

2. **`.gitignore` dosyasına ekleyin:**
   ```
   .env
   balance_*.json
   cron.log
   ```

3. **API key'leri güvenli tutun:**
   - `.env` dosyasını kimseyle paylaşmayın
   - Git'e commit etmeyin

## 📞 Destek

Sorun yaşarsanız:

1. Log dosyalarını kontrol edin
2. Manuel test yapın
3. Cron job zamanlamasını kontrol edin
4. Python ve paket versiyonlarını kontrol edin

## ✅ Kurulum Kontrol Listesi

- [ ] Sistem güncellendi
- [ ] Python 3 ve pip kurulu
- [ ] Tesseract OCR kurulu
- [ ] Proje klasörü oluşturuldu
- [ ] Sanal ortam oluşturuldu ve aktifleştirildi
- [ ] Python paketleri kuruldu
- [ ] Dosyalar kopyalandı
- [ ] `.env` dosyası yapılandırıldı
- [ ] İlk test başarılı
- [ ] Cron job kuruldu
- [ ] Cron job test edildi
- [ ] Log dosyaları kontrol edildi

## 🎉 Tamamlandı!

Kurulum tamamlandı! Script her 30 dakikada bir otomatik olarak çalışacak ve bakiye değişikliklerinde bildirim gönderecek.

