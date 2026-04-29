import { expect, test } from '@playwright/test'

test('supports the main voter education flow', async ({ page }) => {
  await page.route('**/api/v1/eligibility/evaluate', async (route) => {
    await route.fulfill({
      json: {
        eligible: true,
        required_form: 'Form 6',
        reasoning: 'User is over 18 and an Indian citizen.',
        eligible_from_year: null,
      },
    })
  })

  await page.goto('/')
  await expect(page.getByRole('heading', { name: /election guide india/i })).toBeVisible()

  await page
    .getByRole('link', { name: /check eligibility/i })
    .first()
    .click()
  await page.getByLabel(/date of birth/i).fill('2000-01-01')
  await page.getByLabel(/state of residence/i).selectOption('MH')
  await page.getByRole('button', { name: /check eligibility/i }).click()

  await expect(page.getByRole('status')).toContainText(/eligible to vote/i)
})
