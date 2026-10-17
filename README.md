# Din Botu — Islamic Content Telegram Bot

An AI-powered Telegram bot that automatically sends daily Islamic content (Quran verses, hadiths, prayers, sermons) to a channel.

## Features

- **Daily Content:** Sends Quran verses (Arabic + Turkish translation), hadiths (Arabic + Turkish translation), and time-specific prayers at morning, noon, and afternoon
- **Morning Sermon:** Generates a daily themed sermon in a warm, conversational imam style
- **Friday Sermon:** Sends a detailed special Friday sermon on Thursday evening
- **Weekly Surah Rotation:** Each day is assigned a fixed Quran chapter (An-Nisa, Al-Ma'idah, Al-An'am, Al-A'raf, Al-Anfal, At-Tawbah, Yunus)
- **Monthly Topic Rotation:** Each week of the month focuses on a different theme (family, worship, morality, afterlife)
- **Theme Variety:** Random selection from 20 different themes (patience, gratitude, repentance, mercy, etc.)
- **Admin Commands:** Test and send commands via Telegram

## Schedule (Istanbul Time)

| Time | Content |
|------|---------|
| 08:00 (Mon-Wed, Fri-Sun) | Verse + Hadith + Prayer + Sermon |
| 12:00 (Every day) | Verse + Hadith + Prayer |
| 16:00 (Every day) | Verse + Hadith + Prayer |
| 20:00 (Thursday) | Morning content + Special Friday Sermon |

## Tech Stack

- **Python 3.11+**
- **aiogram 3** — Telegram Bot API framework
- **Anthropic Claude API** — AI-powered content generation
- **APScheduler** — Scheduled task management
- **python-dotenv** — Environment variable management

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Hasankr-27/din-botu.git
cd din-botu
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

```env
TELEGRAM_BOT_TOKEN=your_botfather_token
TELEGRAM_CHANNEL_ID=@your_channel
ANTHROPIC_API_KEY=your_anthropic_api_key
ADMIN_ID=your_telegram_user_id
```

- **TELEGRAM_BOT_TOKEN:** Obtained from [@BotFather](https://t.me/BotFather)
- **TELEGRAM_CHANNEL_ID:** Your channel username (e.g. `@islamchannel`)
- **ANTHROPIC_API_KEY:** Obtained from [Anthropic Console](https://console.anthropic.com/)
- **ADMIN_ID:** Telegram user ID authorized to use bot commands

### 4. Run the bot

```bash
python bot.py
```

### 5. Test

Send these commands to your bot on Telegram:

| Command | Description |
|---------|-------------|
| `/start` | Bot info |
| `/test_sabah` | Preview morning content |
| `/test_ogle` | Preview noon content |
| `/test_ikindi` | Preview afternoon content |
| `/test_cuma` | Preview Friday sermon |
| `/test_gonder` | Send to channel |

## Project Structure

```
din-botu/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
├── .env.example        # Environment variables template
├── .gitignore
├── KURULUM.md          # Setup guide (Turkish)
├── README.md           # README (Turkish)
└── README_EN.md        # README (English)
```

## Deployment

The bot can be deployed on platforms like [Railway](https://railway.app/). The `runtime.txt` file specifies the Python version.

## License

This project is for educational purposes.
