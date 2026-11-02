# 📱 Setting Up 1-Tap "Highlight & Send" on iPhone (iOS)

Apple sandboxes iOS strictly, but using **Apple Shortcuts**, you can enable instant text sharing from **any** app (Safari, Notes, WhatsApp, Mail, etc.) directly into your PC's clipboard.

---

### Method A: Quick 2-Step iOS Shortcut (Recommended)

1. Open the **Shortcuts** app on your iPhone.
2. Tap the **`+`** icon in the top right to create a new Shortcut.
3. Tap **Shortcut Details** (the `(i)` info icon at the bottom or top) and toggle **"Show in Share Sheet"**.
4. In "Share Sheet Types", select **Text** and **URLs**.
5. Add the action: **"Get Contents of URL"**:
   - **URL**: `http://<YOUR_PC_IP>:5050/api/send` *(replace `<YOUR_PC_IP>` with your PC's IP, e.g. `192.168.1.15`)*
   - Tap **Show More**:
     - **Method**: `POST`
     - **Headers**: Add `Content-Type` $\to$ `application/json`
     - **Request Body**: Choose `JSON`
     - Tap **Add new field** $\to$ Text
       - Key: `text`
       - Value: Tap variable $\to$ select **Shortcut Input**
6. Rename the shortcut to **"Send to PC"** and choose a computer or lightning icon ⚡.
7. Tap **Done**.

#### How to use it:
* Highlight any text or sentence on your iPhone in any app.
* Tap **Share...**
* Tap **"Send to PC"**.
* **Done!** The text is instantly copied into your Windows clipboard and a notification appears on your computer screen.

---

### Method B: Install ClipFlow as a PWA (Zero Install)

1. Connect your iPhone to the same Wi-Fi or Hotspot as your PC.
2. Open Safari and navigate to `http://<YOUR_PC_IP>:5050` (or scan the QR code).
3. Tap the **Share** button at the bottom of Safari.
4. Scroll down and tap **"Add to Home Screen"**.
5. ClipFlow will now look and feel like a native app on your phone with instant WebSocket sync!
