import apiClient from './api.js'

/**
 * Submits a prompt to the backend for injection/toxicity analysis and
 * returns the full result: injection status, toxicity status, safety
 * score, risk level, recommendation, and reasoning.
 *
 * @param {string} prompt
 * @returns {Promise<object>} PromptAnalysisResponse shape from the backend.
 */
export async function analyzePrompt(prompt) {
  const response = await apiClient.post('/analyze', { prompt })
  return response.data
}

export default { analyzePrompt }
