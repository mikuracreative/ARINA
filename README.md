# Discord NSFW Image Scanner Bot

This Discord bot scans all images posted in a specific server using the [JigsawStack API](https://jigsawstack.com/) to detect NSFW content, nudity, and gore. It deletes flagged images, logs detections to a designated logging channel, and optionally DMs the user with the reason.

The bot also includes:
- Image caching to avoid re-scanning the same image URL
- Per-user rate limiting / cooldowns
- Persistent audit logs to a local file
- A simple modern dashboard showing bot stats and logs (runs on port 8080)

---

## Features

- Automatically scans all posted images in your server
- Deletes messages containing inappropriate images
- Logs detection events in a dedicated logging channel
- Sends a direct message to users whose images were removed
- Caches scanned images in SQLite to avoid repeated scans
- Rate limits image scanning per user to avoid abuse
- Audit trail saved in `audit.log`
- Flask-based dashboard showing uptime, recent logs, and stats

---

## Setup

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/discord-nsfw-scanner.git
cd discord-nsfw-scanner
```

### 2. Create and activate a Python virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root with the following:

```
DISCORD_TOKEN=your_discord_bot_token_here
JIGSAWSTACK_API_KEY=your_jigsawstack_api_key_here
LOGGING_CHANNEL_ID=your_logging_channel_id_here
GUILD_ID=your_guild_id_here
```

- **DISCORD_TOKEN**: Your Discord bot token
- **JIGSAWSTACK_API_KEY**: Your API key from JigsawStack
- **LOGGING_CHANNEL_ID**: The channel ID where the bot will send detection logs
- **GUILD_ID**: Your Discord server (guild) ID where the bot should scan images

---

## Usage

Run the bot with:

```bash
python bot.py
```

You should see output like:

```
Bot connected as YourBotName
Dashboard running at http://localhost:8080 or http://your.local.ip:8080
```

- The dashboard will be accessible on port 8080 of your machine.
- The bot will start monitoring images and act accordingly.

---

## Dashboard

The dashboard is a simple Flask app that shows:

- Bot uptime
- Recent detection logs (from audit log file)
- Basic statistics

Access it by navigating to `http://localhost:8080` in your browser.

---

## Audit Logs

All detection events are saved to `audit.log` with timestamps for audit and review purposes.

---

## Requirements

See `requirements.txt` for all Python dependencies.

---

## Notes

- The bot only works on the server (`GUILD_ID`) you specify.
- Make sure the bot has the necessary permissions:
  - Read Message History
  - Read Messages / View Channels
  - Manage Messages (to delete)
  - Send Messages
  - Embed Links (for logging embeds)
  - Send Direct Messages (to notify users)
- Rate limiting is set to 5 seconds per user by default to avoid spam.

---

## License

MIT License

---

## Contact

For questions or support, please open an issue or contact me directly.

---
