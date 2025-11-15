#!/bin/bash
# Shell Kart Bakiye Kontrol - Cron Job Wrapper Script
# Bu script cron job tarafından çağrılır

# Script'in bulunduğu dizini bul (dinamik)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Çalışma dizini = script'in bulunduğu dizin
WORK_DIR="$SCRIPT_DIR"

# Çalışma dizinine git
cd "$WORK_DIR" || {
    echo "HATA: Çalışma dizinine geçilemedi: $WORK_DIR" >&2
    exit 1
}

# Log dosyası (çalışma dizininde)
LOG_FILE="$WORK_DIR/cron.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log fonksiyonu (hem ekranda göster hem dosyaya yaz)
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Log başlangıcı
log "========================================"
log "[$TIMESTAMP] Bakiye kontrolü başlatılıyor..."
log "Çalışma dizini: $WORK_DIR"

# Sanal ortamı bul (birkaç yerde ara)
VENV_DIR=""

# 1. Önce çalışma dizininde ara
if [ -d "$WORK_DIR/venv" ] && [ -f "$WORK_DIR/venv/bin/activate" ]; then
    VENV_DIR="$WORK_DIR/venv"
    log "✅ venv bulundu: $VENV_DIR"
# 2. Kurulum dizininde ara (~/shell-balance-checker)
elif [ -d "$HOME/shell-balance-checker/venv" ] && [ -f "$HOME/shell-balance-checker/venv/bin/activate" ]; then
    VENV_DIR="$HOME/shell-balance-checker/venv"
    log "✅ venv bulundu: $VENV_DIR"
# 3. Python script'in bulunduğu dizinde ara ve otomatik oluştur
elif [ -f "$WORK_DIR/shell_auto_checker.py" ]; then
    # Script dizininde venv yoksa, otomatik oluştur
    log "⚠️  venv klasörü bulunamadı, otomatik oluşturuluyor..."
    
    # Venv oluştur
    if python3 -m venv "$WORK_DIR/venv" 2>&1 | tee -a "$LOG_FILE"; then
        VENV_DIR="$WORK_DIR/venv"
        log "✅ venv oluşturuldu: $VENV_DIR"
        
        # Aktifleştir
        source "$VENV_DIR/bin/activate" || {
            log "❌ HATA: Yeni oluşturulan venv aktifleştirilemedi"
            exit 1
        }
        
        # Pip'i güncelle
        log "📦 pip güncelleniyor..."
        pip install --upgrade pip -q 2>&1 | tee -a "$LOG_FILE" || true
        
        # Paketleri kur (requirements.txt varsa)
        if [ -f "$WORK_DIR/requirements.txt" ]; then
            log "📦 Python paketleri kuruluyor..."
            pip install -r "$WORK_DIR/requirements.txt" 2>&1 | tee -a "$LOG_FILE" || {
                log "⚠️  Paket kurulumunda bazı sorunlar olabilir, devam ediliyor..."
            }
            log "✅ Paketler kuruldu"
        else
            log "⚠️  requirements.txt bulunamadı, paketler kurulmadı"
        fi
        
        # Venv zaten aktifleştirildi, aşağıdaki aktifleştirme kısmını atla
        VENV_ALREADY_ACTIVATED=1
    else
        log "❌ HATA: venv oluşturulamadı!"
        log "   Manuel çözüm: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
else
    log "❌ HATA: venv klasörü bulunamadı ve shell_auto_checker.py da bulunamadı!"
    log "   Çalışma dizini: $WORK_DIR"
    exit 1
fi

# Sanal ortamı aktifleştir (eğer henüz aktifleştirilmediyse)
if [ -n "$VENV_DIR" ] && [ -z "${VENV_ALREADY_ACTIVATED:-}" ]; then
    source "$VENV_DIR/bin/activate" || {
        log "❌ HATA: Sanal ortam aktifleştirilemedi: $VENV_DIR"
        exit 1
    }
    log "✅ Sanal ortam aktifleştirildi"
fi

# Python script'ini çalıştır (5 defa deneme ile)
MAX_RETRIES=5
RETRY_COUNT=0
EXIT_CODE=1

set -o pipefail  # Pipe'daki hataları yakala

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -gt 1 ]; then
        log ""
        log "🔄 Yeniden deneme $RETRY_COUNT/$MAX_RETRIES..."
        log "========================================"
        # Kısa bir bekleme (yeni CAPTCHA için)
        sleep 2
    fi
    
    # Python script'ini çalıştır (hem ekranda göster hem log'a yaz)
    python3 shell_auto_checker.py 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=$?
    
    # Başarılı olursa döngüden çık
    if [ $EXIT_CODE -eq 0 ]; then
        break
    fi
    
    # Son deneme değilse devam et
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        log "⚠️  Deneme $RETRY_COUNT başarısız, yeniden deneniyor..."
    fi
done

set +o pipefail  # Pipefail'i kapat

# Sanal ortamı deaktif et (eğer aktifse)
if [ -n "$VENV_DIR" ] && [ -n "${VIRTUAL_ENV:-}" ]; then
    deactivate 2>/dev/null || true
fi

# Çıkış kodu kontrolü
if [ $EXIT_CODE -eq 0 ]; then
    if [ $RETRY_COUNT -gt 1 ]; then
        log "[$TIMESTAMP] ✅ Bakiye kontrolü başarıyla tamamlandı ($RETRY_COUNT deneme sonrası)"
    else
        log "[$TIMESTAMP] ✅ Bakiye kontrolü başarıyla tamamlandı"
    fi
else
    log "[$TIMESTAMP] ❌ Bakiye kontrolü $MAX_RETRIES deneme sonrası başarısız oldu"
fi

log "========================================"
log ""

exit $EXIT_CODE

