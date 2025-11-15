#!/bin/bash
# Shell Kart Bakiye Kontrol - Hızlı Kurulum Scripti
# Raspberry Pi için otomatik kurulum

set -e  # Hata durumunda dur

echo "=========================================="
echo "Shell Kart Bakiye Kontrol - Kurulum"
echo "=========================================="
echo ""
echo "📁 Kurulum Dizini: ~/shell-balance-checker"
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hata fonksiyonu
error() {
    echo -e "${RED}❌ Hata: $1${NC}" >&2
    exit 1
}

# Başarı fonksiyonu
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Bilgi fonksiyonu
info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. Sistem güncellemesi
info "Sistem güncelleniyor..."
sudo apt update -qq || error "apt update başarısız"
sudo apt upgrade -y -qq || error "apt upgrade başarısız"
success "Sistem güncellendi"

# 2. Gerekli paketlerin kurulumu
info "Gerekli paketler kuruluyor..."
sudo apt install -y python3-pip python3-venv tesseract-ocr libtesseract-dev libjpeg-dev zlib1g-dev || error "Paket kurulumu başarısız"
success "Paketler kuruldu"

# 3. Tesseract kontrolü
if ! command -v tesseract &> /dev/null; then
    error "Tesseract kurulumu başarısız"
fi
success "Tesseract kurulu: $(tesseract --version | head -1)"

# 4. Proje dizini belirleme
# Kurulum dizini: ~/shell-balance-checker
INSTALL_DIR="$HOME/shell-balance-checker"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

info "Kurulum dizini: $INSTALL_DIR"
info "Script dizini: $SCRIPT_DIR"

# Kurulum dizini yoksa oluştur
if [ ! -d "$INSTALL_DIR" ]; then
    info "Kurulum dizini oluşturuluyor..."
    mkdir -p "$INSTALL_DIR" || error "Kurulum dizini oluşturulamadı"
    success "Kurulum dizini oluşturuldu: $INSTALL_DIR"
else
    info "Kurulum dizini zaten mevcut: $INSTALL_DIR"
fi

# Dosyaları kurulum dizinine kopyala (eğer farklı dizindeyse)
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    info "Dosyalar kurulum dizinine kopyalanıyor..."
    # Tüm dosyaları kopyala (hidden dosyalar dahil)
    cp -r "$SCRIPT_DIR"/. "$INSTALL_DIR"/ 2>/dev/null || {
        # Alternatif yöntem: Her dosyayı tek tek kopyala
        find "$SCRIPT_DIR" -maxdepth 1 -type f -exec cp {} "$INSTALL_DIR"/ \; 2>/dev/null
        find "$SCRIPT_DIR" -maxdepth 1 -type d ! -name "." -exec cp -r {} "$INSTALL_DIR"/ \; 2>/dev/null
    }
    success "Dosyalar kopyalandı"
fi

# Kurulum dizinine git
cd "$INSTALL_DIR" || error "Kurulum dizinine geçilemedi"

# .env.example dosyasının varlığını kontrol et
if [ ! -f ".env.example" ]; then
    info ".env.example dosyası bulunamadı, script dizininden kopyalanıyor..."
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env.example" || error ".env.example kopyalanamadı"
        success ".env.example kopyalandı"
    fi
fi

# 5. Sanal ortam oluşturma
if [ ! -d "venv" ]; then
    info "Python sanal ortamı oluşturuluyor..."
    python3 -m venv venv || error "Sanal ortam oluşturulamadı"
    success "Sanal ortam oluşturuldu"
else
    info "Sanal ortam zaten mevcut"
fi

# 6. Sanal ortamı aktifleştir
info "Sanal ortam aktifleştiriliyor..."
source venv/bin/activate || error "Sanal ortam aktifleştirilemedi"

# 7. Pip güncelleme
info "pip güncelleniyor..."
pip install --upgrade pip -q || error "pip güncellenemedi"

# 8. Python paketlerini kur
if [ -f "requirements.txt" ]; then
    info "Python paketleri kuruluyor..."
    pip install -r requirements.txt -q || error "Python paketleri kurulamadı"
    success "Python paketleri kuruldu"
else
    error "requirements.txt dosyası bulunamadı"
fi

# 9. .env dosyası kontrolü
if [ ! -f ".env" ]; then
    # Önce kurulum dizininde kontrol et
    if [ -f ".env.example" ]; then
        info ".env dosyası oluşturuluyor (.env.example'dan)..."
        cp .env.example .env
        success ".env dosyası oluşturuldu"
        info "Lütfen .env dosyasını düzenleyin: nano .env"
    # Kurulum dizininde yoksa script dizininden kopyala
    elif [ -f "$SCRIPT_DIR/.env.example" ]; then
        info ".env.example dosyası script dizininden kopyalanıyor..."
        cp "$SCRIPT_DIR/.env.example" ".env.example"
        cp .env.example .env
        success ".env dosyası oluşturuldu"
        info "Lütfen .env dosyasını düzenleyin: nano .env"
    else
        info ".env.example dosyası bulunamadı, boş .env dosyası oluşturuluyor..."
        touch .env
        success "Boş .env dosyası oluşturuldu"
        info "Lütfen .env dosyasını düzenleyin: nano .env"
    fi
else
    info ".env dosyası zaten mevcut"
fi

# 10. Script'leri çalıştırılabilir yap
info "Script'ler çalıştırılabilir yapılıyor..."
chmod +x shell_auto_checker.py 2>/dev/null || true
chmod +x run_check.sh 2>/dev/null || true
chmod +x get_chat_id.py 2>/dev/null || true
success "Script'ler hazır"

# 11. Test
info "Kurulum test ediliyor..."
if python3 -c "import requests, bs4, pytesseract, PIL, dotenv" 2>/dev/null; then
    success "Tüm paketler yüklü"
else
    error "Bazı paketler eksik"
fi

# 12. Özet
echo ""
echo "=========================================="
echo "✅ Kurulum Tamamlandı!"
echo "=========================================="
echo ""
echo "📝 Sonraki adımlar:"
echo ""
echo "1. .env dosyasını düzenleyin:"
echo "   cd $INSTALL_DIR"
echo "   nano .env"
echo ""
echo "2. En azından şunları ayarlayın:"
echo "   - CARD_NUMBER"
echo "   - TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID"
echo ""
echo "3. Script'i test edin:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python3 shell_auto_checker.py"
echo ""
echo "4. Cron job kurmak için:"
echo "   crontab -e"
echo "   */30 * * * * $INSTALL_DIR/run_check.sh"
echo ""
echo "📚 Detaylı dokümantasyon:"
echo "   - RASPBERRY_PI_SETUP.md"
echo "   - CRON_SETUP.md"
echo ""
echo "=========================================="

deactivate

