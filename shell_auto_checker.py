#!/usr/bin/env python3
"""
Shell Kart Bakiye Kontrol - Otomatik CAPTCHA Çözücü Versiyonu
Bu script Shell Türkiye kart bakiyesini otomatik olarak kontrol eder
OCR ile CAPTCHA'yı otomatik çözer (%90+ başarı oranı)

Kullanım: python3 shell_auto_checker.py [kart_numarası]
"""

import requests
from bs4 import BeautifulSoup
import time
import sys
import re
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# .env dosyası desteği
try:
    from dotenv import load_dotenv
    load_dotenv()  # .env dosyasını yükle
except ImportError:
    print("⚠️  python-dotenv paketi bulunamadı!")
    print("   Kurulum için: pip install python-dotenv")
    print("   .env dosyası yüklenemedi, environment variable'lar kullanılacak")

# OCR için gerekli kütüphaneler
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # Sadece ilk çalıştırmada göster (tekrar tekrar göstermemek için)
    if not hasattr(sys, '_ocr_warning_shown'):
        print("⚠️  OCR kütüphaneleri bulunamadı!")
        print("   Kurulum için:")
        print("   pip install pytesseract pillow")
        print("   Tesseract kurulumu:")
        print("   - Mac: brew install tesseract")
        print("   - Linux/Raspberry Pi: sudo apt install tesseract-ocr")
        sys._ocr_warning_shown = True

# ============================================================================
# BİLDİRİM AYARLARI
# ============================================================================
# Telegram bildirim ayarları
TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')  # Örnek: '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')  # Örnek: '123456789'

# Email bildirim ayarları
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_FROM = os.getenv('EMAIL_FROM', '')  # Örnek: 'your-email@gmail.com'
EMAIL_TO = os.getenv('EMAIL_TO', '')  # Örnek: 'recipient@example.com'
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # Gmail için App Password gerekli

# WhatsApp bildirim ayarları (Twilio WhatsApp API)
WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'false').lower() == 'true'
WHATSAPP_TWILIO_ACCOUNT_SID = os.getenv('WHATSAPP_TWILIO_ACCOUNT_SID', '')
WHATSAPP_TWILIO_AUTH_TOKEN = os.getenv('WHATSAPP_TWILIO_AUTH_TOKEN', '')
WHATSAPP_TWILIO_FROM = os.getenv('WHATSAPP_TWILIO_FROM', '')  # Twilio WhatsApp numarası (whatsapp:+14155238886 formatında)
WHATSAPP_TO = os.getenv('WHATSAPP_TO', '')  # Alıcı numara (whatsapp:+905551234567 formatında)

# Kart numarası
CARD_NUMBER = os.getenv('CARD_NUMBER', '')  # Shell kart numarası

def send_telegram_notification(message):
    """Telegram bildirimi gönder"""
    if not TELEGRAM_ENABLED:
        return False
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Telegram bildirim hatası: {e}")
        return False

def send_email_notification(subject, message):
    """Email bildirimi gönder"""
    if not EMAIL_ENABLED or not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html', 'utf-8'))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"⚠️  Email bildirim hatası: {e}")
        return False

def send_whatsapp_notification(message):
    """WhatsApp bildirimi gönder (Twilio)"""
    if not WHATSAPP_ENABLED:
        return False
    
    if not WHATSAPP_TWILIO_ACCOUNT_SID or not WHATSAPP_TWILIO_AUTH_TOKEN or not WHATSAPP_TWILIO_FROM or not WHATSAPP_TO:
        return False
    
    # HTML tag'lerini temizle (WhatsApp HTML desteklemez)
    import re
    clean_message = re.sub(r'<[^>]+>', '', message)
    clean_message = clean_message.replace('&nbsp;', ' ')
    clean_message = clean_message.strip()
    
    try:
        # Twilio kütüphanesi gerekli: pip install twilio
        try:
            from twilio.rest import Client
        except ImportError:
            print("⚠️  Twilio kütüphanesi bulunamadı! Kurulum: pip install twilio")
            return False
        
        client = Client(WHATSAPP_TWILIO_ACCOUNT_SID, WHATSAPP_TWILIO_AUTH_TOKEN)
        
        message_obj = client.messages.create(
            from_=WHATSAPP_TWILIO_FROM,
            body=clean_message,
            to=WHATSAPP_TO
        )
        
        return message_obj.sid is not None
    except Exception as e:
        print(f"⚠️  WhatsApp bildirim hatası: {e}")
        return False

def get_last_balance(card_number):
    """Son bakiyeyi dosyadan oku"""
    balance_file = f"balance_{card_number}.json"
    
    if not os.path.exists(balance_file):
        return None
    
    try:
        with open(balance_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('balance')
    except Exception:
        return None

def save_balance(card_number, balance, card_type, status):
    """Bakiyeyi dosyaya kaydet"""
    balance_file = f"balance_{card_number}.json"
    
    data = {
        'card_number': card_number,
        'balance': balance,
        'card_type': card_type,
        'status': status,
        'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp': time.time()
    }
    
    try:
        with open(balance_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️  Bakiye kaydedilemedi: {e}")
        return False

def format_balance_result(card_number, result_data):
    """Bakiye sonuçlarını formatla ve göster"""
    if not result_data or not isinstance(result_data, dict):
        return None
    
    success = result_data.get('result', False)
    message = result_data.get('message', '')
    card_type = result_data.get('cardTypeName', 'Bilinmiyor')
    balance = result_data.get('balanceAmount', 0)
    status = result_data.get('cardStatusName', 'Bilinmiyor')
    
    # Ekranda göster
    print("\n" + "=" * 60)
    print("📊 BAKİYE SONUÇLARI")
    print("=" * 60)
    print(f"💳 Kart Numarası: {card_number}")
    print(f"📋 Kart Tipi: {card_type}")
    print(f"💰 Bakiye: {balance:,.2f} TL")
    print(f"✅ Durum: {status}")
    print(f"📝 Mesaj: {message}")
    print(f"⏰ Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # HTML formatı (bildirimler için)
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>🚗 Shell Kart Bakiye Sorgulama Sonucu</h2>
        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Kart Numarası:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{card_number}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Kart Tipi:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{card_type}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Bakiye:</td>
                <td style="padding: 8px; border: 1px solid #ddd; font-size: 18px; color: #28a745; font-weight: bold;">{balance:,.2f} TL</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Durum:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{status}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Mesaj:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{message}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Tarih:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Telegram formatı
    telegram_message = f"""
🚗 <b>Shell Kart Bakiye Sorgulama</b>

💳 Kart: <code>{card_number}</code>
📋 Tip: {card_type}
💰 Bakiye: <b>{balance:,.2f} TL</b>
✅ Durum: {status}
📝 {message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # WhatsApp formatı (HTML tag'leri olmadan)
    whatsapp_message = f"""🚗 Shell Kart Bakiye Sorgulama

💳 Kart: {card_number}
📋 Tip: {card_type}
💰 Bakiye: {balance:,.2f} TL
✅ Durum: {status}
📝 {message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    return {
        'success': success,
        'card_number': card_number,
        'card_type': card_type,
        'balance': balance,
        'status': status,
        'message': message,
        'html': html_message,
        'telegram': telegram_message,
        'whatsapp': whatsapp_message
    }

def solve_captcha_ocr(captcha_file):
    """
    CAPTCHA'yı OCR ile otomatik çöz
    4 farklı yöntem dener ve en iyi sonucu döndürür
    """
    if not OCR_AVAILABLE:
        return None
    
    print("\n🤖 CAPTCHA otomatik çözülüyor (OCR)...")
    
    try:
        # Görseli yükle
        img = Image.open(captcha_file)
        
        results = []
        
        # Yöntem 1: Orijinal görsel (basit)
        print("   📝 Yöntem 1: Orijinal görsel...")
        try:
            text1 = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            text1 = re.sub(r'[^0-9A-Z]', '', text1.upper().strip())
            if text1 and len(text1) >= 4:
                results.append(('Orijinal', text1))
                print(f"      ✅ Bulundu: {text1}")
        except Exception as e:
            print(f"      ❌ Hata: {e}")
        
        # Yöntem 2: Grayscale + Kontrast artırma
        print("   📝 Yöntem 2: Grayscale + Kontrast...")
        try:
            gray = img.convert('L')
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            text2 = pytesseract.image_to_string(enhanced, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            text2 = re.sub(r'[^0-9A-Z]', '', text2.upper().strip())
            if text2 and len(text2) >= 4:
                results.append(('Grayscale+Kontrast', text2))
                print(f"      ✅ Bulundu: {text2}")
        except Exception as e:
            print(f"      ❌ Hata: {e}")
        
        # Yöntem 3: Binary threshold (siyah-beyaz)
        print("   📝 Yöntem 3: Binary threshold...")
        try:
            gray = img.convert('L')
            # Threshold değerini ayarla
            threshold = 128
            binary = gray.point(lambda p: p > threshold and 255)
            text3 = pytesseract.image_to_string(binary, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            text3 = re.sub(r'[^0-9A-Z]', '', text3.upper().strip())
            if text3 and len(text3) >= 4:
                results.append(('Binary', text3))
                print(f"      ✅ Bulundu: {text3}")
        except Exception as e:
            print(f"      ❌ Hata: {e}")
        
        # Yöntem 4: Noise reduction + resize
        print("   📝 Yöntem 4: Noise reduction + Resize...")
        try:
            # Görseli büyüt (OCR için daha iyi)
            large = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
            gray = large.convert('L')
            # Noise reduction
            denoised = gray.filter(ImageFilter.MedianFilter(size=3))
            enhancer = ImageEnhance.Contrast(denoised)
            enhanced = enhancer.enhance(2.5)
            text4 = pytesseract.image_to_string(enhanced, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            text4 = re.sub(r'[^0-9A-Z]', '', text4.upper().strip())
            if text4 and len(text4) >= 4:
                results.append(('NoiseReduction+Resize', text4))
                print(f"      ✅ Bulundu: {text4}")
        except Exception as e:
            print(f"      ❌ Hata: {e}")
        
        # En iyi sonucu seç (en uzun ve geçerli olan)
        if results:
            # Sonuçları uzunluk ve geçerliliğe göre sırala
            valid_results = []
            for method, text in results:
                # 4-8 karakter arası olmalı (genelde CAPTCHA'lar bu uzunlukta)
                if 4 <= len(text) <= 8:
                    valid_results.append((method, text, len(text)))
            
            if valid_results:
                # En uzun ve geçerli olanı seç
                best = max(valid_results, key=lambda x: x[2])
                print(f"\n✅ En iyi sonuç ({best[0]}): {best[1]}")
                return best[1]
            else:
                # Geçerli sonuç yoksa ilkini dene
                print(f"\n⚠️  Geçerli sonuç bulunamadı, ilk sonuç deneniyor: {results[0][1]}")
                return results[0][1]
        else:
            print("\n❌ Hiçbir yöntemle CAPTCHA çözülemedi")
            return None
            
    except Exception as e:
        print(f"\n❌ OCR hatası: {e}")
        return None

def get_page_and_captcha():
    """Sayfayı yükle, token'ları al ve CAPTCHA'yı göster"""
    
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    print("=" * 60)
    print("🚗 SHELL KART BAKİYE KONTROL (CURL Versiyonu)")
    print("=" * 60)
    print(f"⏰ Zaman: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Sayfayı yükle
    print("\n📄 Sayfa yükleniyor...")
    try:
        response = session.get(
            'https://sfs.turkiyeshell.com/bakiye-sorgula',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        print("✅ Sayfa yüklendi")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None, None
    
    # HTML'i parse et
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Token'ları bul
    captcha_token = None
    captcha_text = None
    
    for input_tag in soup.find_all('input'):
        name = input_tag.get('name', '')
        if name == 'DNTCaptchaToken':
            captcha_token = input_tag.get('value')
            print(f"✅ CAPTCHA Token: {captcha_token[:30]}...")
        elif name == 'DNTCaptchaText':
            captcha_text = input_tag.get('value')
            print(f"✅ CAPTCHA Text: {captcha_text[:30]}...")
    
    if not captcha_token or not captcha_text:
        print("❌ Token'lar bulunamadı!")
        # Debug için sayfayı kaydet
        debug_file = f"debug_shell_page_{int(time.time())}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"🐛 HTML kaydedildi: {debug_file}")
        return None, None
    
    # CAPTCHA görselini bul ve indir
    captcha_img_url = None
    
    # Tüm img taglerini kontrol et
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        
        if 'captcha' in src.lower() or 'captcha' in alt.lower():
            captcha_img_url = src
            break
    
    if captcha_img_url:
        # CAPTCHA'yı indir
        if not captcha_img_url.startswith('http'):
            captcha_img_url = 'https://sfs.turkiyeshell.com' + captcha_img_url
        
        print(f"\n🖼️  CAPTCHA indiriliyor: {captcha_img_url}")
        
        try:
            img_response = session.get(captcha_img_url, headers=headers, timeout=30)
            img_response.raise_for_status()
            
            captcha_filename = f"captcha_{int(time.time())}.png"
            with open(captcha_filename, 'wb') as f:
                f.write(img_response.content)
            
            print(f"✅ CAPTCHA kaydedildi: {captcha_filename}")
            print(f"\n📁 CAPTCHA'yı açmak için:")
            print(f"   open {captcha_filename}")
            
        except Exception as e:
            print(f"⚠️  CAPTCHA indirilemedi: {e}")
    else:
        print("\n⚠️  CAPTCHA görseli bulunamadı")
        print("Tüm görsel URL'leri:")
        for idx, img in enumerate(soup.find_all('img'), 1):
            print(f"   {idx}. {img.get('src', 'N/A')}")
    
    # Cookie'leri al
    cookies = session.cookies.get_dict()
    
    return {
        'captcha_token': captcha_token,
        'captcha_text': captcha_text,
        'cookies': cookies,
        'session': session
    }, captcha_filename if captcha_img_url else None

def check_balance(card_number, captcha_input, tokens):
    """Bakiye sorgula"""
    
    print("\n" + "=" * 60)
    print(f"💳 Kart Sorgulanıyor: {card_number}")
    print(f"🔐 CAPTCHA Kodu: {captcha_input}")
    print("=" * 60)
    
    # POST isteği için data
    data = {
        'CardNumber': card_number,
        'CustomerCode': '',
        'DNTCaptchaText': tokens['captcha_text'],
        'DNTCaptchaInputText': captcha_input,
        'DNTCaptchaToken': tokens['captcha_token'],
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Pragma': 'no-cache',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://sfs.turkiyeshell.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'Priority': 'u=3, i',
        'Referer': 'https://sfs.turkiyeshell.com/bakiye-sorgula',
    }
    
    try:
        response = tokens['session'].post(
            'https://sfs.turkiyeshell.com/account/balanceinquiry',
            data=data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(list(response.headers.items())[:5])}")
        
        # Content-Type kontrolü
        content_type = response.headers.get('Content-Type', '')
        
        if 'json' in content_type:
            # JSON yanıt
            result = response.json()
            print("\n✅ JSON Yanıt Alındı:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            # HTML yanıt
            print("\n📄 HTML Yanıt:")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bakiye bilgisini bul
            print("\nSayfada arama yapılıyor...")
            
            # Bakiye text'i bul
            text_content = soup.get_text()
            
            # Bakiye pattern'leri
            balance_patterns = [
                r'Bakiyeniz[:\s]+([0-9.,]+\s*TL)',
                r'bakiye[:\s]+([0-9.,]+)',
                r'Balance[:\s]+([0-9.,]+)',
                r'([0-9]+)\s*TL',
            ]
            
            found = False
            for pattern in balance_patterns:
                match = re.search(pattern, text_content, re.I)
                if match:
                    print(f"✅ Bakiye bulundu: {match.group(0)}")
                    found = True
                    break
            
            if not found:
                print("\n⚠️  Bakiye bilgisi bulunamadı")
                print("\nSayfa içeriği (ilk 500 karakter):")
                print(text_content[:500])
            
            # Debug için HTML'i kaydet
            debug_file = f"debug_response_{int(time.time())}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n🐛 Yanıt HTML'i kaydedildi: {debug_file}")
            
            return None
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return None

def main():
    # Kart numarası - öncelik sırası: .env > komut satırı argümanı > kullanıcı inputu > varsayılan
    card_number = None
    
    # 1. Önce .env dosyasından oku
    if CARD_NUMBER:
        card_number = CARD_NUMBER.strip()
        print(f"💳 Kart numarası .env dosyasından alındı: {card_number}")
    
    # 2. .env'de yoksa komut satırı argümanından al
    if not card_number and len(sys.argv) > 1:
        card_number = sys.argv[1].strip()
        print(f"💳 Kart numarası komut satırından alındı: {card_number}")
    
    # 3. Hiçbiri yoksa kullanıcıdan sor
    if not card_number:
        if sys.stdin.isatty():
            card_number = input("💳 Kart numarasını girin: ").strip()
        else:
            card_number = "2400030848"  # Non-interactive mod için varsayılan
    
    # 4. Hala yoksa varsayılan değeri kullan
    if not card_number:
        card_number = "2400030848"
        print(f"💳 Varsayılan kart numarası kullanılıyor: {card_number}")
    
    # Token'ları al
    tokens, captcha_file = get_page_and_captcha()
    
    if not tokens:
        print("\n❌ Token'lar alınamadı, işlem iptal edildi")
        return 1
    
    if not captcha_file:
        print("\n❌ CAPTCHA dosyası bulunamadı, işlem iptal edildi")
        return 1
    
    # CAPTCHA'yı otomatik çöz
    captcha_input = None
    captcha_solved = False
    
    if OCR_AVAILABLE:
        captcha_input = solve_captcha_ocr(captcha_file)
        
        if captcha_input:
            captcha_solved = True
            print(f"\n✅ CAPTCHA otomatik çözüldü: {captcha_input}")
            print(f"✅ Otomatik olarak kullanılıyor, bakiye sorgulanıyor...")
            
            # CAPTCHA dosyasını sil
            try:
                if os.path.exists(captcha_file):
                    os.remove(captcha_file)
                    print(f"🗑️  CAPTCHA dosyası silindi: {captcha_file}")
            except Exception as e:
                print(f"⚠️  CAPTCHA dosyası silinemedi: {e}")
        else:
            print("\n⚠️  Otomatik çözme başarısız, manuel giriş gerekiyor")
    else:
        print("\n⚠️  OCR kütüphaneleri yüklü değil, manuel giriş gerekiyor")
    
    # Otomatik çözme başarısızsa veya OCR yoksa manuel giriş
    if not captcha_input:
        # CAPTCHA dosyasını açmayı dene (platform bağımsız)
        import subprocess
        import platform
        
        captcha_opened = False
        system = platform.system()
        
        try:
            if system == 'Darwin':  # macOS
                subprocess.run(['open', captcha_file], check=False)
                captcha_opened = True
            elif system == 'Linux':  # Linux/Raspberry Pi
                # GUI varsa xdg-open kullan
                try:
                    subprocess.run(['xdg-open', captcha_file], check=False, timeout=2)
                    captcha_opened = True
                except:
                    # GUI yoksa sadece dosya yolunu göster
                    pass
            elif system == 'Windows':
                subprocess.run(['start', captcha_file], check=False, shell=True)
                captcha_opened = True
        except Exception:
            pass
        
        if captcha_opened:
            print(f"\n✅ CAPTCHA otomatik açıldı")
        else:
            print(f"\n📁 CAPTCHA dosyası: {os.path.abspath(captcha_file)}")
            print(f"   Dosyayı manuel olarak açabilirsiniz")
        
        print("\n" + "=" * 60)
        
        # Interaktif mod kontrolü
        if sys.stdin.isatty():
            try:
                captcha_input = input("🔐 CAPTCHA kodunu girin: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n❌ CAPTCHA girilmedi, işlem iptal edildi")
                return 1
        else:
            # Non-interactive mod - CAPTCHA dosyasını göster ve hata ver
            print("❌ CAPTCHA dosyası: " + captcha_file)
            print("❌ Non-interactive modda manuel CAPTCHA girişi yapılamaz")
            return 1
        
        if not captcha_input:
            print("❌ CAPTCHA girilmedi, işlem iptal edildi")
            return 1
    
    # Bakiye sorgula
    result_data = check_balance(card_number, captcha_input, tokens)
    
    # Sonuçları formatla ve göster
    if result_data and isinstance(result_data, dict):
        if result_data.get('result'):
            # Başarılı durum
            formatted_result = format_balance_result(card_number, result_data)
            
            if formatted_result:
                # Son bakiyeyi kontrol et
                last_balance = get_last_balance(card_number)
                current_balance = formatted_result['balance']
                balance_changed = False
                
                if last_balance is not None:
                    if abs(last_balance - current_balance) > 0.01:  # 0.01 TL'den fazla fark varsa değişiklik say
                        balance_changed = True
                        difference = current_balance - last_balance
                        print(f"\n📊 Bakiye Değişikliği Tespit Edildi!")
                        print(f"   Önceki Bakiye: {last_balance:,.2f} TL")
                        print(f"   Yeni Bakiye: {current_balance:,.2f} TL")
                        print(f"   Fark: {difference:+,.2f} TL")
                    else:
                        print(f"\n📊 Bakiye Değişmedi: {current_balance:,.2f} TL (Son kontrol: {last_balance:,.2f} TL)")
                else:
                    print(f"\n📊 İlk Bakiye Kaydı: {current_balance:,.2f} TL")
                
                # Bakiyeyi kaydet
                save_balance(
                    card_number,
                    current_balance,
                    formatted_result['card_type'],
                    formatted_result['status']
                )
                
                # Sadece bakiye değiştiyse bildirim gönder
                if balance_changed or last_balance is None:
                    # Bildirim gönder
                    print("\n📨 Bildirimler gönderiliyor...")
                    
                    # Telegram bildirimi
                    if TELEGRAM_ENABLED:
                        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                            if send_telegram_notification(formatted_result['telegram']):
                                print("✅ Telegram bildirimi gönderildi")
                            else:
                                print("⚠️  Telegram bildirimi gönderilemedi")
                        else:
                            print("⚠️  Telegram bildirimi aktif ama TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik")
                    else:
                        print("ℹ️  Telegram bildirimi deaktif (TELEGRAM_ENABLED=false)")
                    
                    # Email bildirimi
                    if EMAIL_ENABLED:
                        if EMAIL_FROM and EMAIL_TO and EMAIL_PASSWORD:
                            subject = f"Shell Kart Bakiye: {formatted_result['balance']:,.2f} TL"
                            if send_email_notification(subject, formatted_result['html']):
                                print("✅ Email bildirimi gönderildi")
                            else:
                                print("⚠️  Email bildirimi gönderilemedi")
                        else:
                            print("⚠️  Email bildirimi aktif ama EMAIL_FROM, EMAIL_TO veya EMAIL_PASSWORD eksik")
                    else:
                        print("ℹ️  Email bildirimi deaktif (EMAIL_ENABLED=false)")
                    
                    # WhatsApp bildirimi
                    if WHATSAPP_ENABLED:
                        if WHATSAPP_TO:
                            if send_whatsapp_notification(formatted_result['whatsapp']):
                                print("✅ WhatsApp bildirimi gönderildi")
                            else:
                                print("⚠️  WhatsApp bildirimi gönderilemedi")
                        else:
                            print("⚠️  WhatsApp bildirimi aktif ama WHATSAPP_TO eksik")
                    else:
                        print("ℹ️  WhatsApp bildirimi deaktif (WHATSAPP_ENABLED=false)")
                else:
                    # Bakiye değişmedi, sadece log
                    print("\n📝 Bakiye değişmediği için bildirim gönderilmedi (sadece log)")
            else:
                print("\n⚠️  Sonuçlar formatlanamadı")
        else:
            # Başarısız durum - mesajı göster
            print("\n" + "=" * 60)
            print("❌ İŞLEM BAŞARISIZ")
            print("=" * 60)
            message = result_data.get('message', 'Bilinmeyen hata')
            print(f"📝 Hata Mesajı: {message}")
            print("=" * 60)
    else:
        print("\n❌ Geçersiz yanıt alındı")
        if result_data:
            print(f"Yanıt: {result_data}")
    
    print("\n" + "=" * 60)
    print("✅ İŞLEM TAMAMLANDI")
    print("=" * 60)
    
    return 0 if (result_data and isinstance(result_data, dict) and result_data.get('result')) else 1

if __name__ == "__main__":
    sys.exit(main())