/**
 * Workflow Builder Page Container
 * Visual workflow automation builder.
 */
import React from 'react'
import { Alert } from '@mui/material'
import { useWorkflowBuilderState } from '../hooks/useWorkflowBuilderState'
import { PageContainer, WorkflowArea } from '../components/WorkflowStyledComponents'
import WorkflowToolbar from '../components/WorkflowToolbar'
import WorkflowNodePalettePanel from '../components/WorkflowNodePalettePanel'
import WorkflowCanvas from '../components/WorkflowCanvas'
import ExecutionsSidebar from '../components/ExecutionsSidebar'
import WorkflowEmptyState from '../components/WorkflowEmptyState'
import CreateWorkflowDialog from '../components/CreateWorkflowDialog'

export default function WorkflowBuilderPage() {
  const state = useWorkflowBuilderState()

  return (
    <PageContainer>
      <WorkflowToolbar
        currentWorkflow={state.currentWorkflow}
        workflowNodes={state.workflowNodes}
        executing={state.executing}
        onToggleExecutions={state.handleToggleExecutions}
        onExecute={state.handleExecute}
        onSave={state.handleSaveWorkflow}
        onOpenCreateDialog={state.handleOpenCreateDialog}
      />

      <WorkflowArea>
        {state.currentWorkflow ? (
          <>
            <WorkflowNodePalettePanel
              onAddNode={state.handleAddNode}
              pendingApprovals={state.pendingApprovals}
              onApproveStep={state.handleApproveStep}
              onRejectStep={state.handleRejectStep}
            />

            <WorkflowCanvas
              workflowNodes={state.workflowNodes}
              selectedNode={state.selectedNode}
              onSelectNode={state.handleSelectNode}
              onDeleteNode={state.handleDeleteNode}
            />

            {state.showExecutions && (
              <ExecutionsSidebar
                executions={state.executions}
                onCancelExecution={state.handleCancelExecution}
                onRetryExecution={state.handleRetryExecution}
              />
            )}
          </>
        ) : (
          <WorkflowEmptyState
            workflows={state.workflows}
            onOpenCreateDialog={state.handleOpenCreateDialog}
            onSelectWorkflow={state.handleSelectWorkflow}
          />
        )}
      </WorkflowArea>

      <CreateWorkflowDialog
        open={state.createDialogOpen}
        onClose={state.handleCloseCreateDialog}
        workflowName={state.newWorkflowName}
        onWorkflowNameChange={state.setNewWorkflowName}
        selectedConnectionId={state.selectedConnectionId}
        onConnectionChange={state.setSelectedConnectionId}
        selectedTemplateId={state.selectedTemplateId}
        onTemplateChange={state.setSelectedTemplateId}
        onCreateWorkflow={state.handleCreateWorkflow}
        loading={state.loading}
      />

      {state.error && (
        <Alert
          severity="error"
          onClose={state.handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {state.error}
        </Alert>
      )}
    </PageContainer>
  )
}
