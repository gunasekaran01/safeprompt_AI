import { useEffect, useState } from 'react'
import { FiAlertTriangle, FiCheck, FiEdit2, FiUser, FiX } from 'react-icons/fi'
import { getMyProfile, updateMyProfile } from '../../services/profileService.js'

const INPUT_CLASSES =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm transition-colors placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500'

function ProfileSkeleton() {
  return (
    <div className="flex animate-pulse items-center gap-3 py-1">
      <div className="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-700" />
      <div className="space-y-2">
        <div className="h-3 w-40 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="h-3 w-56 rounded bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  )
}

/**
 * Account card on SettingsPage — SaaS Phase 2 (view) and Phase 7 (edit).
 * Loads the authenticated user's profile on mount and lets them switch
 * into an inline edit form for name/avatar URL, backed by
 * PATCH /api/profiles/me (services/profileService.js).
 */
function AccountSection() {
  const [profile, setProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)

  const [isEditing, setIsEditing] = useState(false)
  const [nameDraft, setNameDraft] = useState('')
  const [avatarUrlDraft, setAvatarUrlDraft] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState(null)
  const [showSavedNotice, setShowSavedNotice] = useState(false)

  const loadProfile = async () => {
    setIsLoading(true)
    setLoadError(null)
    try {
      const result = await getMyProfile()
      setProfile(result)
    } catch (err) {
      setLoadError(err.message || 'Failed to load your profile.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  function startEditing() {
    setNameDraft(profile?.name || '')
    setAvatarUrlDraft(profile?.avatarUrl || '')
    setSaveError(null)
    setIsEditing(true)
  }

  function cancelEditing() {
    setIsEditing(false)
    setSaveError(null)
  }

  async function handleSave(event) {
    event.preventDefault()
    setIsSaving(true)
    setSaveError(null)
    try {
      const updated = await updateMyProfile({ name: nameDraft, avatarUrl: avatarUrlDraft })
      setProfile(updated)
      setIsEditing(false)
      setShowSavedNotice(true)
      window.setTimeout(() => setShowSavedNotice(false), 2500)
    } catch (err) {
      setSaveError(err.message || 'Failed to update your profile.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <section className="card space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Account
        </h2>
        {!isLoading && !loadError && profile && !isEditing && (
          <button
            type="button"
            onClick={startEditing}
            className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
          >
            <FiEdit2 className="h-3.5 w-3.5" /> Edit
          </button>
        )}
      </div>

      {isLoading ? (
        <ProfileSkeleton />
      ) : loadError ? (
        <div className="flex items-center justify-between gap-4 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-4 py-3 text-sm text-risk-critical">
          <div className="flex items-center gap-2">
            <FiAlertTriangle className="h-4 w-4 shrink-0" />
            {loadError}
          </div>
          <button
            type="button"
            onClick={loadProfile}
            className="shrink-0 font-semibold underline underline-offset-2"
          >
            Retry
          </button>
        </div>
      ) : !profile ? (
        <p className="text-sm text-slate-400">No account details found.</p>
      ) : isEditing ? (
        <form onSubmit={handleSave} className="space-y-3">
          <div>
            <label
              htmlFor="account-name"
              className="mb-1 block text-xs font-medium text-slate-600 dark:text-slate-300"
            >
              Display Name
            </label>
            <input
              id="account-name"
              type="text"
              value={nameDraft}
              onChange={(event) => setNameDraft(event.target.value)}
              maxLength={100}
              placeholder="Your name"
              className={INPUT_CLASSES}
            />
          </div>
          <div>
            <label
              htmlFor="account-avatar"
              className="mb-1 block text-xs font-medium text-slate-600 dark:text-slate-300"
            >
              Avatar URL
            </label>
            <input
              id="account-avatar"
              type="url"
              value={avatarUrlDraft}
              onChange={(event) => setAvatarUrlDraft(event.target.value)}
              maxLength={2048}
              placeholder="https://example.com/avatar.png"
              className={INPUT_CLASSES}
            />
          </div>

          {saveError && (
            <p className="flex items-center gap-1.5 text-xs font-medium text-risk-critical">
              <FiAlertTriangle className="h-3.5 w-3.5 shrink-0" /> {saveError}
            </p>
          )}

          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={isSaving} className="btn-primary">
              {isSaving ? 'Saving…' : 'Save Changes'}
            </button>
            <button type="button" onClick={cancelEditing} disabled={isSaving} className="btn-secondary">
              <FiX className="h-4 w-4" /> Cancel
            </button>
          </div>
        </form>
      ) : (
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-600 text-white">
            {profile.avatarUrl ? (
              <img src={profile.avatarUrl} alt="" className="h-10 w-10 object-cover" />
            ) : (
              <FiUser className="h-5 w-5" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              {profile.name || 'Unnamed account'}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{profile.email}</p>
          </div>
        </div>
      )}

      {showSavedNotice && (
        <p className="flex items-center gap-1.5 text-xs font-medium text-risk-safe">
          <FiCheck className="h-3.5 w-3.5" /> Profile updated
        </p>
      )}
    </section>
  )
}

export default AccountSection
