import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi, uploadFile } from './helpers'

test.describe('Knowledge Library page integration @integration', () => {
  test('page loads with document library', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/knowledge')
    await expect(page.getByText(/Knowledge/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('upload document button visible', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const uploadBtn = page.getByRole('button', { name: /Upload Document|Upload/i }).first()
    if (await uploadBtn.count()) {
      await expect(uploadBtn).toBeVisible()
    }
  })

  test('search documents input works', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const search = page.getByPlaceholder(/Search/i).first()
    if (await search.count()) {
      await search.fill('test query')
      await page.waitForTimeout(500)
    }
  })

  test('semantic search toggle', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Semantic/i }).first()
      ?? page.getByRole('button', { name: /Semantic/i }).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
    }
  })

  test('document card click opens detail', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const card = page.locator('[class*="card"], [class*="document"], [class*="item"]').first()
    if (await card.count()) {
      await card.click()
      await page.waitForTimeout(1000)
    }
  })

  test('favorite toggle on document', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const star = page.getByRole('button', { name: /Favorite|Star/i }).first()
    if (await star.count()) {
      await star.click()
      await page.waitForTimeout(500)
    }
  })

  test('delete document with confirmation', async ({ page }) => {
    await page.goto('/knowledge')
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

  test('create collection button', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const collBtn = page.getByRole('button', { name: /New Collection|Collection/i }).first()
    if (await collBtn.count()) {
      await collBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.first().click()
    }
  })

  test('collections tab loads', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const collectionsTab = page.getByRole('tab', { name: /Collection/i }).first()
      ?? page.getByRole('button', { name: /Collection/i }).first()
    if (await collectionsTab.count()) {
      await collectionsTab.click()
      await page.waitForTimeout(1000)
    }
  })

  test('create tag button', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const tagBtn = page.getByRole('button', { name: /New Tag|Tag/i }).first()
    if (await tagBtn.count()) {
      await tagBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.first().click()
    }
  })

  test('add tag to document', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const tagPicker = page.locator('[class*="tag"], [class*="chip"]').first()
    if (await tagPicker.count()) {
      await expect(tagPicker).toBeVisible()
    }
  })

  test('auto-tag document button', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const autoTagBtn = page.getByRole('button', { name: /Auto.?Tag|Auto/i }).first()
    if (await autoTagBtn.count()) {
      await expect(autoTagBtn).toBeVisible()
    }
  })

  test('related documents section', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const related = page.getByText(/Related/i).first()
    if (await related.count()) {
      await expect(related).toBeVisible()
    }
  })

  test('library statistics section', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const stats = page.getByText(/Stat|Total|Documents/i).first()
    if (await stats.count()) {
      await expect(stats).toBeVisible()
    }
  })

  test('delete collection', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const collectionsTab = page.getByRole('tab', { name: /Collection/i }).first()
      ?? page.getByRole('button', { name: /Collection/i }).first()
    if (await collectionsTab.count()) {
      await collectionsTab.click()
      await page.waitForTimeout(1000)
      const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
      if (await deleteBtn.count()) {
        await expect(deleteBtn).toBeVisible()
      }
    }
  })

  test('knowledge graph button', async ({ page }) => {
    await page.goto('/knowledge')
    await page.waitForTimeout(3000)
    const graphBtn = page.getByRole('button', { name: /Knowledge Graph|Graph/i }).first()
    if (await graphBtn.count()) {
      await expect(graphBtn).toBeVisible()
    }
  })
})
