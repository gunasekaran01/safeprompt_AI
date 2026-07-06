# Build Progress

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Project setup | ✅ Complete |
| 2 | React routing | ✅ Complete |
| 3 | Landing page | ✅ Complete |
| 4 | Dashboard | ✅ Complete |
| 5 | Prompt Analyzer | ⬜ Not started |
| 6 | Backend API | ⬜ Not started |
| 7 | Prompt Injection Detector | ⬜ Not started |
| 8 | Toxicity Detector | ⬜ Not started |
| 9 | Safety Score Engine | ⬜ Not started |
| 10 | SQLite database | ⬜ Not started |
| 11 | History | ⬜ Not started |
| 12 | Charts | ⬜ Not started |
| 13 | PDF Report | ⬜ Not started |
| 14 | Deployment | ⬜ Not started |
| 15 | Documentation | ⬜ Not started |

## Milestone 1 Notes

- Created monorepo structure: `frontend/`, `backend/`, `datasets/`, `reports/`.
- Frontend: Vite + React + Tailwind CSS configured, dark mode wired via a
  real `<html class="dark">` toggle, base component styles (`.card`,
  `.btn-primary`, `.btn-secondary`) defined in `index.css`.
- Backend: FastAPI app boots with CORS configured for the Vite dev server,
  centralized settings via `pydantic-settings`, and a `/api/health`
  endpoint for verification. Swagger UI available at `/api/docs`.
- No business logic yet — routing, pages, and detection services are
  intentionally deferred to their respective milestones.

## Milestone 2 Notes

- Added `react-router-dom` routing via `BrowserRouter` in `main.jsx` and a
  route table in `App.jsx`: `/`, `/dashboard`, `/analyzer`, `/history`,
  `/about`, `/settings`, plus a catch-all 404.
- Built a persistent `Layout` (Navbar + `<Outlet />` + Footer) so chrome
  stays mounted across page transitions.
- `Navbar` has active-link styling, a responsive mobile menu, and a
  light/dark toggle; nav items are centrally defined in
  `utils/navigation.js`.
- Upgraded theme handling to a tri-state (light/dark/system)
  `ThemeContext` with live OS-preference tracking and localStorage
  persistence, consumed by both the Navbar toggle and the new Settings
  page.
- Added a reusable `useLocalStorage` hook, used by Settings for
  Compact Mode and Auto-Analyze-on-Paste preferences (functional, no
  backend needed).
- `HomePage`, `DashboardPage`, `AnalyzerPage`, `HistoryPage` are real,
  routable pages with accurate interim content, since each has a
  dedicated future milestone (3, 4, 5, 11 respectively).
- `AboutPage` and `SettingsPage` have **no** dedicated milestone, so they
  were built fully complete and functional now, not as interim content.
- `NotFoundPage` (404) is fully built.
- Verified: `npm run build` compiles cleanly, `eslint` passes with 0
  errors, and all 7 routes (including an invalid path) return HTTP 200
  from a production `vite preview` server, confirming SPA routing works
  end-to-end.

## Milestone 3 Notes

- Replaced the interim `HomePage.jsx` with a fully built landing page,
  composed from five independent, reusable section components under
  `components/Home/`:
  - `HeroSection` — headline, subtext, primary/secondary CTAs, trust
    badges, and a static demo "sample analysis" result card illustrating
    the product output (score, injection/toxicity status, recommendation).
  - `StatsSection` — quick numeric highlights (detection engines, score
    scale, risk levels, explainability).
  - `FeaturesSection` — 6-card grid built on the new reusable
    `FeatureCard` component, covering injection detection, jailbreak
    detection, toxicity detection, safety scoring, the dashboard, and PDF
    reports.
  - `HowItWorksSection` — 3-step explainer (submit → analyze → report).
  - `CTASection` — closing call-to-action banner linking to the analyzer.
- Fixed an invalid Tailwind color reference (`brand-950`, which isn't
  defined in `tailwind.config.js`) caught while reviewing the hero
  gradient — corrected to `brand-900`.
- Verified: `npm run build` compiles cleanly (60 modules), `eslint`
  passes with 0 errors, and all 7 routes still return HTTP 200 against a
  production `vite preview` server after the changes.

## Milestone 4 Notes

- Added a service layer (`services/dashboardService.js` +
  `services/mockData.js`) that returns realistic mock data shaped
  *exactly* like the real API response Milestones 6 (Backend API) and 10
  (SQLite database) will eventually provide — `getDashboardStats()` and
  `getRecentActivity(limit)`, both async with a simulated network delay.
  No component talks to mock data directly, so repointing these two
  functions at real `axios` calls later requires zero changes elsewhere.
- Added `utils/riskLevels.js`: a shared risk-level config (label, color
  classes, icon, score threshold) mirroring the backend's threshold
  settings in `core/config.py`, plus `getRiskLevelFromScore()`. This is
  the single source of truth for risk display, reused by the new
  `RiskBadge` component and ready for Analyzer/History to consume later.
- Added `utils/formatters.js` (relative time, text truncation, score/count
  formatting) as shared, reusable utilities.
- Built `StatCard` / `StatsGrid` — 6 stat cards (Total Analyses, Safe
  Prompts, Unsafe Prompts, Injection Attempts, Toxic Prompts, Avg. Safety
  Score) with matching loading skeletons.
- Built `RecentActivityTable` — a responsive table of the latest analyses
  with relative timestamps, scores, and `RiskBadge`s, plus loading and
  empty states, linking to `/history`.
- Built `ChartsPlaceholder` — clearly scoped reserved space for the
  Chart.js visualizations that are their own milestone (12), using the
  existing `MilestoneNotice` component rather than a vague TODO.
- Rewrote `DashboardPage.jsx` with real `useEffect`-driven data loading,
  a working Refresh button, and error handling with a Retry action —
  production-shaped state management, not a static mock.
- Verified: `npm run build` compiles cleanly (69 modules), `eslint`
  passes with 0 errors, a standalone Node script exercised
  `dashboardService`, `formatters`, and `riskLevels` directly to confirm
  correct data shapes and threshold behavior (e.g. score 96 → "safe",
  30 → "high"), and all 6 routes still return HTTP 200 from a production
  `vite preview` server.
