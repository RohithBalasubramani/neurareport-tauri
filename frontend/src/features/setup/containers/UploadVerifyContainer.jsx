import { useMemo, useRef, useState, useEffect, useCallback, useId } from 'react'
import {
  Box, Typography, Stack, Button, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, Alert, TextField, Stepper, Step, StepLabel, CircularProgress
} from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import SchemaIcon from '@mui/icons-material/Schema'
import SwapHorizIcon from '@mui/icons-material/SwapHoriz'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { alpha } from '@mui/material/styles'
import { neutral, secondary, status, palette } from '@/app/theme'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import {
  withBase,
  fetchArtifactManifest,
  fetchArtifactHead,
  verifyTemplate as apiVerifyTemplate,
  mappingPreview,
  runCorrectionsPreview,
  mappingApprove,
  postGeneratorAssetsV1,
} from '@/api/client'
import { useStepTimingEstimator, formatDuration } from '@/hooks/useStepTimingEstimator'

// Mapping UI
import HeaderMappingEditor from '@/features/setup/components/HeaderMappingEditor.jsx'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import { resolveTemplatePreviewUrl, getUploadsBase } from '@/utils/preview'
import Surface from '@/components/layout/Surface.jsx'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import ConfirmModal from '@/components/Modal/ConfirmModal'

function detectFormat(file) {
  if (!file?.name) return null
  const name = file.name.toLowerCase()
  if (name.endsWith('.pdf')) return 'PDF'
  if (name.endsWith('.xlsx') || name.endsWith('.xls')) return 'Excel'
  return 'Unknown'
}

const ACCEPTED_FORMATS = new Set(['PDF', 'Excel'])
const ACCEPTED_EXTENSIONS = '.pdf,.xls,.xlsx'
const EXCEL_MAX_DATA_ROWS = Number(import.meta.env?.VITE_EXCEL_MAX_DATA_ROWS ?? '30') || 30

const formatFileSize = (bytes) => {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 KB'
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  const digits = value >= 10 || unitIndex === 0 ? 0 : 1
  return `${value.toFixed(digits)} ${units[unitIndex]}`
}

const isSupportedTemplateFile = (file) => {
  if (!file) return false
  return ACCEPTED_FORMATS.has(detectFormat(file))
}

// helper to append cache-buster
function withCache(src, cacheKey) {
  if (!src) return src
  const key = cacheKey ?? Date.now()
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
    const url = new URL(src, base)
    url.searchParams.set('v', key)
    return url.toString()
  } catch {
    const base = src.split('?')[0]
    return `${base}?v=${encodeURIComponent(key)}`
  }
}

function StepIndicator(props) {
  const { active, completed, icon } = props
  return (
    <Box
      sx={{
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 600,
        fontSize: 14,
        border: '2px solid',
        borderColor: (theme) => completed ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : active ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'divider',
        bgcolor: (theme) => completed ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : active ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'background.paper',
        color: completed || active ? 'common.white' : 'text.secondary',
        boxShadow: (theme) => active ? `0 6px 16px ${alpha(theme.palette.common.black, 0.15)}` : 'none',
        transition: 'all 160ms cubic-bezier(0.22, 1, 0.36, 1)',
      }}
    >
      {completed ? <CheckRoundedIcon fontSize="small" /> : icon}
    </Box>
  )
}

export default function UploadVerify() {
  const setSetupNav = useAppStore((state) => state.setSetupNav)
  const addTemplate = useAppStore((state) => state.addTemplate)
  const setLastApprovedTemplate = useAppStore((state) => state.setLastApprovedTemplate)
  const connection = useAppStore((state) => state.connection)
  const activeConnectionId = useAppStore((state) => state.activeConnectionId)
  const setSetupStep = useAppStore((state) => state.setSetupStep)
  const templateId = useAppStore((state) => state.templateId)
  const setTemplateId = useAppStore((state) => state.setTemplateId)
  const setVerifyArtifacts = useAppStore((state) => state.setVerifyArtifacts)
  const cacheKey = useAppStore((state) => state.cacheKey)
  const setCacheKey = useAppStore((state) => state.setCacheKey)
  const htmlUrls = useAppStore((state) => state.htmlUrls)
  const setHtmlUrls = useAppStore((state) => state.setHtmlUrls)
  const templateKind = useAppStore((state) => state.templateKind)
  const setTemplateKind = useAppStore((state) => state.setTemplateKind)

  const [file, setFile] = useState(null)
  const [pendingFileAction, setPendingFileAction] = useState(null)
  const [selectedPage, setSelectedPage] = useState(0)
  const [pageCount, setPageCount] = useState(1)

  const [verified, setVerified] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [queueingVerify, setQueueingVerify] = useState(false)
  const [queuedJobId, setQueuedJobId] = useState(null)
  const [verifyModalOpen, setVerifyModalOpen] = useState(false)
  const [verifyProgress, setVerifyProgress] = useState(0)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [verifyStage, setVerifyStage] = useState('Idle')
  const [verifyLog, setVerifyLog] = useState([])
  const [preview, setPreview] = useState(null) // { templateId, schema, htmlUrl, llm2HtmlUrl, pngUrl, pdfUrl }
  const previewTemplateId = preview?.templateId
  const previewKind = useMemo(
    () => (preview?.kind === 'excel' ? 'excel' : templateKind === 'excel' ? 'excel' : 'pdf'),
    [preview?.kind, templateKind],
  )
  const previewUploadsBase = useMemo(() => `/${getUploadsBase(previewKind)}`, [previewKind])


  const [mappingOpen, setMappingOpen] = useState(false)
  const [changeConnectionConfirmOpen, setChangeConnectionConfirmOpen] = useState(false)


  const [tplName, setTplName] = useState('New Template')
  const [tplDesc, setTplDesc] = useState('')
  const [tplTags, setTplTags] = useState('')

  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'setup-upload-verify', ...intent } }),
    [navigate]
  )
  const inputRef = useRef()
  const verifyBtnRef = useRef(null)
  const hasInProgressSetupRef = useRef(false)
  const mappingBtnRef = useRef(null)
  const {
    eta: verifyEta,
    startRun: beginVerifyTiming,
    noteStage: trackVerifyStage,
    completeStage: markVerifyStageDone,
    finishRun: finishVerifyTiming,
  } = useStepTimingEstimator('template-verify')
  const uploadInputId = useId()
  const dropDescriptionId = `${uploadInputId}-helper`

  const resetVerificationState = useCallback(
    (options = {}) => {
      setVerified(false)
      setPreview(null)
      setVerifyStage('Idle')
      setVerifyProgress(0)
      setVerifyLog([])
      setVerifyArtifacts(null)
      setHtmlUrls({ template: null, final: null, llm2: null })
      setTemplateId(null)
      setCacheKey(Date.now())
      setQueuedJobId(null)
      setQueueingVerify(false)
      if (options.clearFile) {
        setFile(null)
        setSelectedPage(0)
        setPageCount(1)
        if (inputRef.current) {
          inputRef.current.value = ''
        }
      }
    },
    [inputRef, setCacheKey, setHtmlUrls, setTemplateId, setVerifyArtifacts, setQueuedJobId, setQueueingVerify],
  )

  const applySelectedFile = useCallback(
    (selectedFile) => {
      if (!selectedFile) return
      if (!isSupportedTemplateFile(selectedFile)) {
        toast.show('Unsupported file type. Please upload a PDF or Excel design.', 'warning')
        return
      }
      resetVerificationState({ clearFile: true })
      const detected = detectFormat(selectedFile)
      const nextKind = detected === 'Excel' ? 'excel' : 'pdf'
      setTemplateKind(nextKind)
      setFile(selectedFile)
      setSetupStep('upload')
    },
    [resetVerificationState, setSetupStep, setTemplateKind, toast],
  )

  const clearFile = useCallback(() => {
    if (hasInProgressSetupRef.current) {
      setPendingFileAction({ action: 'remove', file: null })
      return
    }
    resetVerificationState({ clearFile: true })
  }, [resetVerificationState])

  const handleDropzoneKey = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      inputRef.current?.click()
    }
  }, [])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'copy'
    }
  }, [])

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault()
      const fileList = event.dataTransfer?.files
      if (fileList?.length) {
        const dropped = fileList[0]
        if (hasInProgressSetupRef.current) {
          setPendingFileAction({ action: 'replace', file: dropped })
          return
        }
        applySelectedFile(dropped)
      }
    },
    [applySelectedFile],
  )

  const format = useMemo(() => detectFormat(file), [file])
  const verifyEtaText = useMemo(() => {
    if (verifyEta.ms == null) return 'Learning how long this step usually takes...'
    const prefix = verifyEta.reliable ? '' : '~ '
    const suffix = verifyEta.reliable ? '' : ' (learning)'
    return `Estimated remaining time: ${prefix}${formatDuration(verifyEta.ms)}${suffix}`
  }, [verifyEta])
  const verifyStageLabel = verifyStage && verifyStage !== 'Idle' ? verifyStage : 'Preparing verification...'
  const dropDisabled = verifying || queueingVerify
  const hasInProgressSetup = Boolean(
    file || verified || preview?.templateId || verifyLog.length || mappingOpen
  )

  useEffect(() => {
    hasInProgressSetupRef.current = hasInProgressSetup
  }, [hasInProgressSetup])


  const connectionId = connection?.connectionId || activeConnectionId || null
  const normalizedTemplateKind = (templateKind || '').toLowerCase()
  const isExcelFlow = normalizedTemplateKind === 'excel' || format === 'Excel'
  const canGenerate = !!file && verified && !!preview?.templateId && !!connectionId

  const onPick = (e) => {
    const f = e.target.files?.[0]
    if (f) {
      if (hasInProgressSetupRef.current) {
        setPendingFileAction({ action: 'replace', file: f })
      } else {
        applySelectedFile(f)
      }
    }
    if (e.target) {
      // allow selecting the same file again
      e.target.value = ''
    }
  }


  useEffect(() => {
    if (!preview?.templateId) return
    let cancelled = false
    ;(async () => {
      try {
        const manifest = await fetchArtifactManifest(preview.templateId, { kind: previewKind })
        if (cancelled) return
        const producedAt = manifest?.produced_at
        const key = producedAt ? Date.parse(producedAt) || producedAt : Date.now()
        setCacheKey(key)
        const files = manifest?.files || {}
        const templateRel = files['template_p1.html'] || 'template_p1.html'
        const llm2Rel = files['template_llm2.html'] || templateRel
        const finalRel = files['report_final.html'] || null
        const templateBase = withBase(`${previewUploadsBase}/${preview.templateId}/${templateRel}`)
        const llm2Base = withBase(`${previewUploadsBase}/${preview.templateId}/${llm2Rel}`)
        const finalBase = finalRel ? withBase(`${previewUploadsBase}/${preview.templateId}/${finalRel}`) : null
        setHtmlUrls(() => ({
          template: withCache(templateBase, key),
          llm2: withCache(llm2Base, key),
          final: finalBase ? withCache(finalBase, key) : null,
        }))
      } catch {
        if (cancelled) return
        const key = Date.now()
        setCacheKey(key)
        setHtmlUrls((prev) => ({
          ...prev,
          template: withCache(withBase(`${previewUploadsBase}/${preview.templateId}/template_p1.html`), key),
          llm2: withCache(withBase(`${previewUploadsBase}/${preview.templateId}/template_llm2.html`), key),
        }))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [preview?.templateId, previewKind, previewUploadsBase, setCacheKey, setHtmlUrls])


  const startVerify = async () => {
    if (!file) return
    if (!connectionId) {
      toast.show(
        isExcelFlow
          ? 'Please connect to a database before verifying Excel designs.'
          : 'Please connect to a database before verifying designs.',
        'warning'
      )
      return
    }

    await execute({
      type: InteractionType.UPLOAD,
      label: 'Verify design',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId,
        templateKind,
        fileName: file?.name,
        action: 'verify_design',
      },
      action: async () => {
        setQueuedJobId(null)
        setVerifyModalOpen(false)
        setVerifying(true)
        setVerified(false)
        setVerifyProgress(0)
        setUploadProgress(0)
        setVerifyStage('Uploading file...')
        setVerifyLog([])
        beginVerifyTiming()
        trackVerifyStage('upload')

        const handleProgress = (evt) => {
          if (!evt) return;

          if (typeof evt.progress === 'number') {
            setVerifyProgress(evt.progress);
          }

          // Capture page count from the upload-complete or result events
          if (typeof evt.page_count === 'number' && evt.page_count > 0) {
            setPageCount(evt.page_count);
          }
          if (typeof evt.selected_page === 'number') {
            setSelectedPage(evt.selected_page);
          }

          const eventType = evt.event || (evt.stage ? 'stage' : null);

          if (eventType === 'stage') {
            const stageKey = typeof evt.stage === 'string' ? evt.stage : String(evt.stage ?? 'stage');
            const label = evt.label || evt.message || stageKey;
            const rawStatus = typeof evt.status === 'string' ? evt.status.toLowerCase() : '';
            let status = 'started';
            if (rawStatus === 'done' || rawStatus === 'complete') status = 'complete';
            else if (rawStatus === 'error' || rawStatus === 'failed') status = 'error';
            else if (rawStatus === 'skipped') status = 'skipped';
            else if (rawStatus) status = rawStatus;
            const skipped = Boolean(evt.skipped);
            const now = Date.now();

            let stageSummary = '';
            if (status === 'complete') {
              if (skipped) stageSummary = `${label} - skipped`;
              else if (evt.elapsed_ms != null) stageSummary = `${label} - done in ${formatDuration(evt.elapsed_ms)}`;
              else stageSummary = `${label} - done`;
            } else if (status === 'error') {
              const detail = evt.detail ? `: ${evt.detail}` : '';
              stageSummary = `${label} - failed${detail}`;
            } else if (status === 'skipped') {
              stageSummary = `${label} - skipped`;
            } else {
              stageSummary = `${label} - in progress...`;
            }
            setVerifyStage(stageSummary);

            setVerifyLog((prev) => {
              const entries = [...prev];
              const idx = entries.findIndex((entry) => entry.key === stageKey);
              const existing = idx === -1 ? null : entries[idx];
              const startedAt = status === 'started' ? now : (existing?.startedAt ?? now);
              const elapsedMs = (status === 'complete' || status === 'error' || status === 'skipped')
                ? (evt.elapsed_ms ?? existing?.elapsedMs ?? null)
                : existing?.elapsedMs ?? null;
              const nextEntry = {
                key: stageKey,
                label,
                status,
                startedAt,
                updatedAt: now,
                elapsedMs,
                skipped: skipped ?? existing?.skipped ?? false,
                detail: evt.detail ?? existing?.detail ?? null,
                meta: { ...(existing?.meta || {}), ...evt },
              };
              if (idx === -1) entries.push(nextEntry);
              else entries[idx] = nextEntry;
              return entries;
            });

            if (status === 'started') {
              trackVerifyStage(stageKey);
            } else if (status === 'complete' || status === 'error' || status === 'skipped') {
              markVerifyStageDone(stageKey, evt.elapsed_ms);
            }
          } else if (eventType === 'result') {
            const label = evt.stage || 'Verification complete.';
            const now = Date.now();
            const summary = evt.elapsed_ms != null
              ? `${label} - finished in ${formatDuration(evt.elapsed_ms)}`
              : label;
            setVerifyStage(summary);
            setVerifyProgress((p) => {
              if (typeof evt.progress === 'number') {
                return evt.progress;
              }
              return p < 100 ? 100 : p;
            });
            setVerifyLog((prev) => {
              const entries = [...prev];
              const idx = entries.findIndex((entry) => entry.key === 'verify.result');
              const existing = idx === -1 ? null : entries[idx];
              const nextEntry = {
                key: 'verify.result',
                label,
                status: 'complete',
                startedAt: existing?.startedAt ?? now,
                updatedAt: now,
                elapsedMs: evt.elapsed_ms ?? existing?.elapsedMs ?? null,
                skipped: false,
                detail: evt.detail ?? existing?.detail ?? null,
                meta: { ...(existing?.meta || {}), ...evt },
              };
              if (idx === -1) entries.push(nextEntry);
              else entries[idx] = nextEntry;
              return entries;
            });
          } else if (eventType === 'error') {
            const label = evt.stage || 'Verification failed';
            const detail = evt.detail || 'Unknown error';
            setVerifyStage(`${label} - failed: ${detail}`);
            setVerifyLog((prev) => [
              ...prev,
              {
                key: `verify.error.${Date.now()}`,
                label,
                status: 'error',
                startedAt: Date.now(),
                updatedAt: Date.now(),
                elapsedMs: evt.elapsed_ms ?? null,
                skipped: false,
                detail,
                meta: { ...evt },
              },
            ]);
          }
        };

        const handleUploadProgress = (percent, loaded, total) => {
          setUploadProgress(percent)
          if (percent < 100) {
            const fileSizeMB = (total / (1024 * 1024)).toFixed(1)
            const uploadedMB = (loaded / (1024 * 1024)).toFixed(1)
            setVerifyStage(`Uploading file... ${uploadedMB}MB / ${fileSizeMB}MB (${percent}%)`)
          }
        }

        try {
          const res = await apiVerifyTemplate({
            file,
            connectionId,
            page: selectedPage,
            onProgress: handleProgress,
            onUploadProgress: handleUploadProgress,
            kind: templateKind,
          })

          const resolvedKind =
            res?.kind === 'excel' ? 'excel' : res?.kind === 'pdf' ? 'pdf' : templateKind
          setTemplateKind(resolvedKind)
          const schemaExtUrl = res.schema_ext_url || res.artifacts?.schema_ext_url || null
          const htmlUrl = res.artifacts?.html_url || null
          const llm2Url = res.llm2_html_url || res.artifacts?.llm2_html_url || htmlUrl
          const pv = {
            templateId: res.template_id,
            kind: resolvedKind,
            schema: res.schema,
            schemaExtUrl,
            htmlUrl,
            llm2HtmlUrl: llm2Url,
            pngUrl:  res.artifacts?.png_url || null,
            pdfUrl:  res.artifacts?.pdf_url || null,
          }
          setPreview(pv)
          setTemplateId(res.template_id)
          setVerifyArtifacts(res.artifacts ? { ...res.artifacts, kind: resolvedKind } : null)

          setHtmlUrls({ template: htmlUrl, llm2: llm2Url, final: null })
          setCacheKey(Date.now())

          setVerifyStage((prev) => prev || 'Verification complete.')
          setVerifyProgress((p) => (p < 100 ? 100 : p))
          setVerified(true)
          toast.show('Template verified', 'success')
          return res
        } catch (err) {
          console.error(err)
          let msg = err?.message || 'Verification failed'
          if (/Excel verification failed/i.test(err?.message || '')) {
            msg = `Excel previews currently support up to ${EXCEL_MAX_DATA_ROWS} data rows. Delete extra rows and upload the file again.`
          }
          setVerifyStage(`Verification failed: ${msg}`)
          setVerifyLog((prev) => [
            ...prev,
            {
              key: `verify.error.${Date.now()}`,
              label: 'Verification failed',
              status: 'error',
              startedAt: Date.now(),
              updatedAt: Date.now(),
              elapsedMs: null,
              skipped: false,
              detail: msg,
              meta: { error: err?.toString?.() ?? msg },
            },
          ])
          setVerifyProgress(100)
          toast.show(err?.message || 'Verification failed', 'error')
          throw err
        } finally {
          finishVerifyTiming()
          setVerifying(false)
        }
      },
    })
  }

  const queueVerify = async () => {
    if (!file) return
    if (!connectionId) {
      toast.show(
        isExcelFlow
          ? 'Please connect to a database before verifying Excel designs.'
          : 'Please connect to a database before verifying designs.',
        'warning'
      )
      return
    }

    await execute({
      type: InteractionType.EXECUTE,
      label: 'Queue verification',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId,
        templateKind,
        fileName: file?.name,
        action: 'queue_verification',
      },
      action: async () => {
        setQueueingVerify(true)
        setQueuedJobId(null)

        try {
          const res = await apiVerifyTemplate({
            file,
            connectionId,
            page: selectedPage,
            kind: templateKind,
            background: true,
          })

          const jobId = res?.job_id || res?.jobId || null
          setQueuedJobId(jobId)
          toast.show('Verification queued in background', 'success')
          return res
        } catch (err) {
          console.error(err)
          toast.show(err?.message || 'Failed to queue verification', 'error')
          throw err
        } finally {
          setQueueingVerify(false)
        }
      },
    })
  }


  const startMapping = () => {
    if (!preview?.templateId) {
      toast.show('Verify a design first', 'info')
      return
    }
    if (!connectionId) {
      toast.show('Please connect to a database first', 'warning')
      return
    }
  
    setSetupStep('mapping')
    setMappingOpen(true)
  }

  const handleChangeConnection = useCallback(() => {
    if (hasInProgressSetup) {
      setChangeConnectionConfirmOpen(true)
      return
    }
    setSetupNav('connect')
  }, [hasInProgressSetup, setSetupNav])




  const onApprove = async (resp) => {
    const templateId = preview?.templateId
    const stripQuery = (url) => (url ? url.split('?')[0] : url)
    const refinedFinal = resp?.final_html_url ? withBase(stripQuery(resp.final_html_url)) : null
    const refinedTemplate = resp?.template_html_url ? withBase(stripQuery(resp.template_html_url)) : null
    let manifest = resp?.manifest || null

    if (!manifest && templateId) {
      try {
        manifest = await fetchArtifactManifest(templateId, { kind: previewKind })
      } catch (err) {
        console.warn('manifest fetch failed', err)
      }
    }

    const producedAtRaw = manifest?.produced_at
    const cacheSeed = producedAtRaw ? Date.parse(producedAtRaw) || producedAtRaw : Date.now()
    setCacheKey(cacheSeed)

    const buildFromManifest = (name) => {
      if (!templateId) return null
      const rel = manifest?.files?.[name]
      if (!rel) return null
      return withBase(`${previewUploadsBase}/${templateId}/${rel}`)
    }

    const templateBase = buildFromManifest('template_p1.html') || refinedTemplate || (preview?.htmlUrl ? stripQuery(preview.htmlUrl) : null)
    const llm2Base =
      buildFromManifest('template_llm2.html') ||
      (preview?.llm2HtmlUrl ? stripQuery(preview.llm2HtmlUrl) : null) ||
      templateBase
    const finalBase = buildFromManifest('report_final.html') || refinedFinal || templateBase

    let thumbnailBase =
      buildFromManifest('report_final.png') ||
      (resp?.thumbnail_url ? withBase(stripQuery(resp.thumbnail_url)) : null) ||
      preview?.pngUrl ||
      null

    if (templateId && thumbnailBase) {
      try {
        const head = await fetchArtifactHead(templateId, 'report_final.png', { kind: previewKind })
        if (!head?.artifact?.exists) {
          thumbnailBase = null
        }
      } catch (err) {
        console.warn('thumbnail head failed', err)
      }
    }

    const templateUrl = templateBase ? withCache(templateBase, cacheSeed) : null
    const llm2Url = llm2Base ? withCache(llm2Base, cacheSeed) : templateUrl
    const finalUrl = finalBase ? withCache(finalBase, cacheSeed) : templateUrl
    const thumbnailUrl = thumbnailBase ? withCache(thumbnailBase, cacheSeed) : null

    const normalizedKeys = Array.isArray(resp?.keys)
      ? Array.from(
          new Set(
            resp.keys
              .map((token) => (typeof token === 'string' ? token.trim() : ''))
              .filter(Boolean),
          ),
        )
      : []

    const artifacts =
      resp?.artifacts && typeof resp.artifacts === 'object' && !Array.isArray(resp.artifacts)
        ? resp.artifacts
        : undefined

    if (templateUrl || finalUrl || llm2Url) {
      setHtmlUrls({
        template: templateUrl || llm2Url || finalUrl,
        llm2: llm2Url || templateUrl || finalUrl,
        final: finalUrl || templateUrl || llm2Url,
      })
      setPreview((p) => ({
        ...p,
        htmlUrl: finalUrl || templateUrl || p?.htmlUrl,
        llm2HtmlUrl: llm2Url || templateUrl || p?.llm2HtmlUrl,
        pngUrl: thumbnailUrl || p?.pngUrl,
        keys: normalizedKeys,
      }))
    }

    const resolvedTemplateKind = previewKind || templateKind || 'pdf'
    const tpl = {
      id: templateId || `tpl_${Date.now()}`,
      name: tplName || file?.name || 'Template',
      status: 'approved',
      sourceType: resolvedTemplateKind,
      kind: resolvedTemplateKind,
      tags: tplTags ? tplTags.split(',').map((s) => s.trim()).filter(Boolean) : [],
      description: tplDesc || '',
      htmlUrl: finalUrl || templateUrl || undefined,
      thumbnailUrl: thumbnailUrl || undefined,
      mappingKeys: normalizedKeys,
      artifacts,
    }
    addTemplate(tpl)
    setLastApprovedTemplate(tpl)

    toast.show('Template approved and saved', 'success')

    setSetupStep('upload')
    mappingBtnRef.current?.focus()
  }

  const handleCorrectionsComplete = useCallback(
    (payload) => {
      if (!payload) return

      const cacheSeed = payload.cache_key || Date.now()
      setCacheKey(cacheSeed)

      const templateHtmlRaw = payload?.artifacts?.template_html || null
      const pageSummaryRaw = payload?.artifacts?.page_summary || null

      const templateUrl = templateHtmlRaw ? withCache(templateHtmlRaw, cacheSeed) : null
      const pageSummaryUrl = pageSummaryRaw ? withCache(pageSummaryRaw, cacheSeed) : null

      if (templateUrl) {
        setHtmlUrls((prev) => ({
          ...prev,
          template: templateUrl,
          llm2: templateUrl,
        }))
      }

      const fallbackTemplateId = previewTemplateId || payload?.template_id || templateId || null

      setPreview((prev) => {
        const hasPrevious = !!prev
        if (!hasPrevious && !templateUrl && !pageSummaryUrl) {
          return prev
        }
        const next = hasPrevious ? { ...prev } : {}
        if (!hasPrevious && fallbackTemplateId) {
          next.templateId = fallbackTemplateId
        }
        if (!hasPrevious) {
          next.kind = previewKind
        }
        if (templateUrl) {
          next.htmlUrl = templateUrl
          next.llm2HtmlUrl = templateUrl
        }
        if (pageSummaryUrl) {
          next.pageSummaryUrl = pageSummaryUrl
        }
        next.previewTs = cacheSeed
        next.manifest_produced_at = cacheSeed
        return next
      })
    },
    [previewKind, previewTemplateId, templateId, setCacheKey, setHtmlUrls, setPreview],
  )


  const effectiveTemplateHtml =
    htmlUrls?.llm2 ||
    htmlUrls?.final ||
    htmlUrls?.template ||
    preview?.llm2HtmlUrl ||
    preview?.htmlUrl
  const previewInfo = resolveTemplatePreviewUrl(
    {
      templateId: preview?.templateId || templateId,
      final_html_url: htmlUrls?.final,
      template_html_url: htmlUrls?.template,
      llm2_html_url: htmlUrls?.llm2,
      html_url: effectiveTemplateHtml,
      kind: previewKind,
      previewTs: cacheKey,
      manifest_produced_at: cacheKey,
    },
    { ts: cacheKey },
  )
  const templateIframeSrc = previewInfo.url || withCache(effectiveTemplateHtml, cacheKey)
  const templateIframeKey = previewInfo.key || `${preview?.templateId || templateId || 'template'}-${cacheKey}`

  return (
    <Surface sx={{ gap: { xs: 2, md: 2.5 } }}>
      <Stack spacing={1}>
        <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }} justifyContent="space-between" spacing={1.5}>
          <Stack direction="row" alignItems="center" spacing={0.75}>
            <Typography variant="h6">Upload & Verify Design</Typography>
            <InfoTooltip
              content={TOOLTIP_COPY.uploadVerifyTemplate}
              ariaLabel="How to upload and verify a design"
            />
          </Stack>
          <Button
            size="small"
            variant="outlined"
            startIcon={<SwapHorizIcon />}
            sx={{ px: 1.5, display: { xs: 'none', sm: 'inline-flex' } }}
            onClick={handleChangeConnection}
          >
            Change Connection
          </Button>
        </Stack>

        {/* Two-step flow now */}
        <Stepper
          activeStep={verified ? 1 : 0}
          alternativeLabel
          aria-label="Template onboarding steps"
          sx={{
            pb: 0,
            '& .MuiStep-root': { position: 'relative' },
            '& .MuiStepConnector-root': { top: 16 },
            '& .MuiStepLabel-label': { mt: 1 },
            '& .MuiStepConnector-line': { borderColor: 'divider' },
          }}
        >
          {['Check Preview', 'Map Fields'].map((label, idx) => (
            <Step key={label} completed={idx < (verified ? 2 : 0)}>
              <StepLabel StepIconComponent={StepIndicator}>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Alert severity="info" sx={{ borderRadius: 1 }}>
          Upload a report design, verify the preview, then map fields to your data.
          SQL expressions and AI corrections are optional. Approving saves the design for report runs.
        </Alert>

        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1}
          alignItems={{ xs: 'stretch', sm: 'center' }}
          sx={{ mt: 1, width: { xs: '100%', sm: 'auto' } }}
        >
          <Chip label={`Auto: ${format || '-'}`} size="small" variant="outlined" />
          <Chip
            label={connection?.status === 'connected' ? 'Connected' : 'Unknown'}
            size="small"
            variant={connection?.status === 'connected' ? 'filled' : 'outlined'}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        </Stack>
      </Stack>

      {/* Dropzone */}
      <Box sx={{ mt: 1.5, display: 'grid', gap: 1.5 }}>
        <Box
          role="button"
          tabIndex={dropDisabled ? -1 : 0}
          aria-describedby={dropDescriptionId}
          aria-disabled={dropDisabled}
          onClick={() => {
            if (!dropDisabled) inputRef.current?.click()
          }}
          onKeyDown={dropDisabled ? undefined : handleDropzoneKey}
          onDragOver={dropDisabled ? undefined : handleDragOver}
          onDrop={dropDisabled ? undefined : handleDrop}
          sx={{
            position: 'relative',
            borderRadius: 1,  // Figma spec: 8px
            border: '1px dashed',
            borderColor: (theme) => {
              if (dropDisabled) return alpha(theme.palette.action.disabled, 0.4)
              if (file) return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
              return alpha(theme.palette.divider, 0.5)
            },
            px: { xs: 2.5, sm: 3.5 },
            py: { xs: 3, sm: 3.5 },
            textAlign: 'center',
            outline: 'none',
            cursor: dropDisabled ? 'not-allowed' : 'pointer',
            bgcolor: (theme) => {
              if (dropDisabled) return alpha(theme.palette.action.disabledBackground, 0.4)
              if (file) return theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]
              return theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50]
            },
            color: 'text.secondary',
            transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), background-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',
            '&:hover': dropDisabled
              ? {}
              : {
                  borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                },
            '&:focus-visible': dropDisabled
              ? {}
              : {
                  borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                  boxShadow: (theme) => `0 0 0 3px ${alpha(theme.palette.text.primary, 0.1)}`,
                },
          }}
        >
          <Stack spacing={1.5} alignItems="center">
            <Box
              aria-hidden
              sx={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'common.white',
                boxShadow: `0 8px 20px ${alpha(neutral[900], 0.12)}`,
                color: 'text.secondary',
              }}
            >
              <CloudUploadOutlinedIcon fontSize="medium" />
            </Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {dropDisabled ? 'Verification in progress...' : 'Drop design here or click to browse'}
            </Typography>
              <Typography id={dropDescriptionId} variant="body2" color="text.secondary">
                Accepts PDF or Excel files (.pdf, .xls, .xlsx)
              </Typography>
              {format === 'Excel' && (
                <Alert severity="info" sx={{ mt: 1, alignSelf: 'stretch' }}>
                  Excel previews support up to {EXCEL_MAX_DATA_ROWS} data rows. Delete extra rows before uploading a new file.
                </Alert>
              )}
            <Stack direction="row" spacing={1}>
              <Chip label="PDF" size="small" variant="outlined" />
              <Chip label="Excel" size="small" variant="outlined" />
            </Stack>
          </Stack>
          <input
            ref={inputRef}
            id={uploadInputId}
            type="file"
            hidden
            accept={ACCEPTED_EXTENSIONS}
            onChange={onPick}
            disabled={dropDisabled}
          />
        </Box>
      </Box>

      {file ? (
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={{ xs: 1.5, sm: 2 }}
          alignItems={{ sm: 'center' }}
          justifyContent="space-between"
          sx={{
            mt: 2,
            px: { xs: 2, sm: 2.5 },
            py: { xs: 1.75, sm: 2 },
            borderRadius: 1,  // Figma spec: 8px
            border: '1px solid',
            borderColor: (theme) => alpha(theme.palette.divider, 0.3),
            bgcolor: 'common.white',
            boxShadow: `0 10px 24px ${alpha(neutral[900], 0.06)}`,
          }}
        >
          <Stack spacing={0.5}>
            <Typography variant="subtitle2" sx={{ wordBreak: 'break-word' }}>
              {file.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {(format || 'Unknown format')} - {formatFileSize(file.size)}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center" justifyContent="flex-end">
            <Chip
              label={format || 'Unknown'}
              size="small"
              variant={format === 'PDF' || format === 'Excel' ? 'filled' : 'outlined'}
              sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
            />
            <Button variant="text" size="small" onClick={clearFile} sx={{ color: 'text.secondary' }}>
              Remove
            </Button>
          </Stack>
        </Stack>
      ) : null}

      {/* Page selector for multi-page PDFs */}
      {file && format === 'PDF' && pageCount > 1 && (
        <Stack
          direction="row"
          spacing={1.5}
          alignItems="center"
          sx={{
            mt: 1.5,
            px: 2,
            py: 1,
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: (theme) => theme.palette.mode === 'dark'
              ? alpha(theme.palette.info.main, 0.08)
              : alpha(theme.palette.info.main, 0.06),
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            This PDF has {pageCount} pages. Select the page to verify:
          </Typography>
          <Stack direction="row" spacing={0.5} alignItems="center">
            <Button
              size="small"
              variant="outlined"
              disabled={selectedPage <= 0 || verifying}
              onClick={() => setSelectedPage((p) => Math.max(0, p - 1))}
              sx={{ minWidth: 32, px: 0.5 }}
            >
              &lsaquo;
            </Button>
            <Typography
              variant="body2"
              sx={{ minWidth: 60, textAlign: 'center', fontWeight: 600 }}
            >
              Page {selectedPage + 1} / {pageCount}
            </Typography>
            <Button
              size="small"
              variant="outlined"
              disabled={selectedPage >= pageCount - 1 || verifying}
              onClick={() => setSelectedPage((p) => Math.min(pageCount - 1, p + 1))}
              sx={{ minWidth: 32, px: 0.5 }}
            >
              &rsaquo;
            </Button>
          </Stack>
        </Stack>
      )}

      {/* Verify / Mapping buttons */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 2 }}>
        <Button
          variant="contained" color="primary" disableElevation
          startIcon={verifying ? <CircularProgress size={18} /> : <TaskAltIcon />}
          sx={{ px: 2.5 }}
          onClick={startVerify} disabled={!file || verifying || queueingVerify}
          ref={verifyBtnRef}
        >
          {verifying ? 'Verifying...' : 'Verify Design'}
        </Button>

        <Button
          variant="outlined"
          startIcon={queueingVerify ? <CircularProgress size={18} /> : <ScheduleIcon />}
          sx={{ px: 2.5, color: 'text.secondary', borderColor: 'divider' }}
          onClick={queueVerify}
          disabled={!file || verifying || queueingVerify}
        >
          {queueingVerify ? 'Queueing...' : 'Verify in Background'}
        </Button>

        <Button
          variant="outlined"
          startIcon={<SchemaIcon />} sx={{ px: 2.5, color: 'text.secondary', borderColor: 'divider' }}
          onClick={startMapping}
          disabled={!canGenerate || verifying || queueingVerify}
          ref={mappingBtnRef}
        >
          Map Fields
        </Button>
      </Stack>

      {queuedJobId && (
        <Alert
          severity="info"
          sx={{ mt: 2, alignItems: 'center' }}
          action={(
            <Button size="small" onClick={() => handleNavigate('/jobs', 'Open jobs')} sx={{ textTransform: 'none' }}>
              View Jobs
            </Button>
          )}
        >
          Verification queued in background. Job ID: {queuedJobId}
        </Alert>
      )}

      {(verifying || verifyLog.length > 0) && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 1,  // Figma spec: 8px
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Stack spacing={1.25}>
            <Stack direction="row" alignItems="center" justifyContent="space-between">
              <Typography variant="subtitle2">Verification progress</Typography>
              <Button
                size="small"
                variant="text"
                onClick={() => setVerifyModalOpen(true)}
                sx={{ textTransform: 'none' }}
              >
                View details
              </Button>
            </Stack>
            <LoadingState
              label={verifyStageLabel}
              progress={verifyProgress}
              description={verifyEtaText}
            />
            {!!verifyLog.length && (
              <Stack spacing={0.5}>
                {verifyLog.slice(-3).map((entry) => (
                  <Typography
                    key={`inline-${entry.key}`}
                    variant="caption"
                    color="text.secondary"
                  >
                    {entry.label || entry.key}
                  </Typography>
                ))}
              </Stack>
            )}
          </Stack>
        </Box>
      )}

      {/* Preview (after verify) */}
      <Stack spacing={2.5} sx={{ mt: 3 }}>
        <Typography
          variant="subtitle2"
          sx={{ color: 'text.secondary', letterSpacing: '0.08em', textTransform: 'uppercase' }}
        >
          Fidelity Preview
        </Typography>
        {preview ? (
          <Box
            sx={{
              display: 'grid',
              gap: { xs: 2, md: 3 },
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
            }}
          >
            <Stack spacing={1.5}>
              <Typography variant="subtitle2">
                Reference (Page {selectedPage + 1}{pageCount > 1 ? ` of ${pageCount}` : ''})
              </Typography>
              <Box
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,  // Figma spec: 8px
                  overflow: 'hidden',
                  aspectRatio: '210 / 297',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'background.paper',
                  boxShadow: `0 16px 38px ${alpha(neutral[900], 0.08)}`,
                }}
              >
                <Box
                  component="img"
                  alt="Reference page preview"
                  src={preview.pngUrl}
                  loading="lazy"
                  sx={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                    display: 'block',
                  }}
                />
              </Box>
            </Stack>
            <Stack spacing={1.5}>
              <Typography variant="subtitle2">Generated HTML (preview)</Typography>
              <Box
                sx={{
                  position: 'relative',
                  aspectRatio: '210 / 297',
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,  // Figma spec: 8px
                  overflow: 'hidden',
                  bgcolor: 'background.paper',
                  boxShadow: `0 16px 38px ${alpha(neutral[900], 0.08)}`,
                }}
              >
                {templateIframeSrc ? (
                  <>
                    <ScaledIframePreview
                      key={templateIframeKey}
                      src={templateIframeSrc}
                      title="template-preview"
                      frameAspectRatio="210 / 297"
                      loading="eager"
                      contentAlign="top"
                      pageChrome={false}
                      marginGuides={{ inset: 36, color: alpha(secondary.violet[500], 0.3) }}
                      sx={{ width: '100%', height: '100%' }}
                    />
                    {verifying && (
                      <Box
                        sx={{
                          position: 'absolute',
                          inset: 0,
                          zIndex: 1,
                          bgcolor: (theme) => alpha(neutral[900], 0.06),
                          backdropFilter: 'blur(1.5px)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          p: 2,
                        }}
                      >
                        <LoadingState
                          label="Generating preview..."
                          description="We are re-rendering the A4 layout to match the reference PDF."
                          inline
                          dense
                          sx={{ color: 'text.secondary' }}
                        />
                      </Box>
                    )}
                  </>
                ) : (
                  <Box
                    sx={{
                      height: '100%',
                      width: '100%',
                      borderRadius: 1,  // Figma spec: 8px
                      border: '1px dashed',
                      borderColor: 'divider',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      px: 2,
                      bgcolor: 'background.paper',
                    }}
                  >
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                      No preview yet
                    </Typography>
                  </Box>
                )}
              </Box>
            </Stack>
          </Box>
        ) : (
          <EmptyState
            icon={SchemaIcon}
            size="large"
            title="Preview not ready"
            description={file ? 'Verify the design to generate the side-by-side A4 preview.' : 'Upload and verify a design to generate the preview.'}
            action={
              file ? (
                <Button
                  variant="contained"
                  size="small"
                  onClick={startVerify}
                  disabled={verifying}
                  startIcon={verifying ? <CircularProgress size={16} /> : <TaskAltIcon />}
                >
                  {verifying ? 'Verifying...' : 'Verify now'}
                </Button>
              ) : null
            }
            sx={{
              borderStyle: 'solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
              textAlign: 'left',
              alignItems: 'flex-start',
            }}
          />
        )}
      </Stack>

      {/* Verify modal */}
      <Dialog
        open={verifyModalOpen}
        onClose={() => { if (!verifying) { setVerifyModalOpen(false); verifyBtnRef.current?.focus() } }}
        fullWidth
        maxWidth="sm"
        aria-labelledby="verify-dialog-title"
        aria-describedby="verify-dialog-description"
      >
        <DialogTitle id="verify-dialog-title">Design Verification</DialogTitle>
        <DialogContent id="verify-dialog-description">
          <Box sx={{ my: 2 }} aria-live="polite">
            <LoadingState
              label={verifyStageLabel}
              progress={verifyProgress}
              description={verifyEtaText}
            />
            {!!verifyLog.length && (
              <Stack
                component="ol"
                spacing={0.5}
                sx={{
                  mt: 2,
                  pl: 2.5,
                  listStyle: 'decimal',
                }}
              >
                {verifyLog.map((entry, idx) => {
                  const baseLabel = entry?.label || entry?.key || `Step ${idx + 1}`
                  let suffix = ''
                  if (entry?.status === 'complete') {
                    if (entry?.skipped) suffix = ' (skipped)'
                    else if (entry?.elapsedMs != null) suffix = ` (${formatDuration(entry.elapsedMs)})`
                    else suffix = ' (done)'
                  } else if (entry?.status === 'error') {
                    suffix = ` (failed${entry?.detail ? `: ${entry.detail}` : ''})`
                  } else if (entry?.status === 'started') {
                    suffix = ' (in progress)'
                  } else if (entry?.status === 'skipped') {
                    suffix = ' (skipped)'
                  }
                  const text = `${baseLabel}${suffix}`
                  const isActive = Boolean(verifying && entry?.status === 'started')
                  const isError = entry?.status === 'error'
                  return (
                    <Typography
                      key={`${entry?.key || baseLabel}-${idx}`}
                      component="li"
                      variant="caption"
                      color={isActive ? 'text.primary' : isError ? 'text.secondary' : 'text.secondary'}
                      sx={{ display: 'list-item' }}
                    >
                      {text}
                    </Typography>
                  )
                })}
              </Stack>
            )}
          </Box>
          {verified && <Alert severity="success" icon={<CheckCircleOutlineIcon />}>Verification passed</Alert>}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => { setVerifyModalOpen(false); verifyBtnRef.current?.focus() }}
            disabled={verifying}
            autoFocus
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Mapping dialog (preview + meta on left, mapping editor on right) */}
      <Dialog
        open={mappingOpen}
        onClose={() => setMappingOpen(false)}
        maxWidth="xl"
        fullWidth
        aria-labelledby="mapping-dialog-title"
        aria-describedby="mapping-dialog-description"
      >
        <DialogTitle id="mapping-dialog-title">Map Fields</DialogTitle>
        <DialogContent dividers id="mapping-dialog-description">
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              gap: 2,
              alignItems: 'stretch',
            }}
          >
            {/* LEFT: dedicated preview + template meta */}
            <Box
              sx={{
                width: { xs: '100%', md: '50%' },
                flexBasis: { md: '50%' },
                maxWidth: { md: '50%' },
                minWidth: { md: 360 },
                flexShrink: 0,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <Stack spacing={2} sx={{ flexGrow: 1, minHeight: 0 }}>
                <Typography variant="subtitle2">Design Preview</Typography>

                <Box
                  sx={{
                    width: '100%',
                    alignSelf: 'stretch',
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2,
                    mb: 2,
                  }}
                >
                  {templateIframeSrc ? (
                    <Box
                      sx={{
                        width: '100%',
                        maxWidth: { xs: 'min(100%, 620px)', md: 'min(100%, 960px)' },
                        aspectRatio: '210 / 297',
                        maxHeight: {
                          xs: 'min(1440px, calc(260vw), calc(175vh))',
                          md: 'min(2880px, calc(200vw), calc(175vh))',
                        },
                        flexShrink: 0,
                        margin: '0 auto',
                      }}
                    >
                      <ScaledIframePreview
                        key={`${templateIframeKey}-mapping`}
                        title="mapping-template-preview"
                        src={templateIframeSrc}
                        sx={{ width: '100%', height: '100%', overflow: 'hidden', borderRadius: 0 }}
                        frameAspectRatio="210 / 297"
                        fit="width"
                        loading="eager"
                        contentAlign="top"
                        pageShadow
                        pageBorderColor={alpha(neutral[900], 0.08)}
                        clampToParentHeight
                      />
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ px: 2, textAlign: 'center' }}>
                      Upload and verify a design to see the preview here.
                    </Typography>
                  )}
                </Box>

                {/* Design Details */}
                <Typography variant="subtitle2">Design Details</Typography>
                <TextField
                  label="Design Name"
                  size="small"
                  value={tplName}
                  onChange={(e) => setTplName(e.target.value)}
                  fullWidth
                />
                <TextField
                  label="Description"
                  size="small"
                  value={tplDesc}
                  onChange={(e) => setTplDesc(e.target.value)}
                  fullWidth
                />
                <TextField
                  label="Tags (comma separated)"
                  size="small"
                  value={tplTags}
                  onChange={(e) => setTplTags(e.target.value)}
                  fullWidth
                />
              </Stack>
            </Box>

            {/* RIGHT: Mapping editor */}
            <Box
              sx={{
                width: { xs: '100%', md: '50%' },
                flexBasis: { md: '50%' },
                maxWidth: { md: '50%' },
                minWidth: 0,
                display: 'flex',
                flexDirection: 'column',
                flexGrow: 1,
              }}
            >
              <Box
                sx={{
                  flexGrow: 1,
                  minHeight: 0,
                  overflow: 'auto',
                }}
              >
                <HeaderMappingEditor
                  templateId={preview?.templateId}
                  connectionId={connectionId}
                  templateKind={previewKind}
                  onApproved={(resp) => {
                    onApprove(resp)
                    setMappingOpen(false)
                  }}
                  onCorrectionsComplete={handleCorrectionsComplete}
                />
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMappingOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmModal
        open={Boolean(pendingFileAction)}
        onClose={() => setPendingFileAction(null)}
        onConfirm={() => {
          const action = pendingFileAction?.action
          const nextFile = pendingFileAction?.file
          setPendingFileAction(null)
          if (action === 'remove') {
            resetVerificationState({ clearFile: true })
            return
          }
          if (nextFile) {
            applySelectedFile(nextFile)
          }
        }}
        title={pendingFileAction?.action === 'remove' ? 'Remove design file' : 'Replace design file'}
        message={pendingFileAction?.action === 'remove'
          ? 'Removing the file clears verification progress, preview, and mapping changes. Continue?'
          : 'Replacing the file clears verification progress, preview, and mapping changes. Continue?'}
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

    </Surface>
  )
}










