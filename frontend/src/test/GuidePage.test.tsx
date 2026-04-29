import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import GuidePage from '../components/GuidePage'
import { getGuideNextStep } from '../api/client'

vi.mock('../api/client', () => ({
  getGuideNextStep: vi.fn(),
}))

const mockedGetGuideNextStep = vi.mocked(getGuideNextStep)

describe('GuidePage', () => {
  beforeEach(() => {
    mockedGetGuideNextStep.mockReset()
  })

  it('loads a step and advances through the guide', async () => {
    const user = userEvent.setup()
    mockedGetGuideNextStep
      .mockResolvedValueOnce({
        current_state: 'INIT',
        next_state: 'FORM_6',
        instructions: 'Start your voter registration.',
        links: [],
        step_number: 1,
        total_steps: 2,
      })
      .mockResolvedValueOnce({
        current_state: 'FORM_6',
        next_state: 'COMPLETE',
        instructions: 'Submit Form 6.',
        links: [{ type: 'portal', url: 'https://voters.eci.gov.in/', label: 'Voter Portal' }],
        step_number: 2,
        total_steps: 2,
      })

    render(<GuidePage />)

    expect(await screen.findByText(/start your voter registration/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /next step/i }))

    expect(mockedGetGuideNextStep).toHaveBeenCalledWith('FORM_6')
    expect(await screen.findByText(/submit form 6/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /voter portal/i })).toHaveAttribute(
      'href',
      'https://voters.eci.gov.in/',
    )
  })
})
