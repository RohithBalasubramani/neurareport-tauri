import ConfirmDialog from '@/components/ConfirmDialog.jsx'

export default function ConnectDBDialogs({
  confirmSelect,
  setConfirmSelect,
  confirmDelete,
  setConfirmDelete,
  handleConfirmSelectAction,
  handleConfirmDeleteAction,
}) {
  return (
    <>
      <ConfirmDialog
        open={!!confirmSelect}
        title="Replace Active Connection?"
        message="Selecting this connection will replace the current active one. Continue?"
        confirmText="Yes, select"
        onClose={() => setConfirmSelect(null)}
        onConfirm={handleConfirmSelectAction}
      />

      <ConfirmDialog
        open={!!confirmDelete}
        title="Delete Connection"
        message="This will remove the saved connection from NeuraReport. You can undo within a few seconds."
        confirmText="Delete"
        onClose={() => setConfirmDelete(null)}
        onConfirm={handleConfirmDeleteAction}
      />
    </>
  )
}
