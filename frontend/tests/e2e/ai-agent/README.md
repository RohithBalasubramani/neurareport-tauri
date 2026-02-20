# AI Agent Testing System

An LLM-driven browser testing framework that acts like a human test engineer.
Instead of scripted test steps, a Claude AI agent sees the browser screen,
decides what to click/type, and verifies results autonomously.

## Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌──────────────┐
│  Test Scenario   │────▶│  Agent Brain   │────▶│ Browser Agent │
│  (goal + hints)  │     │  (Claude API)  │     │ (Playwright)  │
└─────────────────┘     └───────┬───────┘     └──────┬───────┘
                                │                     │
                         decides action          executes it
                                │                     │
                                ▼                     ▼
                        ┌───────────────┐     ┌──────────────┐
                        │  LLM Decision  │     │  Page State   │
                        │  (JSON action) │     │ (screenshot + │
                        └───────────────┘     │  DOM + APIs)  │
                                              └──────────────┘
```

## Quick Start

```bash
# Ensure Claude Code CLI is installed and authenticated
# npm install -g @anthropic-ai/claude-code
# claude auth login

# Ensure frontend + backend are running
# Frontend: cd frontend && npx vite preview --port 5174
# Backend:  cd .. && python -c "from backend.api import app; ..."

# Run all AI agent tests
npx playwright test ai-agent-test.spec.ts

# Run specific categories
npx playwright test ai-agent-test.spec.ts --grep "connection"
npx playwright test ai-agent-test.spec.ts --grep "ai-brain"
npx playwright test ai-agent-test.spec.ts --grep "audit"
npx playwright test ai-agent-test.spec.ts --grep "e2e"

# Run the comprehensive audit (visits all 30 pages)
npx playwright test ai-agent-test.spec.ts --grep "comprehensive"

# Run full suite with aggregate report
npx playwright test ai-agent-test.spec.ts --grep "full-suite"
```

## Test Categories

| Category | Scenarios | What it tests |
|----------|-----------|---------------|
| **connection** | Create, Test | Database connection CRUD |
| **template** | Browse, Verify | Template management |
| **report** | Generate | Full report generation pipeline |
| **nl2sql** | Basic, Complex | AI query generation from natural language |
| **ai_agent** | Research, Data Analysis | AI agent pipelines |
| **schedule** | Create | Report scheduling |
| **navigation** | Full nav, Per-page audit | All 30 pages |
| **workflow** | Connection → Template → Report | Full E2E |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_TEST_MODEL` | `sonnet` | Claude model alias or full model ID |
| `BASE_URL` | `http://127.0.0.1:5174` | Frontend URL |
| `BACKEND_URL` | `http://127.0.0.1:8001` | Backend API URL |
| `AI_TEST_SCENARIOS` | (all) | Comma-separated scenario IDs |

## Agent Profiles

- `frontend/tests/e2e/ai-agent/` defaults to `qaProfile: "neurareport"` and applies NeuraReport-specific policy hints.
- `packages/ai-qa-agent/` defaults to `qaProfile: "general-purpose"` and stays framework-agnostic.
- Any scenario can override profile via `qaProfile: "neurareport" | "general-purpose"`.

## Evidence Output

All evidence is saved to `tests/e2e/evidence/ai-agent/`:
- **Screenshots**: Before/after each action
- **Network captures**: All API calls
- **LLM conversations**: Full reasoning trail
- **Action logs**: Every decision and result
- **Aggregate reports**: Summary of all scenarios

## How It Works

1. A **TestScenario** defines a high-level goal (e.g., "Create a database connection")
2. The **AgentBrain** (Claude) receives the current page state and decides the next action
3. The **BrowserAgent** (Playwright) executes the action and reports the result
4. The loop continues until the goal is achieved or max actions reached
5. **Success criteria** are evaluated against the final page state
6. **Backend checks** verify the API/LLM pipeline directly

## Adding New Scenarios

Add to `scenarios/index.ts`:

```typescript
export const myScenario: TestScenario = {
  id: 'my-001',
  name: 'My test scenario',
  goal: 'Describe what the AI agent should do...',
  startUrl: '/my-page',
  maxActions: 25,
  successCriteria: [{
    description: 'Expected outcome',
    check: { check: 'text_contains', expected: 'success' },
  }],
  category: 'workflow',
}
```
