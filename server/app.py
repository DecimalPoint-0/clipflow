import asyncio
import os
import json
from pathlib import Path
from typing import List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .clipboard_mgr import clipboard_manager
from .notifier import notify
from .network_utils import get_local_ip, get_qr_base64

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="ClipFlow API", version="1.0.0")

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, data: dict, exclude: WebSocket = None):
        payload = json.dumps(data)
        dead = set()
        for conn in self.active_connections:
            if conn != exclude:
                try:
                    await conn.send_text(payload)
                except Exception:
                    dead.add(conn)
        for dead_conn in dead:
            self.active_connections.discard(dead_conn)

manager = ConnectionManager()
loop_holder = {"loop": None}


class SendPayload(BaseModel):
    text: str
    source: str = "phone"


@app.on_event("startup")
async def startup_event():
    loop_holder["loop"] = asyncio.get_running_loop()


def broadcast_from_hotkey(text: str):
    """Callback used by the Windows hotkey listener to push captured text."""
    item = clipboard_manager.set_text(text, source="pc")
    loop = loop_holder.get("loop")
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "type": "new_clip",
                "item": item
            }),
            loop
        )


@app.get("/api/info")
async def get_server_info():
    ip = get_local_ip()
    port = int(os.environ.get("CLIPFLOW_PORT", 5050))
    url = f"http://{ip}:{port}"
    qr_b64 = get_qr_base64(url)
    return {
        "ip": ip,
        "port": port,
        "url": url,
        "qr_base64": qr_b64,
        "connected_clients": len(manager.active_connections)
    }


@app.get("/api/history")
async def get_history():
    return {
        "history": clipboard_manager.get_history()
    }


@app.post("/api/send")
async def receive_snippet(payload: SendPayload):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # 1. Update Windows Clipboard
    item = clipboard_manager.set_text(text, source=payload.source)

    # 2. Show Windows Toast Notification
    preview = (text[:80] + "...") if len(text) > 80 else text
    notify("ClipFlow - Copied to PC Clipboard", preview)

    # 3. Broadcast to all other connected clients
    await manager.broadcast({
        "type": "new_clip",
        "item": item
    })

    return {
        "status": "success",
        "copied_to_pc": True,
        "item": item
    }


@app.delete("/api/history")
async def clear_history():
    clipboard_manager.clear_history()
    await manager.broadcast({"type": "history_cleared"})
    return {"status": "success"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send current history immediately on connect
        await websocket.send_text(json.dumps({
            "type": "init",
            "history": clipboard_manager.get_history(),
            "latest": clipboard_manager.history[0] if clipboard_manager.history else None
        }))

        while True:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                msg_type = msg.get("type")

                if msg_type == "send":
                    text = msg.get("text", "").strip()
                    source = msg.get("source", "phone")
                    if text:
                        # Copy to PC clipboard
                        item = clipboard_manager.set_text(text, source=source)
                        
                        # Notify Windows user
                        preview = (text[:80] + "...") if len(text) > 80 else text
                        notify(f"ClipFlow - From {source.capitalize()}", preview)

                        # Broadcast to all clients
                        await manager.broadcast({
                            "type": "new_clip",
                            "item": item
                        })
            except Exception as e:
                print(f"[WebSocket Error parsing message] {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# Mount Web directory for PWA UI
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

@app.get("/")
async def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>ClipFlow Web UI initializing...</h1>")
