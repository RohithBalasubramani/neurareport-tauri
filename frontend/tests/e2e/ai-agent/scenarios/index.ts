/**
 * Test Scenarios for the AI Agent.
 *
 * DESIGN PRINCIPLE: Behavioral expectations, not procedural steps.
 *
 * Each scenario tells the agent WHAT outcome to achieve, not HOW to achieve it.
 * The agent figures out the clicks, form fills, and navigation on its own —
 * just like a real user would. If the UI is unclear, the agent gets confused
 * and that's a UX bug worth finding.
 *
 * No API endpoints. No backend checks. Just: "you want X, go get it."
 */
import type { TestScenario } from '../types'

// ═════════════════════════════════════════════════════════════════════
// CONNECTION SCENARIOS
// ═════════════════════════════════════════════════════════════════════

export const createConnectionScenario: TestScenario = {
  id: 'conn-001-create',
  name: 'Create a new database connection',
  goal: `You want a new database connection set up in this app.

Find a way to create one. The connection should be:
- Name: "AI Test Connection"
- Type: SQLite
- Database path: backend/testdata/sample.db

When you're done, you should be able to see "AI Test Connection" listed on the page.`,
  hints: [
    'Look for an "Add" or "New" button to start creating a connection',
    'SQLite connections just need a file path, no host/port',
  ],
  startUrl: '/connections',
  maxActions: 25,
  expectedOutcome: 'A list of connections with "AI Test Connection" visible as an entry',
  successCriteria: [
    {
      description: 'The new connection "AI Test Connection" is visible in the list',
      check: { check: 'text_contains', expected: 'AI Test Connection' },
    },
  ],
  category: 'connection',
  tags: ['crud', 'happy-path'],
  qaProfile: 'neurareport',
}

export const testConnectionScenario: TestScenario = {
  id: 'conn-002-test',
  name: 'Test an existing database connection',
  goal: `You want to check if an existing database connection actually works.

Find a connection in the list and test it. You should see some kind of
success or failure feedback on screen after testing.`,
  hints: [
    'Look for a test button, or a menu with test options',
    'You might need to click into a connection first to find the test action',
  ],
  startUrl: '/connections',
  maxActions: 20,
  expectedOutcome: 'A success or failure message after testing the connection',
  successCriteria: [
    {
      description: 'Stayed on connections page and interacted with a connection',
      check: { check: 'url_contains', expected: '/connections' },
    },
  ],
  category: 'connection',
  tags: ['validation'],
  qaProfile: 'neurareport',
}

// ═════════════════════════════════════════════════════════════════════
// TEMPLATE SCENARIOS
// ═════════════════════════════════════════════════════════════════════

export const browseTemplatesScenario: TestScenario = {
  id: 'tmpl-001-browse',
  name: 'Browse and inspect a template',
  goal: `You want to see what report templates are available and look inside one.

Find the templates, open one to see its details. What does a template contain?
Sections? Variables? A preview? Explore and find out.`,
  hints: [
    'Click on a template row or card to see details',
    'There might be tabs or sections inside the template detail view',
  ],
  startUrl: '/templates',
  maxActions: 20,
  expectedOutcome: 'A template detail view showing sections, variables, or preview content',
  successCriteria: [
    {
      description: 'A template was opened and explored',
      // NeuraReport opens templates via /reports?template=... not /templates/{id}
      check: { check: 'url_contains', expected: '/reports' },
    },
  ],
  category: 'template',
  tags: ['read-only', 'exploration'],
  persona: 'confused', // Upgrade #7: test as a confused user — templates should be discoverable
  qaProfile: 'neurareport',
}

export const exploreTemplatesScenario: TestScenario = {
  id: 'tmpl-002-explore',
  name: 'Deep-explore template configuration',
  goal: `You want to understand everything a template can do.

Open a template and click through ALL its tabs, sections, and options.
What can you configure? What does the schema look like? Is there a preview?
Explore every tab and panel you can find inside the template detail view.

Only say done after you've clicked on at least 2 different tabs or sections.`,
  hints: [
    'Look for tabs like Preview, Schema, Sections, Variables, Mapping',
    'Some tabs may have sub-sections or expandable panels',
  ],
  startUrl: '/templates',
  maxActions: 25,
  expectedOutcome: 'Multiple tabs/sections within a template detail view have been explored',
  successCriteria: [
    {
      description: 'Template details were deeply explored',
      // NeuraReport opens templates via /reports?template=... not /templates/{id}
      check: { check: 'url_contains', expected: '/reports' },
    },
  ],
  category: 'template',
  tags: ['exploration', 'read-only'],
  persona: 'power-user', // Upgrade #7: power user explores everything
  qaProfile: 'neurareport',
}

// ═════════════════════════════════════════════════════════════════════
// AI AGENT SCENARIOS
// ═════════════════════════════════════════════════════════════════════

export const researchAgentScenario: TestScenario = {
  id: 'agent-001-research',
  name: 'Get a research report from the AI',
  goal: `You want the AI to research a topic and give you a report.

Find the Research Agent, give it a topic like "Impact of AI on software testing",
and get a report back. You should see research results, sections, or findings
displayed on screen before you're done.`,
  hints: [
    'The agents page may have different agent types to choose from',
    'Results might take 30-60 seconds to generate',
    'Look for a loading indicator while waiting',
  ],
  startUrl: '/agents',
  maxActions: 30,
  expectedOutcome: 'Research results, findings, or a generated report visible on screen',
  successCriteria: [
    {
      description: 'Research results are visible on the page',
      check: { check: 'url_contains', expected: '/agents' },
    },
  ],
  category: 'ai_agent',
  tags: ['ai-brain', 'llm-pipeline', 'agent'],
  qaProfile: 'neurareport',
}

export const dataAnalystAgentScenario: TestScenario = {
  id: 'agent-002-data-analyst',
  name: 'Get data analysis from the AI',
  goal: `You want the AI to analyze some data and give you insights.

Find the Data Analysis Agent, ask it a question about data, provide some sample data,
and get analysis results back. You should see insights or analysis text on screen
before you're done.`,
  hints: [
    'The data analyst may have fields for a question and for data input',
    'Try asking: "What trends do you see?"',
    'For sample data, try: [{"month":"Jan","sales":100},{"month":"Feb","sales":150}]',
  ],
  startUrl: '/agents',
  maxActions: 30,
  expectedOutcome: 'Data analysis insights or charts visible on screen',
  successCriteria: [
    {
      description: 'Data analysis results are visible on the page',
      check: { check: 'url_contains', expected: '/agents' },
    },
  ],
  category: 'ai_agent',
  tags: ['ai-brain', 'llm-pipeline', 'agent'],
  persona: 'impatient', // Upgrade #7: impatient user — expects quick results
  qaProfile: 'neurareport',
}

// ═════════════════════════════════════════════════════════════════════
// NAVIGATION & EXPLORATION
// ═════════════════════════════════════════════════════════════════════

export const fullNavigationScenario: TestScenario = {
  id: 'nav-001-full',
  name: 'Visit every major section of the app',
  goal: `Check that the app's main sections all load properly.

Using the sidebar, visit at least 5 different pages:
Dashboard, Connections, Templates, Reports, Agents, Query, Settings.
For each page, make sure it actually loads with real content (not an error).

Say done after visiting 5+ pages.`,
  hints: [
    'The sidebar on the left has links to all major sections',
    'Each page should have a heading or content that confirms it loaded',
  ],
  startUrl: '/',
  maxActions: 35,
  expectedOutcome: 'Multiple pages visited, all loading with content (no error screens)',
  successCriteria: [
    {
      description: 'Multiple pages were visited',
      check: { check: 'url_contains', expected: '/' },
    },
  ],
  category: 'navigation',
  tags: ['smoke-test'],
  qaProfile: 'general-purpose',
}

// ═════════════════════════════════════════════════════════════════════
// FULL E2E WORKFLOW
// ═════════════════════════════════════════════════════════════════════

export const fullWorkflowScenario: TestScenario = {
  id: 'workflow-001-full-e2e',
  name: 'Full workflow: Connection → Template → Report',
  goal: `Complete the full report generation workflow.

You want to generate a report. To do that you need:
1. A database connection — create one named "Workflow Test DB" (SQLite, path: backend/testdata/sample.db)
2. A template — find an existing one
3. Generate a report using the connection and template

Navigate through the app using the sidebar. When done, you should have created
a connection and at least attempted to generate a report.`,
  hints: [
    'Start with Connections, then Templates, then Reports',
    'Use the sidebar to navigate between sections',
    'The report generation page lets you pick a template and a data source',
  ],
  startUrl: '/connections',
  maxActions: 50,
  expectedOutcome: 'Connection created, template selected, report generation attempted or completed',
  successCriteria: [
    {
      description: 'Connection "Workflow Test DB" was created',
      check: { check: 'text_contains', expected: 'Workflow Test DB' },
    },
  ],
  category: 'workflow',
  tags: ['e2e', 'full-workflow', 'critical-path'],
  qaProfile: 'neurareport',
}

// ═════════════════════════════════════════════════════════════════════
// COMPREHENSIVE AUDIT
// ═════════════════════════════════════════════════════════════════════

export const ALL_ROUTES = [
  '/', '/dashboard', '/connections', '/templates', '/reports',
  '/schedules', '/jobs', '/activity', '/history', '/settings',
  '/query', '/enrichment', '/federation', '/synthesis', '/docqa',
  '/summary', '/documents', '/spreadsheets', '/dashboard-builder',
  '/connectors', '/workflows', '/agents', '/search', '/visualization',
  '/knowledge', '/design', '/ingestion', '/analyze', '/stats', '/ops',
  '/setup/wizard', '/analyze/legacy',
]

export const comprehensiveAuditScenario: TestScenario = {
  id: 'audit-001-all-pages',
  name: 'Comprehensive app audit',
  goal: `You're a QA tester checking every page in the app.

Visit as many pages as possible using the sidebar. On each page:
- Does it load? Is there content or just errors?
- What buttons are available? Click a few and see what happens.
- Any forms? Try filling one in.
- Anything confusing or broken?

Pages: ${ALL_ROUTES.join(', ')}

Report what works and what doesn't.`,
  hints: [
    'Use the sidebar to move between pages',
    'If a button opens a dialog, explore it then close it',
    'Skip "Notifications" buttons',
  ],
  startUrl: '/',
  maxActions: 500,
  successCriteria: [
    {
      description: 'Multiple pages were visited and tested',
      check: { check: 'text_contains', expected: 'Dashboard' },
    },
  ],
  category: 'navigation',
  tags: ['comprehensive-audit', 'full-coverage'],
  qaProfile: 'general-purpose',
}

/** Per-page audit scenarios */
export function generatePerPageScenarios(): TestScenario[] {
  return ALL_ROUTES.map((route, i) => ({
    id: `page-audit-${String(i).padStart(3, '0')}-${route.replace(/\//g, '') || 'home'}`,
    name: `Page Audit: ${route}`,
    goal: `You're testing the ${route} page.

Click every button, tab, and link you can find. For each one:
- What does it do? Open a dialog? Navigate? Show data?
- If a dialog opens, look inside it then close it.
- Fill any forms with test data.
- Scroll down to find hidden elements.
Report what works and what's broken.`,
    hints: [
      'Skip "Notifications" buttons',
      'Press Escape to close overlays',
      'Scroll down — there may be content below the fold',
    ],
    startUrl: route,
    maxActions: 100,
    successCriteria: [
      {
        description: `Page ${route} was tested`,
        check: { check: 'url_contains', expected: route === '/' ? 'dashboard' : route },
      },
    ],
    category: 'navigation' as const,
    tags: ['per-page-audit', 'comprehensive'],
    qaProfile: 'general-purpose' as const,
  }))
}

// ─── Export ──────────────────────────────────────────────────────────

export const ALL_SCENARIOS: TestScenario[] = [
  createConnectionScenario,
  testConnectionScenario,
  browseTemplatesScenario,
  researchAgentScenario,
  dataAnalystAgentScenario,
  exploreTemplatesScenario,
  fullNavigationScenario,
  fullWorkflowScenario,
  comprehensiveAuditScenario,
]

export function getAllScenariosWithPageAudits(): TestScenario[] {
  return [...ALL_SCENARIOS, ...generatePerPageScenarios()]
}

export function getScenariosByCategory(category: TestScenario['category']): TestScenario[] {
  return ALL_SCENARIOS.filter(s => s.category === category)
}

export function getScenariosByTag(tag: string): TestScenario[] {
  return ALL_SCENARIOS.filter(s => s.tags?.includes(tag))
}

export function getAIBrainScenarios(): TestScenario[] {
  return getScenariosByTag('ai-brain')
}
