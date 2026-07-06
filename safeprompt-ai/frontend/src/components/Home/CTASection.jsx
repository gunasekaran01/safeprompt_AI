import { Link } from 'react-router-dom'
import { FiArrowRight } from 'react-icons/fi'

function CTASection() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="rounded-2xl bg-brand-600 px-6 py-14 text-center shadow-card sm:px-12">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">
          Ready to check your first prompt?
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-brand-100">
          It takes seconds to get a full safety breakdown — injection status,
          toxicity status, score, and recommendation.
        </p>
        <div className="mt-8">
          <Link
            to="/analyzer"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-brand-700 shadow-sm transition-colors hover:bg-brand-50"
          >
            Go to Analyzer <FiArrowRight />
          </Link>
        </div>
      </div>
    </section>
  )
}

export default CTASection
