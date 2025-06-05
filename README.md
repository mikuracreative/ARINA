# 🛡️ Ironimus — Image Moderation Bot for Discord

**Ironimus** scans all images using [JigsawStack](https://jigsawstack.com/) to detect **NSFW**, **nudity**, and **gore**. It removes flagged content, logs it, and can notify users.

> 🚀 Hosting? Use [ZAP-Hosting (Affiliate)](https://zap-hosting.com/majestic)

---

## ✨ Features

- 🧠 AI image detection  
- 🗑️ Auto message deletion  
- 📋 Logging to channel  
- 📬 Optional user DMs  
- 🧊 Image caching  
- ⏳ 5s per-user cooldown  
- 🧾 `audit.log` for records  
- 🌐 Web dashboard (Flask)

---

## ⚙️ Setup

```bash
git clone https://github.com/mikuracreative/Ironimus.git
cd Ironimus

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:

```
DISCORD_TOKEN=your_token
JIGSAWSTACK_API_KEY=your_api_key
LOGGING_CHANNEL_ID=channel_id
GUILD_ID=guild_id
```

---

## ▶️ Run

```bash
python bot.py
```

Access the dashboard at http://localhost:8080 or the address shown in the console.

---

## 📊 Dashboard Shows

- Uptime  
- Logs  
- Basic stats

---

## 📚 Logs

All events saved to `audit.log`.

---

## ✅ Bot Needs

- Read history  
- View channels  
- Manage messages  
- Send messages & DMs  
- Embed links

---

## 📌 Notes

- Only works in `GUILD_ID`  
- Default cooldown: **5s/user**

---

## 📄 License

MIT

---

## 🙋‍♂️ Help?

Open an issue or contact us!
