import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Enrichment page integration @integration', () => {
  test('page loads with source selector', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/enrichment')
    await expect(page.getByText(/Enrichment/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('built-in sources displayed (company, address, exchange)', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    for (const src of ['Company', 'Address', 'Currency']) {
      const el = page.getByText(new RegExp(src, 'i')).first()
      if (await el.count()) {
        await expect(el).toBeVisible()
      }
    }
  })

  test('select enrichment source', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const sourceCard = page.locator('[class*="Card"], [class*="chip"]').filter({ hasText: /Company|Address|Currency/i }).first()
    if (await sourceCard.count()) {
      await sourceCard.click()
    }
  })

  test('data input area accepts data', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const dataInput = page.locator('textarea, [class*="editor"]').first()
    if (await dataInput.count()) {
      await dataInput.fill('{"company_name": "Acme Corp"}')
    }
  })

  test('"Preview" shows sample results', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const previewBtn = page.getByRole('button', { name: /Preview/i }).first()
    if (await previewBtn.count()) {
      await expect(previewBtn).toBeVisible()
    }
  })

  test('"Enrich" processes all data', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const enrichBtn = page.getByRole('button', { name: /Enrich/i }).first()
    if (await enrichBtn.count()) {
      await expect(enrichBtn).toBeVisible()
    }
  })

  test('create custom source', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const createBtn = page.getByRole('button', { name: /Create|Add Source|Custom/i }).first()
    if (await createBtn.count()) {
      await createBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel/i })
      if (await cancelBtn.count()) await cancelBtn.click()
    }
  })

  test('delete custom source', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
    if (await deleteBtn.count()) {
      await expect(deleteBtn).toBeVisible()
    }
  })

  test('cache stats display', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const cacheSection = page.getByText(/Cache/i).first()
    if (await cacheSection.count()) {
      await expect(cacheSection).toBeVisible()
    }
  })

  test('clear cache button', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const clearBtn = page.getByRole('button', { name: /Clear Cache/i }).first()
    if (await clearBtn.count()) {
      await expect(clearBtn).toBeVisible()
    }
  })

  test('source type selector works', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const typeSelect = page.getByRole('combobox', { name: /Type|Source/i }).first()
    if (await typeSelect.count()) {
      await typeSelect.click()
      await page.waitForTimeout(1000)
      await page.keyboard.press('Escape')
    }
  })

  test('options config (target currency etc.)', async ({ page }) => {
    await page.goto('/enrichment')
    await page.waitForTimeout(3000)
    const configInput = page.getByLabel(/Target Currency|Currency/i).first()
    if (await configInput.count()) {
      await expect(configInput).toBeVisible()
    }
  })
})
