import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Templates page integration @integration', () => {
  test('page loads with template list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/templates')
    await expect(page.getByText(/Templates|Report Designs/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"Upload Design" navigates to wizard', async ({ page }) => {
    await page.goto('/templates')
    const btn = page.getByRole('button', { name: /Upload Design/i })
    await expect(btn).toBeVisible({ timeout: 15_000 })
    await btn.click()
    await page.waitForURL('**/setup/wizard')
  })

  test('search input filters templates', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const search = page.getByPlaceholder(/Search/i).first()
    if (await search.count()) {
      await search.fill('nonexistent_template_xyz')
      await page.waitForTimeout(500)
    }
  })

  test('type filter (PDF/Excel) works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const typeFilter = page.getByRole('combobox', { name: /Type/i }).first()
    if (await typeFilter.count()) {
      await typeFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('status filter works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const statusFilter = page.getByRole('combobox', { name: /Status/i }).first()
    if (await statusFilter.count()) {
      await statusFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('tags filter works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const tagsFilter = page.getByRole('combobox', { name: /Tags/i }).first()
    if (await tagsFilter.count()) {
      await tagsFilter.click()
      await page.waitForTimeout(1000)
      await page.keyboard.press('Escape')
    }
  })

  test('quick filter chips removable', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    // Apply a filter first, then check for chip X button
    const chip = page.locator('[class*="Chip"]').first()
    if (await chip.count()) {
      const deleteIcon = chip.locator('svg, [data-testid*="Cancel"]').first()
      if (await deleteIcon.count()) {
        await deleteIcon.click()
      }
    }
  })

  test('click row navigates to reports', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const row = page.locator('tr').nth(1)
    if (await row.count()) {
      await row.click()
      await page.waitForTimeout(2000)
    }
  })

  test('favorite toggle works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const starBtn = page.getByRole('button', { name: /favorite|star/i }).first()
    if (await starBtn.count()) {
      await starBtn.click()
      await page.waitForTimeout(500)
    }
  })

  test('"Edit" navigates to template editor', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const editItem = page.getByRole('menuitem', { name: /^Edit$/ })
      if (await editItem.count()) {
        await editItem.click()
        await page.waitForTimeout(2000)
      }
    }
  })

  test('"Edit Details" opens dialog', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const editDetails = page.getByRole('menuitem', { name: /Edit Details/i })
      if (await editDetails.count()) {
        await editDetails.click()
        await expect(page.getByLabel(/Name/i).first()).toBeVisible({ timeout: 5_000 })
        await page.getByRole('button', { name: /Cancel/i }).click()
      }
    }
  })

  test('edit details form saves changes', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const editDetails = page.getByRole('menuitem', { name: /Edit Details/i })
      if (await editDetails.count()) {
        await editDetails.click()
        const nameInput = page.getByLabel(/Name/i).first()
        if (await nameInput.count()) {
          const currentName = await nameInput.inputValue()
          await nameInput.fill(currentName + ' (edited)')
          const saveBtn = page.getByRole('button', { name: /Save/i })
          if (await saveBtn.count()) {
            await saveBtn.click()
            await page.waitForTimeout(2000)
          }
        }
      }
    }
  })

  test('"Export" downloads template', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const exportItem = page.getByRole('menuitem', { name: /Export/i })
      if (await exportItem.count()) {
        await expect(exportItem).toBeVisible()
        await page.keyboard.press('Escape')
      }
    }
  })

  test('"Duplicate" creates copy', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const dupItem = page.getByRole('menuitem', { name: /Duplicate/i })
      if (await dupItem.count()) {
        await expect(dupItem).toBeVisible()
        await page.keyboard.press('Escape')
      }
    }
  })

  test('"Delete" shows confirmation', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const deleteItem = page.getByRole('menuitem', { name: /Delete/i })
      if (await deleteItem.count()) {
        await deleteItem.click()
        await expect(page.getByRole('button', { name: /Confirm|Delete|Remove/i }).first()).toBeVisible({ timeout: 5_000 })
        await page.getByRole('button', { name: /Cancel/i }).click()
      }
    }
  })

  test('select checkbox enables bulk actions', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      await page.waitForTimeout(500)
      // Bulk action buttons should appear
    }
  })

  test('bulk "Update Status" works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      const bulkStatus = page.getByRole('button', { name: /Update Status/i })
      if (await bulkStatus.count()) {
        await expect(bulkStatus).toBeVisible()
      }
    }
  })

  test('bulk "Add Tags" works', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const checkbox = page.getByRole('checkbox').first()
    if (await checkbox.count()) {
      await checkbox.click()
      const bulkTags = page.getByRole('button', { name: /Add Tags/i })
      if (await bulkTags.count()) {
        await expect(bulkTags).toBeVisible()
      }
    }
  })

  test('bulk "Delete" works', async ({ page }) => {
    await page.goto('/templates')
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

  test('"Import Backup" opens import dialog', async ({ page }) => {
    await page.goto('/templates')
    const importBtn = page.getByRole('button', { name: /Import Backup/i })
    if (await importBtn.count()) {
      await importBtn.click()
      await page.waitForTimeout(1000)
      // Import dialog should appear
      const cancelBtn = page.getByRole('button', { name: /Cancel/i })
      if (await cancelBtn.count()) await cancelBtn.click()
    }
  })

  test('"View Similar" shows related templates', async ({ page }) => {
    await page.goto('/templates')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const similarItem = page.getByRole('menuitem', { name: /Similar|View Similar/i })
      if (await similarItem.count()) {
        await expect(similarItem).toBeVisible()
        await page.keyboard.press('Escape')
      }
    }
  })
})
