/**
 * Quick test: verify Reports page shows runs without requiring template selection
 */
import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:9071'

test.describe('Reports Page — Runs Visibility', () => {
  test.setTimeout(60_000)

  test('Reports page shows recent runs on load (no template selection needed)', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`, { waitUntil: 'networkidle', timeout: 20_000 })

    // Wait for Recent Runs section
    await expect(page.locator('text=Recent Runs').first()).toBeVisible({ timeout: 10_000 })

    // Wait for the async fetch to complete
    await page.waitForTimeout(4000)

    // Take screenshot
    await page.screenshot({ path: 'playwright-results/reports-page-runs.png', fullPage: true })

    // Check page content for run data
    const content = await page.content()

    // Check for Analyze buttons which appear per-run
    const analyzeButtons = page.locator('button:has-text("Analyze")')
    const analyzeCount = await analyzeButtons.count()
    console.log(`Analyze buttons found: ${analyzeCount}`)

    // Check for template name or date content from the runs
    const hasHmwssb = content.includes('hmwssb') || content.includes('HMWSSB')
    const hasDates = content.includes('2020-01-01') || content.includes('2030-12-31')
    console.log(`Has hmwssb: ${hasHmwssb}, has dates: ${hasDates}, analyze btns: ${analyzeCount}`)

    expect(analyzeCount).toBeGreaterThan(0)
  })

  test('Clicking Analyze navigates to agents with run ID', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`, { waitUntil: 'networkidle', timeout: 20_000 })
    await page.waitForTimeout(4000)

    // Find any Analyze button
    const analyzeBtn = page.locator('button:has-text("Analyze")').first()
    const count = await analyzeBtn.count()
    if (count === 0) {
      test.skip()
      return
    }

    await analyzeBtn.click()

    // Should navigate to agents page with analyzeRunId param
    await page.waitForURL(/\/agents/, { timeout: 10_000 })
    expect(page.url()).toContain('analyzeRunId=')

    // Report Analyst should be auto-selected
    await expect(page.locator('text=Report Analyst Configuration')).toBeVisible({ timeout: 10_000 })
  })
})
