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
import { createContext, useContext, useCallback, useReducer, useEffect } from 'react'
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Box,
  Typography,
  Button,
  Alert,
  Paper,
  useTheme,
  alpha,
} from '@mui/material'
import {
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  RadioButtonUnchecked as PendingIcon,
  HourglassEmpty as InProgressIcon,
} from '@mui/icons-material'

// ============================================================================
// WORKFLOW DEFINITIONS
// ============================================================================

/**
 * Step status values
 */
export const StepStatus = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  SKIPPED: 'skipped', // Only allowed if step is optional
}

/**
 * Pre-defined workflow contracts
 * Each workflow defines steps, their order, and requirements
 */
export const WorkflowContracts = {
  // Document Q&A Workflow
  DOCUMENT_QA: {
    id: 'document_qa',
    name: 'Document Q&A',
    description: 'Upload documents and ask questions',
    steps: [
      {
        id: 'create_session',
        name: 'Create Session',
        description: 'Create a new Q&A session',
        required: true,
        interactionType: 'CREATE',
        canRevert: true,
      },
      {
        id: 'add_documents',
        name: 'Add Documents',
        description: 'Upload at least one document',
        required: true,
        interactionType: 'UPLOAD',
        canRevert: true,
        minCount: 1,
      },
      {
        id: 'ask_question',
        name: 'Ask Questions',
        description: 'Ask questions about your documents',
        required: false,
        interactionType: 'ANALYZE',
        canRevert: false,
        repeatable: true,
      },
    ],
    onComplete: 'Session ready for Q&A',
    onAbandon: 'Session can be resumed later',
  },

  // Query Builder Workflow
  QUERY_BUILDER: {
    id: 'query_builder',
    name: 'Query Builder',
    description: 'Generate and execute SQL queries',
    steps: [
      {
        id: 'select_connection',
        name: 'Select Connection',
        description: 'Choose a database connection',
        required: true,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'enter_question',
        name: 'Enter Question',
        description: 'Describe what you want to query',
        required: true,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'generate_sql',
        name: 'Generate SQL',
        description: 'AI generates the SQL query',
        required: true,
        interactionType: 'GENERATE',
        canRevert: true,
      },
      {
        id: 'review_sql',
        name: 'Review SQL',
        description: 'Review and optionally edit the generated SQL',
        required: false,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'execute_query',
        name: 'Execute Query',
        description: 'Run the query against the database',
        required: false,
        interactionType: 'EXECUTE',
        canRevert: false,
      },
    ],
    onComplete: 'Query executed successfully',
    onAbandon: 'Query can be saved for later',
  },

  // Synthesis Workflow
  SYNTHESIS: {
    id: 'synthesis',
    name: 'Document Synthesis',
    description: 'Combine and analyze multiple documents',
    steps: [
      {
        id: 'create_session',
        name: 'Create Session',
        description: 'Create a synthesis session',
        required: true,
        interactionType: 'CREATE',
        canRevert: true,
      },
      {
        id: 'add_documents',
        name: 'Add Documents',
        description: 'Add at least 2 documents',
        required: true,
        interactionType: 'UPLOAD',
        canRevert: true,
        minCount: 2,
      },
      {
        id: 'configure_options',
        name: 'Configure Options',
        description: 'Set output format and focus topics',
        required: false,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'run_analysis',
        name: 'Run Analysis',
        description: 'Find inconsistencies or synthesize',
        required: true,
        interactionType: 'GENERATE',
        canRevert: false,
      },
    ],
    onComplete: 'Synthesis complete',
    onAbandon: 'Session saved for later',
  },

  // Report Generation Workflow
  REPORT_GENERATION: {
    id: 'report_generation',
    name: 'Report Generation',
    description: 'Generate a report from template',
    steps: [
      {
        id: 'select_template',
        name: 'Select Template',
        description: 'Choose a report template',
        required: true,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'select_connection',
        name: 'Select Data Source',
        description: 'Choose data connection',
        required: true,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'configure_parameters',
        name: 'Configure Parameters',
        description: 'Set report parameters',
        required: false,
        interactionType: 'UPDATE',
        canRevert: true,
      },
      {
        id: 'generate_report',
        name: 'Generate Report',
        description: 'Create the report',
        required: true,
        interactionType: 'GENERATE',
        canRevert: false,
      },
      {
        id: 'export_report',
        name: 'Export Report',
        description: 'Download or share the report',
        required: false,
        interactionType: 'DOWNLOAD',
        canRevert: false,
      },
    ],
    onComplete: 'Report generated',
    onAbandon: 'Configuration saved',
  },
}

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
      const step = state.contract.steps[stepIndex]

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
        // Step needs more iterations
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
      // Validate all required steps are complete
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
// CONTEXT
// ============================================================================

const WorkflowContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function WorkflowContractProvider({ children }) {
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
          // Restore step states
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

  const contextValue = {
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
    WorkflowContracts,
    StepStatus,
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
    status: stepState?.status || StepStatus.PENDING,
    data: stepState?.data,
    error: stepState?.error,
    count: stepState?.count || 0,
    start,
    complete,
    fail,
    revert,
    canRevert: step?.canRevert && stepState?.status === StepStatus.COMPLETED,
    isRequired: step?.required,
  }
}

// ============================================================================
// WORKFLOW PROGRESS COMPONENT
// ============================================================================

export function WorkflowProgress({ compact = false }) {
  const theme = useTheme()
  const { contract, stepStates, currentStepIndex } = useWorkflow()

  if (!contract) return null

  const getStepIcon = (status) => {
    switch (status) {
      case StepStatus.COMPLETED:
        return <CompleteIcon sx={{ color: 'text.secondary' }} />
      case StepStatus.FAILED:
        return <ErrorIcon sx={{ color: 'text.secondary' }} />
      case StepStatus.IN_PROGRESS:
        return <InProgressIcon sx={{ color: 'text.secondary' }} />
      default:
        return <PendingIcon sx={{ color: theme.palette.text.disabled }} />
    }
  }

  if (compact) {
    const completedCount = contract.steps.filter(
      (s) => stepStates[s.id]?.status === StepStatus.COMPLETED
    ).length

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {contract.name}:
        </Typography>
        <Typography variant="caption" fontWeight={600}>
          {completedCount}/{contract.steps.length} steps
        </Typography>
      </Box>
    )
  }

  return (
    <Paper
      sx={{
        p: 2,
        bgcolor: alpha(theme.palette.background.paper, 0.8),
        borderRadius: 1,  // Figma spec: 8px
      }}
    >
      <Typography variant="subtitle2" gutterBottom>
        {contract.name}
      </Typography>
      <Stepper activeStep={currentStepIndex} orientation="vertical">
        {contract.steps.map((step) => {
          const stepState = stepStates[step.id]
          return (
            <Step key={step.id} completed={stepState?.status === StepStatus.COMPLETED}>
              <StepLabel
                icon={getStepIcon(stepState?.status)}
                optional={!step.required && (
                  <Typography variant="caption">Optional</Typography>
                )}
              >
                {step.name}
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
                {stepState?.error && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {stepState.error}
                  </Alert>
                )}
              </StepContent>
            </Step>
          )
        })}
      </Stepper>
    </Paper>
  )
}

/**
 * Validate that a step transition is allowed
 * THROWS if invalid
 */
export function validateStepTransition(contract, stepStates, fromStepId, toStepId) {
  const fromIndex = contract.steps.findIndex((s) => s.id === fromStepId)
  const toIndex = contract.steps.findIndex((s) => s.id === toStepId)

  if (toIndex < fromIndex) {
    // Going backwards - check if revert is allowed
    const toStep = contract.steps[toIndex]
    if (!toStep.canRevert) {
      throw new Error(`[WORKFLOW VIOLATION] Cannot go back to "${toStepId}" - step is not revertible`)
    }
  } else if (toIndex > fromIndex + 1) {
    // Skipping steps - check if all skipped are optional
    for (let i = fromIndex + 1; i < toIndex; i++) {
      const skippedStep = contract.steps[i]
      if (skippedStep.required) {
        throw new Error(`[WORKFLOW VIOLATION] Cannot skip required step "${skippedStep.id}"`)
      }
    }
  }

  return true
}
