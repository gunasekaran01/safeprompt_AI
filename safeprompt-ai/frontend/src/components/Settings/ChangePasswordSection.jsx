import { useState } from 'react'
import { FiAlertTriangle, FiCheck, FiLock } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext.jsx'

const INPUT_CLASSES =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm transition-colors placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500'

const MIN_PASSWORD_LENGTH = 8

/**
 * Change-password card on SettingsPage — SaaS Phase 7.
 *
 * Calls AuthContext's updatePassword (supabase.auth.updateUser under the
 * hood), which works directly against the current session with no
 * separate "current password" field: Supabase's password-update API
 * only requires an already-authenticated session, not re-entering the
 * old password. That matches how ResetPasswordPage.jsx sets a fresh
 * password after a reset-link flow — this reuses the same underlying
 * call for the in-app case.
 */
function ChangePasswordSection() {
  const { updatePassword } = useAuth()

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [showSuccess, setShowSuccess] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)

    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`)
      return
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)
    try {
      await updatePassword(newPassword)
      setNewPassword('')
      setConfirmPassword('')
      setShowSuccess(true)
      window.setTimeout(() => setShowSuccess(false), 2500)
    } catch (err) {
      setError(err.message || 'Failed to update your password.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="card space-y-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Change Password
      </h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label
            htmlFor="new-password"
            className="mb-1 block text-xs font-medium text-slate-600 dark:text-slate-300"
          >
            New Password
          </label>
          <div className="relative">
            <FiLock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="new-password"
              type="password"
              autoComplete="new-password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              className={`${INPUT_CLASSES} pl-9`}
              placeholder="At least 8 characters"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="confirm-new-password"
            className="mb-1 block text-xs font-medium text-slate-600 dark:text-slate-300"
          >
            Confirm New Password
          </label>
          <div className="relative">
            <FiLock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="confirm-new-password"
              type="password"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              className={`${INPUT_CLASSES} pl-9`}
            />
          </div>
        </div>

        {error && (
          <p className="flex items-center gap-1.5 text-xs font-medium text-risk-critical">
            <FiAlertTriangle className="h-3.5 w-3.5 shrink-0" /> {error}
          </p>
        )}

        <button type="submit" disabled={isSubmitting} className="btn-primary">
          {isSubmitting ? 'Updating…' : 'Update Password'}
        </button>

        {showSuccess && (
          <p className="flex items-center gap-1.5 text-xs font-medium text-risk-safe">
            <FiCheck className="h-3.5 w-3.5" /> Password updated
          </p>
        )}
      </form>
    </section>
  )
}

export default ChangePasswordSection
