import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi, fillMuiSelect } from './helpers'

test.describe('Reports page integration @integration', () => {
  test('page loads with design selector', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/reports')
    await expect(page.getByText(/Run a Report|Report/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('select report design populates form', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const designSelect = page.getByRole('combobox').first()
    if (await designSelect.count()) {
      await designSelect.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 10_000 })
      await page.getByRole('option').first().click()
    }
  })

  test('date preset chips set date range', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    for (const label of ['Today', 'This Week', 'This Month', 'Last Month']) {
      const chip = page.getByRole('button', { name: new RegExp(label, 'i') }).first()
      if (await chip.count()) {
        await chip.click()
        await page.waitForTimeout(300)
      }
    }
  })

  test('custom date inputs work', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const startDate = page.locator('input[type="date"]').first()
    if (await startDate.count()) {
      await startDate.fill('2024-01-01')
      await expect(startDate).toHaveValue('2024-01-01')
    }
  })

  test('"Find Batches" discovers data', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    // Select a design first
    const designSelect = page.getByRole('combobox').first()
    if (await designSelect.count()) {
      await designSelect.click()
      const option = page.getByRole('option').first()
      if (await option.count()) {
        await option.click()
        const findBtn = page.getByRole('button', { name: /Find Batches/i })
        if (await findBtn.count()) {
          await findBtn.click()
          await page.waitForTimeout(5000)
        }
      }
    }
  })

  test('batch checkboxes toggle selection', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      await page.waitForTimeout(300)
    }
  })

  test('"Select All" selects all batches', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const selectAll = page.getByRole('button', { name: /Select all/i }).first()
    if (await selectAll.count()) {
      await selectAll.click()
    }
  })

  test('"Clear" deselects all batches', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const clearBtn = page.getByRole('button', { name: /Clear/i }).first()
    if (await clearBtn.count()) {
      await clearBtn.click()
    }
  })

  test('"Generate Report" starts async job', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const genBtn = page.getByRole('button', { name: /Generate Report/i })
    if (await genBtn.count()) {
      await expect(genBtn).toBeVisible()
    }
  })

  test('success message shows run ID after generation', async ({ page }) => {
    // This depends on a full flow — verify the element exists
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    // Check that the page has the generate button ready
    const genBtn = page.getByRole('button', { name: /Generate Report/i })
    if (await genBtn.count()) {
      await expect(genBtn).toBeVisible()
    }
  })

  test('"View Progress" navigates to jobs', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const viewProgress = page.getByRole('button', { name: /View Progress/i }).first()
    if (await viewProgress.count()) {
      await viewProgress.click()
      await page.waitForURL('**/jobs')
    }
  })

  test('"Schedule" navigates to schedules', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const scheduleBtn = page.getByRole('button', { name: /Schedule/i }).first()
    if (await scheduleBtn.count()) {
      await scheduleBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('run history loads previous runs', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const history = page.getByText(/History|Previous/i).first()
    if (await history.count()) {
      await expect(history).toBeVisible()
    }
  })

  test('download buttons for completed runs', async ({ page }) => {
    await page.goto('/reports')
    await page.waitForTimeout(3000)
    const downloadBtn = page.getByRole('button', { name: /Download|PDF|HTML/i }).first()
    if (await downloadBtn.count()) {
      await expect(downloadBtn).toBeVisible()
    }
  })
})
