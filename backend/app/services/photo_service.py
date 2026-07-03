"""
Destination photo lookup via the Unsplash Search API.

Design notes:
- Unsplash's old unauthenticated `source.unsplash.com` redirect endpoint was
  shut down in 2021. This uses the real, current Search Photos API
  (https://api.unsplash.com/search/photos), which requires an Access Key.
- The key lives only on the server (UNSPLASH_ACCESS_KEY env var) and is
  never sent to the frontend.
- Results are cached in-memory per normalized destination string with a
  24h TTL, so repeat views of the same trip/destination don't burn API
  quota. Unsplash's free "Demo" tier allows 50 requests/hour; a simple
  cache keeps normal usage well under that even with many users hitting
  popular destinations.
- If no key is configured, or the request fails, or Unsplash returns no
  results, this returns None so the caller (router) can respond with a
  clear "no photo available" payload and the frontend can fall back to a
  themed gradient instead of a broken image.
"""

import time
import httpx
from app.config import get_settings

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

# destination (normalized) -> {"data": {...}, "expires_at": float}
_cache: dict[str, dict] = {}
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def _normalize(destination: str) -> str:
    return " ".join(destination.strip().lower().split())


def _cache_get(key: str):
    entry = _cache.get(key)
    if not entry:
        return None
    if entry["expires_at"] < time.time():
        _cache.pop(key, None)
        return None
    return entry["data"]


def _cache_set(key: str, data: dict):
    _cache[key] = {"data": data, "expires_at": time.time() + CACHE_TTL_SECONDS}


def get_destination_photo(destination: str) -> dict | None:
    """
    Returns a dict like:
      {
        "url": "https://images.unsplash.com/...",       # full-size, for hero banners
        "thumb_url": "https://images.unsplash.com/...",  # small, for cards
        "alt_description": "...",
        "photographer": "Jane Doe",
        "photographer_url": "https://unsplash.com/@jane",
        "unsplash_url": "https://unsplash.com/photos/...",
      }
    or None if unavailable (missing key, no results, or request failure).
    Unsplash's guidelines require attributing the photographer and linking
    back to Unsplash, so both are included for the frontend to display.
    """
    settings = get_settings()
    access_key = getattr(settings, "UNSPLASH_ACCESS_KEY", "") or ""
    if not access_key or not destination:
        return None

    cache_key = _normalize(destination)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    query = f"{destination} travel landmark"
    try:
        response = httpx.get(
            UNSPLASH_SEARCH_URL,
            params={
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {access_key}"},
            timeout=6.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    results = payload.get("results") or []
    if not results:
        return None

    photo = results[0]
    urls = photo.get("urls", {})
    user = photo.get("user", {})

    data = {
        "url": urls.get("regular") or urls.get("full") or urls.get("raw"),
        "thumb_url": urls.get("small") or urls.get("thumb"),
        "alt_description": photo.get("alt_description") or destination,
        "photographer": user.get("name", "Unknown"),
        "photographer_url": (user.get("links") or {}).get("html", "https://unsplash.com"),
        "unsplash_url": (photo.get("links") or {}).get("html", "https://unsplash.com"),
    }

    if not data["url"]:
        return None

    _cache_set(cache_key, data)
    return data
