import { test, expect } from '@playwright/test'
import path from 'node:path'

test.describe('User flows', () => {
  test('connects a SQLite data source and starts a report run @ui', async ({ page }) => {
    test.setTimeout(120_000)

    // 1) Create connection
    await page.goto('/connections')
    await expect(page.getByRole('button', { name: 'Add Data Source' })).toBeVisible()

    await page.getByRole('button', { name: 'Add Data Source' }).click()
    await expect(page.getByText('Add Data Source').first()).toBeVisible()

    const connName = `E2E SQLite ${Date.now()}`
    await page.getByLabel('Connection Name').fill(connName)
    // SQLite uses "Database Path" label but the input is the "database" field.
    const dbPath = path.resolve(process.cwd(), '..', 'backend', 'testdata', 'sample.db')
    const dbPathInput = page.getByLabel('Database Path')
    await dbPathInput.fill(dbPath)

    // Ensure React state has the latest values before testing.
    await expect(page.getByLabel('Connection Name')).toHaveValue(connName)
    await expect(dbPathInput).toHaveValue(dbPath)

    // Cold-start + DataFrame-based verification can be slow on Windows; wait on the network response
    // (and then the success toast) instead of relying on a short fixed timeout.
    const testBtn = page.getByRole('button', { name: 'Test Connection' })
    await expect(testBtn).toBeEnabled()
    const [testResp] = await Promise.all([
      page.waitForResponse((r) => r.url().includes('/connections/test') && r.request().method() === 'POST', { timeout: 60_000 }),
      testBtn.click(),
    ])
    expect(testResp.ok()).toBeTruthy()
    await expect(page.getByText('Connection successful! Database is reachable.')).toBeVisible({ timeout: 60_000 })

    await page.getByRole('button', { name: 'Add Connection' }).click()
    // The connections table is virtualized; use the search box to reliably locate the new record.
    await expect(page.getByRole('heading', { name: 'Add Data Source' })).toHaveCount(0)
    const connSearch = page.getByPlaceholder('Search connections...').first()
    await connSearch.fill(connName)
    await expect(page.getByText(connName).first()).toBeVisible({ timeout: 20_000 })

    // Make it active by clicking the row.
    const activeRow = page.locator('tr[role="button"]').filter({ hasText: connName }).first()
    await activeRow.scrollIntoViewIfNeeded()
    await activeRow.click()
    await expect(activeRow.getByText('Active')).toBeVisible({ timeout: 20_000 })

    // 2) Verify templates list loads
    // Use in-app navigation so the selected connection remains in the SPA store.
    await page.getByRole('button', { name: 'Templates' }).click()
    await page.waitForURL('**/templates')
    await expect(page.getByText('Templates').first()).toBeVisible()
    await expect(page.getByText(/^Orders Template$/).first()).toBeVisible()

    // 3) Start a report run (async)
    await page.getByRole('button', { name: 'My Reports' }).click()
    await page.waitForURL('**/reports')
    await expect(page.getByText(/Run a Report/i).first()).toBeVisible()

    const designLabel = page.getByText('Report Design', { exact: true }).first()
    // MUI Select renders an unnamed combobox; scope selection to the nearest container.
    await designLabel.locator('..').locator('..').getByRole('combobox').click()
    await page.getByRole('option', { name: /Orders Template/i }).first().click()

    // Ensure batches can be discovered (this exercises the backend discover endpoint end-to-end).
    await page.getByRole('button', { name: 'Find Batches' }).click()
    // If discover succeeded, the error alert disappears.
    await expect(page.getByText(/Request failed with status code/i)).toHaveCount(0)

    await page.getByRole('button', { name: 'Generate Report' }).click()
    // Report generation should start and return a run id.
    await expect(page.getByText(/Report started! ID:/)).toBeVisible({ timeout: 20_000 })

    // 4) Clean up the connection (best-effort; do not fail the run if the UI table is virtualized).
    try {
      await page.goto('/connections')
      await expect(page.getByText(connName)).toBeVisible({ timeout: 10_000 })
      const searchBox = page.getByPlaceholder('Search connections...').first()
      await searchBox.fill(connName)
      await page.waitForTimeout(250)

      // Click the first visible row action button after filtering.
      await page.getByRole('button', { name: 'More actions' }).first().click({ timeout: 5_000 })
      await page.getByRole('menuitem', { name: 'Delete' }).click({ timeout: 5_000 })
      await page.getByRole('button', { name: 'Remove' }).click({ timeout: 5_000 })
      await expect(page.getByText(connName)).toHaveCount(0, { timeout: 10_000 })
    } catch {
      // Non-fatal cleanup failure; leaving the record is acceptable for local/dev runs.
    }
  })
})
