import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FiAlertTriangle, FiCheckCircle, FiKey, FiLoader } from 'react-icons/fi'
import AuthLayout from '../components/Auth/AuthLayout.jsx'
import { useAuth } from '../utils/AuthContext.jsx'

const MIN_PASSWORD_LENGTH = 6

function ResetPasswordPage() {
  const { isAuthenticated, isLoading, updatePassword } = useAuth()
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`)
      return
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)
    try {
      await updatePassword(password)
      setIsSuccess(true)
      window.setTimeout(() => navigate('/dashboard', { replace: true }), 1800)
    } catch (err) {
      setError(err.message || 'Failed to update your password. Please request a new reset link.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <AuthLayout title="Reset your password">
        <div className="flex justify-center py-6">
          <FiLoader className="h-6 w-6 animate-spin text-brand-600" />
        </div>
      </AuthLayout>
    )
  }

  // The Supabase recovery link establishes a temporary session automatically.
  // If there's no session by the time loading finishes, the link was
  // invalid, expired, or already used.
  if (!isAuthenticated) {
    return (
      <AuthLayout title="Invalid or expired link">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-risk-critical/10 text-risk-critical">
            <FiAlertTriangle className="h-6 w-6" />
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            This password reset link is invalid or has expired. Please request a new one.
          </p>
          <Link to="/forgot-password" className="btn-primary mt-2">
            Request New Link
          </Link>
        </div>
      </AuthLayout>
    )
  }

  if (isSuccess) {
    return (
      <AuthLayout title="Password updated">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-risk-safe/10 text-risk-safe">
            <FiCheckCircle className="h-6 w-6" />
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Your password has been updated. Redirecting you to the dashboard…
          </p>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Set a new password" subtitle="Choose a strong password for your account">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-sm text-risk-critical">
            <FiAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <div>
          <label htmlFor="new-password" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
            New Password
          </label>
          <input
            id="new-password"
            type="password"
            required
            autoComplete="new-password"
            minLength={MIN_PASSWORD_LENGTH}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>

        <div>
          <label htmlFor="confirm-new-password" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Confirm New Password
          </label>
          <input
            id="confirm-new-password"
            type="password"
            required
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
          {isSubmitting ? (
            <>
              <FiLoader className="h-4 w-4 animate-spin" /> Updating…
            </>
          ) : (
            <>
              <FiKey className="h-4 w-4" /> Update Password
            </>
          )}
        </button>
      </form>
    </AuthLayout>
  )
}

export default ResetPasswordPage
