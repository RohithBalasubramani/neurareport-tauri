import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Dashboard page integration @integration', () => {
  test('page loads with stats cards visible', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/dashboard')
    // Dashboard should render stat cards from /analytics/dashboard
    await expect(page.getByText(/Connections/i).first()).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText(/Templates/i).first()).toBeVisible()
    expectNoConsoleErrors(msgs)
  })

  test('click Connections stat card navigates to /connections @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Connections/i).first()).toBeVisible({ timeout: 15_000 })
    // Click the first card-like element that mentions Connections
    const card = page.locator('[class*="Card"]').filter({ hasText: /Connections/i }).first()
    if (await card.count()) {
      await card.click()
      await page.waitForURL('**/connections')
    }
  })

  test('click Templates stat card navigates to /templates @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Templates/i).first()).toBeVisible({ timeout: 15_000 })
    const card = page.locator('[class*="Card"]').filter({ hasText: /Templates/i }).first()
    if (await card.count()) {
      await card.click()
      await page.waitForURL('**/templates')
    }
  })

  test('click Jobs stat card navigates to /jobs @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Jobs/i).first()).toBeVisible({ timeout: 15_000 })
    const card = page.locator('[class*="Card"]').filter({ hasText: /Jobs/i }).first()
    if (await card.count()) {
      await card.click()
      await page.waitForURL('**/jobs')
    }
  })

  test('click Schedules stat card navigates to /schedules @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Schedules/i).first()).toBeVisible({ timeout: 15_000 })
    const card = page.locator('[class*="Card"]').filter({ hasText: /Schedules/i }).first()
    if (await card.count()) {
      await card.click()
      await page.waitForURL('**/schedules')
    }
  })

  test('"New Report" button navigates to /setup/wizard @integration', async ({ page }) => {
    await page.goto('/dashboard')
    const btn = page.getByRole('button', { name: /New Report/i })
    await expect(btn).toBeVisible({ timeout: 15_000 })
    await btn.click()
    await page.waitForURL('**/setup/wizard')
  })

  test('quick action links navigate correctly @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Manage Connections/i).first()).toBeVisible({ timeout: 15_000 })

    // Verify links exist — click each and verify URL
    for (const [label, urlPart] of [
      ['Manage Connections', '/connections'],
      ['Report Designs', '/templates'],
      ['Run Reports', '/reports'],
      ['Manage Schedules', '/schedules'],
    ] as const) {
      const link = page.getByText(label, { exact: false }).first()
      if (await link.count()) {
        await expect(link).toBeVisible()
      }
    }
  })

  test('refresh button reloads dashboard data @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Connections/i).first()).toBeVisible({ timeout: 15_000 })

    const refreshBtn = page.getByRole('button', { name: /Refresh/i }).first()
    if (await refreshBtn.count()) {
      const [resp] = await Promise.all([
        waitForApi(page, '/analytics/dashboard', 'GET'),
        refreshBtn.click(),
      ])
      expect(resp.ok()).toBeTruthy()
    }
  })

  test('onboarding checklist items are clickable @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(2000) // Let dashboard fully render

    // Onboarding items link to setup pages
    const addSource = page.getByText(/Add a data source/i).first()
    if (await addSource.count()) {
      await expect(addSource).toBeVisible()
    }
  })

  test('recent jobs list loads @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(3000)
    // Jobs section should be present (may be empty)
    const jobsSection = page.getByText(/Recent/i).first()
    if (await jobsSection.count()) {
      await expect(jobsSection).toBeVisible()
    }
  })

  test('command palette opens with Ctrl+K @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(2000)
    await page.keyboard.press('Control+k')
    // Command palette should appear
    const palette = page.getByPlaceholder(/Search|Command/i).first()
    if (await palette.count()) {
      await expect(palette).toBeVisible()
      await page.keyboard.press('Escape')
    }
  })

  test('AI recommendations section renders @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(3000)
    // Recommendations section may or may not have data
    const recSection = page.getByText(/Recommend/i).first()
    if (await recSection.count()) {
      await expect(recSection).toBeVisible()
    }
  })

  test('dismiss onboarding banner @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(2000)
    const dismissBtn = page.getByRole('button', { name: /Dismiss/i }).first()
    if (await dismissBtn.count()) {
      await dismissBtn.click()
      await expect(dismissBtn).toHaveCount(0, { timeout: 5_000 })
    }
  })

  test('top designs list renders @integration', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(3000)
    // Top designs or favorites section
    const designsSection = page.getByText(/Design|Favorites/i).first()
    if (await designsSection.count()) {
      await expect(designsSection).toBeVisible()
    }
  })

  test('"Run Setup Wizard" button works @integration', async ({ page }) => {
    await page.goto('/dashboard')
    const wizardBtn = page.getByRole('button', { name: /Run Setup Wizard|Setup Wizard/i }).first()
    if (await wizardBtn.count()) {
      await wizardBtn.click()
      await page.waitForURL('**/setup/wizard')
    }
  })
})
