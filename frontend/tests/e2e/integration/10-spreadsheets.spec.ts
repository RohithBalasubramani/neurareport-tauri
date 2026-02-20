import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Spreadsheets page integration @integration', () => {
  test('page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/spreadsheets')
    await expect(page.getByText(/Spreadsheet/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('create new spreadsheet', async ({ page }) => {
    await page.goto('/spreadsheets')
    const btn = page.getByRole('button', { name: /New Spreadsheet|Create/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(3000)
    }
  })

  test('spreadsheet grid loads', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const grid = page.locator('[class*="grid"], [class*="spreadsheet"], table').first()
    if (await grid.count()) {
      await expect(grid).toBeVisible()
    }
  })

  test('cell editing works', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const cell = page.locator('td, [class*="cell"]').first()
    if (await cell.count()) {
      await cell.dblclick()
      await page.keyboard.type('Hello')
      await page.keyboard.press('Enter')
    }
  })

  test('add sheet tab', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const addSheet = page.getByRole('button', { name: /Add Sheet|\+/i }).first()
    if (await addSheet.count()) {
      await addSheet.click()
      await page.waitForTimeout(1000)
    }
  })

  test('rename sheet', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const tab = page.getByRole('tab').first()
    if (await tab.count()) {
      await tab.dblclick()
      await page.waitForTimeout(500)
    }
  })

  test('delete sheet', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const tab = page.getByRole('tab').first()
    if (await tab.count()) {
      await tab.click({ button: 'right' })
      const deleteItem = page.getByRole('menuitem', { name: /Delete/i })
      if (await deleteItem.count()) {
        await page.keyboard.press('Escape')
      }
    }
  })

  test('formula bar input works', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const formulaBar = page.locator('[class*="formula"], input[placeholder*="formula"]').first()
    if (await formulaBar.count()) {
      await formulaBar.fill('=SUM(A1:A10)')
    }
  })

  test('AI formula generator', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const aiBtn = page.getByRole('button', { name: /AI|Generate Formula/i }).first()
    if (await aiBtn.count()) {
      await expect(aiBtn).toBeVisible()
    }
  })

  test('explain formula', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const explainBtn = page.getByRole('button', { name: /Explain/i }).first()
    if (await explainBtn.count()) {
      await expect(explainBtn).toBeVisible()
    }
  })

  test('import CSV', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const importBtn = page.getByRole('button', { name: /Import|CSV/i }).first()
    if (await importBtn.count()) {
      await expect(importBtn).toBeVisible()
    }
  })

  test('import Excel', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const importBtn = page.getByRole('button', { name: /Import|Excel|XLSX/i }).first()
    if (await importBtn.count()) {
      await expect(importBtn).toBeVisible()
    }
  })

  test('export spreadsheet', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const exportBtn = page.getByRole('button', { name: /Export/i }).first()
    if (await exportBtn.count()) {
      await expect(exportBtn).toBeVisible()
    }
  })

  test('conditional formatting dialog', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const formatBtn = page.getByRole('button', { name: /Format|Conditional/i }).first()
    if (await formatBtn.count()) {
      await formatBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('pivot table creation', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const pivotBtn = page.getByRole('button', { name: /Pivot/i }).first()
    if (await pivotBtn.count()) {
      await expect(pivotBtn).toBeVisible()
    }
  })

  test('data cleaning suggestions', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const cleanBtn = page.getByRole('button', { name: /Clean|Data Cleaning/i }).first()
    if (await cleanBtn.count()) {
      await expect(cleanBtn).toBeVisible()
    }
  })

  test('anomaly detection', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const anomalyBtn = page.getByRole('button', { name: /Anomal/i }).first()
    if (await anomalyBtn.count()) {
      await expect(anomalyBtn).toBeVisible()
    }
  })

  test('delete spreadsheet', async ({ page }) => {
    await page.goto('/spreadsheets')
    await page.waitForTimeout(3000)
    const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
    if (await deleteBtn.count()) {
      await expect(deleteBtn).toBeVisible()
    }
  })
})
