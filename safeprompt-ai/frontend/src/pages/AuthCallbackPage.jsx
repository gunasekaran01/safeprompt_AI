import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiLoader } from 'react-icons/fi'
import { useAuth } from '../utils/AuthContext.jsx'

/**
 * Landing page for Supabase's email verification links (signUp's
 * emailRedirectTo — see AuthContext.signUp). @supabase/supabase-js's
 * detectSessionInUrl (services/supabaseClient.js) automatically exchanges
 * the URL's token for a session on load; this page just waits for that
 * to finish (AuthContext.isLoading) and then routes onward.
 */
function AuthCallbackPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoading) return
    navigate(isAuthenticated ? '/dashboard' : '/login', { replace: true })
  }, [isAuthenticated, isLoading, navigate])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-slate-500 dark:text-slate-400">
      <FiLoader className="h-6 w-6 animate-spin text-brand-600" />
      <p className="text-sm">Verifying…</p>
    </div>
  )
}

export default AuthCallbackPage
