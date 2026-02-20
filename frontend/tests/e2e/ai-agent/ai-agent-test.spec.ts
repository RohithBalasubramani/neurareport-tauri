/**
 * AI Agent E2E Tests — LLM-driven browser testing.
 *
 * An AI agent (Claude) controls the browser like a real human user —
 * clicking buttons, filling forms, navigating pages, and reading results.
 *
 * Run specific scenarios:
 *   npx playwright test ai-agent-test.spec.ts --grep "conn-001"
 *   npx playwright test ai-agent-test.spec.ts --grep "agent"
 *   npx playwright test ai-agent-test.spec.ts --grep "audit"
 *
 * Run all:
 *   npx playwright test ai-agent-test.spec.ts
 *
 * Environment variables:
 *   AI_TEST_MODEL      - Claude model (default: sonnet)
 *   BASE_URL           - Frontend URL (default: http://127.0.0.1:5176)
 *   AI_TEST_SCENARIOS  - Comma-separated scenario IDs to run (default: all)
 */
import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { AITestRunner, generateAuditReport } from './test-runner'
import {
  ALL_SCENARIOS,
  generatePerPageScenarios,
  comprehensiveAuditScenario,
  fullWorkflowScenario,
} from './scenarios'
import type { TestScenario, ScenarioResult } from './types'

// ─── Configuration ─────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const EVIDENCE_ROOT = path.resolve(__dirname, '..', 'evidence', 'ai-agent')
const SELECTED_SCENARIOS = process.env.AI_TEST_SCENARIOS?.split(',').map(s => s.trim()) || []

function shouldRun(scenario: TestScenario): boolean {
  if (SELECTED_SCENARIOS.length === 0) return true
  return SELECTED_SCENARIOS.includes(scenario.id) || SELECTED_SCENARIOS.includes(scenario.category)
}

function getEvidenceDir(scenarioId: string): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  return path.join(EVIDENCE_ROOT, `${timestamp}-${scenarioId}`)
}

// ─── Preflight check ────────────────────────────────────────────────

test.beforeAll(async () => {
  // Verify claude CLI is available
  try {
    const { spawnSync } = await import('child_process')
    const check = spawnSync('claude', ['--version'], {
      encoding: 'utf-8',
      timeout: 10_000,
      shell: true,
      windowsHide: true,
    })
    if (check.status !== 0) throw new Error(check.stderr || 'exit ' + check.status)
    console.log(`Claude CLI: ${check.stdout?.trim()}`)
  } catch {
    console.warn('\n⚠ Claude CLI not found — AI agent tests require Claude Code CLI')
    console.warn('  Install from: https://docs.anthropic.com/claude-code\n')
  }
  fs.mkdirSync(EVIDENCE_ROOT, { recursive: true })
})

// ─── Helper to run a scenario ───────────────────────────────────────

async function runScenario(page: any, scenario: TestScenario): Promise<ScenarioResult> {
  const runner = new AITestRunner(page, {
    evidenceBaseDir: getEvidenceDir(scenario.id),
    model: process.env.AI_TEST_MODEL,
    screenshotEveryStep: true,
    actionDelay: 500,
  })

  return runner.runScenario(scenario)
}

// ═════════════════════════════════════════════════════════════════════
// USER TASK TESTS — The agent acts like a real user
// ═════════════════════════════════════════════════════════════════════

test.describe('AI Agent: User Tasks', () => {
  test.setTimeout(3_600_000) // 60 minutes per test (LLM steps can timeout at 15min each)

  for (const scenario of ALL_SCENARIOS.filter(s => !s.tags?.includes('comprehensive-audit'))) {
    test(`[${scenario.id}] ${scenario.name}`, async ({ page }) => {
      if (!shouldRun(scenario)) test.skip()

      const result = await runScenario(page, scenario)
      expect(result.status, `Scenario "${scenario.name}" should pass`).toBe('pass')
    })
  }
})

// ═════════════════════════════════════════════════════════════════════
// PER-PAGE AUDIT — Test every page individually
// ═════════════════════════════════════════════════════════════════════

test.describe('AI Agent: Per-Page Audit @audit', () => {
  test.setTimeout(3_600_000) // 60 minutes per test

  const perPageScenarios = generatePerPageScenarios()

  for (const scenario of perPageScenarios) {
    test(`[${scenario.id}] Audit: ${scenario.startUrl}`, async ({ page }) => {
      if (!shouldRun(scenario)) test.skip()

      const result = await runScenario(page, scenario)
      if (result.status !== 'pass') {
        console.warn(`⚠ Page audit ${scenario.startUrl}: ${result.status} — ${result.error || 'check evidence'}`)
      }
    })
  }
})

// ═════════════════════════════════════════════════════════════════════
// FULL SUITE — Run everything and generate a report
// ═════════════════════════════════════════════════════════════════════

test.describe('AI Agent: Full Suite @full-suite', () => {
  test.setTimeout(7_200_000) // 2 hours for full suite

  test('Run all scenarios and generate audit report', async ({ page }) => {
    const allResults: ScenarioResult[] = []

    for (const scenario of ALL_SCENARIOS) {
      if (!shouldRun(scenario)) continue
      try {
        const runner = new AITestRunner(page, {
          evidenceBaseDir: getEvidenceDir(scenario.id),
          model: process.env.AI_TEST_MODEL,
          screenshotEveryStep: true,
        })
        const result = await runner.runScenario(scenario)
        allResults.push(result)
      } catch (err: any) {
        console.error(`✗ Scenario ${scenario.id} crashed: ${err.message}`)
        allResults.push({
          scenarioId: scenario.id,
          scenarioName: scenario.name,
          status: 'error',
          duration: 0,
          actionCount: 0,
          actionLog: [],
          criteriaResults: [],
          error: err.message,
          evidence: { screenshots: [], networkCaptures: [], llmDecisions: '' },
        })
      }
    }

    // Generate aggregate report
    const report = generateAuditReport(allResults)

    const reportDir = path.join(EVIDENCE_ROOT, 'reports')
    fs.mkdirSync(reportDir, { recursive: true })
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
    const reportPath = path.join(reportDir, `ai-agent-report-${timestamp}.json`)
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))

    const summaryPath = path.join(reportDir, `ai-agent-report-${timestamp}.txt`)
    fs.writeFileSync(summaryPath, report.summary)

    console.log('\n' + report.summary)
    console.log(`\nReport saved to: ${reportPath}`)

    const passRate = report.totalScenarios ? report.passed / report.totalScenarios : 0
    expect(passRate, `Overall pass rate should be > 50%`).toBeGreaterThan(0.5)
  })
})
