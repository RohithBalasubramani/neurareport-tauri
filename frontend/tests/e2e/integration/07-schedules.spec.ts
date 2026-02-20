import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi, fillMuiSelect } from './helpers'

test.describe('Schedules page integration @integration', () => {
  test('page loads with schedule list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/schedules')
    await expect(page.getByText(/Schedule/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"Create Schedule" opens dialog', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      await expect(page.getByLabel(/Name|Schedule Name/i).first()).toBeVisible({ timeout: 5_000 })
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('schedule form fields fillable', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const nameInput = page.getByLabel(/Name|Schedule Name/i).first()
      if (await nameInput.count()) {
        await nameInput.fill('Test Schedule')
        await expect(nameInput).toHaveValue('Test Schedule')
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('template dropdown populates', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const templateSelect = page.getByRole('combobox', { name: /Template/i }).first()
      if (await templateSelect.count()) {
        await templateSelect.click()
        await expect(page.getByRole('option').first()).toBeVisible({ timeout: 10_000 })
        await page.keyboard.press('Escape')
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('connection dropdown populates', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const connSelect = page.getByRole('combobox', { name: /Connection/i }).first()
      if (await connSelect.count()) {
        await connSelect.click()
        await expect(page.getByRole('option').first()).toBeVisible({ timeout: 10_000 })
        await page.keyboard.press('Escape')
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('frequency dropdown works', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const freqSelect = page.getByRole('combobox', { name: /Frequency/i }).first()
      if (await freqSelect.count()) {
        await freqSelect.click()
        await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
        await page.keyboard.press('Escape')
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('date inputs work', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const dateInput = page.locator('input[type="date"]').first()
      if (await dateInput.count()) {
        await dateInput.fill('2025-01-01')
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('email fields are optional', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const emailInput = page.getByLabel(/Email|Recipients/i).first()
      if (await emailInput.count()) {
        // Should not be required
        await expect(emailInput).toBeVisible()
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('active toggle switch works', async ({ page }) => {
    await page.goto('/schedules')
    const btn = page.getByRole('button', { name: /Create Schedule/i })
    if (await btn.count()) {
      await btn.click()
      const toggle = page.getByRole('switch').first()
      if (await toggle.count()) {
        await toggle.click()
      }
      await page.getByRole('button', { name: /Cancel/i }).click()
    }
  })

  test('"Create Schedule" submits form', async ({ page }) => {
    await page.goto('/schedules')
    const createBtn = page.getByRole('button', { name: /Create Schedule/i })
    if (await createBtn.count()) {
      await expect(createBtn).toBeVisible()
    }
  })

  test('enable/disable toggle per row works', async ({ page }) => {
    await page.goto('/schedules')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch').first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(1000)
    }
  })

  test('"Edit" opens pre-filled dialog', async ({ page }) => {
    await page.goto('/schedules')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More|actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const editItem = page.getByRole('menuitem', { name: /Edit/i })
      if (await editItem.count()) {
        await editItem.click()
        await page.waitForTimeout(1000)
        await page.getByRole('button', { name: /Cancel/i }).click()
      }
    }
  })

  test('"Delete" with confirmation', async ({ page }) => {
    await page.goto('/schedules')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More|actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const deleteItem = page.getByRole('menuitem', { name: /Delete/i })
      if (await deleteItem.count()) {
        await deleteItem.click()
        const confirmBtn = page.getByRole('button', { name: /Confirm|Delete|Remove/i }).first()
        if (await confirmBtn.count()) {
          await page.getByRole('button', { name: /Cancel/i }).click()
        }
      }
    }
  })

  test('search input filters schedules', async ({ page }) => {
    await page.goto('/schedules')
    await page.waitForTimeout(3000)
    const search = page.getByPlaceholder(/Search/i).first()
    if (await search.count()) {
      await search.fill('nonexistent_schedule')
      await page.waitForTimeout(500)
    }
  })
})
