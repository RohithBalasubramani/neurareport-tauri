import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

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

const views = [
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
    name: 'reports',
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

test.describe('Accessibility audit', () => {
  for (const view of views) {
    test(`${view.name} has no serious violations @a11y`, async ({ page }) => {
      const consoleMessages = captureConsole(page)
      await view.prepare(page)

      const results = await new AxeBuilder({ page }).analyze()
      const serious = results.violations.filter((violation) =>
        ['serious', 'critical'].includes(violation.impact ?? ''),
      )

      expect(serious).toEqual([])
      expect(consoleMessages).toEqual([])
    })
  }
})
