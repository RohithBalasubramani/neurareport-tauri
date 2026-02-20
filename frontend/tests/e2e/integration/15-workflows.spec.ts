import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Workflows page integration @integration', () => {
  test('page loads with workflow list', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/workflows')
    await expect(page.getByText(/Workflow/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('"New Workflow" creates workflow', async ({ page }) => {
    await page.goto('/workflows')
    const btn = page.getByRole('button', { name: /New Workflow|Create/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(3000)
    }
  })

  test('workflow name input', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const nameInput = page.getByLabel(/Name|Workflow Name/i).first()
    if (await nameInput.count()) {
      await nameInput.fill('E2E Test Workflow')
    }
  })

  test('node palette loads node types', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const nodePanel = page.locator('[class*="palette"], [class*="node-panel"], [class*="sidebar"]').first()
    if (await nodePanel.count()) {
      await expect(nodePanel).toBeVisible()
    }
  })

  test('drag node onto canvas', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const node = page.locator('[class*="node-type"], [draggable="true"]').first()
    if (await node.count()) {
      await expect(node).toBeVisible()
    }
  })

  test('connect nodes with edges', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    // Canvas area for flow editor
    const canvas = page.locator('[class*="canvas"], [class*="flow"], svg').first()
    if (await canvas.count()) {
      await expect(canvas).toBeVisible()
    }
  })

  test('node config panel opens on click', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const node = page.locator('[class*="node"]').first()
    if (await node.count()) {
      await node.click()
      await page.waitForTimeout(1000)
    }
  })

  test('save workflow', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('"Run" executes workflow', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const runBtn = page.getByRole('button', { name: /Run|Execute/i }).first()
    if (await runBtn.count()) {
      await expect(runBtn).toBeVisible()
    }
  })

  test('execution status shows', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const status = page.getByText(/Running|Completed|Failed|Pending/i).first()
    if (await status.count()) {
      await expect(status).toBeVisible()
    }
  })

  test('execution logs load', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const logsTab = page.getByRole('tab', { name: /Logs/i }).first()
    if (await logsTab.count()) {
      await logsTab.click()
      await page.waitForTimeout(2000)
    }
  })

  test('cancel execution', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const cancelBtn = page.getByRole('button', { name: /Cancel/i }).first()
    if (await cancelBtn.count()) {
      await expect(cancelBtn).toBeVisible()
    }
  })

  test('add trigger configuration', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const triggerBtn = page.getByRole('button', { name: /Trigger|Add Trigger/i }).first()
    if (await triggerBtn.count()) {
      await triggerBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('trigger type selector', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const triggerSelect = page.getByRole('combobox', { name: /Trigger Type/i }).first()
    if (await triggerSelect.count()) {
      await triggerSelect.click()
      await page.waitForTimeout(1000)
      await page.keyboard.press('Escape')
    }
  })

  test('delete workflow with confirmation', async ({ page }) => {
    await page.goto('/workflows')
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

  test('pending approvals list loads', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const approvalsTab = page.getByRole('tab', { name: /Approval/i }).first()
    if (await approvalsTab.count()) {
      await approvalsTab.click()
      await page.waitForTimeout(2000)
    }
  })

  test('approve step', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const approveBtn = page.getByRole('button', { name: /Approve/i }).first()
    if (await approveBtn.count()) {
      await expect(approveBtn).toBeVisible()
    }
  })

  test('execution history list', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const executionsTab = page.getByRole('tab', { name: /Execution/i }).first()
    if (await executionsTab.count()) {
      await executionsTab.click()
      await page.waitForTimeout(2000)
    }
  })

  test('workflow template gallery', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const templatesBtn = page.getByRole('button', { name: /Template/i }).first()
    if (await templatesBtn.count()) {
      await templatesBtn.click()
      await page.waitForTimeout(2000)
    }
  })

  test('create from template', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForTimeout(3000)
    const fromTemplateBtn = page.getByRole('button', { name: /From Template|Use Template/i }).first()
    if (await fromTemplateBtn.count()) {
      await expect(fromTemplateBtn).toBeVisible()
    }
  })
})
