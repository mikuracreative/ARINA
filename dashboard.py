from flask import Flask, render_template_string
from datetime import datetime, timezone
import threading

app = Flask(__name__)

# Modern Tailwind CSS-based dashboard UI template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ironimus Bot Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 font-sans">
  <div class="container mx-auto p-6">
    <div class="bg-white rounded-2xl shadow-md p-6 mb-6">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">Ironimus Bot Dashboard</h1>
      <p class="text-gray-600">Review NSFW detection logs and system activity.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4">Quick Stats</h2>
        <ul class="space-y-2">
          <li><span class="font-medium">Total Scanned:</span> {{ total_scanned }}</li>
          <li><span class="font-medium">Flagged Images:</span> {{ total_flagged }}</li>
          <li><span class="font-medium">Uptime:</span> {{ uptime }}</li>
        </ul>
      </div>

      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4">Status</h2>
        <p class="text-green-600 font-medium">Bot is running and connected.</p>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-md p-6">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Audit Log</h2>
      <div class="overflow-y-scroll max-h-[400px] border rounded-lg bg-gray-50 p-4 text-sm text-gray-800 whitespace-pre-wrap">
        <pre>{{ logs }}</pre>
      </div>
    </div>
  </div>
</body>
</html>
"""

# Store bot start time here; update this from your bot.py when you start dashboard
bot_start_time = datetime.now(timezone.utc)

@app.route("/")
def home():
    try:
        with open("audit.log", "r", encoding="utf-8") as f:
            logs = f.read()
    except FileNotFoundError:
        logs = "No logs yet."

    total_scanned = logs.count("URL:")
    total_flagged = (
        logs.count("NSFW: True") +
        logs.count("Nudity: True") +
        logs.count("Gore: True")
    )
    uptime_delta = datetime.now(timezone.utc) - bot_start_time
    uptime_minutes = int(uptime_delta.total_seconds() // 60)
    uptime = f"{uptime_minutes} minutes"

    return render_template_string(
        HTML_TEMPLATE,
        logs=logs,
        total_scanned=total_scanned,
        total_flagged=total_flagged,
        uptime=uptime,
    )

def run_dashboard():
    app.run(host="0.0.0.0", port=8080)

def start_dashboard():
    thread = threading.Thread(target=run_dashboard)
    thread.daemon = True
    thread.start()
