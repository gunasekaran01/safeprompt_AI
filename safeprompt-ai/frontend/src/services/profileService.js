import apiClient from './apiClient.js'

/**
 * apiClient.js (unlike api.js) has no response interceptor, so failed
 * requests reject with the raw Axios error. Every exported function here
 * normalizes that into a friendly Error with a real .message, the same
 * way reportService.js and adminService.js already do — otherwise a
 * dropped connection or failed request surfaces as a raw/unfriendly
 * fetch error in ProfileForm.jsx instead of something a user can read.
 */
function toFriendlyError(error, fallbackMessage) {
  if (error.response?.status === 401) {
    return new Error('Your session has expired. Please sign in again.')
  }
  if (error.response) {
    const detail = error.response.data?.detail
    const detailMessage = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(' ')
      : typeof detail === 'string'
        ? detail
        : null
    return new Error(detailMessage || `${fallbackMessage} (${error.response.status})`)
  }
  if (error.request) {
    return new Error(
      'Unable to reach the SafePrompt AI backend. Please check your connection and that the server is running.',
    )
  }
  return new Error(fallbackMessage)
}

/**
 * Fetches the current authenticated user's profile.
 *
 * Backend route is GET /api/profiles/me (app/api/routes/profiles.py) —
 * note the plural "profiles" and the "/me" suffix; a previous version of
 * this file called the singular "/profile", which 404'd against every
 * real deployment of this API and was the root cause of "profile
 * changes don't save/reflect."
 *
 * @returns {Promise<{id: string, name: string|null, email: string, avatarUrl: string|null, createdAt: string, updatedAt: string}>}
 */
export async function getMyProfile() {
  try {
    const response = await apiClient.get('/profiles/me')
    return response.data
  } catch (error) {
    throw toFriendlyError(error, 'Failed to load your profile.')
  }
}

/**
 * Updates the current user's profile with a partial set of fields.
 * @param {{name?: string, avatarUrl?: string}} updates
 */
export async function updateMyProfile(updates) {
  try {
    const response = await apiClient.patch('/profiles/me', updates)
    return response.data
  } catch (error) {
    throw toFriendlyError(error, 'Failed to save your profile.')
  }
}

/**
 * Permanently deletes the current user's account via
 * DELETE /api/profiles/me. Cannot be undone — the caller
 * (DeleteAccountSection.jsx) is responsible for confirming intent first.
 */
export async function deleteMyAccount() {
  try {
    await apiClient.delete('/profiles/me')
  } catch (error) {
    throw toFriendlyError(error, 'Failed to delete your account.')
  }
}

export default { getMyProfile, updateMyProfile, deleteMyAccount }
