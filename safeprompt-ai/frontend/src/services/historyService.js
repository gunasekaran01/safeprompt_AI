import apiClient from './api.js'

/**
 * Fetches the authenticated user's analysis history with optional
 * search, risk-level filter, and pagination.
 * @param {{search?: string, riskLevel?: string, limit?: number, offset?: number}} options
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number}>}
 */
export async function getHistory({ search = '', riskLevel = '', limit = 20, offset = 0 } = {}) {
  const params = { limit, offset }
  if (search) params.search = search
  if (riskLevel) params.risk_level = riskLevel
  const response = await apiClient.get('/history', { params })
  return response.data
}

/**
 * Fetches a single analysis by id.
 * @param {string} id
 */
export async function getHistoryItem(id) {
  const response = await apiClient.get(`/history/${id}`)
  return response.data
}

/**
 * Deletes a single analysis by id.
 * @param {string} id
 */
export async function deleteHistoryItem(id) {
  await apiClient.delete(`/history/${id}`)
}

export default { getHistory, getHistoryItem, deleteHistoryItem }
