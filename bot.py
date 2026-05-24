"""
İslami İçerik Telegram Botu
- Her gün 20:00'de: Günün olayı + Ayet + Hadis + Dua
- Her Perşembe 20:00'de: Günlük içerik + Cuma Vaazı
- Her içeriğin altına otomatik reklam eklenir

Kurulum:
  pip install aiogram anthropic apscheduler python-dotenv

.env dosyası oluştur:
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHANNEL_ID=@kanal_adiniz
  ANTHROPIC_API_KEY=...
"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import anthropic

# ─── Yapılandırma ──────────────────────────────────────────────────────────────

load_dotenv()

TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # örn: @islamikanal
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")

# ─── Reklam Metni (buraya kendi reklamını yaz) ─────────────────────────────────

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

bot        = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode="Markdown")
dp         = Dispatcher()
ai_client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── Claude API Fonksiyonları ──────────────────────────────────────────────────

def claude_iste(prompt: str) -> str:
    """Claude'a istek atar ve cevabı döndürür."""
    mesaj = ai_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return mesaj.content[0].text


def gunluk_icerik_uret() -> str:
    """Günün tarihine göre ayet, hadis, dua ve kısa vaaz üretir."""
    bugun = datetime.now().strftime("%d %B %Y")

    prompt = f"""
Bugünün tarihi: {bugun}

Aşağıdaki formatta Türkçe İslami günlük içerik oluştur.
Markdown kullan (Telegram uyumlu: *kalın*, _italik_).

Format:
📅 *GÜNÜN OLAYI*
[Bu tarihe yakın İslam tarihinden kısa, ilginç bir olay — 2-3 cümle]

📖 *GÜNÜN AYETİ*
[Olayla bağlantılı bir ayet — Türkçe meali, parantez içinde Sure:Ayet numarası]

📚 *GÜNÜN HADİSİ*
[Konuyla ilgili bir hadis — Türkçe, parantez içinde kaynak]

🤲 *GÜNÜN DUASI*
[Kısa, içten bir dua — Arapça orijinal + Türkçe anlamı]

🕌 *GÜNÜN VAAZI*
[Günün olayı veya ayetiyle bağlantılı, sade ve samimi 150-200 kelimelik kısa vaaz.
Günlük hayata dokunan, herkesin anlayabileceği bir dil kullan.]

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt)


def cuma_vaazi_uret() -> str:
    """Haftanın temasına göre kapsamlı Cuma vaazı üretir."""
    bugun = datetime.now().strftime("%d %B %Y")

    prompt = f"""
Bugünün tarihi: {bugun} (Perşembe — yarın Cuma)

Türkçe, 500-600 kelimelik derin ve etkileyici bir Cuma vaazı yaz.
Markdown kullan (Telegram uyumlu).

Format:
🕌 *CUMA VAAZI*
*[Vaazın başlığı — dikkat çekici, düşündürücü]*

_"[Konuyla ilgili güçlü bir ayet meali]"_
_(Sure adı, Ayet numarası)_

*📖 Ayetin Tefsiri:*
[Ayetin derinlemesine açıklaması — 3-4 cümle, alimlerden görüşler]

*📚 Peygamberimizden:*
[2 hadis — kaynaklarıyla birlikte, konuyla doğrudan ilgili]

*💭 Bugüne Yansıması:*
[Modern hayattan somut örneklerle vaazın ana mesajı — 3 paragraf, samimi ve sade dil]

*🌟 Bu Haftanın Ameli:*
[Okuyucunun bu hafta yapabileceği küçük ama anlamlı bir ibadet/davranış önerisi]

*🤲 Cuma Duası:*
[Arapça dua + Türkçe anlamı]

Tema: sabır, şükür, ihlas, tevbe, adalet, merhamet, birlik, dua, tevekkül gibi konulardan
bu haftaya en uygun olanı seç. Vaaz hutbe tadında ama sohbet sıcaklığında olsun.
Sadece vaazı yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt)


# ─── Gönderim Fonksiyonları ────────────────────────────────────────────────────

async def gunluk_gondер():
    """Her gün 20:00'de çalışır — günlük içerik gönderir."""
    log.info("Günlük içerik gönderiliyor...")
    try:
        icerik = gunluk_icerik_uret()
        tam_mesaj = icerik + "\n\n" + REKLAM
        await bot.send_message(TELEGRAM_CHANNEL_ID, tam_mesaj)
        log.info("✅ Günlük içerik gönderildi.")
    except Exception as e:
        log.error(f"❌ Günlük içerik hatası: {e}")


async def persembe_gonder():
    """Her Perşembe 20:00'de çalışır — günlük içerik + Cuma vaazı gönderir."""
    log.info("Perşembe içeriği gönderiliyor...")
    try:
        # 1. Günlük içerik
        gunluk = gunluk_icerik_uret()
        await bot.send_message(TELEGRAM_CHANNEL_ID, gunluk + "\n\n" + REKLAM)
        log.info("✅ Günlük içerik gönderildi.")

        await asyncio.sleep(3)  # Kısa bekleme

        # 2. Cuma vaazı
        vaaz = cuma_vaazi_uret()
        await bot.send_message(TELEGRAM_CHANNEL_ID, vaaz + "\n\n" + REKLAM)
        log.info("✅ Cuma vaazı gönderildi.")

    except Exception as e:
        log.error(f"❌ Perşembe içerik hatası: {e}")


# ─── Zamanlayıcı Kurulumu ──────────────────────────────────────────────────────

def zamanlayici_kur(scheduler: AsyncIOScheduler):
    """
    Zamanlama:
    - Pazartesi–Çarşamba–Cuma–Cumartesi–Pazar: her gün 20:00 günlük içerik
    - Perşembe: 20:00 günlük içerik + Cuma vaazı
    """

    # Her gün 20:00 — günlük içerik (Perşembe hariç)
    scheduler.add_job(
        gunluk_gondер,
        trigger="cron",
        day_of_week="mon,tue,wed,fri,sat,sun",
        hour=20,
        minute=0,
        timezone="Europe/Istanbul"
    )

    # Perşembe 20:00 — günlük içerik + Cuma vaazı
    scheduler.add_job(
        persembe_gonder,
        trigger="cron",
        day_of_week="thu",
        hour=20,
        minute=0,
        timezone="Europe/Istanbul"
    )

    log.info("⏰ Zamanlayıcı kuruldu.")


# ─── Test Komutu (/test) ───────────────────────────────────────────────────────

@dp.message()
async def test_komutu(message: Message):
    """
    Bot'u test etmek için:
    /test_gunluk  → günlük içerik önizle
    /test_vaaz    → Cuma vaazı önizle
    /test_gonder  → kanala gerçekten gönder
    """
    if message.text == "/test_gunluk":
        await message.answer("⏳ Üretiliyor...")
        icerik = gunluk_icerik_uret()
        await message.answer(icerik + "\n\n" + REKLAM)

    elif message.text == "/test_vaaz":
        await message.answer("⏳ Vaaz üretiliyor...")
        vaaz = cuma_vaazi_uret()
        await message.answer(vaaz + "\n\n" + REKLAM)

    elif message.text == "/test_gonder":
        await message.answer("📤 Kanala gönderiliyor...")
        await persembe_gonder()
        await message.answer("✅ Gönderildi!")

    elif message.text == "/start":
        await message.answer(
            "🤖 *İslami İçerik Botu Aktif*\n\n"
            "📅 Her gün 20:00'de içerik gönderilir\n"
            "🕌 Her Perşembe 20:00'de Cuma vaazı eklenir\n\n"
            "Test komutları:\n"
            "`/test_gunluk` — içerik önizle\n"
            "`/test_vaaz` — vaaz önizle\n"
            "`/test_gonder` — kanala gönder"
        )


# ─── Ana Döngü ─────────────────────────────────────────────────────────────────

async def main():
    scheduler = AsyncIOScheduler()
    zamanlayici_kur(scheduler)
    scheduler.start()

    log.info("🚀 Bot başlatıldı — Ctrl+C ile durdur")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())