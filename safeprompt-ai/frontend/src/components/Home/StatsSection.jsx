const STATS = [
  { value: '2', label: 'Detection Engines' },
  { value: '0–100', label: 'Safety Score Scale' },
  { value: '5', label: 'Risk Levels' },
  { value: '100%', label: 'Explainable Results' },
]

function StatsSection() {
  return (
    <section className="border-y border-slate-100 bg-white dark:border-slate-800 dark:bg-surface-dark">
      <div className="mx-auto grid max-w-7xl grid-cols-2 gap-8 px-4 py-10 sm:px-6 lg:grid-cols-4 lg:px-8">
        {STATS.map((stat) => (
          <div key={stat.label} className="text-center">
            <p className="text-3xl font-extrabold text-brand-600 dark:text-brand-400">{stat.value}</p>
            <p className="mt-1 text-xs font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default StatsSection
