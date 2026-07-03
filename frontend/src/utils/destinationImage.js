/**
 * Builds a photo URL for any destination string (city, country, region —
 * whatever the user typed), with no API key required.
 *
 * Uses Unsplash's keyword-based "source" endpoint, which returns a
 * relevant, high-resolution photo for arbitrary search terms. Because it's
 * a redirect-based endpoint rather than a search API, it works instantly
 * for literally any destination without registration, quotas, or secrets.
 */

const FALLBACK_QUERY = 'travel,landmark,skyline';

function cleanDestination(destination) {
  if (!destination) return FALLBACK_QUERY;
  // "Delhi, India" -> "Delhi India travel" (keep it a simple keyword string)
  return destination
    .replace(/,/g, ' ')
    .trim()
    .split(/\s+/)
    .join(',');
}

/**
 * @param {string} destination - e.g. "Delhi, India" or "Paris"
 * @param {{ width?: number, height?: number }} [opts]
 * @returns {string} image URL
 */
export function getDestinationImageUrl(destination, opts = {}) {
  const { width = 1600, height = 900 } = opts;
  const keywords = cleanDestination(destination);
  return `https://source.unsplash.com/${width}x${height}/?${encodeURIComponent(keywords)},travel,landmark`;
}

/**
 * A smaller variant for cards/thumbnails.
 */
export function getDestinationThumbUrl(destination) {
  return getDestinationImageUrl(destination, { width: 640, height: 420 });
}
