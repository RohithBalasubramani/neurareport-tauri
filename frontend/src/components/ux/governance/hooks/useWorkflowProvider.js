/**
 * Workflow Provider Hook
 *
 * Manages workflow state via reducer, persistence, and step transitions.
 */
import { useCallback, useReducer, useEffect } from 'react'
import { WorkflowContracts, StepStatus } from '../workflowConstants'

// ============================================================================
// WORKFLOW REDUCER
// ============================================================================

const workflowReducer = (state, action) => {
  switch (action.type) {
    case 'START_WORKFLOW': {
      const contract = WorkflowContracts[action.workflowId]
      if (!contract) {
        throw new Error(`[WORKFLOW VIOLATION] Unknown workflow: ${action.workflowId}`)
      }
      return {
        ...state,
        activeWorkflow: action.workflowId,
        contract,
        currentStepIndex: 0,
        stepStates: contract.steps.reduce((acc, step) => {
          acc[step.id] = { status: StepStatus.PENDING, data: null, error: null, count: 0 }
          return acc
        }, {}),
        startedAt: Date.now(),
        completedAt: null,
      }
    }

    case 'ADVANCE_STEP': {
      const { stepId, data } = action
      const stepIndex = state.contract.steps.findIndex((s) => s.id === stepId)

      if (stepIndex === -1) {
        throw new Error(`[WORKFLOW VIOLATION] Unknown step: ${stepId}`)
      }

      // Validate step ordering - can't skip required steps
      for (let i = 0; i < stepIndex; i++) {
        const prevStep = state.contract.steps[i]
        const prevState = state.stepStates[prevStep.id]
        if (prevStep.required && prevState.status !== StepStatus.COMPLETED) {
          throw new Error(
            `[WORKFLOW VIOLATION] Cannot advance to "${stepId}" - required step "${prevStep.id}" not completed`
          )
        }
      }

      const currentState = state.stepStates[stepId]

      return {
        ...state,
        currentStepIndex: stepIndex,
        stepStates: {
          ...state.stepStates,
          [stepId]: {
            ...currentState,
            status: StepStatus.IN_PROGRESS,
            data: data || currentState.data,
          },
        },
      }
    }

    case 'COMPLETE_STEP': {
      const { stepId, data } = action
      const currentState = state.stepStates[stepId]
      const step = state.contract.steps.find((s) => s.id === stepId)

      if (currentState.status !== StepStatus.IN_PROGRESS) {
        throw new Error(
          `[WORKFLOW VIOLATION] Cannot complete step "${stepId}" - not in progress (status: ${currentState.status})`
        )
      }

      // Check min count requirement
      const newCount = currentState.count + 1
      if (step.minCount && newCount < step.minCount) {
        return {
          ...state,
          stepStates: {
            ...state.stepStates,
            [stepId]: {
              ...currentState,
              status: step.repeatable ? StepStatus.IN_PROGRESS : StepStatus.PENDING,
              data: data || currentState.data,
              count: newCount,
            },
          },
        }
      }

      return {
        ...state,
        stepStates: {
          ...state.stepStates,
          [stepId]: {
            ...currentState,
            status: StepStatus.COMPLETED,
            data: data || currentState.data,
            count: newCount,
          },
        },
      }
    }

    case 'FAIL_STEP': {
      const { stepId, error } = action
      return {
        ...state,
        stepStates: {
          ...state.stepStates,
          [stepId]: {
            ...state.stepStates[stepId],
            status: StepStatus.FAILED,
            error,
          },
        },
      }
    }

    case 'REVERT_STEP': {
      const { stepId } = action
      const step = state.contract.steps.find((s) => s.id === stepId)

      if (!step.canRevert) {
        throw new Error(`[WORKFLOW VIOLATION] Step "${stepId}" cannot be reverted`)
      }

      return {
        ...state,
        stepStates: {
          ...state.stepStates,
          [stepId]: {
            status: StepStatus.PENDING,
            data: null,
            error: null,
            count: 0,
          },
        },
      }
    }

    case 'COMPLETE_WORKFLOW': {
      for (const step of state.contract.steps) {
        const stepState = state.stepStates[step.id]
        if (step.required && stepState.status !== StepStatus.COMPLETED) {
          throw new Error(
            `[WORKFLOW VIOLATION] Cannot complete workflow - required step "${step.id}" not completed`
          )
        }
      }

      return {
        ...state,
        completedAt: Date.now(),
      }
    }

    case 'ABANDON_WORKFLOW': {
      return {
        ...state,
        activeWorkflow: null,
        contract: null,
        stepStates: {},
        abandonedAt: Date.now(),
      }
    }

    case 'RESET':
      return {
        activeWorkflow: null,
        contract: null,
        currentStepIndex: 0,
        stepStates: {},
        startedAt: null,
        completedAt: null,
      }

    default:
      return state
  }
}

// ============================================================================
// HOOK
// ============================================================================

export function useWorkflowProvider() {
  const [state, dispatch] = useReducer(workflowReducer, {
    activeWorkflow: null,
    contract: null,
    currentStepIndex: 0,
    stepStates: {},
    startedAt: null,
    completedAt: null,
  })

  // Persist workflow state to sessionStorage
  useEffect(() => {
    if (state.activeWorkflow) {
      sessionStorage.setItem('ux_workflow_state', JSON.stringify(state))
    }
  }, [state])

  // Restore workflow state on mount
  useEffect(() => {
    const saved = sessionStorage.getItem('ux_workflow_state')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        if (parsed.activeWorkflow && WorkflowContracts[parsed.activeWorkflow]) {
          dispatch({ type: 'START_WORKFLOW', workflowId: parsed.activeWorkflow })
          Object.entries(parsed.stepStates || {}).forEach(([stepId, stepState]) => {
            if (stepState.status === StepStatus.COMPLETED) {
              dispatch({ type: 'ADVANCE_STEP', stepId, data: stepState.data })
              dispatch({ type: 'COMPLETE_STEP', stepId, data: stepState.data })
            }
          })
        }
      } catch (e) {
        console.warn('[WORKFLOW] Failed to restore workflow state:', e)
      }
    }
  }, [])

  const startWorkflow = useCallback((workflowId) => {
    dispatch({ type: 'START_WORKFLOW', workflowId })
  }, [])

  const advanceStep = useCallback((stepId, data) => {
    dispatch({ type: 'ADVANCE_STEP', stepId, data })
  }, [])

  const completeStep = useCallback((stepId, data) => {
    dispatch({ type: 'COMPLETE_STEP', stepId, data })
  }, [])

  const failStep = useCallback((stepId, error) => {
    dispatch({ type: 'FAIL_STEP', stepId, error })
  }, [])

  const revertStep = useCallback((stepId) => {
    dispatch({ type: 'REVERT_STEP', stepId })
  }, [])

  const completeWorkflow = useCallback(() => {
    dispatch({ type: 'COMPLETE_WORKFLOW' })
  }, [])

  const abandonWorkflow = useCallback(() => {
    sessionStorage.removeItem('ux_workflow_state')
    dispatch({ type: 'ABANDON_WORKFLOW' })
  }, [])

  const resetWorkflow = useCallback(() => {
    sessionStorage.removeItem('ux_workflow_state')
    dispatch({ type: 'RESET' })
  }, [])

  // Check if workflow is complete
  const isWorkflowComplete = state.contract?.steps.every((step) => {
    const stepState = state.stepStates[step.id]
    return !step.required || stepState?.status === StepStatus.COMPLETED
  })

  return {
    ...state,
    isWorkflowComplete,
    startWorkflow,
    advanceStep,
    completeStep,
    failStep,
    revertStep,
    completeWorkflow,
    abandonWorkflow,
    resetWorkflow,
  }
}
