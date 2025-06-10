from flask import Flask, render_template_string
from datetime import datetime, timezone
import threading
from collections import deque

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex" />
  <meta http-equiv="refresh" content="15" />
  <title>ARINA Dashboard</title>
  <script src="https://cdn.tailwindcss.com/3.4.1"></script>
  <style>
    ::-webkit-scrollbar {
      width: 8px;
    }
    ::-webkit-scrollbar-thumb {
      background: #555;
      border-radius: 6px;
    }
  </style>
</head>
<body class="bg-gray-900 text-gray-100 font-sans antialiased">
  <div class="container mx-auto p-6">
    <div class="bg-gray-800 border border-purple-500/30 rounded-2xl shadow-xl p-6 mb-6 transition duration-500 hover:shadow-purple-500/20">
      <h1 class="text-4xl font-bold text-purple-300 mb-2 animate-fade-in">ARINA Bot Dashboard</h1>
      <p class="text-gray-400 text-sm">Monitoring image safety, uptime, and logs in real time.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div class="bg-gray-800 rounded-2xl p-6 border border-purple-400/20">
        <h2 class="text-2xl font-semibold text-purple-200 mb-4">📊 Quick Stats</h2>
        <ul class="space-y-2 text-gray-300">
          <li><span class="font-medium text-white">Total Scanned:</span> {{ total_scanned }}</li>
          <li><span class="font-medium text-white">Flagged Images:</span> {{ total_flagged }}</li>
          <li><span class="font-medium text-white">Uptime:</span> {{ uptime }}</li>
        </ul>
      </div>

      <div class="bg-gray-800 rounded-2xl p-6 border border-green-400/20">
        <h2 class="text-2xl font-semibold text-green-300 mb-4">🟢 Status</h2>
        <p class="text-green-400 font-medium">Bot is active and connected.</p>
      </div>
    </div>

    <div class="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h2 class="text-2xl font-semibold text-indigo-200 mb-4">📁 Audit Log</h2>
      <div class="overflow-y-scroll max-h-[400px] bg-gray-900 border border-gray-700 p-4 rounded-lg text-sm text-gray-300 whitespace-pre-wrap font-mono animate-fade-in">
        <pre>{{ logs | e }}</pre>
      </div>
    </div>
  </div>

  <script>
    document.querySelectorAll('.animate-fade-in').forEach(el => {
      el.classList.add('transition-opacity', 'duration-700', 'opacity-0');
      setTimeout(() => el.classList.remove('opacity-0'), 100);
    });
  </script>
</body>
</html>
"""

bot_start_time = datetime.now(timezone.utc)

def tail(filepath, n=500):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return ''.join(deque(f, maxlen=n))
    except FileNotFoundError:
        return "No logs yet."

def format_uptime(delta):
    seconds = int(delta.total_seconds())
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes}m"

@app.route("/")
def home():
    logs = tail("audit.log", n=500)
    total_scanned = logs.count("URL:")
    total_flagged = sum(logs.count(term) for term in ["NSFW", "Nudity", "Gore"])
    uptime_delta = datetime.now(timezone.utc) - bot_start_time
    uptime = format_uptime(uptime_delta)

    return render_template_string(
        HTML_TEMPLATE,
        logs=logs,
        total_scanned=total_scanned,
        total_flagged=total_flagged,
        uptime=uptime,
    )

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def run_dashboard():
    app.run(host="0.0.0.0", port=8080)

def start_dashboard():
    thread = threading.Thread(target=run_dashboard)
    thread.daemon = True
    thread.start()
