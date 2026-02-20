/**
 * Test: verify task history items are clickable and load results with auto-scroll
 */
import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:9071'

test.describe('Task History — Clickable Items', () => {
  test.setTimeout(60_000)

  test('history items are clickable and show result with auto-scroll', async ({ page }) => {
    await page.goto(`${BASE_URL}/agents`, { waitUntil: 'networkidle', timeout: 20_000 })

    // Open history panel
    await page.locator('button:has-text("History")').click()
    await page.waitForTimeout(2000)

    const historyItems = page.locator('li[class*="MuiListItem"]')
    const count = await historyItems.count()
    console.log(`History items found: ${count}`)
    if (count === 0) { test.skip(); return }

    // Click the first history item
    await historyItems.first().click()

    // Wait for scroll animation
    await page.waitForTimeout(1500)

    // Result should be visible after auto-scroll
    const resultHeading = page.locator('text=Result').first()
    await expect(resultHeading).toBeVisible({ timeout: 5_000 })

    // Take screenshot — should show the result prominently
    await page.screenshot({ path: 'playwright-results/history-click-scrolled.png' })

    // Verify the status chip shows
    await expect(page.locator('.MuiChip-root:has-text("completed")').first()).toBeVisible({ timeout: 3_000 })
  })

  test('clicking Report Analyst history shows structured result', async ({ page }) => {
    await page.goto(`${BASE_URL}/agents`, { waitUntil: 'networkidle', timeout: 20_000 })

    await page.locator('button:has-text("History")').click()
    await page.waitForTimeout(2000)

    const reportAnalystItem = page.locator('li:has-text("Report Analyst")').first()
    if (await reportAnalystItem.count() === 0) { test.skip(); return }

    await reportAnalystItem.click()
    await page.waitForTimeout(1500)

    // Structured result should render — check page content
    const content = await page.content()
    const hasSummary = content.includes('Summary')
    const hasFindings = content.includes('Key Findings') || content.includes('finding')
    console.log(`Summary: ${hasSummary}, Findings: ${hasFindings}`)

    await page.screenshot({ path: 'playwright-results/history-report-analyst-scrolled.png' })

    expect(hasSummary).toBe(true)
  })

  test('selected history item has visual highlight', async ({ page }) => {
    await page.goto(`${BASE_URL}/agents`, { waitUntil: 'networkidle', timeout: 20_000 })

    await page.locator('button:has-text("History")').click()
    await page.waitForTimeout(2000)

    const historyItems = page.locator('li[class*="MuiListItem"]')
    if (await historyItems.count() === 0) { test.skip(); return }

    await historyItems.first().click()
    await page.waitForTimeout(500)

    // Check cursor and border
    const cursor = await historyItems.first().evaluate((el) => window.getComputedStyle(el).cursor)
    expect(cursor).toBe('pointer')
    const borderLeft = await historyItems.first().evaluate((el) => window.getComputedStyle(el).borderLeftWidth)
    expect(borderLeft).toBe('3px')
  })

  test('clicking different history items switches results', async ({ page }) => {
    await page.goto(`${BASE_URL}/agents`, { waitUntil: 'networkidle', timeout: 20_000 })

    await page.locator('button:has-text("History")').click()
    await page.waitForTimeout(2000)

    const historyItems = page.locator('li[class*="MuiListItem"]')
    const count = await historyItems.count()
    if (count < 2) { test.skip(); return }

    // Click first item
    await historyItems.nth(0).click()
    await page.waitForTimeout(1000)
    await expect(page.locator('text=Result').first()).toBeVisible({ timeout: 3_000 })

    // Click second item — should also show result
    await historyItems.nth(1).click()
    await page.waitForTimeout(1000)
    await expect(page.locator('text=Result').first()).toBeVisible({ timeout: 3_000 })
  })
})
