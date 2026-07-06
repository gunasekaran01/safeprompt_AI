import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { supabase } from '../services/supabaseClient.js'
import apiClient from '../services/apiClient.js'
import { getMyProfile } from '../services/profileService.js'

const AuthContext = createContext(undefined)

/**
 * Provides authentication state and actions to the whole app.
 *
 * - On mount, fetches the current session (if any) so a refreshed page
 *   restores a logged-in user automatically (session persistence /
 *   auto-login), then subscribes to further auth state changes (sign in,
 *   sign out, token refresh, password recovery).
 * - Exposes signUp / signIn / signOut / resetPassword / updatePassword,
 *   each throwing on failure so calling components can catch and display
 *   the error message.
 * - Once a session exists, also fetches GET /api/auth/me (for `isAdmin`
 *   — computed server-side, never trust a client-side email comparison
 *   for this) and GET /api/profiles/me (for `profile`, i.e. display
 *   name/avatar — used by Navbar's user menu). Both are exposed here,
 *   in one place, rather than each component fetching its own copy.
 *   `refreshProfile()` lets ProfileForm.jsx re-fetch after a save so the
 *   Navbar reflects an edited name/avatar immediately.
 */
export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAdmin, setIsAdmin] = useState(false)
  const [profile, setProfile] = useState(null)

  const refreshProfile = useCallback(async () => {
    try {
      const nextProfile = await getMyProfile()
      setProfile(nextProfile)
      return nextProfile
    } catch {
      // Non-fatal: the Navbar/AdminPage just fall back to email-only
      // display if this fails. The auth session itself is unaffected.
      return null
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    supabase.auth.getSession().then(({ data }) => {
      if (isMounted) {
        setSession(data.session)
        setIsLoading(false)
      }
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, newSession) => {
      if (isMounted) {
        setSession(newSession)
        setIsLoading(false)
      }
    })

    return () => {
      isMounted = false
      subscription.unsubscribe()
    }
  }, [])

  useEffect(() => {
    if (!session?.user) {
      setIsAdmin(false)
      setProfile(null)
      return
    }

    let isCancelled = false

    apiClient
      .get('/auth/me')
      .then((response) => {
        if (!isCancelled) setIsAdmin(Boolean(response.data?.is_admin))
      })
      .catch(() => {
        if (!isCancelled) setIsAdmin(false)
      })

    refreshProfile()

    return () => {
      isCancelled = true
    }
  }, [session?.user, refreshProfile])

  const signUp = useCallback(async (email, password, name) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name },
      },
    })
    if (error) throw error
    return data
  }, [])

  const signIn = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return data
  }, [])

  const signOut = useCallback(async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }, [])

  const resetPassword = useCallback(async (email) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    })
    if (error) throw error
  }, [])

  const updatePassword = useCallback(async (newPassword) => {
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    if (error) throw error
  }, [])

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      isAuthenticated: Boolean(session?.user),
      isLoading,
      isAdmin,
      profile,
      refreshProfile,
      signUp,
      signIn,
      signOut,
      resetPassword,
      updatePassword,
    }),
    [
      session,
      isLoading,
      isAdmin,
      profile,
      refreshProfile,
      signUp,
      signIn,
      signOut,
      resetPassword,
      updatePassword,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook for consuming auth state. Must be used within an <AuthProvider>.
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
