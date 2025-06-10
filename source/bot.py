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

from discord.ext.commands import CooldownMapping, BucketType
SCAN_COOLDOWN_SECONDS = 2
cooldown = CooldownMapping.from_cooldown(1, SCAN_COOLDOWN_SECONDS, BucketType.user)

AUDIT_LOG_FILE = "audit.log"

def log_audit(message: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {message}\n"
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

async def scan_image(url: str):
    try:
        print(f"🔍 Scanning image at URL: {url}")
        response = await asyncio.to_thread(jigsaw.validate.nsfw, {"url": url})
        print(f"📦 Scan response: {response}")
        if not response["success"]:
            print("❌ API call failed")
            return None
        return response
    except Exception as e:
        print(f"🔥 API error during scanning: {e}")
        traceback.print_exc()
        return None

logging_channel = None

@bot.event
async def on_ready():
    global db_conn, logging_channel
    print(f"✅ Bot connected as {bot.user}")
    start_dashboard()
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    print(f"🌐 Dashboard running at http://localhost:8080 or http://{local_ip}:8080")

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

    logging_channel = bot.get_channel(LOGGING_CHANNEL_ID)
    if not logging_channel:
        print(f"⚠️ Logging channel with ID {LOGGING_CHANNEL_ID} not found")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None or message.guild.id != GUILD_ID:
        return

    print(f"\n📨 Message from {message.author} (ID: {message.author.id}) with {len(message.attachments)} attachments")

    now = datetime.now(timezone.utc)

    bucket = cooldown.get_bucket(message)
    if bucket.update_rate_limit():
        print("⏳ Rate limit triggered, skipping scan.")
        return

    for attachment in message.attachments:
        print(f"📎 Attachment filename: {attachment.filename}")
        print(f"📎 Attachment content type: {attachment.content_type}")

        if not attachment.content_type or not attachment.content_type.startswith("image"):
            print("⚠️ Skipped non-image attachment")
            continue

        url = attachment.url

        try:
            async with db_conn.execute("SELECT scanned_at FROM scanned_images WHERE url = ?", (url,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    print(f"🗃️ Already scanned this URL: {url} at {row[0]}")
                    continue

            result = await scan_image(url)
            if result is None:
                print("❌ Skipping due to invalid scan result")
                continue

            nsfw = result.get("nsfw", False)
            nudity = result.get("nudity", False)
            gore = result.get("gore", False)
            nsfw_score = result.get("nsfw_score", 0)
            nudity_score = result.get("nudity_score", 0)
            gore_score = result.get("gore_score", 0)

            print(f"🧠 NSFW detection flags: nsfw={nsfw} ({nsfw_score}), nudity={nudity} ({nudity_score}), gore={gore} ({gore_score})")

            await db_conn.execute(
                "INSERT OR REPLACE INTO scanned_images (url, scanned_at) VALUES (?, ?)",
                (url, now.isoformat())
            )
            await db_conn.commit()

            if nsfw or nudity or gore:
                try:
                    await message.delete()
                    print("🗑️ Message deleted due to detected content")
                except Exception as e:
                    print(f"❌ Failed to delete message: {e}")
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
                        title="🔞 NSFW/Gore/Nudity Detected and Deleted",
                        description=f"User: {message.author} ({message.author.id})\nURL: {url}\nReason: {reason_str}",
                        color=discord.Color.red(),
                        timestamp=now,
                    )
                    await logging_channel.send(embed=embed)

                try:
                    await message.author.send(
                        f"🚫 Your image was removed because it was flagged as: {reason_str}."
                    )
                except Exception as e:
                    print(f"❌ Failed to notify user: {e}")
                    traceback.print_exc()
            else:
                print("✅ Image passed NSFW checks.")

        except Exception as e:
            print(f"❌ Unexpected error while processing image: {e}")
            traceback.print_exc()

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
