/**
 * Element Execution Audit — clicks every actionable element on a page,
 * captures before/after screenshots, logs outcomes.
 */
import { test, type Page } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'audit')
const DATA = path.join(__dirname, 'screenshots', 'audit', 'data')

interface ElementResult {
  id: string
  type: string
  label: string
  action: string
  outcome: 'pass' | 'partial' | 'fail' | 'untestable' | 'skip-disabled'
  beforeShot: string
  afterShot: string
  observation: string
  consoleErrors: string[]
  networkErrors: string[]
}

// Pages to execute — controlled by env var AUDIT_EXEC_PAGE
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

async function getPageState(page: Page): Promise<string> {
  // Capture a fingerprint of the page state for comparison
  return await page.evaluate(() => {
    const dialogs = document.querySelectorAll('[role="dialog"], [role="presentation"], [class*="MuiModal"], [class*="MuiPopover"], [class*="MuiMenu-paper"]')
    const snackbars = document.querySelectorAll('[class*="MuiSnackbar"]')
    const url = window.location.href
    const bodyText = document.body.innerText.substring(0, 500)
    return JSON.stringify({
      url,
      dialogCount: dialogs.length,
      snackbarCount: snackbars.length,
      bodyLen: bodyText.length,
      bodySnippet: bodyText.substring(0, 200),
    })
  })
}

for (const pg of targetPages) {
  test(`Execute all elements on ${pg.name}`, async ({ page }) => {
    const consoleLogs: string[] = []
    const netErrors: string[] = []

    page.on('console', m => {
      if (m.type() === 'error' || m.type() === 'warning')
        consoleLogs.push(`[${m.type()}] ${m.text().substring(0, 150)}`)
    })
    page.on('requestfailed', r => {
      netErrors.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`)
    })

    // Load inventory
    const invPath = path.join(DATA, `${pg.name}-inventory.json`)
    if (!fs.existsSync(invPath)) {
      console.log(`No inventory for ${pg.name}, run enumeration first`)
      return
    }
    const inventory = JSON.parse(fs.readFileSync(invPath, 'utf-8'))
    const elements = inventory.elements

    console.log(`\n${'='.repeat(70)}`)
    console.log(`EXECUTING: ${pg.name} (${pg.route}) — ${elements.length} elements`)
    console.log(`${'='.repeat(70)}`)

    const results: ElementResult[] = []
    let passCount = 0
    let failCount = 0
    let partialCount = 0
    let untestableCount = 0
    let skipDisabledCount = 0

    for (let i = 0; i < elements.length; i++) {
      const el = elements[i]
      const label = (el.ariaLabel || el.text || el.selector).substring(0, 50)

      // Re-navigate to page for clean state (essential for isolated testing)
      await page.goto(pg.route, { waitUntil: 'domcontentloaded', timeout: 15000 })
      await page.waitForTimeout(1500)

      // Clear console/network logs for this element
      const beforeConsole = consoleLogs.length
      const beforeNet = netErrors.length

      // Skip disabled elements
      if (el.disabled) {
        console.log(`  ${el.id} | ${el.type.padEnd(16)} | SKIP-DISABLED | ${label}`)
        results.push({
          id: el.id, type: el.type, label, action: 'skip',
          outcome: 'skip-disabled',
          beforeShot: '', afterShot: '',
          observation: 'Element is disabled — cannot interact',
          consoleErrors: [], networkErrors: [],
        })
        skipDisabledCount++
        continue
      }

      // Determine the best selector strategy
      let locator
      try {
        if (el.ariaLabel) {
          locator = page.locator(`[aria-label="${el.ariaLabel}"]`).first()
        } else if (el.selector.startsWith('#')) {
          locator = page.locator(el.selector).first()
        } else if (el.selector.startsWith('[data-testid')) {
          locator = page.locator(el.selector).first()
        } else {
          // Use bounding box position to find element
          locator = page.locator(`${el.tag}`).filter({ hasText: el.text.substring(0, 30) || undefined }).first()
        }

        // Verify element exists
        const count = await locator.count()
        if (count === 0) {
          // Fallback: try by exact text content
          if (el.text) {
            locator = page.locator(`text="${el.text.substring(0, 40)}"`).first()
          }
          const count2 = await locator.count()
          if (count2 === 0) {
            console.log(`  ${el.id} | ${el.type.padEnd(16)} | UNTESTABLE    | ${label} (not found after re-nav)`)
            results.push({
              id: el.id, type: el.type, label, action: 'locate',
              outcome: 'untestable',
              beforeShot: '', afterShot: '',
              observation: 'Element not found after page re-navigation (dynamic/conditional rendering)',
              consoleErrors: [], networkErrors: [],
            })
            untestableCount++
            continue
          }
        }

        // BEFORE screenshot
        const beforeShot = `${el.id}-before.png`
        await page.screenshot({ path: path.join(SHOTS, beforeShot) })
        const beforeState = await getPageState(page)

        // Execute the action based on type
        let action = 'click'
        try {
          switch (el.type) {
            case 'input-text':
            case 'input-search':
            case 'input-email':
            case 'input-password':
            case 'input-number':
            case 'input-url':
            case 'textarea':
              action = 'fill'
              await locator.scrollIntoViewIfNeeded().catch(() => {})
              await locator.click({ force: true, timeout: 3000 })
              await locator.fill('test-audit-value')
              await page.waitForTimeout(300)
              break

            case 'input-file':
              action = 'file-input'
              // Cannot upload without a real file — mark as untestable
              throw new Error('UNTESTABLE: file input requires real file')

            case 'checkbox':
            case 'switch':
            case 'radio':
              action = 'toggle'
              await locator.scrollIntoViewIfNeeded().catch(() => {})
              await locator.click({ force: true, timeout: 3000 })
              await page.waitForTimeout(500)
              // Toggle back
              await locator.click({ force: true, timeout: 3000 }).catch(() => {})
              await page.waitForTimeout(300)
              break

            case 'select':
            case 'combobox':
              action = 'open-select'
              await locator.scrollIntoViewIfNeeded().catch(() => {})
              await locator.click({ force: true, timeout: 3000 })
              await page.waitForTimeout(800)
              // Close by pressing Escape
              await page.keyboard.press('Escape')
              await page.waitForTimeout(300)
              break

            case 'slider':
              action = 'drag-slider'
              // Sliders need keyboard interaction
              await locator.scrollIntoViewIfNeeded().catch(() => {})
              await locator.click({ force: true, timeout: 3000 })
              await page.keyboard.press('ArrowRight')
              await page.waitForTimeout(300)
              await page.keyboard.press('ArrowLeft') // revert
              break

            default:
              // Default: click
              action = 'click'
              await locator.scrollIntoViewIfNeeded().catch(() => {})
              await locator.click({ force: true, timeout: 3000 })
              await page.waitForTimeout(800)
              break
          }

          // AFTER screenshot
          const afterShot = `${el.id}-after.png`
          await page.screenshot({ path: path.join(SHOTS, afterShot) })
          const afterState = await getPageState(page)

          // Determine what changed
          const newConsole = consoleLogs.slice(beforeConsole)
          const newNet = netErrors.slice(beforeNet)
          const stateChanged = beforeState !== afterState

          let observation = ''
          if (stateChanged) {
            try {
              const before = JSON.parse(beforeState)
              const after = JSON.parse(afterState)
              if (before.url !== after.url) observation += `Navigation: ${after.url}. `
              if (before.dialogCount !== after.dialogCount) observation += `Dialog opened/closed (${before.dialogCount} → ${after.dialogCount}). `
              if (before.snackbarCount !== after.snackbarCount) observation += `Snackbar appeared. `
              if (Math.abs(before.bodyLen - after.bodyLen) > 50) observation += `Content changed significantly. `
            } catch {}
          }
          if (!observation) observation = stateChanged ? 'UI state changed' : 'No visible change detected'

          // Close any dialogs/menus/popups that opened
          await page.keyboard.press('Escape')
          await page.waitForTimeout(200)

          const outcome = newNet.length > 0 ? 'partial' : 'pass'
          if (outcome === 'pass') passCount++
          else partialCount++

          console.log(`  ${el.id} | ${el.type.padEnd(16)} | ✅ ${action.padEnd(12)} | ${label.substring(0, 35)} | ${observation.substring(0, 50)}`)

          results.push({
            id: el.id, type: el.type, label, action,
            outcome,
            beforeShot, afterShot,
            observation,
            consoleErrors: newConsole,
            networkErrors: newNet,
          })

        } catch (actionErr: any) {
          const msg = actionErr.message?.substring(0, 100) || 'unknown'
          if (msg.includes('UNTESTABLE')) {
            console.log(`  ${el.id} | ${el.type.padEnd(16)} | 🚫 UNTESTABLE  | ${label} | ${msg}`)
            results.push({
              id: el.id, type: el.type, label, action,
              outcome: 'untestable',
              beforeShot: '', afterShot: '',
              observation: msg,
              consoleErrors: [], networkErrors: [],
            })
            untestableCount++
          } else {
            // Try force click as last resort
            try {
              await page.mouse.click(el.boundingBox?.x || 0, el.boundingBox?.y || 0)
              await page.waitForTimeout(500)
              const afterShot = `${el.id}-after.png`
              await page.screenshot({ path: path.join(SHOTS, afterShot) })
              console.log(`  ${el.id} | ${el.type.padEnd(16)} | ⚠️ PARTIAL     | ${label} | force-clicked at coords`)
              results.push({
                id: el.id, type: el.type, label, action: 'force-click-coords',
                outcome: 'partial',
                beforeShot: `${el.id}-before.png`, afterShot,
                observation: `Normal click failed, used coordinate click. Error: ${msg}`,
                consoleErrors: consoleLogs.slice(beforeConsole),
                networkErrors: netErrors.slice(beforeNet),
              })
              partialCount++
            } catch {
              console.log(`  ${el.id} | ${el.type.padEnd(16)} | ❌ FAIL        | ${label} | ${msg}`)
              results.push({
                id: el.id, type: el.type, label, action,
                outcome: 'fail',
                beforeShot: `${el.id}-before.png`, afterShot: '',
                observation: `Click failed: ${msg}`,
                consoleErrors: consoleLogs.slice(beforeConsole),
                networkErrors: netErrors.slice(beforeNet),
              })
              failCount++
            }
          }
        }
      } catch (outerErr: any) {
        console.log(`  ${el.id} | ${el.type.padEnd(16)} | ❌ FAIL        | ${label} | ${outerErr.message?.substring(0, 80)}`)
        results.push({
          id: el.id, type: el.type, label, action: 'locate',
          outcome: 'fail',
          beforeShot: '', afterShot: '',
          observation: `Locator failed: ${outerErr.message?.substring(0, 100)}`,
          consoleErrors: [], networkErrors: [],
        })
        failCount++
      }
    }

    // Summary
    console.log(`\n${'='.repeat(70)}`)
    console.log(`RESULTS FOR ${pg.name}:`)
    console.log(`  Total elements: ${elements.length}`)
    console.log(`  ✅ Passed:      ${passCount}`)
    console.log(`  ⚠️ Partial:     ${partialCount}`)
    console.log(`  ❌ Failed:       ${failCount}`)
    console.log(`  🚫 Untestable:  ${untestableCount}`)
    console.log(`  ⏭️ Skip-disabled: ${skipDisabledCount}`)
    console.log(`${'='.repeat(70)}`)

    // Save results
    const outPath = path.join(DATA, `${pg.name}-results.json`)
    fs.writeFileSync(outPath, JSON.stringify({
      page: pg.name,
      route: pg.route,
      totalElements: elements.length,
      passed: passCount,
      partial: partialCount,
      failed: failCount,
      untestable: untestableCount,
      skipDisabled: skipDisabledCount,
      results,
    }, null, 2))
  })
}
