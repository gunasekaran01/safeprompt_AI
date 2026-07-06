import apiClient from './apiClient.js'

/**
 * Report service — Milestone 13 backend (GET /api/reports/{analysis_id},
 * reportlab-rendered PDF), wired into the frontend in Phase 6.
 *
 * The backend streams a PDF file (`FileResponse`), not JSON, so this
 * calls apiClient with `responseType: 'blob'` and turns the response into
 * a client-side download via a temporary object URL — no separate
 * upload/storage step needed, and it reuses the same axios instance
 * (and therefore the same auth-header interceptor) as every other
 * service.
 */

function toFriendlyError(error) {
  if (error.response?.status === 404) {
    return new Error('That analysis no longer exists, so a report cannot be generated for it.')
  }
  if (error.response) {
    return new Error(
      `Failed to generate the report (${error.response.status} ${error.response.statusText}).`
    )
  }
  if (error.request) {
    return new Error(
      'Could not reach the SafePrompt AI backend. Make sure the API server is running.'
    )
  }
  return new Error('Something went wrong while generating the report.')
}

/**
 * Requests a fresh PDF safety report for `analysisId` and triggers a
 * browser download of it. Resolves once the download has been kicked
 * off; rejects with a user-friendly Error on failure.
 *
 * @param {string} analysisId
 * @returns {Promise<void>}
 */
export async function downloadReport(analysisId) {
  let response
  try {
    response = await apiClient.get(`/reports/${analysisId}`, { responseType: 'blob' })
  } catch (error) {
    throw toFriendlyError(error)
  }

  const blob = new Blob([response.data], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `safeprompt-report-${analysisId}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export default { downloadReport }
