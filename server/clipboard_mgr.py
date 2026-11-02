import time
import uuid
from typing import List, Dict, Optional
import pyperclip


class ClipboardManager:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: List[Dict] = []
        self._last_set_text = ""

    def get_text(self) -> str:
        """Read the current text from system clipboard."""
        try:
            return pyperclip.paste() or ""
        except Exception as e:
            print(f"[Clipboard] Error reading clipboard: {e}")
            return ""

    def set_text(self, text: str, source: str = "local") -> Dict:
        """Write text to system clipboard and record in history."""
        if not text:
            return {}

        self._last_set_text = text
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"[Clipboard] Error writing clipboard: {e}")

        item = {
            "id": str(uuid.uuid4())[:8],
            "text": text,
            "source": source,
            "timestamp": time.time(),
            "preview": (text[:80] + "...") if len(text) > 80 else text
        }

        # Deduplicate recent consecutive identical text
        if self.history and self.history[0]["text"] == text:
            self.history[0]["timestamp"] = time.time()
            return self.history[0]

        self.history.insert(0, item)
        if len(self.history) > self.max_history:
            self.history.pop()

        return item

    def get_history(self) -> List[Dict]:
        """Return clipboard history."""
        return self.history

    def clear_history(self):
        """Clear stored history."""
        self.history.clear()


clipboard_manager = ClipboardManager()
