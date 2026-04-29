import { useState, FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { evaluateEligibility, EligibilityResponse } from '../api/client'

const STATES = [
  { code: 'AN', name: 'Andaman & Nicobar' }, { code: 'AP', name: 'Andhra Pradesh' },
  { code: 'AR', name: 'Arunachal Pradesh' }, { code: 'AS', name: 'Assam' },
  { code: 'BR', name: 'Bihar' }, { code: 'CH', name: 'Chandigarh' },
  { code: 'CT', name: 'Chhattisgarh' }, { code: 'DD', name: 'Daman & Diu' },
  { code: 'DL', name: 'Delhi' }, { code: 'GA', name: 'Goa' },
  { code: 'GJ', name: 'Gujarat' }, { code: 'HP', name: 'Himachal Pradesh' },
  { code: 'HR', name: 'Haryana' }, { code: 'JH', name: 'Jharkhand' },
  { code: 'JK', name: 'Jammu & Kashmir' }, { code: 'KA', name: 'Karnataka' },
  { code: 'KL', name: 'Kerala' }, { code: 'LA', name: 'Ladakh' },
  { code: 'LD', name: 'Lakshadweep' }, { code: 'MH', name: 'Maharashtra' },
  { code: 'ML', name: 'Meghalaya' }, { code: 'MN', name: 'Manipur' },
  { code: 'MP', name: 'Madhya Pradesh' }, { code: 'MZ', name: 'Mizoram' },
  { code: 'NL', name: 'Nagaland' }, { code: 'OD', name: 'Odisha' },
  { code: 'PB', name: 'Punjab' }, { code: 'PY', name: 'Puducherry' },
  { code: 'RJ', name: 'Rajasthan' }, { code: 'SK', name: 'Sikkim' },
  { code: 'TN', name: 'Tamil Nadu' }, { code: 'TG', name: 'Telangana' },
  { code: 'TR', name: 'Tripura' }, { code: 'UK', name: 'Uttarakhand' },
  { code: 'UP', name: 'Uttar Pradesh' }, { code: 'WB', name: 'West Bengal' },
]

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
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.citizen')}
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              id="citizen-yes"
              onClick={() => setIsCitizen(true)}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                isCitizen ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('eligibility.yes')}
            </button>
            <button
              type="button"
              id="citizen-no"
              onClick={() => setIsCitizen(false)}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                !isCitizen ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
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
            {STATES.map((s) => (
              <option key={s.code} value={s.code}>{s.name} ({s.code})</option>
            ))}
          </select>
        </div>

        {/* NRI Status */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            {t('eligibility.nri')}
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              id="nri-yes"
              onClick={() => setIsNri(true)}
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
          {loading && <span className="spinner" />}
          {t('eligibility.check')}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="mt-6 status-ineligible animate-slide-up" id="eligibility-error">
          ⚠️ {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className={`mt-6 animate-slide-up ${result.eligible ? 'status-eligible' : 'status-ineligible'}`} id="eligibility-result">
          <p className="text-lg font-bold mb-2">
            {result.eligible ? `✅ ${t('eligibility.eligible')}` : `❌ ${t('eligibility.not_eligible')}`}
          </p>
          {result.required_form && (
            <p className="mb-2">
              <span className="font-semibold">{t('eligibility.form_required')}:</span> {result.required_form}
            </p>
          )}
          <p className="text-sm">{result.reasoning}</p>
          {result.eligible_from_year && (
            <p className="mt-2 text-sm font-medium">
              📅 Eligible from: {result.eligible_from_year}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
