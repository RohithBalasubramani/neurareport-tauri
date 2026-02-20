/**
 * AI Agent Test Runner — Orchestrates the browser agent + LLM brain.
 *
 * This is the main execution loop:
 * 1. Initialize scenario
 * 2. Observe page state (screenshot + DOM)
 * 3. Send observation to LLM brain → get next action
 * 4. Execute action via browser agent
 * 5. Verify action had expected effect (failure mode mitigation)
 * 6. Record result, repeat until done or max actions
 * 7. Run backend brain checks
 * 8. Evaluate success criteria
 * 9. Generate evidence report
 *
 * Failure mode mitigations implemented:
 * - Wait-for-stable before observing (prevents stale DOM reads)
 * - Post-action verification (prevents false passes)
 * - Action replay detection (prevents stuck loops)
 * - Silent failure detection (checks if UI actually changed)
 */
import * as fs from 'fs'
import * as path from 'path'
import type { Page } from '@playwright/test'
import { BrowserAgent } from './browser-agent'
import { AgentBrain } from './agent-brain'
import { createConfig, type AgentConfig } from './config'
import type {
  TestScenario,
  ScenarioResult,
  ActionLogEntry,
  CriterionResult,
  BackendCheckResult,
} from './types'

export interface RunnerConfig {
  /** Directory for all evidence output */
  evidenceBaseDir: string
  /** Whether to take screenshots at every step */
  screenshotEveryStep?: boolean
  /** Delay between actions (ms) to avoid overwhelming the app */
  actionDelay?: number
  /** Model override (default: sonnet) */
  model?: string
  /** Full agent config (optional, overrides other settings) */
  agentConfig?: Partial<AgentConfig>
}

export class AITestRunner {
  private browser: BrowserAgent
  private brain: AgentBrain
  private runnerConfig: RunnerConfig
  private agentConfig: AgentConfig
  private page: Page

  constructor(page: Page, config: RunnerConfig) {
    this.page = page
    this.runnerConfig = {
      screenshotEveryStep: true,
      actionDelay: 500,
      ...config,
    }

    // Build agent config from runner config
    this.agentConfig = createConfig({
      screenshotEveryStep: config.screenshotEveryStep ?? true,
      actionDelay: config.actionDelay ?? 500,
      llm: {
        model: config.model || process.env.AI_TEST_MODEL || 'sonnet',
        useVision: true,
        timeout: 600_000,
      },
      learningDir: path.join(config.evidenceBaseDir, 'learning'),
      ...config.agentConfig,
    })

    // Create evidence directory for this run
    fs.mkdirSync(config.evidenceBaseDir, { recursive: true })

    this.browser = new BrowserAgent(page, config.evidenceBaseDir, this.agentConfig)
    this.brain = new AgentBrain(this.agentConfig)
  }

  /** Run a single scenario and return the result */
  async runScenario(scenario: TestScenario): Promise<ScenarioResult> {
    const startTime = Date.now()
    const actionLog: ActionLogEntry[] = []
    let error: string | undefined

    console.log(`\n${'═'.repeat(60)}`)
    console.log(`🤖 AI Agent: ${scenario.name}`)
    console.log(`   Goal: ${scenario.goal.slice(0, 100)}...`)
    console.log(`${'═'.repeat(60)}`)

    // Initialize the brain with this scenario
    this.brain.initScenario(scenario)

    // Navigate to start URL
    try {
      const baseUrl = process.env.BASE_URL || 'http://localhost:5174'
      const fullUrl = scenario.startUrl.startsWith('http')
        ? scenario.startUrl
        : `${baseUrl}${scenario.startUrl}`
      await this.page.goto(fullUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 })
      await this.page.waitForTimeout(2000) // let page render
    } catch (err: any) {
      return this.buildResult(scenario, startTime, actionLog, 'error', `Failed to navigate to start URL: ${err.message}`)
    }

    // Take initial screenshot
    await this.browser.takeScreenshot('initial')

    // Main action loop
    let actionCount = 0
    let isDone = false
    let consecutiveErrors = 0
    const MAX_CONSECUTIVE_ERRORS = 5

    while (actionCount < scenario.maxActions && !isDone) {
      actionCount++
      const stepStart = Date.now()

      // Bail if the page/browser was closed (prevents cascade of identical errors)
      if (this.page.isClosed()) {
        console.log(`    ✗ Page closed — stopping agent loop`)
        error = 'Page or browser was closed unexpectedly'
        break
      }

      try {
        // Per-step timeout: gives Claude ample time to think.
        // Claude is the brain — accuracy matters more than speed.
        // Set to 15 minutes to never rush Claude's decision making.
        const STEP_TIMEOUT = 900_000
        const stepResult = await Promise.race([
          this.runSingleStep(actionCount, scenario.maxActions),
          new Promise<{ timedOut: true }>((resolve) =>
            setTimeout(() => resolve({ timedOut: true }), STEP_TIMEOUT)
          ),
        ])

        if ('timedOut' in stepResult) {
          console.warn(`    ⚠ Step ${actionCount} timed out after ${STEP_TIMEOUT / 1000}s — skipping`)
          actionLog.push({
            step: actionCount,
            timestamp: new Date().toISOString(),
            action: { type: 'done', reasoning: `Step timed out after ${STEP_TIMEOUT / 1000}s` },
            result: 'failed',
            error: `Step timeout (${STEP_TIMEOUT / 1000}s)`,
            duration: STEP_TIMEOUT,
          })
          consecutiveErrors++
        } else if (stepResult.isDone) {
          isDone = true
          actionLog.push(stepResult.logEntry)
          break
        } else {
          actionLog.push(stepResult.logEntry)
          if (stepResult.logEntry.result === 'failed') {
            console.log(`    ⚠ Action failed: ${stepResult.logEntry.error?.slice(0, 100)}`)
            consecutiveErrors++
          } else {
            consecutiveErrors = 0
          }
        }

        // Bail after too many consecutive failures
        if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
          console.log(`    ✗ ${MAX_CONSECUTIVE_ERRORS} consecutive failures — stopping`)
          error = `Stopped after ${MAX_CONSECUTIVE_ERRORS} consecutive action failures`
          break
        }

        // Add delay between actions
        if (this.runnerConfig.actionDelay && !this.page.isClosed()) {
          await this.page.waitForTimeout(this.runnerConfig.actionDelay).catch(() => {})
        }

      } catch (err: any) {
        const msg = err.message || ''
        console.error(`    ✗ Step ${actionCount} crashed: ${msg.slice(0, 100)}`)
        actionLog.push({
          step: actionCount,
          timestamp: new Date().toISOString(),
          action: { type: 'done', reasoning: `Error: ${msg}` },
          result: 'failed',
          error: msg,
          duration: Date.now() - stepStart,
        })

        // Fatal: page/context destroyed — stop immediately
        if (msg.includes('has been closed') || msg.includes('Target closed') || msg.includes('browser has been closed')) {
          console.log(`    ✗ Browser/page closed — stopping agent loop`)
          error = 'Page or browser was closed unexpectedly'
          break
        }
        consecutiveErrors++
        if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
          error = `Stopped after ${MAX_CONSECUTIVE_ERRORS} consecutive crashes`
          break
        }
      }
    }

    if (!isDone && actionCount >= scenario.maxActions) {
      error = `Reached maximum actions (${scenario.maxActions}) without completing`
    }

    // Take final screenshot
    await this.browser.takeScreenshot('final')

    // Run backend brain checks
    const backendResults = await this.runBackendChecks(scenario)

    // Evaluate success criteria
    const criteriaResults = await this.evaluateCriteria(scenario)

    // Determine overall status
    const allCriteriaPassed = criteriaResults.every(r => r.passed)
    const allBackendPassed = backendResults.every(r => r.passed)
    const status = error
      ? (actionCount >= scenario.maxActions ? 'timeout' : 'error')
      : (allCriteriaPassed && allBackendPassed ? 'pass' : 'fail')

    // Upgrade #6/#8: Finalize scenario — save action cache (on success) / lessons (on failure)
    this.brain.finalizeScenario(status === 'pass')

    return this.buildResult(scenario, startTime, actionLog, status, error, criteriaResults, backendResults)
  }

  /** Execute a single step (observe → decide → execute → verify → screenshot) */
  private async runSingleStep(actionCount: number, maxActions: number): Promise<{
    isDone: boolean
    logEntry: ActionLogEntry
  }> {
    const stepStart = Date.now()

    // 1. Observe the current page state (includes wait-for-stable)
    const observation = await this.browser.observe()

    // 2. Ask the brain what to do
    const action = await this.brain.decideAction(observation)

    console.log(`  [${actionCount}/${maxActions}] ${action.type}: ${action.reasoning?.slice(0, 80)}`)

    // 3. Check if done
    if (action.type === 'done') {
      return {
        isDone: true,
        logEntry: {
          step: actionCount,
          timestamp: new Date().toISOString(),
          action,
          result: 'success',
          duration: Date.now() - stepStart,
        },
      }
    }

    // 4. FAILURE MODE MITIGATION: Detect action replay (stuck loop)
    if (this.agentConfig.detectActionReplay) {
      const replayCheck = this.browser.detectActionReplay(action)
      if (replayCheck.isReplay) {
        console.log(`    ⚠ REPLAY DETECTED: Same action ${replayCheck.sameActionCount} times`)
        // Don't immediately fail, but record it for the brain to see
        action.blocker = `WARNING: You've tried this exact action ${replayCheck.sameActionCount} times. Try something different!`
      }
    }

    // 5. Execute the action
    const result = await this.browser.execute(action)

    // 6. FAILURE MODE MITIGATION: Verify action had expected effect
    if (result.success && this.agentConfig.verifyAfterAction && action.type !== 'screenshot') {
      const verification = await this.browser.verifyAction(action, observation)
      if (!verification.verified && !verification.uiChanged && !verification.networkActivity) {
        // Action appeared to succeed but nothing changed — possible silent failure
        console.log(`    ⚠ SILENT FAILURE: Action succeeded but no UI change detected`)
        result.success = true // Don't mark as failed, but warn
        result.error = 'Warning: No visible change after action'
      }
    }

    // 7. Take screenshot if configured
    let screenshotPath: string | undefined
    if (this.runnerConfig.screenshotEveryStep) {
      screenshotPath = await this.browser.takeScreenshot(
        `step-${String(actionCount).padStart(3, '0')}-${action.type}`
      )
    }

    // 8. Record the result
    const duration = Date.now() - stepStart
    this.brain.recordResult(action, result, duration)

    return {
      isDone: false,
      logEntry: {
        step: actionCount,
        timestamp: new Date().toISOString(),
        action,
        result: result.success ? 'success' : 'failed',
        error: result.error,
        duration,
        screenshotAfter: screenshotPath,
      },
    }
  }

  /** Run backend API checks defined in the scenario */
  private async runBackendChecks(scenario: TestScenario): Promise<BackendCheckResult[]> {
    if (!scenario.backendChecks?.length) return []

    const results: BackendCheckResult[] = []
    for (const check of scenario.backendChecks) {
      try {
        const { status, data } = await this.browser.apiCall(
          check.method,
          check.endpoint,
          check.body,
        )

        const passed = check.expectedStatus
          ? status === check.expectedStatus
          : status < 400

        results.push({
          description: check.description,
          passed,
          endpoint: check.endpoint,
          status,
          responsePreview: JSON.stringify(data).slice(0, 300),
        })
      } catch (err: any) {
        results.push({
          description: check.description,
          passed: false,
          endpoint: check.endpoint,
          error: err.message,
        })
      }
    }
    return results
  }

  /** Evaluate success criteria against current page state */
  private async evaluateCriteria(scenario: TestScenario): Promise<CriterionResult[]> {
    const results: CriterionResult[] = []
    for (const criterion of scenario.successCriteria) {
      const result = await this.browser.verify(criterion.check)
      results.push({
        description: criterion.description,
        passed: result.passed,
        actual: result.actual,
        expected: criterion.check.expected as string,
      })
    }
    return results
  }

  /** Build the scenario result object */
  private buildResult(
    scenario: TestScenario,
    startTime: number,
    actionLog: ActionLogEntry[],
    status: ScenarioResult['status'],
    error?: string,
    criteriaResults?: CriterionResult[],
    backendResults?: BackendCheckResult[],
  ): ScenarioResult {
    // Upgrade #5: Failure categorization
    const failureCategory = status !== 'pass'
      ? this.brain.categorizeFailure(error, actionLog)
      : undefined

    const result: ScenarioResult = {
      scenarioId: scenario.id,
      scenarioName: scenario.name,
      status,
      duration: Date.now() - startTime,
      actionCount: actionLog.length,
      actionLog,
      criteriaResults: criteriaResults || [],
      backendResults,
      error,
      failureCategory,
      evidence: {
        screenshots: [],
        networkCaptures: [],
        llmDecisions: '',
      },
    }

    // Save evidence
    const evidenceDir = this.runnerConfig.evidenceBaseDir

    // Save action log
    const actionLogPath = path.join(evidenceDir, `${scenario.id}-action-log.json`)
    fs.writeFileSync(actionLogPath, JSON.stringify(actionLog, null, 2))

    // Save LLM conversation
    const convoPath = path.join(evidenceDir, `${scenario.id}-llm-conversation.json`)
    fs.writeFileSync(convoPath, JSON.stringify(this.brain.getConversation(), null, 2))
    result.evidence.llmDecisions = convoPath

    // Save perception log (what the user "experienced" each step)
    const perceptionPath = path.join(evidenceDir, `${scenario.id}-perception.json`)
    fs.writeFileSync(perceptionPath, JSON.stringify(this.brain.getPerceptionLog(), null, 2))

    // Save goal ledger (progress tracking)
    const ledgerPath = path.join(evidenceDir, `${scenario.id}-goal-ledger.json`)
    fs.writeFileSync(ledgerPath, JSON.stringify(this.brain.getLedger(), null, 2))

    // Save network log
    this.browser.saveNetworkLog(scenario.id)

    // Save full result
    const resultPath = path.join(evidenceDir, `${scenario.id}-result.json`)
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2))

    // Print summary
    const icon = status === 'pass' ? '✓' : status === 'fail' ? '✗' : status === 'timeout' ? '⏱' : '⚠'
    const ledger = this.brain.getLedger()
    console.log(`\n${icon} ${scenario.name}: ${status.toUpperCase()} (${actionLog.length} actions, ${Math.round(result.duration / 1000)}s)`)
    console.log(`  Goal progress: ${ledger.completedOutcomes.length}/${ledger.requiredOutcomes.length} outcomes | stuck score: ${ledger.stuckScore}`)
    if (criteriaResults?.length) {
      criteriaResults.forEach(c => {
        console.log(`  ${c.passed ? '✓' : '✗'} ${c.description}`)
      })
    }
    // Print perception confidence trend
    const perceptions = this.brain.getPerceptionLog()
    const avgConfidence = perceptions.length
      ? (perceptions.reduce((sum, p) => sum + p.confidence, 0) / perceptions.length).toFixed(2)
      : 'N/A'
    const confusionCount = perceptions.filter(p => p.confusionSignals.length > 0).length
    console.log(`  Confidence: ${avgConfidence} avg | ${confusionCount} confused steps`)
    if (failureCategory) {
      console.log(`  Failure category: ${failureCategory}`)
    }

    return result
  }
}

// ─── Aggregate report generation ─────────────────────────────────────

export interface AuditReport {
  timestamp: string
  totalScenarios: number
  passed: number
  failed: number
  errors: number
  timeouts: number
  totalDuration: number
  totalActions: number
  scenarios: ScenarioResult[]
  summary: string
}

export function generateAuditReport(results: ScenarioResult[]): AuditReport {
  const passed = results.filter(r => r.status === 'pass').length
  const failed = results.filter(r => r.status === 'fail').length
  const errors = results.filter(r => r.status === 'error').length
  const timeouts = results.filter(r => r.status === 'timeout').length

  const report: AuditReport = {
    timestamp: new Date().toISOString(),
    totalScenarios: results.length,
    passed,
    failed,
    errors,
    timeouts,
    totalDuration: results.reduce((sum, r) => sum + r.duration, 0),
    totalActions: results.reduce((sum, r) => sum + r.actionCount, 0),
    scenarios: results,
    summary: [
      `AI Agent Audit Report`,
      `═════════════════════`,
      `Total Scenarios: ${results.length}`,
      `Passed: ${passed} | Failed: ${failed} | Errors: ${errors} | Timeouts: ${timeouts}`,
      `Pass Rate: ${results.length ? Math.round(passed / results.length * 100) : 0}%`,
      `Total Actions: ${results.reduce((sum, r) => sum + r.actionCount, 0)}`,
      `Total Duration: ${Math.round(results.reduce((sum, r) => sum + r.duration, 0) / 1000)}s`,
      '',
      ...results.map(r => {
        const icon = r.status === 'pass' ? '✓' : r.status === 'fail' ? '✗' : '⚠'
        const category = r.failureCategory ? ` [${r.failureCategory}]` : ''
        return `${icon} [${r.status.toUpperCase()}]${category} ${r.scenarioName} (${r.actionCount} actions, ${Math.round(r.duration / 1000)}s)`
      }),
    ].join('\n'),
  }

  return report
}
