import hashlib
from datetime import datetime, timezone
from typing import Optional


def generate_filename(value: str, prefix: str = "file", extension: str = "mp3") -> str:
    """
    Generates a unique, filesystem-safe filename using a UTC timestamp and an MD5 hash.

    Example output: "audio_20260723_142035_a1b2c3d4.mp3"
    """
    # 1. UTC Timestamp formatted as YYYYMMDD_HHMMSS
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 2. Short 8-character hash from the input value (URL, text, content string)
    hash_object = hashlib.md5(value.encode("utf-8"))
    short_hash = hash_object.hexdigest()[:8]

    # 3. Clean up leading dots from extension if present (.mp3 -> mp3)
    ext = extension.lstrip(".")

    return f"{prefix}_{timestamp}_{short_hash}.{ext}"
