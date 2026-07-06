/**
 * Shows a single detector's result (injection or toxicity): whether
 * something was detected, a confidence bar, and the explanation text.
 */
function DetectionStatusCard({ icon: Icon, title, detected, confidence, description, extraLabel }) {
  const confidencePercent = Math.round(confidence * 100)
  const accentClass = detected ? 'bg-risk-critical' : 'bg-risk-safe'
  const statusTextClass = detected ? 'text-risk-critical' : 'text-risk-safe'

  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white ${accentClass}`}>
            <Icon className="h-4 w-4" />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{title}</h3>
            {extraLabel && <p className="text-xs text-slate-400">{extraLabel}</p>}
          </div>
        </div>
        <span className={`shrink-0 text-xs font-bold ${statusTextClass}`}>
          {detected ? 'Detected' : 'Not Detected'}
        </span>
      </div>

      <p className="mt-3 text-xs leading-relaxed text-slate-500 dark:text-slate-400">{description}</p>

      <div className="mt-3">
        <div className="mb-1 flex justify-between text-[11px] text-slate-400">
          <span>Confidence</span>
          <span>{confidencePercent}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
          <div className={`h-full rounded-full ${accentClass}`} style={{ width: `${confidencePercent}%` }} />
        </div>
      </div>
    </div>
  )
}

export default DetectionStatusCard
