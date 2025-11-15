#!/bin/bash
# OCR Kütüphaneleri Kurulum Scripti
# Raspberry Pi için pytesseract ve Pillow kurulumu

set -e

echo "=========================================="
echo "OCR Kütüphaneleri Kurulumu"
echo "=========================================="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

error() {
    echo -e "${RED}❌ Hata: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Tesseract kontrolü
info "Tesseract OCR kontrol ediliyor..."
if ! command -v tesseract &> /dev/null; then
    info "Tesseract kuruluyor..."
    sudo apt update -qq
    sudo apt install -y tesseract-ocr || error "Tesseract kurulumu başarısız"
    success "Tesseract kuruldu: $(tesseract --version | head -1)"
else
    success "Tesseract zaten kurulu: $(tesseract --version | head -1)"
fi

# Python sanal ortamı kontrolü
INSTALL_DIR="$HOME/shell-balance-checker"

if [ ! -d "$INSTALL_DIR/venv" ]; then
    error "Sanal ortam bulunamadı. Önce install.sh script'ini çalıştırın."
fi

# Sanal ortamı aktifleştir
info "Sanal ortam aktifleştiriliyor..."
source "$INSTALL_DIR/venv/bin/activate" || error "Sanal ortam aktifleştirilemedi"

# Python paketlerini kur
info "OCR Python kütüphaneleri kuruluyor..."
pip install --upgrade pip -q
pip install pytesseract pillow -q || error "Python paketleri kurulamadı"
success "Python paketleri kuruldu"

# Test
info "Kurulum test ediliyor..."
python3 -c "import pytesseract; from PIL import Image; print('✅ OCR kütüphaneleri başarıyla yüklendi!')" || error "Test başarısız"

echo ""
echo "=========================================="
echo "✅ Kurulum Tamamlandı!"
echo "=========================================="
echo ""
echo "Artık script otomatik CAPTCHA çözme özelliğini kullanabilir."
echo ""
echo "Test için:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python3 shell_auto_checker.py"
echo ""

deactivate

