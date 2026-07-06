import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FiAlertTriangle, FiCheckCircle, FiLoader, FiMail } from 'react-icons/fi'
import AuthLayout from '../components/Auth/AuthLayout.jsx'
import { useAuth } from '../utils/AuthContext.jsx'

function ForgotPasswordPage() {
  const { resetPassword } = useAuth()

  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [isSent, setIsSent] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await resetPassword(email)
      setIsSent(true)
    } catch (err) {
      setError(err.message || 'Failed to send the reset email. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSent) {
    return (
      <AuthLayout title="Check your email" subtitle="Password reset link sent">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-risk-safe/10 text-risk-safe">
            <FiCheckCircle className="h-6 w-6" />
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            If an account exists for <strong>{email}</strong>, we&apos;ve sent a link to reset
            your password.
          </p>
          <Link to="/login" className="btn-primary mt-2">
            Back to Sign In
          </Link>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Forgot your password?" subtitle="We'll email you a reset link">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-sm text-risk-critical">
            <FiAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
          {isSubmitting ? (
            <>
              <FiLoader className="h-4 w-4 animate-spin" /> Sending…
            </>
          ) : (
            <>
              <FiMail className="h-4 w-4" /> Send Reset Link
            </>
          )}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        Remembered your password?{' '}
        <Link to="/login" className="font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  )
}

export default ForgotPasswordPage
