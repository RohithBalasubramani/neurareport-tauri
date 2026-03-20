import { useCallback } from 'react'
import { InteractionType, Reversibility } from '@/components/ux/governance'
import { verifyTemplate as apiVerifyTemplate } from '@/api/client'
import { formatDuration } from '@/hooks/useStepTimingEstimator'

const EXCEL_MAX_DATA_ROWS = Number(import.meta.env?.VITE_EXCEL_MAX_DATA_ROWS ?? '30') || 30

function buildStageHandler({
  setVerifyProgress, setPageCount, setSelectedPage, setVerifyStage, setVerifyLog,
  trackVerifyStage, markVerifyStageDone,
}) {
  return (evt) => {
    if (!evt) return

    if (typeof evt.progress === 'number') {
      setVerifyProgress(evt.progress)
    }
    if (typeof evt.page_count === 'number' && evt.page_count > 0) {
      setPageCount(evt.page_count)
    }
    if (typeof evt.selected_page === 'number') {
      setSelectedPage(evt.selected_page)
    }

    const eventType = evt.event || (evt.stage ? 'stage' : null)

    if (eventType === 'stage') {
      const stageKey = typeof evt.stage === 'string' ? evt.stage : String(evt.stage ?? 'stage')
      const label = evt.label || evt.message || stageKey
      const rawStatus = typeof evt.status === 'string' ? evt.status.toLowerCase() : ''
      let status = 'started'
      if (rawStatus === 'done' || rawStatus === 'complete') status = 'complete'
      else if (rawStatus === 'error' || rawStatus === 'failed') status = 'error'
      else if (rawStatus === 'skipped') status = 'skipped'
      else if (rawStatus) status = rawStatus
      const skipped = Boolean(evt.skipped)
      const now = Date.now()

      let stageSummary = ''
      if (status === 'complete') {
        if (skipped) stageSummary = `${label} - skipped`
        else if (evt.elapsed_ms != null) stageSummary = `${label} - done in ${formatDuration(evt.elapsed_ms)}`
        else stageSummary = `${label} - done`
      } else if (status === 'error') {
        const detail = evt.detail ? `: ${evt.detail}` : ''
        stageSummary = `${label} - failed${detail}`
      } else if (status === 'skipped') {
        stageSummary = `${label} - skipped`
      } else {
        stageSummary = `${label} - in progress...`
      }
      setVerifyStage(stageSummary)

      setVerifyLog((prev) => {
        const entries = [...prev]
        const idx = entries.findIndex((entry) => entry.key === stageKey)
        const existing = idx === -1 ? null : entries[idx]
        const startedAt = status === 'started' ? now : (existing?.startedAt ?? now)
        const elapsedMs = (status === 'complete' || status === 'error' || status === 'skipped')
          ? (evt.elapsed_ms ?? existing?.elapsedMs ?? null)
          : existing?.elapsedMs ?? null
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
        }
        if (idx === -1) entries.push(nextEntry)
        else entries[idx] = nextEntry
        return entries
      })

      if (status === 'started') {
        trackVerifyStage(stageKey)
      } else if (status === 'complete' || status === 'error' || status === 'skipped') {
        markVerifyStageDone(stageKey, evt.elapsed_ms)
      }
    } else if (eventType === 'result') {
      const label = evt.stage || 'Verification complete.'
      const now = Date.now()
      const summary = evt.elapsed_ms != null
        ? `${label} - finished in ${formatDuration(evt.elapsed_ms)}`
        : label
      setVerifyStage(summary)
      setVerifyProgress((p) => {
        if (typeof evt.progress === 'number') return evt.progress
        return p < 100 ? 100 : p
      })
      setVerifyLog((prev) => {
        const entries = [...prev]
        const idx = entries.findIndex((entry) => entry.key === 'verify.result')
        const existing = idx === -1 ? null : entries[idx]
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
        }
        if (idx === -1) entries.push(nextEntry)
        else entries[idx] = nextEntry
        return entries
      })
    } else if (eventType === 'error') {
      const label = evt.stage || 'Verification failed'
      const detail = evt.detail || 'Unknown error'
      setVerifyStage(`${label} - failed: ${detail}`)
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
      ])
    }
  }
}

export function useVerifyAction({
  file, connectionId, isExcelFlow, templateKind, selectedPage,
  execute, toast,
  setQueuedJobId, setVerifyModalOpen, setVerifying, setVerified,
  setVerifyProgress, setUploadProgress, setVerifyStage, setVerifyLog,
  setPageCount, setSelectedPage, setPreview, setTemplateId, setVerifyArtifacts,
  setHtmlUrls, setCacheKey, setTemplateKind,
  beginVerifyTiming, trackVerifyStage, markVerifyStageDone, finishVerifyTiming,
}) {
  return useCallback(async () => {
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

        const handleProgress = buildStageHandler({
          setVerifyProgress, setPageCount, setSelectedPage, setVerifyStage, setVerifyLog,
          trackVerifyStage, markVerifyStageDone,
        })

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
            pngUrl: res.artifacts?.png_url || null,
            pdfUrl: res.artifacts?.pdf_url || null,
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
  }, [
    file, connectionId, isExcelFlow, templateKind, selectedPage,
    execute, toast,
    setQueuedJobId, setVerifyModalOpen, setVerifying, setVerified,
    setVerifyProgress, setUploadProgress, setVerifyStage, setVerifyLog,
    setPageCount, setSelectedPage, setPreview, setTemplateId, setVerifyArtifacts,
    setHtmlUrls, setCacheKey, setTemplateKind,
    beginVerifyTiming, trackVerifyStage, markVerifyStageDone, finishVerifyTiming,
  ])
}

export function useQueueVerifyAction({
  file, connectionId, isExcelFlow, templateKind, selectedPage,
  execute, toast,
  setQueueingVerify, setQueuedJobId,
}) {
  return useCallback(async () => {
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
  }, [
    file, connectionId, isExcelFlow, templateKind, selectedPage,
    execute, toast, setQueueingVerify, setQueuedJobId,
  ])
}
