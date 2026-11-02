// ClipFlow Frontend Client Logic
let socket = null;
let currentLatestText = "";
let allHistory = [];
let serverInfo = null;

// DOM Elements
const statusBadge = document.getElementById("statusBadge");
const statusText = document.getElementById("statusText");
const latestContent = document.getElementById("latestContent");
const latestMeta = document.getElementById("latestMeta");
const copyLatestBtn = document.getElementById("copyLatestBtn");
const copyBtnText = document.getElementById("copyBtnText");
const sendInput = document.getElementById("sendInput");
const sendBtn = document.getElementById("sendBtn");
const pasteBtn = document.getElementById("pasteBtn");
const historyList = document.getElementById("historyList");
const historyCount = document.getElementById("historyCount");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const searchInput = document.getElementById("searchInput");
const toast = document.getElementById("toast");
const toastMsg = document.getElementById("toastMsg");
const chimeAudio = document.getElementById("chimeAudio");

// Modals
const openQrBtn = document.getElementById("openQrBtn");
const closeQrBtn = document.getElementById("closeQrBtn");
const qrModal = document.getElementById("qrModal");
const qrImg = document.getElementById("qrImg");
const urlDisplay = document.getElementById("urlDisplay");

const openGuideBtn = document.getElementById("openGuideBtn");
const closeGuideBtn = document.getElementById("closeGuideBtn");
const guideModal = document.getElementById("guideModal");
const guideApiUrl = document.getElementById("guideApiUrl");

// Check if running on mobile
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
if (isMobile) {
  const hotkeyBanner = document.getElementById("hotkeyBanner");
  if (hotkeyBanner) hotkeyBanner.style.display = "none";
}

// Show Toast
function showToast(message) {
  toastMsg.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

// Fetch Server Info & QR Code
async function loadServerInfo() {
  try {
    const res = await fetch("/api/info");
    if (res.ok) {
      serverInfo = await res.json();
      qrImg.src = serverInfo.qr_base64;
      urlDisplay.textContent = serverInfo.url;
      if (guideApiUrl) {
        guideApiUrl.textContent = `${serverInfo.url}/api/send`;
      }
    }
  } catch (err) {
    console.warn("Could not load server info:", err);
  }
}

// Relative Time
function formatTimeAgo(timestamp) {
  if (!timestamp) return "just now";
  const seconds = Math.floor(Date.now() / 1000 - timestamp);
  if (seconds < 5) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const mins = Math.floor(seconds / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  return `${hours}h ago`;
}

// Update Active Clip Box
function updateLatestCard(item) {
  if (!item || !item.text) return;
  currentLatestText = item.text;
  latestContent.textContent = item.text;
  latestContent.classList.remove("empty");

  const sourceName = item.source === "pc" ? "PC" : "Phone";
  latestMeta.textContent = `${sourceName} • ${formatTimeAgo(item.timestamp)} • ${item.text.length} chars`;
}

// Render History
function renderHistory() {
  const query = searchInput.value.toLowerCase().trim();
  const filtered = allHistory.filter(item => 
    !query || (item.text && item.text.toLowerCase().includes(query))
  );

  historyCount.textContent = filtered.length;
  historyList.innerHTML = "";

  if (filtered.length === 0) {
    historyList.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 0.8rem; padding: 12px;">No clips</div>`;
    return;
  }

  filtered.forEach(item => {
    const div = document.createElement("div");
    div.className = "history-item";

    const textSpan = document.createElement("span");
    textSpan.className = "history-text";
    textSpan.textContent = item.preview || item.text;

    const metaSpan = document.createElement("div");
    metaSpan.className = "history-meta";

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = item.source || "pc";

    const time = document.createElement("span");
    time.textContent = formatTimeAgo(item.timestamp);

    metaSpan.appendChild(badge);
    metaSpan.appendChild(time);

    div.appendChild(textSpan);
    div.appendChild(metaSpan);

    // Clicking an item copies it
    div.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(item.text);
        updateLatestCard(item);
        showToast("Copied to clipboard");
      } catch (e) {
        showToast("Tap again to copy");
      }
    });

    historyList.appendChild(div);
  });
}

// WebSocket Connection
function connectWebSocket() {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${location.host}/ws`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    statusBadge.className = "status";
    statusText.textContent = "connected";
  };

  socket.onclose = () => {
    statusBadge.className = "status disconnected";
    statusText.textContent = "connecting";
    setTimeout(connectWebSocket, 2000);
  };

  socket.onerror = (err) => {
    console.error("WebSocket error:", err);
    socket.close();
  };

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "init") {
        allHistory = msg.history || [];
        if (msg.latest) {
          updateLatestCard(msg.latest);
        }
        renderHistory();
      } else if (msg.type === "new_clip") {
        const item = msg.item;
        if (item) {
          if (navigator.vibrate) {
            try { navigator.vibrate([20]); } catch (e) {}
          }
          try {
            chimeAudio.play().catch(() => {});
          } catch (e) {}

          updateLatestCard(item);
          if (!allHistory.some(h => h.id === item.id)) {
            allHistory.unshift(item);
          }
          renderHistory();
          showToast(`New clip from ${item.source.toUpperCase()}`);
        }
      } else if (msg.type === "history_cleared") {
        allHistory = [];
        latestContent.textContent = "No text received yet.";
        latestContent.classList.add("empty");
        latestMeta.textContent = "waiting";
        currentLatestText = "";
        renderHistory();
        showToast("History cleared");
      }
    } catch (e) {
      console.error("Error processing WebSocket message", e);
    }
  };
}

// Copy Latest to Clipboard
copyLatestBtn.addEventListener("click", async () => {
  if (!currentLatestText) {
    showToast("No text to copy");
    return;
  }
  try {
    await navigator.clipboard.writeText(currentLatestText);
    copyBtnText.textContent = "Copied!";
    showToast("Copied to clipboard");
    setTimeout(() => {
      copyBtnText.textContent = "Copy to clipboard";
    }, 1800);
  } catch (err) {
    const ta = document.createElement("textarea");
    ta.value = currentLatestText;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    showToast("Copied");
  }
});

// Send Text to PC
async function sendTextToPC(text) {
  if (!text.trim()) {
    showToast("Enter some text");
    return;
  }

  const payload = {
    text: text.trim(),
    source: isMobile ? "phone" : "client"
  };

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: "send",
      ...payload
    }));
    sendInput.value = "";
    showToast("Sent to PC");
  } else {
    try {
      const res = await fetch("/api/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        sendInput.value = "";
        showToast("Sent to PC");
      } else {
        showToast("Failed to send");
      }
    } catch (e) {
      showToast("Network error");
    }
  }
}

sendBtn.addEventListener("click", () => {
  sendTextToPC(sendInput.value);
});

// Paste & Send
pasteBtn.addEventListener("click", async () => {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      sendInput.value = text;
      sendTextToPC(text);
    } else {
      showToast("Clipboard empty");
    }
  } catch (e) {
    sendInput.focus();
    showToast("Paste into box");
  }
});

// Clear History
clearHistoryBtn.addEventListener("click", async () => {
  if (confirm("Clear clipboard history?")) {
    try {
      await fetch("/api/history", { method: "DELETE" });
    } catch (e) {
      console.error(e);
    }
  }
});

// Search
searchInput.addEventListener("input", renderHistory);

// Modals
openQrBtn.addEventListener("click", () => qrModal.classList.add("active"));
closeQrBtn.addEventListener("click", () => qrModal.classList.remove("active"));
qrModal.addEventListener("click", (e) => {
  if (e.target === qrModal) qrModal.classList.remove("active");
});

openGuideBtn.addEventListener("click", () => guideModal.classList.add("active"));
closeGuideBtn.addEventListener("click", () => guideModal.classList.remove("active"));
guideModal.addEventListener("click", (e) => {
  if (e.target === guideModal) guideModal.classList.remove("active");
});

// Web Share Target (?text=... or ?url=...)
function handleShareTarget() {
  const urlParams = new URLSearchParams(window.location.search);
  const sharedText = urlParams.get("text") || urlParams.get("url") || urlParams.get("title");
  if (sharedText) {
    sendTextToPC(sharedText);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}

// Service Worker
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js").catch(console.error);
}

// Init
window.addEventListener("DOMContentLoaded", () => {
  loadServerInfo();
  connectWebSocket();
  handleShareTarget();
});
