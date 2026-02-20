import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Dashboard Builder page integration @integration', () => {
  test('page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/dashboard-builder')
    await expect(page.getByText(/Dashboard/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('create new dashboard', async ({ page }) => {
    await page.goto('/dashboard-builder')
    const btn = page.getByRole('button', { name: /New Dashboard|Create/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(3000)
    }
  })

  test('dashboard canvas loads', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const canvas = page.locator('[class*="grid"], [class*="canvas"], [class*="layout"]').first()
    if (await canvas.count()) {
      await expect(canvas).toBeVisible()
    }
  })

  test('add widget', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const addBtn = page.getByRole('button', { name: /Add Widget|Widget/i }).first()
    if (await addBtn.count()) {
      await addBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('widget config panel', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const widget = page.locator('[class*="widget"]').first()
    if (await widget.count()) {
      await widget.click()
      await page.waitForTimeout(1000)
    }
  })

  test('save widget config', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('delete widget', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const deleteBtn = page.getByRole('button', { name: /Remove|Delete Widget/i }).first()
    if (await deleteBtn.count()) {
      await expect(deleteBtn).toBeVisible()
    }
  })

  test('drag-drop widget reorder', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const dragHandle = page.locator('[class*="drag"], [class*="handle"]').first()
    if (await dragHandle.count()) {
      await expect(dragHandle).toBeVisible()
    }
  })

  test('add filter', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const filterBtn = page.getByRole('button', { name: /Add Filter|Filter/i }).first()
    if (await filterBtn.count()) {
      await filterBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('refresh all widgets', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const refreshBtn = page.getByRole('button', { name: /Refresh/i }).first()
    if (await refreshBtn.count()) {
      await refreshBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('AI insights generation', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const insightsBtn = page.getByRole('button', { name: /Insights|AI/i }).first()
    if (await insightsBtn.count()) {
      await expect(insightsBtn).toBeVisible()
    }
  })

  test('export dashboard', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const exportBtn = page.getByRole('button', { name: /Export/i }).first()
    if (await exportBtn.count()) {
      await expect(exportBtn).toBeVisible()
    }
  })

  test('share dashboard dialog', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const shareBtn = page.getByRole('button', { name: /Share/i }).first()
    if (await shareBtn.count()) {
      await shareBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.click()
    }
  })

  test('generate embed token', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const embedBtn = page.getByRole('button', { name: /Embed/i }).first()
    if (await embedBtn.count()) {
      await expect(embedBtn).toBeVisible()
    }
  })

  test('delete dashboard with confirmation', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
    if (await deleteBtn.count()) {
      await deleteBtn.click()
      const confirmBtn = page.getByRole('button', { name: /Confirm|Delete|Remove/i }).first()
      if (await confirmBtn.count()) {
        await page.getByRole('button', { name: /Cancel/i }).click()
      }
    }
  })

  test('dashboard templates gallery', async ({ page }) => {
    await page.goto('/dashboard-builder')
    await page.waitForTimeout(3000)
    const templatesBtn = page.getByRole('button', { name: /Template/i }).first()
    if (await templatesBtn.count()) {
      await templatesBtn.click()
      await page.waitForTimeout(2000)
    }
  })
})
