# İslami İçerik Telegram Botu — Kurulum Rehberi

## 1. Gerekli Kütüphaneleri Kur

```bash
pip install aiogram anthropic apscheduler python-dotenv
```

## 2. Telegram Bot Token Al

1. Telegram'da @BotFather'a mesaj at
2. `/newbot` yaz
3. Bot adı ve kullanıcı adı gir
4. Sana verilen TOKEN'ı kopyala

## 3. Kanal Oluştur ve Botu Admin Yap

1. Telegram'da yeni bir kanal oluştur (örn: @islamikanal)
2. Kanal Ayarları → Yöneticiler → Botu ekle
3. "Mesaj gönder" yetkisi ver

## 4. .env Dosyası Oluştur

Aynı klasörde `.env` adında dosya oluştur:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHANNEL_ID=@islamikanal
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 5. Reklamı Düzenle

`bot.py` içinde REKLAM değişkenini bul ve kendi reklamını yaz:

```python
REKLAM = """
━━━━━━━━━━━━━━━━━━━━━━━
📢 *Sponsorlu*
[Reklam metninizi buraya yazın]
🔗 [Link](https://example.com)
━━━━━━━━━━━━━━━━━━━━━━━
"""
```

## 6. Botu Başlat

```bash
python bot.py
```

## 7. Test Et

Telegram'da botuna şu komutları gönder:
- `/start` — botu tanı
- `/test_gunluk` — günlük içerik önizle
- `/test_vaaz` — Cuma vaazı önizle
- `/test_gonder` — kanala gerçekten gönder

---

## Zamanlama

| Ne zaman | İçerik |
|----------|--------|
| Her gün 20:00 | Günlük olay + Ayet + Hadis + Dua + Reklam |
| Her Perşembe 20:00 | Yukarıdakiler + Cuma Vaazı + Reklam |

---

## Sunucuda Sürekli Çalıştırmak (Opsiyonel)

```bash
# nohup ile arka planda çalıştır
nohup python bot.py &

# VEYA systemd servisi olarak kur (Linux)
# VEYA Railway / Render ücretsiz hosting kullan
```

## Reklam Geliri İçin

Kanal büyüdükçe (1000+ üye):
1. Kanal bio'suna "@senin_telegram" ekle
2. Reklam almak isteyenler sana ulaşır
3. Mesaj başına 50-500₺ arası anlaşma yapabilirsin