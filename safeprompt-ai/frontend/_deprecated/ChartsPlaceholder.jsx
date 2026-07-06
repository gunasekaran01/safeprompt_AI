import { FiBarChart2 } from 'react-icons/fi'
import MilestoneNotice from '../MilestoneNotice.jsx'

/**
 * Reserves the layout space for the Chart.js visualizations (safety score
 * trend, risk level distribution, etc.) that are built in Milestone 12.
 * Kept as its own component so swapping in real charts later only means
 * replacing this file's contents, not restructuring DashboardPage.
 */
function ChartsPlaceholder() {
  return (
    <div className="card flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-white">
        <FiBarChart2 className="h-6 w-6" />
      </div>
      <h2 className="text-base font-semibold text-slate-900 dark:text-white">Trend Charts</h2>
      <p className="max-w-sm text-sm text-slate-500 dark:text-slate-400">
        Safety score trends and a risk level breakdown chart will render
        here, built on top of the stats above.
      </p>
      <MilestoneNotice milestone={12} feature="Charts" />
    </div>
  )
}

export default ChartsPlaceholder
