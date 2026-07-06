import { FiAlertTriangle, FiCode, FiShield, FiTarget } from 'react-icons/fi'
import { APP_DESCRIPTION, APP_NAME, APP_VERSION } from '../utils/constants.js'

const DETECTION_CATEGORIES = [
  {
    title: 'Prompt Injection',
    description:
      'Identifies attempts to override, ignore, or manipulate an AI system\'s original instructions through crafted user input.',
  },
  {
    title: 'Jailbreak Attempts',
    description:
      'Flags patterns designed to bypass safety guardrails, such as fictional framing, role-play personas, or "developer mode" requests.',
  },
  {
    title: 'Toxic Content',
    description:
      'Detects profanity, harassment, threats, hate speech, and other harmful language within a submitted prompt.',
  },
]

const TECH_STACK = [
  { group: 'Frontend', items: ['React', 'Vite', 'Tailwind CSS', 'React Router', 'Axios', 'Chart.js'] },
  { group: 'Backend', items: ['Python', 'FastAPI', 'Pydantic', 'SQLAlchemy', 'SQLite'] },
  { group: 'AI / ML', items: ['Hugging Face Transformers', 'Detoxify', 'Sentence Transformers'] },
  { group: 'Deployment', items: ['Docker'] },
]

function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-10 px-4 py-16 sm:px-6 lg:px-8">
      {/* Intro */}
      <div className="space-y-4 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-card">
          <FiShield className="h-7 w-7" />
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight">About {APP_NAME}</h1>
        <p className="text-slate-600 dark:text-slate-300">{APP_DESCRIPTION}</p>
      </div>

      {/* Mission */}
      <section className="card space-y-3">
        <div className="flex items-center gap-2">
          <FiTarget className="h-5 w-5 text-brand-600 dark:text-brand-400" />
          <h2 className="text-lg font-semibold">Why SafePrompt AI Exists</h2>
        </div>
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
          As AI systems are increasingly exposed to untrusted user input, they
          become vulnerable to prompt injection and jailbreak attacks that try
          to override their intended behavior, as well as to toxic content
          that can degrade the quality and safety of an interaction.
          SafePrompt AI gives developers and researchers a simple way to
          submit a prompt and get back an evidence-based safety assessment,
          rather than relying on gut feeling alone.
        </p>
      </section>

      {/* What it detects */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <FiAlertTriangle className="h-5 w-5 text-brand-600 dark:text-brand-400" />
          <h2 className="text-lg font-semibold">What It Detects</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {DETECTION_CATEGORIES.map((category) => (
            <div key={category.title} className="card">
              <h3 className="mb-2 text-sm font-semibold text-slate-900 dark:text-white">
                {category.title}
              </h3>
              <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                {category.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* How scoring works */}
      <section className="card space-y-3">
        <h2 className="text-lg font-semibold">How the Safety Score Works</h2>
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
          Every analyzed prompt receives a numeric Safety Score from 0
          (extremely unsafe) to 100 (completely safe). The score combines
          signals from the injection detector and the toxicity detector, and
          maps to one of five risk levels: Safe, Low Risk, Medium Risk, High
          Risk, or Critical. Each result also includes a plain-language
          recommendation and the reasoning behind the score, so the output is
          explainable rather than a black box. The full scoring engine is
          built in Milestone 9.
        </p>
      </section>

      {/* Tech stack */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <FiCode className="h-5 w-5 text-brand-600 dark:text-brand-400" />
          <h2 className="text-lg font-semibold">Tech Stack</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {TECH_STACK.map((group) => (
            <div key={group.group} className="card">
              <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">
                {group.group}
              </h3>
              <div className="flex flex-wrap gap-2">
                {group.items.map((item) => (
                  <span
                    key={item}
                    className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer */}
      <section className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-900/10 dark:text-amber-300">
        <strong className="font-semibold">Disclaimer:</strong> SafePrompt AI
        is a research and educational tool. Detection results are
        probabilistic, not guaranteed, and should not be treated as the sole
        safeguard in a production system handling untrusted input.
      </section>

      <p className="text-center text-xs text-slate-400 dark:text-slate-500">
        {APP_NAME} v{APP_VERSION}
      </p>
    </div>
  )
}

export default AboutPage
