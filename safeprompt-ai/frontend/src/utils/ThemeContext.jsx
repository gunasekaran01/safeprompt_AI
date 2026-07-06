import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const THEME_STORAGE_KEY = 'safeprompt-ai-theme'
const VALID_THEMES = ['light', 'dark', 'system']

const ThemeContext = createContext(undefined)

function getStoredTheme() {
  if (typeof window === 'undefined') return 'system'
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  return VALID_THEMES.includes(stored) ? stored : 'system'
}

function getSystemPrefersDark() {
  if (typeof window === 'undefined' || !window.matchMedia) return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

/**
 * Provides theme state (light / dark / system) to the whole app.
 *
 * - Persists the user's explicit choice to localStorage.
 * - When set to "system", tracks the OS color-scheme preference live via
 *   a matchMedia change listener, so the UI updates without a reload.
 * - Applies/removes the `dark` class on <html>, which Tailwind's
 *   `darkMode: 'class'` strategy relies on.
 */
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getStoredTheme)
  const [systemPrefersDark, setSystemPrefersDark] = useState(getSystemPrefersDark)

  // Track OS-level preference changes while theme === 'system'
  useEffect(() => {
    if (!window.matchMedia) return undefined
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (event) => setSystemPrefersDark(event.matches)

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
    // Safari < 14 fallback
    mediaQuery.addListener(handleChange)
    return () => mediaQuery.removeListener(handleChange)
  }, [])

  const resolvedTheme = theme === 'system' ? (systemPrefersDark ? 'dark' : 'light') : theme

  // Apply the resolved theme to the document root
  useEffect(() => {
    const root = document.documentElement
    if (resolvedTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [resolvedTheme])

  // Persist the user's explicit selection (including "system")
  useEffect(() => {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme)
    } catch (error) {
      console.error('Failed to persist theme preference:', error)
    }
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const currentResolved = prev === 'system' ? (getSystemPrefersDark() ? 'dark' : 'light') : prev
      return currentResolved === 'dark' ? 'light' : 'dark'
    })
  }, [])

  const value = useMemo(
    () => ({
      theme,
      setTheme,
      toggleTheme,
      resolvedTheme,
      isDarkMode: resolvedTheme === 'dark',
    }),
    [theme, toggleTheme, resolvedTheme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

/**
 * Hook for consuming theme state. Must be used within a <ThemeProvider>.
 */
export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export default ThemeContext
