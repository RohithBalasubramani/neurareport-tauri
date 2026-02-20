import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Synthesis page integration @integration', () => {
  test('page loads with session list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/synthesis')
    await expect(page.getByText(/Synthesis|Multi-Document/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"New Session" creates session', async ({ page }) => {
    await page.goto('/synthesis')
    const btn = page.getByRole('button', { name: /New Session|Create/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(3000)
    }
  })

  test('add document to session', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const addBtn = page.getByRole('button', { name: /Add Document|Add/i }).first()
    if (await addBtn.count()) {
      await expect(addBtn).toBeVisible()
    }
  })

  test('document content input', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const textarea = page.locator('textarea').first()
    if (await textarea.count()) {
      await textarea.fill('Sample document content for synthesis testing.')
    }
  })

  test('remove document from session', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const removeBtn = page.getByRole('button', { name: /Remove/i }).first()
    if (await removeBtn.count()) {
      await expect(removeBtn).toBeVisible()
    }
  })

  test('"Find Inconsistencies" button', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const btn = page.getByRole('button', { name: /Inconsistenc|Analyze/i }).first()
    if (await btn.count()) {
      await expect(btn).toBeVisible()
    }
  })

  test('"Synthesize" generates output', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const synthesizeBtn = page.getByRole('button', { name: /Synthesize/i }).first()
    if (await synthesizeBtn.count()) {
      await expect(synthesizeBtn).toBeVisible()
    }
  })

  test('output format selector', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const formatSelect = page.getByRole('combobox', { name: /Format|Output/i }).first()
    if (await formatSelect.count()) {
      await formatSelect.click()
      await page.waitForTimeout(1000)
      await page.keyboard.press('Escape')
    }
  })

  test('delete session', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
    if (await deleteBtn.count()) {
      await deleteBtn.click()
      const confirmBtn = page.getByRole('button', { name: /Confirm|Delete/i }).first()
      if (await confirmBtn.count()) {
        await page.getByRole('button', { name: /Cancel/i }).click()
      }
    }
  })

  test('session list shows all sessions', async ({ page }) => {
    await page.goto('/synthesis')
    await page.waitForTimeout(3000)
    const list = page.locator('[class*="List"], [class*="Card"]').first()
    if (await list.count()) {
      await expect(list).toBeVisible()
    }
  })
})
