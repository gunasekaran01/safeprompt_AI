import PlaceholderPage from '../components/common/PlaceholderPage'

/**
 * Prompt Analyzer — route: "/analyzer"
 * The prompt input form, safety score, risk level, and reasoning output
 * are built in Milestone 5 (UI) and wired to real detection in Milestones
 * 6-9 (backend + detectors + scoring engine).
 */
function Analyzer() {
  return (
    <PlaceholderPage
      title="Prompt Analyzer"
      description="Paste a prompt here to get a safety score, risk level, and reasoning."
      milestone={5}
    />
  )
}

export default Analyzer
