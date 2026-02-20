/**
 * Shared helpers for frontend-backend integration tests.
 *
 * Utilities used across all spec files to reduce boilerplate and
 * ensure consistent patterns (MUI handling, API waits, console capture, etc.).
 */
import { type Page, expect } from '@playwright/test'
import path from 'node:path'

// ---------------------------------------------------------------------------
// Console capture
// ---------------------------------------------------------------------------

/**
 * Attach a console listener that records warning/error messages.
 * Call at the top of each test and assert `expect(messages).toEqual([])` at the end.
 */
export function captureConsole(page: Page): string[] {
  const messages: string[] = []
  page.on('console', (msg) => {
    if (['warning', 'error'].includes(msg.type())) {
      const text = msg.text()
      // Ignore network refusals from dev proxy when backend is not up yet
      if (text.includes('net::ERR_CONNECTION_REFUSED')) return
      // Ignore React StrictMode double-render warnings
      if (text.includes('ReactDOM.render is no longer supported')) return
      messages.push(`${msg.type()}: ${text}`)
    }
  })
  return messages
}

export function expectNoConsoleErrors(messages: string[]) {
  expect(messages).toEqual([])
}

// ---------------------------------------------------------------------------
// API response helpers
// ---------------------------------------------------------------------------

/**
 * Wait for a backend response matching the given URL fragment and optional method.
 * Returns the Response object for further assertions.
 *
 * Example:
 *   const resp = await waitForApi(page, '/connections/test', 'POST')
 *   expect(resp.ok()).toBeTruthy()
 */
export function waitForApi(
  page: Page,
  urlPart: string,
  method?: string,
  timeout = 30_000,
) {
  return page.waitForResponse(
    (r) =>
      r.url().includes(urlPart) &&
      (method ? r.request().method() === method : true),
    { timeout },
  )
}

// ---------------------------------------------------------------------------
// MUI helpers
// ---------------------------------------------------------------------------

/**
 * Open an MUI Select identified by its accessible label, then click an option.
 *
 * MUI renders Select options in a portal overlay, so we:
 *   1. Click the combobox / trigger
 *   2. Wait for at least one option to become visible
 *   3. Click the matching option text
 */
export async function fillMuiSelect(
  page: Page,
  label: string | RegExp,
  optionText: string | RegExp,
) {
  const select = page.getByRole('combobox', { name: label })
  await expect(select).toBeVisible()
  await select.click()
  // MUI portals its listbox; wait for an option to appear
  await expect(page.getByRole('option').first()).toBeVisible({ timeout: 10_000 })
  await page.getByRole('option', { name: optionText }).first().click()
}

/**
 * Confirm an MUI Dialog by clicking the primary action button.
 * Falls back to common labels: Confirm, Delete, Remove, OK, Yes.
 */
export async function confirmDialog(page: Page, buttonLabel?: string | RegExp) {
  if (buttonLabel) {
    await page.getByRole('button', { name: buttonLabel }).click()
    return
  }
  // Try common confirmation labels in order
  for (const label of ['Confirm', 'Delete', 'Remove', 'OK', 'Yes']) {
    const btn = page.getByRole('button', { name: label, exact: true })
    if ((await btn.count()) > 0) {
      await btn.click()
      return
    }
  }
  throw new Error('Could not find a confirmation button in dialog')
}

/**
 * Dismiss an MUI Dialog by clicking Cancel.
 */
export async function cancelDialog(page: Page) {
  await page.getByRole('button', { name: 'Cancel' }).click()
}

// ---------------------------------------------------------------------------
// Data seeding helpers
// ---------------------------------------------------------------------------

/**
 * Seed a test SQLite connection via the Connections page UI.
 * Returns the generated connection name for later cleanup.
 */
export async function seedConnection(page: Page): Promise<string> {
  const connName = `E2E Test ${Date.now()}`
  await page.goto('/connections')
  await page.getByRole('button', { name: 'Add Data Source' }).click()
  await page.getByLabel('Connection Name').fill(connName)
  const dbPath = path.resolve(process.cwd(), '..', 'backend', 'testdata', 'sample.db')
  await page.getByLabel('Database Path').fill(dbPath)
  await page.getByRole('button', { name: 'Add Connection' }).click()
  // Wait for the connection to appear
  await expect(page.getByText(connName).first()).toBeVisible({ timeout: 20_000 })
  return connName
}

/**
 * Best-effort cleanup of a named connection. Does NOT fail the test on error.
 */
export async function cleanupConnection(page: Page, connName: string) {
  try {
    await page.goto('/connections')
    const searchBox = page.getByPlaceholder('Search connections...').first()
    await searchBox.fill(connName)
    await page.waitForTimeout(300)
    await page.getByRole('button', { name: 'More actions' }).first().click({ timeout: 5_000 })
    await page.getByRole('menuitem', { name: 'Delete' }).click({ timeout: 5_000 })
    await page.getByRole('button', { name: 'Remove' }).click({ timeout: 5_000 })
    await expect(page.getByText(connName)).toHaveCount(0, { timeout: 10_000 })
  } catch {
    // Non-fatal — connection cleanup failure is acceptable in dev/test
  }
}

// ---------------------------------------------------------------------------
// Navigation helpers
// ---------------------------------------------------------------------------

/**
 * Navigate via the sidebar by clicking the named button.
 */
export async function navigateSidebar(page: Page, name: string) {
  await page.getByRole('button', { name }).click()
}

/**
 * Verify a page heading is visible after navigation.
 */
export async function expectHeading(page: Page, text: string | RegExp) {
  await expect(
    page.getByRole('heading', { name: text }).first(),
  ).toBeVisible({ timeout: 15_000 })
}

// ---------------------------------------------------------------------------
// File upload helper
// ---------------------------------------------------------------------------

/**
 * Upload a file using an invisible <input type="file"> connected to a button.
 * Clicks the trigger button, then sets the file on the input.
 */
export async function uploadFile(
  page: Page,
  triggerLabel: string | RegExp,
  filePath: string,
) {
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.getByRole('button', { name: triggerLabel }).click(),
  ])
  await fileChooser.setFiles(filePath)
}
