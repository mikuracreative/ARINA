# 🛡️ **Ironimus** — Smart Image Moderation Bot for Discord

**Ironimus** is a powerful Discord bot that scans every image posted in your server using the [JigsawStack API](https://jigsawstack.com/) to detect **NSFW**, **nudity**, and **gore** 🔍. It removes flagged content, logs events to a dedicated channel, and can even DM users with the reason 📩.

> 🚀 **Want reliable hosting for your bot?** Check out Zap-Hosting:  
> 👉 <a href="https://zap-hosting.com/majestic">ZAP-Hosting (Affiliate Link)</a>

---

## ✨ Features

- 🧠 **AI-Powered Scanning** – Automatically detects inappropriate images
- 🗑️ **Auto Deletes** – Removes offending messages instantly
- 📋 **Logging** – Posts alerts in your logging channel
- 📬 **Optional DM Notices** – Notifies users when their content is removed
- 🧊 **Image Caching** – Avoids re-scanning the same images
- ⏳ **Rate Limiting** – Prevents abuse (default: 5s cooldown per user)
- 🧾 **Audit Logs** – All detections saved in `audit.log`
- 🌐 **Web Dashboard** – Simple Flask dashboard with stats and logs

---

## ⚙️ Setup

### 1. 🧩 Clone the Repo

\`\`\`bash
git clone https://github.com/mikuracreative/Ironimus.git
cd Ironimus
\`\`\`

### 2. 🧪 Create a Virtual Environment (Recommended)

\`\`\`bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 3. 📦 Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. 🔐 Configure Environment

Create a `.env` file in the root with:

\`\`\`
DISCORD_TOKEN=your_discord_bot_token_here
JIGSAWSTACK_API_KEY=your_jigsawstack_api_key_here
LOGGING_CHANNEL_ID=your_logging_channel_id_here
GUILD_ID=your_guild_id_here
\`\`\`

---

## ▶️ Running the Bot

\`\`\`bash
python bot.py
\`\`\`

🟢 Once running, you’ll see:

\`\`\`
Bot connected as YourBotName
Dashboard running at http://localhost:8080
\`\`\`

---

## 📊 Dashboard

Access it at `http://localhost:8080` to see:

- 🕒 Bot uptime  
- 📁 Recent logs  
- 📈 Basic stats  

---

## 📚 Audit Trail

All detection events are saved in `audit.log` with timestamps for easy review 🗂️.

---

## ✅ Permissions Required

Make sure your bot has:

- 🔍 Read Message History  
- 👀 View Channels  
- 🗑️ Manage Messages  
- 📨 Send Messages & DMs  
- 🔗 Embed Links  

---

## 📌 Notes

- Works **only** in the specified `GUILD_ID`
- Default cooldown: **5s per user**

---

## 📄 License

MIT License

---

## 🙋‍♂️ Need Help?

Open an issue or reach out directly — happy to help!
