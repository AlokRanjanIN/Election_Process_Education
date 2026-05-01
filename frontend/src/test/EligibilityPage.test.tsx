import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EligibilityPage from '../components/EligibilityPage'
import { evaluateEligibility } from '../api/client'

vi.mock('../api/client', () => ({
  evaluateEligibility: vi.fn(),
}))

const mockedEvaluateEligibility = vi.mocked(evaluateEligibility)

describe('EligibilityPage', () => {
  beforeEach(() => {
    mockedEvaluateEligibility.mockReset()
  })

  it('submits voter details and announces the result', async () => {
    const user = userEvent.setup()
    mockedEvaluateEligibility.mockResolvedValue({
      eligible: true,
      required_form: 'Form 6',
      reasoning: 'User is over 18 and an Indian citizen.',
      eligible_from_year: null,
    })

    render(<EligibilityPage />)

    await user.type(screen.getByLabelText(/date of birth/i), '2000-01-01')
    await user.selectOptions(screen.getByLabelText(/state of residence/i), 'MH')
    await user.click(screen.getByRole('button', { name: /check eligibility/i }))

    await waitFor(() => {
      expect(mockedEvaluateEligibility).toHaveBeenCalledWith({
        dob: '2000-01-01',
        is_citizen: true,
        state_of_residence: 'MH',
        is_nri: false,
      })
    })
    expect(await screen.findByRole('status')).toHaveTextContent(/eligible to vote/i)
  })
})
