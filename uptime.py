import time
import requests
import threading
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== CONFIG ====================
# මෙතනට ඔයාගේ URLs දාන්න
URLS_TO_MONITOR = [
    "https://uptime-xrrj.onrender.com",
    "https://wpms-uptime.hf.space",
    "https://wpms-wpmfun.hf.space",
    "https://wpms-wpms.hf.space",
    "https://youtubedl-skbk.onrender.com",
    "https://pornhub-nq7x.onrender.com",
    "https://sriconvert.onrender.com",
    # ඕනෙ තරම් links දාන්න පුළුවන්
]

CHECK_INTERVAL = 60    # සැම විනාඩියකම check කරයි (seconds)
TIMEOUT = 10           # request එකකට ඉවසීමේ කාලය (seconds)
PORT = int(os.environ.get("PORT", 10000))
# ===============================================

status_data = {}

def check_url(url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False

def monitor():
    global status_data
    while True:
        for url in URLS_TO_MONITOR:
            is_up = check_url(url)
            status_data[url] = {
                "status": "UP" if is_up else "DOWN",
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {url} -> {'✅ UP' if is_up else '❌ DOWN'}")
        time.sleep(CHECK_INTERVAL)

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uptime Monitor</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; background: #0f0f23; color: #fff; }}
        h1 {{ text-align: center; color: #00d4aa; }}
        .info {{ text-align: center; color: #888; margin-bottom: 30px; }}
        .site {{ background: #1a1a2e; padding: 18px; margin: 12px 0; border-radius: 10px; border-left: 4px solid #333; }}
        .site.up {{ border-left-color: #00d4aa; }}
        .site.down {{ border-left-color: #ff4757; }}
        .url {{ font-size: 16px; word-break: break-all; }}
        .badge {{ float: right; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        .up .badge {{ background: #00d4aa33; color: #00d4aa; }}
        .down .badge {{ background: #ff475733; color: #ff4757; }}
        .time {{ color: #666; font-size: 13px; margin-top: 6px; }}
        .clear {{ clear: both; }}
    </style>
</head>
<body>
    <h1>🌐 Uptime Monitor</h1>
    <div class="info">Checking every {CHECK_INTERVAL} seconds • {len(URLS_TO_MONITOR)} site(s) monitored</div>
"""
        for url, data in status_data.items():
            cls = "up" if data["status"] == "UP" else "down"
            html += f"""
    <div class="site {cls}">
        <span class="badge">{data["status"]}</span>
        <div class="url">{url}</div>
        <div class="clear"></div>
        <div class="time">🕐 Last checked: {data["last_checked"]}</div>
    </div>"""
        
        html += """
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print("🚀 Uptime Monitor Started!")
    print(f"📋 Monitoring {len(URLS_TO_MONITOR)} URL(s) every {CHECK_INTERVAL} seconds")
    
    # Background monitoring thread
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    
    # First check immediately
    for url in URLS_TO_MONITOR:
        is_up = check_url(url)
        status_data[url] = {
            "status": "UP" if is_up else "DOWN",
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {url} -> {'✅ UP' if is_up else '❌ DOWN'}")
    
    # Web server for Render
    print(f"🌐 Web server running on port {PORT}")
    server = HTTPServer(('0.0.0.0', PORT), StatusHandler)
    server.serve_forever()
