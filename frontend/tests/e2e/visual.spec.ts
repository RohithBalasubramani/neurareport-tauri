import { test, expect } from '@playwright/test'

const breakpoints = [
  { width: 360, height: 720 },
  { width: 768, height: 900 },
  { width: 1280, height: 900 },
]

const surfaces = [
  {
    name: 'dashboard',
    prepare: async (page) => {
      await page.goto('/')
      await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible()
    },
  },
  {
    name: 'connections',
    prepare: async (page) => {
      await page.goto('/connections')
      await expect(page.getByText('Data Sources', { exact: true })).toBeVisible()
    },
  },
  {
    name: 'templates',
    prepare: async (page) => {
      await page.goto('/templates')
      await expect(page.getByText('Templates', { exact: true })).toBeVisible()
    },
  },
  {
    name: 'reports-page',
    prepare: async (page) => {
      await page.goto('/reports')
      await expect(page.getByRole('heading', { name: 'Run a Report' })).toBeVisible()
    },
  },
  {
    name: 'setup-wizard',
    prepare: async (page) => {
      await page.goto('/setup/wizard')
      await page.waitForTimeout(150)
    },
  },
]

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

test.describe('Responsive visuals', () => {
  for (const viewport of breakpoints) {
    test(`renders without overflow at ${viewport.width}px @visual`, async ({ page }) => {
      const consoleMessages = captureConsole(page)
      await page.setViewportSize({ width: viewport.width, height: viewport.height })

      for (const surface of surfaces) {
        await surface.prepare(page)
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth > window.innerWidth + 1,
        )
        expect(overflow).toBeFalsy()

        const screenshot = await page.locator('#main-content').screenshot()
        test.info().attach(`${surface.name}-${viewport.width}`, {
          body: screenshot,
          contentType: 'image/png',
        })
      }

      expect(consoleMessages).toEqual([])
    })
  }
})
