import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const features = [
  {
    path: '/eligibility',
    icon: '✅',
    titleKey: 'nav.eligibility',
    descKey: 'eligibility.description',
    color: 'from-green-500 to-emerald-600',
  },
  {
    path: '/guide',
    icon: '📋',
    titleKey: 'nav.guide',
    descKey: 'guide.description',
    color: 'from-blue-500 to-indigo-600',
  },
  {
    path: '/timeline',
    icon: '📅',
    titleKey: 'nav.timeline',
    descKey: 'timeline.description',
    color: 'from-purple-500 to-violet-600',
  },
  {
    path: '/faq',
    icon: '💬',
    titleKey: 'nav.faq',
    descKey: 'faq.description',
    color: 'from-orange-500 to-amber-600',
  },
]

export default function HomePage() {
  const { t } = useTranslation()

  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-800 via-primary-900 to-indigo-950 text-white py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 leading-tight">
            <span aria-hidden="true">🗳️</span> {t('app.title')}
          </h1>
          <p className="text-xl sm:text-2xl text-primary-200 mb-2">{t('app.subtitle')}</p>
          <p className="text-primary-300 text-sm mt-4">{t('app.tagline')}</p>
          <Link
            to="/eligibility"
            id="hero-cta"
            className="inline-block mt-8 bg-accent-500 hover:bg-accent-600 text-white font-bold px-8 py-4 rounded-xl text-lg transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          >
            {t('eligibility.check')} <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Link
              key={feature.path}
              to={feature.path}
              id={`feature-${feature.path.slice(1)}`}
              className="card group cursor-pointer animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div
                className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-200`}
              >
                <span aria-hidden="true">{feature.icon}</span>
              </div>
              <h2 className="text-lg font-bold text-gray-900 mb-2">{t(feature.titleKey)}</h2>
              <p className="text-gray-600 text-sm leading-relaxed">{t(feature.descKey)}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Helpline Banner */}
      <section className="bg-accent-50 border-t border-accent-200 py-6 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-accent-800 font-semibold">
            <span aria-hidden="true">📞</span> {t('common.helpline')}
          </p>
        </div>
      </section>
    </div>
  )
}
