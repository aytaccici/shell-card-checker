#!/usr/bin/env python3
"""
Telegram Chat ID Alıcı
Botunuza mesaj gönderdikten sonra Chat ID'nizi almak için bu script'i çalıştırın
"""

import requests
import json
import os
from dotenv import load_dotenv

# .env dosyasından token'ı oku
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("=" * 60)
    print("❌ HATA: TELEGRAM_BOT_TOKEN bulunamadı!")
    print("=" * 60)
    print("\n📝 .env dosyasına şunu ekleyin:")
    print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
    print("\nBot token'ınızı @BotFather'dan alabilirsiniz.")
    exit(1)

print("=" * 60)
print("🤖 Telegram Chat ID Alıcı")
print("=" * 60)
print(f"Token: {BOT_TOKEN[:20]}...")
print("\n📱 ÖNCE botunuza bir mesaj gönderin!")
print("   Telegram'da botunuza 'Merhaba' yazın")
print("\n⏳ Son mesajları kontrol ediliyor...\n")

try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('ok'):
            updates = data.get('result', [])
            
            if updates:
                # Tüm mesajları göster
                print("✅ Mesajlar bulundu:\n")
                chat_ids = set()
                
                for update in updates:
                    if 'message' in update:
                        msg = update['message']
                        chat = msg['chat']
                        chat_id = chat['id']
                        chat_ids.add(chat_id)
                        
                        first_name = chat.get('first_name', '')
                        username = chat.get('username', '')
                        text = msg.get('text', '')
                        
                        print(f"👤 Kullanıcı: {first_name} (@{username})")
                        print(f"💬 Mesaj: {text}")
                        print(f"🆔 Chat ID: {chat_id}")
                        print("-" * 60)
                
                if chat_ids:
                    chat_id = list(chat_ids)[-1]  # Son chat ID
                    print(f"\n✅ Chat ID'niz: {chat_id}")
                    print("\n📝 .env dosyasına ekleyin:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
                    print("\nVeya şu komutu çalıştırın:")
                    print(f"echo 'TELEGRAM_CHAT_ID={chat_id}' >> .env")
            else:
                print("⚠️  Henüz mesaj bulunamadı.")
                print("\n📱 Yapmanız gerekenler:")
                print("1. Telegram'ı açın")
                print("2. botunuza'u bulun")
                print("3. Bot'a 'Merhaba' yazın")
                print("4. Bu script'i tekrar çalıştırın")
        else:
            print(f"❌ API hatası: {data}")
    else:
        print(f"❌ HTTP hatası: {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Bağlantı hatası: {e}")
    print("\nİnternet bağlantınızı kontrol edin.")
except Exception as e:
    print(f"❌ Hata: {e}")

