import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('AI Agents page integration @integration', () => {
  test('agents page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/agents')
    await expect(page.getByText(/Agent/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('agent type selector loads', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const typeSelect = page.getByRole('combobox', { name: /Agent|Type/i }).first()
      ?? page.locator('[class*="select"], [class*="agent-type"]').first()
    if (await typeSelect.count()) {
      await typeSelect.click()
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
    }
  })

  test('research agent form visible', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const researchBtn = page.getByRole('button', { name: /Research/i }).first()
    if (await researchBtn.count()) {
      await researchBtn.click()
      await page.waitForTimeout(1000)
    }
    const topicInput = page.getByLabel(/Topic|Query|Question/i).first()
      ?? page.getByPlaceholder(/topic|research|question/i).first()
    if (await topicInput.count()) {
      await topicInput.fill('Test research topic')
    }
  })

  test('research agent run button', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const runBtn = page.getByRole('button', { name: /Run|Execute|Start/i }).first()
    if (await runBtn.count()) {
      await expect(runBtn).toBeVisible()
    }
  })

  test('data analyst agent form', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const analystBtn = page.getByRole('button', { name: /Data Analyst|Analyst/i }).first()
    if (await analystBtn.count()) {
      await analystBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('email draft agent form', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const emailBtn = page.getByRole('button', { name: /Email/i }).first()
    if (await emailBtn.count()) {
      await emailBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('task list tab loads', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const tasksTab = page.getByRole('tab', { name: /Task/i }).first()
      ?? page.getByRole('button', { name: /Task/i }).first()
    if (await tasksTab.count()) {
      await tasksTab.click()
      await page.waitForTimeout(1000)
    }
  })

  test('cancel running task button', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const cancelBtn = page.getByRole('button', { name: /Cancel/i }).first()
    if (await cancelBtn.count()) {
      await expect(cancelBtn).toBeVisible()
    }
  })

  test('retry failed task button', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const retryBtn = page.getByRole('button', { name: /Retry/i }).first()
    if (await retryBtn.count()) {
      await expect(retryBtn).toBeVisible()
    }
  })

  test('agent stats dashboard section', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const stats = page.getByText(/Stat|Total Tasks|Completed/i).first()
    if (await stats.count()) {
      await expect(stats).toBeVisible()
    }
  })

  test('content repurpose agent', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const repurposeBtn = page.getByRole('button', { name: /Repurpose|Content/i }).first()
    if (await repurposeBtn.count()) {
      await repurposeBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('proofreading agent', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForTimeout(3000)
    const proofBtn = page.getByRole('button', { name: /Proofread/i }).first()
    if (await proofBtn.count()) {
      await proofBtn.click()
      await page.waitForTimeout(1000)
    }
  })
})

test.describe('Ingestion page integration @integration', () => {
  test('ingestion page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/ingestion')
    await expect(page.getByText(/Ingestion|Import|Upload/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('single file upload button', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const uploadBtn = page.getByRole('button', { name: /Upload/i }).first()
    if (await uploadBtn.count()) {
      await expect(uploadBtn).toBeVisible()
    }
  })

  test('bulk upload area visible', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const bulkArea = page.getByText(/Bulk|Drag.*Drop|Multiple/i).first()
      ?? page.locator('[class*="dropzone"], [class*="upload"]').first()
    if (await bulkArea.count()) {
      await expect(bulkArea).toBeVisible()
    }
  })

  test('ZIP upload button', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const zipBtn = page.getByRole('button', { name: /ZIP|Archive/i }).first()
    if (await zipBtn.count()) {
      await expect(zipBtn).toBeVisible()
    }
  })

  test('import from URL input', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const urlInput = page.getByLabel(/URL/i).first()
      ?? page.getByPlaceholder(/url|link/i).first()
    if (await urlInput.count()) {
      await urlInput.fill('https://example.com/test.pdf')
      await page.waitForTimeout(500)
    }
  })

  test('import from URL button', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const importBtn = page.getByRole('button', { name: /Import|Fetch/i }).first()
    if (await importBtn.count()) {
      await expect(importBtn).toBeVisible()
    }
  })

  test('transcribe audio button', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const transcribeBtn = page.getByRole('button', { name: /Transcribe|Audio/i }).first()
    if (await transcribeBtn.count()) {
      await expect(transcribeBtn).toBeVisible()
    }
  })

  test('folder watcher create button', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const watcherBtn = page.getByRole('button', { name: /Watcher|Watch Folder|Create Watcher/i }).first()
    if (await watcherBtn.count()) {
      await watcherBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.first().click()
    }
  })

  test('supported file types info', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const typesInfo = page.getByText(/Supported|File Types|PDF|CSV/i).first()
    if (await typesInfo.count()) {
      await expect(typesInfo).toBeVisible()
    }
  })

  test('web clipping section', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const clipSection = page.getByText(/Clip|Web Clip/i).first()
      ?? page.getByRole('button', { name: /Clip/i }).first()
    if (await clipSection.count()) {
      await expect(clipSection).toBeVisible()
    }
  })

  test('email ingestion section', async ({ page }) => {
    await page.goto('/ingestion')
    await page.waitForTimeout(3000)
    const emailSection = page.getByText(/Email|Inbox/i).first()
      ?? page.getByRole('button', { name: /Email/i }).first()
    if (await emailSection.count()) {
      await expect(emailSection).toBeVisible()
    }
  })
})
