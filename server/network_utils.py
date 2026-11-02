import socket
import io
import os
import base64
import qrcode


def get_local_ip() -> str:
    """Detect the local LAN IP address of this machine quickly without blocking."""
    if os.environ.get("CLIPFLOW_IP"):
        return os.environ.get("CLIPFLOW_IP")

    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        # Using a LAN broadcast address doesn't attempt internet routing
        s.connect(('10.255.255.255', 1))
        detected = s.getsockname()[0]
        s.close()
        if detected and not detected.startswith('127.'):
            return detected
    except Exception:
        pass

    try:
        # Secondary fallback
        hostname = socket.gethostname()
        detected = socket.gethostbyname(hostname)
        if detected and not detected.startswith('127.'):
            return detected
    except Exception:
        pass

    return ip


def print_ascii_qr(url: str):
    """Print an ASCII QR code to the terminal console."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    print("\n" + "=" * 48)
    print(" SCAN THIS QR CODE WITH YOUR PHONE CAMERA:")
    print("=" * 48)
    qr.print_ascii(invert=True)
    print("=" * 48 + "\n")


def get_qr_base64(url: str) -> str:
    """Generate a base64 encoded PNG of the QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
