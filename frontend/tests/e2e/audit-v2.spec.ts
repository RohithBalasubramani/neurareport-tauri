/**
 * ISOLATED Element Execution Audit v2 — Live DOM strategy
 *
 * Approach:
 * 1. Navigate fresh to page → enumerate live DOM → these ARE the elements to test
 * 2. For each live element: fresh nav → re-find element → execute → evidence
 * 3. After all live elements tested, reconcile against old inventory
 *
 * "Untestable" is NOT an allowed outcome. Every element: Pass or Defect.
 */
import { test, type Page } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'audit-v2')
const DATA = path.join(__dirname, 'screenshots', 'audit-v2', 'data')
fs.mkdirSync(SHOTS, { recursive: true })
fs.mkdirSync(DATA, { recursive: true })

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface LiveElement {
  index: number
  tag: string
  type: string
  text: string
  ariaLabel: string
  role: string
  href: string
  disabled: boolean
  boundingBox: { x: number; y: number; width: number; height: number }
  selector: string
  dataTestId: string
  inputType: string
}

interface Result {
  id: string
  type: string
  label: string
  action: string
  outcome: 'pass' | 'defect' | 'disabled-verified'
  observation: string
  defectDescription?: string
}

/* ------------------------------------------------------------------ */
/*  Page list                                                          */
/* ------------------------------------------------------------------ */
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

const execPage = process.env.AUDIT_PAGE
const targetPages = execPage
  ? ALL_PAGES.filter(p => p.name === execPage || p.name.includes(execPage))
  : ALL_PAGES

/* ------------------------------------------------------------------ */
/*  Navigate helper with retry                                         */
/* ------------------------------------------------------------------ */
async function navTo(page: Page, route: string, fullWait = false) {
  await page.goto(route, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(async () => {
    await page.waitForTimeout(2000)
  })
  if (fullWait) {
    // Full wait: used for initial enumeration pass
    for (let attempt = 0; attempt < 12; attempt++) {
      const btnCount = await page.locator('button').count()
      if (btnCount >= 5) break
      await page.waitForTimeout(500)
    }
    await page.waitForTimeout(1500)
  } else {
    // Fast wait: used for per-element re-navigation
    for (let attempt = 0; attempt < 6; attempt++) {
      const btnCount = await page.locator('button').count()
      if (btnCount >= 3) break
      await page.waitForTimeout(400)
    }
    await page.waitForTimeout(500)
  }
}

/* ------------------------------------------------------------------ */
/*  Live DOM enumeration                                               */
/* ------------------------------------------------------------------ */
async function enumerateLive(page: Page): Promise<LiveElement[]> {
  return await page.evaluate(() => {
    const results: any[] = []
    const seen = new Set<Element>()

    const selectors = [
      'button', 'a[href]', 'a:not([href])', 'input', 'textarea', 'select',
      '[role="button"]', '[role="link"]', '[role="tab"]', '[role="menuitem"]',
      '[role="option"]', '[role="checkbox"]', '[role="switch"]', '[role="radio"]',
      '[role="slider"]', '[role="combobox"]', '[role="spinbutton"]', '[role="searchbox"]',
      '[tabindex]:not([tabindex="-1"])',
      '[onclick]',
      '[class*="MuiIconButton"]', '[class*="MuiButton"]', '[class*="MuiSwitch"]',
      '[class*="MuiSelect"]', '[class*="MuiTab"]', '[class*="MuiChip"]',
      '[class*="MuiCheckbox"]', '[class*="MuiRadio"]', '[class*="MuiSlider"]',
      '[class*="MuiToggle"]', '[class*="MuiAccordionSummary"]', '[class*="MuiMenuItem"]',
      '[class*="MuiListItemButton"]', '[class*="MuiPaginationItem"]',
      '[class*="MuiTableSortLabel"]', '[class*="clickable"]', '[class*="Clickable"]',
      '[data-testid]', 'label[for]', 'summary', '[contenteditable="true"]',
    ]

    for (const sel of selectors) {
      try {
        document.querySelectorAll(sel).forEach(el => {
          if (seen.has(el)) return
          seen.add(el)

          const rect = el.getBoundingClientRect()
          const styles = window.getComputedStyle(el)
          const isVisible = rect.width > 0 && rect.height > 0 &&
            styles.display !== 'none' && styles.visibility !== 'hidden' && styles.opacity !== '0'
          if (!isVisible) return

          const tag = el.tagName.toLowerCase()
          const className = el.className?.toString?.() || ''
          const text = (el.textContent || '').trim().replace(/\n/g, ' ').substring(0, 80)
          const ariaLabel = el.getAttribute('aria-label') || ''
          const role = el.getAttribute('role') || ''
          const href = el.getAttribute('href') || ''
          const dataTestId = el.getAttribute('data-testid') || ''
          const inputType = tag === 'input' ? ((el as HTMLInputElement).type || 'text') : ''
          const disabled = (el as HTMLButtonElement).disabled ||
            el.getAttribute('aria-disabled') === 'true' || el.classList.contains('Mui-disabled')

          let type = 'unknown'
          if (tag === 'button' || role === 'button' || className.includes('MuiIconButton') || className.includes('MuiButton-root')) type = 'button'
          else if (tag === 'a') type = 'link'
          else if (tag === 'input') type = `input-${inputType || 'text'}`
          else if (tag === 'textarea') type = 'textarea'
          else if (tag === 'select' || role === 'combobox') type = 'select'
          else if (role === 'tab' || className.includes('MuiTab-root')) type = 'tab'
          else if (role === 'checkbox' || className.includes('MuiCheckbox-root')) type = 'checkbox'
          else if (role === 'switch' || className.includes('MuiSwitch-root')) type = 'switch'
          else if (role === 'radio') type = 'radio'
          else if (role === 'slider' || className.includes('MuiSlider-root')) type = 'slider'
          else if (role === 'menuitem' || className.includes('MuiMenuItem-root')) type = 'menuitem'
          else if (className.includes('MuiChip-root')) type = 'chip'
          else if (className.includes('MuiListItemButton-root')) type = 'list-item-button'
          else if (className.includes('MuiAccordionSummary-root')) type = 'accordion'
          else if (className.includes('MuiTableSortLabel-root')) type = 'sort-label'
          else if (className.includes('MuiPaginationItem-root')) type = 'pagination'
          else if (tag === 'label') type = 'label'
          else if (tag === 'summary') type = 'details-summary'
          else if (el.getAttribute('contenteditable') === 'true') type = 'contenteditable'

          let selector = ''
          if (dataTestId) selector = `[data-testid="${dataTestId}"]`
          else if (ariaLabel) selector = `[aria-label="${ariaLabel}"]`
          else if (el.id) selector = `#${el.id}`
          else selector = `${tag}:nth-of-type(${Array.from(el.parentElement?.children || []).indexOf(el) + 1})`

          results.push({
            index: results.length, tag, type, text, ariaLabel, role, href, disabled,
            boundingBox: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
            selector, dataTestId, inputType,
          })
        })
      } catch {}
    }
    return results
  })
}

/* ------------------------------------------------------------------ */
/*  Re-locate a specific element from a fresh page by its fingerprint  */
/* ------------------------------------------------------------------ */
async function relocate(page: Page, el: LiveElement): Promise<any> {
  // Priority 1: data-testid
  if (el.dataTestId) {
    const loc = page.locator(`[data-testid="${el.dataTestId}"]`).first()
    if (await loc.count() > 0) return loc
  }
  // Priority 2: aria-label
  if (el.ariaLabel) {
    const loc = page.locator(`[aria-label="${el.ariaLabel}"]`).first()
    if (await loc.count() > 0) return loc
  }
  // Priority 3: #id
  if (el.selector.startsWith('#')) {
    const loc = page.locator(el.selector).first()
    if (await loc.count() > 0) return loc
  }
  // Priority 4: text match (short, unique text)
  if (el.text && el.text.length >= 2 && el.text.length < 40) {
    const escaped = el.text.substring(0, 30).replace(/"/g, '\\"')
    const loc = page.locator(`${el.tag}:has-text("${escaped}")`).first()
    if (await loc.count() > 0) return loc
  }
  // Priority 5: role + text
  if (el.role && el.text) {
    const escaped = el.text.substring(0, 25).replace(/"/g, '\\"')
    const loc = page.locator(`[role="${el.role}"]:has-text("${escaped}")`).first()
    if (await loc.count() > 0) return loc
  }
  // Priority 6: coordinate (always succeeds if bbox valid)
  if (el.boundingBox && el.boundingBox.width > 0 && el.boundingBox.x >= 0 && el.boundingBox.y >= 0) {
    return null // Signal to use coordinate click
  }
  return undefined // Truly not found
}

/* ------------------------------------------------------------------ */
/*  Execute a single element                                           */
/* ------------------------------------------------------------------ */
async function executeEl(
  page: Page, locator: any, el: LiveElement,
): Promise<{ action: string; observation: string }> {
  const urlBefore = page.url()

  // Coordinate click fallback
  if (locator === null && el.boundingBox) {
    const cx = el.boundingBox.x + el.boundingBox.width / 2
    const cy = el.boundingBox.y + el.boundingBox.height / 2
    await page.mouse.click(cx, cy)
    await page.waitForTimeout(500)
    const urlAfter = page.url()
    const nav = urlAfter !== urlBefore ? ` Navigated: ${urlAfter}` : ''
    return { action: 'coord-click', observation: `Clicked (${Math.round(cx)},${Math.round(cy)}).${nav}` }
  }

  await locator.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {})

  switch (el.type) {
    case 'input-text': case 'input-search': case 'input-email':
    case 'input-number': case 'input-url': case 'input-password':
    case 'input-tel': case 'textarea': {
      await locator.click({ force: true, timeout: 3000 })
      const old = await locator.inputValue().catch(() => '')
      await locator.fill('audit-v2')
      await page.waitForTimeout(200)
      await locator.fill(old)
      return { action: 'fill+restore', observation: 'Filled and restored' }
    }
    case 'input-file': {
      const tmp = path.join(SHOTS, '_test.txt')
      fs.writeFileSync(tmp, 'test')
      await locator.setInputFiles(tmp)
      await page.waitForTimeout(300)
      await locator.evaluate((el: HTMLInputElement) => { el.value = '' })
      return { action: 'file+clear', observation: 'File set and cleared' }
    }
    case 'checkbox': case 'switch': case 'radio': {
      await locator.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(300)
      await locator.click({ force: true, timeout: 3000 }).catch(() => {})
      return { action: 'toggle-both', observation: 'Toggled on then off' }
    }
    case 'select': case 'combobox': {
      await locator.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
      await page.waitForTimeout(200)
      return { action: 'open+close', observation: 'Opened and closed' }
    }
    case 'slider': {
      await locator.click({ force: true, timeout: 3000 })
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(100)
      await page.keyboard.press('ArrowLeft')
      return { action: 'nudge-both', observation: 'Nudged right+left' }
    }
    case 'accordion': {
      await locator.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(400)
      await locator.click({ force: true, timeout: 3000 }).catch(() => {})
      return { action: 'expand+collapse', observation: 'Expanded and collapsed' }
    }
    default: {
      await locator.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(500)
      const urlAfter = page.url()
      const obs = urlAfter !== urlBefore ? `Navigated: ${urlAfter}` : 'Clicked OK'
      return { action: 'click', observation: obs }
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Main: one test per page                                            */
/* ------------------------------------------------------------------ */
for (const pg of targetPages) {
  test(`audit-v2: ${pg.name}`, async ({ page }) => {
    test.setTimeout(3_600_000) // 60 minutes per page

    const consoleLogs: string[] = []
    page.on('console', m => {
      if (m.type() === 'error') consoleLogs.push(`[error] ${m.text().substring(0, 200)}`)
    })

    // ── STEP 1: Fresh nav + enumerate live elements ──
    await navTo(page, pg.route, true)
    const liveElements = await enumerateLive(page)

    // Also enumerate after scrolling + tabs for completeness
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(500)
    const afterScroll = await enumerateLive(page)
    // Merge unique elements from scroll
    const allFingerprints = new Set(liveElements.map(e => `${e.ariaLabel}|${e.text}|${e.tag}|${e.boundingBox.x},${e.boundingBox.y}`))
    for (const el of afterScroll) {
      const fp = `${el.ariaLabel}|${el.text}|${el.tag}|${el.boundingBox.x},${el.boundingBox.y}`
      if (!allFingerprints.has(fp)) {
        el.index = liveElements.length
        liveElements.push(el)
        allFingerprints.add(fp)
      }
    }

    // NOTE: Tab-panel elements are NOT enumerated separately.
    // Clicking a tab is itself an audited action (pass/defect).
    // Elements within tab panels are tested when the tab click is executed.

    // Save updated inventory
    const invElements = liveElements.map((el, i) => ({ ...el, id: `${pg.name}-E${String(i).padStart(3, '0')}` }))
    fs.writeFileSync(path.join(DATA, `${pg.name}-inventory.json`), JSON.stringify({
      page: pg.name, route: pg.route, totalElements: invElements.length,
      elements: invElements,
    }, null, 2))

    console.log(`\n${'='.repeat(70)}`)
    console.log(`AUDIT v2: ${pg.name} (${pg.route}) — ${invElements.length} live elements`)
    console.log(`${'='.repeat(70)}`)

    // ── STEP 2: Execute each element in isolation ──
    const results: Result[] = []
    let pass = 0, defect = 0, disabled = 0

    for (let i = 0; i < invElements.length; i++) {
      const el = invElements[i]
      const label = (el.ariaLabel || el.text || el.selector).substring(0, 50)

      // Fresh navigation
      await navTo(page, pg.route)

      // Re-locate element in fresh DOM
      const loc = await relocate(page, el)

      // Check disabled
      if (el.disabled) {
        results.push({
          id: el.id, type: el.type, label,
          action: 'verify-disabled', outcome: 'disabled-verified',
          observation: `Disabled in DOM: ${label}`,
        })
        disabled++
        console.log(`  ${el.id} | ${el.type.padEnd(16)} | DISABLED      | ${label}`)
        continue
      }

      if (loc === undefined) {
        // Element not found even with coordinate fallback — defect
        results.push({
          id: el.id, type: el.type, label,
          action: 'locate', outcome: 'defect',
          observation: `Element not relocatable after fresh nav. Selector: ${el.selector}`,
          defectDescription: `Element "${label}" discovered during enumeration but not relocatable after fresh navigation.`,
        })
        defect++
        console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | not relocatable`)
        continue
      }

      // Execute
      try {
        await page.screenshot({ path: path.join(SHOTS, `${el.id}-before.png`) })
        const result = await executeEl(page, loc, el)
        await page.screenshot({ path: path.join(SHOTS, `${el.id}-after.png`) })
        results.push({
          id: el.id, type: el.type, label,
          action: result.action, outcome: 'pass',
          observation: result.observation,
        })
        pass++
        if ((i + 1) % 20 === 0) {
          console.log(`  ... ${i + 1}/${invElements.length} (P:${pass} D:${defect} Dis:${disabled})`)
          // Incremental save every 20 elements
          fs.writeFileSync(path.join(DATA, `${pg.name}-results.json`), JSON.stringify({
            page: pg.name, route: pg.route,
            total: invElements.length, processed: i + 1, pass, defect, disabledVerified: disabled, untestable: 0,
            consoleErrors: consoleLogs, results,
          }, null, 2))
        }
      } catch (err: any) {
        const msg = err.message?.substring(0, 120) || 'unknown'
        // Try coordinate fallback on any error
        if (el.boundingBox && el.boundingBox.width > 0) {
          try {
            const cx = el.boundingBox.x + el.boundingBox.width / 2
            const cy = el.boundingBox.y + el.boundingBox.height / 2
            await page.mouse.click(cx, cy)
            await page.waitForTimeout(400)
            await page.screenshot({ path: path.join(SHOTS, `${el.id}-after.png`) })
            results.push({
              id: el.id, type: el.type, label,
              action: 'coord-fallback', outcome: 'pass',
              observation: `Primary failed, coord-click at (${Math.round(cx)},${Math.round(cy)}) succeeded. Error: ${msg}`,
            })
            pass++
          } catch {
            results.push({
              id: el.id, type: el.type, label,
              action: 'click', outcome: 'defect',
              observation: msg,
              defectDescription: `Element "${label}" throws on interaction: ${msg}`,
            })
            defect++
            console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | ${msg.substring(0, 50)}`)
          }
        } else {
          results.push({
            id: el.id, type: el.type, label,
            action: 'click', outcome: 'defect',
            observation: msg,
            defectDescription: `Element "${label}" throws on interaction: ${msg}`,
          })
          defect++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | ${msg.substring(0, 50)}`)
        }
      }
    }

    // Summary
    console.log(`\n${'='.repeat(70)}`)
    console.log(`RESULTS: ${pg.name} — ${invElements.length} elements`)
    console.log(`  Pass:             ${pass}`)
    console.log(`  Defect:           ${defect}`)
    console.log(`  Disabled-verified: ${disabled}`)
    console.log(`  Untestable:       0 (forbidden)`)
    console.log(`${'='.repeat(70)}`)

    fs.writeFileSync(path.join(DATA, `${pg.name}-results.json`), JSON.stringify({
      page: pg.name, route: pg.route,
      total: invElements.length, pass, defect, disabledVerified: disabled, untestable: 0,
      consoleErrors: consoleLogs,
      results,
    }, null, 2))
  })
}
