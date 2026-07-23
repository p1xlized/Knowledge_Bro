from urllib.parse import urlparse


def fallback_name(url: str) -> str:
    """Extracts domain host as temporary title if name isn't provided."""
    parsed = urlparse(url)
    return parsed.netloc or "Untitled Content"
