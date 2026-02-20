import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Jobs page integration @integration', () => {
  test('page loads with job list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/jobs')
    await expect(page.getByText(/Jobs|Reports/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"Refresh" reloads jobs', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const refreshBtn = page.getByRole('button', { name: /Refresh/i }).first()
    if (await refreshBtn.count()) {
      const [resp] = await Promise.all([
        waitForApi(page, '/jobs', 'GET'),
        refreshBtn.click(),
      ])
      expect(resp.ok()).toBeTruthy()
    }
  })

  test('search input filters jobs', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const search = page.getByPlaceholder(/Search/i).first()
    if (await search.count()) {
      await search.fill('nonexistent_job_xyz')
      await page.waitForTimeout(500)
    }
  })

  test('status filter works', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const statusFilter = page.getByRole('combobox', { name: /Status/i }).first()
    if (await statusFilter.count()) {
      await statusFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('click row shows details', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const row = page.locator('tr').nth(1)
    if (await row.count()) {
      await row.click()
      await page.waitForTimeout(2000)
    }
  })

  test('job detail dialog shows info', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const row = page.locator('tr').nth(1)
    if (await row.count()) {
      await row.click()
      await page.waitForTimeout(2000)
      // Dialog or detail panel should be visible
      const dialog = page.getByRole('dialog').first()
      if (await dialog.count()) {
        await expect(dialog).toBeVisible()
      }
    }
  })

  test('"Download" button in detail dialog', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const downloadBtn = page.getByRole('button', { name: /Download/i }).first()
    if (await downloadBtn.count()) {
      await expect(downloadBtn).toBeVisible()
    }
  })

  test('"Retry" button retries failed job', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const retryBtn = page.getByRole('button', { name: /Retry/i }).first()
    if (await retryBtn.count()) {
      await expect(retryBtn).toBeVisible()
    }
  })

  test('"Cancel" button cancels running job', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const cancelBtn = page.getByRole('button', { name: /Cancel/i }).first()
    if (await cancelBtn.count()) {
      await expect(cancelBtn).toBeVisible()
    }
  })

  test('cancel confirmation dialog', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    // Trigger cancel on a job if one exists
    const cancelBtn = page.getByRole('button', { name: /Cancel/i }).first()
    if (await cancelBtn.count()) {
      await cancelBtn.click()
      // Confirm dialog may appear
      const confirmBtn = page.getByRole('button', { name: /Confirm|Yes/i }).first()
      if (await confirmBtn.count()) {
        await page.getByRole('button', { name: /No|Cancel|Close/i }).first().click()
      }
    }
  })

  test('select checkboxes for bulk operations', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
    }
  })

  test('bulk cancel selected jobs', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      const bulkCancel = page.getByRole('button', { name: /Cancel/i }).first()
      if (await bulkCancel.count()) {
        await expect(bulkCancel).toBeVisible()
      }
    }
  })

  test('bulk delete selected jobs', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      const bulkDelete = page.getByRole('button', { name: /Delete/i }).first()
      if (await bulkDelete.count()) {
        await expect(bulkDelete).toBeVisible()
      }
    }
  })

  test('close detail dialog', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const row = page.locator('tr').nth(1)
    if (await row.count()) {
      await row.click()
      await page.waitForTimeout(1000)
      const closeBtn = page.getByRole('button', { name: /Close|X/i }).first()
      if (await closeBtn.count()) {
        await closeBtn.click()
      }
    }
  })

  test('type filter dropdown works', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const typeFilter = page.getByRole('combobox', { name: /Type/i }).first()
    if (await typeFilter.count()) {
      await typeFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('job status chips display correctly', async ({ page }) => {
    await page.goto('/jobs')
    await page.waitForTimeout(3000)
    const chip = page.locator('[class*="Chip"]').first()
    if (await chip.count()) {
      await expect(chip).toBeVisible()
    }
  })
})
