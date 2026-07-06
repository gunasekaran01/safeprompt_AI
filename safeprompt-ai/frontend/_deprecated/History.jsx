import PlaceholderPage from '../components/common/PlaceholderPage'

/**
 * History — route: "/history"
 * A searchable, filterable list of past analyzed prompts is built in
 * Milestone 11, once the SQLite persistence layer (Milestone 10) exists.
 */
function History() {
  return (
    <PlaceholderPage
      title="History"
      description="Past analyzed prompts, their scores, and risk levels will be listed here."
      milestone={11}
    />
  )
}

export default History
