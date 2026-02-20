import { test, expect } from '@playwright/test'

test('minimal test', async ({ page }) => {
  await page.goto('http://127.0.0.1:5174')
  console.log('Page loaded successfully')
  expect(true).toBe(true)
})
