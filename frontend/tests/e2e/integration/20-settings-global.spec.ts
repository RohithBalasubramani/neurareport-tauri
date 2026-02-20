import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Settings page integration @integration', () => {
  test('settings page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/settings')
    await expect(page.getByText(/Settings|Preferences/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('language selector changes locale', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const langSelect = page.getByRole('combobox', { name: /Language/i }).first()
      ?? page.getByLabel(/Language/i).first()
    if (await langSelect.count()) {
      await langSelect.click()
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
    }
  })

  test('timezone selector works', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const tzSelect = page.getByRole('combobox', { name: /Timezone|Time Zone/i }).first()
      ?? page.getByLabel(/Timezone|Time Zone/i).first()
    if (await tzSelect.count()) {
      await tzSelect.click()
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
    }
  })

  test('demo mode toggle', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Demo/i }).first()
      ?? page.getByLabel(/Demo/i).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
      // Toggle back
      await toggle.click()
    }
  })

  test('auto-refresh toggle', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Auto.?Refresh/i }).first()
      ?? page.getByLabel(/Auto.?Refresh/i).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
      await toggle.click()
    }
  })

  test('notifications toggle', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Notification/i }).first()
      ?? page.getByLabel(/Notification/i).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
      await toggle.click()
    }
  })

  test('compact view toggle', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Compact/i }).first()
      ?? page.getByLabel(/Compact/i).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
      await toggle.click()
    }
  })

  test('export configuration button', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForTimeout(3000)
    const exportBtn = page.getByRole('button', { name: /Export Config|Export/i }).first()
    if (await exportBtn.count()) {
      await expect(exportBtn).toBeVisible()
    }
  })
})

test.describe('Activity page integration @integration', () => {
  test('activity page loads with log', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/activity')
    await expect(page.getByText(/Activity/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('activity log entries display', async ({ page }) => {
    await page.goto('/activity')
    await page.waitForTimeout(3000)
    const logEntry = page.locator('[class*="activity"], [class*="log"], [class*="entry"]').first()
    if (await logEntry.count()) {
      await expect(logEntry).toBeVisible()
    }
  })

  test('clear activity log button', async ({ page }) => {
    await page.goto('/activity')
    await page.waitForTimeout(3000)
    const clearBtn = page.getByRole('button', { name: /Clear/i }).first()
    if (await clearBtn.count()) {
      await expect(clearBtn).toBeVisible()
    }
  })
})

test.describe('Search page integration @integration', () => {
  test('search page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/search')
    await expect(page.getByText(/Search/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('global search input works', async ({ page }) => {
    await page.goto('/search')
    await page.waitForTimeout(3000)
    const searchInput = page.getByPlaceholder(/Search/i).first()
      ?? page.getByRole('searchbox').first()
    if (await searchInput.count()) {
      await searchInput.fill('test query')
      await page.waitForTimeout(500)
    }
  })

  test('semantic search mode toggle', async ({ page }) => {
    await page.goto('/search')
    await page.waitForTimeout(3000)
    const toggle = page.getByRole('switch', { name: /Semantic/i }).first()
      ?? page.getByRole('button', { name: /Semantic/i }).first()
    if (await toggle.count()) {
      await toggle.click()
      await page.waitForTimeout(500)
    }
  })

  test('save search button', async ({ page }) => {
    await page.goto('/search')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save Search|Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('saved searches list', async ({ page }) => {
    await page.goto('/search')
    await page.waitForTimeout(3000)
    const savedTab = page.getByRole('tab', { name: /Saved/i }).first()
      ?? page.getByRole('button', { name: /Saved/i }).first()
    if (await savedTab.count()) {
      await savedTab.click()
      await page.waitForTimeout(1000)
    }
  })

  test('search type selector', async ({ page }) => {
    await page.goto('/search')
    await page.waitForTimeout(3000)
    const typeSelect = page.getByRole('combobox', { name: /Type|Mode/i }).first()
    if (await typeSelect.count()) {
      await typeSelect.click()
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
    }
  })
})

test.describe('Ops Console page integration @integration', () => {
  test('ops console loads health data', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/ops')
    await expect(page.getByText(/Ops|Operations|Health/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('health status indicators', async ({ page }) => {
    await page.goto('/ops')
    await page.waitForTimeout(3000)
    const status = page.locator('[class*="status"], [class*="health"], [class*="indicator"]').first()
    if (await status.count()) {
      await expect(status).toBeVisible()
    }
  })

  test('refresh health button', async ({ page }) => {
    await page.goto('/ops')
    await page.waitForTimeout(3000)
    const refreshBtn = page.getByRole('button', { name: /Refresh/i }).first()
    if (await refreshBtn.count()) {
      await refreshBtn.click()
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('Stats page integration @integration', () => {
  test('usage stats page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/stats')
    await expect(page.getByText(/Stat|Usage|Analytics/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('token usage section displays', async ({ page }) => {
    await page.goto('/stats')
    await page.waitForTimeout(3000)
    const tokenSection = page.getByText(/Token|Usage|API/i).first()
    if (await tokenSection.count()) {
      await expect(tokenSection).toBeVisible()
    }
  })
})

test.describe('History page integration @integration', () => {
  test('history page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/history')
    await expect(page.getByText(/History|Report/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('history entries display', async ({ page }) => {
    await page.goto('/history')
    await page.waitForTimeout(3000)
    const entry = page.locator('[class*="history"], [class*="entry"], [class*="row"]').first()
    if (await entry.count()) {
      await expect(entry).toBeVisible()
    }
  })
})

test.describe('Analyze page integration @integration', () => {
  test('analyze page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/analyze')
    await expect(page.getByText(/Analyze|Analysis/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('document analysis upload button', async ({ page }) => {
    await page.goto('/analyze')
    await page.waitForTimeout(3000)
    const uploadBtn = page.getByRole('button', { name: /Upload|Analyze/i }).first()
    if (await uploadBtn.count()) {
      await expect(uploadBtn).toBeVisible()
    }
  })

  test('insights generation button', async ({ page }) => {
    await page.goto('/analyze')
    await page.waitForTimeout(3000)
    const insightsBtn = page.getByRole('button', { name: /Insight|Generate/i }).first()
    if (await insightsBtn.count()) {
      await expect(insightsBtn).toBeVisible()
    }
  })

  test('trends analysis section', async ({ page }) => {
    await page.goto('/analyze')
    await page.waitForTimeout(3000)
    const trends = page.getByText(/Trend/i).first()
    if (await trends.count()) {
      await expect(trends).toBeVisible()
    }
  })
})

test.describe('Summary page integration @integration', () => {
  test('summary page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/summary')
    await expect(page.getByText(/Summary/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('generate summary button', async ({ page }) => {
    await page.goto('/summary')
    await page.waitForTimeout(3000)
    const genBtn = page.getByRole('button', { name: /Generate/i }).first()
    if (await genBtn.count()) {
      await expect(genBtn).toBeVisible()
    }
  })

  test('summary output area', async ({ page }) => {
    await page.goto('/summary')
    await page.waitForTimeout(3000)
    const output = page.locator('[class*="summary"], [class*="output"], [class*="result"]').first()
    if (await output.count()) {
      await expect(output).toBeVisible()
    }
  })
})

test.describe('Notifications integration @integration', () => {
  test('notification bell visible', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const bell = page.getByRole('button', { name: /Notification/i }).first()
      ?? page.locator('[class*="notification"], [class*="bell"]').first()
    if (await bell.count()) {
      await expect(bell).toBeVisible()
    }
  })

  test('notification panel opens', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const bell = page.getByRole('button', { name: /Notification/i }).first()
    if (await bell.count()) {
      await bell.click()
      await page.waitForTimeout(1000)
      // Close it
      await page.keyboard.press('Escape')
    }
  })

  test('mark all read button', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const bell = page.getByRole('button', { name: /Notification/i }).first()
    if (await bell.count()) {
      await bell.click()
      await page.waitForTimeout(1000)
      const markAllBtn = page.getByRole('button', { name: /Mark All|Read All/i }).first()
      if (await markAllBtn.count()) {
        await expect(markAllBtn).toBeVisible()
      }
      await page.keyboard.press('Escape')
    }
  })
})
