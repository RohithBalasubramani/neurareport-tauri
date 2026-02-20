/**
 * BrowserAgent — Playwright-based browser controller.
 *
 * This is the "hands" of the AI test agent. It can:
 * - Take screenshots and observe the current page state
 * - Click buttons, type into fields, select dropdown options
 * - Navigate to URLs, scroll the page
 * - Capture network traffic (API calls to the backend)
 * - Upload files
 *
 * The BrowserAgent does NOT decide what to do — that's the AgentBrain's job.
 * This class simply executes actions and reports observations.
 */
import { type Page, type Response, type Request } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import type {
  AgentAction,
  PageObservation,
  InteractiveElement,
  ApiCallRecord,
  ActionTarget,
  ActionVerification,
  PageStability,
  ActionLogEntry,
} from './types'
import type { AgentConfig } from './config'

// Pattern borrowed from semantic audit: comprehensive API route matching
const API_ROUTE_PATTERN = /\/(api|connections|templates|reports|jobs|schedules|analyze|enrichment|federation|synthesis|docqa|documents|spreadsheets|dashboards|connectors|workflows|export|design|knowledge|ingestion|search|visualization|agents|nl2sql|charts|summary|recommendations|docai|ai)\b/

export class BrowserAgent {
  private page: Page
  private config: AgentConfig
  private apiCalls: ApiCallRecord[] = []
  private requestBodies: Map<string, string> = new Map()
  private consoleErrors: string[] = []
  private evidenceDir: string
  private screenshotCount = 0
  private pendingRequests = 0

  // Failure mode mitigation: action replay detection
  private actionHistory: Array<{ type: string; targetKey: string; timestamp: number }> = []

  // Failure mode mitigation: track last page state for change detection
  private lastObservation: { url: string; heading?: string; elementCount: number } | null = null

  constructor(page: Page, evidenceDir: string, config?: AgentConfig) {
    this.page = page
    this.evidenceDir = evidenceDir
    this.config = config || {
      appName: 'NeuraReport',
      baseUrl: process.env.BASE_URL || 'http://localhost:5174',
      llm: { model: 'sonnet', useVision: true },
      verifyAfterAction: true,
      waitForStable: true,
      stabilityTimeout: 5000,
      detectActionReplay: true,
      maxRepeatedActions: 3,
    }
    fs.mkdirSync(path.join(evidenceDir, 'screenshots'), { recursive: true })
    fs.mkdirSync(path.join(evidenceDir, 'network'), { recursive: true })
    this.setupNetworkCapture()
    this.setupConsoleCapture()
    this.setupRequestTracking()
  }

  /**
   * FAILURE MODE MITIGATION: Track pending network requests
   * This helps detect when the page is still loading/fetching data
   */
  private setupRequestTracking() {
    this.page.on('request', () => {
      this.pendingRequests++
    })
    this.page.on('response', () => {
      this.pendingRequests = Math.max(0, this.pendingRequests - 1)
    })
    this.page.on('requestfailed', () => {
      this.pendingRequests = Math.max(0, this.pendingRequests - 1)
    })
  }

  /**
   * Attach request+response listeners to capture API calls.
   * Enhanced from semantic audit: captures request bodies and uses comprehensive route matching.
   */
  private setupNetworkCapture() {
    // Capture request bodies (from semantic audit pattern)
    this.page.on('request', (request: Request) => {
      const url = request.url()
      if (!url.includes('/api/') && !API_ROUTE_PATTERN.test(url)) return
      const postData = request.postData()
      if (postData) {
        this.requestBodies.set(`${request.method()}:${url}`, postData.slice(0, 1000))
      }
    })

    this.page.on('response', async (response: Response) => {
      const url = response.url()
      // Match API calls using comprehensive pattern (from semantic audit)
      if (!url.includes('/api/') && !API_ROUTE_PATTERN.test(url)) return
      const request = response.request()
      let responsePreview = ''
      try {
        const contentType = response.headers()['content-type'] || ''
        if (contentType.includes('json')) {
          const body = await response.json().catch(() => null)
          responsePreview = JSON.stringify(body).slice(0, 500)
        } else {
          responsePreview = (await response.text().catch(() => '')).slice(0, 500)
        }
      } catch { /* streaming or binary */ }

      const reqKey = `${request.method()}:${url}`
      this.apiCalls.push({
        method: request.method(),
        url: url,
        status: response.status(),
        responseTime: 0,
        responsePreview,
        requestBody: this.requestBodies.get(reqKey),
      })
      this.requestBodies.delete(reqKey)
    })
  }

  /**
   * Upgrade #2: Console error capturing (from Playwright Healer).
   * Captures browser console errors so the agent knows about JS crashes,
   * unhandled rejections, and runtime errors it can't see in the UI.
   */
  private setupConsoleCapture() {
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text().slice(0, 300)
        // Skip noisy/irrelevant errors
        if (text.includes('favicon') || text.includes('net::ERR_')) return
        this.consoleErrors.push(text)
      }
    })
    this.page.on('pageerror', (err) => {
      this.consoleErrors.push(`Uncaught: ${err.message.slice(0, 300)}`)
    })
  }

  // ─── FAILURE MODE MITIGATIONS ─────────────────────────────────────

  /**
   * MITIGATION: Wait for page stability before observing
   * Prevents reading stale DOM when spinners/loaders shift the layout
   */
  async waitForStable(timeout?: number): Promise<PageStability> {
    const maxWait = timeout || this.config.stabilityTimeout || 5000
    const startTime = Date.now()
    let lastCheck: PageStability = {
      isStable: false,
      pendingRequests: this.pendingRequests,
      hasAnimations: false,
      loadingIndicators: 0,
    }

    while (Date.now() - startTime < maxWait) {
      // Check for loading indicators (MUI spinners, skeletons, progress bars)
      const loadingIndicators = await this.page.evaluate(() => {
        const spinners = document.querySelectorAll('.MuiCircularProgress-root, .MuiLinearProgress-root, .MuiSkeleton-root, [role="progressbar"]')
        return spinners.length
      }).catch(() => 0)

      // Check for CSS animations
      const hasAnimations = await this.page.evaluate(() => {
        const animated = document.querySelectorAll(':not(:defined), .MuiCollapse-root.MuiCollapse-entered, .MuiFade-root')
        return animated.length > 0
      }).catch(() => false)

      lastCheck = {
        isStable: this.pendingRequests === 0 && loadingIndicators === 0 && !hasAnimations,
        pendingRequests: this.pendingRequests,
        hasAnimations,
        loadingIndicators,
      }

      if (lastCheck.isStable) {
        return lastCheck
      }

      await this.page.waitForTimeout(100)
    }

    // Timed out waiting for stability — return current state
    return lastCheck
  }

  /**
   * MITIGATION: Verify that an action had its expected effect
   * Prevents false passes where button clicks silently do nothing
   */
  async verifyAction(action: AgentAction, beforeState: PageObservation): Promise<ActionVerification> {
    // Wait a moment for the action to take effect
    await this.page.waitForTimeout(300)

    const afterUrl = this.page.url()
    const afterHeading = await this.getHeading()
    const afterElements = await this.getInteractiveElements()
    const recentApiCalls = [...this.apiCalls]

    // Check if URL changed
    const urlChanged = afterUrl !== beforeState.url

    // Check if heading changed
    const headingChanged = afterHeading !== beforeState.heading

    // Check if element count changed significantly (± 3)
    const elementCountChanged = Math.abs(afterElements.length - beforeState.interactiveElements.length) >= 3

    // Check if there was any network activity
    const networkActivity = recentApiCalls.length > 0

    // Check for expected signal if specified
    let signalFound = !action.expectedSignal // if no signal expected, consider it found
    if (action.expectedSignal) {
      const toasts = await this.getToasts()
      const pageText = await this.page.textContent('body').catch(() => '') || ''
      signalFound = toasts.some(t => t.toLowerCase().includes(action.expectedSignal!.toLowerCase()))
        || pageText.toLowerCase().includes(action.expectedSignal.toLowerCase())
    }

    const uiChanged = urlChanged || headingChanged || elementCountChanged
    const verified = uiChanged || networkActivity || signalFound

    return {
      verified,
      expectedSignal: action.expectedSignal,
      actualSignal: signalFound ? action.expectedSignal : undefined,
      uiChanged,
      networkActivity,
    }
  }

  /**
   * MITIGATION: Detect repeated identical actions (stuck loop)
   * Prevents infinite loops where agent clicks same button repeatedly
   */
  detectActionReplay(action: AgentAction): { isReplay: boolean; sameActionCount: number } {
    const targetKey = action.target
      ? `${action.target.role || ''}:${action.target.name || action.target.label || action.target.text || ''}`
      : 'no-target'
    const actionKey = `${action.type}:${targetKey}`
    const now = Date.now()

    // Add to history
    this.actionHistory.push({ type: action.type, targetKey: actionKey, timestamp: now })

    // Keep only last 20 actions
    if (this.actionHistory.length > 20) {
      this.actionHistory = this.actionHistory.slice(-20)
    }

    // Count how many times this exact action was taken recently (last 60s)
    const recentCutoff = now - 60_000
    const sameActionCount = this.actionHistory.filter(
      a => a.targetKey === actionKey && a.timestamp > recentCutoff
    ).length

    const maxRepeated = this.config.maxRepeatedActions || 3
    return {
      isReplay: sameActionCount > maxRepeated,
      sameActionCount,
    }
  }

  /**
   * MITIGATION: Check if the page actually changed after an action
   * Helps detect silent failures where action appeared to succeed but did nothing
   */
  async didPageChange(): Promise<boolean> {
    if (!this.lastObservation) return true // first observation, assume changed

    const currentUrl = this.page.url()
    const currentHeading = await this.getHeading()
    const currentElements = await this.getInteractiveElements()

    const urlChanged = currentUrl !== this.lastObservation.url
    const headingChanged = currentHeading !== this.lastObservation.heading
    const elementCountChanged = Math.abs(currentElements.length - this.lastObservation.elementCount) >= 2

    return urlChanged || headingChanged || elementCountChanged
  }

  // ─── Screenshots ─────────────────────────────────────────────────────

  /** Take a screenshot and save it as evidence */
  async takeScreenshot(label?: string): Promise<string> {
    this.screenshotCount++
    const filename = `${String(this.screenshotCount).padStart(3, '0')}-${label || 'step'}.png`
    const filepath = path.join(this.evidenceDir, 'screenshots', filename)
    try {
      await this.page.screenshot({ path: filepath, fullPage: false })
    } catch {
      // Screenshot can fail if page is navigating or crashed — non-fatal
      console.warn(`[BrowserAgent] Screenshot failed: ${label}`)
    }
    return filepath
  }

  /** Take a screenshot and return as base64 for LLM vision */
  async getScreenshotBase64(): Promise<string> {
    try {
      const buffer = await Promise.race([
        this.page.screenshot({ fullPage: false }),
        new Promise<Buffer>((_, reject) =>
          setTimeout(() => reject(new Error('Screenshot timeout')), 10_000)
        ),
      ])
      return buffer.toString('base64')
    } catch {
      return '' // return empty if screenshot fails or times out
    }
  }

  /** Observe the current page state — this is what the LLM "sees" */
  async observe(): Promise<PageObservation> {
    // MITIGATION: Wait for page to stabilize before observing
    if (this.config.waitForStable) {
      await this.waitForStable()
    }

    const url = this.page.url()
    const title = await this.page.title()

    // Get interactive elements on page
    const interactiveElements = await this.getInteractiveElements()

    // Get visible toasts/alerts
    const toasts = await this.getToasts()

    // Get visible errors
    const errors = await this.getErrors()

    // Get page heading
    const heading = await this.getHeading()

    // Get recent API calls and reset
    const recentApiCalls = [...this.apiCalls]
    this.apiCalls = []

    // Get recent console errors and reset
    const consoleErrors = [...this.consoleErrors]
    this.consoleErrors = []

    // Get screenshot as base64 for LLM
    const screenshot = await this.getScreenshotBase64()

    // Semantic hints from API activity (from semantic audit's SemanticVerifier pattern)
    // This tells the LLM brain about backend behavior it can't see from the UI
    const semanticHints: string[] = []
    for (const call of recentApiCalls) {
      if (call.status >= 400) {
        semanticHints.push(`Backend error: ${call.method} ${call.url} → ${call.status}`)
      }
      if (call.method === 'POST' && call.status < 300 && call.responsePreview) {
        try {
          const resp = JSON.parse(call.responsePreview)
          if (resp.id || resp.connection_id || resp.template_id || resp.job_id) {
            semanticHints.push(`Resource created: ID=${resp.id || resp.connection_id || resp.template_id || resp.job_id}`)
          }
        } catch { /* not JSON */ }
      }
    }

    // Track last observation for change detection
    this.lastObservation = {
      url,
      heading,
      elementCount: interactiveElements.length,
    }

    return {
      url,
      title,
      interactiveElements,
      toasts,
      screenshot,
      recentApiCalls,
      errors,
      heading,
      semanticHints,
      consoleErrors,
    }
  }

  /**
   * Get all interactive elements currently visible on the page.
   * Enhanced with MUI-aware disabled detection (from semantic audit).
   * Cap raised to 80 elements for better coverage.
   */
  private async getInteractiveElements(): Promise<InteractiveElement[]> {
    // Wrap page.evaluate with a timeout to prevent hangs when page JS is frozen
    const EVAL_TIMEOUT = 15_000
    return Promise.race([
      this.page.evaluate(() => {
      const elements: Array<{
        role: string
        name: string
        type?: string
        value?: string
        disabled?: boolean
        location?: string
        testId?: string
        x?: number
        y?: number
      }> = []

      // MUI-aware disabled detection (from semantic audit)
      function isDisabled(el: HTMLElement): boolean {
        return (el as any).disabled === true
          || el.getAttribute('aria-disabled') === 'true'
          || el.classList.contains('Mui-disabled')
          || (el.closest('button') as HTMLButtonElement)?.disabled === true
          || el.closest('.Mui-disabled') !== null
      }

      // Upgrade #9: Get element center coordinates for fallback clicking (from AskUI)
      function getCenter(el: HTMLElement): { x: number; y: number } {
        const rect = el.getBoundingClientRect()
        return { x: Math.round(rect.left + rect.width / 2), y: Math.round(rect.top + rect.height / 2) }
      }

      // Buttons (including icon buttons, MUI buttons)
      document.querySelectorAll('button, [role="button"], .MuiIconButton-root, .MuiButton-root').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return // not visible
        const htmlEl = el as HTMLElement
        const name = htmlEl.textContent?.trim().slice(0, 80)
          || htmlEl.getAttribute('aria-label')
          || htmlEl.getAttribute('title')
          || ''
        // Skip notification buttons (known to cause hangs)
        if (name.toLowerCase().includes('notification')) return
        const btnCenter = getCenter(htmlEl)
        elements.push({
          role: 'button',
          name,
          disabled: isDisabled(htmlEl),
          testId: htmlEl.dataset.testid || undefined,
          location: `${Math.round(htmlEl.getBoundingClientRect().top)}px from top`,
          ...btnCenter,
        })
      })

      // Text inputs (including MUI TextFields)
      document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="search"], input[type="url"], input[type="number"], textarea, .MuiInputBase-input').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLInputElement
        const label = htmlEl.getAttribute('aria-label')
          || document.querySelector(`label[for="${htmlEl.id}"]`)?.textContent?.trim()
          || htmlEl.placeholder
          || htmlEl.closest('.MuiFormControl-root')?.querySelector('label')?.textContent?.trim()
          || ''
        elements.push({
          role: 'textbox',
          name: label.slice(0, 80),
          type: htmlEl.type,
          value: htmlEl.value?.slice(0, 50),
          disabled: isDisabled(htmlEl),
          testId: htmlEl.dataset.testid || undefined,
        })
      })

      // Select/combobox (MUI Select, Autocomplete)
      document.querySelectorAll('[role="combobox"], select, .MuiSelect-select').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLElement
        elements.push({
          role: 'combobox',
          name: htmlEl.getAttribute('aria-label')
            || htmlEl.closest('.MuiFormControl-root')?.querySelector('label')?.textContent?.trim()
            || htmlEl.textContent?.trim().slice(0, 80)
            || '',
          disabled: isDisabled(htmlEl),
          testId: htmlEl.dataset.testid || undefined,
        })
      })

      // Links
      document.querySelectorAll('a[href]').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLAnchorElement
        elements.push({
          role: 'link',
          name: htmlEl.textContent?.trim().slice(0, 80) || htmlEl.getAttribute('aria-label') || '',
        })
      })

      // Tabs (MUI Tabs)
      document.querySelectorAll('[role="tab"], .MuiTab-root').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLElement
        elements.push({
          role: 'tab',
          name: htmlEl.textContent?.trim().slice(0, 80) || htmlEl.getAttribute('aria-label') || '',
        })
      })

      // Checkboxes & Switches (MUI)
      document.querySelectorAll('input[type="checkbox"], [role="checkbox"], .MuiSwitch-root input, [role="switch"]').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLElement
        elements.push({
          role: 'checkbox',
          name: htmlEl.getAttribute('aria-label')
            || htmlEl.closest('.MuiFormControlLabel-root')?.textContent?.trim().slice(0, 80)
            || '',
          value: (el as HTMLInputElement).checked ? 'checked' : 'unchecked',
        })
      })

      // Table sort headers (from semantic audit — these are clickable but client-side only)
      document.querySelectorAll('th[role="columnheader"], .MuiTableSortLabel-root').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLElement
        elements.push({
          role: 'columnheader',
          name: htmlEl.textContent?.trim().slice(0, 80) || '',
        })
      })

      // Menus/menu items (MUI)
      document.querySelectorAll('[role="menuitem"], .MuiMenuItem-root').forEach((el) => {
        if (!(el as HTMLElement).offsetParent) return
        const htmlEl = el as HTMLElement
        elements.push({
          role: 'menuitem',
          name: htmlEl.textContent?.trim().slice(0, 80) || '',
        })
      })

      return elements.slice(0, 100) // give Claude full visibility of all interactive elements
    }),
      new Promise<InteractiveElement[]>((_, reject) =>
        setTimeout(() => reject(new Error('getInteractiveElements timed out')), EVAL_TIMEOUT)
      ),
    ]).catch(() => []) // Return empty on timeout so the agent can still proceed
  }

  /** Get visible toast/snackbar messages */
  private async getToasts(): Promise<string[]> {
    return Promise.race([
      this.page.evaluate(() => {
        const toasts: string[] = []
        document.querySelectorAll('.MuiSnackbar-root, [role="alert"], .MuiAlert-root').forEach((el) => {
          const text = (el as HTMLElement).textContent?.trim()
          if (text) toasts.push(text.slice(0, 200))
        })
        return toasts
      }),
      new Promise<string[]>((resolve) => setTimeout(() => resolve([]), 5000)),
    ])
  }

  /** Get visible error messages */
  private async getErrors(): Promise<string[]> {
    return Promise.race([
      this.page.evaluate(() => {
        const errors: string[] = []
        document.querySelectorAll('.MuiFormHelperText-root.Mui-error, .MuiAlert-standardError, [role="alert"]').forEach((el) => {
          const text = (el as HTMLElement).textContent?.trim()
          if (text) errors.push(text.slice(0, 200))
        })
        return errors
      }),
      new Promise<string[]>((resolve) => setTimeout(() => resolve([]), 5000)),
    ])
  }

  /** Get the main page heading */
  private async getHeading(): Promise<string | undefined> {
    return Promise.race([
      this.page.evaluate(() => {
        const h = document.querySelector('h1, h2, [role="heading"]')
        return h?.textContent?.trim().slice(0, 100) || undefined
      }),
      new Promise<string | undefined>((resolve) => setTimeout(() => resolve(undefined), 5000)),
    ])
  }

  // ─── Action execution ──────────────────────────────────────────────

  /** Execute an action decided by the AgentBrain */
  async execute(action: AgentAction): Promise<{ success: boolean; error?: string }> {
    try {
      switch (action.type) {
        case 'click':
          return await this.executeClick(action)
        case 'type':
          return await this.executeType(action)
        case 'navigate':
          return await this.executeNavigate(action)
        case 'scroll':
          return await this.executeScroll(action)
        case 'select':
          return await this.executeSelect(action)
        case 'upload':
          return await this.executeUpload(action)
        case 'wait':
          return await this.executeWait(action)
        case 'verify': {
          const verification = await this.verify(action.assertion)
          return verification.passed
            ? { success: true }
            : { success: false, error: `Verification failed: ${verification.actual}` }
        }
        case 'api_call': {
          if (!action.url) return { success: false, error: 'No URL for api_call action' }
          const method = action.method || 'GET'
          const apiResult = await this.apiCall(method, action.url, action.body)
          return apiResult.status < 400
            ? { success: true }
            : { success: false, error: `API ${method} ${action.url} -> ${apiResult.status}` }
        }
        case 'key':
          return await this.executeKey(action)
        case 'read' as any: // LLM sometimes emits "read" meaning "look at screenshot" — treat as screenshot
        case 'screenshot':
          await this.takeScreenshot(action.reasoning?.replace(/\s+/g, '-').slice(0, 40) || 'capture')
          return { success: true }
        case 'done':
          return { success: true }
        default:
          return { success: false, error: `Unknown action type: ${action.type}` }
      }
    } catch (err: any) {
      return { success: false, error: err.message?.slice(0, 300) }
    }
  }

  private resolveLocator(target?: ActionTarget) {
    if (!target) throw new Error('No target specified for action')

    // Support "nth" index for disambiguating multiple matches (e.g. multiple "PDF" buttons)
    const nthIndex = (target as any).nth

    if (target.role && target.name) {
      const loc = this.page.getByRole(target.role as any, { name: target.name })
      return typeof nthIndex === 'number' ? loc.nth(nthIndex) : loc.first()
    }
    if (target.label) {
      const loc = this.page.getByLabel(target.label)
      return typeof nthIndex === 'number' ? loc.nth(nthIndex) : loc.first()
    }
    if (target.placeholder) {
      const loc = this.page.getByPlaceholder(target.placeholder)
      return typeof nthIndex === 'number' ? loc.nth(nthIndex) : loc.first()
    }
    if (target.testId) {
      return this.page.getByTestId(target.testId)
    }
    if (target.text) {
      const loc = this.page.getByText(target.text)
      return typeof nthIndex === 'number' ? loc.nth(nthIndex) : loc.first()
    }
    if (target.css) {
      return this.page.locator(target.css).first()
    }
    throw new Error('No valid selector in target')
  }

  /**
   * Execute click with multi-strategy fallback (from semantic audit + AskUI):
   * 1. Scroll into view
   * 2. Regular click
   * 3. Force click (bypasses actionability checks)
   * 4. Coordinate-based click fallback (Upgrade #9 — from AskUI)
   */
  private async executeClick(action: AgentAction) {
    // Upgrade #9: Direct coordinate click if coordinates are provided
    if (action.target?.coordinates) {
      await this.page.mouse.click(action.target.coordinates.x, action.target.coordinates.y)
      await this.page.waitForTimeout(500)
      return { success: true }
    }

    const locator = this.resolveLocator(action.target)

    // Step 1: Scroll into view
    try {
      await locator.scrollIntoViewIfNeeded({ timeout: 3000 })
    } catch { /* fixed/sticky elements — continue */ }

    // Step 2: Try regular click
    try {
      await locator.click({ timeout: 10_000 })
    } catch (clickErr: any) {
      // Step 3: Force click as fallback
      try {
        await locator.click({ force: true, timeout: 10_000 })
      } catch {
        // Step 4: Coordinate-based click fallback (Upgrade #9)
        try {
          const box = await locator.boundingBox()
          if (box) {
            await this.page.mouse.click(
              box.x + box.width / 2,
              box.y + box.height / 2,
            )
          } else {
            throw clickErr
          }
        } catch {
          throw clickErr
        }
      }
    }

    await this.page.waitForTimeout(500) // let UI settle
    return { success: true }
  }

  private async executeType(action: AgentAction) {
    if (!action.value) return { success: false, error: 'No value to type' }

    if (action.target?.label) {
      const field = this.page.getByLabel(action.target.label)
      await field.fill(action.value, { timeout: 10_000 })
    } else {
      const locator = this.resolveLocator(action.target)
      await locator.fill(action.value, { timeout: 10_000 })
    }
    return { success: true }
  }

  /**
   * Navigate with retry on timeout/connection refused (from semantic audit).
   */
  private async executeNavigate(action: AgentAction) {
    if (!action.url) return { success: false, error: 'No URL to navigate to' }
    let retries = 3
    while (retries > 0) {
      try {
        await this.page.goto(action.url, { waitUntil: 'domcontentloaded', timeout: 30_000 })
        await this.page.waitForTimeout(1000)
        return { success: true }
      } catch (err: any) {
        retries--
        const isRetryable = err.message?.includes('Timeout') || err.message?.includes('ERR_CONNECTION_REFUSED')
        if (retries === 0 || !isRetryable) throw err
        const waitTime = err.message?.includes('ERR_CONNECTION_REFUSED') ? 15000 : 3000
        await this.page.waitForTimeout(waitTime)
      }
    }
    return { success: true }
  }

  private async executeScroll(action: AgentAction) {
    const amount = action.amount || 300
    const direction = action.direction === 'up' ? -amount : amount
    await this.page.mouse.wheel(0, direction)
    await this.page.waitForTimeout(300)
    return { success: true }
  }

  private async executeSelect(action: AgentAction) {
    if (!action.value) return { success: false, error: 'No option value to select' }
    // MUI Select: click combobox, wait for options, click option
    const locator = this.resolveLocator(action.target)
    await locator.click({ timeout: 10_000 })
    await this.page.waitForTimeout(300)
    // Wait for options dropdown
    await this.page.getByRole('option').first().waitFor({ state: 'visible', timeout: 10_000 })
    await this.page.getByRole('option', { name: action.value }).first().click()
    await this.page.waitForTimeout(300)
    return { success: true }
  }

  private async executeUpload(action: AgentAction) {
    if (!action.value) return { success: false, error: 'No file path to upload' }
    const locator = this.resolveLocator(action.target)
    const [fileChooser] = await Promise.all([
      this.page.waitForEvent('filechooser'),
      locator.click(),
    ])
    await fileChooser.setFiles(action.value)
    await this.page.waitForTimeout(1000)
    return { success: true }
  }

  private async executeWait(action: AgentAction) {
    if (action.waitFor) {
      // Wait for text to appear
      await this.page.getByText(action.waitFor).first().waitFor({
        state: 'visible',
        timeout: 30_000,
      })
    } else {
      // Default wait
      await this.page.waitForTimeout(2000)
    }
    return { success: true }
  }

  /**
   * Execute a keyboard key press (Escape, Enter, Tab, etc.)
   */
  private async executeKey(action: AgentAction) {
    const key = action.key || 'Escape'
    await this.page.keyboard.press(key)
    await this.page.waitForTimeout(300) // let UI settle
    return { success: true }
  }

  /** Run a verification check */
  async verify(assertion: AgentAction['assertion']): Promise<{ passed: boolean; actual?: string }> {
    if (!assertion) return { passed: false, actual: 'No assertion provided' }

    try {
      switch (assertion.check) {
        case 'visible': {
          const loc = assertion.target ? this.resolveLocator(assertion.target) : null
          if (!loc) return { passed: false, actual: 'No target for visibility check' }
          const isVisible = await loc.isVisible()
          return { passed: isVisible, actual: String(isVisible) }
        }
        case 'text_contains': {
          const pageText = await this.page.textContent('body') || ''
          const contains = pageText.includes(assertion.expected as string || '')
          return { passed: contains, actual: contains ? 'found' : 'not found' }
        }
        case 'url_contains': {
          const url = this.page.url()
          const contains = url.includes(assertion.expected as string || '')
          return { passed: contains, actual: url }
        }
        case 'toast_message': {
          const toasts = await this.getToasts()
          const found = toasts.some(t => t.toLowerCase().includes((assertion.expected as string || '').toLowerCase()))
          return { passed: found, actual: toasts.join('; ') || 'no toasts' }
        }
        case 'api_response': {
          // Check most recent API call
          const lastCall = this.apiCalls[this.apiCalls.length - 1]
          if (!lastCall) return { passed: false, actual: 'no API calls captured' }
          return { passed: lastCall.status < 400, actual: `${lastCall.method} ${lastCall.url} → ${lastCall.status}` }
        }
        default:
          return { passed: false, actual: `Unknown check type: ${assertion.check}` }
      }
    } catch (err: any) {
      return { passed: false, actual: err.message }
    }
  }

  /** Make a direct API call (bypassing the browser) */
  async apiCall(
    method: string,
    endpoint: string,
    body?: Record<string, unknown>,
  ): Promise<{ status: number; data: unknown }> {
    const baseUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8001'
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`
    const apiKey = process.env.API_KEY || 'dev'

    const response = await this.page.request.fetch(url, {
      method,
      data: body,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      timeout: 30_000,
    })

    let data: unknown
    try {
      data = await response.json()
    } catch {
      data = await response.text()
    }
    return { status: response.status(), data }
  }

  /** Save the network capture log */
  async saveNetworkLog(scenarioId: string) {
    const logPath = path.join(this.evidenceDir, 'network', `${scenarioId}-network.json`)
    fs.writeFileSync(logPath, JSON.stringify(this.apiCalls, null, 2))
    return logPath
  }
}
