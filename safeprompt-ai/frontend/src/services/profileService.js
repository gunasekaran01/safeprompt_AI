import apiClient from './api.js'

/**
 * Fetches the current authenticated user's profile.
 * @returns {Promise<{id: string, name: string|null, email: string, avatarUrl: string|null, createdAt: string, updatedAt: string}>}
 */
export async function getMyProfile() {
  const response = await apiClient.get('/profile')
  return response.data
}

/**
 * Updates the current user's profile with a partial set of fields.
 * @param {{name?: string, avatarUrl?: string}} updates
 */
export async function updateMyProfile(updates) {
  const response = await apiClient.patch('/profile', updates)
  return response.data
}

export default { getMyProfile, updateMyProfile }
