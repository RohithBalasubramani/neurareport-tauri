/**
 * UX Governance System (Level 1 + Level 2)
 *
 * LEVEL 1 - Interaction Governance:
 * - No interaction can exist without full UX guarantees
 * - No developer can bypass interaction safety
 * - No backend action can occur without UX context
 *
 * LEVEL 2 - Extended Governance:
 * - Time expectations and escalation for all operations
 * - Workflow contracts spanning multiple interactions
 * - Background operations visibility
 * - CI/runtime guards for regression prevention
 *
 * VIOLATIONS FAIL FAST - no advisory systems.
 *
 * USAGE:
 * 1. Wrap your app with <UXGovernanceProvider>
 * 2. Use useInteraction() for ALL user-triggered actions
 * 3. Use useConfirmedAction() for irreversible actions
 * 4. Use useNavigationSafety() for navigation guards
 * 5. Use useTimeExpectations() for operation timing
 * 6. Use useWorkflow() for multi-step operations
 * 7. Use useBackgroundOperations() for background task visibility
 */

// Core Interaction API
export {
  InteractionProvider,
  useInteraction,
  useNavigateInteraction,
  InteractionType,
  Reversibility,
  FeedbackType,
} from './InteractionAPI'

// Intent System (UI -> Backend -> Audit)
export {
  IntentProvider,
  useIntent,
  IntentStatus,
  createIntent,
  createIntentHeaders,
} from './IntentSystem'

// Navigation Safety
export {
  NavigationSafetyProvider,
  useNavigationSafety,
  useOperationBlocker,
  useUnsavedChangesBlocker,
  BlockerType,
} from './NavigationSafety'

// Irreversible Action Boundaries
export {
  IrreversibleBoundaryProvider,
  useIrreversibleAction,
  useConfirmedAction,
  IrreversibleActions,
  ActionSeverity,
} from './IrreversibleBoundaries'

// Level-2: Time Expectations
export {
  TimeExpectationProvider,
  useTimeExpectations,
  useTrackedOperation,
  TimeExpectations,
  OperationTimeMap,
  EscalationLevel,
  validateTimeExpectation,
} from './TimeExpectations'

// Level-2: Workflow Contracts
export {
  WorkflowContractProvider,
  useWorkflow,
  useWorkflowStep,
  WorkflowContracts,
  StepStatus,
  WorkflowProgress,
} from './WorkflowContracts'

// Level-2: Background Operations
export {
  BackgroundOperationsProvider,
  useBackgroundOperations,
  useBackgroundTask,
  BackgroundOperationType,
  BackgroundOperationStatus,
  BackgroundTasksButton,
} from './BackgroundOperations'

// Level-2: Regression Guards
export {
  VIOLATION_PATTERNS,
  REQUIRED_PATTERNS,
  guardAgainstViolations,
  validateComponentCompliance,
  runCIGovernanceCheck,
  formatCIResults,
  useGovernanceValidation,
  ESLINT_RULES,
} from './RegressionGuards'

// Combined Provider for convenience
import { InteractionProvider } from './InteractionAPI'
import { IntentProvider } from './IntentSystem'
import { NavigationSafetyProvider } from './NavigationSafety'
import { IrreversibleBoundaryProvider } from './IrreversibleBoundaries'
import { TimeExpectationProvider } from './TimeExpectations'
import { WorkflowContractProvider } from './WorkflowContracts'
import { BackgroundOperationsProvider } from './BackgroundOperations'

/**
 * Combined UX Governance Provider (Level 1 + Level 2)
 * Wraps all governance contexts in the correct order
 */
export function UXGovernanceProvider({ children, auditClient }) {
  return (
    <IntentProvider auditClient={auditClient}>
      <TimeExpectationProvider>
        <WorkflowContractProvider>
          <BackgroundOperationsProvider>
            <NavigationSafetyProvider>
              <IrreversibleBoundaryProvider>
                <InteractionProvider>
                  {children}
                </InteractionProvider>
              </IrreversibleBoundaryProvider>
            </NavigationSafetyProvider>
          </BackgroundOperationsProvider>
        </WorkflowContractProvider>
      </TimeExpectationProvider>
    </IntentProvider>
  )
}

// Enforcement utilities
export {
  useEnforceGovernance,
  withGovernanceWarning,
  createGovernedHandler,
  validateContract,
  generateComplianceReport,
  resetEnforcement,
} from './useEnforcement'

// Development-time enforcement helpers
export { GovernanceEnforcement } from './GovernanceEnforcement'
