import axios, { AxiosInstance } from 'axios'

/** Typed API client for the Election Assistant backend. */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// --- Request Types ---

export interface EligibilityRequest {
  dob: string
  is_citizen: boolean
  state_of_residence: string
  is_nri: boolean
}

export interface FAQRequest {
  query: string
  locale: string
}

// --- Response Types ---

export interface EligibilityResponse {
  eligible: boolean
  required_form: string | null
  reasoning: string
  eligible_from_year: number | null
}

export interface GuideLink {
  type: string
  url: string
  label: string | null
}

export interface GuideResponse {
  current_state: string
  next_state: string
  instructions: string
  links: GuideLink[]
  step_number: number
  total_steps: number
}

export interface TimelineEvent {
  phase: string
  date: string
}

export interface TimelineResponse {
  constituency_id: string
  events: TimelineEvent[]
}

export interface Citation {
  title: string
  url: string
}

export interface FAQResponse {
  answer: string
  citations: Citation[]
  locale: string | null
}

// --- API Functions ---

export async function evaluateEligibility(data: EligibilityRequest): Promise<EligibilityResponse> {
  const response = await apiClient.post<EligibilityResponse>('/api/v1/eligibility/evaluate', data)
  return response.data
}

export async function getGuideNextStep(currentState: string = 'INIT'): Promise<GuideResponse> {
  const response = await apiClient.get<GuideResponse>('/api/v1/guide/next-step', {
    params: { current_state: currentState },
  })
  return response.data
}

export async function getTimeline(stateCode: string, constituencyId?: string): Promise<TimelineResponse[]> {
  const params: Record<string, string> = { state_code: stateCode }
  if (constituencyId) params.constituency_id = constituencyId
  const response = await apiClient.get<TimelineResponse[]>('/api/v1/timeline', { params })
  return response.data
}

export async function askFAQ(data: FAQRequest): Promise<FAQResponse> {
  const response = await apiClient.post<FAQResponse>('/api/v1/faq/ask', data)
  return response.data
}

export default apiClient
