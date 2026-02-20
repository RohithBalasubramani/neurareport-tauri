/**
 * Configuration for the NeuraReport AI Test Agent.
 *
 * This is a simplified config tailored for NeuraReport's MUI-based UI.
 * For the general-purpose agent, see packages/ai-qa-agent/src/config.ts
 */
import type { PersonaModifier } from './types'

// ─── LLM Configuration ───────────────────────────────────────────────

export interface LLMConfig {
  /** Model to use (sonnet, opus, haiku) */
  model: string
  /** Maximum tokens for response */
  maxTokens?: number
  /** Timeout for LLM calls in ms */
  timeout?: number
  /** Whether to use vision (screenshots) */
  useVision?: boolean
}

// ─── Agent Configuration ─────────────────────────────────────────────

export interface AgentConfig {
  /** Name of the application being tested */
  appName: string
  /** Base URL of the application */
  baseUrl: string
  /** Backend API base URL */
  apiBaseUrl?: string
  /** LLM configuration */
  llm: LLMConfig
  /** Directory for cross-session learning data */
  learningDir?: string
  /** Whether to take screenshots at every step */
  screenshotEveryStep?: boolean
  /** Delay between actions in ms */
  actionDelay?: number
  /** Default persona for tests */
  defaultPersona?: PersonaModifier
  /** Enable debug logging */
  debug?: boolean
  /** Page load timeout in ms */
  pageLoadTimeout?: number
  /** Action timeout in ms */
  actionTimeout?: number
  /** Maximum elements to include in observation */
  maxElementsInObservation?: number

  // ─── Failure Mode Mitigation Settings ────────────────────────────────

  /** Enable post-action verification (checks if action had expected effect) */
  verifyAfterAction?: boolean
  /** Wait for page stability before observing */
  waitForStable?: boolean
  /** Maximum time to wait for page stability in ms */
  stabilityTimeout?: number
  /** Detect and warn on repeated identical actions */
  detectActionReplay?: boolean
  /** Maximum identical actions before forcing abort */
  maxRepeatedActions?: number
  /** Enable deterministic mode for reproducible tests */
  deterministicMode?: boolean
  /** Random seed for deterministic mode */
  randomSeed?: number
}

// ─── Default Configuration ───────────────────────────────────────────

export const DEFAULT_CONFIG: AgentConfig = {
  appName: 'NeuraReport',
  baseUrl: process.env.BASE_URL || 'http://localhost:5174',
  apiBaseUrl: process.env.BACKEND_URL || 'http://127.0.0.1:8001',
  llm: {
    model: process.env.AI_TEST_MODEL || 'sonnet',
    maxTokens: 1024,
    timeout: 600_000, // 10 minutes
    useVision: true,
  },
  screenshotEveryStep: true,
  actionDelay: 500,
  defaultPersona: 'default',
  debug: false,
  pageLoadTimeout: 30_000,
  actionTimeout: 10_000,
  maxElementsInObservation: 100,

  // Failure mode mitigations (all enabled by default)
  verifyAfterAction: true,
  waitForStable: true,
  stabilityTimeout: 5_000,
  detectActionReplay: true,
  maxRepeatedActions: 3,
  deterministicMode: false,
  randomSeed: undefined,
}

/**
 * Create a config by merging with defaults
 */
export function createConfig(overrides: Partial<AgentConfig> = {}): AgentConfig {
  return {
    ...DEFAULT_CONFIG,
    ...overrides,
    llm: {
      ...DEFAULT_CONFIG.llm,
      ...overrides.llm,
    },
  }
}
