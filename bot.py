"""
İslami İçerik Telegram Botu
Zamanlama (Istanbul saati):
  08:00 — Sabah: Ayet + Hadis + Dua + Vaaz
  12:00 — Öğle:  Ayet + Hadis + Dua
  16:00 — İkindi: Ayet + Hadis + Dua
  Perşembe 20:00 — Sabah içeriği + Cuma Özel Vaazı

Kurulum:
  pip install aiogram anthropic apscheduler python-dotenv

.env dosyası oluştur:
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHANNEL_ID=@kanal_adiniz
  ANTHROPIC_API_KEY=...
"""

import asyncio
import logging
import random
import sys
from datetime import datetime
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import anthropic

# ─── Yapılandırma ──────────────────────────────────────────────────────────────

load_dotenv()

TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
ADMIN_ID            = int(os.getenv("ADMIN_ID", "0"))

# Gerekli değişkenleri doğrula
_eksik = [k for k, v in {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHANNEL_ID": TELEGRAM_CHANNEL_ID,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
}.items() if not v]

if _eksik:
    print(f"HATA: .env dosyasında eksik değişkenler: {', '.join(_eksik)}")
    sys.exit(1)

# ─── Reklam Metni ──────────────────────────────────────────────────────────────

REKLAM = """
━━━━━━━━━━━━━━━━━━━━━━━
📢 *Sponsorlu*
[Reklam metninizi buraya yazın]
🔗 [Link](https://example.com)
━━━━━━━━━━━━━━━━━━━━━━━
"""

# ─── Başlatma ──────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger(__name__)

bot       = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp        = Dispatcher()
ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── Claude API ────────────────────────────────────────────────────────────────

def claude_iste(prompt: str, max_tokens: int = 2000) -> str:
    prompt += "\n\nBakara 155. ayet ile Buhari Merda 1 hadisini KULLANMA."
    mesaj = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return mesaj.content[0].text

# ─── Tema Listeleri ────────────────────────────────────────────────────────────

SABAH_TEMALAR = [
    "tevbe ve af", "şükür", "sabır", "tevekkül", "ihlas",
    "merhamet", "adalet", "dürüstlük", "cömertlik", "tövbe",
    "namaz", "oruç", "zikir", "dua", "aile", "komşuluk",
    "ilim", "çalışmak", "yardımlaşma", "anne-baba hakkı"
]

OGLE_TEMALAR = [
    "şükür", "sabır", "tevbe ve af", "ihlas", "tevekkül",
    "adalet", "merhamet", "cömertlik", "dürüstlük", "tövbe",
    "oruç", "namaz", "dua", "zikir", "komşuluk", "aile",
    "anne-baba hakkı", "yardımlaşma", "ilim", "çalışmak"
]

IKINDI_TEMALAR = [
    "ihlas", "tevekkül", "tevbe ve af", "sabır", "şükür",
    "cömertlik", "dürüstlük", "adalet", "merhamet", "tövbe",
    "zikir", "dua", "namaz", "oruç", "yardımlaşma", "ilim",
    "çalışmak", "komşuluk", "anne-baba hakkı", "aile"
]

# ─── İçerik Üretici Fonksiyonlar ───────────────────────────────────────────────

def ayet_hadis_dua_uret(vakit: str, tema: str = None) -> str:
    """Öğle, İkindi için kısa içerik üretir."""
    if tema is None:
        tema = random.choice(SABAH_TEMALAR)
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun}, Vakit: {vakit}

Bu günün teması: {tema}. SADECE bu konuyla ilgili ayet ve hadis seç.

Aşağıdaki formatta kısa Türkçe İslami içerik oluştur.
Markdown kullan (Telegram uyumlu: *kalın*, _italik_).

📖 *AYET*
["{tema}" temasıyla ilgili bir ayetin Arapça orijinali]
[Türkçe meali — (Sure Adı, Ayet numarası)]

📚 *HADİS*
[Konuyla ilgili hadisin Arapça orijinali]
[Türkçe çevirisi — (kaynak)]

🤲 *{vakit.upper()} DUASI*
[Vakitle ilgili kısa dua — sadece Türkçe]

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=1100)


def sabah_icerigi_uret(tema: str = None) -> str:
    """Sabah için ayet + hadis + dua + vaaz üretir."""
    if tema is None:
        tema = random.choice(SABAH_TEMALAR)
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun}

Bu günün teması: {tema}. SADECE bu konuyla ilgili ayet ve hadis seç.

Aşağıdaki formatta Türkçe İslami sabah içeriği oluştur.
Markdown kullan (Telegram uyumlu: *kalın*, _italik_).

📖 *AYET*
["{tema}" temasıyla ilgili bir ayetin Arapça orijinali]
[Türkçe meali — (Sure Adı, Ayet numarası)]

📚 *HADİS*
[Konuyla ilgili hadisin Arapça orijinali]
[Türkçe çevirisi — (kaynak)]

🤲 *SABAH DUASI*
[Sabah duası — sadece Türkçe]

🕌 *GÜNÜN VAAZI*
["{tema}" temasında 150-200 kelimelik bir vaaz yaz. Şu tarzda olsun:
- Bir din hocasının cemaate sohbet anlatır gibi samimi ve akıcı
- Önce konuyu günlük hayattan somut bir örnekle aç
- Sonra ayet veya hadisle destekle
- Tarihi bir olay ya da peygamber kıssasıyla pekiştir
- Günümüzde nasıl uygulanır bağlantısını kur
- Kapanışta kısa bir dua veya öğütle bitir
- Dil sade Türkçe, ağır Osmanlıca kelime kullanma
- Kısa ve anlaşılır cümleler kur
- Okuyucuya "siz", "bizler", "kardeşlerim" diye hitap et]

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=1900)


def cuma_vaazi_uret() -> str:
    """Perşembe akşamı için derin Cuma vaazı üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun} (Perşembe — yarın Cuma)

Türkçe, 500-600 kelimelik bir Cuma vaazı yaz.
Markdown kullan (Telegram uyumlu).

Vaaz tarzı şöyle olsun:
- Bir din hocasının cemaate sohbet anlatır gibi samimi ve akıcı
- Önce konuyu günlük hayattan somut bir örnekle aç
- Sonra ayet ve hadisle destekle (Arapça orijinal + Türkçe meal/çeviri + kaynak)
- Tarihi bir olay ya da peygamber kıssasıyla pekiştir
- Günümüzde nasıl uygulanır bağlantısını kur
- Kapanışta dua ve öğütle bitir
- Dil sade Türkçe, ağır Osmanlıca kelime kullanma
- Kısa ve anlaşılır cümleler kur
- Okuyucuya "siz", "bizler", "kardeşlerim" diye hitap et

🕌 *CUMA VAAZI*
*[Vaazın başlığı — kısa ve dikkat çekici]*

[Önce günlük hayattan bir örnekle başla]

[Ayet: Arapça orijinal, ardından Türkçe meali — (Sure Adı, Ayet numarası)]

[Hadis: Arapça orijinal, ardından Türkçe çevirisi — (kaynak)]

[Tarihi olay veya peygamber kıssası]

[Günümüze bağlantı — nasıl uygularız]

*🌟 Bu Haftanın Ameli:*
[Bu hafta yapılabilecek küçük ama anlamlı bir öneri]

*🤲 Cuma Duası:*
[Sadece Türkçe dua]

Tema bu haftanın ruhuna uygun seç: tevbe, merhamet, kul hakkı, ihlas, tevekkül vb.

Sadece vaazı yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=2600)

# ─── Gönderim Fonksiyonları ────────────────────────────────────────────────────

async def sabah_gonder():
    """Her gün 08:00 — Ayet + Hadis + Dua + Vaaz"""
    log.info("Sabah içeriği gönderiliyor...")
    try:
        tema = random.choice(SABAH_TEMALAR)
        icerik = await asyncio.to_thread(sabah_icerigi_uret, tema)
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info(f"✅ Sabah içeriği gönderildi. (tema: {tema})")
    except Exception as e:
        log.error(f"❌ Sabah hatası: {e}")


async def ogle_gonder():
    """Her gün 12:00 — Ayet + Hadis + Dua"""
    log.info("Öğle içeriği gönderiliyor...")
    try:
        tema = random.choice(OGLE_TEMALAR)
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Öğle", tema)
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info(f"✅ Öğle içeriği gönderildi. (tema: {tema})")
    except Exception as e:
        log.error(f"❌ Öğle hatası: {e}")


async def ikindi_gonder():
    """Her gün 16:00 — Ayet + Hadis + Dua"""
    log.info("İkindi içeriği gönderiliyor...")
    try:
        tema = random.choice(IKINDI_TEMALAR)
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "İkindi", tema)
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info(f"✅ İkindi içeriği gönderildi. (tema: {tema})")
    except Exception as e:
        log.error(f"❌ İkindi hatası: {e}")


async def aksam_gonder():
    """Her gün 21:00 — Ayet + Hadis + Dua"""
    log.info("Akşam içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Akşam/Yatsı")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info("✅ Akşam içeriği gönderildi.")
    except Exception as e:
        log.error(f"❌ Akşam hatası: {e}")


async def persembe_gonder():
    """Her Perşembe 20:00 — Sabah içeriği + Cuma Vaazı"""
    log.info("Perşembe/Cuma içeriği gönderiliyor...")
    try:
        # 1. Sabah içeriği
        tema = random.choice(SABAH_TEMALAR)
        sabah = await asyncio.to_thread(sabah_icerigi_uret, tema)
        await bot.send_message(TELEGRAM_CHANNEL_ID, sabah)
        log.info(f"✅ Sabah içeriği gönderildi. (tema: {tema})")

        await asyncio.sleep(3)

        # 2. Cuma vaazı
        vaaz = await asyncio.to_thread(cuma_vaazi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, vaaz)
        log.info("✅ Cuma vaazı gönderildi.")

    except Exception as e:
        log.error(f"❌ Perşembe hatası: {e}")

# ─── Zamanlayıcı ───────────────────────────────────────────────────────────────

def zamanlayici_kur(scheduler: AsyncIOScheduler):
    tz = "Europe/Istanbul"

    # 08:00 — Sabah (Perşembe hariç her gün)
    scheduler.add_job(sabah_gonder, "cron",
        day_of_week="mon,tue,wed,fri,sat,sun", hour=8, minute=0, timezone=tz)

    # 12:00 — Öğle (her gün)
    scheduler.add_job(ogle_gonder, "cron",
        hour=12, minute=0, timezone=tz)

    # 16:00 — İkindi (her gün)
    scheduler.add_job(ikindi_gonder, "cron",
        hour=16, minute=0, timezone=tz)

    # Perşembe 20:00 — Sabah içeriği + Cuma vaazı
    scheduler.add_job(persembe_gonder, "cron",
        day_of_week="thu", hour=20, minute=0, timezone=tz)

    log.info("⏰ Zamanlayıcı kuruldu.")

# ─── Test Komutları ────────────────────────────────────────────────────────────

@dp.message()
async def komutlar(message: Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return
    if message.text == "/start":
        await message.answer(
            "🤖 *İslami İçerik Botu Aktif*\n\n"
            "📅 Günlük program:\n"
            "• 08:00 — Ayet + Hadis + Dua + Vaaz\n"
            "• 12:00 — Öğle Ayeti + Hadis + Dua\n"
            "• 16:00 — İkindi Ayeti + Hadis + Dua\n"
            "• Perşembe 20:00 — Sabah içeriği + Cuma Vaazı\n\n"
            "Test komutları:\n"
            "`/test_sabah` — sabah içeriği\n"
            "`/test_ogle` — öğle içeriği\n"
            "`/test_ikindi` — ikindi içeriği\n"
            "`/test_cuma` — Cuma vaazı\n"
            "`/test_gonder` — Perşembe içeriğini kanala gönder"
        )
    elif message.text == "/test_sabah":
        await message.answer("⏳ Üretiliyor...")
        icerik = await asyncio.to_thread(sabah_icerigi_uret)
        await message.answer(icerik)
    elif message.text == "/test_ogle":
        await message.answer("⏳ Üretiliyor...")
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Öğle")
        await message.answer(icerik)
    elif message.text == "/test_ikindi":
        await message.answer("⏳ Üretiliyor...")
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "İkindi")
        await message.answer(icerik)
    elif message.text == "/test_cuma":
        await message.answer("⏳ Cuma vaazı üretiliyor...")
        vaaz = await asyncio.to_thread(cuma_vaazi_uret)
        await message.answer(vaaz)
    elif message.text == "/test_gonder":
        await message.answer("📤 Kanala gönderiliyor...")
        await persembe_gonder()
        await message.answer("✅ Gönderildi!")

# ─── Ana Döngü ─────────────────────────────────────────────────────────────────

async def main():
    scheduler = AsyncIOScheduler()
    zamanlayici_kur(scheduler)
    scheduler.start()
    log.info("🚀 Bot başlatıldı — Ctrl+C ile durdur")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
