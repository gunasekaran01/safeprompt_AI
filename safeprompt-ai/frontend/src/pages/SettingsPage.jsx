import { useState } from 'react'
import { FiCheck, FiInfo, FiMonitor, FiMoon, FiRefreshCw, FiSettings, FiSun, FiUser } from 'react-icons/fi'
import { useTheme } from '../utils/ThemeContext.jsx'
import { useLocalStorage } from '../utils/useLocalStorage.js'
import { APP_NAME, APP_VERSION } from '../utils/constants.js'
import ProfileForm from '../components/Settings/ProfileForm.jsx'

const THEME_OPTIONS = [
  { value: 'light', label: 'Light', icon: FiSun },
  { value: 'dark', label: 'Dark', icon: FiMoon },
  { value: 'system', label: 'System', icon: FiMonitor },
]

function ToggleRow({ title, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div>
        <p className="text-sm font-medium text-slate-900 dark:text-white">{title}</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">{description}</p>
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
          checked ? 'bg-brand-600' : 'bg-slate-300 dark:bg-slate-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}

function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [compactMode, setCompactMode] = useLocalStorage('safeprompt-ai-compact-mode', false)
  const [autoAnalyzeOnPaste, setAutoAnalyzeOnPaste] = useLocalStorage(
    'safeprompt-ai-auto-analyze-on-paste',
    false,
  )
  const [showResetConfirmation, setShowResetConfirmation] = useState(false)

  const handleResetPreferences = () => {
    setTheme('system')
    setCompactMode(false)
    setAutoAnalyzeOnPaste(false)
    setShowResetConfirmation(true)
    window.setTimeout(() => setShowResetConfirmation(false), 2500)
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8 px-4 py-16 sm:px-6 lg:px-8">
      <div className="space-y-2 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-white">
          <FiSettings className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Preferences are saved locally in your browser.
        </p>
      </div>

      {/* Profile */}
      <section className="card space-y-4">
        <div className="flex items-center gap-2">
          <FiUser className="h-4 w-4 text-slate-400" />
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Profile
          </h2>
        </div>
        <ProfileForm />
      </section>

      {/* Appearance */}
      <section className="card space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Appearance
        </h2>
        <div className="grid grid-cols-3 gap-3">
          {THEME_OPTIONS.map(({ value, label, icon: Icon }) => {
            const isSelected = theme === value
            return (
              <button
                key={value}
                type="button"
                onClick={() => setTheme(value)}
                className={`flex flex-col items-center gap-2 rounded-lg border-2 px-4 py-3 text-sm font-medium transition-colors ${
                  isSelected
                    ? 'border-brand-600 bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                    : 'border-slate-200 text-slate-600 hover:border-slate-300 dark:border-slate-700 dark:text-slate-300 dark:hover:border-slate-600'
                }`}
              >
                <Icon className="h-5 w-5" />
                {label}
                {isSelected && <FiCheck className="h-3.5 w-3.5" />}
              </button>
            )
          })}
        </div>
      </section>

      {/* Preferences */}
      <section className="card divide-y divide-slate-100 dark:divide-slate-700">
        <h2 className="pb-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Preferences
        </h2>
        <ToggleRow
          title="Compact Mode"
          description="Reduce spacing in the dashboard and history tables for denser layouts."
          checked={compactMode}
          onChange={setCompactMode}
        />
        <ToggleRow
          title="Auto-Analyze on Paste"
          description="Automatically run the analyzer when a prompt is pasted into the input field."
          checked={autoAnalyzeOnPaste}
          onChange={setAutoAnalyzeOnPaste}
        />
      </section>

      {/* Reset */}
      <section className="card space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Reset
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Restore appearance and preference settings to their defaults. This
          does not delete any analysis history.
        </p>
        <button type="button" onClick={handleResetPreferences} className="btn-secondary">
          <FiRefreshCw className="h-4 w-4" />
          Reset to Defaults
        </button>
        {showResetConfirmation && (
          <p className="flex items-center gap-1.5 text-xs font-medium text-risk-safe">
            <FiCheck className="h-3.5 w-3.5" /> Preferences reset
          </p>
        )}
      </section>

      {/* App info */}
      <section className="card">
        <div className="flex items-start gap-3">
          <FiInfo className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          <div className="text-xs text-slate-500 dark:text-slate-400">
            <p>
              {APP_NAME} v{APP_VERSION}
            </p>
            <p>Environment: {import.meta.env.MODE}</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default SettingsPage
