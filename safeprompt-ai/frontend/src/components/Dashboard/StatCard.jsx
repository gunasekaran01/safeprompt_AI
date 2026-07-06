/**
 * Single metric card used in the dashboard's top stat row (Total
 * Analyses, Safe Prompts, etc.). Renders a skeleton while `isLoading` is
 * true so the layout doesn't jump once real data arrives.
 */
function StatCard({ icon: Icon, label, value, accentClassName = 'bg-brand-600', isLoading = false }) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="mb-3 h-9 w-9 rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="h-7 w-16 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="mt-2 h-3 w-24 rounded bg-slate-200 dark:bg-slate-700" />
      </div>
    )
  }

  return (
    <div className="card">
      <div
        className={`mb-3 flex h-9 w-9 items-center justify-center rounded-lg text-white ${accentClassName}`}
      >
        <Icon className="h-4 w-4" />
      </div>
      <p className="text-2xl font-extrabold text-slate-900 dark:text-white">{value}</p>
      <p className="mt-1 text-xs font-medium text-slate-500 dark:text-slate-400">{label}</p>
    </div>
  )
}

export default StatCard
