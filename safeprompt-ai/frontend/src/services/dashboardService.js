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

/**
 * Fetches the three Chart.js dashboard datasets (score trend, risk-level
 * distribution, detection breakdown) from the real backend
 * (GET /api/dashboard/charts).
 * @param {number} days
 */
export async function getDashboardCharts(days = 14) {
  const response = await apiClient.get('/dashboard/charts', { params: { days } })
  return response.data
}

export default { getDashboardStats, getRecentActivity, getDashboardCharts }
