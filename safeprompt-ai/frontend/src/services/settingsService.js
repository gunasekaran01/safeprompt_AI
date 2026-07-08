import apiClient from './api.js'

/**
 * Server-synced counterpart to the theme/compact-mode/auto-analyze
 * preferences (backend/app/api/settings.py, backed by the
 * `user_settings` Supabase table). Response/request JSON is camelCase
 * (theme, compactMode, autoAnalyzeOnPaste, updatedAt) since the backend
 * schema extends CamelCaseModel.
 */

/** Fetches the current user's settings, creating defaults on the server on first access. */
export async function getSettings() {
  const response = await apiClient.get('/settings')
  return response.data
}

/**
 * Applies a partial update. Only pass the fields that changed --
 * e.g. updateSettings({ theme: 'dark' }).
 */
export async function updateSettings(updates) {
  const response = await apiClient.patch('/settings', updates)
  return response.data
}

export default { getSettings, updateSettings }
