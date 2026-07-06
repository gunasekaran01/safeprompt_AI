/**
 * Standard "not built yet" page body.
 *
 * Used by pages whose real UI arrives in a later milestone, so that
 * routing (Milestone 2) can be verified end-to-end without pages fully
 * implementing their eventual content. Once a page's milestone lands, its
 * page component stops using this and gets real markup instead.
 */
function PlaceholderPage({ title, description, milestone }) {
  return (
    <div className="card mx-auto max-w-xl space-y-3 text-center">
      <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">{title}</h1>
      <p className="text-sm text-slate-600 dark:text-slate-300">{description}</p>
      <span className="inline-block rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-600/20 dark:text-brand-300">
        Coming in Milestone {milestone}
      </span>
    </div>
  )
}

export default PlaceholderPage
