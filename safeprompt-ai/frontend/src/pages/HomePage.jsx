import HeroSection from '../components/Home/HeroSection.jsx'
import StatsSection from '../components/Home/StatsSection.jsx'
import FeaturesSection from '../components/Home/FeaturesSection.jsx'
import HowItWorksSection from '../components/Home/HowItWorksSection.jsx'
import CTASection from '../components/Home/CTASection.jsx'

/**
 * Landing page. Composed of independent, reusable sections so each piece
 * (hero, stats, features, how-it-works, CTA) can evolve or be reordered
 * without touching the others.
 */
function HomePage() {
  return (
    <div>
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
    </div>
  )
}

export default HomePage
