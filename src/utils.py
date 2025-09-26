from __future__ import annotations

import base64
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


def slugify(text: str, max_length: int = 80) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\-\_\s]+", "", text)
    text = re.sub(r"[\s\_\-]+", "-", text)
    return text[:max_length].strip("-") or "screenshot"


def ensure_unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def image_to_data_url(image_path: Path) -> str:
    mime = "image/png"
    ext = image_path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        mime = "image/jpeg"
    elif ext == ".gif":
        mime = "image/gif"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def wait_for_file_stable(path: Path, timeout_seconds: float = 10.0, interval: float = 0.25) -> bool:
    deadline = time.time() + timeout_seconds
    last_size: Optional[int] = None
    while time.time() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(interval)
            continue
        if last_size is not None and size == last_size:
            return True
        last_size = size
        time.sleep(interval)
    return False


def timestamp_for_filename(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.now()
    return dt.strftime("%Y%m%d-%H%M%S")




