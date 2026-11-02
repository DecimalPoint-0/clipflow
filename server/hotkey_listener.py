import time
import threading
from typing import Callable, Optional
from pynput import keyboard
import pyperclip
from .notifier import notify


class HotkeyListener:
    def __init__(self, on_trigger_send: Callable[[str], None]):
        self.on_trigger_send = on_trigger_send
        self.keyboard_controller = keyboard.Controller()
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._is_running = False

    def _on_hotkey_pressed(self):
        """Called when Ctrl+Alt+C is pressed."""
        threading.Thread(target=self._capture_and_send, daemon=True).start()

    def _capture_and_send(self):
        try:
            # 1. Store previous clipboard to detect whether copy actually grabbed new text
            old_clip = ""
            try:
                old_clip = pyperclip.paste()
            except Exception:
                pass

            # 2. Release any currently held modifier keys to avoid interference
            self.keyboard_controller.release(keyboard.Key.ctrl)
            self.keyboard_controller.release(keyboard.Key.alt)
            time.sleep(0.04)

            # 3. Simulate Ctrl + C to copy whatever text is currently highlighted in active window
            with self.keyboard_controller.pressed(keyboard.Key.ctrl):
                self.keyboard_controller.press('c')
                self.keyboard_controller.release('c')

            # Give the active OS application time to copy into Windows clipboard
            time.sleep(0.08)

            # 4. Read the text
            new_clip = pyperclip.paste()
            if not new_clip:
                return

            print(f"\n[ClipFlow] Captured highlighted text: {new_clip[:50]!r}...")
            
            # 5. Broadcast to connected mobile devices
            self.on_trigger_send(new_clip)

            # Show quick confirmation
            preview = (new_clip[:60] + "...") if len(new_clip) > 60 else new_clip
            notify("ClipFlow - Sent to Phone", preview)

        except Exception as e:
            print(f"[ClipFlow Hotkey Error] {e}")

    def start(self):
        """Start listening for Ctrl+Alt+C in background."""
        if self._is_running:
            return

        hotkeys = {
            '<ctrl>+<alt>+c': self._on_hotkey_pressed,
            '<ctrl>+<alt>+<shift>+c': self._on_hotkey_pressed
        }

        self._listener = keyboard.GlobalHotKeys(hotkeys)
        self._listener.daemon = True
        self._listener.start()
        self._is_running = True
        print("[ClipFlow] Global hotkey active: Highlight text and press [Ctrl + Alt + C] to send to phone!")

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._is_running = False
