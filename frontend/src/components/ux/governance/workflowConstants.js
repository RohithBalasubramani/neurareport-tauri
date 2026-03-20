/**
 * Workflow Contract Constants and Definitions
 */

// ============================================================================
// STEP STATUS
// ============================================================================

export const StepStatus = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  SKIPPED: 'skipped', // Only allowed if step is optional
}

// ============================================================================
// WORKFLOW CONTRACTS
// ============================================================================

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
// VALIDATION UTILITY
// ============================================================================

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
