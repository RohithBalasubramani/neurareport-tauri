/**
 * Phases 3-8: Deep Interaction for ALL remaining pages.
 * Each test exercises buttons, forms, dropdowns, toggles, and captures before/after screenshots.
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
  page.on('console', m => {
    if (m.type() === 'error' || m.type() === 'warning')
      consoleLogs.push(`[${m.type()}] ${m.text().substring(0, 200)}`)
  })
  page.on('requestfailed', r => {
    netErrors.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`)
  })
})

async function safeClick(loc: ReturnType<Page['locator']>, timeout = 3000) {
  try { await loc.click({ timeout }) } catch { await loc.click({ force: true }) }
}

async function snap(page: Page, name: string, fullPage = false) {
  await page.screenshot({ path: path.join(SHOTS, `${name}.png`), fullPage })
}

async function logInteractive(page: Page, label: string) {
  const btns = await page.locator('button:visible').count()
  const inputs = await page.locator('input:visible, textarea:visible').count()
  const selects = await page.locator('select:visible, [role="combobox"]:visible').count()
  const switches = await page.locator('[role="checkbox"]:visible, [class*="Switch"]:visible').count()
  console.log(`  [${label}] buttons=${btns} inputs=${inputs} selects=${selects} switches=${switches}`)
}

// ═══════════════════════════════════════════════════
// PHASE 3: Reports + Jobs + Schedules
// ═══════════════════════════════════════════════════
test('P3: Reports page interactions', async ({ page }) => {
  await page.goto('/reports', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p3-reports-01-init', true)
  await logInteractive(page, 'Reports')

  // Time period chips
  const chips = ['Today', 'This Week', 'This Month', 'Last Month', 'Custom']
  for (const chip of chips) {
    const el = page.locator(`text="${chip}"`).first()
    if (await el.count()) {
      await el.click({ force: true })
      await page.waitForTimeout(500)
      console.log(`  Clicked chip: ${chip}`)
    }
  }
  await snap(page, 'p3-reports-02-chips')

  // Find Batches button
  const findBatch = page.getByRole('button', { name: /Find Batches/i }).first()
  if (await findBatch.count()) {
    console.log('  Clicking Find Batches')
    await snap(page, 'p3-reports-03-before-find')
    await safeClick(findBatch)
    await page.waitForTimeout(2000)
    await snap(page, 'p3-reports-04-after-find', true)
  }

  // Generate Report button (may be disabled)
  const genBtn = page.getByRole('button', { name: /Generate Report/i }).first()
  if (await genBtn.count()) {
    const disabled = await genBtn.isDisabled()
    console.log(`  Generate Report button: disabled=${disabled}`)
    await snap(page, 'p3-reports-05-generate-btn')
  }

  // Schedule button
  const schedBtn = page.getByRole('button', { name: /Schedule/i }).first()
  if (await schedBtn.count()) {
    console.log('  Schedule button visible')
  }

  // View Progress link
  const viewProg = page.locator('text="View Progress"').first()
  if (await viewProg.count()) {
    console.log('  View Progress link visible')
  }

  console.log(`Reports errors: ${consoleLogs.length}`)
})

test('P3: Jobs page interactions', async ({ page }) => {
  await page.goto('/jobs', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p3-jobs-01-init', true)
  await logInteractive(page, 'Jobs')

  // Refresh button
  const refresh = page.getByRole('button', { name: /Refresh/i }).first()
  if (await refresh.count()) {
    console.log('  Clicking Refresh')
    await safeClick(refresh)
    await page.waitForTimeout(1500)
    await snap(page, 'p3-jobs-02-refreshed')
  }

  // Filters
  const filtersBtn = page.getByRole('button', { name: /Filters/i }).first()
  if (await filtersBtn.count()) {
    await safeClick(filtersBtn)
    await page.waitForTimeout(1000)
    await snap(page, 'p3-jobs-03-filters')
    await page.keyboard.press('Escape')
  }

  // Click a job row
  const rows = page.locator('table tbody tr, [role="row"]').filter({ hasText: /Run_report|Completed|Failed/ })
  if (await rows.count() > 0) {
    console.log('  Clicking first job row')
    await rows.first().click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p3-jobs-04-row-detail', true)
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // Kebab menu
  const kebab = page.locator('[data-testid*="MoreVert"], [aria-label="more"]').first()
  if (await kebab.count()) {
    await kebab.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p3-jobs-05-kebab')
    // List menu items
    const items = page.locator('[role="menuitem"]')
    for (let i = 0; i < await items.count(); i++) {
      console.log(`    Menu: ${await items.nth(i).textContent()}`)
    }
    await page.keyboard.press('Escape')
  }

  // Pagination
  const nextPage = page.locator('[aria-label="Go to next page"]').first()
  if (await nextPage.count()) {
    const disabled = await nextPage.isDisabled()
    console.log(`  Next page button: disabled=${disabled}`)
    if (!disabled) {
      await nextPage.click({ force: true })
      await page.waitForTimeout(1500)
      await snap(page, 'p3-jobs-06-page2', true)
    }
  }
})

test('P3: Schedules page interactions', async ({ page }) => {
  await page.goto('/schedules', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p3-sched-01-init', true)
  await logInteractive(page, 'Schedules')

  // Create Schedule button
  const createBtn = page.getByRole('button', { name: /Create Schedule/i }).first()
  if (await createBtn.count()) {
    console.log('  Clicking Create Schedule')
    await safeClick(createBtn)
    await page.waitForTimeout(2000)
    await snap(page, 'p3-sched-02-create-dialog', true)
    // Check for dialog/form inputs
    const dialogInputs = page.locator('[role="dialog"] input, [class*="Dialog"] input, form input')
    console.log(`  Dialog inputs: ${await dialogInputs.count()}`)
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // Empty state visible
  const emptyState = page.locator('text=/No schedules yet/i')
  if (await emptyState.count()) {
    console.log('  Empty state displayed correctly')
  }
})

// ═══════════════════════════════════════════════════
// PHASE 4: Query + Documents + Spreadsheets
// ═══════════════════════════════════════════════════
test('P4: Query Builder interactions', async ({ page }) => {
  await page.goto('/query', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p4-query-01-init', true)
  await logInteractive(page, 'Query')

  // Connection dropdown
  const connSelect = page.locator('[role="combobox"], select').first()
  if (await connSelect.count()) {
    console.log('  Clicking connection dropdown')
    await connSelect.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p4-query-02-conn-dropdown')
    await page.keyboard.press('Escape')
  }

  // NL input field
  const nlInput = page.locator('textarea, input[placeholder*="question"], input[placeholder*="Show me"]').first()
  if (await nlInput.count()) {
    console.log('  Typing NL query')
    await nlInput.click({ force: true })
    await nlInput.fill('Show me all customers who made purchases last month')
    await page.waitForTimeout(500)
    await snap(page, 'p4-query-03-nl-typed')
  }

  // Generate SQL button
  const genSql = page.getByRole('button', { name: /Generate SQL/i }).first()
  if (await genSql.count()) {
    const disabled = await genSql.isDisabled()
    console.log(`  Generate SQL: disabled=${disabled}`)
    await snap(page, 'p4-query-04-gen-btn')
  }

  // Saved / History tabs
  const saved = page.locator('text="Saved"').first()
  if (await saved.count()) {
    await saved.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p4-query-05-saved-tab')
  }
  const history = page.locator('text="History"').first()
  if (await history.count()) {
    await history.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p4-query-06-history-tab')
  }
})

test('P4: Documents interactions', async ({ page }) => {
  await page.goto('/documents', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p4-docs-01-init', true)
  await logInteractive(page, 'Documents')

  // New Document button
  const newDoc = page.getByRole('button', { name: /New Document|Create Document/i }).first()
  if (await newDoc.count()) {
    console.log('  Clicking New Document')
    await safeClick(newDoc)
    await page.waitForTimeout(2000)
    await snap(page, 'p4-docs-02-new-doc', true)
    console.log(`  URL: ${page.url()}`)
    // Go back
    await page.goto('/documents', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // Empty state check
  const empty = page.locator('text=/No Document Selected/i')
  if (await empty.count()) {
    console.log('  Empty state: "No Document Selected"')
  }
})

test('P4: Spreadsheets interactions', async ({ page }) => {
  await page.goto('/spreadsheets', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p4-spread-01-init', true)
  await logInteractive(page, 'Spreadsheets')

  // Create Spreadsheet button
  const createBtn = page.getByRole('button', { name: /Create Spreadsheet/i }).first()
  if (await createBtn.count()) {
    console.log('  Clicking Create Spreadsheet')
    await safeClick(createBtn)
    await page.waitForTimeout(2000)
    await snap(page, 'p4-spread-02-created', true)
    console.log(`  URL: ${page.url()}`)
  }

  // Import File button
  const importBtn = page.getByRole('button', { name: /Import File/i }).first()
  if (await importBtn.count()) {
    console.log('  Import File button visible')
  }

  // Empty state
  const empty = page.locator('text=/No Spreadsheet Selected/i')
  if (await empty.count()) {
    console.log('  Empty state visible')
  }
})

// ═══════════════════════════════════════════════════
// PHASE 5: Enrichment + Federation + Synthesis + DocQA
// ═══════════════════════════════════════════════════
test('P5: Enrichment interactions', async ({ page }) => {
  await page.goto('/enrichment', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p5-enrich-01-init', true)
  await logInteractive(page, 'Enrichment')

  // Tabs
  const cacheTab = page.locator('text="Cache Admin"').first()
  if (await cacheTab.count()) {
    await cacheTab.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p5-enrich-02-cache-tab', true)
  }

  // Data input textarea
  const dataInput = page.locator('textarea').first()
  if (await dataInput.count()) {
    await page.locator('text="Enrich Data"').first().click({ force: true }).catch(() => {})
    await page.waitForTimeout(500)
    await dataInput.click({ force: true })
    await dataInput.fill('[{"name": "Acme Corp", "address": "123 Main St"}]')
    await page.waitForTimeout(500)
    await snap(page, 'p5-enrich-03-data-filled')
  }

  // Preview + Enrich All buttons
  const preview = page.getByRole('button', { name: /Preview/i }).first()
  if (await preview.count()) {
    const disabled = await preview.isDisabled()
    console.log(`  Preview: disabled=${disabled}`)
  }
  const enrichAll = page.getByRole('button', { name: /Enrich All/i }).first()
  if (await enrichAll.count()) {
    const disabled = await enrichAll.isDisabled()
    console.log(`  Enrich All: disabled=${disabled}`)
  }

  // Add Custom Source
  const addSrc = page.getByRole('button', { name: /Add Custom Source/i }).first()
  if (await addSrc.count()) {
    console.log('  Clicking Add Custom Source')
    await safeClick(addSrc)
    await page.waitForTimeout(1500)
    await snap(page, 'p5-enrich-04-custom-source')
    await page.keyboard.press('Escape')
  }
})

test('P5: Federation interactions', async ({ page }) => {
  await page.goto('/federation', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p5-fed-01-init', true)
  await logInteractive(page, 'Federation')

  // New Virtual Schema button
  const newSchema = page.getByRole('button', { name: /New Virtual Schema/i }).first()
  if (await newSchema.count()) {
    console.log('  Clicking New Virtual Schema')
    await safeClick(newSchema)
    await page.waitForTimeout(2000)
    await snap(page, 'p5-fed-02-new-schema', true)
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  }

  // Click existing "Test Schema"
  const testSchema = page.locator('text="Test Schema"').first()
  if (await testSchema.count()) {
    console.log('  Clicking Test Schema')
    await testSchema.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p5-fed-03-schema-detail', true)
  }

  // Delete button (trash icon)
  const deleteBtn = page.locator('[aria-label*="delete"], [data-testid*="Delete"]').first()
  if (await deleteBtn.count()) {
    console.log('  Delete button visible')
  }
})

test('P5: Synthesis interactions', async ({ page }) => {
  await page.goto('/synthesis', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p5-synth-01-init', true)
  await logInteractive(page, 'Synthesis')

  // New Session button
  const newSession = page.getByRole('button', { name: /New Session/i }).first()
  if (await newSession.count()) {
    console.log('  Clicking New Session')
    await safeClick(newSession)
    await page.waitForTimeout(2000)
    await snap(page, 'p5-synth-02-new-session', true)
  }

  // Click existing Test Session
  const testSession = page.locator('text="Test Session"').first()
  if (await testSession.count()) {
    console.log('  Clicking Test Session')
    await testSession.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p5-synth-03-session-detail', true)
  }
})

test('P5: DocQA interactions', async ({ page }) => {
  await page.goto('/docqa', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p5-docqa-01-init', true)
  await logInteractive(page, 'DocQA')

  // Create Your First Session
  const createBtn = page.getByRole('button', { name: /Create.*Session/i }).first()
  if (await createBtn.count()) {
    console.log('  Clicking Create Session')
    await safeClick(createBtn)
    await page.waitForTimeout(2000)
    await snap(page, 'p5-docqa-02-session-created', true)
  }

  // Session list items (trash icons visible in sidebar)
  const sessions = page.locator('[data-testid*="delete"], [aria-label*="delete"]')
  console.log(`  Session delete buttons: ${await sessions.count()}`)
})

// ═══════════════════════════════════════════════════
// PHASE 6: Workflows + Dashboard Builder + Knowledge
// ═══════════════════════════════════════════════════
test('P6: Workflows interactions', async ({ page }) => {
  await page.goto('/workflows', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p6-wf-01-init', true)
  await logInteractive(page, 'Workflows')

  // New Workflow button
  const newWf = page.getByRole('button', { name: /New Workflow/i }).first()
  if (await newWf.count()) {
    console.log('  Clicking New Workflow')
    await safeClick(newWf)
    await page.waitForTimeout(2000)
    await snap(page, 'p6-wf-02-new-workflow', true)
    await page.goto('/workflows', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // Create Workflow CTA
  const createWf = page.getByRole('button', { name: /Create Workflow/i }).first()
  if (await createWf.count()) {
    console.log('  Create Workflow CTA visible')
  }

  // Click an existing workflow
  const wfItem = page.locator('text="test"').first()
  if (await wfItem.count()) {
    console.log('  Clicking existing workflow "test"')
    await wfItem.click({ force: true })
    await page.waitForTimeout(2000)
    await snap(page, 'p6-wf-03-workflow-detail', true)
  }
})

test('P6: Dashboard Builder interactions', async ({ page }) => {
  await page.goto('/dashboard-builder', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p6-dashb-01-init', true)
  await logInteractive(page, 'DashboardBuilder')

  // Create Dashboard CTA
  const createBtn = page.getByRole('button', { name: /Create Dashboard/i }).first()
  if (await createBtn.count()) {
    console.log('  Clicking Create Dashboard')
    await safeClick(createBtn)
    await page.waitForTimeout(2000)
    await snap(page, 'p6-dashb-02-created', true)
  }

  // Empty state
  const empty = page.locator('text=/No Dashboard Selected/i')
  if (await empty.count()) {
    console.log('  Empty state visible')
  }
})

test('P6: Knowledge interactions', async ({ page }) => {
  await page.goto('/knowledge', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p6-know-01-init', true)
  await logInteractive(page, 'Knowledge')

  // Upload Document button
  const uploadBtn = page.getByRole('button', { name: /Upload.*Document/i }).first()
  if (await uploadBtn.count()) {
    console.log('  Upload Document button visible')
  }

  // Knowledge Graph button
  const kgBtn = page.locator('text="Knowledge Graph"').first()
  if (await kgBtn.count()) {
    console.log('  Clicking Knowledge Graph')
    await kgBtn.click({ force: true })
    await page.waitForTimeout(2000)
    await snap(page, 'p6-know-02-kg', true)
    await page.goto('/knowledge', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // Generate FAQ button
  const faqBtn = page.locator('text="Generate FAQ"').first()
  if (await faqBtn.count()) {
    console.log('  Generate FAQ button visible')
  }

  // Empty state
  const empty = page.locator('text=/No documents found/i')
  if (await empty.count()) {
    console.log('  Empty state: "No documents found"')
  }
})

// ═══════════════════════════════════════════════════
// PHASE 7: Design + Visualization + Agents + Ingestion
// ═══════════════════════════════════════════════════
test('P7: Design page interactions', async ({ page }) => {
  await page.goto('/design', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p7-design-01-init', true)
  await logInteractive(page, 'Design')

  // Tabs: Brand Kits, Themes, Color Generator
  const tabs = ['Themes', 'Color Generator']
  for (const tab of tabs) {
    const el = page.locator(`text="${tab}"`).first()
    if (await el.count()) {
      console.log(`  Clicking tab: ${tab}`)
      await el.click({ force: true })
      await page.waitForTimeout(1500)
      await snap(page, `p7-design-02-tab-${tab.replace(/\s/g, '')}`, true)
    }
  }

  // New Brand Kit button
  const newKit = page.getByRole('button', { name: /New Brand Kit/i }).first()
  if (await newKit.count()) {
    console.log('  Clicking New Brand Kit')
    await safeClick(newKit)
    await page.waitForTimeout(2000)
    await snap(page, 'p7-design-03-new-kit', true)
    await page.goto('/design', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // Brand kit cards — click "Set Default"
  const setDefault = page.locator('text="Set Default"').first()
  if (await setDefault.count()) {
    console.log('  Clicking Set Default on a brand kit')
    await setDefault.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p7-design-04-set-default')
  }

  // Delete buttons on brand kits
  const deleteIcons = page.locator('[aria-label*="delete"], [data-testid*="Delete"]')
  console.log(`  Delete icons on brand kits: ${await deleteIcons.count()}`)
})

test('P7: Visualization page interactions', async ({ page }) => {
  await page.goto('/visualization', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p7-viz-01-init', true)
  await logInteractive(page, 'Visualization')

  // "Try with Example Data" button
  const tryExample = page.getByRole('button', { name: /Try with Example Data/i }).first()
  if (await tryExample.count()) {
    console.log('  Clicking Try with Example Data')
    await safeClick(tryExample)
    await page.waitForTimeout(2000)
    await snap(page, 'p7-viz-02-example', true)
  }

  // Diagram type sidebar items (left panel)
  const diagramTypes = page.locator('[class*="sidebar"] button, [class*="Sidebar"] button, [class*="drawer"] button')
  console.log(`  Diagram type buttons: ${await diagramTypes.count()}`)
})

test('P7: Agents page interactions', async ({ page }) => {
  await page.goto('/agents', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p7-agents-01-init', true)
  await logInteractive(page, 'Agents')

  // Agent type cards
  const agentCards = page.locator('text=/Research|Data Analyst|Content Repurpose|Proofreading/')
  console.log(`  Agent type cards: ${await agentCards.count()}`)

  // Click "Data Analyst" card
  const dataAnalyst = page.locator('text="Data Analyst"').first()
  if (await dataAnalyst.count()) {
    console.log('  Clicking Data Analyst')
    await dataAnalyst.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p7-agents-02-data-analyst', true)
  }

  // Depth dropdown
  const depthSelect = page.locator('[role="combobox"], select').first()
  if (await depthSelect.count()) {
    console.log('  Depth dropdown visible')
  }

  // History button
  const historyBtn = page.locator('text="History"').first()
  if (await historyBtn.count()) {
    console.log('  Clicking History')
    await historyBtn.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p7-agents-03-history')
  }
})

test('P7: Ingestion page interactions', async ({ page }) => {
  await page.goto('/ingestion', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p7-ingest-01-init', true)
  await logInteractive(page, 'Ingestion')

  // Method cards (Web Clipper, Folder Watcher, Email Import, Transcription)
  const methods = ['Web Clipper', 'Folder Watcher', 'Email Import', 'Transcription']
  for (const m of methods) {
    const card = page.locator(`text="${m}"`).first()
    if (await card.count()) {
      console.log(`  Method card visible: ${m}`)
    }
  }

  // Drag & drop zone
  const dropzone = page.locator('text=/Drag.*drop|click to browse/')
  if (await dropzone.count()) {
    console.log('  File drop zone visible')
  }

  // Click a method card
  const webClipper = page.locator('text="Web Clipper"').first()
  if (await webClipper.count()) {
    console.log('  Clicking Web Clipper card')
    await webClipper.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p7-ingest-02-webclipper', true)
  }
})

// ═══════════════════════════════════════════════════
// PHASE 8: Settings + Activity + Search + Ops + Stats + History + Analyze + Summary
// ═══════════════════════════════════════════════════
test('P8: Settings page interactions', async ({ page }) => {
  await page.goto('/settings', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-settings-01-init', true)
  await logInteractive(page, 'Settings')

  // Toggle switches (Demo Mode, Auto-refresh, Notifications, etc.)
  const switches = page.locator('[role="checkbox"], input[type="checkbox"], [class*="MuiSwitch"]')
  const swCount = await switches.count()
  console.log(`  Toggle switches: ${swCount}`)
  if (swCount > 0) {
    const lastSwitch = switches.last()
    await lastSwitch.scrollIntoViewIfNeeded()
    await lastSwitch.click({ force: true })
    await page.waitForTimeout(500)
    await snap(page, 'p8-settings-02-toggle')
    await lastSwitch.click({ force: true }) // toggle back
    await page.waitForTimeout(500)
  }

  // Language dropdown
  const langSelect = page.locator('text="Language"').first()
  if (await langSelect.count()) {
    console.log('  Language setting visible')
  }

  // Export Configuration button
  const exportBtn = page.getByRole('button', { name: /Export Configuration/i }).first()
  if (await exportBtn.count()) {
    console.log('  Export Configuration button visible')
    await snap(page, 'p8-settings-03-export-btn')
  }
})

test('P8: Activity page interactions', async ({ page }) => {
  await page.goto('/activity', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-activity-01-init', true)
  await logInteractive(page, 'Activity')

  // Refresh button
  const refresh = page.locator('[aria-label*="refresh"], [aria-label*="Refresh"]').first()
  if (await refresh.count()) {
    console.log('  Clicking Refresh')
    await refresh.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p8-activity-02-refreshed')
  }

  // Activity log entries
  const entries = page.locator('text=/Status Updated|Deleted|Created/')
  console.log(`  Activity entries: ${await entries.count()}`)

  // Action filter dropdown
  const actionFilter = page.locator('text="Action"').first()
  if (await actionFilter.count()) {
    console.log('  Clicking Action filter')
    await actionFilter.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p8-activity-03-action-filter')
    await page.keyboard.press('Escape')
  }
})

test('P8: Search page interactions', async ({ page }) => {
  await page.goto('/search', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-search-01-init', true)
  await logInteractive(page, 'Search')

  // Search tabs: Full Text, Semantic, Regex, Boolean
  const tabs = ['Semantic', 'Regex', 'Boolean']
  for (const tab of tabs) {
    const el = page.locator(`text="${tab}"`).first()
    if (await el.count()) {
      console.log(`  Clicking tab: ${tab}`)
      await el.click({ force: true })
      await page.waitForTimeout(1000)
      await snap(page, `p8-search-02-tab-${tab}`)
    }
  }

  // Search input
  const searchInput = page.locator('input[placeholder*="Search"]').first()
  if (await searchInput.count()) {
    await searchInput.fill('quarterly revenue')
    await page.waitForTimeout(500)
    await snap(page, 'p8-search-03-typed')
    // Click Search button
    const searchBtn = page.getByRole('button', { name: /^Search$/i }).first()
    if (await searchBtn.count()) {
      await safeClick(searchBtn)
      await page.waitForTimeout(2000)
      await snap(page, 'p8-search-04-results', true)
    }
  }

  // Example search chips
  const exampleChips = page.locator('text=/quarterly revenue|documents about market|budget AND/')
  console.log(`  Example search chips: ${await exampleChips.count()}`)
})

test('P8: Ops Console interactions', async ({ page }) => {
  await page.goto('/ops', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-ops-01-init', true)
  await logInteractive(page, 'Ops')

  // Health & Data section
  const healthTabs = page.locator('text=/Health|Clients|Queue|Results|Cron|Scheduled|Database|Error|Analysis|Charts/')
  const tabCount = await healthTabs.count()
  console.log(`  Ops tabs/sections: ${tabCount}`)

  // Click a few health tabs
  for (const tab of ['Clients', 'Queue', 'Results']) {
    const el = page.locator(`text="${tab}"`).first()
    if (await el.count()) {
      await el.click({ force: true })
      await page.waitForTimeout(1000)
      await snap(page, `p8-ops-02-tab-${tab}`)
    }
  }

  // Get Active Tokens button
  const tokensBtn = page.getByRole('button', { name: /Get Active Tokens/i }).first()
  if (await tokensBtn.count()) {
    console.log('  Get Active Tokens visible')
  }

  // Cancel Job button
  const cancelBtn = page.getByRole('button', { name: /Cancel Job/i }).first()
  if (await cancelBtn.count()) {
    console.log('  Cancel Job visible')
  }
})

test('P8: Stats page interactions', async ({ page }) => {
  await page.goto('/stats', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-stats-01-init', true)
  await logInteractive(page, 'Stats')

  // Time Period dropdown
  const timePeriod = page.locator('text="Last 7 days"').first()
  if (await timePeriod.count()) {
    console.log('  Clicking Time Period dropdown')
    await timePeriod.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p8-stats-02-period-dropdown')
    await page.keyboard.press('Escape')
  }

  // Export button
  const exportBtn = page.getByRole('button', { name: /Export/i }).first()
  if (await exportBtn.count()) {
    console.log('  Export button visible')
  }

  // Refresh button
  const refresh = page.locator('[aria-label*="refresh"]').first()
  if (await refresh.count()) {
    await refresh.click({ force: true })
    await page.waitForTimeout(1500)
    await snap(page, 'p8-stats-03-refreshed')
  }

  // Stat cards
  const statCards = page.locator('text=/SUCCESS RATE|TEMPLATES|CONNECTIONS/')
  console.log(`  Stat cards: ${await statCards.count()}`)

  // Tabs (Jobs, Templates)
  const jobsTab = page.locator('text="Jobs"').first()
  const templatesTab = page.locator('text="Templates"').first()
  if (await templatesTab.count()) {
    await templatesTab.click({ force: true })
    await page.waitForTimeout(1000)
    await snap(page, 'p8-stats-04-templates-tab', true)
  }
})

test('P8: History page interactions', async ({ page }) => {
  await page.goto('/history', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-history-01-init', true)
  await logInteractive(page, 'History')

  // Generate New button
  const genNew = page.getByRole('button', { name: /Generate New/i }).first()
  if (await genNew.count()) {
    console.log('  Clicking Generate New')
    await safeClick(genNew)
    await page.waitForTimeout(2000)
    await snap(page, 'p8-history-02-generate', true)
    console.log(`  URL: ${page.url()}`)
    await page.goto('/history', { waitUntil: 'domcontentloaded', timeout: 10000 })
    await page.waitForTimeout(1500)
  }

  // Loading state or table
  const loading = page.locator('text=/Loading history/i')
  if (await loading.count()) {
    console.log('  Loading state visible')
  }

  // Filter dropdown
  const filterDD = page.locator('select, [role="combobox"]').first()
  if (await filterDD.count()) {
    console.log('  Filter dropdown visible')
  }
})

test('P8: Analyze page interactions', async ({ page }) => {
  await page.goto('/analyze', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-analyze-01-init', true)
  await logInteractive(page, 'Analyze')

  // Upload area
  const dropzone = page.locator('text=/Drop your document|click to browse/')
  if (await dropzone.count()) {
    console.log('  Document drop zone visible')
  }

  // Supported formats
  const formats = page.locator('text=/PDF|Excel|CSV|Word|Images/')
  console.log(`  Format labels: ${await formats.count()}`)

  // Confidence/Reversible badges
  const badges = page.locator('text=/Confidence|Reversible/')
  console.log(`  Safety badges: ${await badges.count()}`)
})

test('P8: Summary page interactions', async ({ page }) => {
  await page.goto('/summary', { waitUntil: 'domcontentloaded', timeout: 15000 })
  await page.waitForTimeout(2500)
  await snap(page, 'p8-summary-01-init', true)
  await logInteractive(page, 'Summary')

  // Text input area
  const textarea = page.locator('textarea').first()
  if (await textarea.count()) {
    console.log('  Typing content into textarea')
    await textarea.click({ force: true })
    await textarea.fill('This is a test report about quarterly financial performance and growth metrics.')
    await page.waitForTimeout(500)
    await snap(page, 'p8-summary-02-typed')
  }

  // Summary length slider
  const slider = page.locator('[role="slider"], input[type="range"]').first()
  if (await slider.count()) {
    console.log('  Summary length slider visible')
  }

  // Focus area chips
  const focusChips = page.locator('text=/Key findings|Financial metrics|Trends|Recommendations|Risks/')
  console.log(`  Focus area chips: ${await focusChips.count()}`)

  // Click a focus chip
  const keyFindings = page.locator('text="Key findings"').first()
  if (await keyFindings.count()) {
    await keyFindings.click({ force: true })
    await page.waitForTimeout(500)
    await snap(page, 'p8-summary-03-focus-selected')
  }

  // Generate Summary button
  const genBtn = page.getByRole('button', { name: /Generate Summary/i }).first()
  if (await genBtn.count()) {
    const disabled = await genBtn.isDisabled()
    console.log(`  Generate Summary: disabled=${disabled}`)
  }

  // Queue in Background button
  const queueBtn = page.getByRole('button', { name: /Queue in Background/i }).first()
  if (await queueBtn.count()) {
    console.log('  Queue in Background button visible')
  }

  console.log(`\n=== FINAL CONSOLE ERRORS: ${consoleLogs.length} ===`)
  consoleLogs.slice(0, 20).forEach(l => console.log(l))
  console.log(`=== FINAL NETWORK ERRORS: ${netErrors.length} ===`)
  netErrors.slice(0, 20).forEach(l => console.log(l))
})
