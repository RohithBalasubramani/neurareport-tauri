import ConfirmModal from '@/components/modal/ConfirmModal'

export default function UploadConfirmModals({
  pendingFileAction,
  setPendingFileAction,
  resetVerificationState,
  applySelectedFile,
  changeConnectionConfirmOpen,
  setChangeConnectionConfirmOpen,
  setMappingOpen,
  setVerifyModalOpen,
  setSetupNav,
}) {
  return (
    <>
      <ConfirmModal
        open={Boolean(pendingFileAction)}
        onClose={() => setPendingFileAction(null)}
        onConfirm={() => {
          const act = pendingFileAction?.action
          const nf = pendingFileAction?.file
          setPendingFileAction(null)
          if (act === 'remove') {
            resetVerificationState({ clearFile: true })
            return
          }
          if (nf) applySelectedFile(nf)
        }}
        title={pendingFileAction?.action === 'remove' ? 'Remove design file' : 'Replace design file'}
        message={
          pendingFileAction?.action === 'remove'
            ? 'Removing the file clears verification progress, preview, and mapping changes. Continue?'
            : 'Replacing the file clears verification progress, preview, and mapping changes. Continue?'
        }
        confirmLabel={pendingFileAction?.action === 'remove' ? 'Remove file' : 'Replace file'}
        severity="warning"
      />
      <ConfirmModal
        open={changeConnectionConfirmOpen}
        onClose={() => setChangeConnectionConfirmOpen(false)}
        onConfirm={() => {
          resetVerificationState({ clearFile: true })
          setMappingOpen(false)
          setVerifyModalOpen(false)
          setChangeConnectionConfirmOpen(false)
          setSetupNav('connect')
        }}
        title="Switch Connection"
        message="Switching connections will clear the uploaded file, verification progress, and any mapping work. Continue?"
        confirmLabel="Switch"
        severity="warning"
      />
    </>
  )
}
