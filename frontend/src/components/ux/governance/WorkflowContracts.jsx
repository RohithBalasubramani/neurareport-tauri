/**
 * UX Governance Level-2: Workflow Contracts
 *
 * ENFORCES that:
 * - Multi-step workflows are explicitly defined
 * - Step ordering is enforced (can't skip steps)
 * - Workflow state is persisted and recoverable
 * - Partial completion is handled gracefully
 * - Users always know where they are in a workflow
 *
 * VIOLATIONS FAIL FAST - invalid workflow transitions throw errors.
 */
import { createContext, useContext, useCallback } from 'react'
import { useWorkflowProvider } from './hooks/useWorkflowProvider'
import { WorkflowContracts as WorkflowContractDefs, StepStatus as StepStatusEnum } from './workflowConstants'

// Re-export constants for backwards compatibility
export { StepStatus, WorkflowContracts, validateStepTransition } from './workflowConstants'

// Re-export WorkflowProgress as named export (preserving original export name)
export { default as WorkflowProgress } from './WorkflowProgressView'

// ============================================================================
// CONTEXT
// ============================================================================

const WorkflowContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function WorkflowContractProvider({ children }) {
  const workflowState = useWorkflowProvider()

  const contextValue = {
    ...workflowState,
    WorkflowContracts: WorkflowContractDefs,
    StepStatus: StepStatusEnum,
  }

  return (
    <WorkflowContext.Provider value={contextValue}>
      {children}
    </WorkflowContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useWorkflow() {
  const context = useContext(WorkflowContext)
  if (!context) {
    throw new Error('useWorkflow must be used within WorkflowContractProvider')
  }
  return context
}

/**
 * Hook to manage a specific workflow step
 */
export function useWorkflowStep(stepId) {
  const { stepStates, advanceStep, completeStep, failStep, revertStep, contract } = useWorkflow()

  const step = contract?.steps.find((s) => s.id === stepId)
  const stepState = stepStates[stepId]

  const start = useCallback((data) => {
    advanceStep(stepId, data)
  }, [stepId, advanceStep])

  const complete = useCallback((data) => {
    completeStep(stepId, data)
  }, [stepId, completeStep])

  const fail = useCallback((error) => {
    failStep(stepId, error)
  }, [stepId, failStep])

  const revert = useCallback(() => {
    revertStep(stepId)
  }, [stepId, revertStep])

  return {
    step,
    status: stepState?.status || 'pending',
    data: stepState?.data,
    error: stepState?.error,
    count: stepState?.count || 0,
    start,
    complete,
    fail,
    revert,
    canRevert: step?.canRevert && stepState?.status === 'completed',
    isRequired: step?.required,
  }
}
