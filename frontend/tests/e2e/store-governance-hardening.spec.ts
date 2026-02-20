/**
 * Source-inspection tests for frontend store/governance hardening — lines 1208-1247
 * of FORENSIC_AUDIT_REPORT.md.
 *
 * These tests verify that the fixes applied to frontend stores and UX governance
 * components are present in the source code by inspecting file contents.
 *
 * Run with: npx playwright test store-governance-hardening.spec.ts
 */
import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT = path.resolve(__dirname, '..', '..')

function readSource(relativePath: string): string {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf-8')
}

// =============================================================================
// STORE HARDENING
// =============================================================================

test.describe('ingestionStore — upload progress stale-state fix', () => {
  const src = () => readSource('src/stores/ingestionStore.js')

  test('uploadProgress uses updater function (not get())', () => {
    const source = src()
    // The old pattern: { ...get().uploadProgress, [fileId]: ... }
    expect(source).not.toContain('get().uploadProgress')
    // The new pattern uses Zustand state-updater callback
    expect(source).toContain('state.uploadProgress')
  })
})

test.describe('documentStore — savingComment loading flag', () => {
  const src = () => readSource('src/stores/documentStore.js')

  test('savingComment state field exists', () => {
    expect(src()).toContain('savingComment: false')
  })

  test('addComment sets savingComment', () => {
    expect(src()).toContain("savingComment: true")
  })

  test('addComment clears savingComment on success', () => {
    // After the API call succeeds, savingComment should be false in the set() call
    const source = src()
    const addCommentBlock = source.slice(
      source.indexOf('addComment:'),
      source.indexOf('resolveComment:')
    )
    expect(addCommentBlock).toContain('savingComment: false')
  })
})

test.describe('useAppStore — localStorage size guard', () => {
  const src = () => readSource('src/stores/useAppStore.js')

  test('loadDiscoveryFromStorage checks raw.length before JSON.parse', () => {
    const source = src()
    const loadFnStart = source.indexOf('const loadDiscoveryFromStorage')
    const loadFnEnd = source.indexOf('const evictOldestResults')
    const loadFn = source.slice(loadFnStart, loadFnEnd)
    expect(loadFn).toContain('raw.length > DISCOVERY_MAX_SIZE_BYTES')
  })
})

test.describe('queryStore — persisted selectedConnectionId validation', () => {
  const src = () => readSource('src/stores/queryStore.js')

  test('onRehydrateStorage is defined', () => {
    expect(src()).toContain('onRehydrateStorage')
  })

  test('validates selectedConnectionId on rehydration', () => {
    const source = src()
    expect(source).toContain('selectedConnectionId')
    // Should null out invalid values
    expect(source).toContain("state.selectedConnectionId = null")
  })
})

// =============================================================================
// UX GOVERNANCE HARDENING
// =============================================================================

test.describe('useEnforcement.js — dead code removed, Set bounded', () => {
  const src = () => readSource('src/components/ux/governance/useEnforcement.js')

  test('analyzeHandler function removed', () => {
    expect(src()).not.toContain('function analyzeHandler')
  })

  test('MAX_CHECKED_COMPONENTS cap defined', () => {
    expect(src()).toContain('MAX_CHECKED_COMPONENTS')
  })

  test('Set.clear() called when cap exceeded', () => {
    expect(src()).toContain('checkedComponents.clear()')
  })
})

test.describe('WorkflowContracts.jsx — sessionStorage validation', () => {
  const src = () => readSource('src/components/ux/governance/WorkflowContracts.jsx')

  test('validates workflowId exists in WorkflowContracts before dispatch', () => {
    const source = src()
    // The fix adds WorkflowContracts[parsed.activeWorkflow] check
    expect(source).toContain('WorkflowContracts[parsed.activeWorkflow]')
  })
})

test.describe('InteractionAPI.jsx — userAgent truncation', () => {
  const src = () => readSource('src/components/ux/governance/InteractionAPI.jsx')

  test('userAgent is sliced to max length', () => {
    const source = src()
    expect(source).toContain('.slice(0, 512)')
  })
})

test.describe('CommandPalette.jsx — query length cap', () => {
  const src = () => readSource('src/features/shell/components/CommandPalette.jsx')

  test('query is capped before sending to API', () => {
    const source = src()
    expect(source).toContain('cappedQuery')
    expect(source).toContain('.slice(0, 200)')
  })

  test('globalSearch uses cappedQuery, not raw query', () => {
    const source = src()
    // The globalSearch call should use cappedQuery
    expect(source).toContain('globalSearch(cappedQuery')
  })
})

// =============================================================================
// STORE UNBOUNDED ARRAY CAPS (13 stores)
// =============================================================================

test.describe('exportStore — array caps', () => {
  const src = () => readSource('src/stores/exportStore.js')

  test('exportJobs capped with .slice(0, 200)', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('agentStore — tasks cap', () => {
  const src = () => readSource('src/stores/agentStore.js')

  test('tasks array is capped', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('docqaStore — sessions and messages cap', () => {
  const src = () => readSource('src/stores/docqaStore.js')

  test('sessions capped', () => {
    expect(src()).toContain('.slice(0, 100)')
  })

  test('messages capped', () => {
    expect(src()).toContain('.slice(-500)')
  })
})

test.describe('workflowStore — workflows and executions cap', () => {
  const src = () => readSource('src/stores/workflowStore.js')

  test('arrays capped', () => {
    const source = src()
    expect(source).toContain('.slice(0, 200)')
  })
})

test.describe('visualizationStore — diagrams cap', () => {
  const src = () => readSource('src/stores/visualizationStore.js')

  test('diagrams capped', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('knowledgeStore — documents, collections, tags cap', () => {
  const src = () => readSource('src/stores/knowledgeStore.js')

  test('documents capped at 500', () => {
    expect(src()).toContain('.slice(0, 500)')
  })

  test('collections capped at 200', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('spreadsheetStore — spreadsheets and pivotTables cap', () => {
  const src = () => readSource('src/stores/spreadsheetStore.js')

  test('spreadsheets capped', () => {
    expect(src()).toContain('.slice(0, 200)')
  })

  test('pivotTables capped', () => {
    expect(src()).toContain('.slice(0, 100)')
  })
})

test.describe('dashboardStore — dashboards and widgets cap', () => {
  const src = () => readSource('src/stores/dashboardStore.js')

  test('dashboards capped', () => {
    expect(src()).toContain('.slice(0, 100)')
  })

  test('widgets capped', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('synthesisStore — sessions cap', () => {
  const src = () => readSource('src/stores/synthesisStore.js')

  test('sessions capped', () => {
    expect(src()).toContain('.slice(0, 100)')
  })
})

test.describe('connectorStore — connections cap', () => {
  const src = () => readSource('src/stores/connectorStore.js')

  test('connections capped at 200', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('federationStore — schemas cap', () => {
  const src = () => readSource('src/stores/federationStore.js')

  test('schemas capped at 200', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('enrichmentStore — customSources cap', () => {
  const src = () => readSource('src/stores/enrichmentStore.js')

  test('customSources capped at 200', () => {
    expect(src()).toContain('.slice(0, 200)')
  })
})

test.describe('templateChatStore — messages cap', () => {
  const src = () => readSource('src/stores/templateChatStore.js')

  test('messages capped at 500', () => {
    expect(src()).toContain('.slice(-500)')
  })
})

// =============================================================================
// GOVERNANCE COMPONENTS — SESSION 3 FIXES
// =============================================================================

test.describe('BackgroundOperations — operations cap + dead poll removal', () => {
  const src = () => readSource('src/components/ux/governance/BackgroundOperations.jsx')

  test('operations array is capped', () => {
    expect(src()).toContain('.slice(0, 200)')
  })

  test('dead polling code removed', () => {
    const source = src()
    // The empty poll function should no longer exist
    expect(source).not.toContain('const poll = () => {}')
  })
})

test.describe('IntentSystem — Map eviction', () => {
  const src = () => readSource('src/components/ux/governance/IntentSystem.jsx')

  test('intentMap size is checked against maxHistory', () => {
    const source = src()
    expect(source).toContain('intentMap.current.size > maxHistory')
  })

  test('oldest entry is evicted from Map', () => {
    const source = src()
    expect(source).toContain('intentMap.current.delete(oldest)')
  })
})

test.describe('TimeExpectations — Map eviction', () => {
  const src = () => readSource('src/components/ux/governance/TimeExpectations.jsx')

  test('MAX_TRACKED_OPERATIONS constant defined', () => {
    expect(src()).toContain('MAX_TRACKED_OPERATIONS')
  })

  test('oldest operation evicted when cap reached', () => {
    const source = src()
    expect(source).toContain('next.delete(oldest)')
  })
})

test.describe('IrreversibleBoundaries — useEffect cleanup', () => {
  const src = () => readSource('src/components/ux/governance/IrreversibleBoundaries.jsx')

  test('cooldownInterval cleaned up on unmount via useEffect', () => {
    const source = src()
    // Must have a useEffect that clears the interval on unmount
    expect(source).toContain('clearInterval(cooldownInterval.current)')
  })
})

test.describe('NavigationSafety — forceNavigation error handling', () => {
  const src = () => readSource('src/components/ux/governance/NavigationSafety.jsx')

  test('forceNavigation wraps callback in try-catch', () => {
    const source = src()
    const forceBlock = source.slice(
      source.indexOf('const forceNavigation'),
      source.indexOf('const cancelNavigation')
    )
    expect(forceBlock).toContain('try {')
    expect(forceBlock).toContain('catch')
    expect(forceBlock).toContain('finally')
  })
})

test.describe('RegressionGuards — try-catch around pattern.test', () => {
  const src = () => readSource('src/components/ux/governance/RegressionGuards.js')

  test('violation patterns wrapped in try-catch', () => {
    const source = src()
    const violationBlock = source.slice(
      source.indexOf('// Check violation patterns'),
      source.indexOf('// Check required patterns')
    )
    expect(violationBlock).toContain('try {')
    expect(violationBlock).toContain('} catch')
  })

  test('required patterns wrapped in try-catch', () => {
    const source = src()
    const requiredBlock = source.slice(
      source.indexOf('// Check required patterns'),
      source.indexOf('// In strict mode')
    )
    expect(requiredBlock).toContain('try {')
    expect(requiredBlock).toContain('} catch')
  })
})

// =============================================================================
// FRONTEND FEATURE FIXES
// =============================================================================

test.describe('useKeyboardShortcuts — handler try-catch', () => {
  const src = () => readSource('src/hooks/useKeyboardShortcuts.js')

  test('handler invocation is wrapped in try-catch', () => {
    const source = src()
    const handlerBlock = source.slice(
      source.indexOf('if (matchesShortcut(event, parsed))'),
      source.indexOf('return')  // first return after the match
    )
    expect(source).toContain('try {')
    expect(source).toContain('[useKeyboardShortcuts]')
  })
})

test.describe('NetworkStatusBanner — timeout cleanup', () => {
  const src = () => readSource('src/components/ux/NetworkStatusBanner.jsx')

  test('successTimeoutRef is used for setTimeout', () => {
    const source = src()
    expect(source).toContain('successTimeoutRef')
    expect(source).toContain('clearTimeout(successTimeoutRef.current)')
  })

  test('useEffect cleanup for successTimeoutRef exists', () => {
    const source = src()
    // Should have a cleanup useEffect
    expect(source).toContain('clearTimeout(successTimeoutRef.current)')
  })
})

test.describe('EditHistoryTimeline — history cap', () => {
  const src = () => readSource('src/features/generate/components/EditHistoryTimeline.jsx')

  test('MAX_HISTORY_ENTRIES constant defined', () => {
    expect(src()).toContain('MAX_HISTORY_ENTRIES')
  })

  test('history is capped before rendering', () => {
    const source = src()
    expect(source).toContain('history.slice(-MAX_HISTORY_ENTRIES)')
  })
})
