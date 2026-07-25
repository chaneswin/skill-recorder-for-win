from __future__ import annotations

import base64
import io

from mss import mss
from PIL import Image, ImageGrab


def _grab_screen() -> Image.Image:
    try:
        with mss() as sct:
            monitor = sct.monitors[0]
            raw = sct.grab(monitor)
            return Image.frombytes("RGB", raw.size, raw.rgb)
    except Exception:
        return ImageGrab.grab(all_screens=True).convert("RGB")


def capture_screen_b64(quality: int = 80, max_width: int = 1600) -> str | None:
    try:
        image = _grab_screen()
    except Exception:
        return None

    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize((max_width, int(image.height * ratio)), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
