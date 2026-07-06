import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { supabase } from '../services/supabaseClient.js'
import { ADMIN_EMAIL } from '../utils/constants.js'

const AuthContext = createContext(undefined)

function toFriendlyAuthError(error) {
  if (!error) return 'Something went wrong. Please try again.'
  return error.message || 'Something went wrong. Please try again.'
}

/**
 * Provides authentication state (session/user) and actions (sign up,
 * login, logout, password reset) to the whole app, backed directly by
 * Supabase Auth via @supabase/supabase-js (see services/supabaseClient.js).
 * This backend's FastAPI app never sees passwords — apiClient.js attaches
 * the resulting access token to API requests as a Bearer header.
 *
 * - Session Persistence + Auto Login: on mount, restores any existing
 *   session from localStorage via supabase.auth.getSession(), so a
 *   refresh or new tab doesn't force a re-login.
 * - Subscribes to onAuthStateChange for every subsequent auth event
 *   (sign in, sign out, token refresh, password recovery), keeping
 *   `session`/`user` state — and every <ProtectedRoute> — in sync live.
 */
export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return
      setSession(data.session)
      setIsLoading(false)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      setIsLoading(false)
    })

    return () => {
      isMounted = false
      listener.subscription.unsubscribe()
    }
  }, [])

  const signUp = useCallback(async (email, password, name) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) throw new Error(toFriendlyAuthError(error))
    return data
  }, [])

  const login = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw new Error(toFriendlyAuthError(error))
    return data
  }, [])

  const logout = useCallback(async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw new Error(toFriendlyAuthError(error))
  }, [])

  const requestPasswordReset = useCallback(async (email) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    })
    if (error) throw new Error(toFriendlyAuthError(error))
  }, [])

  const updatePassword = useCallback(async (newPassword) => {
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    if (error) throw new Error(toFriendlyAuthError(error))
  }, [])

  const resendVerificationEmail = useCallback(async (email) => {
    const { error } = await supabase.auth.resend({
      type: 'signup',
      email,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
    })
    if (error) throw new Error(toFriendlyAuthError(error))
  }, [])

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      accessToken: session?.access_token ?? null,
      isAuthenticated: Boolean(session),
      // UI-gating only -- see ADMIN_EMAIL's doc comment in utils/constants.js.
      isAdmin: Boolean(
        session?.user?.email && session.user.email.toLowerCase() === ADMIN_EMAIL.toLowerCase()
      ),
      isLoading,
      signUp,
      login,
      logout,
      requestPasswordReset,
      updatePassword,
      resendVerificationEmail,
    }),
    [
      session,
      isLoading,
      signUp,
      login,
      logout,
      requestPasswordReset,
      updatePassword,
      resendVerificationEmail,
    ]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook for consuming auth state/actions. Must be used within an
 * <AuthProvider> (mounted once in main.jsx, mirroring ThemeContext.jsx).
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
