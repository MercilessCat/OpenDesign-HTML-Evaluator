"""Shared image utilities for vision model integration."""

import base64
import io

from PIL import Image


def encode_screenshot_base64(path: str, max_side: int = 1280) -> str | None:
    """Read a screenshot PNG, optionally resize, return base64 string.

    Returns None if the file doesn't exist or can't be read.
    """
    try:
        img = Image.open(path)
        w, h = img.size
        if max(w, h) > max_side:
            ratio = max_side / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None
