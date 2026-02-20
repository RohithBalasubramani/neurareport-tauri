/**
 * FAST Element Execution Audit — clicks every actionable element on each page.
 * Optimized: navigates once per page, recovers state in-place (no re-nav per element).
 * Captures before/after screenshots + console/network logs.
 */
import { test, type Page } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'audit')
const DATA = path.join(__dirname, 'screenshots', 'audit', 'data')
fs.mkdirSync(SHOTS, { recursive: true })
fs.mkdirSync(DATA, { recursive: true })

const ALL_PAGES = [
  { route: '/', name: 'dashboard' },
  { route: '/connections', name: 'connections' },
  { route: '/templates', name: 'templates' },
  { route: '/reports', name: 'reports' },
  { route: '/jobs', name: 'jobs' },
  { route: '/schedules', name: 'schedules' },
  { route: '/query', name: 'query' },
  { route: '/documents', name: 'documents' },
  { route: '/spreadsheets', name: 'spreadsheets' },
  { route: '/connectors', name: 'connectors' },
  { route: '/enrichment', name: 'enrichment' },
  { route: '/federation', name: 'federation' },
  { route: '/synthesis', name: 'synthesis' },
  { route: '/docqa', name: 'docqa' },
  { route: '/workflows', name: 'workflows' },
  { route: '/dashboard-builder', name: 'dashboard-builder' },
  { route: '/knowledge', name: 'knowledge' },
  { route: '/design', name: 'design' },
  { route: '/visualization', name: 'visualization' },
  { route: '/agents', name: 'agents' },
  { route: '/ingestion', name: 'ingestion' },
  { route: '/settings', name: 'settings' },
  { route: '/activity', name: 'activity' },
  { route: '/search', name: 'search' },
  { route: '/ops', name: 'ops' },
  { route: '/stats', name: 'stats' },
  { route: '/history', name: 'history' },
  { route: '/analyze', name: 'analyze' },
  { route: '/summary', name: 'summary' },
]

const execPage = process.env.AUDIT_EXEC_PAGE
const targetPages = execPage ? ALL_PAGES.filter(p => p.name === execPage) : ALL_PAGES

interface ActionResult {
  id: string
  type: string
  label: string
  action: string
  outcome: string
  observation: string
}

async function recoverState(page: Page, originalUrl: string) {
  // Close any open dialogs/menus/popovers
  await page.keyboard.press('Escape')
  await page.waitForTimeout(150)
  await page.keyboard.press('Escape')
  await page.waitForTimeout(150)

  // Check if we navigated away
  const currentUrl = page.url()
  if (!currentUrl.includes(new URL(originalUrl, 'http://localhost:4173').pathname)) {
    await page.goto(originalUrl, { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1000)
  }
}

for (const pg of targetPages) {
  test(`Fast audit: ${pg.name} (${pg.route})`, async ({ page }) => {
    const consoleLogs: string[] = []
    const netErrors: string[] = []

    page.on('console', m => {
      if (m.type() === 'error') consoleLogs.push(`[error] ${m.text().substring(0, 150)}`)
    })
    page.on('requestfailed', r => {
      netErrors.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`)
    })

    // Load inventory
    const invPath = path.join(DATA, `${pg.name}-inventory.json`)
    if (!fs.existsSync(invPath)) {
      console.log(`No inventory for ${pg.name}`)
      return
    }
    const inventory = JSON.parse(fs.readFileSync(invPath, 'utf-8'))
    const elements = inventory.elements

    console.log(`\n${'='.repeat(70)}`)
    console.log(`FAST AUDIT: ${pg.name} (${pg.route}) — ${elements.length} elements`)
    console.log(`${'='.repeat(70)}`)

    // Navigate to the page
    await page.goto(pg.route, { waitUntil: 'domcontentloaded', timeout: 15000 })
    await page.waitForTimeout(2500)

    // Take overview screenshot
    await page.screenshot({ path: path.join(SHOTS, `${pg.name}-audit-overview.png`), fullPage: true })

    const results: ActionResult[] = []
    let pass = 0, partial = 0, fail = 0, untestable = 0, skipDisabled = 0

    for (let i = 0; i < elements.length; i++) {
      const el = elements[i]
      const label = (el.ariaLabel || el.text || el.selector).substring(0, 50)

      if (el.disabled) {
        results.push({ id: el.id, type: el.type, label, action: 'skip', outcome: 'skip-disabled', observation: 'Disabled element' })
        skipDisabled++
        continue
      }

      try {
        // Find the element — try multiple strategies
        let locator
        if (el.ariaLabel) {
          locator = page.locator(`[aria-label="${el.ariaLabel}"]`).first()
        } else if (el.selector.startsWith('#') || el.selector.startsWith('[data-testid')) {
          locator = page.locator(el.selector).first()
        } else if (el.text && el.text.length > 2 && el.text.length < 50) {
          locator = page.locator(`${el.tag}:has-text("${el.text.substring(0, 30).replace(/"/g, '\\"')}")`).first()
        } else {
          // Use bounding box coordinates for elements we can't reliably locate by text
          if (el.boundingBox && el.boundingBox.x > 0 && el.boundingBox.y > 0) {
            // Click by coordinates
            const cx = el.boundingBox.x + el.boundingBox.width / 2
            const cy = el.boundingBox.y + el.boundingBox.height / 2
            await page.mouse.click(cx, cy)
            await page.waitForTimeout(400)
            await recoverState(page, pg.route)
            results.push({ id: el.id, type: el.type, label, action: 'coord-click', outcome: 'pass', observation: `Clicked at (${Math.round(cx)}, ${Math.round(cy)})` })
            pass++
            continue
          }
          results.push({ id: el.id, type: el.type, label, action: 'locate', outcome: 'untestable', observation: 'No reliable selector or bounding box' })
          untestable++
          continue
        }

        const count = await locator.count()
        if (count === 0) {
          results.push({ id: el.id, type: el.type, label, action: 'locate', outcome: 'untestable', observation: 'Element not found in current DOM state' })
          untestable++
          continue
        }

        // Execute based on type
        let action = 'click'
        let observation = ''

        const urlBefore = page.url()

        switch (el.type) {
          case 'input-text':
          case 'input-search':
          case 'input-email':
          case 'input-number':
          case 'input-url':
          case 'input-password':
          case 'textarea':
            action = 'fill+clear'
            await locator.scrollIntoViewIfNeeded().catch(() => {})
            await locator.click({ force: true, timeout: 2000 })
            const oldVal = await locator.inputValue().catch(() => '')
            await locator.fill('audit-test')
            await page.waitForTimeout(200)
            await locator.fill(oldVal) // restore
            observation = 'Input filled and restored'
            break

          case 'input-file':
            action = 'skip-file'
            observation = 'File input requires real file — untestable'
            results.push({ id: el.id, type: el.type, label, action, outcome: 'untestable', observation })
            untestable++
            continue

          case 'checkbox':
          case 'switch':
          case 'radio':
            action = 'toggle+revert'
            await locator.scrollIntoViewIfNeeded().catch(() => {})
            await locator.click({ force: true, timeout: 2000 })
            await page.waitForTimeout(200)
            await locator.click({ force: true, timeout: 2000 }).catch(() => {}) // revert
            await page.waitForTimeout(200)
            observation = 'Toggled and reverted'
            break

          case 'select':
            action = 'open+close'
            await locator.scrollIntoViewIfNeeded().catch(() => {})
            await locator.click({ force: true, timeout: 2000 })
            await page.waitForTimeout(400)
            await page.keyboard.press('Escape')
            await page.waitForTimeout(200)
            observation = 'Select opened and closed'
            break

          case 'slider':
            action = 'nudge+revert'
            await locator.scrollIntoViewIfNeeded().catch(() => {})
            await locator.click({ force: true, timeout: 2000 })
            await page.keyboard.press('ArrowRight')
            await page.waitForTimeout(100)
            await page.keyboard.press('ArrowLeft')
            observation = 'Slider nudged right then left'
            break

          default:
            action = 'click'
            await locator.scrollIntoViewIfNeeded().catch(() => {})
            await locator.click({ force: true, timeout: 2000 })
            await page.waitForTimeout(400)

            const urlAfter = page.url()
            if (urlAfter !== urlBefore) {
              observation = `Navigated to ${urlAfter}`
            } else {
              observation = 'Clicked successfully'
            }
            break
        }

        // Recover state after action
        await recoverState(page, pg.route)

        results.push({ id: el.id, type: el.type, label, action, outcome: 'pass', observation })
        pass++

      } catch (err: any) {
        const msg = err.message?.substring(0, 80) || 'unknown'
        // Try coordinate fallback
        if (el.boundingBox && el.boundingBox.width > 0) {
          try {
            const cx = el.boundingBox.x + el.boundingBox.width / 2
            const cy = el.boundingBox.y + el.boundingBox.height / 2
            await page.mouse.click(cx, cy)
            await page.waitForTimeout(300)
            await recoverState(page, pg.route)
            results.push({ id: el.id, type: el.type, label, action: 'coord-fallback', outcome: 'partial', observation: `Selector failed, coord click at (${Math.round(cx)},${Math.round(cy)}). Error: ${msg}` })
            partial++
          } catch {
            results.push({ id: el.id, type: el.type, label, action: 'click', outcome: 'fail', observation: msg })
            fail++
          }
        } else {
          results.push({ id: el.id, type: el.type, label, action: 'click', outcome: 'fail', observation: msg })
          fail++
        }
      }

      // Progress logging every 20 elements
      if ((i + 1) % 20 === 0) {
        console.log(`  ... processed ${i + 1}/${elements.length} (P:${pass} F:${fail} U:${untestable})`)
      }
    }

    // Take final screenshot
    await page.screenshot({ path: path.join(SHOTS, `${pg.name}-audit-final.png`), fullPage: true })

    // Print per-element results
    console.log(`\nDETAILED RESULTS:`)
    results.forEach(r => {
      const icon = r.outcome === 'pass' ? '✅' : r.outcome === 'partial' ? '⚠️' : r.outcome === 'fail' ? '❌' : r.outcome === 'untestable' ? '🚫' : '⏭️'
      console.log(`  ${r.id} | ${icon} ${r.outcome.padEnd(14)} | ${r.type.padEnd(16)} | ${r.label.substring(0, 35).padEnd(35)} | ${r.action.padEnd(14)} | ${r.observation.substring(0, 50)}`)
    })

    console.log(`\n${'='.repeat(70)}`)
    console.log(`SUMMARY: ${pg.name}`)
    console.log(`  Total:        ${elements.length}`)
    console.log(`  ✅ Pass:       ${pass}`)
    console.log(`  ⚠️ Partial:    ${partial}`)
    console.log(`  ❌ Fail:        ${fail}`)
    console.log(`  🚫 Untestable: ${untestable}`)
    console.log(`  ⏭️ Disabled:    ${skipDisabled}`)
    console.log(`  Console errors: ${consoleLogs.length}`)
    console.log(`  Network errors: ${netErrors.length}`)
    console.log(`${'='.repeat(70)}`)

    // Save results
    fs.writeFileSync(
      path.join(DATA, `${pg.name}-results.json`),
      JSON.stringify({ page: pg.name, route: pg.route, total: elements.length, pass, partial, fail, untestable, skipDisabled, consoleErrors: consoleLogs, networkErrors: netErrors, results }, null, 2)
    )
  })
}
