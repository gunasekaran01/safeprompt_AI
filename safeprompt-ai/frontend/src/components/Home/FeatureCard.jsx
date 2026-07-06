/**
 * Presentational card for a single platform capability. Kept generic
 * (icon + title + description) so it can be reused anywhere a feature
 * needs highlighting, not just on the landing page.
 */
function FeatureCard({ icon: Icon, title, description, accentClassName = 'bg-brand-600' }) {
  return (
    <div className="card h-full transition-transform duration-150 hover:-translate-y-0.5">
      <div
        className={`mb-4 flex h-11 w-11 items-center justify-center rounded-xl text-white ${accentClassName}`}
      >
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mb-2 text-base font-semibold text-slate-900 dark:text-white">{title}</h3>
      <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400">{description}</p>
    </div>
  )
}

export default FeatureCard
