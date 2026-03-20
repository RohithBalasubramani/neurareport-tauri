/**
 * Dashboard Builder Page Container
 * Drag-and-drop dashboard builder with react-grid-layout and ECharts.
 * Slim orchestrator — logic lives in useDashboardBuilder hook,
 * render sections in sub-components.
 */
import React from 'react'
import { Typography, Alert } from '@mui/material'
import { Dashboard as DashboardIcon, Add as AddIcon } from '@mui/icons-material'
import { useDashboardBuilder } from '../hooks/useDashboardBuilder'
import { PageContainer, MainContent, EmptyState, ActionButton } from '../components/DashboardBuilderStyles'
import DashboardSidebar from '../components/DashboardSidebar'
import DashboardToolbar from '../components/DashboardToolbar'
import DashboardCanvas from '../components/DashboardCanvas'
import CreateDashboardDialog from '../components/CreateDashboardDialog'
import AddWidgetDialog from '../components/AddWidgetDialog'
import AIAnalyticsMenu from '../components/AIAnalyticsMenu'

export default function DashboardBuilderPage() {
  const {
    dashboards, currentDashboard, widgets, insights,
    loading, saving, refreshing, error,
    createDialogOpen, newDashboardName, setNewDashboardName,
    addWidgetDialogOpen, pendingWidgetType, widgetTitle, setWidgetTitle,
    widgetChartType, setWidgetChartType, pendingVariant, setPendingVariant,
    aiMenuAnchor, localLayout, hasUnsavedChanges,
    selectedConnectionId, setSelectedConnectionId,
    handleOpenCreateDialog, handleCloseCreateDialog,
    handleSelectDashboard, handleCreateDashboard,
    handleAddWidgetFromPalette, handleCloseAddWidgetDialog, handleConfirmAddWidget,
    handleDeleteWidget, handleLayoutChange, handleSave, handleRefresh,
    handleOpenAiMenu, handleCloseAiMenu, handleAIAction,
    handleSnapshot, handleEmbed, handleDismissError,
    handleImportWidget, handleAddAIWidgets,
  } = useDashboardBuilder()

  return (
    <PageContainer>
      <DashboardSidebar
        dashboards={dashboards}
        currentDashboard={currentDashboard}
        loading={loading}
        insights={insights}
        onOpenCreateDialog={handleOpenCreateDialog}
        onSelectDashboard={handleSelectDashboard}
        onAddWidgetFromPalette={handleAddWidgetFromPalette}
        onImportWidget={handleImportWidget}
        onAddAIWidgets={handleAddAIWidgets}
      />

      <MainContent>
        {currentDashboard ? (
          <>
            <DashboardToolbar
              currentDashboard={currentDashboard}
              widgetCount={widgets.length}
              hasUnsavedChanges={hasUnsavedChanges}
              saving={saving}
              refreshing={refreshing}
              onRefresh={handleRefresh}
              onOpenAiMenu={handleOpenAiMenu}
              onSnapshot={handleSnapshot}
              onEmbed={handleEmbed}
              onSave={handleSave}
            />
            <DashboardCanvas
              widgets={widgets}
              localLayout={localLayout}
              onLayoutChange={handleLayoutChange}
              onDeleteWidget={handleDeleteWidget}
              selectedConnectionId={selectedConnectionId}
              currentDashboard={currentDashboard}
            />
          </>
        ) : (
          <EmptyState>
            <DashboardIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              No Dashboard Selected
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Create a new dashboard or select one from the sidebar.
            </Typography>
            <ActionButton variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreateDialog}>
              Create Dashboard
            </ActionButton>
          </EmptyState>
        )}
      </MainContent>

      <AIAnalyticsMenu
        anchorEl={aiMenuAnchor}
        onClose={handleCloseAiMenu}
        onAction={handleAIAction}
      />

      <CreateDashboardDialog
        open={createDialogOpen}
        onClose={handleCloseCreateDialog}
        loading={loading}
        name={newDashboardName}
        onNameChange={setNewDashboardName}
        selectedConnectionId={selectedConnectionId}
        onConnectionChange={setSelectedConnectionId}
        onCreate={handleCreateDashboard}
      />

      <AddWidgetDialog
        open={addWidgetDialogOpen}
        onClose={handleCloseAddWidgetDialog}
        pendingWidgetType={pendingWidgetType}
        widgetTitle={widgetTitle}
        onTitleChange={setWidgetTitle}
        widgetChartType={widgetChartType}
        onChartTypeChange={setWidgetChartType}
        pendingVariant={pendingVariant}
        onVariantChange={setPendingVariant}
        selectedConnectionId={selectedConnectionId}
        onConnectionChange={setSelectedConnectionId}
        currentDashboard={currentDashboard}
        onConfirm={handleConfirmAddWidget}
      />

      {error && (
        <Alert
          severity="error"
          onClose={handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}
