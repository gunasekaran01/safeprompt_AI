import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiAlertTriangle, FiTrash2 } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext.jsx'
import { deleteMyAccount } from '../../services/profileService.js'

const INPUT_CLASSES =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm transition-colors placeholder:text-slate-400 focus:border-risk-critical focus:outline-none focus:ring-2 focus:ring-risk-critical/30 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500'

const CONFIRMATION_PHRASE = 'DELETE'

/**
 * Danger-zone card on SettingsPage — SaaS Phase 7.
 *
 * Requires typing "DELETE" before the button is even clickable, since
 * this is the one destructive, irreversible action in the app (unlike
 * deleting a single history entry) — a stray click should not be enough
 * to remove someone's whole account. On success, signs the user out
 * (their Supabase session is invalid anyway the moment the account no
 * longer exists) and redirects to the homepage.
 */
function DeleteAccountSection() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const [confirmationText, setConfirmationText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState(null)

  const canDelete = confirmationText.trim() === CONFIRMATION_PHRASE && !isDeleting

  async function handleDelete() {
    setError(null)
    setIsDeleting(true)
    try {
      await deleteMyAccount()
    } catch (err) {
      setError(err.message || 'Failed to delete your account.')
      setIsDeleting(false)
      return
    }

    // The account (and its session) no longer exists at this point, so
    // signOut() clearing local Supabase state is best-effort — a failure
    // here shouldn't block navigating away from a deleted account.
    try {
      await logout()
    } catch {
      // Intentionally ignored — see comment above.
    }
    navigate('/', { replace: true })
  }

  return (
    <section className="card space-y-4 border-risk-critical/30">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-risk-critical">
        Danger Zone
      </h2>

      <div className="space-y-1">
        <p className="text-sm font-medium text-slate-900 dark:text-white">Delete Account</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Permanently deletes your account and all of your data — analyses, history, reports, and
          settings. This action cannot be undone.
        </p>
      </div>

      <div>
        <label
          htmlFor="delete-confirmation"
          className="mb-1 block text-xs font-medium text-slate-600 dark:text-slate-300"
        >
          Type <span className="font-mono font-semibold">{CONFIRMATION_PHRASE}</span> to confirm
        </label>
        <input
          id="delete-confirmation"
          type="text"
          value={confirmationText}
          onChange={(event) => setConfirmationText(event.target.value)}
          className={INPUT_CLASSES}
          placeholder={CONFIRMATION_PHRASE}
          autoComplete="off"
        />
      </div>

      {error && (
        <p className="flex items-center gap-1.5 text-xs font-medium text-risk-critical">
          <FiAlertTriangle className="h-3.5 w-3.5 shrink-0" /> {error}
        </p>
      )}

      <button
        type="button"
        onClick={handleDelete}
        disabled={!canDelete}
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-risk-critical px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-risk-critical/90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <FiTrash2 className="h-4 w-4" />
        {isDeleting ? 'Deleting…' : 'Delete My Account'}
      </button>
    </section>
  )
}

export default DeleteAccountSection
