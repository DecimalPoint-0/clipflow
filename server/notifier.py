import subprocess
import threading
import sys
import os

try:
    import winsound
except ImportError:
    winsound = None


def _show_toast_ps(title: str, message: str):
    """Trigger a native Windows 10/11 Toast Notification using PowerShell in background."""
    if os.environ.get("CLIPFLOW_TEST") == "1":
        return

    safe_title = title.replace('"', '`"').replace("'", "''")
    safe_msg = message.replace('"', '`"').replace("'", "''")
    if len(safe_msg) > 120:
        safe_msg = safe_msg[:117] + "..."

    ps_script = f"""
    try {{
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>{safe_title}</text>
            <text>{safe_msg}</text>
        </binding>
    </visual>
</toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("ClipFlow").Show($toast)
    }} catch {{}}
    """

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        p = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        try:
            p.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            p.kill()
    except Exception:
        if winsound:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass


def notify(title: str, message: str):
    """Display a non-blocking Windows notification."""
    t = threading.Thread(target=_show_toast_ps, args=(title, message), daemon=True)
    t.start()
