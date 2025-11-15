#!/bin/bash
# .env.example dosyasını kurulum dizinine kopyalama scripti

INSTALL_DIR="$HOME/shell-balance-checker"
SCRIPT_DIR="$(pwd)"

echo "Script dizini: $SCRIPT_DIR"
echo "Kurulum dizini: $INSTALL_DIR"

if [ -f "$SCRIPT_DIR/.env.example" ]; then
    echo "✅ .env.example bulundu: $SCRIPT_DIR/.env.example"
    
    if [ ! -d "$INSTALL_DIR" ]; then
        mkdir -p "$INSTALL_DIR"
        echo "✅ Kurulum dizini oluşturuldu"
    fi
    
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env.example"
    echo "✅ .env.example kopyalandı"
    
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        echo "✅ .env dosyası oluşturuldu"
    else
        echo "ℹ️  .env dosyası zaten mevcut"
    fi
else
    echo "❌ .env.example bulunamadı"
fi
