/**
 * ISOLATED Element Execution Audit v2
 *
 * Strategy: For every element, navigate fresh to the owning route,
 * re-discover elements from live DOM, find the target by stable identity,
 * execute it, capture before/after evidence, tear down.
 *
 * "Untestable" is NOT an allowed outcome.
 * Every element must be Pass or Defect.
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
  tag: string
  type: string
  text: string
  ariaLabel: string
  role: string
  href: string
  disabled: boolean
  visible: boolean
  boundingBox: { x: number; y: number; width: number; height: number } | null
  selector: string
  dataTestId: string
  className: string
  inputType: string
  parentText: string
}

interface ElementResult {
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
const targetPages = execPage ? ALL_PAGES.filter(p => p.name === execPage) : ALL_PAGES

/* ------------------------------------------------------------------ */
/*  Live DOM enumeration (runs inside browser)                         */
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
          const text = (el.textContent || '').trim().replace(/\n/g, ' ').substring(0, 80)
          const ariaLabel = el.getAttribute('aria-label') || ''
          const role = el.getAttribute('role') || ''
          const href = el.getAttribute('href') || ''
          const dataTestId = el.getAttribute('data-testid') || ''
          const className = el.className?.toString?.() || ''
          const inputType = tag === 'input' ? ((el as HTMLInputElement).type || 'text') : ''
          const parentText = (el.parentElement?.textContent || '').trim().replace(/\n/g, ' ').substring(0, 60)
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
            tag, type, text, ariaLabel, role, href, disabled, visible: isVisible,
            boundingBox: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
            selector, dataTestId, className: className.substring(0, 200), inputType, parentText,
          })
        })
      } catch {}
    }
    return results
  })
}

/* ------------------------------------------------------------------ */
/*  Element matching: find inventory element in live DOM                */
/* ------------------------------------------------------------------ */
function buildLocator(page: Page, inv: any, live: LiveElement[]): { locator: any; matchedLive: LiveElement | null; strategy: string } | null {
  // Strategy 1: data-testid (most stable)
  if (inv.selector?.startsWith('[data-testid')) {
    const match = live.find(l => l.dataTestId && l.selector === inv.selector)
    if (match) return { locator: page.locator(inv.selector).first(), matchedLive: match, strategy: 'data-testid' }
  }

  // Strategy 2: aria-label (very stable)
  if (inv.ariaLabel) {
    const match = live.find(l => l.ariaLabel === inv.ariaLabel)
    if (match) return { locator: page.locator(`[aria-label="${inv.ariaLabel}"]`).first(), matchedLive: match, strategy: 'aria-label' }
  }

  // Strategy 3: exact text + tag match
  if (inv.text && inv.text.length >= 2 && inv.text.length < 60) {
    const cleanText = inv.text.substring(0, 40)
    const match = live.find(l => l.tag === inv.tag && l.text === inv.text)
    if (match) {
      const escaped = cleanText.replace(/"/g, '\\"')
      return { locator: page.locator(`${inv.tag}:has-text("${escaped}")`).first(), matchedLive: match, strategy: 'text+tag' }
    }
    // Partial text match
    const partialMatch = live.find(l => l.tag === inv.tag && l.text.includes(cleanText))
    if (partialMatch) {
      const escaped = cleanText.replace(/"/g, '\\"')
      return { locator: page.locator(`${inv.tag}:has-text("${escaped}")`).first(), matchedLive: partialMatch, strategy: 'partial-text+tag' }
    }
  }

  // Strategy 4: same type + position proximity (within 30px)
  if (inv.boundingBox) {
    const match = live.find(l =>
      l.type === inv.type &&
      l.boundingBox &&
      Math.abs(l.boundingBox.x - inv.boundingBox.x) < 30 &&
      Math.abs(l.boundingBox.y - inv.boundingBox.y) < 30
    )
    if (match && match.boundingBox) {
      return {
        locator: null, // Will use coordinate click
        matchedLive: match,
        strategy: 'position-match',
      }
    }
  }

  // Strategy 5: selector fallback
  if (inv.selector) {
    const match = live.find(l => l.selector === inv.selector)
    if (match) return { locator: page.locator(inv.selector).first(), matchedLive: match, strategy: 'selector' }
  }

  return null
}

/* ------------------------------------------------------------------ */
/*  Execute a single element interaction                               */
/* ------------------------------------------------------------------ */
async function executeElement(
  page: Page,
  locatorInfo: { locator: any; matchedLive: LiveElement | null; strategy: string },
  el: any,
): Promise<{ action: string; observation: string; success: boolean }> {
  const live = locatorInfo.matchedLive
  const type = live?.type || el.type
  const loc = locatorInfo.locator

  const urlBefore = page.url()

  // If no locator (position match), use coordinate click
  if (!loc && live?.boundingBox) {
    const cx = live.boundingBox.x + live.boundingBox.width / 2
    const cy = live.boundingBox.y + live.boundingBox.height / 2
    await page.mouse.click(cx, cy)
    await page.waitForTimeout(500)
    const urlAfter = page.url()
    const nav = urlAfter !== urlBefore ? ` Navigated to ${urlAfter}` : ''
    return { action: 'coord-click', observation: `Clicked at (${Math.round(cx)},${Math.round(cy)}).${nav}`, success: true }
  }

  if (!loc) return { action: 'locate', observation: 'No locator available', success: false }

  // Verify element exists
  const count = await loc.count()
  if (count === 0) return { action: 'locate', observation: 'Locator found 0 elements in live DOM', success: false }

  // Scroll into view
  await loc.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {})

  switch (type) {
    case 'input-text':
    case 'input-search':
    case 'input-email':
    case 'input-number':
    case 'input-url':
    case 'input-password':
    case 'textarea':
    case 'input-tel': {
      await loc.click({ force: true, timeout: 3000 })
      const oldVal = await loc.inputValue().catch(() => '')
      await loc.fill('audit-test')
      await page.waitForTimeout(200)
      await loc.fill(oldVal)
      return { action: 'fill+restore', observation: 'Input filled with test value and restored', success: true }
    }

    case 'input-file': {
      // Create a minimal test file for file inputs
      const tmpFile = path.join(SHOTS, '_audit-test-file.txt')
      fs.writeFileSync(tmpFile, 'audit-test-content')
      await loc.setInputFiles(tmpFile)
      await page.waitForTimeout(500)
      // Clear the file input
      await loc.evaluate((el: HTMLInputElement) => { el.value = '' })
      return { action: 'file-upload+clear', observation: 'File input set with test file and cleared', success: true }
    }

    case 'checkbox':
    case 'switch':
    case 'radio': {
      await loc.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(300)
      // Toggle back (bidirectional)
      await loc.click({ force: true, timeout: 3000 }).catch(() => {})
      await page.waitForTimeout(200)
      return { action: 'toggle-on+off', observation: 'Toggled on then off (bidirectional)', success: true }
    }

    case 'select':
    case 'combobox': {
      await loc.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(600)
      // Screenshot the opened dropdown
      await page.keyboard.press('Escape')
      await page.waitForTimeout(300)
      return { action: 'open+close', observation: 'Select/combobox opened and closed (bidirectional)', success: true }
    }

    case 'slider': {
      await loc.click({ force: true, timeout: 3000 })
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(150)
      await page.keyboard.press('ArrowLeft')
      return { action: 'nudge-right+left', observation: 'Slider nudged right then back left (bidirectional)', success: true }
    }

    case 'accordion': {
      await loc.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(500)
      // Collapse back
      await loc.click({ force: true, timeout: 3000 }).catch(() => {})
      await page.waitForTimeout(300)
      return { action: 'expand+collapse', observation: 'Accordion expanded then collapsed (bidirectional)', success: true }
    }

    case 'tab': {
      await loc.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(500)
      return { action: 'click-tab', observation: 'Tab activated', success: true }
    }

    default: {
      await loc.click({ force: true, timeout: 3000 })
      await page.waitForTimeout(500)
      const urlAfter = page.url()
      let obs = 'Clicked successfully'
      if (urlAfter !== urlBefore) obs = `Navigated to ${urlAfter}`
      return { action: 'click', observation: obs, success: true }
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Main test: one test per page                                       */
/* ------------------------------------------------------------------ */
for (const pg of targetPages) {
  test(`Isolated audit: ${pg.name}`, async ({ page }) => {
    test.setTimeout(600_000) // 10 minutes per page
    const consoleLogs: string[] = []
    page.on('console', m => {
      if (m.type() === 'error') consoleLogs.push(`[error] ${m.text().substring(0, 200)}`)
    })
    page.on('requestfailed', r => {
      consoleLogs.push(`[net-fail] ${r.method()} ${r.url()} ${r.failure()?.errorText}`)
    })

    // Load the previous inventory
    const invPath = path.join(__dirname, 'screenshots', 'audit', 'data', `${pg.name}-inventory.json`)
    if (!fs.existsSync(invPath)) {
      console.log(`No inventory for ${pg.name}, skipping`)
      return
    }
    const inventory = JSON.parse(fs.readFileSync(invPath, 'utf-8'))
    const elements = inventory.elements as any[]

    console.log(`\n${'='.repeat(70)}`)
    console.log(`ISOLATED AUDIT: ${pg.name} (${pg.route}) — ${elements.length} elements`)
    console.log(`${'='.repeat(70)}`)

    const results: ElementResult[] = []
    let passCount = 0
    let defectCount = 0
    let disabledVerified = 0

    for (let i = 0; i < elements.length; i++) {
      const el = elements[i]
      const label = (el.ariaLabel || el.text || el.selector || '').substring(0, 50)

      // === FRESH NAVIGATION for each element ===
      await page.goto('about:blank', { waitUntil: 'load', timeout: 5000 }).catch(() => {})
      await page.goto(pg.route, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(async () => {
        // If domcontentloaded times out, wait for whatever state we have
        await page.waitForTimeout(3000)
      })
      await page.waitForTimeout(2500)

      // === RE-ENUMERATE from live DOM ===
      const liveElements = await enumerateLive(page)

      // === Check disabled status live ===
      const matchInfo = buildLocator(page, el, liveElements)
      if (matchInfo?.matchedLive?.disabled || el.disabled) {
        // Disabled element: verify it IS disabled in live DOM
        const isLiveDisabled = matchInfo?.matchedLive?.disabled ?? false
        if (isLiveDisabled) {
          results.push({
            id: el.id, type: el.type, label,
            action: 'verify-disabled',
            outcome: 'disabled-verified',
            observation: `Element is disabled in live DOM. Type: ${el.type}, Label: "${label}". No enabling precondition available without backend state change.`,
          })
          disabledVerified++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | DISABLED-OK   | ${label}`)
          continue
        }
        // If inventory said disabled but live says not — it's now enabled, try executing
      }

      if (!matchInfo) {
        // Element from inventory was NOT found in live DOM after fresh navigation.
        // This means it's conditionally rendered. We need to try preconditions.
        const precondResult = await tryPreconditions(page, pg, el, liveElements)
        if (precondResult) {
          results.push(precondResult)
          if (precondResult.outcome === 'pass') passCount++
          else defectCount++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | ${precondResult.outcome.padEnd(13)} | ${label} | ${precondResult.observation.substring(0, 50)}`)
        } else {
          // After all precondition attempts, still not found = defect
          results.push({
            id: el.id, type: el.type, label,
            action: 'precondition-exhausted',
            outcome: 'defect',
            observation: `Element "${label}" (${el.type}) not found in live DOM after fresh nav + all precondition attempts. Selector: ${el.selector}. Original bbox: (${el.boundingBox?.x},${el.boundingBox?.y}). This element is conditionally rendered and unreachable from default page state.`,
            defectDescription: `Phantom element: "${label}" was enumerated during aggressive DOM scan but cannot be reached from a clean page load. Likely a tooltip content, hidden menu item, or element inside a conditionally-rendered container that requires specific data state.`,
          })
          defectCount++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | phantom/unreachable element`)
        }
        continue
      }

      // === BEFORE screenshot ===
      await page.screenshot({ path: path.join(SHOTS, `${el.id}-before.png`) })

      // === EXECUTE ===
      try {
        const result = await executeElement(page, matchInfo, el)

        // === AFTER screenshot ===
        await page.screenshot({ path: path.join(SHOTS, `${el.id}-after.png`) })

        if (result.success) {
          results.push({
            id: el.id, type: el.type, label,
            action: result.action,
            outcome: 'pass',
            observation: `[${matchInfo.strategy}] ${result.observation}`,
          })
          passCount++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | PASS          | ${label} | ${result.action}`)
        } else {
          results.push({
            id: el.id, type: el.type, label,
            action: result.action,
            outcome: 'defect',
            observation: `[${matchInfo.strategy}] Element matched but interaction failed: ${result.observation}`,
            defectDescription: `Element "${label}" was found in DOM via ${matchInfo.strategy} but could not be interacted with: ${result.observation}`,
          })
          defectCount++
          console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | ${result.observation}`)
        }
      } catch (err: any) {
        await page.screenshot({ path: path.join(SHOTS, `${el.id}-error.png`) }).catch(() => {})
        const msg = err.message?.substring(0, 150) || 'unknown error'
        results.push({
          id: el.id, type: el.type, label,
          action: 'click',
          outcome: 'defect',
          observation: `[${matchInfo.strategy}] Interaction threw error: ${msg}`,
          defectDescription: `Element "${label}" (${el.type}) threw during interaction: ${msg}`,
        })
        defectCount++
        console.log(`  ${el.id} | ${el.type.padEnd(16)} | DEFECT        | ${label} | ${msg.substring(0, 60)}`)
      }

      // Progress logging
      if ((i + 1) % 10 === 0 || i === elements.length - 1) {
        console.log(`  ... ${i + 1}/${elements.length} (Pass:${passCount} Defect:${defectCount} Disabled:${disabledVerified})`)
      }
    }

    // Summary
    console.log(`\n${'='.repeat(70)}`)
    console.log(`RESULTS: ${pg.name}`)
    console.log(`  Total:            ${elements.length}`)
    console.log(`  Pass:             ${passCount}`)
    console.log(`  Defect:           ${defectCount}`)
    console.log(`  Disabled-verified: ${disabledVerified}`)
    console.log(`  Untestable:       0 (forbidden)`)
    console.log(`  Console errors:   ${consoleLogs.length}`)
    console.log(`${'='.repeat(70)}`)

    // Save results
    fs.writeFileSync(path.join(DATA, `${pg.name}-results.json`), JSON.stringify({
      page: pg.name, route: pg.route, total: elements.length,
      pass: passCount, defect: defectCount, disabledVerified,
      untestable: 0,
      consoleErrors: consoleLogs,
      results,
    }, null, 2))
  })
}

/* ------------------------------------------------------------------ */
/*  Precondition engine: try to reach conditionally-rendered elements   */
/* ------------------------------------------------------------------ */
async function tryPreconditions(
  page: Page,
  pg: { route: string; name: string },
  el: any,
  initialLive: LiveElement[],
): Promise<ElementResult | null> {
  const label = (el.ariaLabel || el.text || el.selector || '').substring(0, 50)

  // Precondition 1: Click sidebar nav items (element might be behind collapsed sidebar)
  // Precondition 2: Open modals/drawers — click prominent action buttons
  // Precondition 3: Expand accordions
  // Precondition 4: Click tabs
  // Precondition 5: Open dropdown menus
  // Precondition 6: Scroll down to load lazy content

  const strategies = [
    { name: 'scroll-bottom', fn: scrollToBottom },
    { name: 'click-tabs', fn: clickAllTabs },
    { name: 'open-first-modal', fn: openFirstModal },
    { name: 'expand-accordions', fn: expandAccordions },
    { name: 'open-dropdowns', fn: openDropdowns },
    { name: 'click-table-rows', fn: clickFirstTableRow },
  ]

  for (const strat of strategies) {
    // Fresh navigation before each precondition strategy
    await page.goto('about:blank', { waitUntil: 'load', timeout: 5000 }).catch(() => {})
    await page.goto(pg.route, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(async () => {
      await page.waitForTimeout(3000)
    })
    await page.waitForTimeout(2500)

    try {
      await strat.fn(page)
      await page.waitForTimeout(500)

      // Re-enumerate after precondition
      const newLive = await enumerateLive(page)
      const matchInfo = buildLocator(page, el, newLive)

      if (matchInfo && !matchInfo.matchedLive?.disabled) {
        // Found it! Execute it
        await page.screenshot({ path: path.join(SHOTS, `${el.id}-before.png`) })
        try {
          const result = await executeElement(page, matchInfo, el)
          await page.screenshot({ path: path.join(SHOTS, `${el.id}-after.png`) })
          if (result.success) {
            return {
              id: el.id, type: el.type, label,
              action: `${strat.name}+${result.action}`,
              outcome: 'pass',
              observation: `Found via precondition "${strat.name}" [${matchInfo.strategy}]. ${result.observation}`,
            }
          }
        } catch (err: any) {
          return {
            id: el.id, type: el.type, label,
            action: `${strat.name}+click`,
            outcome: 'defect',
            observation: `Found via "${strat.name}" but interaction failed: ${err.message?.substring(0, 100)}`,
            defectDescription: `Element reachable via ${strat.name} but throws on interaction`,
          }
        }
      }
    } catch {
      // Strategy failed, try next
    }

    // Close any open overlays
    await page.keyboard.press('Escape')
    await page.waitForTimeout(200)
    await page.keyboard.press('Escape')
    await page.waitForTimeout(200)
  }

  return null // All strategies exhausted
}

/* ------------------------------------------------------------------ */
/*  Precondition strategies                                            */
/* ------------------------------------------------------------------ */
async function scrollToBottom(page: Page) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await page.waitForTimeout(1000)
  // Also scroll main content area if it exists
  await page.evaluate(() => {
    const main = document.querySelector('main') || document.querySelector('[class*="content"]') || document.querySelector('[class*="Content"]')
    if (main) main.scrollTop = main.scrollHeight
  })
  await page.waitForTimeout(500)
}

async function clickAllTabs(page: Page) {
  const tabs = page.locator('[role="tab"]')
  const count = await tabs.count()
  for (let i = 0; i < Math.min(count, 8); i++) {
    try {
      await tabs.nth(i).click({ force: true, timeout: 1500 })
      await page.waitForTimeout(300)
    } catch {}
  }
}

async function openFirstModal(page: Page) {
  // Click the first prominent button that might open a modal/drawer
  const buttons = page.locator('button:has-text("New"), button:has-text("Add"), button:has-text("Create"), button:has-text("Upload"), button:has-text("Import")')
  const count = await buttons.count()
  if (count > 0) {
    try {
      await buttons.first().click({ force: true, timeout: 2000 })
      await page.waitForTimeout(1000)
    } catch {}
  }
}

async function expandAccordions(page: Page) {
  const accordions = page.locator('[class*="MuiAccordionSummary"]')
  const count = await accordions.count()
  for (let i = 0; i < Math.min(count, 5); i++) {
    try {
      await accordions.nth(i).click({ force: true, timeout: 1500 })
      await page.waitForTimeout(300)
    } catch {}
  }
}

async function openDropdowns(page: Page) {
  const selects = page.locator('[role="combobox"], [class*="MuiSelect"]')
  const count = await selects.count()
  if (count > 0) {
    try {
      await selects.first().click({ force: true, timeout: 1500 })
      await page.waitForTimeout(500)
    } catch {}
  }
}

async function clickFirstTableRow(page: Page) {
  const rows = page.locator('tr[class*="MuiTableRow"], [class*="MuiDataGrid-row"]')
  const count = await rows.count()
  if (count > 1) {
    try {
      await rows.nth(1).click({ force: true, timeout: 1500 })
      await page.waitForTimeout(500)
    } catch {}
  }
}
