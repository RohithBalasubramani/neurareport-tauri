import { useEffect, useRef, useState } from 'react'
import { Stack } from '@mui/material'
import { useConnectionHealth } from '../hooks/useConnectionHealth'
import { useConnectionList } from '../hooks/useConnectionList'
import { useConnectionForm } from '../hooks/useConnectionForm'
import ConnectDBHeader from '../components/ConnectDBHeader'
import ConnectionFormFields from '../components/ConnectionFormFields'
import SavedConnectionsList from '../components/SavedConnectionsList'
import ConnectionDetailPanel from '../components/ConnectionDetailPanel'
import ConnectDBDialogs from '../components/ConnectDBDialogs'

/**
 * Slim orchestrator that wires together extracted hooks and sub-components.
 * All business logic lives in hooks; all rendering in sub-components.
 */
export default function ConnectDB() {
  const [canSave, setCanSave] = useState(false)
  const [isTesting, setIsTesting] = useState(false)

  const healthHook = useConnectionHealth({ isTesting })

  // Stable ref for form.reset so list hook can call it
  const resetRef = useRef(null)
  const stableReset = (...args) => resetRef.current?.(...args)

  const listHook = useConnectionList({
    setCanSave,
    setLastLatencyMs: healthHook.setLastLatencyMs,
    reset: stableReset,
  })

  const formHook = useConnectionForm({
    editingId: listHook.editingId,
    setEditingId: listHook.setEditingId,
    setDetailId: listHook.setDetailId,
    setShowDetails: listHook.setShowDetails,
    lastLatencyMs: healthHook.lastLatencyMs,
    setLastLatencyMs: healthHook.setLastLatencyMs,
    setCanSave,
    canSave,
  })

  // Patch reset ref for list hook's beginEditConnection
  resetRef.current = formHook.reset

  // Sync mutation.isPending → isTesting for health hook
  const pendingNow = formHook.mutation.isPending
  useEffect(() => {
    setIsTesting(pendingNow)
  }, [pendingNow])

  return (
    <Stack spacing={3}>
      <ConnectDBHeader
        hbStatus={healthHook.hbStatus}
        lastLatencyMs={healthHook.lastLatencyMs}
        heartbeatChipColor={healthHook.heartbeatChipColor}
        showHeartbeatChip={healthHook.showHeartbeatChip}
        lastHeartbeatLabel={healthHook.lastHeartbeatLabel}
      >
        <ConnectionFormFields
          formProps={formHook}
          showDetails={listHook.showDetails}
          setShowDetails={listHook.setShowDetails}
          canSave={canSave}
        />
      </ConnectDBHeader>

      <SavedConnectionsList
        listRef={listHook.listRef}
        detailId={listHook.detailId}
        setDetailId={listHook.setDetailId}
        rowHeartbeat={listHook.rowHeartbeat}
      />

      <ConnectionDetailPanel
        panelRef={listHook.panelRef}
        detailConnection={listHook.detailConnection}
        detailAnchor={listHook.detailAnchor}
        detailStatus={listHook.detailStatus}
        detailLatency={listHook.detailLatency}
        detailNote={listHook.detailNote}
        setDetailId={listHook.setDetailId}
        setConfirmDelete={listHook.setConfirmDelete}
        requestSelect={listHook.requestSelect}
        handleRowTest={listHook.handleRowTest}
        beginEditConnection={listHook.beginEditConnection}
      />

      <ConnectDBDialogs
        confirmSelect={listHook.confirmSelect}
        setConfirmSelect={listHook.setConfirmSelect}
        confirmDelete={listHook.confirmDelete}
        setConfirmDelete={listHook.setConfirmDelete}
        handleConfirmSelectAction={listHook.handleConfirmSelectAction}
        handleConfirmDeleteAction={listHook.handleConfirmDeleteAction}
      />
    </Stack>
  )
}
