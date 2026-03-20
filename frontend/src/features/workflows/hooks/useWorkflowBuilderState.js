/**
 * Custom hook: all state + effects + handlers for WorkflowBuilderPage
 */
import { useState, useEffect, useCallback } from 'react'
import useWorkflowStore from '@/stores/workflowStore'
import useSharedData from '@/hooks/useSharedData'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useWorkflowBuilderState() {
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    workflows,
    currentWorkflow,
    executions,
    currentExecution,
    pendingApprovals,
    loading,
    executing,
    error,
    fetchWorkflows,
    createWorkflow,
    getWorkflow,
    updateWorkflow,
    deleteWorkflow,
    executeWorkflow,
    fetchExecutions,
    cancelExecution,
    retryExecution,
    fetchPendingApprovals,
    approveStep,
    rejectStep,
    reset,
  } = useWorkflowStore()

  const { connections, templates, activeConnectionId } = useSharedData()

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newWorkflowName, setNewWorkflowName] = useState('')
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId || '')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [workflowNodes, setWorkflowNodes] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [showExecutions, setShowExecutions] = useState(false)

  useEffect(() => {
    fetchWorkflows()
    fetchPendingApprovals()
    return () => reset()
  }, [fetchWorkflows, fetchPendingApprovals, reset])

  useEffect(() => {
    if (currentWorkflow?.nodes) {
      setWorkflowNodes(currentWorkflow.nodes)
    }
  }, [currentWorkflow])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'workflows', ...intent },
      action,
    })
  }, [execute])

  const handleOpenCreateDialog = useCallback(() => {
    return executeUI('Open create workflow', () => setCreateDialogOpen(true))
  }, [executeUI])

  const handleCloseCreateDialog = useCallback(() => {
    return executeUI('Close create workflow', () => setCreateDialogOpen(false))
  }, [executeUI])

  const handleCreateWorkflow = useCallback(() => {
    if (!newWorkflowName) return undefined
    return execute({
      type: InteractionType.CREATE,
      label: 'Create workflow',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', name: newWorkflowName },
      action: async () => {
        const workflow = await createWorkflow({
          name: newWorkflowName,
          connectionId: selectedConnectionId || undefined,
          templateId: selectedTemplateId || undefined,
          nodes: [],
          edges: [],
          triggers: [],
        })
        if (workflow) {
          setCreateDialogOpen(false)
          setNewWorkflowName('')
          setSelectedConnectionId(activeConnectionId || '')
          setSelectedTemplateId('')
          toast.show('Workflow created', 'success')
        }
        return workflow
      },
    })
  }, [activeConnectionId, createWorkflow, execute, newWorkflowName, selectedConnectionId, selectedTemplateId, toast])

  const handleAddNode = useCallback((nodeType) => {
    if (!currentWorkflow) return undefined
    return executeUI('Add workflow node', () => {
      const newNode = {
        id: `node_${Date.now()}`,
        type: nodeType.type,
        label: nodeType.label,
        config: {},
        position: { x: 100 + workflowNodes.length * 50, y: 100 + workflowNodes.length * 50 },
      }
      setWorkflowNodes([...workflowNodes, newNode])
      toast.show(`${nodeType.label} node added`, 'success')
    }, { workflowId: currentWorkflow.id, nodeType: nodeType.type })
  }, [currentWorkflow, executeUI, toast, workflowNodes])

  const handleDeleteNode = useCallback((nodeId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Remove workflow node',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', nodeId },
      action: async () => {
        setWorkflowNodes(workflowNodes.filter((n) => n.id !== nodeId))
        if (selectedNode?.id === nodeId) {
          setSelectedNode(null)
        }
        toast.show('Node removed', 'success')
      },
    })
  }, [execute, selectedNode?.id, toast, workflowNodes])

  const handleSelectNode = useCallback((node) => {
    return executeUI('Select workflow node', () => setSelectedNode(node), { nodeId: node?.id })
  }, [executeUI])

  const handleSaveWorkflow = useCallback(() => {
    if (!currentWorkflow) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Save workflow',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', workflowId: currentWorkflow.id },
      action: async () => {
        await updateWorkflow(currentWorkflow.id, {
          nodes: workflowNodes,
        })
        toast.show('Workflow saved', 'success')
      },
    })
  }, [currentWorkflow, execute, toast, updateWorkflow, workflowNodes])

  const handleExecute = useCallback(() => {
    if (!currentWorkflow) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Run workflow',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'workflows', workflowId: currentWorkflow.id },
      action: async () => {
        const execution = await executeWorkflow(currentWorkflow.id)
        if (execution) {
          toast.show('Workflow execution started', 'success')
          setShowExecutions(true)
          fetchExecutions(currentWorkflow.id)
        }
        return execution
      },
    })
  }, [currentWorkflow, execute, executeWorkflow, fetchExecutions, toast])

  const handleCancelExecution = useCallback((executionId) => {
    if (!currentWorkflow) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Cancel execution',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', workflowId: currentWorkflow.id, executionId },
      action: async () => {
        await cancelExecution(currentWorkflow.id, executionId)
        toast.show('Execution cancelled', 'info')
      },
    })
  }, [cancelExecution, currentWorkflow, execute, toast])

  const handleRetryExecution = useCallback((executionId) => {
    if (!currentWorkflow) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Retry execution',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', workflowId: currentWorkflow.id, executionId },
      action: async () => {
        await retryExecution(currentWorkflow.id, executionId)
        toast.show('Retry started', 'success')
      },
    })
  }, [currentWorkflow, execute, retryExecution, toast])

  const handleToggleExecutions = useCallback(() => {
    if (!currentWorkflow) return undefined
    return executeUI('Toggle executions', () => {
      const next = !showExecutions
      setShowExecutions(next)
      if (next) fetchExecutions(currentWorkflow.id)
    }, { workflowId: currentWorkflow.id, open: !showExecutions })
  }, [currentWorkflow, executeUI, fetchExecutions, showExecutions])

  const handleApproveStep = useCallback((executionId, stepId) => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Approve step',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', executionId, stepId },
      action: async () => {
        await approveStep(executionId, stepId)
      },
    })
  }, [approveStep, execute])

  const handleRejectStep = useCallback((executionId, stepId) => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Reject step',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'workflows', executionId, stepId },
      action: async () => {
        await rejectStep(executionId, stepId, 'Rejected')
      },
    })
  }, [execute, rejectStep])

  const handleSelectWorkflow = useCallback((workflowId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Open workflow',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'workflows', workflowId },
      action: async () => {
        await getWorkflow(workflowId)
      },
    })
  }, [execute, getWorkflow])

  const handleDismissError = useCallback(() => {
    return executeUI('Dismiss workflow error', () => reset())
  }, [executeUI, reset])

  return {
    // Store state
    workflows,
    currentWorkflow,
    executions,
    pendingApprovals,
    loading,
    executing,
    error,

    // Local state
    createDialogOpen,
    newWorkflowName,
    setNewWorkflowName,
    selectedConnectionId,
    setSelectedConnectionId,
    selectedTemplateId,
    setSelectedTemplateId,
    workflowNodes,
    selectedNode,
    showExecutions,

    // Shared data
    activeConnectionId,

    // Handlers
    handleOpenCreateDialog,
    handleCloseCreateDialog,
    handleCreateWorkflow,
    handleAddNode,
    handleDeleteNode,
    handleSelectNode,
    handleSaveWorkflow,
    handleExecute,
    handleCancelExecution,
    handleRetryExecution,
    handleToggleExecutions,
    handleApproveStep,
    handleRejectStep,
    handleSelectWorkflow,
    handleDismissError,
  }
}
