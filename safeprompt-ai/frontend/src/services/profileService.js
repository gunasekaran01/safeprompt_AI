import apiClient from './apiClient.js'

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
  const response = await apiClient.get('/profiles/me')
  return response.data
}

/**
 * Updates the current user's profile with a partial set of fields.
 * @param {{name?: string, avatarUrl?: string}} updates
 */
export async function updateMyProfile(updates) {
  const response = await apiClient.patch('/profiles/me', updates)
  return response.data
}

/**
 * Permanently deletes the current user's account via
 * DELETE /api/profiles/me. Cannot be undone — the caller
 * (DeleteAccountSection.jsx) is responsible for confirming intent first.
 */
export async function deleteMyAccount() {
  await apiClient.delete('/profiles/me')
}

export default { getMyProfile, updateMyProfile, deleteMyAccount }
