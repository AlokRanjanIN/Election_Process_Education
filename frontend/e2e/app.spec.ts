import { expect, test } from '@playwright/test'

test.describe('Accessibility and Internationalization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('has skip to main content link', async ({ page }) => {
    const skipLink = page.locator('.skip-link')
    await expect(skipLink).toBeAttached()
    // Tab to it
    await page.keyboard.press('Tab')
    await expect(skipLink).toBeVisible()
    await expect(skipLink).toHaveAttribute('href', '#main-content')
  })

  test('toggles language and updates html lang attribute', async ({ page }) => {
    // Initial state (English)
    await expect(page.locator('html')).toHaveAttribute('lang', 'en')
    await expect(page.locator('h1')).toContainText('Indian Election')

    // Click language toggle
    await page.click('#language-toggle')
    
    // Check Hindi state
    await expect(page.locator('html')).toHaveAttribute('lang', 'hi')
    // Title should change (assuming translation key exists)
    await expect(page.locator('#language-toggle')).toContainText('English')
  })

  test('navigates to all pages without errors', async ({ page }) => {
    const navLinks = ['#nav-eligibility', '#nav-guide', '#nav-timeline', '#nav-faq']
    for (const id of navLinks) {
      await page.click(id)
      await expect(page).not.toHaveURL(/.*error.*/)
    }
  })
})

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
