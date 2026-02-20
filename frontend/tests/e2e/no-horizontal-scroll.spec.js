import { test, expect } from '@playwright/test'

const viewports = [
  { width: 360, height: 780 },
  { width: 390, height: 820 },
  { width: 414, height: 896 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1280, height: 900 },
  { width: 1440, height: 900 },
]

const scenarios = [
  {
    name: 'Dashboard',
    path: '/',
    prepare: async (page) => {
      // On smaller viewports this is rendered as a paragraph, not a heading.
      await expect(page.getByText('Welcome back')).toBeVisible()
    },
  },
  {
    name: 'Data Sources',
    path: '/connections',
    prepare: async (page) => {
      await expect(page.getByRole('button', { name: 'Add Data Source' })).toBeVisible()
    },
  },
  {
    name: 'Templates',
    path: '/templates',
    prepare: async (page) => {
      await expect(page.getByRole('button', { name: 'Upload Design' })).toBeVisible()
    },
  },
  {
    name: 'Reports',
    path: '/reports',
    prepare: async (page) => {
      await expect(page.getByText(/Run a Report/i).first()).toBeVisible()
    },
  },
]

test.describe('@ui Layout has no horizontal scroll', () => {
  for (const viewport of viewports) {
    test.describe(`${viewport.width}x${viewport.height}`, () => {
      for (const scenario of scenarios) {
        test(`${scenario.name}`, async ({ page }) => {
          await page.setViewportSize(viewport)
          await page.goto(scenario.path, { waitUntil: 'domcontentloaded' })
          await page.waitForLoadState('domcontentloaded')
          await scenario.prepare(page)
          await page.waitForTimeout(100)

          const { scrollWidth, clientWidth, offenders } = await page.evaluate(() => {
            const { documentElement } = document
            // Find elements that extend beyond the viewport; keep this list small for debugging.
            const offenders = []
            const maxOffenders = 10
            const viewportWidth = documentElement.clientWidth
            const elements = Array.from(document.body.querySelectorAll('*'))
            for (const el of elements) {
              if (offenders.length >= maxOffenders) break
              const style = window.getComputedStyle(el)
              if (style.display === 'none') continue
              const r = el.getBoundingClientRect()
              if (r.width <= viewportWidth + 1) continue
              if (r.right <= viewportWidth + 1) continue
              // Skip SVG paths etc.
              if (!el.tagName) continue
              offenders.push({
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                className: (el.className && typeof el.className === 'string') ? el.className.slice(0, 120) : null,
                width: Math.round(r.width),
                right: Math.round(r.right),
              })
            }
            return {
              scrollWidth: documentElement.scrollWidth,
              clientWidth: documentElement.clientWidth,
              offenders,
            }
          })

          // Helpful debug if a layout regresses.
          expect.soft(offenders, `${scenario.name} overflow offenders`).toEqual([])
          expect.soft(scrollWidth, `${scenario.name} width`).toBeLessThanOrEqual(clientWidth + 1)
        })
      }
    })
  }
})
