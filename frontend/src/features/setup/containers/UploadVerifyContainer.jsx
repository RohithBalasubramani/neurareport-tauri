import { useMemo, useRef, useState, useEffect, useCallback, useId } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, useNavigateInteraction } from '@/components/ux/governance'
import { withBase } from '@/api/client'
import { useStepTimingEstimator, formatDuration } from '@/hooks/useStepTimingEstimator'
import { resolveTemplatePreviewUrl, getUploadsBase } from '@/utils/preview'
import Surface from '@/components/layout/Surface.jsx'
import useUploadVerification from '@/features/setup/hooks/useUploadVerification'
import useTemplateFormFields from '@/features/setup/hooks/useTemplateFormFields'
import usePdfPaging from '@/features/setup/hooks/usePdfPaging'
import useFileUpload from '@/features/setup/hooks/useFileUpload'
import { useVerifyAction, useQueueVerifyAction } from '@/features/setup/hooks/useVerifyActions'
import { useManifestEffect } from '@/features/setup/hooks/useManifestEffect'
import { useApproveHandler, useCorrectionsHandler } from '@/features/setup/hooks/useApproveHandlers'
import UploadHeader from '@/features/setup/components/UploadHeader'
import UploadDropzone from '@/features/setup/components/UploadDropzone'
import FileInfoBar from '@/features/setup/components/FileInfoBar'
import PdfPageSelector from '@/features/setup/components/PdfPageSelector'
import VerifyActionButtons from '@/features/setup/components/VerifyActionButtons'
import VerifyProgressPanel from '@/features/setup/components/VerifyProgressPanel'
import FidelityPreview from '@/features/setup/components/FidelityPreview'
import VerifyDetailsDialog from '@/features/setup/components/VerifyDetailsDialog'
import MappingDialog from '@/features/setup/components/MappingDialog'
import UploadConfirmModals from '@/features/setup/components/UploadConfirmModals'

function detectFormat(file) {
  if (!file?.name) return null
  const n = file.name.toLowerCase()
  if (n.endsWith('.pdf')) return 'PDF'
  if (n.endsWith('.xlsx') || n.endsWith('.xls')) return 'Excel'
  return 'Unknown'
}

function withCache(src, ck) {
  if (!src) return src
  const key = ck ?? Date.now()
  try { const u = new URL(src, window?.location?.origin || 'http://localhost'); u.searchParams.set('v', key); return u.toString() }
  catch { return `${src.split('?')[0]}?v=${encodeURIComponent(key)}` }
}

const sel = (s) => ({
  setSetupNav: s.setSetupNav, addTemplate: s.addTemplate, setLastApprovedTemplate: s.setLastApprovedTemplate,
  connection: s.connection, activeConnectionId: s.activeConnectionId, setSetupStep: s.setSetupStep,
  templateId: s.templateId, setTemplateId: s.setTemplateId, setVerifyArtifacts: s.setVerifyArtifacts,
  cacheKey: s.cacheKey, setCacheKey: s.setCacheKey, htmlUrls: s.htmlUrls, setHtmlUrls: s.setHtmlUrls,
  templateKind: s.templateKind, setTemplateKind: s.setTemplateKind,
})

export default function UploadVerify() {
  const store = useAppStore(sel)
  const { connection, activeConnectionId, templateId, cacheKey, htmlUrls, templateKind } = store
  const { setSetupNav, addTemplate, setLastApprovedTemplate, setSetupStep } = store
  const { setTemplateId, setVerifyArtifacts, setCacheKey, setHtmlUrls, setTemplateKind } = store

  const inputRef = useRef(), verifyBtnRef = useRef(null), mappingBtnRef = useRef(null)
  const uploadInputId = useId(), dropDescriptionId = `${uploadInputId}-helper`

  const v = useUploadVerification()
  const formFields = useTemplateFormFields()
  const paging = usePdfPaging()
  const fu = useFileUpload({
    resetVerification: v.resetVerification,
    resetPaging: () => { paging.setSelectedPage(0); paging.setPageCount(1) },
    inputRef,
  })
  const [mappingOpen, setMappingOpen] = useState(false)
  const [ccOpen, setCcOpen] = useState(false)
  const toast = useToast()
  const { execute } = useInteraction()
  const nav = useNavigateInteraction()
  const handleNav = useCallback((p, l, i = {}) => nav(p, { label: l, intent: { from: 'setup-upload-verify', ...i } }), [nav])
  const timing = useStepTimingEstimator('template-verify')

  const { file, preview, setPreview, hasInProgressSetupRef, applySelectedFile,
    clearFile, setPendingFileAction, pendingFileAction, setUploadProgress, resetVerificationState } = fu
  const { selectedPage, setSelectedPage, pageCount, setPageCount } = paging
  const format = useMemo(() => detectFormat(file), [file])
  const connectionId = connection?.connectionId || activeConnectionId || null
  const isExcelFlow = (templateKind || '').toLowerCase() === 'excel' || format === 'Excel'
  const previewKind = useMemo(() => (preview?.kind === 'excel' || templateKind === 'excel' ? 'excel' : 'pdf'), [preview?.kind, templateKind])
  const previewUploadsBase = useMemo(() => `/${getUploadsBase(previewKind)}`, [previewKind])
  const canGenerate = !!file && v.verified && !!preview?.templateId && !!connectionId
  const dropDisabled = v.verifying || v.queueingVerify
  const hasInProgress = Boolean(file || v.verified || preview?.templateId || v.verifyLog.length || mappingOpen)
  useEffect(() => { hasInProgressSetupRef.current = hasInProgress }, [hasInProgress, hasInProgressSetupRef])

  const verifyEtaText = useMemo(() => {
    if (timing.eta.ms == null) return 'Learning how long this step usually takes...'
    const p = timing.eta.reliable ? '' : '~ ', s = timing.eta.reliable ? '' : ' (learning)'
    return `Estimated remaining time: ${p}${formatDuration(timing.eta.ms)}${s}`
  }, [timing.eta])
  const stageLabel = v.verifyStage && v.verifyStage !== 'Idle' ? v.verifyStage : 'Preparing verification...'

  const onPick = (e) => {
    const f = e.target.files?.[0]
    if (f) { hasInProgressSetupRef.current ? setPendingFileAction({ action: 'replace', file: f }) : applySelectedFile(f) }
    if (e.target) e.target.value = ''
  }

  useManifestEffect({ preview, previewKind, previewUploadsBase, setCacheKey, setHtmlUrls })

  const startVerify = useVerifyAction({
    file, connectionId, isExcelFlow, templateKind, selectedPage, execute, toast,
    setQueuedJobId: v.setQueuedJobId, setVerifyModalOpen: v.setVerifyModalOpen,
    setVerifying: v.setVerifying, setVerified: v.setVerified,
    setVerifyProgress: v.setVerifyProgress, setUploadProgress, setVerifyStage: v.setVerifyStage,
    setVerifyLog: v.setVerifyLog, setPageCount, setSelectedPage, setPreview,
    setTemplateId, setVerifyArtifacts, setHtmlUrls, setCacheKey, setTemplateKind,
    beginVerifyTiming: timing.startRun, trackVerifyStage: timing.noteStage,
    markVerifyStageDone: timing.completeStage, finishVerifyTiming: timing.finishRun,
  })
  const queueVerify = useQueueVerifyAction({
    file, connectionId, isExcelFlow, templateKind, selectedPage, execute, toast,
    setQueueingVerify: v.setQueueingVerify, setQueuedJobId: v.setQueuedJobId,
  })
  const startMapping = () => {
    if (!preview?.templateId) { toast.show('Verify a design first', 'info'); return }
    if (!connectionId) { toast.show('Please connect to a database first', 'warning'); return }
    setSetupStep('mapping'); setMappingOpen(true)
  }
  const handleChangeConn = useCallback(() => {
    if (hasInProgress) { setCcOpen(true); return }
    setSetupNav('connect')
  }, [hasInProgress, setSetupNav])

  const onApprove = useApproveHandler({
    preview, previewKind, previewUploadsBase, templateKind, file,
    tplName: formFields.tplName, tplDesc: formFields.tplDesc, tplTags: formFields.tplTags,
    setCacheKey, setHtmlUrls, setPreview, addTemplate, setLastApprovedTemplate,
    toast, setSetupStep, mappingBtnRef,
  })
  const handleCorr = useCorrectionsHandler({
    previewKind, previewTemplateId: preview?.templateId, templateId, setCacheKey, setHtmlUrls, setPreview,
  })

  const eh = htmlUrls?.llm2 || htmlUrls?.final || htmlUrls?.template || preview?.llm2HtmlUrl || preview?.htmlUrl
  const pi = resolveTemplatePreviewUrl(
    { templateId: preview?.templateId || templateId, final_html_url: htmlUrls?.final,
      template_html_url: htmlUrls?.template, llm2_html_url: htmlUrls?.llm2,
      html_url: eh, kind: previewKind, previewTs: cacheKey, manifest_produced_at: cacheKey },
    { ts: cacheKey },
  )
  const iframeSrc = pi.url || withCache(eh, cacheKey)
  const iframeKey = pi.key || `${preview?.templateId || templateId || 'template'}-${cacheKey}`

  return (
    <Surface sx={{ gap: { xs: 2, md: 2.5 } }}>
      <UploadHeader verified={v.verified} format={format} connection={connection} onChangeConnection={handleChangeConn} />
      <UploadDropzone file={file} format={format} dropDisabled={dropDisabled} inputRef={inputRef}
        uploadInputId={uploadInputId} dropDescriptionId={dropDescriptionId} onPick={onPick}
        hasInProgressSetupRef={hasInProgressSetupRef} applySelectedFile={applySelectedFile} setPendingFileAction={setPendingFileAction} />
      <FileInfoBar file={file} format={format} onClear={clearFile} />
      <PdfPageSelector file={file} format={format} pageCount={pageCount}
        selectedPage={selectedPage} setSelectedPage={setSelectedPage} verifying={v.verifying} />
      <VerifyActionButtons ref={verifyBtnRef} mappingBtnRef={mappingBtnRef}
        file={file} verifying={v.verifying} queueingVerify={v.queueingVerify} canGenerate={canGenerate}
        onVerify={startVerify} onQueue={queueVerify} onMapping={startMapping}
        queuedJobId={v.queuedJobId} onNavigateJobs={() => handleNav('/jobs', 'Open jobs')} />
      <VerifyProgressPanel verifying={v.verifying} verifyLog={v.verifyLog}
        verifyStageLabel={stageLabel} verifyProgress={v.verifyProgress}
        verifyEtaText={verifyEtaText} onViewDetails={() => v.setVerifyModalOpen(true)} />
      <FidelityPreview preview={preview} file={file} verifying={v.verifying}
        selectedPage={selectedPage} pageCount={pageCount}
        templateIframeSrc={iframeSrc} templateIframeKey={iframeKey} startVerify={startVerify} />
      <VerifyDetailsDialog open={v.verifyModalOpen} onClose={() => v.setVerifyModalOpen(false)}
        verifying={v.verifying} verified={v.verified} verifyStageLabel={stageLabel}
        verifyProgress={v.verifyProgress} verifyEtaText={verifyEtaText}
        verifyLog={v.verifyLog} verifyBtnRef={verifyBtnRef} />
      <MappingDialog open={mappingOpen} onClose={() => setMappingOpen(false)}
        templateIframeSrc={iframeSrc} templateIframeKey={iframeKey}
        previewKind={previewKind} preview={preview} connectionId={connectionId}
        tplName={formFields.tplName} setTplName={formFields.setTplName}
        tplDesc={formFields.tplDesc} setTplDesc={formFields.setTplDesc}
        tplTags={formFields.tplTags} setTplTags={formFields.setTplTags}
        onApprove={(resp) => { onApprove(resp); setMappingOpen(false) }}
        onCorrectionsComplete={handleCorr} />
      <UploadConfirmModals pendingFileAction={pendingFileAction} setPendingFileAction={setPendingFileAction}
        resetVerificationState={resetVerificationState} applySelectedFile={applySelectedFile}
        changeConnectionConfirmOpen={ccOpen} setChangeConnectionConfirmOpen={setCcOpen}
        setMappingOpen={setMappingOpen} setVerifyModalOpen={v.setVerifyModalOpen} setSetupNav={setSetupNav} />
    </Surface>
  )
}
