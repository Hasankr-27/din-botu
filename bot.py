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
import json
import logging
import pathlib
import re
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

# ─── Kullanılan İçerik Takibi ─────────────────────────────────────────────────

_data_dir = pathlib.Path("/app/data")
try:
    _data_dir.mkdir(parents=True, exist_ok=True)
    USED_CONTENT_FILE = _data_dir / "used_content.json"
except OSError:
    USED_CONTENT_FILE = pathlib.Path("used_content.json")

MAX_USED = 50

def _used_yukle() -> dict:
    try:
        with open(USED_CONTENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "ayetler" in data:
            return data
    except Exception:
        pass
    return {"ayetler": [], "hadisler": []}

def _used_kaydet(ayet: str | None, hadis: str | None):
    data = _used_yukle()
    if ayet:
        data["ayetler"].append(ayet)
        if len(data["ayetler"]) > MAX_USED:
            data["ayetler"] = data["ayetler"][-MAX_USED:]
    if hadis:
        data["hadisler"].append(hadis)
        if len(data["hadisler"]) > MAX_USED:
            data["hadisler"] = data["hadisler"][-MAX_USED:]
    try:
        with open(USED_CONTENT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"used_content.json yazma hatası: {e}")

# ─── Claude API ────────────────────────────────────────────────────────────────

def claude_iste(prompt: str, max_tokens: int = 2000) -> str:
    used = _used_yukle()

    # Kullanılmış listeyi prompt'un başına ekle
    parts = []
    if used["ayetler"]:
        parts.append("Ayetler: " + ", ".join(used["ayetler"]))
    if used["hadisler"]:
        parts.append("Hadisler: " + ", ".join(used["hadisler"]))
    if parts:
        used_str = "\n".join(parts)
        prompt = (
            f"KESİNLİKLE şu ayet ve hadisleri KULLANMA:\n{used_str}\n"
            f"Tamamen farklı ayet ve hadis seç.\n\n"
        ) + prompt

    # İçerikten sonra referans satırları iste
    prompt += (
        "\n\nİçeriği verdikten sonra en sona şu iki satırı ekle "
        "(başka hiçbir şey ekleme):\n"
        "KULLANILAN_AYET: [sure:ayet_no, örn: Bakara:255]\n"
        "KULLANILAN_HADİS: [kaynak, örn: Buhari:İman1]"
    )

    mesaj = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = mesaj.content[0].text

    # Referansları çıkar ve kaydet
    ayet_m = re.search(r"KULLANILAN_AYET:\s*(.+)", raw)
    hadis_m = re.search(r"KULLANILAN_HADİS:\s*(.+)", raw)
    _used_kaydet(
        ayet_m.group(1).strip() if ayet_m else None,
        hadis_m.group(1).strip() if hadis_m else None,
    )

    # Referans satırlarını temizleyip döndür
    clean = re.sub(r"\n*KULLANILAN_AYET:.*", "", raw, flags=re.DOTALL).strip()
    return clean

# ─── Günlük Tema ──────────────────────────────────────────────────────────────

TEMALAR = [
    "sabır ve tahammül",
    "şükür ve minnettarlık",
    "tevbe ve af dilemek",
    "merhamet ve şefkat",
    "musibetler ve imtihan",
    "kul hakkı ve adalet",
    "ihlas ve samimiyet",
    "günah ve sevap",
    "tevekkül ve Allah'a güven",
    "ölüm ve ahiret",
    "aile ve anne-baba hakkı",
    "sadaka ve yardımlaşma",
    "kibir ve tevazu",
    "haset ve kıskançlık",
    "dua ve niyaz",
    "ilim ve hikmet",
    "zikir ve Allah'ı anmak",
    "dürüstlük ve emanet",
    "birlik ve kardeşlik",
    "nefis terbiyesi",
]

def gunun_temasi() -> str:
    gun = datetime.now().timetuple().tm_yday
    return TEMALAR[gun % len(TEMALAR)]

# ─── İçerik Üretici Fonksiyonlar ───────────────────────────────────────────────

def ayet_hadis_dua_uret(vakit: str) -> str:
    """Öğle, İkindi için kısa içerik üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    tema = gunun_temasi()
    prompt = f"""
Bugünün tarihi: {bugun}, Vakit: {vakit}, Günün teması: {tema}

Her gün farklı ayet ve hadis seç, bir önceki günle aynı olmasın.

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

ÖNEMLİ: Bugünün tarihi {bugun}. Bu tarihe özel, rastgele ama anlamlı bir ayet ve hadis seç.

Sadece içeriği yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=1100)


def sabah_icerigi_uret() -> str:
    """Sabah için ayet + hadis + dua + vaaz üretir."""
    bugun = datetime.now().strftime("%d %B %Y")
    tema = gunun_temasi()
    prompt = f"""
Bugünün tarihi: {bugun}, Günün teması: {tema}

Her gün farklı ayet ve hadis seç, bir önceki günle aynı olmasın.

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

ÖNEMLİ: Bugünün tarihi {bugun}. Rastgele ama anlamlı bir ayet ve hadis seç.

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

Tema bu haftanın ruhuna uygun seç: sabır, şükür, tevbe, merhamet, kul hakkı, ihlas vb.

Sadece vaazı yaz, başka açıklama ekleme.
"""
    return claude_iste(prompt, max_tokens=2600)

# ─── Gönderim Fonksiyonları ────────────────────────────────────────────────────

async def sabah_gonder():
    """Her gün 08:00 — Ayet + Hadis + Dua + Vaaz"""
    log.info("Sabah içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(sabah_icerigi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info("✅ Sabah içeriği gönderildi.")
    except Exception as e:
        log.error(f"❌ Sabah hatası: {e}")


async def ogle_gonder():
    """Her gün 12:00 — Ayet + Hadis + Dua"""
    log.info("Öğle içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "Öğle")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info("✅ Öğle içeriği gönderildi.")
    except Exception as e:
        log.error(f"❌ Öğle hatası: {e}")


async def ikindi_gonder():
    """Her gün 16:00 — Ayet + Hadis + Dua"""
    log.info("İkindi içeriği gönderiliyor...")
    try:
        icerik = await asyncio.to_thread(ayet_hadis_dua_uret, "İkindi")
        await bot.send_message(TELEGRAM_CHANNEL_ID, icerik)
        log.info("✅ İkindi içeriği gönderildi.")
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
        sabah = await asyncio.to_thread(sabah_icerigi_uret)
        await bot.send_message(TELEGRAM_CHANNEL_ID, sabah)
        log.info("✅ Sabah içeriği gönderildi.")

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
