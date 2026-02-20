/**
 * Element Enumeration Audit — discovers every actionable element on a given page.
 * Outputs structured inventory: selector, tag, text, role, location, type.
 */
import { test, type Page, type Locator } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOTS = path.join(__dirname, 'screenshots', 'audit')
const DATA = path.join(__dirname, 'screenshots', 'audit', 'data')

// Ensure directories exist
fs.mkdirSync(SHOTS, { recursive: true })
fs.mkdirSync(DATA, { recursive: true })

interface ActionableElement {
  id: string
  index: number
  tag: string
  type: string // button, link, input, select, switch, tab, menuitem, etc.
  text: string
  ariaLabel: string
  role: string
  href: string
  disabled: boolean
  visible: boolean
  boundingBox: { x: number; y: number; width: number; height: number } | null
  selector: string
}

async function enumerateActionableElements(page: Page): Promise<ActionableElement[]> {
  return await page.evaluate(() => {
    const results: any[] = []
    const seen = new Set<Element>()

    // Comprehensive selector list for all actionable elements
    const selectors = [
      'button',
      'a[href]',
      'a:not([href])', // anchor without href but may have onClick
      'input',
      'textarea',
      'select',
      '[role="button"]',
      '[role="link"]',
      '[role="tab"]',
      '[role="menuitem"]',
      '[role="option"]',
      '[role="checkbox"]',
      '[role="switch"]',
      '[role="radio"]',
      '[role="slider"]',
      '[role="combobox"]',
      '[role="spinbutton"]',
      '[role="searchbox"]',
      '[tabindex]',
      '[onclick]',
      '[class*="MuiIconButton"]',
      '[class*="MuiButton"]',
      '[class*="MuiSwitch"]',
      '[class*="MuiSelect"]',
      '[class*="MuiTab"]',
      '[class*="MuiChip"]',
      '[class*="MuiCheckbox"]',
      '[class*="MuiRadio"]',
      '[class*="MuiSlider"]',
      '[class*="MuiToggle"]',
      '[class*="MuiAccordionSummary"]',
      '[class*="MuiMenuItem"]',
      '[class*="MuiListItemButton"]',
      '[class*="MuiPaginationItem"]',
      '[class*="MuiTableSortLabel"]',
      '[class*="clickable"]',
      '[class*="Clickable"]',
      '[data-testid]',
      'label[for]',
      'summary', // <details><summary>
      '[contenteditable="true"]',
    ]

    for (const sel of selectors) {
      try {
        const elements = document.querySelectorAll(sel)
        elements.forEach((el) => {
          if (seen.has(el)) return
          seen.add(el)

          const rect = el.getBoundingClientRect()
          const styles = window.getComputedStyle(el)
          const isVisible =
            rect.width > 0 &&
            rect.height > 0 &&
            styles.display !== 'none' &&
            styles.visibility !== 'hidden' &&
            styles.opacity !== '0'

          // Skip invisible elements deeply nested
          if (!isVisible) return

          const tag = el.tagName.toLowerCase()
          const text = (el.textContent || '').trim().substring(0, 80)
          const ariaLabel = el.getAttribute('aria-label') || ''
          const role = el.getAttribute('role') || ''
          const href = el.getAttribute('href') || ''
          const disabled =
            (el as HTMLButtonElement).disabled ||
            el.getAttribute('aria-disabled') === 'true' ||
            el.classList.contains('Mui-disabled')

          // Determine element type
          let type = 'unknown'
          if (tag === 'button' || role === 'button' || el.classList.contains('MuiIconButton-root') || el.classList.contains('MuiButton-root')) type = 'button'
          else if (tag === 'a') type = 'link'
          else if (tag === 'input') type = `input-${(el as HTMLInputElement).type || 'text'}`
          else if (tag === 'textarea') type = 'textarea'
          else if (tag === 'select' || role === 'combobox') type = 'select'
          else if (role === 'tab' || el.classList.contains('MuiTab-root')) type = 'tab'
          else if (role === 'checkbox' || el.classList.contains('MuiCheckbox-root')) type = 'checkbox'
          else if (role === 'switch' || el.classList.contains('MuiSwitch-root')) type = 'switch'
          else if (role === 'radio') type = 'radio'
          else if (role === 'slider' || el.classList.contains('MuiSlider-root')) type = 'slider'
          else if (role === 'menuitem' || el.classList.contains('MuiMenuItem-root')) type = 'menuitem'
          else if (el.classList.contains('MuiChip-root')) type = 'chip'
          else if (el.classList.contains('MuiListItemButton-root')) type = 'list-item-button'
          else if (el.classList.contains('MuiAccordionSummary-root')) type = 'accordion'
          else if (el.classList.contains('MuiTableSortLabel-root')) type = 'sort-label'
          else if (el.classList.contains('MuiPaginationItem-root')) type = 'pagination'
          else if (tag === 'label') type = 'label'
          else if (tag === 'summary') type = 'details-summary'
          else if (el.getAttribute('contenteditable') === 'true') type = 'contenteditable'

          // Generate a stable selector
          let selector = ''
          const testId = el.getAttribute('data-testid')
          if (testId) {
            selector = `[data-testid="${testId}"]`
          } else if (ariaLabel) {
            selector = `[aria-label="${ariaLabel}"]`
          } else if (el.id) {
            selector = `#${el.id}`
          } else {
            selector = `${tag}:nth-of-type(${Array.from(el.parentElement?.children || []).indexOf(el) + 1})`
          }

          results.push({
            index: results.length,
            tag,
            type,
            text: text.replace(/\n/g, ' ').substring(0, 80),
            ariaLabel,
            role,
            href,
            disabled,
            visible: isVisible,
            boundingBox: {
              x: Math.round(rect.x),
              y: Math.round(rect.y),
              width: Math.round(rect.width),
              height: Math.round(rect.height),
            },
            selector,
          })
        })
      } catch (e) {
        // Ignore invalid selector errors
      }
    }

    return results
  })
}

// Page routes to audit — run all in sequence
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

// Filter to specific page if env var set, else first page only for targeted runs
const pageFilter = process.env.AUDIT_NAME
const PAGES_TO_AUDIT = pageFilter
  ? ALL_PAGES.filter(p => p.name === pageFilter)
  : ALL_PAGES

for (const pg of PAGES_TO_AUDIT) {
  test(`Enumerate actionable elements on ${pg.name}`, async ({ page }) => {
    await page.goto(pg.route, { waitUntil: 'domcontentloaded', timeout: 20000 })
    await page.waitForTimeout(3000)

    // Take full-page screenshot
    await page.screenshot({ path: path.join(SHOTS, `${pg.name}-overview.png`), fullPage: true })

    // Enumerate all actionable elements
    const elements = await enumerateActionableElements(page)

    // Add IDs
    elements.forEach((el: any, i: number) => {
      el.id = `${pg.name}-E${String(i).padStart(3, '0')}`
    })

    // Summary by type
    const byType: Record<string, number> = {}
    elements.forEach((el: any) => {
      byType[el.type] = (byType[el.type] || 0) + 1
    })

    console.log(`\n${'='.repeat(70)}`)
    console.log(`PAGE: ${pg.name} (${pg.route})`)
    console.log(`TOTAL ACTIONABLE ELEMENTS: ${elements.length}`)
    console.log(`${'='.repeat(70)}`)
    console.log(`\nBREAKDOWN BY TYPE:`)
    Object.entries(byType)
      .sort((a, b) => b[1] - a[1])
      .forEach(([type, count]) => {
        console.log(`  ${type.padEnd(20)} ${count}`)
      })

    console.log(`\nFULL INVENTORY:`)
    elements.forEach((el: any) => {
      const disabled = el.disabled ? ' [DISABLED]' : ''
      const label = el.ariaLabel || el.text.substring(0, 40) || el.selector
      console.log(`  ${el.id} | ${el.type.padEnd(18)} | ${label.substring(0, 45).padEnd(45)} | ${el.tag}${disabled}`)
    })

    // Save to JSON
    const outPath = path.join(DATA, `${pg.name}-inventory.json`)
    fs.writeFileSync(outPath, JSON.stringify({ page: pg.name, route: pg.route, totalElements: elements.length, byType, elements }, null, 2))
    console.log(`\nInventory saved to: ${outPath}`)
  })
}
