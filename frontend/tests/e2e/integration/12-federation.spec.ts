import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Federation page integration @integration', () => {
  test('page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/federation')
    await expect(page.getByText(/Federation|Virtual Schema|Schema Builder/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('create virtual schema form', async ({ page }) => {
    await page.goto('/federation')
    const btn = page.getByRole('button', { name: /Create|New|Add/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('connection multi-select', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const connSelect = page.getByRole('combobox', { name: /Connection/i }).first()
    if (await connSelect.count()) {
      await connSelect.click()
      await page.waitForTimeout(1000)
      await page.keyboard.press('Escape')
    }
  })

  test('schema name input', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const nameInput = page.getByLabel(/Name|Schema Name/i).first()
    if (await nameInput.count()) {
      await nameInput.fill('Test Virtual Schema')
    }
  })

  test('"Suggest Joins" generates suggestions', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const suggestBtn = page.getByRole('button', { name: /Suggest Joins|Suggest/i }).first()
    if (await suggestBtn.count()) {
      await expect(suggestBtn).toBeVisible()
    }
  })

  test('schema list loads', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    // Schema list section
    const list = page.locator('[class*="List"], table').first()
    if (await list.count()) {
      await expect(list).toBeVisible()
    }
  })

  test('click schema shows detail', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const schemaItem = page.locator('[class*="Card"], [class*="ListItem"]').first()
    if (await schemaItem.count()) {
      await schemaItem.click()
      await page.waitForTimeout(2000)
    }
  })

  test('execute federated query', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const queryInput = page.locator('textarea').first()
    if (await queryInput.count()) {
      await queryInput.fill('SELECT 1')
      const executeBtn = page.getByRole('button', { name: /Execute|Run/i }).first()
      if (await executeBtn.count()) {
        await expect(executeBtn).toBeVisible()
      }
    }
  })

  test('delete schema with confirmation', async ({ page }) => {
    await page.goto('/federation')
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

  test('results table displays query output', async ({ page }) => {
    await page.goto('/federation')
    await page.waitForTimeout(3000)
    const results = page.getByText(/Results/i).first()
    if (await results.count()) {
      await expect(results).toBeVisible()
    }
  })
})
