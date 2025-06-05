import discord
from discord.ext import commands
import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from jigsawstack import JigsawStack
from dashboard import start_dashboard, bot_start_time
import socket
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# --- Config from environment ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIGSAW_API_KEY = os.getenv("JIGSAWSTACK_API_KEY")  
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# --- Discord intents and bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- JigsawStack client ---
jigsaw = JigsawStack(api_key=JIGSAW_API_KEY)

# --- Database for caching scanned images ---
conn = sqlite3.connect("cache.db")
c = conn.cursor()
c.execute(
    """
CREATE TABLE IF NOT EXISTS scanned_images (
    url TEXT PRIMARY KEY,
    scanned_at TEXT
)
"""
)
conn.commit()

# --- Rate limiting per user ---
SCAN_COOLDOWN_SECONDS = 5
last_scan_time = {}

# --- Audit log file ---
AUDIT_LOG_FILE = "audit.log"

# --- Helper to log audit info ---
def log_audit(message: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {message}\n"
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

async def scan_image(url: str):
    try:
        # Run blocking call in thread pool to avoid blocking event loop
        response = await asyncio.to_thread(jigsaw.validate.nsfw, {"url": url})
        if not response["success"]:
            return None
        return response
    except Exception as e:
        print(f"API error: {e}")
        return None

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    start_dashboard()
    # Print dashboard URL info
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    print(f"Dashboard running at http://localhost:8080 or http://{local_ip}:8080")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None or message.guild.id != GUILD_ID:
        return

    now = datetime.now(timezone.utc)
    user_id = message.author.id
    last_time = last_scan_time.get(user_id)
    if last_time and (now - last_time).total_seconds() < SCAN_COOLDOWN_SECONDS:
        return
    last_scan_time[user_id] = now

    for attachment in message.attachments:
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            continue
        url = attachment.url

        # Check cache (avoid rescanning)
        c.execute("SELECT scanned_at FROM scanned_images WHERE url = ?", (url,))
        if c.fetchone():
            continue  # Already scanned

        result = await scan_image(url)
        if result is None:
            continue

        nsfw = result.get("nsfw", False)
        nudity = result.get("nudity", False)
        gore = result.get("gore", False)
        nsfw_score = result.get("nsfw_score", 0)
        nudity_score = result.get("nudity_score", 0)
        gore_score = result.get("gore_score", 0)

        # Cache the scanned image
        c.execute(
            "INSERT OR REPLACE INTO scanned_images (url, scanned_at) VALUES (?, ?)",
            (url, now.isoformat()),
        )
        conn.commit()

        if nsfw or nudity or gore:
            try:
                await message.delete()
            except Exception as e:
                print(f"Failed to delete message: {e}")

            reasons = []
            if nsfw:
                reasons.append(f"NSFW (score: {nsfw_score:.2f})")
            if nudity:
                reasons.append(f"Nudity (score: {nudity_score:.2f})")
            if gore:
                reasons.append(f"Gore (score: {gore_score:.2f})")
            reason_str = ", ".join(reasons)

            log_msg = f"User: {message.author} | URL: {url} | {reason_str}"
            log_audit(log_msg)

            if LOGGING_CHANNEL_ID:
                channel = bot.get_channel(LOGGING_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        title="NSFW/Gore/Nudity Detected and Deleted",
                        description=f"User: {message.author} ({message.author.id})\nURL: {url}\nReason: {reason_str}",
                        color=discord.Color.red(),
                        timestamp=now,
                    )
                    await channel.send(embed=embed)

            try:
                await message.author.send(
                    f"Your image was removed because it was flagged as: {reason_str}."
                )
            except Exception:
                pass

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
