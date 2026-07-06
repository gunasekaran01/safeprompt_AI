import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey)

if (!isSupabaseConfigured) {
  // eslint-disable-next-line no-console
  console.warn(
    'VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are not set. Authentication will not ' +
      'work until these are configured in frontend/.env (see .env.example).',
  )
}

/**
 * Shared Supabase client. Falls back to placeholder values when not
 * configured so the app can still build and boot (e.g. in this sandbox,
 * or before a developer has set up their own Supabase project) — auth
 * calls will simply fail cleanly instead of the app crashing on import.
 */
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key',
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  },
)

export default supabase
