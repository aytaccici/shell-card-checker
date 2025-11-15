# Cron Job Kurulum Rehberi

Bu rehber Shell Kart Bakiye Kontrol scriptini otomatik çalıştırmak için cron job kurulumunu açıklar.

## 📋 Ön Gereksinimler

- Script'in kurulu ve test edilmiş olması
- `run_check.sh` wrapper script'inin hazır olması
- Sanal ortamın (venv) oluşturulmuş olması

## 🔧 Adım Adım Kurulum

### 1. Wrapper Script'i Hazırlama

`run_check.sh` dosyasını çalıştırılabilir yapın:

```bash
cd ~/shell-balance-checker
chmod +x run_check.sh
```

### 2. Manuel Test

Önce script'i manuel olarak test edin:

```bash
cd ~/shell-balance-checker
./run_check.sh
```

Başarılı olursa, cron job'a geçebilirsiniz.

### 3. Cron Job Ekleme

Crontab'ı düzenleyin:

```bash
crontab -e
```

Aşağıdaki satırı ekleyin (her 30 dakikada bir):

```cron
*/30 * * * * /home/pi/shell-balance-checker/run_check.sh
```

**Önemli:** `/home/pi/shell-balance-checker` yolunu kendi proje dizininize göre değiştirin!

### 4. Cron Job'u Kaydetme

- Nano editörü kullanıyorsanız: `Ctrl+O` (kaydet), `Enter`, `Ctrl+X` (çık)
- Vim kullanıyorsanız: `:wq` (kaydet ve çık)

### 5. Cron Job'u Kontrol Etme

```bash
# Aktif cron job'ları listele
crontab -l

# Cron servisinin çalıştığını kontrol et
sudo systemctl status cron
```

## ⏰ Zamanlama Örnekleri

### Her 30 Dakikada Bir (Önerilen)
```cron
*/30 * * * * /home/pi/shell-balance-checker/run_check.sh
```

### Her 15 Dakikada Bir
```cron
*/15 * * * * /home/pi/shell-balance-checker/run_check.sh
```

### Her Saat Başı
```cron
0 * * * * /home/pi/shell-balance-checker/run_check.sh
```

### Her Gün Belirli Saatlerde (09:00, 12:00, 18:00)
```cron
0 9,12,18 * * * /home/pi/shell-balance-checker/run_check.sh
```

### Her Gün Gece Yarısı
```cron
0 0 * * * /home/pi/shell-balance-checker/run_check.sh
```

### Sadece Hafta İçi (Pazartesi-Cuma)
```cron
*/30 * * * 1-5 /home/pi/shell-balance-checker/run_check.sh
```

## 📊 Cron Syntax Açıklaması

```
* * * * * komut
│ │ │ │ │
│ │ │ │ └─── Haftanın günü (0-7, 0 ve 7 = Pazar)
│ │ │ └───── Ay (1-12)
│ │ └─────── Ayın günü (1-31)
│ └───────── Saat (0-23)
└─────────── Dakika (0-59)
```

**Örnekler:**
- `*/30 * * * *` - Her 30 dakikada bir
- `0 */2 * * *` - Her 2 saatte bir
- `0 9 * * 1-5` - Hafta içi her gün saat 09:00
- `0 0 1 * *` - Her ayın 1'i gece yarısı

## 📝 Log Dosyaları

Cron job çıktıları `cron.log` dosyasına yazılır:

```bash
# Son logları görüntüle
tail -f ~/shell-balance-checker/cron.log

# Son 100 satırı görüntüle
tail -n 100 ~/shell-balance-checker/cron.log

# Belirli bir tarihteki logları görüntüle
grep "2025-11-14" ~/shell-balance-checker/cron.log
```

## 🔍 Sorun Giderme

### Cron Job Çalışmıyor

1. **Cron servisini kontrol edin:**
   ```bash
   sudo systemctl status cron
   sudo systemctl start cron  # Eğer çalışmıyorsa başlatın
   ```

2. **Cron loglarını kontrol edin:**
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. **Yolları kontrol edin:**
   - Crontab'daki tüm yollar mutlak (absolute) olmalı
   - `~` kullanmayın, `/home/pi/...` kullanın

4. **Manuel test:**
   ```bash
   # Wrapper script'i manuel çalıştırın
   /home/pi/shell-balance-checker/run_check.sh
   ```

5. **Çevre değişkenlerini kontrol edin:**
   ```bash
   # Crontab'a PATH ekleyin (gerekirse)
   PATH=/usr/local/bin:/usr/bin:/bin
   */30 * * * * /home/pi/shell-balance-checker/run_check.sh
   ```

### Log Dosyası Oluşturulmuyor

```bash
# Log dosyası için yazma izni kontrol edin
touch ~/shell-balance-checker/cron.log
chmod 666 ~/shell-balance-checker/cron.log
```

### Python Modülleri Bulunamıyor

Sanal ortamın doğru aktifleştirildiğinden emin olun. `run_check.sh` script'i bunu otomatik yapar.

### İzin Sorunları

```bash
# Script'in çalıştırılabilir olduğundan emin olun
chmod +x ~/shell-balance-checker/run_check.sh
chmod +x ~/shell-balance-checker/shell_auto_checker.py
```

## 🔄 Cron Job'u Güncelleme

```bash
# Crontab'ı düzenle
crontab -e

# Değişiklikleri kaydet ve çık
```

## 🗑️ Cron Job'u Kaldırma

```bash
# Crontab'ı düzenle
crontab -e

# İlgili satırı silin veya başına # ekleyin (yorum satırı yapar)
```

Veya tüm cron job'ları kaldırmak için:

```bash
crontab -r
```

**DİKKAT:** Bu komut tüm cron job'larınızı siler!

## 📊 Cron Job Performansı

### Log Dosyası Boyutu

Log dosyası büyüyebilir, düzenli temizleyin:

```cron
# Her gün gece yarısı log dosyasını temizle (son 1000 satırı tut)
0 0 * * * tail -n 1000 /home/pi/shell-balance-checker/cron.log > /home/pi/shell-balance-checker/cron.log.tmp && mv /home/pi/shell-balance-checker/cron.log.tmp /home/pi/shell-balance-checker/cron.log
```

### Disk Kullanımı

```bash
# Log dosyasının boyutunu kontrol edin
du -h ~/shell-balance-checker/cron.log

# Bakiye JSON dosyalarının boyutunu kontrol edin
du -h ~/shell-balance-checker/balance_*.json
```

## ✅ Kontrol Listesi

- [ ] `run_check.sh` script'i oluşturuldu ve çalıştırılabilir yapıldı
- [ ] Manuel test başarılı
- [ ] Crontab'a job eklendi
- [ ] Cron servisi çalışıyor
- [ ] Log dosyası oluşturuluyor
- [ ] İlk otomatik çalıştırma başarılı
- [ ] Bildirimler çalışıyor

## 🎉 Tamamlandı!

Cron job kuruldu! Script belirlediğiniz zamanlarda otomatik olarak çalışacak.

