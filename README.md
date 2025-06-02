# Ironimus - NSFW Image Moderation Discord Bot

Ironimus is a powerful Discord bot that automatically scans images posted in your server and removes any content that is NSFW, contains nudity, or gore. It uses the [JigsawStack API](https://jigsawstack.com) for accurate content detection, helps keep your community safe, and provides detailed logs for moderators.

---

## 🚀 Features

- ✅ Automatically scans all images sent in your server  
- ❌ Deletes messages containing NSFW, nudity, or gore  
- 📩 Notifies the user via DM when their image is removed  
- 📊 Sends detailed logs to a moderation channel using embeds  
- ⏱️ Enforces per-user rate limiting (3 deletions per 10 minutes)  
- 🧾 Saves weekly logs to disk in `/logs`  

---

## 📦 Requirements

- Node.js v18+  
- A Discord bot token  
- A [JigsawStack API key](https://jigsawstack.com)  
- Required Node packages:
  ```bash
  npm install discord.js jigsawstack
  ```

---

## 🔧 Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ironimus.git
   cd ironimus
   ```

2. **Install dependencies:**
   ```bash
   npm install discord.js jigsawstack
   ```

3. **Configure the bot:**

   Edit the bot's config directly in the script (or use environment variables if preferred):

   ```js
   const DISCORD_TOKEN = 'YOUR_DISCORD_BOT_TOKEN';
   const JIGSAW_API_KEY = 'YOUR_JIGSAW_API_KEY';
   const LOG_CHANNEL_ID = 'YOUR_LOG_CHANNEL_ID';
   const GUILD_ID = 'YOUR_GUILD_ID';
   ```

4. **Run the bot:**
   ```bash
   node index.js
   ```

---

## 📁 Logs

All moderation actions are saved weekly in the `/logs` directory with filenames like:

```
log_2025_week22.txt
```

Each entry includes the user, channel, detection type, and timestamp.

---

## ⚠️ Rate Limiting

To prevent abuse or flooding:

- Each user can have **up to 20 deleted images per 10 minutes**
- If a user exceeds the limit, Ironimus temporarily stops deleting their messages
- A warning is sent to the log channel

---

## 🤖 Permissions Required

To function properly, your bot should have the following permissions:

- Read Messages  
- Manage Messages (for deleting)  
- Send Messages  
- Embed Links  
- Read Message History  
- Direct Messages (to notify users)  

---

## 📬 Support & Contribution

Feel free to fork, improve, or report issues. Contributions are welcome!

---

## 🛡 Disclaimer

Ironimus relies on JigsawStack's AI-based detection. No system is perfect—always review logs to ensure fair moderation.
