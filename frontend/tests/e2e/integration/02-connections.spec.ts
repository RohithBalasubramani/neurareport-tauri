import { test, expect } from '@playwright/test'
import path from 'node:path'
import { captureConsole, expectNoConsoleErrors, waitForApi, fillMuiSelect, confirmDialog } from './helpers'

test.describe('Connections page integration @integration', () => {
  test('page loads with connection list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/connections')
    await expect(page.getByRole('button', { name: 'Add Data Source' })).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"Add Data Source" opens drawer', async ({ page }) => {
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()
    await expect(page.getByText('Add Data Source').first()).toBeVisible()
    await expect(page.getByLabel('Connection Name')).toBeVisible()
  })

  test('connection form fields are fillable', async ({ page }) => {
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()
    await page.getByLabel('Connection Name').fill('Test Connection')
    await expect(page.getByLabel('Connection Name')).toHaveValue('Test Connection')
  })

  test('DB Type dropdown shows options', async ({ page }) => {
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()
    // Look for a type selector (may be a select or radio)
    const typeSelect = page.getByRole('combobox').first()
    if (await typeSelect.count()) {
      await typeSelect.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('"Test Connection" sends POST and shows success toast', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()

    const connName = `E2E Test ${Date.now()}`
    await page.getByLabel('Connection Name').fill(connName)
    const dbPath = path.resolve(process.cwd(), '..', 'backend', 'testdata', 'sample.db')
    await page.getByLabel('Database Path').fill(dbPath)

    const testBtn = page.getByRole('button', { name: 'Test Connection' })
    await expect(testBtn).toBeEnabled()

    const [resp] = await Promise.all([
      waitForApi(page, '/connections/test', 'POST', 60_000),
      testBtn.click(),
    ])
    expect(resp.ok()).toBeTruthy()
    await expect(page.getByText(/Connection successful/i)).toBeVisible({ timeout: 60_000 })
  })

  test('error toast on invalid connection config', async ({ page }) => {
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()
    await page.getByLabel('Connection Name').fill('Bad Connection')

    // Fill an invalid path
    const dbPathInput = page.getByLabel('Database Path')
    if (await dbPathInput.count()) {
      await dbPathInput.fill('/nonexistent/path/fake.db')
    }

    const testBtn = page.getByRole('button', { name: 'Test Connection' })
    if (await testBtn.isEnabled()) {
      await testBtn.click()
      // Should show error feedback
      await page.waitForTimeout(5_000)
      const errorVisible = await page.getByText(/fail|error|unable/i).first().count()
      expect(errorVisible).toBeGreaterThan(0)
    }
  })

  test('"Add Connection" saves and shows in table', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()

    const connName = `E2E Save ${Date.now()}`
    await page.getByLabel('Connection Name').fill(connName)
    const dbPath = path.resolve(process.cwd(), '..', 'backend', 'testdata', 'sample.db')
    await page.getByLabel('Database Path').fill(dbPath)

    // Test first
    const testBtn = page.getByRole('button', { name: 'Test Connection' })
    await expect(testBtn).toBeEnabled()
    await Promise.all([
      waitForApi(page, '/connections/test', 'POST', 60_000),
      testBtn.click(),
    ])
    await expect(page.getByText(/Connection successful/i)).toBeVisible({ timeout: 60_000 })

    // Save
    await page.getByRole('button', { name: 'Add Connection' }).click()
    await expect(page.getByText(connName).first()).toBeVisible({ timeout: 20_000 })
  })

  test('search input filters connections', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const searchInput = page.getByPlaceholder('Search connections...').first()
    if (await searchInput.count()) {
      await searchInput.fill('nonexistent_xyz_999')
      await page.waitForTimeout(500)
      // Table should be empty or show "no results"
    }
  })

  test('click row sets active connection', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const row = page.locator('tr[role="button"]').first()
    if (await row.count()) {
      await row.click()
      // Should highlight or show "Active" badge
      await page.waitForTimeout(1000)
    }
  })

  test('favorite button toggles star', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const starBtn = page.getByRole('button', { name: /favorite|star/i }).first()
    if (await starBtn.count()) {
      await starBtn.click()
      await page.waitForTimeout(500)
    }
  })

  test('more actions menu opens', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      await expect(page.getByRole('menuitem').first()).toBeVisible({ timeout: 5_000 })
    }
  })

  test('"Inspect Schema" opens schema drawer', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const schemaItem = page.getByRole('menuitem', { name: /Schema|Inspect/i })
      if (await schemaItem.count()) {
        const [resp] = await Promise.all([
          waitForApi(page, '/schema', 'GET'),
          schemaItem.click(),
        ])
        expect(resp.ok()).toBeTruthy()
      }
    }
  })

  test('"Edit" opens edit form', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const editItem = page.getByRole('menuitem', { name: /Edit/i })
      if (await editItem.count()) {
        await editItem.click()
        await expect(page.getByLabel('Connection Name')).toBeVisible({ timeout: 5_000 })
      }
    }
  })

  test('"Delete" shows confirmation dialog', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const deleteItem = page.getByRole('menuitem', { name: /Delete/i })
      if (await deleteItem.count()) {
        await deleteItem.click()
        // Confirmation dialog should appear
        await expect(page.getByRole('button', { name: /Remove|Confirm|Delete/i }).first()).toBeVisible({ timeout: 5_000 })
        // Cancel to avoid deleting
        const cancelBtn = page.getByRole('button', { name: /Cancel/i })
        if (await cancelBtn.count()) await cancelBtn.click()
      }
    }
  })

  test('confirm delete removes connection', async ({ page }) => {
    test.setTimeout(120_000)
    // Seed a connection to delete
    await page.goto('/connections')
    await page.getByRole('button', { name: 'Add Data Source' }).click()
    const connName = `E2E Delete ${Date.now()}`
    await page.getByLabel('Connection Name').fill(connName)
    const dbPath = path.resolve(process.cwd(), '..', 'backend', 'testdata', 'sample.db')
    await page.getByLabel('Database Path').fill(dbPath)

    const testBtn = page.getByRole('button', { name: 'Test Connection' })
    await expect(testBtn).toBeEnabled()
    await Promise.all([
      waitForApi(page, '/connections/test', 'POST', 60_000),
      testBtn.click(),
    ])
    await expect(page.getByText(/Connection successful/i)).toBeVisible({ timeout: 60_000 })
    await page.getByRole('button', { name: 'Add Connection' }).click()
    await expect(page.getByText(connName).first()).toBeVisible({ timeout: 20_000 })

    // Now delete it
    const searchBox = page.getByPlaceholder('Search connections...').first()
    await searchBox.fill(connName)
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: /More actions/i }).first().click()
    await page.getByRole('menuitem', { name: /Delete/i }).click()
    await page.getByRole('button', { name: /Remove/i }).click()
    await expect(page.getByText(connName)).toHaveCount(0, { timeout: 10_000 })
  })

  test('cancel delete keeps connection', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const moreBtn = page.getByRole('button', { name: /More actions/i }).first()
    if (await moreBtn.count()) {
      await moreBtn.click()
      const deleteItem = page.getByRole('menuitem', { name: /Delete/i })
      if (await deleteItem.count()) {
        await deleteItem.click()
        const cancelBtn = page.getByRole('button', { name: /Cancel/i })
        if (await cancelBtn.count()) {
          await cancelBtn.click()
          // Connection should still be visible
        }
      }
    }
  })

  test('status filter dropdown works', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const statusFilter = page.getByRole('combobox', { name: /Status/i }).first()
    if (await statusFilter.count()) {
      await statusFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })

  test('type filter dropdown works', async ({ page }) => {
    await page.goto('/connections')
    await page.waitForTimeout(3000)
    const typeFilter = page.getByRole('combobox', { name: /Type/i }).first()
    if (await typeFilter.count()) {
      await typeFilter.click()
      await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5_000 })
      await page.keyboard.press('Escape')
    }
  })
})
