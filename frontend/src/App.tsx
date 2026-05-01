import { Suspense, lazy, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import ErrorBoundary from './components/ErrorBoundary'
import { usePageMetadata } from './hooks/usePageMetadata'

const EligibilityPage = lazy(() => import('./components/EligibilityPage'))
const GuidePage = lazy(() => import('./components/GuidePage'))
const TimelinePage = lazy(() => import('./components/TimelinePage'))
const FAQPage = lazy(() => import('./components/FAQPage'))
const HomePage = lazy(() => import('./components/HomePage'))

function NavBar() {
  const { t, i18n } = useTranslation()
  const location = useLocation()

  const links = [
    { path: '/', label: t('nav.home'), id: 'nav-home' },
    { path: '/eligibility', label: t('nav.eligibility'), id: 'nav-eligibility' },
    { path: '/guide', label: t('nav.guide'), id: 'nav-guide' },
    { path: '/timeline', label: t('nav.timeline'), id: 'nav-timeline' },
    { path: '/faq', label: t('nav.faq'), id: 'nav-faq' },
  ]

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'hi' : 'en'
    i18n.changeLanguage(newLang)
  }

  return (
    <nav className="bg-primary-900 text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-bold text-lg min-h-0">
            <span className="text-2xl" aria-hidden="true">
              🗳️
            </span>
            <span className="hidden sm:inline">{t('app.title')}</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1 overflow-x-auto">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                id={link.id}
                aria-current={location.pathname === link.path ? 'page' : undefined}
                className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors min-h-0
                  ${
                    location.pathname === link.path
                      ? 'bg-primary-700 text-white'
                      : 'text-primary-200 hover:bg-primary-800 hover:text-white'
                  }`}
              >
                {link.label}
              </Link>
            ))}

            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              id="language-toggle"
              className="ml-2 px-3 py-2 rounded-lg text-sm font-medium bg-accent-600 hover:bg-accent-700 transition-colors min-h-0 min-w-0"
              aria-label={t('common.language')}
            >
              {i18n.language === 'en' ? 'हिन्दी' : 'English'}
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function Footer() {
  const { t } = useTranslation()
  return (
    <footer className="bg-gray-800 text-gray-300 py-8 mt-auto">
      <div className="max-w-6xl mx-auto px-4 text-center">
        <p className="text-sm">{t('app.tagline')}</p>
        <p className="text-xs mt-2 text-gray-500">{t('common.helpline')}</p>
        <p className="text-xs mt-1 text-gray-500">
          © {new Date().getFullYear()} Election Guide India — Not affiliated with ECI
        </p>
      </div>
    </footer>
  )
}

function AppContent() {
  const { t } = useTranslation()
  usePageMetadata()

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <NavBar />
      <main id="main-content" className="flex-grow focus:outline-none" tabIndex={-1}>
        <ErrorBoundary>
          <Suspense
            fallback={
              <div className="max-w-6xl mx-auto px-4 py-8 text-gray-600" role="status">
                {t('common.loading')}
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/eligibility" element={<EligibilityPage />} />
              <Route path="/guide" element={<GuidePage />} />
              <Route path="/timeline" element={<TimelinePage />} />
              <Route path="/faq" element={<FAQPage />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </main>
      <Footer />
    </div>
  )
}

export default function App() {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    document.documentElement.lang = i18n.language
  }, [i18n.language])

  return (
    <BrowserRouter>
      <a href="#main-content" className="skip-link">
        {t('common.skip_to_main')}
      </a>
      <AppContent />
    </BrowserRouter>
  )
}
