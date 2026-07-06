/**
 * Inline status badge shown on pages whose full feature set is built in a
 * later milestone (Dashboard, Analyzer, History). Keeps the "coming in
 * milestone N" messaging consistent instead of repeating markup per page.
 */
function MilestoneNotice({ milestone, feature }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-xs font-medium text-brand-700 dark:border-brand-800 dark:bg-brand-900/30 dark:text-brand-300">
      <span className="h-1.5 w-1.5 rounded-full bg-brand-500" aria-hidden="true" />
      {feature} ships in Milestone {milestone}
    </div>
  )
}

export default MilestoneNotice
