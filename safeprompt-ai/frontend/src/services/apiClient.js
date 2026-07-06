import axios from 'axios'
import { supabase } from './supabaseClient.js'

/**
 * Shared axios instance for all real backend calls.
 *
 * Base URL comes from VITE_API_BASE_URL (see .env.example), defaulting to
 * "/api" so the Vite dev server proxy (vite.config.js) forwards requests
 * to the FastAPI backend on :8000 without any CORS configuration needed
 * in development.
 *
 * A request interceptor attaches the current Supabase session's access
 * token as `Authorization: Bearer <token>` (SaaS Phase 1 — JWT
 * Validation), so every backend call is authenticated the moment a user
 * is logged in. supabase.auth.getSession() reads from local state / a
 * cached in-memory session (only hitting the network to refresh an
 * expired token), so this adds no perceptible latency to normal
 * requests. Requests made while logged out simply go out without the
 * header, matching today's backend (Phase 4 will start requiring it on
 * specific routes).
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
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

export default apiClient
