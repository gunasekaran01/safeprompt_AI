import { useEffect, useState } from 'react'
import { FiAlertTriangle, FiCheck, FiLoader, FiSave, FiUser } from 'react-icons/fi'
import { getMyProfile, updateMyProfile } from '../../services/profileService.js'

function ProfileForm() {
  const [name, setName] = useState('')
  const [avatarUrl, setAvatarUrl] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState(null)
  const [isSaved, setIsSaved] = useState(false)

  useEffect(() => {
    let isMounted = true
    setIsLoading(true)
    setError(null)

    getMyProfile()
      .then((profile) => {
        if (!isMounted) return
        setName(profile.name || '')
        setAvatarUrl(profile.avatarUrl || '')
        setEmail(profile.email || '')
      })
      .catch((err) => {
        if (isMounted) setError(err.message || 'Failed to load your profile.')
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setIsSaving(true)
    try {
      const updated = await updateMyProfile({ name, avatarUrl })
      setName(updated.name || '')
      setAvatarUrl(updated.avatarUrl || '')
      setIsSaved(true)
      window.setTimeout(() => setIsSaved(false), 2500)
    } catch (err) {
      setError(err.message || 'Failed to save your profile.')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <FiLoader className="h-5 w-5 animate-spin text-brand-600" />
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-sm text-risk-critical">
          <FiAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
          {avatarUrl ? (
            <img src={avatarUrl} alt="Avatar preview" className="h-full w-full object-cover" />
          ) : (
            <FiUser className="h-6 w-6" />
          )}
        </div>
        <div className="text-sm text-slate-500 dark:text-slate-400">
          <p className="font-medium text-slate-900 dark:text-white">{email}</p>
          <p className="text-xs">Your email is managed through your account and can&apos;t be changed here.</p>
        </div>
      </div>

      <div>
        <label htmlFor="profile-name" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Name
        </label>
        <input
          id="profile-name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Your name"
          className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
      </div>

      <div>
        <label htmlFor="profile-avatar" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Avatar URL
        </label>
        <input
          id="profile-avatar"
          type="url"
          value={avatarUrl}
          onChange={(event) => setAvatarUrl(event.target.value)}
          placeholder="https://example.com/avatar.png"
          className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
      </div>

      <div className="flex items-center gap-3">
        <button type="submit" disabled={isSaving} className="btn-primary">
          {isSaving ? (
            <>
              <FiLoader className="h-4 w-4 animate-spin" /> Saving…
            </>
          ) : (
            <>
              <FiSave className="h-4 w-4" /> Save Profile
            </>
          )}
        </button>
        {isSaved && (
          <span className="flex items-center gap-1.5 text-xs font-medium text-risk-safe">
            <FiCheck className="h-3.5 w-3.5" /> Saved
          </span>
        )}
      </div>
    </form>
  )
}

export default ProfileForm
