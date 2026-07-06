import axios from 'axios'
import { supabase } from './supabaseClient.js'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * Shared Axios client for all backend calls. Attaches the current
 * Supabase session's access token as a Bearer header (needed for every
 * protected endpoint the backend exposes), and normalizes error
 * responses into a consistent { message, status } shape so components
 * never need to parse FastAPI's error format directly.
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const accessToken = data.session?.access_token
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status ?? null
    const detail = error.response?.data?.detail
    let message = 'Something went wrong. Please try again.'

    if (!error.response) {
      message = 'Unable to reach the server. Please check your connection and that the backend is running.'
    } else if (status === 401) {
      message = 'Your session has expired. Please sign in again.'
    } else if (Array.isArray(detail)) {
      // FastAPI/Pydantic validation errors come back as a list of { msg, loc, ... }
      message = detail.map((item) => item.msg).join(' ')
    } else if (typeof detail === 'string') {
      message = detail
    } else if (status >= 500) {
      message = 'The server ran into a problem processing this request.'
    }

    return Promise.reject({ message, status, cause: error })
  },
)

export default apiClient
