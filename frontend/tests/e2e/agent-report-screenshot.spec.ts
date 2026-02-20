/**
 * Screenshot test: capture the structured Report Analyst result rendering.
 */
import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:9071'
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:9070'

test.describe('Report Analyst Screenshot', () => {
  test.setTimeout(180_000)

  let testRunId: string | null = null

  test.beforeAll(async ({ request }) => {
    try {
      const response = await request.get(`${BACKEND_URL}/api/v1/reports/runs?limit=5`)
      const data = await response.json()
      const runs = data?.runs || data || []
      if (Array.isArray(runs) && runs.length > 0) {
        const runWithArtifacts = runs.find((r: any) => r.artifacts?.html_url) || runs[0]
        testRunId = runWithArtifacts.id
      }
    } catch {}
  })

  test('capture structured result screenshot', async ({ page }) => {
    if (!testRunId) {
      test.skip()
      return
    }

    await page.goto(`${BASE_URL}/agents?analyzeRunId=${testRunId}`, {
      waitUntil: 'networkidle',
      timeout: 20_000,
    })

    // Wait for config to load
    await expect(page.locator('text=Report Analyst Configuration')).toBeVisible({ timeout: 10_000 })

    // Run the analysis
    const runButton = page.locator('button:has-text("Run Report Analyst")')
    await runButton.click()

    // Wait for result
    await expect(page.locator('text=Result').first()).toBeVisible({ timeout: 150_000 })
    await page.waitForTimeout(3000)

    // Use Playwright's locator to scroll the result into view
    const summaryLocator = page.locator('text=Summary').first()
    if (await summaryLocator.count() > 0) {
      await summaryLocator.scrollIntoViewIfNeeded()
      await page.waitForTimeout(1000)
    } else {
      // Fallback: find any element in the result area
      const resultLocator = page.locator('text=completed').first()
      if (await resultLocator.count() > 0) {
        await resultLocator.scrollIntoViewIfNeeded()
        await page.waitForTimeout(1000)
      }
    }

    // Take a screenshot of the result area
    await page.screenshot({
      path: 'playwright-results/report-analyst-result.png',
    })

    // Also take a screenshot of just the result section (element-level)
    const resultPaper = page.locator('[data-testid="agent-copy-result-button"]').locator('..').locator('..').locator('..')
    if (await resultPaper.count() > 0) {
      await resultPaper.first().screenshot({
        path: 'playwright-results/report-analyst-result-section.png',
      })
    }
  })
})
