/**
 * Formats an ISO timestamp as a short relative time string (e.g. "5m ago",
 * "3h ago", "2d ago"). Falls back to a locale date string for anything
 * older than a week.
 */
export function formatRelativeTime(isoTimestamp) {
  const then = new Date(isoTimestamp).getTime()
  const now = Date.now()
  const diffSeconds = Math.max(0, Math.floor((now - then) / 1000))

  if (diffSeconds < 60) return 'Just now'
  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`

  return new Date(isoTimestamp).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/**
 * Truncates text to a maximum length, breaking on a word boundary where
 * possible and appending an ellipsis.
 */
export function truncateText(text, maxLength = 80) {
  if (!text || text.length <= maxLength) return text
  const truncated = text.slice(0, maxLength)
  const lastSpace = truncated.lastIndexOf(' ')
  return `${lastSpace > maxLength * 0.6 ? truncated.slice(0, lastSpace) : truncated}…`
}

/**
 * Formats a 0-100 safety score for display, rounding to a whole number.
 */
export function formatScore(score) {
  return Math.round(score)
}

/**
 * Formats a large count with thousands separators (e.g. 1284 -> "1,284").
 */
export function formatCount(count) {
  return new Intl.NumberFormat('en-US').format(count)
}
