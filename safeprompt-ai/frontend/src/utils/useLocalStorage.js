import { useCallback, useEffect, useState } from 'react'

/**
 * Persists a piece of state to localStorage under the given key.
 *
 * Used throughout the app for lightweight, client-only preferences (theme,
 * compact mode, etc.) that don't need to round-trip through the backend.
 *
 * @param {string} key - localStorage key.
 * @param {*} initialValue - value used when nothing is stored yet.
 * @returns {[*, Function, Function]} [value, setValue, remove]
 */
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    if (typeof window === 'undefined') return initialValue
    try {
      const item = window.localStorage.getItem(key)
      return item !== null ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Failed to read localStorage key "${key}":`, error)
      return initialValue
    }
  })

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error(`Failed to write localStorage key "${key}":`, error)
    }
  }, [key, value])

  const remove = useCallback(() => {
    try {
      window.localStorage.removeItem(key)
      setValue(initialValue)
    } catch (error) {
      console.error(`Failed to remove localStorage key "${key}":`, error)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  return [value, setValue, remove]
}

export default useLocalStorage
