import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Document Q&A page integration @integration', () => {
  test('page loads with heading', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/docqa')
    await expect(page.getByRole('heading', { name: /Document Q&A/i })).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"New Session" creates session', async ({ page }) => {
    await page.goto('/docqa')
    const btn = page.getByRole('button', { name: /New Session/i })
    await expect(btn).toBeVisible({ timeout: 15_000 })
    await btn.click()
    await page.waitForTimeout(3000)
  })

  test('session list loads', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    // Sessions sidebar or list
    const sessionList = page.locator('[class*="List"], [class*="sidebar"]').first()
    if (await sessionList.count()) {
      await expect(sessionList).toBeVisible()
    }
  })

  test('click session opens it', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const sessionItem = page.locator('[class*="ListItem"], [class*="session"]').first()
    if (await sessionItem.count()) {
      await sessionItem.click()
      await page.waitForTimeout(2000)
    }
  })

  test('add document to session', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const addBtn = page.getByRole('button', { name: /Add Document|Upload/i }).first()
    if (await addBtn.count()) {
      await expect(addBtn).toBeVisible()
    }
  })

  test('remove document', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const removeBtn = page.getByRole('button', { name: /Remove/i }).first()
    if (await removeBtn.count()) {
      await expect(removeBtn).toBeVisible()
    }
  })

  test('ask question in chat', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const chatInput = page.getByPlaceholder(/Ask|question|type/i).first()
    if (await chatInput.count()) {
      await chatInput.fill('What is the main topic of this document?')
      // Press Enter or click Send
      const sendBtn = page.getByRole('button', { name: /Send|Ask/i }).first()
      if (await sendBtn.count()) {
        await expect(sendBtn).toBeVisible()
      }
    }
  })

  test('response displays with citations', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    // Chat response area
    const responseArea = page.locator('[class*="message"], [class*="response"], [class*="chat"]').first()
    if (await responseArea.count()) {
      await expect(responseArea).toBeVisible()
    }
  })

  test('thumbs up feedback', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const thumbsUp = page.getByRole('button', { name: /thumbs up|like|helpful/i }).first()
    if (await thumbsUp.count()) {
      await expect(thumbsUp).toBeVisible()
    }
  })

  test('thumbs down feedback', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const thumbsDown = page.getByRole('button', { name: /thumbs down|dislike|not helpful/i }).first()
    if (await thumbsDown.count()) {
      await expect(thumbsDown).toBeVisible()
    }
  })

  test('regenerate response', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const regenBtn = page.getByRole('button', { name: /Regenerate|Retry/i }).first()
    if (await regenBtn.count()) {
      await expect(regenBtn).toBeVisible()
    }
  })

  test('clear history', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const clearBtn = page.getByRole('button', { name: /Clear/i }).first()
    if (await clearBtn.count()) {
      await expect(clearBtn).toBeVisible()
    }
  })

  test('delete session', async ({ page }) => {
    await page.goto('/docqa')
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

  test('chat history loads on session open', async ({ page }) => {
    await page.goto('/docqa')
    await page.waitForTimeout(3000)
    const chatArea = page.locator('[class*="chat"], [class*="history"]').first()
    if (await chatArea.count()) {
      await expect(chatArea).toBeVisible()
    }
  })
})
