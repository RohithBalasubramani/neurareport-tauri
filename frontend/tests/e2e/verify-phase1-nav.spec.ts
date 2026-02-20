/**
 * Phase 1: Navigation Structure + Route Reachability
 * Visits every route, captures full-page screenshot, logs interactive element counts.
 */
import { test, type Page } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'verify')

const ALL_ROUTES = [
  '/', '/connections', '/connectors', '/templates', '/reports',
  '/jobs', '/schedules', '/query', '/documents', '/spreadsheets',
  '/enrichment', '/federation', '/synthesis', '/docqa',
  '/workflows', '/dashboard-builder', '/knowledge', '/design',
  '/visualization', '/agents', '/ingestion', '/settings',
  '/activity', '/search', '/ops', '/stats', '/history',
  '/analyze', '/summary',
]

const consoleLogs: string[] = []
const netErrors: string[] = []

test.beforeEach(async ({ page }) => {
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') consoleLogs.push(`[${m.type()}] ${m.text().substring(0, 200)}`) })
  page.on('requestfailed', r => { netErrors.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`) })
})

test('Phase 1: Visit all 29 routes and capture screenshots', async ({ page }) => {
  for (const route of ALL_ROUTES) {
    const name = route === '/' ? 'dashboard' : route.slice(1)
    console.log(`\n>>> ${name} (${route})`)
    try {
      await page.goto(route, { waitUntil: 'domcontentloaded', timeout: 15000 })
      await page.waitForTimeout(2500)
      await page.screenshot({ path: path.join(SHOTS, `nav-${name}.png`), fullPage: true })
      const btns = await page.locator('button').count()
      const inputs = await page.locator('input, textarea').count()
      console.log(`  ✓ loaded | buttons=${btns} inputs=${inputs}`)
    } catch (e: any) {
      console.log(`  ✗ FAILED: ${e.message?.substring(0, 120)}`)
      await page.screenshot({ path: path.join(SHOTS, `nav-${name}-ERROR.png`) }).catch(() => {})
    }
  }
  console.log(`\n=== Console errors: ${consoleLogs.length} ===`)
  consoleLogs.slice(0, 30).forEach(l => console.log(l))
  console.log(`=== Network errors: ${netErrors.length} ===`)
  netErrors.slice(0, 20).forEach(l => console.log(l))
})

test('Phase 1B: Sidebar click-through navigation', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2000)

  // The sidebar uses MUI ListItemButton/ListItemText — find clickable items
  const sidebarItems = page.locator('[class*="MuiDrawer"] [class*="MuiListItemButton"], [class*="sidebar"] [role="button"]')
  const count = await sidebarItems.count()
  console.log(`Sidebar clickable items found: ${count}`)

  // If that didn't work, try broader selectors
  if (count === 0) {
    const allClickable = page.locator('[class*="Drawer"] [class*="ListItem"]')
    const c2 = await allClickable.count()
    console.log(`Fallback: Drawer ListItems found: ${c2}`)
  }

  await page.screenshot({ path: path.join(SHOTS, `nav-sidebar-overview.png`), fullPage: true })

  // Try clicking sidebar text items directly
  const sidebarTexts = [
    'Dashboard', 'My Reports', 'Templates', 'Running Jobs', 'Schedules',
    'Data Sources', 'Connectors', 'Query Builder',
    'Documents', 'Spreadsheets', 'Enrichment', 'Federation',
  ]

  for (const txt of sidebarTexts) {
    console.log(`\nClicking sidebar: "${txt}"`)
    try {
      const item = page.locator(`text="${txt}"`).first()
      if (await item.count() === 0) {
        console.log(`  — not visible, skipping`)
        continue
      }
      await item.scrollIntoViewIfNeeded()
      await item.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(1500)
      const url = page.url()
      console.log(`  → navigated to: ${url}`)
      await page.screenshot({ path: path.join(SHOTS, `nav-sidebar-${txt.replace(/\s+/g, '')}.png`) })
    } catch (e: any) {
      console.log(`  ✗ click failed: ${e.message?.substring(0, 80)}`)
    }
  }
})
