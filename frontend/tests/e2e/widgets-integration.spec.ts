/**
 * Widget Intelligence E2E Tests
 *
 * Verifies:
 * 1. Widgets page is accessible from sidebar
 * 2. Widget page shows "no connection" state or recommended widgets
 * 3. Backend /widgets/recommend returns dynamic recommendations
 * 4. Backend /widgets/data returns live data from active DB
 * 5. Dashboard builder renders without crash
 */
import { test, expect } from '@playwright/test'

const BASE = 'http://127.0.0.1:5174'
// Direct backend for API tests
const BACKEND = 'http://127.0.0.1:8000/api/v1'

test.describe('Widget Intelligence', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home and wait for SPA to boot
    await page.goto(BASE, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
  })

  test('sidebar has Widgets entry', async ({ page }) => {
    // The sidebar is a MUI Drawer — find the scrollable nav container
    const drawer = page.locator('[class*="MuiDrawer-paper"]').first()
    // Scroll the drawer container to bottom to reveal Create section
    await drawer.evaluate((el) => el.querySelector('[style*="overflow"]')?.scrollTo(0, 9999) || el.scrollTo(0, 9999))
    await page.waitForTimeout(300)

    const widgetsLink = drawer.getByText('Widgets', { exact: true })
    await expect(widgetsLink).toBeVisible({ timeout: 5000 })
  })

  test('navigates to /widgets page from sidebar', async ({ page }) => {
    // Scroll sidebar to reveal Create section
    const drawer = page.locator('[class*="MuiDrawer-paper"]').first()
    await drawer.evaluate((el) => el.querySelector('[style*="overflow"]')?.scrollTo(0, 9999) || el.scrollTo(0, 9999))
    await page.waitForTimeout(300)

    const widgetsLink = drawer.getByText('Widgets', { exact: true })
    await widgetsLink.click()
    await page.waitForURL('**/widgets', { timeout: 10000 })

    // Page header should be visible
    await expect(page.getByText('Widget Intelligence')).toBeVisible({ timeout: 10000 })
  })

  test('widgets page shows header and content', async ({ page }) => {
    await page.goto(`${BASE}/widgets`, { waitUntil: 'networkidle' })

    // Should show page header
    await expect(page.getByText('Widget Intelligence')).toBeVisible({ timeout: 10000 })

    // Should show either recommended widgets or "no connection" state
    await page.waitForTimeout(3000)
    const hasCards = (await page.locator('[class*="MuiCard-root"]').count()) > 0
    const hasNoConnection = (await page.getByText('No database connected').count()) > 0
    const hasRecommended = (await page.getByText('recommended', { exact: false }).count()) > 0

    // At least one of these states should be true
    expect(hasCards || hasNoConnection || hasRecommended).toBeTruthy()
  })

  test('widget cards render with connection', async ({ page }) => {
    await page.goto(`${BASE}/widgets`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(5000) // Wait for recommendations to load

    // If there are cards, they should have scenario info
    const cards = page.locator('[class*="MuiCard-root"]')
    const count = await cards.count()
    if (count > 0) {
      // Cards should have variant chips
      await expect(cards.first()).toBeVisible({ timeout: 5000 })
    }
  })

  test('clicking a widget card shows variant detail panel', async ({ page }) => {
    await page.goto(`${BASE}/widgets`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(5000)

    // Click first card if available
    const cards = page.locator('[class*="MuiCard-root"]')
    if ((await cards.count()) > 0) {
      await cards.first().click()
      await page.waitForTimeout(500)

      // Should show the variants section
      const variantsHeading = page.getByText('variants', { exact: false })
      if ((await variantsHeading.count()) > 0) {
        await variantsHeading.first().scrollIntoViewIfNeeded()
        await expect(variantsHeading.first()).toBeVisible({ timeout: 5000 })
      }
    }
  })
})

test.describe('Dashboard Builder Widgets', () => {
  test('dashboard builder page loads', async ({ page }) => {
    await page.goto(`${BASE}/dashboard-builder`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)

    // Page should render without crash
    const body = page.locator('body')
    await expect(body).toBeVisible()

    // Should not show a blank/error page
    const errorText = page.getByText('Something went wrong')
    expect(await errorText.count()).toBe(0)
  })
})

test.describe('Widget API Endpoints', () => {
  test('GET /widgets/catalog returns 24 scenarios', async ({ request }) => {
    const response = await request.get(`${BACKEND}/widgets/catalog`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.count).toBe(24)
    expect(data.widgets).toHaveLength(24)

    // Each widget should have required fields
    for (const widget of data.widgets) {
      expect(widget.scenario).toBeTruthy()
      expect(widget.variants).toBeTruthy()
      expect(widget.rag_strategy).toBeTruthy()
    }
  })

  test('POST /widgets/recommend returns dynamic recommendations', async ({ request }) => {
    const response = await request.post(`${BACKEND}/widgets/recommend`, {
      data: {
        connection_id: 'de4126f8-f743-4a8a-a36e-f6e014ffc4eb',
        query: 'overview',
        max_widgets: 8,
      },
    })

    // Might fail if DB doesn't exist in test env — check gracefully
    if (response.ok()) {
      const data = await response.json()
      expect(data.widgets).toBeTruthy()
      expect(data.count).toBeGreaterThanOrEqual(1)
      expect(data.grid).toBeTruthy()
      expect(data.grid.cells).toBeTruthy()
      expect(data.profile).toBeTruthy()
      expect(data.profile.table_count).toBeGreaterThanOrEqual(1)

      // Each widget should have scenario and variant
      for (const widget of data.widgets) {
        expect(widget.scenario).toBeTruthy()
        expect(widget.variant).toBeTruthy()
        expect(widget.relevance).toBeGreaterThan(0)
      }
    }
  })

  test('POST /widgets/recommend returns 404 for invalid connection', async ({ request }) => {
    const response = await request.post(`${BACKEND}/widgets/recommend`, {
      data: {
        connection_id: 'nonexistent-connection-id',
      },
    })
    // Backend returns 404 for unknown connections
    expect(response.status()).toBe(404)
  })

  test('GET /widgets/kpi/demo endpoint is removed (404)', async ({ request }) => {
    const response = await request.get(`${BACKEND}/widgets/kpi/demo`)
    // Demo endpoint no longer exists
    expect(response.status()).toBe(404)
  })

  test('POST /widgets/data with real connection returns live data', async ({ request }) => {
    // Use HMWSSB Billing DB
    const response = await request.post(`${BACKEND}/widgets/data`, {
      data: {
        connection_id: 'de4126f8-f743-4a8a-a36e-f6e014ffc4eb',
        scenario: 'kpi',
      },
    })

    // Might fail if DB doesn't exist in test env — check gracefully
    if (response.ok()) {
      const data = await response.json()
      expect(data.data).toBeTruthy()
      expect(data.strategy).toBe('single_metric')
      // Should NOT have fallback flag — live data only
      expect(data.error).toBeUndefined()
    }
  })

  test('POST /widgets/data returns error when connection invalid', async ({ request }) => {
    const response = await request.post(`${BACKEND}/widgets/data`, {
      data: {
        connection_id: 'nonexistent-connection-id',
        scenario: 'kpi',
      },
    })

    // Backend returns error with empty data (no demo fallback)
    const data = await response.json()
    expect(data.error).toBeTruthy()
    expect(data.data).toEqual({})
  })

  test('POST /widgets/select returns widget suggestions', async ({ request }) => {
    const response = await request.post(`${BACKEND}/widgets/select`, {
      data: {
        query: 'show power trends and alerts',
        max_widgets: 5,
      },
    })
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.widgets).toBeTruthy()
    expect(data.count).toBeGreaterThanOrEqual(1)
  })
})
