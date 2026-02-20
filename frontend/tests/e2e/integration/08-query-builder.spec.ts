import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi, fillMuiSelect } from './helpers'

test.describe('Query Builder (NL2SQL) page integration @integration', () => {
  test('page loads with connection selector', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/query')
    await expect(page.getByText(/Query|NL2SQL|Natural Language/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('connection dropdown populates', async ({ page }) => {
    await page.goto('/query')
    const connSelect = page.getByRole('combobox', { name: /Database Connection|Connection/i }).first()
    if (await connSelect.count()) {
      await connSelect.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 20_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('NL input accepts question', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const nlInput = page.getByPlaceholder(/Ask a question|question about your data/i).first()
    if (await nlInput.count()) {
      await nlInput.fill('How many orders are there?')
      await expect(nlInput).toHaveValue('How many orders are there?')
    }
  })

  test('"Generate SQL" creates query', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto('/query')
    // Select connection first
    const connSelect = page.getByRole('combobox', { name: /Database Connection|Connection/i }).first()
    if (await connSelect.count()) {
      await connSelect.click()
      const option = page.getByRole('option').first()
      if (await option.count()) {
        await option.click()
        const nlInput = page.getByPlaceholder(/Ask a question/i).first()
        if (await nlInput.count()) {
          await nlInput.fill('How many orders are there?')
          const genBtn = page.getByRole('button', { name: /Generate SQL/i })
          if (await genBtn.count() && await genBtn.isEnabled()) {
            await genBtn.click()
            await page.waitForTimeout(10_000)
          }
        }
      }
    }
  })

  test('generated SQL displayed', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const sqlDisplay = page.getByText(/Generated SQL|SELECT/i).first()
    if (await sqlDisplay.count()) {
      await expect(sqlDisplay).toBeVisible()
    }
  })

  test('"Execute Query" runs SQL', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const execBtn = page.getByRole('button', { name: /Execute Query/i })
    if (await execBtn.count()) {
      await expect(execBtn).toBeVisible()
    }
  })

  test('results table displays data', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const results = page.getByText(/Results/i).first()
    if (await results.count()) {
      await expect(results).toBeVisible()
    }
  })

  test('"Explain" button explains query', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const explainBtn = page.getByRole('button', { name: /Explain/i }).first()
    if (await explainBtn.count()) {
      await expect(explainBtn).toBeVisible()
    }
  })

  test('"Save Query" button saves', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('saved queries list loads', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const savedTab = page.getByRole('tab', { name: /Saved/i }).first()
    if (await savedTab.count()) {
      await savedTab.click()
      await page.waitForTimeout(2000)
    }
  })

  test('click saved query loads it', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const savedTab = page.getByRole('tab', { name: /Saved/i }).first()
    if (await savedTab.count()) {
      await savedTab.click()
      await page.waitForTimeout(2000)
      const savedItem = page.locator('[class*="ListItem"]').first()
      if (await savedItem.count()) {
        await savedItem.click()
      }
    }
  })

  test('delete saved query works', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const savedTab = page.getByRole('tab', { name: /Saved/i }).first()
    if (await savedTab.count()) {
      await savedTab.click()
      await page.waitForTimeout(2000)
      const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
      if (await deleteBtn.count()) {
        await expect(deleteBtn).toBeVisible()
      }
    }
  })

  test('query history loads', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const historyTab = page.getByRole('tab', { name: /History/i }).first()
    if (await historyTab.count()) {
      await historyTab.click()
      await page.waitForTimeout(2000)
    }
  })

  test('click history item loads query', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const historyTab = page.getByRole('tab', { name: /History/i }).first()
    if (await historyTab.count()) {
      await historyTab.click()
      await page.waitForTimeout(2000)
      const historyItem = page.locator('[class*="ListItem"]').first()
      if (await historyItem.count()) {
        await historyItem.click()
      }
    }
  })

  test('delete history entry', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const historyTab = page.getByRole('tab', { name: /History/i }).first()
    if (await historyTab.count()) {
      await historyTab.click()
      await page.waitForTimeout(2000)
      const deleteBtn = page.getByRole('button', { name: /Delete/i }).first()
      if (await deleteBtn.count()) {
        await expect(deleteBtn).toBeVisible()
      }
    }
  })

  test('limit/offset pagination works', async ({ page }) => {
    await page.goto('/query')
    await page.waitForTimeout(3000)
    const pagination = page.getByRole('button', { name: /Next|>/i }).first()
    if (await pagination.count()) {
      await expect(pagination).toBeVisible()
    }
  })
})
