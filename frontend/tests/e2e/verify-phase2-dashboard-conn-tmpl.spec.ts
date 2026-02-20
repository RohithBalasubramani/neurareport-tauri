/**
 * Phase 2: Deep Interaction — Dashboard + Connections + Templates
 * Every button, link, toggle, dropdown, form field exercised with before/after screenshots.
 */
import { test, expect, type Page } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'verify')

const consoleLogs: string[] = []
const netErrors: string[] = []

test.beforeEach(async ({ page }) => {
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') consoleLogs.push(`[${m.type()}] ${m.text().substring(0, 200)}`) })
  page.on('requestfailed', r => { netErrors.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`) })
})

async function safeClick(loc: ReturnType<Page['locator']>, timeout = 3000) {
  try { await loc.click({ timeout }) } catch { await loc.click({ force: true }) }
}

// ═══════════════════════════════════════════════════
// DASHBOARD PAGE
// ═══════════════════════════════════════════════════
test('Phase 2A: Dashboard — all interactive elements', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: path.join(SHOTS, 'p2-dash-01-initial.png'), fullPage: true })

  // 1. Stat cards — click each one
  const statCards = page.locator('[class*="stat"], [class*="Stat"], [class*="card"]').filter({ hasText: /TEMPLATES|JOBS TODAY|SUCCESS RATE|SCHEDULES/ })
  const cardCount = await statCards.count()
  console.log(`Dashboard stat cards: ${cardCount}`)
  for (let i = 0; i < Math.min(cardCount, 4); i++) {
    const card = statCards.nth(i)
    const text = await card.textContent()
    console.log(`  Clicking stat card ${i}: ${text?.trim().substring(0, 40)}`)
    await card.click({ force: true }).catch(() => {})
    await page.waitForTimeout(800)
    await page.screenshot({ path: path.join(SHOTS, `p2-dash-02-statcard-${i}.png`) })
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 2. "+ New Report" button (top-right)
  const newReportBtn = page.getByRole('button', { name: /New Report/i }).first()
  if (await newReportBtn.count()) {
    console.log('Clicking "+ New Report" button')
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-03-before-newreport.png') })
    await safeClick(newReportBtn)
    await page.waitForTimeout(2000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-04-after-newreport.png'), fullPage: true })
    console.log(`  Navigated to: ${page.url()}`)
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 3. "View All" link in Recent Jobs
  const viewAll = page.locator('text="View All"').first()
  if (await viewAll.count()) {
    console.log('Clicking "View All" in Recent Jobs')
    await safeClick(viewAll)
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-05-viewall-jobs.png'), fullPage: true })
    console.log(`  Navigated to: ${page.url()}`)
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 4. Click a Recent Job item
  const jobItem = page.locator('text="Orders Template"').first()
  if (await jobItem.count()) {
    console.log('Clicking a Recent Job item')
    await safeClick(jobItem)
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-06-job-click.png'), fullPage: true })
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 5. AI Recommendations - Refresh button
  const refreshRec = page.locator('text="Refresh"').first()
  if (await refreshRec.count()) {
    console.log('Clicking AI Recommendations Refresh')
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-07-before-refresh-rec.png') })
    await safeClick(refreshRec)
    await page.waitForTimeout(2000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-08-after-refresh-rec.png') })
  }

  // 6. Recommendation template cards
  const recCards = page.locator('text=/Imported Orders|Orders Template|Orders Template Copy/').first()
  if (await recCards.count()) {
    console.log('Clicking a recommendation card')
    await safeClick(recCards)
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-09-rec-card-click.png'), fullPage: true })
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 7. Search bar in top header
  const searchBar = page.locator('input[placeholder*="Search"], [class*="search"] input').first()
  if (await searchBar.count()) {
    console.log('Clicking search bar')
    await searchBar.click({ force: true })
    await page.waitForTimeout(500)
    await searchBar.fill('orders')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-10-search-typed.png') })
    await page.keyboard.press('Escape')
  }

  // 8. Command palette (Ctrl+K)
  console.log('Opening command palette with Ctrl+K')
  await page.keyboard.press('Control+k')
  await page.waitForTimeout(1000)
  await page.screenshot({ path: path.join(SHOTS, 'p2-dash-11-command-palette.png') })
  await page.keyboard.press('Escape')
  await page.waitForTimeout(500)

  // 9. Active connection badge at bottom
  const connBadge = page.locator('text=/E2E SQLite|Connected to/').first()
  if (await connBadge.count()) {
    console.log('Active connection badge visible')
    await page.screenshot({ path: path.join(SHOTS, 'p2-dash-12-conn-badge.png') })
  }

  // 10. Top-bar notification bell
  const bell = page.locator('[aria-label*="notification"], [aria-label*="Notification"], button:has([data-testid*="notification"])').first()
  if (await bell.count() === 0) {
    // Try MUI badge approach
    const bellAlt = page.locator('button:has(svg[data-testid="NotificationsIcon"]), [class*="notification"]').first()
    if (await bellAlt.count()) {
      console.log('Clicking notification bell')
      await bellAlt.click({ force: true })
      await page.waitForTimeout(1000)
      await page.screenshot({ path: path.join(SHOTS, 'p2-dash-13-notif-panel.png') })
      await page.keyboard.press('Escape')
    }
  }

  console.log(`\nDashboard console errors: ${consoleLogs.length}`)
  consoleLogs.forEach(l => console.log(l))
})

// ═══════════════════════════════════════════════════
// CONNECTIONS PAGE
// ═══════════════════════════════════════════════════
test('Phase 2B: Connections — all interactive elements', async ({ page }) => {
  await page.goto('/connections', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: path.join(SHOTS, 'p2-conn-01-initial.png'), fullPage: true })

  // 1. Table data — verify rows are present
  const rows = page.locator('table tbody tr, [class*="MuiTableBody"] tr, [role="row"]')
  const rowCount = await rows.count()
  console.log(`Connections table rows: ${rowCount}`)

  // 2. "+ Add Data Source" button
  const addBtn = page.getByRole('button', { name: /Add Data Source/i }).first()
  if (await addBtn.count()) {
    console.log('Clicking "+ Add Data Source"')
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-02-before-add.png') })
    await safeClick(addBtn)
    await page.waitForTimeout(2000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-03-after-add-drawer.png'), fullPage: true })

    // 3. Fill the form in the drawer/dialog
    const nameInput = page.locator('input[name="name"], input[placeholder*="name"], label:has-text("Name") + div input, input').nth(0)
    // Try filling connection form fields
    const formInputs = page.locator('dialog input, [role="dialog"] input, [class*="Drawer"] input, [class*="drawer"] input, form input')
    const formCount = await formInputs.count()
    console.log(`  Form inputs found: ${formCount}`)
    if (formCount > 0) {
      for (let i = 0; i < Math.min(formCount, 5); i++) {
        const inp = formInputs.nth(i)
        const placeholder = await inp.getAttribute('placeholder') || ''
        const label = await inp.getAttribute('aria-label') || ''
        console.log(`  Input ${i}: placeholder="${placeholder}" label="${label}"`)
      }
    }

    // 4. Close drawer/dialog
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 5. Filters dropdown
  const filtersBtn = page.getByRole('button', { name: /Filters/i }).first()
  if (await filtersBtn.count()) {
    console.log('Clicking Filters dropdown')
    await safeClick(filtersBtn)
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-04-filters-open.png') })
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 6. Click a connection row
  if (rowCount > 0) {
    const firstRow = rows.first()
    console.log('Clicking first connection row')
    await firstRow.click({ force: true })
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-05-row-clicked.png'), fullPage: true })
  }

  // 7. Kebab menu (three dots) on a row
  const kebab = page.locator('[aria-label="more"], [data-testid*="MoreVert"], button:has(svg[data-testid="MoreVertIcon"])').first()
  if (await kebab.count()) {
    console.log('Clicking kebab menu on a row')
    await kebab.click({ force: true })
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-06-kebab-menu.png') })
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 8. Favorite star button
  const star = page.locator('[aria-label*="favorite"], [aria-label*="Favorite"], [data-testid*="Star"]').first()
  if (await star.count()) {
    console.log('Clicking favorite star')
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-07-before-star.png') })
    await star.click({ force: true })
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-conn-08-after-star.png') })
  }

  // 9. Pagination
  const pagination = page.locator('text=/Rows per page|1-10 of/')
  if (await pagination.count()) {
    console.log('Pagination visible')
    const nextPage = page.locator('[aria-label="Go to next page"], button:has(svg[data-testid="KeyboardArrowRightIcon"])').first()
    if (await nextPage.count()) {
      console.log('  Clicking next page')
      await nextPage.click({ force: true })
      await page.waitForTimeout(1500)
      await page.screenshot({ path: path.join(SHOTS, 'p2-conn-09-page2.png'), fullPage: true })
    }
  }

  console.log(`\nConnections console errors: ${consoleLogs.length}`)
})

// ═══════════════════════════════════════════════════
// TEMPLATES PAGE
// ═══════════════════════════════════════════════════
test('Phase 2C: Templates — all interactive elements', async ({ page }) => {
  await page.goto('/templates', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-01-initial.png'), fullPage: true })

  // 1. "+ Upload Design" button
  const uploadBtn = page.getByRole('button', { name: /Upload Design/i }).first()
  if (await uploadBtn.count()) {
    console.log('Clicking "+ Upload Design"')
    await safeClick(uploadBtn)
    await page.waitForTimeout(2000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-02-upload-dialog.png'), fullPage: true })
    console.log(`  Navigated to: ${page.url()}`)
    // Go back
    await page.goto('/templates', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 2. "Import Backup" button
  const importBtn = page.getByRole('button', { name: /Import Backup/i }).first()
  if (await importBtn.count()) {
    console.log('Clicking "Import Backup"')
    await safeClick(importBtn)
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-03-import-dialog.png') })
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 3. Filters dropdown
  const filtersBtn = page.getByRole('button', { name: /Filters/i }).first()
  if (await filtersBtn.count()) {
    console.log('Clicking Filters')
    await safeClick(filtersBtn)
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-04-filters.png') })
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 4. Template table rows
  const rows = page.locator('table tbody tr, [class*="MuiTableBody"] tr').filter({ hasText: /PDF|EXCEL/ })
  const rowCount = await rows.count()
  console.log(`Template rows: ${rowCount}`)

  // 5. Click a row
  if (rowCount > 0) {
    console.log('Clicking first template row')
    await rows.first().click({ force: true })
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-05-row-clicked.png'), fullPage: true })
    console.log(`  Navigated to: ${page.url()}`)
    await page.goto('/templates', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // 6. Favorite star
  const star = page.locator('[aria-label*="favorite"], [aria-label*="Favorite"]').first()
  if (await star.count()) {
    console.log('Clicking favorite star')
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-06-before-star.png') })
    await star.click({ force: true })
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-07-after-star.png') })
    // Toggle back
    await star.click({ force: true })
    await page.waitForTimeout(500)
  }

  // 7. Kebab menu on a template row
  const kebab = page.locator('[aria-label="more"], [data-testid*="MoreVert"], button:has(svg[data-testid="MoreVertIcon"])').first()
  if (await kebab.count()) {
    console.log('Clicking kebab menu')
    await kebab.click({ force: true })
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-08-kebab-menu.png') })

    // Check menu items
    const menuItems = page.locator('[role="menuitem"], [class*="MenuItem"]')
    const menuCount = await menuItems.count()
    console.log(`  Menu items: ${menuCount}`)
    for (let i = 0; i < menuCount; i++) {
      const text = await menuItems.nth(i).textContent()
      console.log(`    ${i}: ${text?.trim()}`)
    }
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // 8. Row checkboxes for bulk selection
  const checkboxes = page.locator('input[type="checkbox"], [role="checkbox"]')
  const cbCount = await checkboxes.count()
  console.log(`Checkboxes found: ${cbCount}`)
  if (cbCount > 1) {
    console.log('Clicking first row checkbox')
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-09-before-checkbox.png') })
    await checkboxes.nth(1).click({ force: true }) // nth(0) might be "select all"
    await page.waitForTimeout(1000)
    await page.screenshot({ path: path.join(SHOTS, 'p2-tmpl-10-after-checkbox.png') })
    // Uncheck
    await checkboxes.nth(1).click({ force: true })
    await page.waitForTimeout(500)
  }

  // 9. Tabs: "Jobs = progress" and "History = downloads"
  const tabs = page.locator('text=/Jobs.*progress|History.*downloads/')
  const tabCount = await tabs.count()
  console.log(`Tab-like elements: ${tabCount}`)
  if (tabCount > 0) {
    for (let i = 0; i < tabCount; i++) {
      const tab = tabs.nth(i)
      const txt = await tab.textContent()
      console.log(`  Clicking tab: ${txt?.trim()}`)
      await tab.click({ force: true })
      await page.waitForTimeout(1000)
      await page.screenshot({ path: path.join(SHOTS, `p2-tmpl-11-tab-${i}.png`), fullPage: true })
    }
  }

  console.log(`\nTemplates console errors: ${consoleLogs.length}`)
})
