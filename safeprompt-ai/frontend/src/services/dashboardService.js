import apiClient from './api.js'

/**
 * Fetches aggregate dashboard statistics for the authenticated user from
 * the real backend (GET /api/dashboard/stats).
 */
export async function getDashboardStats() {
  const response = await apiClient.get('/dashboard/stats')
  return response.data
}

/**
 * Fetches the authenticated user's most recent analyses
 * (GET /api/dashboard/recent-activity).
 * @param {number} limit
 */
export async function getRecentActivity(limit = 8) {
  const response = await apiClient.get('/dashboard/recent-activity', { params: { limit } })
  return response.data.items
}

export default { getDashboardStats, getRecentActivity }
