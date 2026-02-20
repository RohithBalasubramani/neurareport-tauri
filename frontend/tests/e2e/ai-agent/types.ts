/**
 * Type definitions for the AI Test Agent system.
 *
 * The AI agent acts like ChatGPT agent mode / Claude computer-use —
 * it sees the browser, decides what to click/type, and autonomously
 * tests the application like a human test engineer would.
 */

// ─── Action types the LLM can decide to perform ───────────────────────

export type AgentActionType =
  | 'click'
  | 'type'
  | 'navigate'
  | 'scroll'
  | 'select'       // MUI select dropdown
  | 'upload'       // file upload
  | 'wait'         // wait for condition
  | 'verify'       // assert something about the page
  | 'api_call'     // call backend API directly
  | 'screenshot'   // take a screenshot for evidence
  | 'key'          // press a keyboard key (Escape, Enter, Tab, etc.)
  | 'done'         // scenario complete

export interface AgentAction {
  type: AgentActionType
  /** Human-readable description of why the agent is doing this */
  reasoning: string
  /** Progress reflection from the last step */
  progress?: string
  /** Current blocker (if any) */
  blocker?: string
  /** What visible signal should happen if this action works */
  expectedSignal?: string
  /** Self-estimated confidence in this action (0.0-1.0) */
  confidence?: number
  /** Selector or target — role-based preferred: { role: 'button', name: 'Submit' } */
  target?: ActionTarget
  /** Value to type or select */
  value?: string
  /** URL for navigate or API call */
  url?: string
  /** HTTP method for api_call */
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  /** Body for api_call */
  body?: Record<string, unknown>
  /** Condition to wait for */
  waitFor?: string
  /** Assertion for verify */
  assertion?: VerifyAssertion
  /** Scroll direction */
  direction?: 'up' | 'down'
  /** Scroll amount in pixels */
  amount?: number
  /** Key to press (for 'key' action type) - e.g., 'Escape', 'Enter', 'Tab' */
  key?: string
}

export interface ActionTarget {
  /** Playwright role selector */
  role?: string
  /** Accessible name */
  name?: string
  /** data-testid */
  testId?: string
  /** CSS selector as fallback */
  css?: string
  /** Text content to find */
  text?: string
  /** Label for form fields */
  label?: string
  /** Placeholder text for inputs */
  placeholder?: string
  /** Nth index when multiple matches exist (0=first) */
  nth?: number
  /** Coordinate-based click fallback (from AskUI) — x,y pixel position */
  coordinates?: { x: number; y: number }
}

export interface VerifyAssertion {
  /** What to check */
  check: 'visible' | 'hidden' | 'text_contains' | 'text_equals' | 'count' | 'api_response' | 'page_title' | 'url_contains' | 'toast_message'
  /** Target element (optional - some checks are page-level) */
  target?: ActionTarget
  /** Expected value */
  expected?: string | number
  /** Tolerance for numeric checks */
  tolerance?: number
}

// ─── Agent observation of the page state ─────────────────────────────

export interface PageObservation {
  /** Current URL */
  url: string
  /** Page title */
  title: string
  /** Simplified DOM summary - interactive elements visible on page */
  interactiveElements: InteractiveElement[]
  /** Any visible toasts/alerts */
  toasts: string[]
  /** Screenshot (base64 encoded) */
  screenshot?: string
  /** Network calls since last observation */
  recentApiCalls: ApiCallRecord[]
  /** Any error messages visible on page */
  errors: string[]
  /** Current page heading */
  heading?: string
  /** Semantic hints inferred from backend activity (resource IDs, errors, etc.) */
  semanticHints?: string[]
  /** Browser console errors captured since last observation */
  consoleErrors?: string[]
}

export interface InteractiveElement {
  role: string
  name: string
  type?: string
  value?: string
  disabled?: boolean
  /** Visual location hint */
  location?: string
  testId?: string
  /** Bounding box center coordinates for fallback clicking */
  x?: number
  y?: number
}

export interface ApiCallRecord {
  method: string
  url: string
  status: number
  responseTime: number
  /** Truncated response body (first 500 chars) */
  responsePreview?: string
  /** Truncated request body (first 1000 chars) — for semantic verification */
  requestBody?: string
}

// ─── Test scenario definition ────────────────────────────────────────

export interface TestScenario {
  /** Unique ID */
  id: string
  /** Human-readable name */
  name: string
  /** What the agent should accomplish — described naturally */
  goal: string
  /** Step-by-step hints (optional — the LLM should figure it out) */
  hints?: string[]
  /** Starting URL */
  startUrl: string
  /** Maximum actions before giving up */
  maxActions: number
  /** Success criteria — what must be true for the scenario to pass */
  successCriteria: SuccessCriterion[]
  /** Backend brain checks — direct API validations */
  backendChecks?: BackendCheck[]
  /** Category for organization */
  category: 'connection' | 'template' | 'report' | 'schedule' | 'ai_agent' | 'nl2sql' | 'docqa' | 'workflow' | 'navigation'
  /** Tags */
  tags?: string[]
  /** Expected outcome — what the screen should look like when done (from WebDreamer) */
  expectedOutcome?: string
  /** Persona modifier — changes how the agent interacts (from Agent A/B paper) */
  persona?: PersonaModifier
  /** QA profile: NeuraReport-specialized or general-purpose */
  qaProfile?: QaAgentProfile
}

/** Persona modifiers change agent behavior to test UX from different perspectives */
export type PersonaModifier =
  | 'default'       // normal user
  | 'impatient'     // clicks fast, doesn't read instructions, expects instant feedback
  | 'confused'      // misclicks, hesitates, needs clear labels
  | 'power-user'    // uses keyboard shortcuts, expects advanced features
  | 'accessibility' // relies on screen readers, keyboard navigation
  | 'mobile'        // expects touch-friendly targets and responsive behavior
  | 'slow-network'  // expects robust loading and retry states

/** QA policy profile used by the agent brain */
export type QaAgentProfile =
  | 'neurareport'
  | 'general-purpose'

export interface SuccessCriterion {
  description: string
  check: VerifyAssertion
}

export interface BackendCheck {
  /** Description of what we're checking */
  description: string
  /** API endpoint to call */
  endpoint: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: Record<string, unknown>
  /** What to assert about the response */
  expectedStatus?: number
  /** JSON path expression to check in response */
  responseCheck?: {
    path: string
    operator: 'equals' | 'contains' | 'exists' | 'gt' | 'lt' | 'matches'
    value: unknown
  }
}

// ─── Agent execution result ──────────────────────────────────────────

/** Failure categories for structured analysis (from mabl Auto TFA) */
export type FailureCategory =
  | 'element_not_found'   // target element doesn't exist or isn't visible
  | 'element_not_interactable' // target element exists but cannot be interacted with
  | 'navigation_error'    // page failed to load or redirect
  | 'form_error'          // form validation or submission failed
  | 'timeout'             // action or page timed out
  | 'stuck_loop'          // agent repeated same actions without progress
  | 'assertion_failed'    // success criteria not met
  | 'browser_crash'       // page or browser closed unexpectedly
  | 'llm_error'           // Claude CLI failed to respond
  | 'network_error'       // network/API layer failed
  | 'auth_error'          // authentication/authorization failure
  | 'unknown'

export interface ScenarioResult {
  scenarioId: string
  scenarioName: string
  status: 'pass' | 'fail' | 'error' | 'timeout'
  /** Total time in ms */
  duration: number
  /** Number of actions taken */
  actionCount: number
  /** Full action log with reasoning */
  actionLog: ActionLogEntry[]
  /** Success criteria results */
  criteriaResults: CriterionResult[]
  /** Backend check results */
  backendResults?: BackendCheckResult[]
  /** Error message if failed */
  error?: string
  /** Structured failure category (from mabl Auto TFA) */
  failureCategory?: FailureCategory
  /** Evidence paths */
  evidence: {
    screenshots: string[]
    networkCaptures: string[]
    llmDecisions: string
  }
}

export interface ActionLogEntry {
  step: number
  timestamp: string
  action: AgentAction
  result: 'success' | 'failed' | 'skipped'
  error?: string
  /** Time taken for this action */
  duration: number
  /** Screenshot path after action */
  screenshotAfter?: string
}

export interface CriterionResult {
  description: string
  passed: boolean
  actual?: string
  expected?: string
}

export interface BackendCheckResult {
  description: string
  passed: boolean
  endpoint: string
  status?: number
  responsePreview?: string
  error?: string
}

// ─── Goal Ledger for progress tracking ───────────────────────────────

export interface GoalLedger {
  goal: string
  requiredOutcomes: string[]
  completedOutcomes: string[]
  stuckScore: number
  stepsSinceProgress: number
}

// ─── Perception Entry for UX analysis ────────────────────────────────

export interface PerceptionEntry {
  step: number
  url: string
  screenSummary: string
  visibleCTAs: string[]
  confidence: number
  confusionSignals: string[]
  progressMade: boolean
}

// ─── Action Cache for replay optimization ────────────────────────────

export interface CachedActionSequence {
  scenarioId: string
  actions: Array<{ type: string; target?: ActionTarget; value?: string }>
  success: boolean
  timestamp: string
}

// ─── Cross-session Learning ──────────────────────────────────────────

export interface LessonLearned {
  scenarioId: string
  lesson: string
  timestamp: string
}

// ─── Failure Mode Mitigation Types ───────────────────────────────────

/** Post-action verification result */
export interface ActionVerification {
  verified: boolean
  expectedSignal?: string
  actualSignal?: string
  uiChanged: boolean
  networkActivity: boolean
}

/** Page stability check result */
export interface PageStability {
  isStable: boolean
  pendingRequests: number
  hasAnimations: boolean
  loadingIndicators: number
}

/** Action replay detection */
export interface ReplayDetection {
  isReplay: boolean
  sameActionCount: number
  lastSameAction?: ActionLogEntry
}
