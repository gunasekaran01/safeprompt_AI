import apiClient from './apiClient.js'

/**
 * Admin dashboard service (frontend/src/pages/AdminPage.jsx). Every call
 * goes through apiClient, which attaches the current user's Supabase
 * session token as a Bearer header (see apiClient.js) — the backend's
 * app.api.deps.require_admin dependency is what actually authorizes
 * these, not anything on this side.
 */

function mapOverview(data) {
  return {
    totalUsers: data.total_users,
    totalAnalyses: data.total_analyses,
    totalReports: data.total_reports,
    safePrompts: data.safe_prompts,
    unsafePrompts: data.unsafe_prompts,
    injectionAttempts: data.injection_attempts,
    toxicPrompts: data.toxic_prompts,
    averageSafetyScore: data.average_safety_score,
    riskLevelDistribution: data.risk_level_distribution.map((entry) => ({
      riskLevel: entry.risk_level,
      count: entry.count,
    })),
  }
}

function mapUser(user) {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    isAdmin: user.is_admin,
    createdAt: user.created_at,
    analysesCount: user.analyses_count,
  }
}

function toFriendlyError(error, fallbackMessage) {
  if (error.response?.status === 403) {
    return new Error('You do not have admin access.')
  }
  if (error.response) {
    return new Error(`${fallbackMessage} (${error.response.status})`)
  }
  if (error.request) {
    return new Error(
      'Could not reach the SafePrompt AI backend. Make sure the API server is running.'
    )
  }
  return new Error(fallbackMessage)
}

/**
 * Fetches platform-wide totals from GET /api/admin/overview.
 */
export async function getAdminOverview() {
  try {
    const response = await apiClient.get('/admin/overview')
    return mapOverview(response.data)
  } catch (error) {
    throw toFriendlyError(error, 'Failed to load admin overview.')
  }
}

/**
 * Fetches every user (plus their analysis count) from GET /api/admin/users.
 */
export async function getAdminUsers() {
  try {
    const response = await apiClient.get('/admin/users')
    return {
      users: response.data.users.map(mapUser),
      total: response.data.total,
    }
  } catch (error) {
    throw toFriendlyError(error, 'Failed to load users.')
  }
}

/**
 * Permanently deletes a user's account via DELETE /api/admin/users/{id}.
 * Cannot be undone — the caller (AdminPage.jsx) is responsible for
 * confirming with the admin before calling this.
 */
export async function deleteAdminUser(userId) {
  try {
    await apiClient.delete(`/admin/users/${userId}`)
  } catch (error) {
    throw toFriendlyError(error, 'Failed to delete this user.')
  }
}

export default { getAdminOverview, getAdminUsers, deleteAdminUser }
