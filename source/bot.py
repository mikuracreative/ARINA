import discord
from discord.ext import commands
import asyncio
import os
import atexit
import aiosqlite
from datetime import datetime, timezone
from jigsawstack import JigsawStack
from dashboard import start_dashboard, bot_start_time
import socket
from dotenv import load_dotenv
import traceback

# Load .env variables
load_dotenv()

# --- Config from environment ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIGSAW_API_KEY = os.getenv("JIGSAWSTACK_API_KEY")
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# ✅ Security: Validate critical configuration
if not DISCORD_TOKEN or not JIGSAW_API_KEY:
    raise ValueError("Missing DISCORD_TOKEN or JIGSAWSTACK_API_KEY in environment.")

# --- Discord intents and bot ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- JigsawStack client ---
jigsaw = JigsawStack(api_key=JIGSAW_API_KEY)

# --- Database for caching scanned images ---
db_conn = None

def close_db():
    if db_conn:
        asyncio.run(db_conn.close())

atexit.register(close_db)

# --- Rate limiting per user ---
from discord.ext.commands import CooldownMapping, BucketType
SCAN_COOLDOWN_SECONDS = 2
cooldown = CooldownMapping.from_cooldown(1, SCAN_COOLDOWN_SECONDS, BucketType.user)

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
        # ⚡ Async safety: Run blocking call in thread pool
        response = await asyncio.to_thread(jigsaw.validate.nsfw, {"url": url})
        if not response["success"]:
            return None
        return response
    except Exception as e:
        print(f"API error: {e}")
        traceback.print_exc()
        return None

logging_channel = None

@bot.event
async def on_ready():
    global db_conn, logging_channel
    print(f"Bot connected as {bot.user}")
    start_dashboard()
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    print(f"Dashboard running at http://localhost:8080 or http://{local_ip}:8080")

    # ⚡ Async safety: Open DB connection
    db_conn = await aiosqlite.connect("cache.db")
    await db_conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scanned_images (
            url TEXT PRIMARY KEY,
            scanned_at TEXT
        )
        """
    )
    await db_conn.commit()

    # 🧹 Cleanup: Cache logging channel
    logging_channel = bot.get_channel(LOGGING_CHANNEL_ID)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None or message.guild.id != GUILD_ID:
        return

    now = datetime.now(timezone.utc)

    # 🔁 Rate limit
    bucket = cooldown.get_bucket(message)
    if bucket.update_rate_limit():
        return

    for attachment in message.attachments:
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            continue
        url = attachment.url

        try:
            async with db_conn.execute("SELECT scanned_at FROM scanned_images WHERE url = ?", (url,)) as cursor:
                if await cursor.fetchone():
                    continue

            result = await scan_image(url)
            if result is None:
                continue

            nsfw = result.get("nsfw", False)
            nudity = result.get("nudity", False)
            gore = result.get("gore", False)
            nsfw_score = result.get("nsfw_score", 0)
            nudity_score = result.get("nudity_score", 0)
            gore_score = result.get("gore_score", 0)

            # Cache scanned image
            await db_conn.execute(
                "INSERT OR REPLACE INTO scanned_images (url, scanned_at) VALUES (?, ?)",
                (url, now.isoformat())
            )
            await db_conn.commit()

            if nsfw or nudity or gore:
                try:
                    await message.delete()
                except Exception as e:
                    print(f"Failed to delete message: {e}")
                    traceback.print_exc()

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

                if logging_channel:
                    embed = discord.Embed(
                        title="NSFW/Gore/Nudity Detected and Deleted",
                        description=f"User: {message.author} ({message.author.id})\nURL: {url}\nReason: {reason_str}",
                        color=discord.Color.red(),
                        timestamp=now,
                    )
                    await logging_channel.send(embed=embed)

                try:
                    await message.author.send(
                        f"Your image was removed because it was flagged as: {reason_str}."
                    )
                except Exception as e:
                    print(f"Failed to notify user: {e}")
                    traceback.print_exc()

        except Exception as e:
            print(f"Unexpected error while processing image: {e}")
            traceback.print_exc()

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
