import { useEffect, useState } from 'react'

const STORAGE_KEY = 'safeprompt-color-scheme'

/**
 * Tracks and persists the app's dark/light color scheme.
 *
 * Resolution order:
 * 1. A previously saved user preference in localStorage.
 * 2. The OS-level `prefers-color-scheme` media query.
 *
 * The resolved value is applied as a `dark` class on <html> (Tailwind's
 * `darkMode: 'class'` strategy) any time it changes.
 */
export function useDarkMode() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = window.localStorage?.getItem(STORAGE_KEY)
    if (saved === 'dark') return true
    if (saved === 'light') return false
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
  })

  useEffect(() => {
    const root = document.documentElement
    if (isDarkMode) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    window.localStorage?.setItem(STORAGE_KEY, isDarkMode ? 'dark' : 'light')
  }, [isDarkMode])

  const toggleDarkMode = () => setIsDarkMode((prev) => !prev)

  return { isDarkMode, toggleDarkMode }
}
