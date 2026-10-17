# Telegram Automation Bot — İslami İçerik

Telegram kanalına günlük otomatik İslami içerik (ayet, hadis, dua, vaaz) gönderen yapay zeka destekli bot.

## Özellikler

- **Günlük İçerik:** Sabah, öğle ve ikindi vakitlerinde ayet (Arapça + Türkçe meal), hadis (Arapça + Türkçe çeviri) ve vakitle ilgili dua gönderir
- **Sabah Vaazı:** Her sabah günün temasına uygun, din hocası sohbet tarzında vaaz üretir
- **Cuma Vaazı:** Perşembe akşamı özel detaylı Cuma vaazı gönderir
- **Haftalık Sure Rotasyonu:** Her güne sabit bir Kur'an suresi atanmıştır (Nisa, Maide, Enam, Araf, Enfal, Tevbe, Yunus)
- **Aylık Konu Rotasyonu:** Ayın her haftasında farklı bir ana tema işlenir (aile, ibadet, ahlak, ahiret)
- **Tema Çeşitliliği:** 20 farklı tema arasından rastgele seçim yapılır (sabır, şükür, tevbe, merhamet vb.)
- **Admin Komutları:** Telegram üzerinden test ve gönderim komutları

## Zamanlama (Istanbul Saati)

| Saat | İçerik |
|------|--------|
| 08:00 (Pzt-Çar, Cum-Paz) | Ayet + Hadis + Dua + Vaaz |
| 12:00 (Her gün) | Ayet + Hadis + Dua |
| 16:00 (Her gün) | Ayet + Hadis + Dua |
| 20:00 (Perşembe) | Sabah içeriği + Cuma Özel Vaazı |

## Kullanılan Teknolojiler

- **Python 3.11+**
- **aiogram 3** — Telegram Bot API framework
- **Anthropic Claude API** — Yapay zeka ile içerik üretimi
- **APScheduler** — Zamanlanmış görev yönetimi
- **python-dotenv** — Ortam değişkenleri yönetimi

## Kurulum

### 1. Repoyu klonla

```bash
git clone https://github.com/Hasankr-27/telegram-automation-bot.git
cd telegram-automation-bot
```

### 2. Bağımlılıkları kur

```bash
pip install -r requirements.txt
```

### 3. Ortam değişkenlerini ayarla

`.env.example` dosyasını kopyala ve değerleri doldur:

```bash
cp .env.example .env
```

```env
TELEGRAM_BOT_TOKEN=botfather_token
TELEGRAM_CHANNEL_ID=@kanal_adi
ANTHROPIC_API_KEY=anthropic_api_key
ADMIN_ID=telegram_kullanici_id
```

- **TELEGRAM_BOT_TOKEN:** [@BotFather](https://t.me/BotFather) üzerinden alınır
- **TELEGRAM_CHANNEL_ID:** Kanalın kullanıcı adı (örn: `@islamikanal`)
- **ANTHROPIC_API_KEY:** [Anthropic Console](https://console.anthropic.com/) üzerinden alınır
- **ADMIN_ID:** Bot komutlarını kullanacak Telegram kullanıcı ID'si

### 4. Botu başlat

```bash
python bot.py
```

### 5. Test et

Telegram'da bota şu komutları gönder:

| Komut | Açıklama |
|-------|----------|
| `/start` | Bot bilgisi |
| `/test_sabah` | Sabah içeriği önizleme |
| `/test_ogle` | Öğle içeriği önizleme |
| `/test_ikindi` | İkindi içeriği önizleme |
| `/test_cuma` | Cuma vaazı önizleme |
| `/test_gonder` | Kanala gerçek gönderim |

## Proje Yapısı

```
telegram-automation-bot/
├── bot.py              # Ana bot dosyası
├── requirements.txt    # Python bağımlılıkları
├── runtime.txt         # Python sürümü
├── .env.example        # Ortam değişkenleri şablonu
├── .gitignore
├── KURULUM.md          # Detaylı kurulum rehberi
└── README.md
```

## Deploy

Bot, [Railway](https://railway.app/) gibi platformlarda deploy edilebilir. `runtime.txt` dosyası Python sürümünü belirtir.

## Lisans

Bu proje eğitim amaçlıdır.
