# clipflow

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/your-username/clipflow/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/clipflow/actions)

Fast, minimalist, 100% offline cross-device clipboard sync between Windows PC, Android, and iOS over local Wi-Fi or mobile hotspot.

---

## Features

- **100% Offline & Private:** Operates purely on your local network (LAN) or mobile hotspot. No cloud relays, third-party servers, or telemetry.
- **Highlight & Send on PC:** Select any text in Windows and press `Ctrl + Alt + C` to broadcast it straight to connected phones.
- **Highlight & Send on Mobile:**
  - **Android:** Share directly via native Share menu / Web Share Target.
  - **iOS:** Highlight text $\to$ Share $\to$ tap custom "Send to PC" iOS Shortcut.
- **Instant Windows Clipboard Injection:** Received snippets are automatically written to your Windows clipboard with a native notification toast. Just press `Ctrl + V`.
- **Zero-Typing QR Pairing:** Startup displays an ASCII terminal QR code and web code for instant mobile pairing.
- **Bi-directional WebSockets:** Real-time push under 15ms latency.
- **Minimalist Web Companion:** Clean, dark-mode, non-distracting PWA interface with search and clipboard history.

---

## Quickstart

### Prerequisites
- Python 3.10 or higher.
- Both devices connected to the **same local Wi-Fi** or **Phone Hotspot**.

### Installation

```bash
git clone https://github.com/<your-username>/clipflow.git
cd clipflow
pip install -r requirements.txt
```

### Run

```bash
python run.py
```

1. The terminal will display an **ASCII QR Code** and local network URL (e.g. `http://192.168.1.15:5050`).
2. Scan the QR code with your phone camera.
3. You're connected!

---

## Usage

### PC to Phone
1. Highlight any text in any Windows app (browser, editor, PDF, Word).
2. Press `Ctrl + Alt + C`.
3. Your phone receives it immediately with a one-tap **Copy to clipboard** button.

### Phone to PC
- **From Web App:** Paste into the input area and tap **Send**.
- **From Any App (Android):** Add to Home Screen in Chrome, highlight text anywhere, tap **Share $\to$ ClipFlow**.
- **From Any App (iOS):** Follow the 2-step [iOS Shortcut Guide](shortcuts/iOS_Shortcut_Guide.md) to add a 1-tap "Send to PC" button to your iOS Share Sheet.
- Text is automatically copied into your PC clipboard—just press `Ctrl + V`.

---

## Standalone Executable (.exe)

You can compile ClipFlow into a standalone Windows binary so others can run it without Python installed:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --add-data "web;web" --name "ClipFlow" run.py
```

The compiled output will be in the `dist/ClipFlow` folder.

---

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## License

[MIT License](LICENSE)
