import { useState, FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { evaluateEligibility, EligibilityResponse } from '../api/client'
import { INDIAN_STATES } from '../constants/states'

export default function EligibilityPage() {
  const { t } = useTranslation()
  const [dob, setDob] = useState('')
  const [isCitizen, setIsCitizen] = useState(true)
  const [state, setState] = useState('')
  const [isNri, setIsNri] = useState(false)
  const [result, setResult] = useState<EligibilityResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)

    try {
      const response = await evaluateEligibility({
        dob,
        is_citizen: isCitizen,
        state_of_residence: state,
        is_nri: isNri,
      })
      setResult(response)
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : t('common.error')
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('eligibility.title')}</h1>
      <p className="text-gray-600 mb-8">{t('eligibility.description')}</p>

      <form onSubmit={handleSubmit} className="card space-y-6" id="eligibility-form">
        {/* Date of Birth */}
        <div>
          <label htmlFor="dob" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.dob')}
          </label>
          <input
            type="date"
            id="dob"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            required
            max={new Date().toISOString().split('T')[0]}
            className="input-field"
          />
        </div>

        {/* Citizenship */}
        <div>
          <div id="citizen-label" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.citizen')}
          </div>
          <div className="flex gap-4" role="radiogroup" aria-labelledby="citizen-label">
            <button
              type="button"
              id="citizen-yes"
              onClick={() => setIsCitizen(true)}
              role="radio"
              aria-checked={isCitizen}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                isCitizen
                  ? 'bg-primary-700 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('eligibility.yes')}
            </button>
            <button
              type="button"
              id="citizen-no"
              onClick={() => setIsCitizen(false)}
              role="radio"
              aria-checked={!isCitizen}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                !isCitizen
                  ? 'bg-primary-700 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('eligibility.no')}
            </button>
          </div>
        </div>

        {/* State */}
        <div>
          <label htmlFor="state" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.state')}
          </label>
          <select
            id="state"
            value={state}
            onChange={(e) => setState(e.target.value)}
            required
            className="input-field"
          >
            <option value="">-- {t('timeline.state')} --</option>
            {INDIAN_STATES.map((s) => (
              <option key={s.code} value={s.code}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>
        </div>

        {/* NRI Status */}
        <div>
          <div id="nri-label" className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.nri')}
          </div>
          <div className="flex gap-4" role="radiogroup" aria-labelledby="nri-label">
            <button
              type="button"
              id="nri-yes"
              onClick={() => setIsNri(true)}
              role="radio"
              aria-checked={isNri}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                isNri ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('eligibility.yes')}
            </button>
            <button
              type="button"
              id="nri-no"
              onClick={() => setIsNri(false)}
              role="radio"
              aria-checked={!isNri}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                !isNri ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('eligibility.no')}
            </button>
          </div>
        </div>

        <button
          type="submit"
          id="check-eligibility-btn"
          disabled={loading || !dob || !state}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading && <span className="spinner" aria-hidden="true" />}
          {t('eligibility.check')}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div
          className="mt-6 status-ineligible animate-slide-up"
          id="eligibility-error"
          role="alert"
        >
          <span aria-hidden="true">⚠️</span> {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div
          className={`mt-6 animate-slide-up ${result.eligible ? 'status-eligible' : 'status-ineligible'}`}
          id="eligibility-result"
          role="status"
          aria-live="polite"
        >
          <p className="text-lg font-bold mb-2">
            <span aria-hidden="true">{result.eligible ? '✅' : '❌'}</span>{' '}
            {result.eligible ? t('eligibility.eligible') : t('eligibility.not_eligible')}
          </p>
          {result.required_form && (
            <p className="mb-2">
              <span className="font-semibold">{t('eligibility.form_required')}:</span>{' '}
              {result.required_form}
            </p>
          )}
          <p className="text-sm">{result.reasoning}</p>
          {result.eligible_from_year && (
            <p className="mt-2 text-sm font-medium">
              <span aria-hidden="true">📅</span> Eligible from: {result.eligible_from_year}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
