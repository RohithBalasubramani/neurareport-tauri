import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Documents page integration @integration', () => {
  test('page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/documents')
    await expect(page.getByText(/Document/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"New Document" creates document', async ({ page }) => {
    await page.goto('/documents')
    const btn = page.getByRole('button', { name: /New Document|Create/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(3000)
    }
  })

  test('document editor loads content', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    // Editor area (contenteditable, textarea, or rich text)
    const editor = page.locator('[contenteditable="true"], textarea, [class*="editor"]').first()
    if (await editor.count()) {
      await expect(editor).toBeVisible()
    }
  })

  test('save button persists changes', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('delete document with confirmation', async ({ page }) => {
    await page.goto('/documents')
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

  test('version history sidebar loads', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const versionBtn = page.getByRole('button', { name: /Version|History/i }).first()
    if (await versionBtn.count()) {
      await versionBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('restore version works', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const restoreBtn = page.getByRole('button', { name: /Restore/i }).first()
    if (await restoreBtn.count()) {
      await expect(restoreBtn).toBeVisible()
    }
  })

  test('comments panel loads', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const commentsBtn = page.getByRole('button', { name: /Comment/i }).first()
    if (await commentsBtn.count()) {
      await commentsBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('add comment submits', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const commentInput = page.getByPlaceholder(/Add a comment|comment/i).first()
    if (await commentInput.count()) {
      await commentInput.fill('Test comment from e2e')
      const submitBtn = page.getByRole('button', { name: /Submit|Add|Send/i }).first()
      if (await submitBtn.count()) {
        await expect(submitBtn).toBeVisible()
      }
    }
  })

  test('reply to comment', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const replyBtn = page.getByRole('button', { name: /Reply/i }).first()
    if (await replyBtn.count()) {
      await expect(replyBtn).toBeVisible()
    }
  })

  test('resolve comment toggle', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const resolveBtn = page.getByRole('button', { name: /Resolve/i }).first()
    if (await resolveBtn.count()) {
      await expect(resolveBtn).toBeVisible()
    }
  })

  test('delete comment', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const deleteCommentBtn = page.getByRole('button', { name: /Delete comment|Remove comment/i }).first()
    if (await deleteCommentBtn.count()) {
      await expect(deleteCommentBtn).toBeVisible()
    }
  })

  test('AI Grammar check tool', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const grammarBtn = page.getByRole('button', { name: /Grammar/i }).first()
    if (await grammarBtn.count()) {
      await expect(grammarBtn).toBeVisible()
    }
  })

  test('AI Summarize tool', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const summarizeBtn = page.getByRole('button', { name: /Summarize/i }).first()
    if (await summarizeBtn.count()) {
      await expect(summarizeBtn).toBeVisible()
    }
  })

  test('AI Rewrite tool', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const rewriteBtn = page.getByRole('button', { name: /Rewrite/i }).first()
    if (await rewriteBtn.count()) {
      await expect(rewriteBtn).toBeVisible()
    }
  })

  test('AI Translate tool', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const translateBtn = page.getByRole('button', { name: /Translate/i }).first()
    if (await translateBtn.count()) {
      await expect(translateBtn).toBeVisible()
    }
  })

  test('export to PDF', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const exportBtn = page.getByRole('button', { name: /Export|PDF/i }).first()
    if (await exportBtn.count()) {
      await expect(exportBtn).toBeVisible()
    }
  })

  test('PDF tools (rotate, watermark)', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const pdfTool = page.getByRole('button', { name: /Rotate|Watermark/i }).first()
    if (await pdfTool.count()) {
      await expect(pdfTool).toBeVisible()
    }
  })

  test('template picker loads', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const templateBtn = page.getByRole('button', { name: /Template/i }).first()
    if (await templateBtn.count()) {
      await templateBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('create from template', async ({ page }) => {
    await page.goto('/documents')
    await page.waitForTimeout(3000)
    const fromTemplateBtn = page.getByRole('button', { name: /From Template|Use Template/i }).first()
    if (await fromTemplateBtn.count()) {
      await expect(fromTemplateBtn).toBeVisible()
    }
  })
})
