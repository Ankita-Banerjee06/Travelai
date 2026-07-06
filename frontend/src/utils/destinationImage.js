import { useEffect, useState } from 'react';
import client from '../api/client';

/**
 * Fetches a real destination photo. Tries our backend (which calls the
 * Unsplash Search API server-side and caches results) first. If Unsplash
 * has no match — common for small towns/villages that aren't in its
 * curated stock catalog — falls back to Wikimedia Commons, which has much
 * broader geographic coverage since it's sourced from Wikipedia uploads.
 * Falls back to a themed gradient — never a broken image — if neither
 * source has anything.
 */

// A handful of moody, cinematic gradient pairs to rotate through for the
// fallback state, so different destinations still feel distinct.
const FALLBACK_GRADIENTS = [
  'linear-gradient(135deg, #0f2027 0%, #2c5364 100%)',
  'linear-gradient(135deg, #232526 0%, #414345 100%)',
  'linear-gradient(135deg, #1a2980 0%, #26d0ce 100%)',
  'linear-gradient(135deg, #360033 0%, #0b8793 100%)',
  'linear-gradient(135deg, #093028 0%, #237a57 100%)',
  'linear-gradient(135deg, #3a1c71 0%, #d76d77 60%, #ffaf7b 100%)',
  'linear-gradient(135deg, #16222a 0%, #3a6073 100%)',
];

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

/**
 * Deterministic fallback gradient for a destination string, used whenever
 * no photo is available (no API key configured, no results, or the
 * request failed).
 */
export function getFallbackGradient(destination) {
  if (!destination) return FALLBACK_GRADIENTS[0];
  const idx = hashString(destination) % FALLBACK_GRADIENTS.length;
  return FALLBACK_GRADIENTS[idx];
}

// Simple in-memory cache shared across components in this session, so
// navigating between pages (or rendering many TripCards) doesn't re-fire
// a request per mount for the same destination.
const inMemoryCache = new Map();
const inFlight = new Map();

/**
 * Wikimedia Commons fallback — free, no API key, no rate-limit setup
 * required. Searches Commons for an image matching the destination name
 * and returns it in the same shape as the Unsplash photo object, minus
 * the photographer credit (Wikimedia images aren't Unsplash photos, so we
 * don't show the "Photo by ... on Unsplash" credit line for these).
 */
async function fetchWikimediaPhoto(destination) {
  try {
    const searchUrl =
      `https://commons.wikimedia.org/w/api.php?action=query&list=search` +
      `&srsearch=${encodeURIComponent(destination)}&srnamespace=6` +
      `&srlimit=1&format=json&origin=*`;

    const searchRes = await fetch(searchUrl);
    if (!searchRes.ok) return null;
    const searchData = await searchRes.json();

    const fileTitle = searchData?.query?.search?.[0]?.title;
    if (!fileTitle) return null;

    const infoUrl =
      `https://commons.wikimedia.org/w/api.php?action=query` +
      `&titles=${encodeURIComponent(fileTitle)}&prop=imageinfo` +
      `&iiprop=url&iiurlwidth=800&format=json&origin=*`;

    const infoRes = await fetch(infoUrl);
    if (!infoRes.ok) return null;
    const infoData = await infoRes.json();

    const pages = infoData?.query?.pages;
    const page = pages ? Object.values(pages)[0] : null;
    const info = page?.imageinfo?.[0];
    const imageUrl = info?.thumburl || info?.url;
    if (!imageUrl) return null;

    return {
      available: true,
      thumb_url: imageUrl,
      photographer: null,
      photographer_url: null,
      source: 'wikimedia',
    };
  } catch {
    return null;
  }
}

async function fetchDestinationPhoto(destination) {
  const key = destination.trim().toLowerCase();
  if (inMemoryCache.has(key)) return inMemoryCache.get(key);
  if (inFlight.has(key)) return inFlight.get(key);

  const promise = client
    .get('/photos/destination', { params: { destination } })
    .then((res) => (res.data?.available ? res.data : null))
    .catch(() => null)
    .then(async (data) => {
      if (data) return data;
      // Unsplash had nothing — try Wikimedia Commons before giving up.
      const wikiPhoto = await fetchWikimediaPhoto(destination);
      return wikiPhoto || null;
    })
    .then((data) => {
      inMemoryCache.set(key, data);
      return data;
    })
    .finally(() => {
      inFlight.delete(key);
    });

  inFlight.set(key, promise);
  return promise;
}

/**
 * React hook: returns { photo, loading, fallbackGradient }.
 * `photo` is null until loaded (or if unavailable from every source) —
 * always check it before rendering an <img>/background-image, and use
 * fallbackGradient as the background in the meantime / on failure.
 */
export function useDestinationPhoto(destination) {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    if (!destination) {
      setPhoto(null);
      setLoading(false);
      return undefined;
    }
    setLoading(true);
    fetchDestinationPhoto(destination).then((data) => {
      if (!cancelled) {
        setPhoto(data);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [destination]);

  return { photo, loading, fallbackGradient: getFallbackGradient(destination) };
}