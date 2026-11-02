import os
import sys

os.environ["CLIPFLOW_TEST"] = "1"

import unittest
from starlette.testclient import TestClient

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.app import app
from server.clipboard_mgr import clipboard_manager
from server.network_utils import get_local_ip, get_qr_base64


class TestClipFlow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        clipboard_manager.clear_history()

    def test_local_ip_detection(self):
        ip = get_local_ip()
        self.assertIsInstance(ip, str)
        self.assertTrue(len(ip) >= 7)  # At least 'x.x.x.x'

    def test_qr_code_generation(self):
        qr_b64 = get_qr_base64("http://192.168.1.5:5050")
        self.assertTrue(qr_b64.startswith("data:image/png;base64,"))

    def test_clipboard_manager_history(self):
        item = clipboard_manager.set_text("Hello World Test", source="test")
        self.assertEqual(item["text"], "Hello World Test")
        self.assertEqual(item["source"], "test")

        history = clipboard_manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["text"], "Hello World Test")

        clipboard_manager.clear_history()
        self.assertEqual(len(clipboard_manager.get_history()), 0)

    def test_api_info_endpoint(self):
        response = self.client.get("/api/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ip", data)
        self.assertIn("port", data)
        self.assertIn("qr_base64", data)
        self.assertIn("connected_clients", data)

    def test_api_send_and_history(self):
        test_snippet = "Offline Clipboard Sync 123"
        response = self.client.post("/api/send", json={"text": test_snippet, "source": "phone"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["item"]["text"], test_snippet)

        # Verify snippet appears in history
        hist_resp = self.client.get("/api/history")
        self.assertEqual(hist_resp.status_code, 200)
        history = hist_resp.json()["history"]
        self.assertTrue(any(h["text"] == test_snippet for h in history))

    def test_serve_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ClipFlow", response.text)


if __name__ == "__main__":
    unittest.main()
