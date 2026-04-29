import { useState, FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { getTimeline, TimelineResponse } from '../api/client'

const STATES = [
  { code: 'MH', name: 'Maharashtra' }, { code: 'DL', name: 'Delhi' },
  { code: 'KA', name: 'Karnataka' }, { code: 'TN', name: 'Tamil Nadu' },
  { code: 'UP', name: 'Uttar Pradesh' }, { code: 'WB', name: 'West Bengal' },
  { code: 'GJ', name: 'Gujarat' }, { code: 'RJ', name: 'Rajasthan' },
  { code: 'AP', name: 'Andhra Pradesh' }, { code: 'KL', name: 'Kerala' },
]

export default function TimelinePage() {
  const { t } = useTranslation()
  const [stateCode, setStateCode] = useState('')
  const [constituencyId, setConstituencyId] = useState('')
  const [timelines, setTimelines] = useState<TimelineResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSearched(true)

    try {
      const results = await getTimeline(stateCode, constituencyId || undefined)
      setTimelines(results)
    } catch (err: unknown) {
      setTimelines([])
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number } }
        if (axiosErr.response?.status === 404) {
          setError(t('timeline.no_results'))
        } else {
          setError(t('common.error'))
        }
      } else {
        setError(t('common.error'))
      }
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-IN', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    })
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('timeline.title')}</h1>
      <p className="text-gray-600 mb-8">{t('timeline.description')}</p>

      <form onSubmit={handleSearch} className="card space-y-4 mb-8" id="timeline-form">
        <div>
          <label htmlFor="timeline-state" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('timeline.state')}
          </label>
          <select
            id="timeline-state"
            value={stateCode}
            onChange={(e) => setStateCode(e.target.value)}
            required
            className="input-field"
          >
            <option value="">-- {t('timeline.state')} --</option>
            {STATES.map((s) => (
              <option key={s.code} value={s.code}>{s.name} ({s.code})</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="constituency-id" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('timeline.constituency')}
          </label>
          <input
            type="text"
            id="constituency-id"
            value={constituencyId}
            onChange={(e) => setConstituencyId(e.target.value)}
            placeholder="e.g., MH-23"
            className="input-field"
          />
        </div>

        <button
          type="submit"
          id="search-timeline-btn"
          disabled={loading || !stateCode}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading && <span className="spinner" />}
          {t('timeline.search')}
        </button>
      </form>

      {error && (
        <div className="status-ineligible animate-slide-up" id="timeline-error">
          ⚠️ {error}
        </div>
      )}

      {timelines.length > 0 && (
        <div className="space-y-6" id="timeline-results">
          {timelines.map((timeline, idx) => (
            <div key={idx} className="card animate-slide-up" style={{ animationDelay: `${idx * 100}ms` }}>
              <h3 className="font-bold text-lg text-primary-900 mb-4">
                📍 {timeline.constituency_id}
              </h3>
              <div className="relative pl-6 border-l-2 border-primary-200 space-y-4">
                {timeline.events.map((event, eIdx) => (
                  <div key={eIdx} className="relative">
                    <div className="absolute -left-[29px] w-4 h-4 rounded-full bg-primary-500 border-2 border-white" />
                    <div>
                      <p className="font-semibold text-gray-900">{event.phase}</p>
                      <p className="text-sm text-gray-500">{formatDate(event.date)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {searched && timelines.length === 0 && !error && !loading && (
        <p className="text-center text-gray-500 py-8">{t('timeline.no_results')}</p>
      )}
    </div>
  )
}
