/**
 * Minimal smoke test to diagnose the AI agent execution environment.
 */
import { test, expect } from '@playwright/test'
import { spawnSync } from 'child_process'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const EVIDENCE_ROOT = path.resolve(__dirname, '..', 'evidence', 'ai-agent-smoke')

test.describe('AI Agent Smoke Check', () => {
  test.setTimeout(120_000)

  test('Step 1: basic test runs', async ({ page }) => {
    console.log('[SMOKE] Test started')
    expect(1 + 1).toBe(2)
    console.log('[SMOKE] Basic assertion passed')
  })

  test('Step 2: claude CLI accessible', async ({ page }) => {
    console.log('[SMOKE] Checking claude CLI...')
    const r = spawnSync('claude --version', {
      encoding: 'utf-8',
      timeout: 15_000,
      shell: true,
      windowsHide: true,
    })
    console.log(`[SMOKE] claude --version: status=${r.status}, stdout="${r.stdout?.trim()}"`)
    expect(r.status).toBe(0)
  })

  test('Step 3: claude responds to prompt', async ({ page }) => {
    console.log('[SMOKE] Sending test prompt to claude...')
    const prompt = 'Respond with ONLY this JSON, nothing else: {"type":"done","reasoning":"smoke test"}'
    const cmd = 'claude -p --output-format json --model haiku --tools ""'
    const r = spawnSync(cmd, {
      input: prompt,
      encoding: 'utf-8',
      timeout: 60_000,
      maxBuffer: 1024 * 1024,
      shell: true,
      windowsHide: true,
    })
    console.log(`[SMOKE] claude -p: status=${r.status}`)
    console.log(`[SMOKE] stdout length: ${r.stdout?.length}`)
    console.log(`[SMOKE] stderr: ${r.stderr?.trim().slice(0, 200)}`)
    expect(r.status).toBe(0)

    const cliResult = JSON.parse(r.stdout!.trim())
    console.log(`[SMOKE] is_error: ${cliResult.is_error}`)
    console.log(`[SMOKE] result preview: ${cliResult.result?.slice(0, 200)}`)
    expect(cliResult.is_error).toBe(false)
    expect(cliResult.result).toBeTruthy()
  })

  test('Step 4: page navigation works', async ({ page }) => {
    const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:5175'
    console.log(`[SMOKE] Navigating to ${baseUrl}...`)
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 15_000 })
    const title = await page.title()
    console.log(`[SMOKE] Page title: "${title}"`)
    console.log(`[SMOKE] Page URL: ${page.url()}`)
    expect(page.url()).toContain(baseUrl.replace('http://', ''))
  })

  test('Step 5: evidence directory creation', async ({ page }) => {
    console.log(`[SMOKE] Creating evidence dir: ${EVIDENCE_ROOT}`)
    fs.mkdirSync(EVIDENCE_ROOT, { recursive: true })
    expect(fs.existsSync(EVIDENCE_ROOT)).toBe(true)
    fs.writeFileSync(
      path.join(EVIDENCE_ROOT, 'smoke-test.json'),
      JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }, null, 2)
    )
    console.log('[SMOKE] Evidence written successfully')
  })
})
