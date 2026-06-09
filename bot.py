"""
İslami İçerik Telegram Botu
Zamanlama (Istanbul saati):
  08:00 — Sabah: Olay + Ayet + Hadis + Dua + Vaaz + Reklam
  12:00 — Öğle:  Ayet + Hadis + Dua + Reklam
  15:00 — İkindi: Ayet + Hadis + Dua + Reklam
  21:00 — Akşam/Yatsı: Ayet + Hadis + Dua + Reklam
  Perşembe 20:00 — Sabah içeriği + Cuma Özel Vaazı + Reklam

Kurulum:
  pip install aiogram anthropic apscheduler python-dotenv

.env dosyası oluştur:
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHANNEL_ID=@kanal_adiniz
  ANTHROPIC_API_KEY=...
"""

import asyncio
import logging
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
    mesaj = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return mesaj.content[0].text

# ─── İçerik Üretici Fonksiyonlar ───────────────────────────────────────────────

def ayet_hadis_dua_uret(vakit: str) -> str:
    """Öğle, İkindi, Akşam/Yatsı için kısa içerik üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun}, Vakit: {vakit}

Her gün farklı ayet ve hadis seç, bir önceki günle aynı olmasın.

Aşağıdaki formatta kısa Türkçe İslami içerik oluştur.
Markdown kullan (Telegram uyumlu: *kalın*, _italik_).

📖 *{vakit.upper()} AYETİ*
[Vakitle uyumlu ayetin Arapça orijinali]
[Türkçe meali — (Sure Adı, Ayet numarası)]

📚 *HADİS*
[Hadisin Arapça orijinali]
[Türkçe çevirisi — (kaynak)]

🤲 *DUA*
[Vakitle ilgili kısa dua — sadece Türkçe]

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=1000)


def sabah_icerigi_uret() -> str:
    """Sabah için olay + ayet + hadis + dua + vaaz üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun}

Her gün farklı ayet ve hadis seç, bir önceki günle aynı olmasın.

Aşağıdaki formatta Türkçe İslami sabah içeriği oluştur.
Markdown kullan (Telegram uyumlu: *kalın*, _italik_).

📅 *GÜNÜN OLAYI*
[Bu tarihe yakın İslam tarihinden kısa, ilginç bir olay — 2-3 cümle]

📖 *SABAH AYETİ*
[Olayla bağlantılı ayetin Arapça orijinali]
[Türkçe meali — (Sure Adı, Ayet numarası)]

📚 *HADİS*
[Hadisin Arapça orijinali]
[Türkçe çevirisi — (kaynak)]

🤲 *SABAH DUASI*
[Sabah duası — sadece Türkçe]

🕌 *GÜNÜN VAAZI*
[150-200 kelime, sade ve samimi. Günün olayı veya ayetiyle bağlantılı.
Günlük hayata dokunan, herkesin anlayabileceği bir dil.]

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=2000)


def cuma_vaazi_uret() -> str:
    """Perşembe akşamı için derin Cuma vaazı üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    prompt = f"""
Bugünün tarihi: {bugun} (Perşembe — yarın Cuma)

Türkçe, 500-600 kelimelik derin ve etkileyici bir Cuma vaazı yaz.
Markdown kullan (Telegram uyumlu).

🕌 *CUMA VAAZI*
*[Vaazın başlığı — dikkat çekici, düşündürücü]*

_"[Konuyla ilgili güçlü bir ayet meali]"_
_(Sure adı, Ayet numarası)_

*📖 Ayetin Tefsiri:*
[Derinlemesine açıklama — 3-4 cümle, alimlerden görüşler]

*📚 Peygamberimizden:*
[2 hadis — kaynaklarıyla, konuyla doğrudan ilgili]

*💭 Bugüne Yansıması:*
[Modern hayattan somut örnekler — 3 paragraf, samimi dil]

*🌟 Bu Haftanın Ameli:*
[Bu hafta yapılabilecek küçük ama anlamlı bir ibadet/davranış önerisi]

*🤲 Cuma Duası:*
[Arapça dua + Türkçe anlamı]

Tema: sabır, şükür, ihlas, tevbe, adalet, merhamet, birlik, tevekkül vb.
Hutbe tadında ama sohbet sıcaklığında olsun.
Sadece vaazı yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=2500)

# ─── Gönderim Fonksiyonları ────────────────────────────────────────────────────

async def sabah_gonder():
    """Her gün 08:00 — Olay + Ayet + Hadis + Dua + Vaaz"""
    log.info("Sabah içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(sabah_icerigi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        await asyncio.sleep(2)
        await bot.send_message(TELEGRAM_CHANNEL_ID, REKLAM)
        log.info("✅ Sabah içeriği ve reklam gönderildi.")
    except Exception as e:
        log.error(f"❌ Sabah hatası: {e}")


async def ogle_gonder():
    """Her gün 12:00 — Ayet + Hadis + Dua"""
    log.info("Öğle içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Öğle")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        await asyncio.sleep(2)
        await bot.send_message(TELEGRAM_CHANNEL_ID, REKLAM)
        log.info("✅ Öğle içeriği ve reklam gönderildi.")
    except Exception as e:
        log.error(f"❌ Öğle hatası: {e}")


async def ikindi_gonder():
    """Her gün 15:00 — Ayet + Hadis + Dua"""
    log.info("İkindi içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "İkindi")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        await asyncio.sleep(2)
        await bot.send_message(TELEGRAM_CHANNEL_ID, REKLAM)
        log.info("✅ İkindi içeriği ve reklam gönderildi.")
    except Exception as e:
        log.error(f"❌ İkindi hatası: {e}")


async def aksam_gonder():
    """Her gün 21:00 — Ayet + Hadis + Dua"""
    log.info("Akşam içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Akşam/Yatsı")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        await asyncio.sleep(2)
        await bot.send_message(TELEGRAM_CHANNEL_ID, REKLAM)
        log.info("✅ Akşam içeriği ve reklam gönderildi.")
    except Exception as e:
        log.error(f"❌ Akşam hatası: {e}")


async def persembe_gonder():
    """Her Perşembe 20:00 — Sabah içeriği + Cuma Vaazı"""
    log.info("Perşembe/Cuma içeriği gönderiliyor...")
    try:
        # 1. Sabah içeriği
        sabah = await asyncio.to_thread(sabah_icerigi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, sabah)
        log.info("✅ Sabah içeriği gönderildi.")

        await asyncio.sleep(3)

        # 2. Cuma vaazı
        vaaz = await asyncio.to_thread(cuma_vaazi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, vaaz)
        log.info("✅ Cuma vaazı gönderildi.")

        await asyncio.sleep(2)

        # 3. Reklam
        await bot.send_message(TELEGRAM_CHANNEL_ID, REKLAM)
        log.info("✅ Reklam gönderildi.")

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

    # 15:00 — İkindi (her gün)
    scheduler.add_job(ikindi_gonder, "cron",
        hour=15, minute=0, timezone=tz)

    # 21:00 — Akşam/Yatsı (her gün)
    scheduler.add_job(aksam_gonder, "cron",
        hour=21, minute=0, timezone=tz)

    # Perşembe 20:00 — Sabah içeriği + Cuma vaazı
    scheduler.add_job(persembe_gonder, "cron",
        day_of_week="thu", hour=20, minute=0, timezone=tz)

    log.info("⏰ Zamanlayıcı kuruldu.")

# ─── Test Komutları ────────────────────────────────────────────────────────────

@dp.message()
async def komutlar(message: Message):
    if message.text == "/start":
        await message.answer(
            "🤖 *İslami İçerik Botu Aktif*\n\n"
            "📅 Günlük program:\n"
            "• 08:00 — Olay + Ayet + Hadis + Dua + Vaaz\n"
            "• 12:00 — Öğle Ayeti + Hadis + Dua\n"
            "• 15:00 — İkindi Ayeti + Hadis + Dua\n"
            "• 21:00 — Akşam Ayeti + Hadis + Dua\n"
            "• Perşembe 20:00 — Sabah içeriği + Cuma Vaazı\n\n"
            "Test komutları:\n"
            "`/test_sabah` — sabah içeriği\n"
            "`/test_ogle` — öğle içeriği\n"
            "`/test_ikindi` — ikindi içeriği\n"
            "`/test_aksam` — akşam içeriği\n"
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
    elif message.text == "/test_aksam":
        await message.answer("⏳ Üretiliyor...")
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Akşam/Yatsı")
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
