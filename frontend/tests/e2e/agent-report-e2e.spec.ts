/**
 * End-to-end test: Agent-Report integration with real backend calls.
 *
 * This test runs the Report Analyst agent against a real report run
 * through the frontend UI and verifies the structured result rendering.
 */
import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:9071'
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:9070'

test.describe('Agent-Report E2E with Backend', () => {
  test.setTimeout(180_000) // 3 min — LLM calls can be slow

  let testRunId: string | null = null

  test.beforeAll(async ({ request }) => {
    // Find a report run to use for testing
    try {
      const response = await request.get(`${BACKEND_URL}/api/v1/reports/runs?limit=5`)
      const data = await response.json()
      const runs = data?.runs || data || []
      if (Array.isArray(runs) && runs.length > 0) {
        // Pick a run that has artifacts (html_url)
        const runWithArtifacts = runs.find((r: any) => r.artifacts?.html_url) || runs[0]
        testRunId = runWithArtifacts.id
      }
    } catch {
      // No runs available
    }
  })

  test('Backend health check — agents v2', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/agents/v2/health`)
    expect(response.ok()).toBe(true)
    const data = await response.json()
    expect(data.status).toBeTruthy()
  })

  test('Backend lists agent types including report_analyst', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/agents/v2/types`)
    expect(response.ok()).toBe(true)
    const data = await response.json()
    const types = data?.types || data || []
    const reportAnalyst = types.find((t: any) => t.id === 'report_analyst' || t.type === 'report_analyst' || t.name === 'report_analyst')
    expect(reportAnalyst).toBeTruthy()
  })

  test('Run Report Analyst via frontend and verify structured results', async ({ page }) => {
    if (!testRunId) {
      test.skip()
      return
    }

    // Navigate to agents page with deep link
    await page.goto(`${BASE_URL}/agents?analyzeRunId=${testRunId}`, {
      waitUntil: 'networkidle',
      timeout: 20_000,
    })

    // Verify Report Analyst is selected and run ID is pre-filled
    await expect(page.locator('text=Report Analyst Configuration')).toBeVisible({ timeout: 10_000 })

    const runInput = page.locator('label:has-text("Report Run")').locator('..').locator('input').first()
    await expect(runInput).toHaveValue(testRunId, { timeout: 5_000 })

    // Click the Run button
    const runButton = page.locator('button:has-text("Run Report Analyst")')
    await expect(runButton).toBeEnabled({ timeout: 5_000 })
    await runButton.click()

    // Wait for the result to appear (LLM call, may take up to 2 minutes)
    const resultHeader = page.locator('text=Result').first()
    await expect(resultHeader).toBeVisible({ timeout: 150_000 })
    // Scroll to bottom to reveal structured content
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(2000) // Give structured rendering time to complete

    // Check full page content for structured rendering (regardless of viewport)
    const pageContent = await page.content()
    const hasSummary = pageContent.includes('>Summary<')
    const hasKeyFindings = pageContent.includes('Key Findings')
    const hasDataHighlights = pageContent.includes('Data Highlights')
    const hasRecommendations = pageContent.includes('Recommendations')

    // At least one structured section should be present
    const anyStructured = hasSummary || hasKeyFindings || hasDataHighlights || hasRecommendations
    expect(anyStructured).toBe(true)

    // Verify the "Generate Report" button exists in the DOM
    const generateBtn = page.locator('[data-testid="agent-generate-report-button"]')
    const hasGenerateBtn = await generateBtn.count() > 0
    expect(hasGenerateBtn).toBe(true)

    // Verify the status chip shows completed
    expect(pageContent.includes('completed')).toBe(true)
  })

  test('Report Analyst with insights mode', async ({ page }) => {
    if (!testRunId) {
      test.skip()
      return
    }

    await page.goto(`${BASE_URL}/agents`, { waitUntil: 'networkidle', timeout: 20_000 })

    // Select Report Analyst
    await page.locator('text=Report Analyst').first().click()

    // Fill in the run ID
    const runInput = page.locator('label:has-text("Report Run")').locator('..').locator('input').first()
    await runInput.fill(testRunId)

    // Change to insights mode
    const analysisTypeSelect = page.locator('label:has-text("Analysis Type")').locator('..')
    await analysisTypeSelect.click()
    await page.locator('li[role="option"]:has-text("Insights")').click()

    // Run the analysis
    const runButton = page.locator('button:has-text("Run Report Analyst")')
    await runButton.click()

    // Wait for result to appear and scroll to it
    const resultHeader = page.locator('text=Result').first()
    await expect(resultHeader).toBeVisible({ timeout: 150_000 })
    // Scroll to bottom of the page to reveal all structured result content
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(2000) // Give structured rendering time to render

    // Check the full page content for structured sections (not just what's visible in viewport)
    const pageContent = await page.content()
    const hasSummary = pageContent.includes('Summary')
    const hasKeyFindings = pageContent.includes('Key Findings')
    const hasDataHighlights = pageContent.includes('Data Highlights')
    const hasRecommendations = pageContent.includes('Recommendations')

    // At minimum, some structured content should be present
    expect(hasSummary || hasKeyFindings || hasDataHighlights || hasRecommendations).toBe(true)
  })
})
