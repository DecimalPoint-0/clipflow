import sys
import os
import uvicorn
from server.network_utils import get_local_ip, print_ascii_qr
from server.hotkey_listener import HotkeyListener
from server.app import app, broadcast_from_hotkey

PORT = 5050
os.environ["CLIPFLOW_PORT"] = str(PORT)


def main():
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}"

    print("=" * 60)
    print("   ⚡ ClipFlow - Offline Cross-Device Clipboard Sync ⚡   ")
    print("=" * 60)
    print(f" PC Server Running At : {url}")
    print(f" Local Machine IP     : {local_ip}")
    print(f" Shortcut to Send     : Highlight text & press [Ctrl + Alt + C]")
    print("=" * 60)

    # Print ASCII QR Code for instant phone pairing
    try:
        print_ascii_qr(url)
    except Exception as e:
        print(f"Note: To pair your phone, open this URL in your mobile browser:\n  --> {url}\n")

    # Start the global hotkey hook in background
    hotkey = HotkeyListener(on_trigger_send=broadcast_from_hotkey)
    try:
        hotkey.start()
    except Exception as e:
        print(f"[Warning] Could not register global hotkey hook: {e}")

    print("[Ready] Waiting for devices to connect...")
    print("Press Ctrl+C in this terminal to stop.\n")

    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
    except KeyboardInterrupt:
        print("\n[ClipFlow] Shutting down...")
    finally:
        hotkey.stop()


if __name__ == "__main__":
    main()
