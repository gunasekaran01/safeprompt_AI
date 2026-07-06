import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { formatCount, formatRelativeTime, formatScore, truncateText } from './formatters.js'

describe('formatRelativeTime', () => {
  const NOW = new Date('2026-07-05T12:00:00.000Z')

  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(NOW)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows "Just now" for anything under a minute old', () => {
    expect(formatRelativeTime(new Date(NOW.getTime() - 30_000).toISOString())).toBe('Just now')
  })

  it('shows minutes for under an hour', () => {
    expect(formatRelativeTime(new Date(NOW.getTime() - 5 * 60_000).toISOString())).toBe('5m ago')
  })

  it('shows hours for under a day', () => {
    expect(formatRelativeTime(new Date(NOW.getTime() - 3 * 3_600_000).toISOString())).toBe('3h ago')
  })

  it('shows days for under a week', () => {
    expect(formatRelativeTime(new Date(NOW.getTime() - 2 * 86_400_000).toISOString())).toBe('2d ago')
  })

  it('falls back to a locale date for a week or older', () => {
    const eightDaysAgo = new Date(NOW.getTime() - 8 * 86_400_000).toISOString()
    expect(formatRelativeTime(eightDaysAgo)).not.toMatch(/ago$/)
  })
})

describe('truncateText', () => {
  it('returns short text unchanged', () => {
    expect(truncateText('hello', 80)).toBe('hello')
  })

  it('returns falsy input unchanged rather than throwing', () => {
    expect(truncateText('', 10)).toBe('')
    expect(truncateText(undefined, 10)).toBeUndefined()
  })

  it('truncates long text and appends an ellipsis', () => {
    const long = 'a'.repeat(100)
    const result = truncateText(long, 20)
    expect(result.endsWith('…')).toBe(true)
    expect(result.length).toBeLessThanOrEqual(21)
  })

  it('breaks on a word boundary when one exists past 60% of maxLength', () => {
    const text = 'The quick brown fox jumps over the lazy dog'
    const result = truncateText(text, 20)
    expect(result).not.toMatch(/\s…$/) // shouldn't cut mid-word leaving a dangling space
    expect(result.endsWith('…')).toBe(true)
  })
})

describe('formatScore', () => {
  it('rounds to the nearest whole number', () => {
    expect(formatScore(87.4)).toBe(87)
    expect(formatScore(87.6)).toBe(88)
    expect(formatScore(0)).toBe(0)
    expect(formatScore(100)).toBe(100)
  })
})

describe('formatCount', () => {
  it('adds thousands separators', () => {
    expect(formatCount(1284)).toBe('1,284')
    expect(formatCount(0)).toBe('0')
    expect(formatCount(999)).toBe('999')
    expect(formatCount(1000000)).toBe('1,000,000')
  })
})
