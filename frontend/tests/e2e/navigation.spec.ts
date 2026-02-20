import { test, expect } from '@playwright/test'

const captureConsole = (page) => {
  const messages: string[] = []
  page.on('console', (msg) => {
    if (['warning', 'error'].includes(msg.type())) {
      const text = msg.text()
      if (text.includes('net::ERR_CONNECTION_REFUSED')) return
      messages.push(`${msg.type()}: ${text}`)
    }
  })
  return messages
}

test.describe('Keyboard navigation', () => {
  test('skip link focuses main content @ui', async ({ page }) => {
    const consoleMessages = captureConsole(page)
    await page.goto('/')
    await page.keyboard.press('Tab')

    const skipLink = page.locator('a[href="#main-content"]')
    await expect(skipLink).toBeVisible()

    const outlineWidth = await skipLink.evaluate((el) => getComputedStyle(el).outlineWidth)
    expect(outlineWidth).not.toBe('0px')

    await page.keyboard.press('Enter')
    await expect(page.locator('#main-content')).toBeFocused()

    expect(consoleMessages).toEqual([])
  })

  test('tab order reaches setup navigation @ui', async ({ page }) => {
    const consoleMessages = captureConsole(page)
    await page.goto('/')

    // From the top of the page, keyboard users should be able to reach the primary sidebar navigation.
    // (Do not activate the skip link; that intentionally bypasses navigation.)
    await page.keyboard.press('Tab')

    const navItem = page.getByRole('button', { name: 'Data Sources' })
    let focused = false
    for (let i = 0; i < 40; i += 1) {
      await page.keyboard.press('Tab')
      const isFocused = await navItem.evaluate((el) => el === document.activeElement)
      if (isFocused) {
        focused = true
        break
      }
    }
    expect(focused).toBe(true)

    const reportsItem = page.getByRole('button', { name: 'My Reports' })
    let reached = false
    for (let i = 0; i < 40; i += 1) {
      await page.keyboard.press('Tab')
      const isFocused = await reportsItem.evaluate((el) => el === document.activeElement)
      if (isFocused) {
        reached = true
        break
      }
    }
    expect(reached).toBe(true)

    expect(consoleMessages).toEqual([])
  })
})
