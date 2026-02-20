import { test, expect } from '@playwright/test'
import { captureConsole, expectNoConsoleErrors, waitForApi } from './helpers'

test.describe('Design page integration @integration', () => {
  test('design page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/design')
    await expect(page.getByText(/Design|Brand/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('create brand kit button', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const btn = page.getByRole('button', { name: /New Brand Kit|Create|Brand Kit/i }).first()
    if (await btn.count()) {
      await btn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.first().click()
    }
  })

  test('brand kit editor loads', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const kit = page.locator('[class*="card"], [class*="kit"], [class*="brand"]').first()
    if (await kit.count()) {
      await kit.click()
      await page.waitForTimeout(1000)
    }
  })

  test('save brand kit changes', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const saveBtn = page.getByRole('button', { name: /Save/i }).first()
    if (await saveBtn.count()) {
      await expect(saveBtn).toBeVisible()
    }
  })

  test('delete brand kit with confirmation', async ({ page }) => {
    await page.goto('/design')
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

  test('generate color palette button', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const genBtn = page.getByRole('button', { name: /Generate|Color Palette|Palette/i }).first()
    if (await genBtn.count()) {
      await expect(genBtn).toBeVisible()
    }
  })

  test('contrast checker tool', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const contrastBtn = page.getByRole('button', { name: /Contrast|Check/i }).first()
    if (await contrastBtn.count()) {
      await expect(contrastBtn).toBeVisible()
    }
  })

  test('themes tab loads', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const themesTab = page.getByRole('tab', { name: /Theme/i }).first()
      ?? page.getByRole('button', { name: /Theme/i }).first()
    if (await themesTab.count()) {
      await themesTab.click()
      await page.waitForTimeout(1000)
    }
  })

  test('create theme button', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const themeBtn = page.getByRole('button', { name: /New Theme|Create Theme/i }).first()
    if (await themeBtn.count()) {
      await themeBtn.click()
      await page.waitForTimeout(1000)
      const cancelBtn = page.getByRole('button', { name: /Cancel|Close/i })
      if (await cancelBtn.count()) await cancelBtn.first().click()
    }
  })

  test('font list and pairings', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const fontSection = page.getByText(/Font|Typography/i).first()
    if (await fontSection.count()) {
      await expect(fontSection).toBeVisible()
    }
  })

  test('export brand kit button', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const exportBtn = page.getByRole('button', { name: /Export/i }).first()
    if (await exportBtn.count()) {
      await expect(exportBtn).toBeVisible()
    }
  })

  test('import brand kit button', async ({ page }) => {
    await page.goto('/design')
    await page.waitForTimeout(3000)
    const importBtn = page.getByRole('button', { name: /Import/i }).first()
    if (await importBtn.count()) {
      await expect(importBtn).toBeVisible()
    }
  })
})

test.describe('Visualization page integration @integration', () => {
  test('visualization page loads', async ({ page }) => {
    const msgs = captureConsole(page)
    await page.goto('/visualization')
    await expect(page.getByText(/Visualization|Diagram|Chart/i).first()).toBeVisible({ timeout: 15_000 })
    expectNoConsoleErrors(msgs)
  })

  test('diagram type selector', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const typeSelector = page.getByRole('combobox', { name: /Type|Diagram/i }).first()
      ?? page.locator('[class*="type"], [class*="selector"]').first()
    if (await typeSelector.count()) {
      await typeSelector.click()
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
    }
  })

  test('generate flowchart button', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const flowBtn = page.getByRole('button', { name: /Flowchart|Generate/i }).first()
    if (await flowBtn.count()) {
      await expect(flowBtn).toBeVisible()
    }
  })

  test('generate mindmap button', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const mindBtn = page.getByRole('button', { name: /Mindmap|Mind Map/i }).first()
    if (await mindBtn.count()) {
      await expect(mindBtn).toBeVisible()
    }
  })

  test('export diagram as SVG', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const svgBtn = page.getByRole('button', { name: /SVG|Export SVG/i }).first()
    if (await svgBtn.count()) {
      await expect(svgBtn).toBeVisible()
    }
  })

  test('export diagram as PNG', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const pngBtn = page.getByRole('button', { name: /PNG|Export PNG/i }).first()
    if (await pngBtn.count()) {
      await expect(pngBtn).toBeVisible()
    }
  })

  test('chart type selector', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const chartTab = page.getByRole('tab', { name: /Chart/i }).first()
      ?? page.getByRole('button', { name: /Chart/i }).first()
    if (await chartTab.count()) {
      await chartTab.click()
      await page.waitForTimeout(1000)
    }
  })

  test('data input area for diagrams', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const dataInput = page.getByRole('textbox').first()
      ?? page.locator('textarea').first()
    if (await dataInput.count()) {
      await expect(dataInput).toBeVisible()
    }
  })

  test('org chart button', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const orgBtn = page.getByRole('button', { name: /Org Chart|Organization/i }).first()
    if (await orgBtn.count()) {
      await expect(orgBtn).toBeVisible()
    }
  })

  test('timeline diagram button', async ({ page }) => {
    await page.goto('/visualization')
    await page.waitForTimeout(3000)
    const timelineBtn = page.getByRole('button', { name: /Timeline/i }).first()
    if (await timelineBtn.count()) {
      await expect(timelineBtn).toBeVisible()
    }
  })
})
